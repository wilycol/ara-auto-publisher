import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ai_provider_service import ai_provider_service

async def test_ai_providers():
    print("\n🚀 Iniciando Validación de Multi-IA Providers...\n")
    
    test_prompt = "Genera un JSON simple con un título de prueba. Ejemplo: {'title': 'Hola'}"
    
    # CASO 1: Probar Fallback Local (Forzado)
    print("🔹 Caso 1: Forzando Fallback Local (Simulando API Key inválida)")
    
    # Backup original key if exists
    original_key = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = "" # Borrar key para forzar fallo
    
    # Re-instanciar servicio para que tome el cambio de env (hacky para test)
    # En realidad el servicio lee en init. 
    # Vamos a manipular la instancia directamente para el test.
    ai_provider_service.providers[0].api_key = None 
    ai_provider_service.providers[1].api_key = None
    
    try:
        result = await ai_provider_service.generate(test_prompt)
        print("   Resultado:")
        print(f"   {result[:100]}...")
        
        if "Fallback" in result or "Modo Fallback" in result:
            print("   ✅ ÉXITO: Fallback activado correctamente.")
        else:
            print("   ⚠️ ADVERTENCIA: Se obtuvo resultado pero no parece ser el fallback esperado.")
            
    except Exception as e:
        print(f"   ❌ FALLO: {e}")

    # CASO 2: Probar OpenRouter (Si hay key)
    print("\n🔹 Caso 2: Probando OpenRouter (Si hay key configurada)")
    
    # Restore key
    real_key = "sk-or-v1-..." # Poner key real aquí para probar manualmente, o leer de .env real
    # Como no tengo la key del usuario, este test saltará o fallará controlado si no hay key en entorno.
    
    if original_key:
        os.environ["OPENROUTER_API_KEY"] = original_key
        ai_provider_service.providers[0].api_key = original_key
        ai_provider_service.providers[1].api_key = original_key
        
        try:
            result = await ai_provider_service.generate(test_prompt)
            print("   Resultado OpenRouter:")
            print(f"   {result[:100]}...")
            print("   ✅ ÉXITO: OpenRouter respondió.")
        except Exception as e:
            print(f"   ❌ FALLO OpenRouter: {e}")
            print("   (Esto es esperado si la key es inválida o no hay saldo)")
    else:
        print("   ⚠️ SKIPPING: No hay OPENROUTER_API_KEY en el entorno para probar el caso real.")

if __name__ == "__main__":
    asyncio.run(test_ai_providers())
