from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import get_settings
from app.models.automation import CampaignAutomation, AutonomousDecisionLog
from app.models.optimization import OptimizationRecommendation, RecommendationStatus
from app.services.autonomy_policy import AutonomyState

router = APIRouter()
settings = get_settings()

class AutomationSetupRequest(BaseModel):
    project_id: int
    name: str
    status: str = "active"
    autonomy_status: str = AutonomyState.ACTIVE
    style_locked: bool = False

# 0. Setup Automation (Fase 13 - Wizard Support)
@router.post("/setup")
def setup_automation(payload: AutomationSetupRequest, db: Session = Depends(get_db)):
    """
    Configura o actualiza la automatización para un proyecto/campaña.
    """
    existing = db.query(CampaignAutomation).filter(CampaignAutomation.project_id == payload.project_id).first()
    
    if existing:
        existing.name = payload.name
        existing.status = payload.status
        existing.autonomy_status = payload.autonomy_status
        existing.style_locked = payload.style_locked
        # Si se reactiva, quitamos override manual si existía, o decidimos mantenerlo.
        # Regla: Si el usuario configura explícitamente, reseteamos override manual para dar paso a la nueva config.
        existing.is_manually_overridden = False
        existing.override_reason = None
        
        db.commit()
        db.refresh(existing)
        return existing
        
    new_auto = CampaignAutomation(
        project_id=payload.project_id,
        name=payload.name,
        status=payload.status,
        autonomy_status=payload.autonomy_status,
        style_locked=payload.style_locked,
        is_manually_overridden=False,
        trigger_type="time", # Default
        trigger_config={"cron": "0 9 * * *"} # Default daily 9am
    )
    db.add(new_auto)
    db.commit()
    db.refresh(new_auto)
    return new_auto

# 1. Dashboard Stats
@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Estado global de autonomía y contadores.
    """
    total_campaigns = db.query(CampaignAutomation).count()
    active = db.query(CampaignAutomation).filter(CampaignAutomation.status == "active").count()
    paused = db.query(CampaignAutomation).filter(CampaignAutomation.status == "paused").count()
    
    # Autonomy Status Stats
    autonomous_active = db.query(CampaignAutomation).filter(CampaignAutomation.autonomy_status == AutonomyState.ACTIVE).count()
    autonomous_paused = db.query(CampaignAutomation).filter(CampaignAutomation.autonomy_status == AutonomyState.PAUSED).count()
    
    # Overridden count
    overridden = db.query(CampaignAutomation).filter(CampaignAutomation.is_manually_overridden == True).count()
    
    # Error count (Fase 13)
    # Check if 'last_error' column exists in CampaignAutomation model before querying
    # For MVP robustness, if column doesn't exist, assume 0 errors to avoid 500
    errors = 0
    if hasattr(CampaignAutomation, 'last_error'):
        try:
            errors = db.query(CampaignAutomation).filter(CampaignAutomation.last_error.isnot(None)).count()
        except Exception:
            # If DB schema is behind code, ignore error counting
            pass
    
    # Last Human Action
    # Search for decisions starting with MANUAL_ or EMERGENCY_
    last_human_log = db.query(AutonomousDecisionLog).filter(
        (AutonomousDecisionLog.decision.like("MANUAL_%")) | 
        (AutonomousDecisionLog.decision == "EMERGENCY_STOP")
    ).order_by(AutonomousDecisionLog.created_at.desc()).first()
    
    return {
        "global_autonomy_enabled": settings.AUTONOMY_ENABLED,
        "campaigns": {
            "total": total_campaigns,
            "active_status": active,
            "paused_status": paused
        },
        "autonomy_states": {
            "active": autonomous_active,
            "paused": autonomous_paused,
            "manually_overridden": overridden,
            "errors": errors
        },
        "last_human_action": {
            "decision": last_human_log.decision,
            "reason": last_human_log.reason,
            "created_at": last_human_log.created_at
        } if last_human_log else None
    }

# 2. Campaign Status
@router.get("/campaign/{automation_id}/status")
def get_campaign_status(automation_id: int, db: Session = Depends(get_db)):
    """
    Estado detallado de autonomía de una campaña.
    """
    automation = db.query(CampaignAutomation).filter(CampaignAutomation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
        
    last_decision = db.query(AutonomousDecisionLog).filter(
        AutonomousDecisionLog.automation_id == automation_id
    ).order_by(AutonomousDecisionLog.created_at.desc()).first()
    
    return {
        "id": automation.id,
        "name": automation.name,
        "status": automation.status,
        "autonomy_status": automation.autonomy_status,
        "is_manually_overridden": automation.is_manually_overridden,
        "override_reason": automation.override_reason,
        "style_locked": automation.style_locked,
        "last_run_at": automation.last_run_at,
        "next_run_at": automation.next_run_at,
        "last_decision": {
            "decision": last_decision.decision if last_decision else None,
            "reason": last_decision.reason if last_decision else None,
            "created_at": last_decision.created_at if last_decision else None
        } if last_decision else None
    }

# 3. Decision History
@router.get("/history")
def get_decision_history(
    automation_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Listado paginado de decisiones autónomas.
    """
    query = db.query(AutonomousDecisionLog)
    if automation_id:
        query = query.filter(AutonomousDecisionLog.automation_id == automation_id)
        
    total = query.count()
    logs = query.order_by(AutonomousDecisionLog.created_at.desc()).limit(limit).offset(offset).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": log.id,
                "automation_id": log.automation_id,
                "decision": log.decision,
                "reason": log.reason,
                "created_at": log.created_at,
                "metrics_snapshot": log.metrics_snapshot
            } for log in logs
        ]
    }

# 3.1 Get Recommendations
@router.get("/recommendations")
def get_recommendations(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Listar recomendaciones (default: PENDING).
    """
    query = db.query(OptimizationRecommendation)
    if status:
        query = query.filter(OptimizationRecommendation.status == status)
    else:
        # Default to PENDING if not specified, or ALL? 
        # User prompt implies "Panel de Recomendaciones... Cada recomendación... Acciones disponibles".
        # Usually we want to see pending ones primarily.
        query = query.filter(OptimizationRecommendation.status == RecommendationStatus.PENDING)
        
    recs = query.order_by(OptimizationRecommendation.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": r.id,
            "automation_id": r.automation_id,
            "automation_name": r.automation.name if r.automation else "Unknown",
            "type": r.type,
            "suggested_value": r.suggested_value,
            "reasoning": r.reasoning,
            "status": r.status,
            "created_at": r.created_at
        } for r in recs
    ]

# 3.2 Emergency Stop
@router.post("/emergency-stop")
def emergency_stop(db: Session = Depends(get_db)):
    """
    ⛔ EMERGENCY STOP: Pausa TODAS las automatizaciones activas inmediatamente.
    """
    active_automations = db.query(CampaignAutomation).filter(
        CampaignAutomation.status == "active"
    ).all()
    
    count = 0
    for auto in active_automations:
        auto.status = "paused"
        auto.autonomy_status = AutonomyState.PAUSED
        auto.is_manually_overridden = True
        auto.override_reason = "GLOBAL EMERGENCY STOP TRIGGERED"
        count += 1
        
        # Log decision
        log = AutonomousDecisionLog(
            automation_id=auto.id,
            decision="EMERGENCY_STOP",
            reason="User triggered Global Emergency Stop",
            metrics_snapshot={"action": "emergency_stop", "actor": "human"}
        )
        db.add(log)
        
    db.commit()
    
    return {"status": "success", "stopped_campaigns": count, "message": "All systems stopped."}

# 4. Recommendation Control
@router.post("/recommendation/{recommendation_id}/{action}")
def control_recommendation(
    recommendation_id: int, 
    action: str, # APPROVE, REJECT, ARCHIVE
    db: Session = Depends(get_db)
):
    """
    Control humano sobre recomendaciones.
    Action: approve, reject, archive
    """
    rec = db.query(OptimizationRecommendation).filter(OptimizationRecommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    action = action.upper()
    valid_actions = ["APPROVE", "REJECT", "ARCHIVE"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of {valid_actions}")
        
    # Logic per action
    if action == "APPROVE":
        rec.status = RecommendationStatus.APPLIED
        # NOTE: Changes are NOT applied automatically to campaign configuration in Phase 11.
        # This just acknowledges the recommendation.
        
    elif action == "REJECT":
        rec.status = RecommendationStatus.REJECTED
        
    elif action == "ARCHIVE":
        rec.status = RecommendationStatus.ARCHIVED
    
    rec.handled_at = datetime.utcnow()
    rec.handled_by = "human_operator" # In a real app, from auth token
    
    db.commit()
    
    return {"status": "success", "recommendation_status": rec.status}

# 5. Manual Override Actions
@router.post("/campaign/{automation_id}/override/{action}")
def manual_override(
    automation_id: int,
    action: str, # force_resume, force_pause, lock_style, unlock_style
    reason: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Override manual de campaña.
    Actions: force_resume, force_pause, lock_style, unlock_style
    """
    automation = db.query(CampaignAutomation).filter(CampaignAutomation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
        
    action = action.lower()
    
    if action == "force_resume":
        # Force Active, Clear Autonomy Pause, Set Override Flag
        automation.status = "active"
        automation.autonomy_status = AutonomyState.ACTIVE
        automation.is_manually_overridden = True
        automation.override_reason = reason
        
    elif action == "force_pause":
        # Force Pause, Set Override Flag
        automation.status = "paused"
        automation.autonomy_status = AutonomyState.PAUSED
        automation.is_manually_overridden = True
        automation.override_reason = reason
        
    elif action == "lock_style":
        automation.style_locked = True
        
    elif action == "unlock_style":
        automation.style_locked = False
        
    else:
         raise HTTPException(status_code=400, detail="Invalid action")
    
    db.commit()
    
    # Audit Log
    log = AutonomousDecisionLog(
        automation_id=automation.id,
        decision=f"MANUAL_OVERRIDE_{action.upper()}",
        reason=f"Human Override: {reason}",
        metrics_snapshot={"action": action, "actor": "human", "override_reason": reason}
    )
    db.add(log)
    db.commit()
    
    return {
        "status": "success", 
        "automation_status": automation.status,
        "autonomy_status": automation.autonomy_status,
        "is_manually_overridden": automation.is_manually_overridden,
        "style_locked": automation.style_locked
    }
