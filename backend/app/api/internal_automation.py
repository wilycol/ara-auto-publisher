from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.campaign_automation_service import CampaignAutomationService
from app.schemas.common.base import StandardResponse
from typing import Dict, Any

router = APIRouter()

@router.post("/", response_model=StandardResponse)
def create_automation(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Crea una nueva regla de automatización"""
    service = CampaignAutomationService(db)
    try:
        automation = service.create_automation(payload)
        return StandardResponse(data={"id": automation.id, "name": automation.name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{automation_id}/trigger", response_model=StandardResponse)
def trigger_automation(
    automation_id: int,
    db: Session = Depends(get_db)
):
    """Dispara manualmente una automatización"""
    service = CampaignAutomationService(db)
    try:
        result = service.trigger_campaign(automation_id, manual_override=True)
        return StandardResponse(data=result)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
