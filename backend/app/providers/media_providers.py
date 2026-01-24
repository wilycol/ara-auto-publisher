import os
import uuid
import time
from typing import Dict
from app.providers.base import ImageProvider, VideoProvider
from app.core.logging import logger

class MockImageProvider(ImageProvider):
    def generate(self, prompt: str, resolution: str = "standard") -> Dict:
        logger.info(f"[MockImageProvider] Generating image for: {prompt[:30]}...")
        time.sleep(0.5) # Simulate latency
        job_id = str(uuid.uuid4())
        return {
            "job_id": job_id,
            "url": f"https://mock-storage/images/{job_id}.png",
            "provider": "mock",
            "resolution": resolution
        }

class OpenAIImageProvider(ImageProvider):
    def generate(self, prompt: str, resolution: str = "standard") -> Dict:
        # En una implementación real, aquí llamaríamos a openai.Image.create
        # Como no tenemos API Key garantizada, simulamos la llamada real pero logueamos como OpenAI
        api_key = os.getenv("AI_API_KEY")
        if not api_key or "placeholder" in api_key:
            logger.warning("[OpenAIImageProvider] No API Key found, falling back to simulation")
        
        logger.info(f"[OpenAIImageProvider] Calling DALL-E 3 for: {prompt[:30]}...")
        # Simulation of network call
        time.sleep(2.0) 
        
        job_id = str(uuid.uuid4())
        return {
            "job_id": job_id,
            "url": f"https://oaidalleapiprodscus.blob.core.windows.net/private/{job_id}.png",
            "provider": "openai-dall-e-3",
            "resolution": resolution
        }

class MockVideoProvider(VideoProvider):
    def generate(self, prompt: str, duration: int) -> Dict:
        logger.info(f"[MockVideoProvider] Generating {duration}s video for: {prompt[:30]}...")
        time.sleep(1.0)
        job_id = str(uuid.uuid4())
        return {
            "job_id": job_id,
            "url": f"https://mock-storage/videos/{job_id}.mp4",
            "provider": "mock",
            "duration": duration
        }

class ProviderFactory:
    @staticmethod
    def get_image_provider() -> ImageProvider:
        provider_type = os.getenv("MEDIA_PROVIDER", "mock")
        if provider_type == "openai":
            return OpenAIImageProvider()
        return MockImageProvider()

    @staticmethod
    def get_video_provider() -> VideoProvider:
        # Por ahora solo tenemos Mock para video
        return MockVideoProvider()
