from app.schemas.ai import AIRequest, AIResponse
import time
import httpx
from typing import Optional

class AIClientInterface:
    def generate_content(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError

class MockAIClient(AIClientInterface):
    """
    Cliente simulado para desarrollo y pruebas.
    No consume créditos ni requiere conexión real.
    """
    def generate_content(self, request: AIRequest) -> AIResponse:
        # Simular latencia de red/procesamiento
        time.sleep(0.5)
        
        return AIResponse(
            title=f"Post sobre {request.prompt[:20]}...",
            content=f"[MOCK CONTENT] Generado para prompt: {request.prompt[:50]}...\n\nEste es un contenido simulado que cumple con el tono {request.tone}.",
            raw_response={"mock": True, "latency": 500},
            suggested_image_prompt=f"Una imagen artística representando: {request.prompt[:30]}",
            tokens_used=42
        )

class OpenAICompatibleClient(AIClientInterface):
    """
    Cliente para proveedores compatibles con OpenAI API (DeepSeek, LLaMA, GPT-4).
    """
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def generate_content(self, request: AIRequest) -> AIResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"You are a social media expert. Tone: {request.tone}. Context: {request.context}. Return a title in the first line, then the post content."},
                {"role": "user", "content": request.prompt}
            ],
            "max_tokens": request.max_length,
            "temperature": 0.7
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                full_text = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                
                # Simple parsing: First line is title, rest is content
                parts = full_text.split("\n", 1)
                title = parts[0].strip()[:100] # Limit title length
                content = parts[1].strip() if len(parts) > 1 else full_text
                
                # Simple heurística para extraer sugerencia de imagen
                image_prompt = f"Image inspired by: {title}..." 
                
                return AIResponse(
                    title=title,
                    content=content,
                    raw_response=data,
                    suggested_image_prompt=image_prompt,
                    tokens_used=tokens
                )
        except Exception as e:
            # Fallback seguro o re-raise
            raise RuntimeError(f"AI Provider Error: {str(e)}")
