from typing import List, Optional
from app.services.ai_providers.base import AIProviderAdapter
from app.services.ai_providers.openrouter import OpenRouterProvider
from app.services.ai_providers.local import LocalFallbackProvider
from app.core.logging import logger

class AIProviderService:
    """
    Orquestador de proveedores de IA.
    Implementa patrón Chain of Responsibility / Fallback.
    """
    
    def __init__(self):
        import os
        
        # Check if we are in Forced Local Mode (e.g. for testing)
        force_local = os.getenv("AI_PROVIDER") == "local"
        
        if force_local:
            logger.info("🔧 MODO FORZADO: Usando SOLO LocalFallbackProvider")
            self.providers: List[AIProviderAdapter] = [
                LocalFallbackProvider()
            ]
        else:
            # Configurar cadena de proveedores en orden de prioridad
            self.providers: List[AIProviderAdapter] = [
                OpenRouterProvider(model="mistralai/mistral-7b-instruct"), # Opción 1: Mistral (Balanceado)
                OpenRouterProvider(model="openchat/openchat-7b"),          # Opción 2: OpenChat (Gratis/Barato)
                LocalFallbackProvider()                                    # Opción Final: Fallback Local
            ]
    
    def is_real_ai_available(self) -> bool:
        """
        Verifica si hay al menos un proveedor de 'IA Real' configurado y activo.
        """
        for provider in self.providers:
            if not isinstance(provider, LocalFallbackProvider):
                return True
        return False

    async def generate(self, prompt: str, skip_fallback: bool = False, **kwargs) -> str:
        """
        Intenta generar contenido usando los proveedores en orden.
        Si skip_fallback=True, ignora proveedores locales/dummy.
        """
        last_error = None
        
        for provider in self.providers:
            if skip_fallback and isinstance(provider, LocalFallbackProvider):
                continue

            try:
                # logger.info(f"🤖 Intentando generación con proveedor: {provider.name} ({getattr(provider, 'model', '')})")
                # Reducimos log level para no ensuciar tanto, o lo mantenemos info para trazabilidad
                
                result = await provider.generate(prompt, **kwargs)
                
                # logger.info(f"✅ Generación exitosa con {provider.name}")
                return result
                
            except Exception as e:
                logger.warning(f"⚠️ Falló proveedor {provider.name}: {str(e)}")
                last_error = e
                continue
        
        # Si llegamos aquí, fallaron todos los proveedores elegibles
        logger.error("❌ Todos los proveedores de IA fallaron (o fueron omitidos).")
        raise last_error or Exception("IA Real no disponible")

# Singleton instance
ai_provider_service = AIProviderService()
