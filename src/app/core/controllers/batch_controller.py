from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database.database import get_db
from app.core.schemas import schemas
from app.core.services.services import BatchService
from app.core.dependencies.dependencies import get_current_active_user
from app.core.models.models import User, UserRole

router = APIRouter(prefix="/batches", tags=["Batches"])

def get_batch_service(db: Session = Depends(get_db)) -> BatchService:
    return BatchService(db)

def require_stock_manager_or_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Permite acesso a gerentes de estoque e administradores."""
    if current_user.role not in (UserRole.STOCK_MANAGER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a gerentes de estoque ou administradores"
        )
    return current_user

@router.post("/", response_model=schemas.BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    batch: schemas.BatchCreate,
    batch_service: BatchService = Depends(get_batch_service),
    current_user: User = Depends(require_stock_manager_or_admin)
):
    """
    Cria um novo lote para um medicamento específico.
    Requer privilégios de Gerente de Estoque ou Administrador.
    """
    try:
        return batch_service.create_batch(batch)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{batch_id}/quantity", response_model=schemas.BatchResponse)
async def update_batch_quantity(
    batch_id: int,
    quantity_change: int,
    batch_service: BatchService = Depends(get_batch_service),
    current_user: User = Depends(require_stock_manager_or_admin)
):
    try:
        return batch_service.update_batch_quantity(batch_id, quantity_change)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.BatchResponse])
async def read_batches(
    skip: int = 0,
    limit: int = 100,
    batch_service: BatchService = Depends(get_batch_service),
    current_user: User = Depends(get_current_active_user)
):
    return batch_service.get_multi(skip=skip, limit=limit)

@router.get("/medication/{medication_id}", response_model=List[schemas.BatchResponse])
async def read_batches_by_medication(
    medication_id: int,
    batch_service: BatchService = Depends(get_batch_service),
    current_user: User = Depends(get_current_active_user)
):
    return batch_service.repository.db.query(batch_service.repository.model).filter(
        batch_service.repository.model.medication_id == medication_id
    ).all()
