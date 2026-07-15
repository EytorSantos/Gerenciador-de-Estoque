from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database.database import get_db
from app.core.schemas import schemas
from app.core.services.services import MedicationService
from app.core.dependencies.dependencies import get_current_active_user
from app.core.models.models import User, UserRole

router = APIRouter(prefix="/medications", tags=["Medications"])

def get_medication_service(db: Session = Depends(get_db)) -> MedicationService:
    return MedicationService(db)

def require_stock_manager_or_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Permite acesso a gerentes de estoque e administradores."""
    if current_user.role not in (UserRole.STOCK_MANAGER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a gerentes de estoque ou administradores"
        )
    return current_user

@router.post("/", response_model=schemas.MedicationResponse, status_code=status.HTTP_201_CREATED)
async def create_medication(
    medication: schemas.MedicationCreate,
    medication_service: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(require_stock_manager_or_admin)
):
    """
    Cadastra um novo medicamento no sistema.
    Requer privilégios de Gerente de Estoque ou Administrador.
    """
    db_medication = medication_service.get_medication_by_barcode(medication.barcode)
    if db_medication:
        raise HTTPException(status_code=400, detail="Medicamento com este código de barras já existe")
    return medication_service.create_medication(medication)

@router.get("/", response_model=List[schemas.MedicationResponse])
async def read_medications(
    skip: int = 0,
    limit: int = 100,
    medication_service: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todos os medicamentos cadastrados com seus respectivos saldos de estoque.
    """
    return medication_service.get_medications_with_stock(skip=skip, limit=limit)

@router.get("/{medication_id}", response_model=schemas.MedicationResponse)
async def read_medication(
    medication_id: int,
    medication_service: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(get_current_active_user)
):
    medication = medication_service.get_medication_with_stock(medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    return medication

@router.put("/{medication_id}", response_model=schemas.MedicationResponse)
async def update_medication(
    medication_id: int,
    medication: schemas.MedicationUpdate,
    medication_service: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(require_stock_manager_or_admin)
):
    db_medication = medication_service.get(medication_id)
    if db_medication is None:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    return medication_service.update(db_medication, medication.model_dump(exclude_unset=True))

@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication(
    medication_id: int,
    medication_service: MedicationService = Depends(get_medication_service),
    current_user: User = Depends(require_stock_manager_or_admin)
):
    medication = medication_service.delete(medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    return
