
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database.database import Base
from app.core.models.models import Medication, Batch, Movement, User, UserRole, MedicationTarja, MovementType, Prescription
from app.core.schemas.schemas import MovementCreate, PrescriptionCreate
from app.core.services.services import MovementService, UserService
from app.core.security.jwt import get_password_hash
from datetime import datetime
from app.core.security.two_factor_auth import generate_totp_secret

# Setup for in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def db_session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def user_service(db_session):
    return UserService(db_session)

@pytest.fixture
def movement_service(db_session):
    return MovementService(db_session)

@pytest.fixture
def admin_user(db_session):
    user = User(
        username="admin_test",
        email="admin_test@example.com",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def pharmacist_user(db_session):
    user = User(
        username="pharma_test",
        email="pharma_test@example.com",
        hashed_password=get_password_hash("pharma123"),
        role=UserRole.PHARMACIST,
        is_active=True,
        two_factor_secret=generate_totp_secret(), # Generate a secret for 2FA
        is_2fa_enabled=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def medication_controlled(db_session):
    med = Medication(
        name="Morfina",
        barcode="MED001", active_principle="Morfina", dosage="10mg", manufacturer="Farmaco", price=10.50, min_stock=5,
        tarja=MedicationTarja.PRETA,


    )
    db_session.add(med)
    db_session.commit()
    db_session.refresh(med)
    return med

@pytest.fixture
def medication_common(db_session):
    med = Medication(
        name="Paracetamol",
        barcode="MED002", active_principle="Paracetamol", dosage="500mg", manufacturer="Generico", price=5.00, min_stock=10,
        tarja=MedicationTarja.LIVRE,


    )
    db_session.add(med)
    db_session.commit()
    db_session.refresh(med)
    return med

@pytest.fixture
def batch_controlled(db_session, medication_controlled):
    batch = Batch(
        medication_id=medication_controlled.id,
        batch_number="BATCH-001-C",
        expiration_date=datetime(2027, 12, 31),
        quantity=100
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    return batch

@pytest.fixture
def batch_common(db_session, medication_common):
    batch = Batch(
        medication_id=medication_common.id,
        batch_number="BATCH-001-N",
        expiration_date=datetime(2027, 12, 31),
        quantity=200
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    return batch


class TestMovementServiceAtomicTransactions:

    def test_create_entry_movement_success(self, movement_service, admin_user, medication_common, batch_common):
        initial_batch_quantity = batch_common.quantity
        movement_data = MovementCreate(
            type=MovementType.ENTRY,
            quantity=50,
            reason="Compra de novo estoque",
            user_id=admin_user.id,
            medication_id=medication_common.id,
            batch_id=batch_common.id
        )
        movement = movement_service.create_movement(movement_data, admin_user)

        assert movement is not None
        assert movement.type == MovementType.ENTRY
        assert movement.quantity == 50
        assert movement.user_id == admin_user.id
        assert movement.medication_id == medication_common.id
        assert movement.batch_id == batch_common.id

        # Verify batch quantity updated
        movement_service.repository.db.refresh(batch_common)
        assert batch_common.quantity == initial_batch_quantity + 50

        # Verify no prescription created for non-controlled medication entry
        prescriptions = movement_service.repository.db.query(Prescription).filter(Prescription.movement_id == movement.id).all()
        assert len(prescriptions) == 0

    def test_create_exit_movement_success(self, movement_service, admin_user, medication_common, batch_common):
        initial_batch_quantity = batch_common.quantity
        movement_data = MovementCreate(
            type=MovementType.EXIT,
            quantity=30,
            reason="Venda",
            user_id=admin_user.id,
            medication_id=medication_common.id,
            batch_id=batch_common.id
        )
        movement = movement_service.create_movement(movement_data, admin_user)

        assert movement is not None
        assert movement.type == MovementType.EXIT
        assert movement.quantity == 30
        assert movement.user_id == admin_user.id

        # Verify batch quantity updated
        movement_service.repository.db.refresh(batch_common)
        assert batch_common.quantity == initial_batch_quantity - 30

    def test_create_exit_movement_insufficient_quantity_rollback(self, movement_service, admin_user, medication_common, batch_common):
        initial_batch_quantity = batch_common.quantity
        movement_data = MovementCreate(
            type=MovementType.EXIT,
            quantity=initial_batch_quantity + 10,
            reason="Venda",
            user_id=admin_user.id,
            medication_id=medication_common.id,
            batch_id=batch_common.id
        )
        with pytest.raises(ValueError, match="Quantidade insuficiente no lote."):
            movement_service.create_movement(movement_data, admin_user)

        # Verify batch quantity was not updated (rollback occurred)
        movement_service.repository.db.refresh(batch_common)
        assert batch_common.quantity == initial_batch_quantity

        # Verify no movement was created
        movements = movement_service.repository.db.query(Movement).filter(Movement.medication_id == medication_common.id).all()
        assert len(movements) == 0

    def test_create_controlled_medication_exit_success_with_2fa(self, movement_service, pharmacist_user, medication_controlled, batch_controlled):
        from pyotp import TOTP
        otp_generator = TOTP(pharmacist_user.two_factor_secret)
        otp_code = otp_generator.now() # Generate a valid OTP for testing
        
        initial_batch_quantity = batch_controlled.quantity
        prescription_data = PrescriptionCreate(
            doctor_crm="CRM12345",
            doctor_name="Dr. House",
            buyer_cpf="123.456.789-00",
            buyer_name="John Doe",
            prescription_number="RX12345",
            movement_id=0 # This will be set by the service
        )
        movement_data = MovementCreate(
            type=MovementType.EXIT,
            quantity=10,
            reason="Venda controlada",
            user_id=pharmacist_user.id,
            medication_id=medication_controlled.id,
            batch_id=batch_controlled.id,
            prescription=prescription_data,
            pharmacist_otp=otp_code
        )
        movement = movement_service.create_movement(movement_data, pharmacist_user)

        assert movement is not None
        assert movement.type == MovementType.EXIT
        assert movement.quantity == 10
        assert movement.user_id == pharmacist_user.id

        # Verify batch quantity updated
        movement_service.repository.db.refresh(batch_controlled)
        assert batch_controlled.quantity == initial_batch_quantity - 10

        # Verify prescription created
        prescription = movement_service.repository.db.query(Prescription).filter(Prescription.movement_id == movement.id).first()
        assert prescription is not None
        assert prescription.prescription_number == "RX12345"

    def test_create_controlled_medication_exit_no_prescription_rollback(self, movement_service, pharmacist_user, medication_controlled, batch_controlled):
        from pyotp import TOTP
        otp_generator = TOTP(pharmacist_user.two_factor_secret)
        otp_code = otp_generator.now() # Generate a valid OTP for testing

        initial_batch_quantity = batch_controlled.quantity
        movement_data = MovementCreate(
            type=MovementType.EXIT,
            quantity=10,
            reason="Venda controlada",
            user_id=pharmacist_user.id,
            medication_id=medication_controlled.id,
            batch_id=batch_controlled.id,
            pharmacist_otp=otp_code
        )
        with pytest.raises(ValueError, match="Receita médica obrigatória para medicamentos controlados."):
            movement_service.create_movement(movement_data, pharmacist_user)

        # Verify batch quantity was not updated (rollback occurred)
        movement_service.repository.db.refresh(batch_controlled)
        assert batch_controlled.quantity == initial_batch_quantity

        # Verify no movement or prescription was created
        movements = movement_service.repository.db.query(Movement).filter(Movement.medication_id == medication_controlled.id).all()
        assert len(movements) == 0
        prescriptions = movement_service.repository.db.query(Prescription).all()
        assert len(prescriptions) == 0

    def test_create_controlled_medication_exit_invalid_2fa_rollback(self, movement_service, pharmacist_user, medication_controlled, batch_controlled):
        initial_batch_quantity = batch_controlled.quantity
        prescription_data = PrescriptionCreate(
            doctor_crm="CRM12345",
            doctor_name="Dr. House",
            buyer_cpf="123.456.789-00",
            buyer_name="John Doe",
            prescription_number="RX12345",
            movement_id=0 # This will be set by the service
        )
        movement_data = MovementCreate(
            type=MovementType.EXIT,
            quantity=10,
            reason="Venda controlada",
            user_id=pharmacist_user.id,
            medication_id=medication_controlled.id,
            batch_id=batch_controlled.id,
            prescription=prescription_data,
            pharmacist_otp="INVALID_OTP" # Invalid OTP
        )
        with pytest.raises(ValueError, match="Código 2FA de autorização inválido."):
            movement_service.create_movement(movement_data, pharmacist_user)

        # Verify batch quantity was not updated (rollback occurred)
        movement_service.repository.db.refresh(batch_controlled)
        assert batch_controlled.quantity == initial_batch_quantity

        # Verify no movement or prescription was created
        movements = movement_service.repository.db.query(Movement).filter(Movement.medication_id == medication_controlled.id).all()
        assert len(movements) == 0
        prescriptions = movement_service.repository.db.query(Prescription).all()
        assert len(prescriptions) == 0

    def test_create_movement_invalid_medication_id_rollback(self, movement_service, admin_user, batch_common):
        initial_batch_quantity = batch_common.quantity
        movement_data = MovementCreate(
            type=MovementType.ENTRY,
            quantity=50,
            reason="Compra de novo estoque",
            user_id=admin_user.id,
            medication_id=9999, # Invalid medication ID
            batch_id=batch_common.id
        )
        with pytest.raises(ValueError, match="Medicamento não encontrado."):
            movement_service.create_movement(movement_data, admin_user)

        # Verify batch quantity was not updated (rollback occurred)
        movement_service.repository.db.refresh(batch_common)
        assert batch_common.quantity == initial_batch_quantity

        # Verify no movement was created
        movements = movement_service.repository.db.query(Movement).all()
        assert len(movements) == 0

    def test_create_movement_invalid_batch_id_rollback(self, movement_service, admin_user, medication_common):
        movement_data = MovementCreate(
            type=MovementType.ENTRY,
            quantity=50,
            reason="Compra de novo estoque",
            user_id=admin_user.id,
            medication_id=medication_common.id,
            batch_id=9999 # Invalid batch ID
        )
        with pytest.raises(ValueError, match="Lote não encontrado para a movimentação."):
            movement_service.create_movement(movement_data, admin_user)

        # Verify no movement was created
        movements = movement_service.repository.db.query(Movement).all()
        assert len(movements) == 0

    def test_create_movement_batch_medication_mismatch_rollback(self, movement_service, admin_user, medication_common, batch_controlled):
        initial_batch_quantity = batch_controlled.quantity
        movement_data = MovementCreate(
            type=MovementType.ENTRY,
            quantity=50,
            reason="Compra de novo estoque",
            user_id=admin_user.id,
            medication_id=medication_common.id, # Common medication
            batch_id=batch_controlled.id # Controlled medication batch
        )
        with pytest.raises(ValueError, match="O lote informado não pertence ao medicamento selecionado."):
            movement_service.create_movement(movement_data, admin_user)

        # Verify batch quantity was not updated (rollback occurred)
        movement_service.repository.db.refresh(batch_controlled)
        assert batch_controlled.quantity == initial_batch_quantity

        # Verify no movement was created
        movements = movement_service.repository.db.query(Movement).all()
        assert len(movements) == 0



