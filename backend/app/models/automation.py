from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.domain import Base

class CampaignAutomation(Base):
    """
    Reglas de automatización para generación de contenido.
    Fase 9.0
    """
    __tablename__ = "campaign_automations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, index=True)
    
    # Configuración de Disparo
    trigger_type = Column(String, default="manual") # manual, time, event
    trigger_config = Column(JSON, nullable=True) # { "cron": "0 9 * * *", "event": "news_alert" }
    
    # Reglas de Generación
    rules = Column(JSON, nullable=True) # { "platform": "linkedin", "audience": "tech", "topic_keywords": ["ai"] }
    
    # Estado
    status = Column(String, default="active") # active, paused
    autonomy_status = Column(String, default="autonomous_active") # autonomous_active, autonomous_paused, autonomous_blocked
    
    # [Fase 11] Human Control & Governance
    is_manually_overridden = Column(Boolean, default=False) # Si True, protege contra cambios automáticos de estado
    override_reason = Column(String, nullable=True)
    style_locked = Column(Boolean, default=False) # Si True, impide cambios de estilo automáticos

    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    
    # [Fase 13] UX & Error Visibility
    last_error = Column(Text, nullable=True)
    error_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    project = relationship("Project", backref="automations")

class AutonomousDecisionLog(Base):
    """
    [Fase 10] Log de decisiones autónomas (Audit Trail).
    """
    __tablename__ = "autonomous_decision_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    automation_id = Column(Integer, ForeignKey("campaign_automations.id"), nullable=False, index=True)
    
    decision = Column(String, nullable=False) # ALLOW_EXECUTION, BLOCK_COOLDOWN, BLOCK_PERFORMANCE, PAUSE_CAMPAIGN, etc.
    reason = Column(String, nullable=False)
    metrics_snapshot = Column(JSON, nullable=True) # Métricas usadas para decidir
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    automation = relationship("CampaignAutomation", backref="decision_logs")
