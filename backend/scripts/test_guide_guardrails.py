import asyncio
import json
import sys
import os

# Añadir el directorio raíz al path para poder importar modulos de app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.guide_orchestrator import GuideOrchestratorService
from app.schemas.guide import GuideNextRequest, GuideState, GuideOption

# Mock para simular fallos de IA
class ConfigurableMockAI:
    def __init__(self):
        self.mode = "normal" # normal, invalid_json, missing_fields, timeout

    async def generate(self, prompt):
        if self.mode == "normal":
            return json.dumps({
                "message": "Valid response",
                "options": [{"label": "A", "value": "a"}, {"label": "B", "value": "b"}]
            })
        elif self.mode == "invalid_json":
            return "This is not JSON { unclosed brace"
        elif self.mode == "missing_fields":
            return json.dumps({"foo": "bar"}) # No message, no options
        elif self.mode == "malformed_options":
            return json.dumps({
                "message": "Ok",
                "options": "this should be a list"
            })
        elif self.mode == "insufficient_options":
             return json.dumps({
                "message": "Ok",
                "options": [{"label": "Solo una", "value": "1"}]
            })
        elif self.mode == "timeout":
            await asyncio.sleep(11) # > 10s timeout
            return "{}"
        return "{}"

async def run_tests():
    print("🚀 Starting Guardrails QA Test...")
    
    # Setup Service con Mock
    service = GuideOrchestratorService()
    mock_ai = ConfigurableMockAI()
    service.ai_service = mock_ai # Inyección de dependencia manual para el test
    
    # Base Request
    base_req = GuideNextRequest(
        current_step=1,
        state=GuideState(step=1),
        user_input="Test Goal",
        guide_session_id="qa-session-1"
    )

    # ---------------------------------------------------------
    # TEST 1: Invalid JSON
    # ---------------------------------------------------------
    print("\n🧪 TEST 1: Invalid JSON Response...")
    mock_ai.mode = "invalid_json"
    resp = await service._step_audience(base_req, 2, {})
    
    if resp.assistant_message and "Perfecto" in resp.assistant_message:
        print("✅ PASS: System fell back gracefully on Invalid JSON")
    else:
        print(f"❌ FAIL: Unexpected response: {resp.assistant_message}")

    # ---------------------------------------------------------
    # TEST 2: Missing Fields
    # ---------------------------------------------------------
    print("\n🧪 TEST 2: Missing Fields (Schema Validation)...")
    mock_ai.mode = "missing_fields"
    resp = await service._step_audience(base_req, 2, {})
    
    if resp.assistant_message and "Perfecto" in resp.assistant_message:
        print("✅ PASS: System fell back gracefully on Missing Fields")
    else:
        print(f"❌ FAIL: Unexpected response: {resp.assistant_message}")

    # ---------------------------------------------------------
    # TEST 3: Timeout
    # ---------------------------------------------------------
    print("\n🧪 TEST 3: Timeout Protection (>10s)...")
    mock_ai.mode = "timeout"
    
    start_time = asyncio.get_event_loop().time()
    resp = await service._step_audience(base_req, 2, {})
    end_time = asyncio.get_event_loop().time()
    
    duration = end_time - start_time
    print(f"   ⏱️ Duration: {duration:.2f}s")
    
    if duration < 11 and resp.assistant_message:
        print("✅ PASS: Timeout triggered and handled correctly")
    else:
        print("❌ FAIL: Timeout did not trigger or took too long")

    # ---------------------------------------------------------
    # TEST 4: Illegal State Patch
    # ---------------------------------------------------------
    print("\n🧪 TEST 4: Illegal State Patch Guard...")
    # Mockeamos respuesta válida pero con patch ilegal
    mock_ai.mode = "illegal_patch" 
    
    # Inyectamos comportamiento específico en el mock para este caso
    # Nota: Como ConfigurableMockAI es simple, modificaremos su lógica abajo o 
    # simplemente confiamos en que el Orchestrator filtra el patch aunque la IA lo mande.
    # Para probarlo realmente, necesitamos que el Orchestrator reciba un patch sucio.
    # En la implementación actual, el patch se construye en el método _step_X usando datos del request/IA.
    # Vamos a simular un paso donde la IA devuelve datos que se usan para el patch.
    
    # En _step_audience (step 1->2), el patch es {"objective": objective}. 
    # La IA no devuelve el patch directamente en el JSON, el código lo construye.
    # PERO, el guardrail _validate_state_patch se aplica sobre 'state_patch' antes de retornar.
    
    # Para probar esto efectivamente, voy a invocar directamente el validador
    # ya que es una prueba unitaria de la lógica de seguridad.
    
    dirty_patch = {"audience": "valid", "topics": ["HACKED"], "step": 999}
    clean_patch = service._validate_state_patch(dirty_patch, current_step=2, session_id="test-session")
    
    if "topics" not in clean_patch and "step" not in clean_patch and clean_patch.get("audience") == "valid":
        print(f"✅ PASS: Illegal keys removed. Result: {clean_patch}")
    else:
        print(f"❌ FAIL: Patch not sanitized. Result: {clean_patch}")

    print("\n🏁 QA Tests Completed.")

if __name__ == "__main__":
    asyncio.run(run_tests())
