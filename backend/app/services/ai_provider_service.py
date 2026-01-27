from typing import List, Optional, Dict
from app.services.ai_providers.base import AIProviderAdapter
from app.services.ai_providers.openrouter import OpenRouterProvider
from app.services.ai_providers.openai_compatible import OpenAICompatibleProvider
from app.services.ai_providers.gemini import GeminiProvider
from app.services.ai_providers.local import LocalFallbackProvider
from app.core.config import get_settings
from app.core.logging import logger

class AIProviderService:
    """
    Orquestador de proveedores de IA con Fallback Automático.
    Selecciona dinámicamente el mejor proveedor disponible según prioridad y salud.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.providers: List[AIProviderAdapter] = self._initialize_providers()
        
    def _initialize_providers(self) -> List[AIProviderAdapter]:
        providers = []
        priority_list = [p.strip().lower() for p in self.settings.AI_PROVIDER_PRIORITY.split(",")]
        
        for p_name in priority_list:
            if p_name == "openai":
                if self.settings.OPENAI_API_KEY:
                    providers.append(OpenAICompatibleProvider(
                        name="openai",
                        api_key=self.settings.OPENAI_API_KEY,
                        base_url="https://api.openai.com/v1",
                        model="gpt-4o-mini" # Cost effective standard
                    ))
            
            elif p_name == "openrouter":
                if self.settings.OPENROUTER_API_KEY:
                    # OpenRouter usa su propia clase por headers especiales
                    providers.append(OpenRouterProvider(model="mistralai/mistral-7b-instruct"))
            
            elif p_name == "gemini":
                if self.settings.GEMINI_API_KEY:
                    providers.append(GeminiProvider(
                        api_key=self.settings.GEMINI_API_KEY,
                        model="gemini-flash-latest" # Trying latest alias for stability
                    ))
            
            elif p_name == "grok":
                if self.settings.GROK_API_KEY:
                    providers.append(OpenAICompatibleProvider(
                        name="grok",
                        api_key=self.settings.GROK_API_KEY,
                        base_url="https://api.x.ai/v1",
                        model="grok-beta"
                    ))
        
        # SIEMPRE al final: Fallback Local
        providers.append(LocalFallbackProvider())
        
        # Log providers loaded
        loaded_names = [p.name for p in providers]
        logger.info(f"🤖 AI Providers Initialized: {loaded_names}")
        
        return providers

    def is_real_ai_available(self) -> bool:
        """
        Verifica si hay al menos un proveedor de 'IA Real' configurado.
        No garantiza salud en tiempo real, solo configuración.
        """
        for provider in self.providers:
            if not isinstance(provider, LocalFallbackProvider):
                return True
        return False

    async def check_health(self) -> dict:
        """
        Busca el PRIMER proveedor saludable en la lista de prioridad.
        """
        for provider in self.providers:
            # Fallback local siempre es "último recurso"
            if isinstance(provider, LocalFallbackProvider):
                continue
            
            # Check real (con ping de red)
            is_healthy = await provider.check_health()
            if is_healthy:
                return {
                    "status": "connected", 
                    "provider": provider.name, 
                    "is_real_ai": True
                }
        
        # Si llegamos aquí, ningún proveedor real respondió
        return {
            "status": "disconnected", 
            "provider": "none", 
            "is_real_ai": False
        }

    async def generate(self, prompt: str, skip_fallback: bool = False, **kwargs) -> str:
        """
        Intenta generar contenido rotando proveedores en caso de fallo.
        """
        last_error = None
        
        for provider in self.providers:
            if skip_fallback and isinstance(provider, LocalFallbackProvider):
                continue

            try:
                # Opcional: Podríamos hacer check_health antes, pero añade latencia.
                # Confiamos en try/except para failover rápido.
                
                result = await provider.generate(prompt, **kwargs)
                return result
                
            except Exception as e:
                logger.warning(f"⚠️ Falló proveedor {provider.name}: {str(e)}")
                last_error = e
                continue
        
        # Fallo total
        logger.error("❌ Todos los proveedores de IA fallaron.")
        raise last_error or Exception("IA Real no disponible y Fallback omitido")

# Singleton instance
ai_provider_service = AIProviderService()
