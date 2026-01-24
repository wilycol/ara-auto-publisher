from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.versioning_service import VersioningService
from app.schemas.common.base import StandardResponse

router = APIRouter()

@router.post("/{content_id}/version", response_model=StandardResponse)
def create_content_version(
    content_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva versión de un contenido.
    Payload: {
        "change_reason": "Corrección de tono",
        "changes": {
            "notes": "Texto ajustado manualmente",
            "generated_url": "..."
        }
    }
    """
    service = VersioningService(db)
    reason = payload.get("change_reason", "No reason provided")
    changes = payload.get("changes", {})
    
    try:
        new_version = service.create_version(content_id, changes, reason)
        return StandardResponse(data={
            "tracking_id": new_version.tracking_id,
            "version_number": new_version.version_number,
            "parent_id": new_version.parent_content_id
        })
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{content_id}/versions", response_model=StandardResponse)
def get_content_versions(
    content_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene el historial de versiones"""
    service = VersioningService(db)
    versions = service.get_versions(content_id)
    return StandardResponse(data=versions)
