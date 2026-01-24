from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.usage_snapshot_service import UsageSnapshotService

router = APIRouter()

@router.get("/usage/{user_id}")
def get_usage_snapshot(
    user_id: str,
    plan: str = "free",
    db: Session = Depends(get_db),
    x_correlation_id: str = Header(None)
):
    """
    Endpoint interno para obtener el snapshot de uso y facturación de un usuario.
    No requiere autenticación pública (protegido a nivel de red/infraestructura).
    """
    service = UsageSnapshotService(db)
    return service.generate_daily_snapshot(user_id, plan, correlation_id=x_correlation_id)
