from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.domain import Base

class BillingEvent(Base):
    """
    Registro inmutable de un evento facturable.
    Append-only. Source of truth para facturación.
    """
    __tablename__ = "billing_events"

    id = Column(Integer, primary_key=True, index=True)
    
    # Contexto del Usuario
    user_id = Column(String, index=True, nullable=False)
    plan = Column(String, nullable=False) # Snapshot del plan en el momento del evento
    
    # Detalles del Consumo
    media_type = Column(String, index=True, nullable=False) # text, image, video
    provider = Column(String, nullable=False) # openai, deepseek, mock
    
    # Métricas
    units = Column(Float, default=1.0) # Cantidad consumida (1 imagen, 15 segundos, 500 tokens)
    unit_type = Column(String, nullable=False) # image, second, token
    
    # Costos (Calculados al momento de inserción)
    cost_estimated = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    
    # Trazabilidad
    correlation_id = Column(String, index=True, unique=True) # ID único de la operación (job_id)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Metadatos técnicos (Opcional, para debug)
    pricing_version = Column(String, nullable=False) # Versión de la tabla de precios usada
