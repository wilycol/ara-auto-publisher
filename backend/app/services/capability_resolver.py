import json
import os
from typing import Dict, Any
from app.schemas.policy import AgentMode, AgentCapabilities
from app.core.logging import logger
from app.core.database import SessionLocal
from app.repositories.usage_repository import UsageRepository

class CapabilityResolverService:
    def __init__(self, policy_version: str = "v1.1"):
        self.policy_path = os.path.join(
            os.path.dirname(__file__), 
            f"../policies/{policy_version}/agent_modes.json"
        )
        self.agent_modes = self._load_policies()

    def _load_policies(self) -> Dict[str, AgentMode]:
        try:
            with open(self.policy_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                modes = {}
                for name, config in data["agent_modes"].items():
                    modes[name] = AgentMode(**config)
                return modes
        except Exception as e:
            logger.error(f"Failed to load policies from {self.policy_path}: {e}")
            raise RuntimeError("Critical: Could not load agent policies")

    def resolve_capabilities(self, plan: str) -> AgentCapabilities:
        """
        Retorna las capacidades permitidas para un plan dado.
        El plan se mapea directamente al nombre del modo (strict, educational, editorial).
        """
        mode = self.agent_modes.get(plan)
        if not mode:
            # Default to strict if plan not found
            logger.warning(f"Unknown plan '{plan}', defaulting to 'strict'")
            return self.agent_modes["strict"].capabilities
        return mode.capabilities

    def validate_request(self, user_id: str, plan: str, media_type: str, params: dict = None) -> bool:
        """
        Valida si una solicitud de generación de medios está permitida.
        Verifica:
        1. Si el tipo de medio está habilitado para el plan.
        2. Si no se ha excedido la cuota diaria.
        3. Restricciones específicas (ej. duración video).
        """
        capabilities = self.resolve_capabilities(plan)
        
        # 1. Validación de Tipo
        if media_type == "text":
            if not capabilities.text:
                self._log_denial(user_id, plan, media_type, "capability_disabled")
                return False
            return True # Texto ilimitado por ahora
            
        elif media_type == "image":
            cap = capabilities.images
            if not cap.enabled:
                self._log_denial(user_id, plan, media_type, "capability_disabled")
                return False
            
            # 2. Validación de Cuota
            current_usage = self._get_usage(user_id, "image")
            if current_usage >= cap.max_per_day:
                self._log_quota_exceeded(user_id, plan, media_type, cap.max_per_day)
                return False
            
            return True

        elif media_type == "video":
            cap = capabilities.video
            if not cap.enabled:
                self._log_denial(user_id, plan, media_type, "capability_disabled")
                return False
            
            # 2. Validación de Cuota
            current_usage = self._get_usage(user_id, "video")
            if current_usage >= cap.max_per_day:
                self._log_quota_exceeded(user_id, plan, media_type, cap.max_per_day)
                return False
            
            # 3. Restricciones Específicas
            duration = params.get("duration", 0) if params else 0
            if duration > cap.max_duration_seconds:
                self._log_denial(user_id, plan, media_type, f"duration_exceeded_max_{cap.max_duration_seconds}")
                return False

            return True

        return False

    def record_usage(self, user_id: str, media_type: str):
        """Incrementa el contador de uso (Persistido en DB)"""
        db = SessionLocal()
        try:
            repo = UsageRepository(db)
            repo.increment_usage(user_id, media_type)
        except Exception as e:
            logger.error(f"Failed to record usage for {user_id}: {e}")
        finally:
            db.close()

    def _get_usage(self, user_id: str, media_type: str) -> int:
        """Obtiene el uso actual desde DB"""
        db = SessionLocal()
        try:
            repo = UsageRepository(db)
            return repo.get_daily_usage(user_id, media_type)
        except Exception as e:
            logger.error(f"Failed to get usage for {user_id}: {e}")
            return 0 # Fail open in case of DB error to avoid blocking user
        finally:
            db.close()

    def _log_denial(self, user_id: str, plan: str, media_type: str, reason: str):
        logger.warning(json.dumps({
            "event": "capability_denied",
            "user_id": user_id,
            "plan": plan,
            "media_type": media_type,
            "reason": reason
        }))

    def _log_quota_exceeded(self, user_id: str, plan: str, media_type: str, limit: int):
        logger.warning(json.dumps({
            "event": "media_quota_exceeded",
            "user_id": user_id,
            "plan": plan,
            "media_type": media_type,
            "limit": limit
        }))
