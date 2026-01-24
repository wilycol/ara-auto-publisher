import json
import uuid
from app.services.capability_resolver import CapabilityResolverService
from app.core.logging import logger
from app.providers.media_providers import ProviderFactory
from app.services.budget_guard_service import BudgetGuardService
from app.services.tracking_service import TrackingService
from app.core.database import SessionLocal

class MediaStubBase:
    def __init__(self, capability_service: CapabilityResolverService):
        self.cap_service = capability_service

    def _check_budget(self, user_id: str, plan: str):
        """Verifica presupuesto antes de ejecutar"""
        db = SessionLocal()
        try:
            guard = BudgetGuardService(db)
            guard.check_limits(user_id, plan)
        finally:
            db.close()

    def _record_tracking(self, user_id: str, media_type: str, url: str, params: dict):
        """Registra en tracking store"""
        db = SessionLocal()
        try:
            service = TrackingService(db)
            service.record_generation({
                "user_id": user_id,
                "project_id": 0, # Placeholder, needs context passing in future
                "project_name": "Unknown", # Needs context
                "platform": "unknown", # Needs context
                "content_type": media_type,
                "generated_url": url,
                "status": "generated",
                "notes": str(params)
            })
        except Exception as e:
            logger.error(f"Failed to record tracking: {e}")
        finally:
            db.close()

    def _log_job_created(self, user_id: str, media_type: str, job_id: str, params: dict):
        logger.info(json.dumps({
            "event": "media_job_created",
            "job_id": job_id,
            "user_id": user_id,
            "media_type": media_type,
            "params": params,
            "status": "queued"
        }))

class ImageGeneratorStub(MediaStubBase):
    def generate(self, user_id: str, plan: str, prompt: str, resolution: str = "standard") -> dict:
        # 1. Validar Capacidad
        if not self.cap_service.validate_request(user_id, plan, "image"):
            raise PermissionError("Image generation denied by policy")
            
        # 1.5 Validar Presupuesto (Fase 7.2)
        self._check_budget(user_id, plan)
            
        # 2. Registrar Uso (Persistido)
        self.cap_service.record_usage(user_id, "image")
        
        # 3. Provider Ejecuta
        provider = ProviderFactory.get_image_provider()
        try:
            result = provider.generate(prompt, resolution)
        except Exception as e:
            logger.error(f"Image Provider failed for user {user_id}: {e}")
            raise e

        # 4. Log Obligatorio
        # Usamos job_id del provider o generamos uno si falta
        job_id = result.get("job_id", str(uuid.uuid4()))
        
        self._log_job_created(user_id, "image", job_id, {"prompt": prompt, "resolution": resolution})
        
        return result

class VideoGeneratorStub(MediaStubBase):
    def generate(self, user_id: str, plan: str, prompt: str, duration: int) -> dict:
        # 1. Validar Capacidad
        if not self.cap_service.validate_request(user_id, plan, "video"):
            raise PermissionError("Video generation denied by policy")
            
        # 1.5 Validar Presupuesto (Fase 7.2)
        self._check_budget(user_id, plan)
            
        # 2. Registrar Uso (Persistido)
        self.cap_service.record_usage(user_id, "video")
        
        # 3. Provider Ejecuta
        provider = ProviderFactory.get_video_provider()
        try:
            result = provider.generate(prompt, duration)
        except Exception as e:
            logger.error(f"Video Provider failed for user {user_id}: {e}")
            raise e
            
        # 4. Log Obligatorio
        job_id = result.get("job_id", str(uuid.uuid4()))
        
        self._log_job_created(user_id, "video", job_id, {"prompt": prompt, "duration": duration})
        
        # 5. Tracking (Fase 8)
        self._record_tracking(user_id, "video", result.get("url", ""), {"prompt": prompt})

        return result
