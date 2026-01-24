from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.impact_service import ImpactService
from app.schemas.common.base import StandardResponse

router = APIRouter()

@router.post("/{content_id}", response_model=StandardResponse)
def record_impact_metrics(
    content_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Registra métricas para un contenido (Manual o Simulado).
    Payload: {"impressions": 1000, "clicks": 50, "source": "manual"}
    """
    service = ImpactService(db)
    try:
        metric = service.record_snapshot(content_id, payload)
        return StandardResponse(data={"id": metric.id, "captured_at": metric.captured_at})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{content_id}", response_model=StandardResponse)
def get_impact_performance(
    content_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene KPI y último snapshot"""
    service = ImpactService(db)
    data = service.get_content_performance(content_id)
    return StandardResponse(data=data)
