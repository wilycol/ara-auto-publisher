from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from app.models.tracking import ImpactMetric, ContentTracking

class ImpactRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_metric(self, metric: ImpactMetric) -> ImpactMetric:
        """Registra una nueva métrica (snapshot)"""
        self.db.add(metric)
        try:
            self.db.commit()
            self.db.refresh(metric)
            return metric
        except Exception:
            self.db.rollback()
            raise

    def get_by_content(self, content_id: int) -> List[ImpactMetric]:
        """Obtiene historial de métricas para un contenido"""
        return self.db.query(ImpactMetric)\
            .filter(ImpactMetric.tracking_id == content_id)\
            .order_by(desc(ImpactMetric.captured_at))\
            .all()

    def get_metrics_report(
        self,
        project_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ImpactMetric]:
        """Consulta métricas con filtros (requiere join si filtra por proyecto)"""
        query = self.db.query(ImpactMetric).join(ContentTracking)

        if project_id:
            query = query.filter(ContentTracking.project_id == project_id)
        
        if start_date:
            query = query.filter(ImpactMetric.captured_at >= start_date)
            
        if end_date:
            query = query.filter(ImpactMetric.captured_at <= end_date)

        return query.order_by(desc(ImpactMetric.captured_at)).limit(limit).all()
