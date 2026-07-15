from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database.database import get_db
from app.core.schemas import schemas
from app.core.services.services import PrescriptionService
from app.core.dependencies.dependencies import get_current_pharmacist
from app.core.models.models import User

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])

def get_prescription_service(db: Session = Depends(get_db)) -> PrescriptionService:
    return PrescriptionService(db)

@router.post("/", response_model=schemas.PrescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_prescription(prescription: schemas.PrescriptionCreate, prescription_service: PrescriptionService = Depends(get_prescription_service), current_user: User = Depends(get_current_pharmacist)):
    """
    Registra os dados de uma receita médica vinculada a uma movimentação de medicamento controlado.
    Requer privilégios de Farmacêutico.
    """
    return prescription_service.create_prescription(prescription)
