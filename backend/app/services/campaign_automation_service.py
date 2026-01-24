from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.models.automation import CampaignAutomation
from app.services.tracking_service import TrackingService
from croniter import croniter
import uuid
import json

class CampaignAutomationService:
    def __init__(self, db: Session):
        self.db = db
        self.tracking = TrackingService(db)

    def create_automation(self, data: Dict[str, Any]) -> CampaignAutomation:
        automation = CampaignAutomation(**data)
        
        # Calcular primer next_run_at al crear
        if automation.status == "active":
            automation.next_run_at = self._calculate_next_run(automation)
            
        self.db.add(automation)
        self.db.commit()
        self.db.refresh(automation)
        return automation

    def get_automation(self, automation_id: int) -> CampaignAutomation:
        return self.db.query(CampaignAutomation).filter(CampaignAutomation.id == automation_id).first()

    def _calculate_next_run(self, automation: CampaignAutomation) -> Optional[datetime]:
        """Calcula la próxima ejecución basada en trigger_config"""
        if not automation.trigger_config:
            return None
            
        now = datetime.utcnow()
        config = automation.trigger_config
        
        try:
            if automation.trigger_type == "interval":
                minutes = config.get("minutes", 60)
                # Si last_run existe, sumar desde ahí. Si no, desde now.
                base_time = automation.last_run_at or now
                return base_time + timedelta(minutes=minutes)
                
            elif automation.trigger_type == "cron":
                cron_exp = config.get("cron")
                if not cron_exp:
                    return None
                return croniter(cron_exp, now).get_next(datetime)
                
            # Otros tipos o manual no programan next_run
            return None
            
        except Exception as e:
            print(f"Error calculating next run for {automation.id}: {e}")
            return None

    def trigger_campaign(self, automation_id: int, manual_override: bool = False) -> Dict[str, Any]:
        """
        Ejecuta una campaña automatizada.
        Evalúa reglas y genera contenido si corresponde.
        """
        automation = self.get_automation(automation_id)
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")
            
        if automation.status != "active" and not manual_override:
            return {"status": "skipped", "reason": "Automation is paused"}
            
        # Ejecutar Generación (Simulada para Fase 9.0)
        # En producción real llamaría a AIClient
        
        rules = automation.rules or {}
        platform = rules.get("platform", "linkedin")
        topic = rules.get("topic", "General")
        
        # Generar contenido dummy pero trackeado
        content_data = {
            "user_id": "system_automation",
            "project_id": automation.project_id,
            "project_name": f"Project {automation.project_id}", # Idealmente query project name
            "platform": platform,
            "content_type": "text",
            "status": "generated",
            "objective": "Automated Campaign Run",
            "topic": topic,
            "generated_url": "http://automated-content.com",
            "correlation_id": str(uuid.uuid4()),
            "ai_agent": "automation_v1",
            "notes": f"Triggered by automation {automation.id}"
        }
        
        tracked_content = self.tracking.record_generation(content_data)
        
        # Actualizar estado de ejecución
        now = datetime.utcnow()
        automation.last_run_at = now
        
        # Calcular siguiente ejecución
        automation.next_run_at = self._calculate_next_run(automation)
        
        self.db.commit()
        
        return {
            "status": "success",
            "automation_id": automation.id,
            "content_id": tracked_content.tracking_id,
            "correlation_id": tracked_content.correlation_id,
            "platform": platform,
            "next_run_at": automation.next_run_at
        }
