from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database.database import get_db
from app.core.schemas import schemas
from app.core.services.services import MedicationService
from app.core.dependencies.dependencies import get_current_active_user
from app.core.models.models import User

router = APIRouter(prefix="/quick-search", tags=["Quick Search"])

def get_medication_service(db: Session = Depends(get_db)) -> MedicationService:
    return MedicationService(db)

@router.get("/", response_model=List[schemas.QuickSearchResponse])
async def quick_search_medications(query: str, medication_service: MedicationService = Depends(get_medication_service), current_user: User = Depends(get_current_active_user)):
    """
    Realiza uma busca rápida de medicamentos por nome, princípio ativo ou código de barras.
    Retorna detalhes dos medicamentos encontrados, incluindo estoque atual e lotes disponíveis.
    """
    return medication_service.search_medications(query)
