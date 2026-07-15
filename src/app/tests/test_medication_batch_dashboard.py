import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database.database import Base
from app.core.models.models import Medication, Batch, User, UserRole, MedicationTarja, MovementType
from app.core.schemas.schemas import MedicationCreate, BatchCreate
from app.core.services.services import MedicationService, BatchService, DashboardService
from app.core.security.jwt import get_password_hash
from datetime import datetime, timedelta

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
def medication_service(db_session):
    return MedicationService(db_session)

@pytest.fixture
def batch_service(db_session):
    return BatchService(db_session)

@pytest.fixture
def dashboard_service(db_session):
    return DashboardService(db_session)

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
def medication_data_valid():
    return MedicationCreate(
        name="Dipirona",
        barcode="7891234567890",
        active_principle="Dipirona Sódica",
        dosage="500mg",
        manufacturer="Generico Pharma",
        tarja=MedicationTarja.LIVRE,
        price=8.50,
        min_stock=20
    )

@pytest.fixture
def medication_data_duplicate_barcode(medication_data_valid):
    # Simulate a duplicate barcode scenario
    return MedicationCreate(
        name="Dipirona Duplicada",
        barcode="7891234567890", # Same barcode as valid
        active_principle="Dipirona Sódica",
        dosage="500mg",
        manufacturer="Generico Pharma",
        tarja=MedicationTarja.LIVRE,
        price=9.00,
        min_stock=10
    )

@pytest.fixture
def batch_data_valid(medication_service, medication_data_valid):
    med = medication_service.create_medication(medication_data_valid)
    return BatchCreate(
        medication_id=med.id,
        batch_number="BATCH-DIP-001",
        expiration_date=datetime.now() + timedelta(days=365),
        quantity=100
    )

@pytest.fixture
def batch_data_expired(medication_service, medication_data_valid):
    med = medication_service.create_medication(medication_data_valid)
    return BatchCreate(
        medication_id=med.id,
        batch_number="BATCH-EXP-001",
        expiration_date=datetime.now() - timedelta(days=1),
        quantity=50
    )

@pytest.fixture
def batch_data_expiring_soon(medication_service, medication_data_valid):
    med = medication_service.create_medication(medication_data_valid)
    return BatchCreate(
        medication_id=med.id,
        batch_number="BATCH-SOON-001",
        expiration_date=datetime.now() + timedelta(days=20), # Expires in 20 days
        quantity=30
    )

@pytest.fixture
def medication_below_min_stock(db_session, medication_service):
    med = MedicationCreate(
        name="Aspirina",
        barcode="ASP001",
        active_principle="Ácido Acetilsalicílico",
        dosage="100mg",
        manufacturer="Farmaco",
        tarja=MedicationTarja.LIVRE,
        price=2.00,
        min_stock=50 # Min stock is 50
    )
    db_med = medication_service.create_medication(med)
    # Add a batch with quantity below min_stock
    batch = Batch(
        medication_id=db_med.id,
        batch_number="BATCH-ASP-001",
        expiration_date=datetime.now() + timedelta(days=365),
        quantity=20 # Current stock is 20
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(db_med)
    return db_med


class TestMedicationService:

    def test_create_medication_success(self, medication_service, medication_data_valid):
        # RF01 - Cenário 1: Inclusão com sucesso
        medication = medication_service.create_medication(medication_data_valid)
        assert medication.id is not None
        assert medication.barcode == medication_data_valid.barcode
        assert medication.name == medication_data_valid.name

    def test_create_medication_duplicate_barcode_fails(self, medication_service, medication_data_valid, medication_data_duplicate_barcode):
        # RF01 - Cenário 2: Bloqueio de duplicidade por EAN
        medication_service.create_medication(medication_data_valid)
        with pytest.raises(Exception, match="IntegrityError"):
            medication_service.create_medication(medication_data_duplicate_barcode)

    def test_search_medications_by_name(self, medication_service, medication_data_valid):
        # RF10 - Consulta Unificada: Pesquisa por nome
        medication_service.create_medication(medication_data_valid)
        results = medication_service.search_medications(query="Dipirona")
        assert len(results) == 1
        assert results[0]["name"] == "Dipirona"

    def test_search_medications_by_active_principle(self, medication_service, medication_data_valid):
        # RF10 - Consulta Unificada: Pesquisa por princípio ativo
        medication_service.create_medication(medication_data_valid)
        results = medication_service.search_medications(query="Sódica")
        assert len(results) == 1
        assert results[0]["active_principle"] == "Dipirona Sódica"

    def test_search_medications_by_barcode(self, medication_service, medication_data_valid):
        # RF10 - Consulta Unificada: Pesquisa por código de barras
        medication_service.create_medication(medication_data_valid)
        results = medication_service.search_medications(query="7891234567890")
        assert len(results) == 1
        assert results[0]["barcode"] == "7891234567890"

    def test_search_medications_no_results(self, medication_service):
        results = medication_service.search_medications(query="Inexistente")
        assert len(results) == 0


class TestBatchService:

    def test_create_batch_success(self, batch_service, batch_data_valid):
        # RF02 - Cenário 1 (parte): Validação de campos obrigatórios (via Pydantic e DB)
        batch = batch_service.create_batch(batch_data_valid)
        assert batch.id is not None
        assert batch.batch_number == batch_data_valid.batch_number

    def test_create_batch_expired_date_fails(self, batch_service, batch_data_expired):
        # RF02 - Cenário 2: Bloqueio de validade retroativa/vencida
        with pytest.raises(ValueError, match="A data de validade não pode ser retroativa ou vencida."):
            batch_service.create_batch(batch_data_expired)


class TestDashboardService:

    def test_get_expiring_medications(self, dashboard_service, medication_service, batch_service, batch_data_expiring_soon):
        # RF04 - Alerta de Vencimento Próximo: Testar backend para medicamentos vencendo em 30 dias
        batch_service.create_batch(batch_data_expiring_soon)
        expiring_meds = dashboard_service.get_expiring_medications(days_threshold=30)
        assert len(expiring_meds) == 1
        assert expiring_meds[0]["name"] == "Dipirona"
        assert expiring_meds[0]["batch_number"] == "BATCH-SOON-001"

    def test_get_expiring_medications_no_results(self, dashboard_service):
        expiring_meds = dashboard_service.get_expiring_medications(days_threshold=30)
        assert len(expiring_meds) == 0

    def test_get_low_stock_medications(self, dashboard_service, medication_below_min_stock):
        # RF05 - Alerta de Estoque Mínimo: Testar backend para medicamentos abaixo do estoque mínimo
        low_stock_meds = dashboard_service.get_low_stock_medications()
        assert len(low_stock_meds) == 1
        assert low_stock_meds[0]["name"] == "Aspirina"
        assert low_stock_meds[0]["current_stock"] == 20
        assert low_stock_meds[0]["min_stock"] == 50

    def test_get_low_stock_medications_no_results(self, dashboard_service, medication_service, batch_service, medication_data_valid):
        # Ensure no low stock if stock is above min_stock
        med = medication_service.create_medication(medication_data_valid)
        batch = BatchCreate(
            medication_id=med.id,
            batch_number="BATCH-OK-001",
            expiration_date=datetime.now() + timedelta(days=365),
            quantity=100 # min_stock is 20, current is 100
        )
        batch_service.create_batch(batch)
        low_stock_meds = dashboard_service.get_low_stock_medications()
        assert len(low_stock_meds) == 0

    def test_get_dashboard_stats(self, dashboard_service, medication_service, batch_service, batch_data_expiring_soon, medication_below_min_stock):
        # Test overall dashboard stats
        batch_service.create_batch(batch_data_expiring_soon)
        # medication_below_min_stock fixture already adds a medication with low stock

        stats = dashboard_service.get_dashboard_stats()

        assert "total_medications" in stats
        assert "total_batches" in stats
        assert "total_stock_value" in stats
        assert "expiring_soon_count" in stats
        assert "expiring_medications" in stats
        assert "low_stock_count" in stats
        assert "low_stock_medications" in stats

        assert stats["expiring_soon_count"] == 1
        assert len(stats["expiring_medications"]) == 1
        assert stats["low_stock_count"] == 1
        assert len(stats["low_stock_medications"]) == 1

