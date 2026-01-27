import httpx
from app.services.ai_providers.base import AIProviderAdapter

class GeminiProvider(AIProviderAdapter):
    """
    Adaptador nativo para Google Gemini API.
    """
    name: str = "gemini"
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def check_health(self) -> bool:
        if not self.api_key:
            return False
            
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                # Verificar modelo específico (get info)
                # GET https://generativelanguage.googleapis.com/v1beta/models/gemini-pro?key=API_KEY
                response = await client.get(
                    f"{self.base_url}/{self.model}",
                    params={"key": self.api_key}
                )
                
                return response.status_code == 200
            except Exception:
                return False

    async def generate(self, prompt: str, **kwargs) -> str:
        if not self.api_key:
            raise ValueError("Gemini API Key missing")
            
        url = f"{self.base_url}/{self.model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 2000)
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                params={"key": self.api_key},
                json=payload
            )
            
            if response.status_code in [401, 403]:
                raise ValueError(f"Gemini Auth Error: {response.text}")
                
            response.raise_for_status()
            data = response.json()
            
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                raise ValueError(f"Gemini response parsing error: {data}")
