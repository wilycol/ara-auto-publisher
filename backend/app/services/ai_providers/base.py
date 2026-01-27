from abc import ABC, abstractmethod

class AIProviderAdapter(ABC):
    """
    Interface base para adaptadores de proveedores de IA.
    Define el contrato común que deben cumplir OpenRouter, Groq, LocalFallback, etc.
    """
    name: str = "base"
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Genera texto a partir de un prompt.
        Debe lanzar excepción controlada si falla.
        
        Args:
            prompt (str): El texto de entrada para el modelo.
            **kwargs: Parámetros adicionales (ej: temperature, max_tokens, model_name).
            
        Returns:
            str: El texto generado por el modelo.
        """
        pass

    async def check_health(self) -> bool:
        """
        Verifica si el proveedor está disponible y la API Key es válida.
        Por defecto retorna True (asume disponible si no se implementa).
        """
        return True
