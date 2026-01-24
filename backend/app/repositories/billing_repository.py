from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.models.billing import BillingEvent

class BillingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_event(self, event: BillingEvent) -> BillingEvent:
        """
        Persiste un evento de facturación.
        Append-only: No hay updates ni deletes.
        """
        self.db.add(event)
        try:
            self.db.commit()
            self.db.refresh(event)
            return event
        except Exception as e:
            self.db.rollback()
            raise e

    def get_user_events(self, user_id: str, limit: int = 100):
        """Retorna historial reciente (para debugging/soporte)"""
        return self.db.query(BillingEvent)\
            .filter(BillingEvent.user_id == user_id)\
            .order_by(BillingEvent.timestamp.desc())\
            .limit(limit)\
            .all()

    def get_daily_metrics_by_type(self, user_id: str, target_date: datetime.date) -> dict:
        """
        Retorna métricas acumuladas (costo y unidades) por tipo de media para un día.
        Retorna: {"image": {"cost": 0.20, "units": 5}, "video": {"cost": 1.50, "units": 30}}
        """
        start_of_day = datetime(target_date.year, target_date.month, target_date.day)
        end_of_day = start_of_day + timedelta(days=1)

        results = self.db.query(
            BillingEvent.media_type,
            func.sum(BillingEvent.cost_estimated).label("total_cost"),
            func.sum(BillingEvent.units).label("total_units")
        ).filter(
            BillingEvent.user_id == user_id,
            BillingEvent.timestamp >= start_of_day,
            BillingEvent.timestamp < end_of_day
        ).group_by(BillingEvent.media_type).all()

        metrics = {}
        for r in results:
            metrics[r.media_type] = {
                "cost": r.total_cost or 0.0,
                "units": r.total_units or 0.0
            }
        return metrics

    def get_monthly_cost(self, user_id: str, target_date: datetime.date) -> float:
        """
        Retorna el costo total acumulado del mes hasta la fecha.
        """
        start_of_month = datetime(target_date.year, target_date.month, 1)
        # Fin de mes es inicio del siguiente mes
        if target_date.month == 12:
            end_of_month = datetime(target_date.year + 1, 1, 1)
        else:
            end_of_month = datetime(target_date.year, target_date.month + 1, 1)

        result = self.db.query(
            func.sum(BillingEvent.cost_estimated).label("total_cost")
        ).filter(
            BillingEvent.user_id == user_id,
            BillingEvent.timestamp >= start_of_month,
            BillingEvent.timestamp < end_of_month
        ).scalar()

        return result or 0.0
