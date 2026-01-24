from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

class AutonomyState(str, Enum):
    ACTIVE = "autonomous_active"
    PAUSED = "autonomous_paused"
    BLOCKED = "autonomous_blocked"

class DecisionType(str, Enum):
    ALLOW_EXECUTION = "ALLOW_EXECUTION"
    BLOCK_COOLDOWN = "BLOCK_COOLDOWN"
    BLOCK_PERFORMANCE = "BLOCK_PERFORMANCE"
    BLOCK_KILLSWITCH = "BLOCK_KILLSWITCH"
    BLOCK_STATUS = "BLOCK_STATUS"
    PAUSE_CAMPAIGN = "PAUSE_CAMPAIGN"
    ARCHIVE_CAMPAIGN = "ARCHIVE_CAMPAIGN"

class AutonomyPolicy:
    """
    [Fase 10] Motor de reglas y políticas de autonomía.
    Define CUÁNDO y CÓMO debe actuar el sistema.
    """
    
    # Límites globales por defecto
    DEFAULT_COOLDOWN_MINUTES = 60
    MAX_DAILY_EXECUTIONS = 5
    
    # Umbrales de rendimiento (Simulados para Fase 10, expandibles en futuro)
    MIN_CTR_THRESHOLD = 0.5 # 0.5%
    MIN_ENGAGEMENT_RATE = 0.1 # 0.1%
    
    @staticmethod
    def check_cooldown(last_run: Optional[datetime], cooldown_minutes: int = DEFAULT_COOLDOWN_MINUTES) -> bool:
        """Retorna True si ya pasó el tiempo de enfriamiento"""
        if not last_run:
            return True
        
        # Usar datetime.utcnow() consistente con el resto del sistema
        now = datetime.utcnow()
        elapsed = now - last_run
        return elapsed >= timedelta(minutes=cooldown_minutes)

    @staticmethod
    def should_pause_due_to_performance(metrics: Dict[str, float]) -> bool:
        """
        Evalúa si el rendimiento es tan bajo que requiere pausar.
        metrics esperadas: {"ctr": float, "engagement_rate": float}
        """
        ctr = metrics.get("ctr", 0.0)
        engagement = metrics.get("engagement_rate", 0.0)
        
        # Regla simple: Si ambos están por debajo del mínimo, pausar.
        if ctr < AutonomyPolicy.MIN_CTR_THRESHOLD and engagement < AutonomyPolicy.MIN_ENGAGEMENT_RATE:
            return True
        return False
