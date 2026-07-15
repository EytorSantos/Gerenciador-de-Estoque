from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.database import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    PHARMACIST = "pharmacist"
    CLERK = "clerk"
    STOCK_MANAGER = "stock_manager"

class MedicationTarja(enum.Enum):
    LIVRE = "livre"
    AMARELA = "amarela"
    VERMELHA = "vermelha"
    PRETA = "preta"

class MovementType(enum.Enum):
    ENTRY = "entry"
    EXIT = "exit"
    ADJUSTMENT = "adjustment"
    WASTE = "waste"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    two_factor_secret = Column(String, nullable=True)
    is_2fa_enabled = Column(Boolean, default=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("Profile", back_populates="user", uselist=False)
    movements = relationship("Movement", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String)
    cpf = Column(String, unique=True)
    crm = Column(String, unique=True, nullable=True) # Apenas para farmacêuticos

    user = relationship("User", back_populates="profile")

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    active_principle = Column(String, index=True, nullable=False)
    dosage = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    tarja = Column(Enum(MedicationTarja), nullable=False)
    price = Column(Float, nullable=False)
    min_stock = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    batches = relationship("Batch", back_populates="medication", cascade="all, delete-orphan")
    movements = relationship("Movement", back_populates="medication")

class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"))
    batch_number = Column(String, index=True, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    quantity = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    medication = relationship("Medication", back_populates="batches")
    movements = relationship("Movement", back_populates="batch")

class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    medication_id = Column(Integer, ForeignKey("medications.id"))
    batch_id = Column(Integer, ForeignKey("batches.id"))
    type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="movements")
    medication = relationship("Medication", back_populates="movements")
    batch = relationship("Batch", back_populates="movements")
    prescription = relationship("Prescription", back_populates="movement", uselist=False)

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    movement_id = Column(Integer, ForeignKey("movements.id"), unique=True)
    doctor_crm = Column(String, nullable=False)
    doctor_name = Column(String, nullable=False)
    buyer_cpf = Column(String, nullable=False)
    buyer_name = Column(String, nullable=False)
    prescription_number = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    movement = relationship("Movement", back_populates="prescription")
