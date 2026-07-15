from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database.database import get_db
from app.core.schemas import schemas
from app.core.services.services import MovementService
from app.core.dependencies.dependencies import get_current_stock_manager, get_current_active_user
from app.core.models.models import User

router = APIRouter(prefix="/movements", tags=["Movements"])

def get_movement_service(db: Session = Depends(get_db)) -> MovementService:
    return MovementService(db)

@router.post("/", response_model=schemas.MovementResponse, status_code=status.HTTP_201_CREATED)
async def create_movement(movement: schemas.MovementCreate, movement_service: MovementService = Depends(get_movement_service), current_user: User = Depends(get_current_active_user)):
    """
    Registra uma nova movimentação de estoque (entrada, saída, perda ou ajuste).
    
    **RF06 - Controle de Controlados:** Saídas de medicamentos controlados exigem que o usuário seja um farmacêutico e forneça um código OTP válido.
    """
    try:
        return movement_service.create_movement(movement, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.MovementResponse])
async def read_movements(skip: int = 0, limit: int = 100, movement_service: MovementService = Depends(get_movement_service), current_user: User = Depends(get_current_active_user)):
    return movement_service.get_movements_with_details(skip=skip, limit=limit)
