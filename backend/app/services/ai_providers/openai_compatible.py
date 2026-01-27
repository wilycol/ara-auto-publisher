import httpx
from app.services.ai_providers.base import AIProviderAdapter
from app.core.config import get_settings

class OpenAICompatibleProvider(AIProviderAdapter):
    """
    Adaptador genérico para cualquier proveedor compatible con la API de OpenAI.
    (OpenAI, Grok, DeepSeek, etc.)
    """
    def __init__(self, name: str, api_key: str, base_url: str, model: str, headers: dict = None):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.custom_headers = headers or {}

    async def check_health(self) -> bool:
        if not self.api_key:
            return False
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            **self.custom_headers
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                # Intento 1: Listar modelos (Standard OpenAI)
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return True
                
                # Si falla auth explícitamente -> ROJO
                if response.status_code in [401, 403]:
                    return False
                    
                return False
                
            except Exception:
                return False

    async def generate(self, prompt: str, **kwargs) -> str:
        if not self.api_key:
            raise ValueError(f"API Key no configurada para {self.name}")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            **self.custom_headers
        }
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000)
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code in [401, 403]:
                    raise ValueError(f"Auth Error {self.name}: {response.text}")
                    
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    raise ValueError(f"Respuesta vacía de {self.name}")
                    
            except Exception as e:
                raise e
