from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.tracking import ImpactMetric
from app.repositories.impact_repository import ImpactRepository

class ImpactService:
    def __init__(self, db: Session):
        self.repo = ImpactRepository(db)

    def record_snapshot(self, content_id: int, data: Dict[str, Any]) -> ImpactMetric:
        """
        Registra un snapshot de métricas para un contenido.
        data: {
            "impressions": 100,
            "clicks": 5,
            ...
            "source": "manual"
        }
        """
        metric = ImpactMetric(
            tracking_id=content_id,
            impressions=data.get("impressions", 0),
            clicks=data.get("clicks", 0),
            reactions=data.get("reactions", 0),
            comments=data.get("comments", 0),
            shares=data.get("shares", 0),
            source=data.get("source", "manual"),
            captured_at=datetime.utcnow()
        )
        return self.repo.add_metric(metric)

    def get_content_performance(self, content_id: int) -> Dict[str, Any]:
        """Calcula rendimiento actual (último snapshot + calculados)"""
        metrics = self.repo.get_by_content(content_id)
        if not metrics:
            return {"status": "no_data"}
        
        latest = metrics[0] # Ordered by desc date
        
        # Cálculos básicos
        ctr = (latest.clicks / latest.impressions * 100) if latest.impressions > 0 else 0.0
        total_engagement = latest.reactions + latest.comments + latest.shares
        engagement_rate = (total_engagement / latest.impressions * 100) if latest.impressions > 0 else 0.0
        
        return {
            "content_id": content_id,
            "latest_snapshot": latest.captured_at,
            "metrics": {
                "impressions": latest.impressions,
                "clicks": latest.clicks,
                "engagement": total_engagement
            },
            "kpis": {
                "ctr_percent": round(ctr, 2),
                "engagement_rate_percent": round(engagement_rate, 2)
            },
            "history_count": len(metrics)
        }

    def get_aggregated_metrics(self, content_id: int) -> Dict[str, float]:
        """
        Retorna diccionario plano con métricas clave para análisis.
        Se usa en PerformanceFeedbackService.
        """
        perf = self.get_content_performance(content_id)
        if perf.get("status") == "no_data":
            return {"ctr": 0.0, "engagement_rate": 0.0}
            
        kpis = perf.get("kpis", {})
        return {
            "ctr": kpis.get("ctr_percent", 0.0),
            "engagement_rate": kpis.get("engagement_rate_percent", 0.0)
        }
