import httpx
import os
from app.services.ai_providers.base import AIProviderAdapter
from app.core.config import get_settings

class OpenRouterProvider(AIProviderAdapter):
    """
    Adaptador para OpenRouter.
    Permite acceso a múltiples modelos (Mistral, Llama, etc.) a través de una API unificada.
    """
    name: str = "openrouter"
    
    def __init__(self, model: str = "mistralai/mistral-7b-instruct"):
        self.api_key = os.getenv("AI_API_KEY") # Use standard AI_API_KEY from .env
        if not self.api_key:
             # Fallback to settings
             settings = get_settings()
             self.api_key = settings.AI_API_KEY
             
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        
    async def generate(self, prompt: str, **kwargs) -> str:
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY no configurada")
            
        model_to_use = kwargs.get("model", self.model)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://ara-autopublisher.local", # Requerido por OpenRouter
            "X-Title": "Ara Auto Publisher"
        }
        
        payload = {
            "model": model_to_use,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
            # Force JSON mode if requested via kwargs or implied by prompt? 
            # OpenRouter supports response_format={"type": "json_object"} for some models.
            # For now, we stick to prompt engineering for JSON.
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                # Extraer contenido
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    raise ValueError(f"Respuesta inesperada de OpenRouter: {data}")
                    
            except httpx.HTTPStatusError as e:
                # Capturar errores HTTP específicos
                raise ValueError(f"Error HTTP OpenRouter: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                # Capturar errores de conexión/timeout
                raise ValueError(f"Error de conexión OpenRouter: {str(e)}")
            except Exception as e:
                raise ValueError(f"Error desconocido en OpenRouter: {str(e)}")
