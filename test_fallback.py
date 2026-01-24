
import asyncio
import json

# Simulación de la clase base
class AIProviderAdapter:
    pass

# Copia exacta de la lógica modificada (sin imports externos)
class LocalFallbackProvider(AIProviderAdapter):
    """
    Proveedor de respaldo local.
    Nunca falla. Devuelve contenido genérico estructurado.
    Útil para desarrollo offline o cuando se acaban los créditos.
    """
    name: str = "local_fallback"
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Devuelve un JSON válido simulado, adaptándose al contexto del prompt.
        """
        
        # Detección robusta de contexto: Guía vs Generación de Posts
        prompt_lower = prompt.lower()
        is_guide_request = (
            "guideoption" in prompt_lower or 
            "message" in prompt_lower or 
            "state_patch" in prompt_lower or
            "modo colaborador" in prompt_lower or
            "modo experto" in prompt_lower or
            "modo guía" in prompt_lower or
            "arapost manager" in prompt_lower
        )
        
        if is_guide_request:
            # Intentar extraer el input del usuario para personalizar la respuesta (Simulación de "eco")
            # Buscamos "INPUT USUARIO:\n" o similar
            user_echo = ""
            try:
                if "INPUT USUARIO:" in prompt:
                    parts = prompt.split("INPUT USUARIO:")
                    if len(parts) > 1:
                        # Tomar la siguiente línea o el contenido entre comillas
                        raw_input = parts[1].strip().split("\n")[0].strip('"')
                        if raw_input and len(raw_input) > 2:
                            user_echo = f" (Entendido: '{raw_input}')"
            except:
                pass

            fallback_guide = {
                "message": f"¡Hola! 👋 Parece que mi conexión neuronal (IA) está inestable, pero te escucho{user_echo}. Cuéntame más detalles sobre tu objetivo para poder avanzar.",
                "options": [
                    {"label": "Continuar", "value": "continue"},
                    {"label": "Reintentar conexión", "value": "retry"}
                ],
                "state_patch": {},
                "updated_summary": "Conversación en modo respaldo local."
            }
            return json.dumps(fallback_guide, ensure_ascii=False)
        
        # Default: Fallback para generación de posts
        fallback_content = {
            "title": "Contenido Generado (Modo Fallback)",
            "content": "Este es un contenido generado automáticamente en modo de respaldo. "
                       "El proveedor principal de IA no estaba disponible. "
                       "Por favor, edite este borrador antes de aprobarlo.",
            "hashtags": ["#Fallback", "#AraAutoPublisher", "#ModoSeguro"],
            "cta": "Revise la configuración de IA",
            "platform": "linkedin"
        }
        
        return json.dumps(fallback_content, ensure_ascii=False)

async def test_fallback():
    provider = LocalFallbackProvider()
    
    # Prompt típico de colaborador
    prompt = """
    Eres AraPost Manager en MODO COLABORADOR.
    INPUT USUARIO:
    "Hola, soy Wily y quiero vender zapatos"
    FORMATO RESPUESTA (JSON): { "message": ... }
    """
    
    print(f"Testing prompt with length: {len(prompt)}")
    response = await provider.generate(prompt)
    print("\n--- Response ---")
    print(response)
    
    try:
        data = json.loads(response)
        print("\n✅ Valid JSON")
        print(f"Message: {data.get('message')}")
        
        if "Wily" in data.get('message'):
             print("✅ User input echoed correctly")
        else:
             print("❌ User input NOT echoed")
             
    except Exception as e:
        print(f"\n❌ Invalid JSON: {e}")

if __name__ == "__main__":
    asyncio.run(test_fallback())
