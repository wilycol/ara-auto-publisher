from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.domain import MediaUsage

class UsageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_daily_usage(self, user_id: str, media_type: str) -> int:
        """Obtiene el consumo acumulado del día actual (UTC)"""
        today = datetime.utcnow().date()
        # Convertimos date a datetime para comparar (SQLite a veces es tricky con fechas)
        # Asumiremos que guardamos datetime truncado a medianoche
        today_dt = datetime(today.year, today.month, today.day)
        
        usage = self.db.query(MediaUsage).filter(
            MediaUsage.user_id == user_id,
            MediaUsage.media_type == media_type,
            MediaUsage.date == today_dt
        ).first()
        
        return usage.count if usage else 0

    def get_all_daily_usage(self, user_id: str) -> dict:
        """
        Retorna todos los contadores de uso del día actual.
        Retorna: {"image": 5, "video": 2}
        """
        today = datetime.utcnow().date()
        today_dt = datetime(today.year, today.month, today.day)

        results = self.db.query(MediaUsage).filter(
            MediaUsage.user_id == user_id,
            MediaUsage.date == today_dt
        ).all()

        return {r.media_type: r.count for r in results}

    def increment_usage(self, user_id: str, media_type: str) -> int:
        """Incrementa el consumo y retorna el nuevo valor"""
        today = datetime.utcnow().date()
        today_dt = datetime(today.year, today.month, today.day)
        
        usage = self.db.query(MediaUsage).filter(
            MediaUsage.user_id == user_id,
            MediaUsage.media_type == media_type,
            MediaUsage.date == today_dt
        ).first()
        
        if usage:
            usage.count += 1
        else:
            usage = MediaUsage(
                user_id=user_id,
                media_type=media_type,
                date=today_dt,
                count=1
            )
            self.db.add(usage)
        
        try:
            self.db.commit()
            self.db.refresh(usage)
            return usage.count
        except Exception:
            self.db.rollback()
            raise
