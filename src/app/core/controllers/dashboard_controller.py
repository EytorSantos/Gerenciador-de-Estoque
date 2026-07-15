from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.core.database.database import get_db
from app.core.models.models import Medication, Batch, Movement, MedicationTarja, MovementType
from app.core.dependencies.dependencies import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Retorna estatísticas consolidadas para o dashboard, incluindo:
    - Total de medicamentos e lotes cadastrados.
    - Contagem de medicamentos controlados.
    - Alertas de estoque baixo e vencimento próximo.
    - Lista das 5 movimentações mais recentes.
    """
    # Total de medicamentos
    total_medications = db.query(Medication).count()
    
    # Total de lotes
    total_batches = db.query(Batch).count()
    
    # Medicamentos controlados
    controlled_medications = db.query(Medication).filter(
        Medication.tarja.in_([MedicationTarja.VERMELHA, MedicationTarja.PRETA])
    ).count()
    
    # Baixo estoque (Estoque total de todos os lotes < estoque mínimo)
    # Esta query é um pouco mais complexa, faremos uma versão simplificada para o MVP
    low_stock_count = 0
    medications = db.query(Medication).all()
    for med in medications:
        current_stock = sum(batch.quantity for batch in med.batches)
        if current_stock < med.min_stock:
            low_stock_count += 1

    # Medicamentos próximos do vencimento (próximos 30 dias)
    thirty_days_from_now = datetime.now() + timedelta(days=30)
    expiring_batches = db.query(Batch).filter(
        Batch.expiration_date <= thirty_days_from_now,
        Batch.expiration_date >= datetime.now(),
        Batch.quantity > 0
    ).all()
    
    expiring_soon_count = len(expiring_batches)
    expiring_data = []
    for b in expiring_batches:
        expiring_data.append({
            "medication_name": b.medication.name,
            "batch_number": b.batch_number,
            "expiry_date": b.expiration_date.isoformat()
        })

    # Movimentações recentes (últimas 5)
    recent_movements = db.query(Movement).order_by(Movement.timestamp.desc()).limit(5).all()
    movements_data = []
    for m in recent_movements:
        movements_data.append({
            "id": m.id,
            "type": m.type.value,
            "quantity": m.quantity,
            "medication_name": m.medication.name,
            "batch_number": m.batch.batch_number,
            "timestamp": m.timestamp.isoformat()
        })

    return {
        "total_medications": total_medications,
        "total_batches": total_batches,
        "controlled_medications": controlled_medications,
        "low_stock_count": low_stock_count,
        "expiring_soon_count": expiring_soon_count,
        "expiring_medications": expiring_data,
        "recent_movements": movements_data
    }
