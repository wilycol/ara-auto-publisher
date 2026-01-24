import json
import os
import uuid
from datetime import datetime
from typing import Optional
from app.core.logging import logger
from app.models.billing import BillingEvent
from app.repositories.billing_repository import BillingRepository
from sqlalchemy.orm import Session

class BillingService:
    def __init__(self, db: Session, policy_version: str = "v1.0"):
        self.db = db
        self.repo = BillingRepository(db)
        self.policy_version = policy_version
        self.pricing_table = self._load_pricing()

    def _load_pricing(self) -> dict:
        """Carga la tabla de precios versionada"""
        path = os.path.join(
            os.path.dirname(__file__), 
            f"../policies/pricing/{self.policy_version}.json"
        )
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"CRITICAL: Failed to load pricing table {path}: {e}")
            raise RuntimeError("Billing System Failure: Pricing table not found")

    def _calculate_cost(self, plan: str, media_type: str, units: float) -> float:
        """Calcula costo basado en el plan y tipo de medio"""
        plans = self.pricing_table.get("plans", {})
        plan_config = plans.get(plan)
        
        if not plan_config:
            logger.warning(f"Billing: Unknown plan '{plan}', defaulting to 0 cost")
            return 0.0
            
        media_config = plan_config.get(media_type)
        if not media_config:
            logger.warning(f"Billing: Unknown media_type '{media_type}' for plan '{plan}'")
            return 0.0
            
        unit_price = media_config.get("unit_price", 0.0)
        return round(unit_price * units, 6)

    def record_usage_event(self, 
                          user_id: str, 
                          plan: str, 
                          media_type: str, 
                          provider: str, 
                          units: float,
                          unit_type: str,
                          correlation_id: Optional[str] = None) -> BillingEvent:
        """
        Registra un evento facturable.
        Traduce uso técnico -> impacto financiero.
        """
        # 1. Calcular Costo
        cost = self._calculate_cost(plan, media_type, units)
        
        # 2. Generar Correlation ID si no existe
        cid = correlation_id or str(uuid.uuid4())
        
        # 3. Crear Entidad
        event = BillingEvent(
            user_id=user_id,
            plan=plan,
            media_type=media_type,
            provider=provider,
            units=units,
            unit_type=unit_type,
            cost_estimated=cost,
            currency=self.pricing_table.get("currency", "USD"),
            correlation_id=cid,
            timestamp=datetime.utcnow(),
            pricing_version=self.policy_version
        )
        
        # 4. Persistir
        saved_event = self.repo.create_event(event)
        
        # 5. Log Estructurado (Observabilidad Fase 7.1)
        logger.info(json.dumps({
            "event": "billing_event_created",
            "billing_id": saved_event.id,
            "correlation_id": cid,
            "user_id": user_id,
            "cost": cost,
            "currency": saved_event.currency,
            "plan": plan,
            "provider": provider
        }))
        
        return saved_event
