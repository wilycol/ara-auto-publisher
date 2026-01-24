import json
import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.billing_repository import BillingRepository
from app.repositories.usage_repository import UsageRepository

logger = logging.getLogger(__name__)

class UsageSnapshotService:
    def __init__(self, db: Session):
        self.db = db
        self.billing_repo = BillingRepository(db)
        self.usage_repo = UsageRepository(db)

    def generate_daily_snapshot(self, user_id: str, plan: str, correlation_id: str = None) -> dict:
        """
        Genera un snapshot del uso diario y costos acumulados.
        """
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        today = datetime.utcnow().date()
        
        # 1. Obtener contadores de uso (Source: MediaUsage)
        usage_counts = self.usage_repo.get_all_daily_usage(user_id)
        
        # 2. Obtener métricas acumuladas (Source: BillingRepository)
        billing_metrics = self.billing_repo.get_daily_metrics_by_type(user_id, today)
        
        # 3. Construir respuesta
        snapshot = {
            "user_id": user_id,
            "plan": plan,
            "period": "daily",
            "usage": {},
            "total_cost": 0.0
        }
        
        # Unir claves
        all_media_types = set(usage_counts.keys()) | set(billing_metrics.keys())
        
        total_cost = 0.0
        
        for media_type in all_media_types:
            count = usage_counts.get(media_type, 0)
            metrics = billing_metrics.get(media_type, {"cost": 0.0, "units": 0.0})
            
            entry = {
                "count": count,
                "cost": round(metrics["cost"], 4)
            }
            
            # Para video, agregar seconds (basado en units de billing)
            if media_type == "video":
                entry["seconds"] = metrics["units"]
                
            snapshot["usage"][media_type] = entry
            total_cost += metrics["cost"]
            
        snapshot["total_cost"] = round(total_cost, 4)
        
        # 4. Log Estructurado (Obligatorio)
        log_payload = {
            "event": "usage_snapshot_generated",
            "user_id": user_id,
            "plan": plan,
            "total_cost": snapshot["total_cost"],
            "correlation_id": correlation_id
        }
        logger.info(json.dumps(log_payload))
        
        return snapshot
