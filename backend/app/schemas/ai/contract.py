from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AIRequest(BaseModel):
    """Contrato de petición al AI Engine"""
    prompt: str
    context: Optional[str] = None
    tone: Optional[str] = "neutral"
    max_length: Optional[int] = 500
    model: str = "deepseek-r1" # Default, pero sobreescribible
    
    # Parámetros extra para flexibilidad (temperature, etc)
    parameters: Dict[str, Any] = {}

class AIResponse(BaseModel):
    """Contrato de respuesta del AI Engine"""
    title: str
    content: str
    raw_response: Dict[str, Any] = {}
    
    # Campos opcionales para flexibilidad futura
    suggested_image_prompt: Optional[str] = None
    tokens_used: Optional[int] = 0
