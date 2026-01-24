from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.domain import Base

class RecommendationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    IGNORED = "IGNORED"
    ARCHIVED = "ARCHIVED"

class RecommendationType(str, enum.Enum):
    FREQUENCY_ADJUSTMENT = "FREQUENCY_ADJUSTMENT"
    CONTENT_TYPE_CHANGE = "CONTENT_TYPE_CHANGE"
    PLATFORM_CHANGE = "PLATFORM_CHANGE"
    VERSION_ROLLBACK = "VERSION_ROLLBACK"
    STYLE_LOCK = "STYLE_LOCK"

class OptimizationRecommendation(Base):
    """
    [Fase 9.2] Recomendaciones de optimización basadas en feedback loop.
    No se ejecutan automáticamente, solo se proponen.
    """
    __tablename__ = "optimization_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    automation_id = Column(Integer, ForeignKey("campaign_automations.id"), nullable=False, index=True)
    
    # Contexto
    content_id = Column(Integer, ForeignKey("content_tracking.tracking_id"), nullable=True) # Si es específica para un contenido
    
    # Recomendación
    type = Column(String, nullable=False) # RecommendationType value
    suggested_value = Column(JSON, nullable=True) # El cambio propuesto (ej: {"frequency_minutes": 120})
    reasoning = Column(Text, nullable=False) # Explicación humana (ej: "CTR dropped 50% in V2")
    
    # Estado
    status = Column(String, default=RecommendationStatus.PENDING)
    
    # [Fase 11] Audit Trail
    handled_at = Column(DateTime, nullable=True)
    handled_by = Column(String, nullable=True) # human, system
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    automation = relationship("CampaignAutomation", backref="recommendations")
    content = relationship("ContentTracking", backref="optimizations")
