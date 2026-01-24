import json
import os
import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.billing_repository import BillingRepository

logger = logging.getLogger(__name__)

class BudgetGuardService:
    def __init__(self, db: Session, policy_version: str = "v1.0"):
        self.db = db
        self.repo = BillingRepository(db)
        self.policy_version = policy_version
        self.policy = self._load_policy()

    def _load_policy(self) -> dict:
        """Carga la política de presupuestos"""
        path = os.path.join(
            os.path.dirname(__file__), 
            f"../policies/budget/{self.policy_version}.json"
        )
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"CRITICAL: Failed to load budget policy {path}: {e}")
            # Fallback seguro: bloquear todo si no hay policy (o permitir free? mejor fail-safe)
            # En este caso, retornamos un default mínimo para no romper todo el sistema
            return {"free": {"monthly_usd": 0.0}}

    def check_limits(self, user_id: str, plan: str, correlation_id: str = None) -> None:
        """
        Verifica si el usuario ha excedido su presupuesto mensual.
        - Hard Limit (100%): Lanza excepción y bloquea.
        - Soft Limit (80%): Loguea advertencia.
        """
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # 1. Obtener límite del plan
        plan_config = self.policy.get(plan)
        if not plan_config:
            logger.warning(f"Plan {plan} not found in budget policy. Defaulting to 0 limit.")
            limit_usd = 0.0
        else:
            limit_usd = plan_config.get("monthly_usd", 0.0)

        # Si el límite es 0 o negativo, asumimos que no hay budget (o es free tier estricto)
        # Si es free tier (0), cualquier costo > 0 bloquea.
        
        # 2. Consultar gasto actual del mes
        today = datetime.utcnow().date()
        current_usd = self.repo.get_monthly_cost(user_id, today)

        # 3. Validar Hard Limit (100%)
        # Para free tier (limit=0), si current > 0 ya se pasó.
        # Pero permitimos gasto 0 siempre.
        # Si el usuario intenta generar algo que cuesta dinero, el billing service lo registrará DESPUÉS.
        # Aquí estamos previniendo. Pero no sabemos cuánto costará la PRÓXIMA acción exactamente aquí 
        # (aunque podríamos estimarlo, el prompt dice "basado en BillingRepository" que es histórico).
        # Asumiremos que si ya alcanzó el límite, no puede hacer MÁS.
        
        if current_usd >= limit_usd:
            # Caso especial: Si el límite es > 0, es un bloqueo real.
            # Si el límite es 0 (Free), y current es 0, técnicamente está al 100%.
            # Pero si es Free, el costo de las acciones permitidas (si las hay gratis) debería ser 0.
            # Si intenta hacer algo de pago siendo Free, el billing detectará costo > 0.
            # Sin embargo, el Guard debe bloquear si YA se gastó el presupuesto.
            # Si limit es 0, y current es 0, ¿bloqueamos? 
            # Depende si la acción va a costar. Pero el Guard no sabe la acción futura en este método genérico.
            # Asumiremos: Si limit > 0 y current >= limit -> Bloqueo.
            # Si limit == 0 -> Bloqueo si current >= limit (es decir, siempre que current >= 0? No).
            # Si limit es 0, significa "Presupuesto $0". Solo puede hacer cosas gratis.
            # Si ya gastó algo (current > 0) y su limite es 0, bloqueo.
            
            if limit_usd > 0 or current_usd > 0:
                self._log_event(
                    "billing_hard_limit_blocked", 
                    user_id, plan, limit_usd, current_usd, correlation_id
                )
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"Budget limit reached for plan {plan}. Limit: ${limit_usd}, Used: ${current_usd}"
                )

        # 4. Validar Soft Limit (80%)
        # Solo aplica si hay un límite > 0
        if limit_usd > 0:
            soft_limit = limit_usd * 0.8
            if current_usd >= soft_limit:
                self._log_event(
                    "billing_soft_limit_reached",
                    user_id, plan, limit_usd, current_usd, correlation_id
                )

    def _log_event(self, event_name: str, user_id: str, plan: str, limit: float, current: float, correlation_id: str):
        payload = {
            "event": event_name,
            "user_id": user_id,
            "plan": plan,
            "limit_usd": limit,
            "current_usd": current,
            "correlation_id": correlation_id
        }
        logger.info(json.dumps(payload))
