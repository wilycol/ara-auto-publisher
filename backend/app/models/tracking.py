from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.domain import Base

class ContentTracking(Base):
    """
    Tracking de Producción (Append-Only).
    Mini base de datos de auditoría y reporting.
    """
    __tablename__ = "content_tracking"

    # --- CAMPOS AUTOMÁTICOS (SISTEMA) ---
    tracking_id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Contexto
    user_id = Column(String, index=True, nullable=False)
    project_id = Column(Integer, index=True, nullable=False)
    project_name = Column(String, nullable=True) # Desnormalizado para reporting rápido
    
    # Contenido
    objective = Column(String, nullable=True) # Objetivo del contenido
    topic = Column(String, nullable=True)
    subtopic = Column(String, nullable=True)
    audience = Column(String, nullable=True)
    
    # Distribución
    platform = Column(String, index=True, nullable=False) # linkedin, twitter, instagram
    content_type = Column(String, index=True, nullable=False) # text, image, video
    
    # IA & Métricas
    ai_agent = Column(String, nullable=True) # educational, editorial, etc.
    piece_count = Column(Integer, default=1)
    generated_url = Column(Text, nullable=True) # URL del asset o link interno
    
    # Trazabilidad
    correlation_id = Column(String, index=True, nullable=True)

    # --- VERSIONADO (FASE 8.2) ---
    parent_content_id = Column(Integer, ForeignKey("content_tracking.tracking_id"), nullable=True, index=True)
    version_number = Column(Integer, default=1)
    change_reason = Column(String, nullable=True)
    
    # Relaciones
    parent = relationship("ContentTracking", remote_side=[tracking_id], backref="versions")

    # --- CAMPOS HUMANOS (OPERATIVOS) ---
    status = Column(String, default="generated", index=True) # generated, approved, published, discarded
    published_at = Column(DateTime, nullable=True)
    owner = Column(String, nullable=True) # Responsable humano
    notes = Column(Text, nullable=True)

class ImpactMetric(Base):
    """
    Métricas de Impacto (Append-Only).
    Registra snapshots de rendimiento de un contenido.
    """
    __tablename__ = "impact_metrics"

    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(Integer, ForeignKey("content_tracking.tracking_id"), nullable=False, index=True)
    
    # Métricas Crudas
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    reactions = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # Metadatos
    captured_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String, default="manual") # manual, api, simulated
    
    # Relaciones
    content = relationship("ContentTracking", backref="metrics")
