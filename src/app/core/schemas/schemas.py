from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.core.models.models import UserRole, MedicationTarja, MovementType

# Schemas para Autenticação
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole
    is_2fa_enabled: bool = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    profile: Optional["ProfileBase"] = None

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    two_factor_secret: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_2fa_enabled: bool
    two_factor_secret: Optional[str] = None
    created_at: datetime
    profile: Optional["ProfileResponse"] = None

    class Config:
        from_attributes = True

# Schemas para 2FA
class TwoFactorAuthSetup(BaseModel):
    secret: str
    qrcode_uri: str

class TwoFactorAuthVerify(BaseModel):
    otp: str

class TwoFactorAuthDisable(BaseModel):
    otp: str

# Schemas para Perfil
class ProfileBase(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    cpf: Optional[str] = Field(None, max_length=14)
    crm: Optional[str] = Field(None, max_length=20)

class ProfileCreate(ProfileBase):
    user_id: int

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Schemas para Medicamento
class MedicationBase(BaseModel):
    barcode: str = Field(..., min_length=5, max_length=50, description="Código de barras EAN-13 ou similar")
    name: str = Field(..., min_length=2, max_length=100, description="Nome comercial do medicamento")
    active_principle: str = Field(..., min_length=2, max_length=100, description="Princípio ativo (Ex: Paracetamol)")
    dosage: str = Field(..., min_length=1, max_length=50, description="Dosagem (Ex: 500mg, 10ml)")
    manufacturer: str = Field(..., min_length=2, max_length=100, description="Laboratório fabricante")
    tarja: MedicationTarja = Field(..., description="Classificação de tarja do medicamento")
    price: float = Field(..., gt=0, description="Preço de venda unitário")
    min_stock: int = Field(0, ge=0, description="Quantidade mínima para alerta de estoque baixo")

class MedicationCreate(MedicationBase):
    pass

class MedicationUpdate(MedicationBase):
    barcode: Optional[str] = Field(None, min_length=5, max_length=50)
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    active_principle: Optional[str] = Field(None, min_length=2, max_length=100)
    dosage: Optional[str] = Field(None, min_length=1, max_length=50)
    manufacturer: Optional[str] = Field(None, min_length=2, max_length=100)
    tarja: Optional[MedicationTarja] = None
    price: Optional[float] = Field(None, gt=0)
    min_stock: Optional[int] = Field(None, ge=0)

class MedicationResponse(MedicationBase):
    id: int
    created_at: datetime
    current_stock: Optional[int] = 0

    class Config:
        from_attributes = True

# Schemas para Lote
class BatchBase(BaseModel):
    batch_number: str = Field(..., min_length=1, max_length=50, description="Número de identificação do lote")
    expiration_date: datetime = Field(..., description="Data de validade do lote")
    quantity: int = Field(..., ge=0, description="Quantidade disponível neste lote")

class BatchCreate(BatchBase):
    medication_id: int

class BatchUpdate(BatchBase):
    batch_number: Optional[str] = Field(None, min_length=1, max_length=50)
    expiration_date: Optional[datetime] = None
    quantity: Optional[int] = Field(None, ge=0)

class BatchResponse(BatchBase):
    id: int
    medication_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Schemas para Movimentação
class MovementBase(BaseModel):
    type: MovementType = Field(..., description="Tipo de movimentação: entry (entrada), exit (saída), loss (perda), adjustment (ajuste)")
    quantity: int = Field(..., gt=0, description="Quantidade movimentada")
    reason: str = Field(..., min_length=3, max_length=200, description="Motivo detalhado da movimentação")

class MovementCreate(MovementBase):
    user_id: int
    medication_id: int
    batch_id: int
    prescription: Optional["PrescriptionBase"] = None
    pharmacist_otp: Optional[str] = None

class MovementResponse(MovementBase):
    id: int
    user_id: int
    medication_id: int
    batch_id: int
    timestamp: datetime
    
    # Campos extras para o frontend (opcionais para não quebrar o ORM mapping se não carregados)
    medication_name: Optional[str] = None
    batch_number: Optional[str] = None
    username: Optional[str] = None

    class Config:
        from_attributes = True

# Schemas para Receita (Prescription)
class PrescriptionBase(BaseModel):
    doctor_crm: str = Field(..., min_length=5, max_length=20)
    doctor_name: str = Field(..., min_length=3, max_length=100)
    buyer_cpf: str = Field(..., min_length=11, max_length=14)
    buyer_name: str = Field(..., min_length=3, max_length=100)
    prescription_number: str = Field(..., min_length=5, max_length=50)

class PrescriptionCreate(PrescriptionBase):
    movement_id: int

class PrescriptionResponse(PrescriptionBase):
    id: int
    movement_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Schemas para Consulta Rápida (RF10)
class BatchDetailResponse(BaseModel):
    """Detalhes de um lote para consulta rápida."""
    batch_number: str
    expiration_date: datetime
    quantity: int
    
    class Config:
        from_attributes = True

class QuickSearchResponse(MedicationBase):
    """Resposta detalhada para consulta rápida (RF10)."""
    id: int
    created_at: datetime
    current_stock: int
    batches: List[BatchDetailResponse] = []
    
    class Config:
        from_attributes = True


UserUpdate.model_rebuild()
UserResponse.model_rebuild()
MovementCreate.model_rebuild()