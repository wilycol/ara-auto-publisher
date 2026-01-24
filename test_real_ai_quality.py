import requests
import json
import time

def test_real_ai_collaborator():
    print("\n" + "="*60)
    print("🚀 TEST DE PRIMERA DIVISIÓN: CALIDAD DE IA REAL")
    print("="*60)

    url = "http://localhost:8000/api/v1/guide/next"
    
    # Payload simulates a user entering Collaborator mode with a specific strategic intent
    payload = {
        "current_step": 0,
        "mode": "collaborator",
        "user_input": "Quiero vender mis servicios de auditoría de ciberseguridad para e-commerce. Tengo mucha experiencia técnica pero me cuesta vender el valor de negocio. ¿Qué publico hoy?",
        "state": {
            "step": 0,
            "conversation_summary": ""
        }
    }

    print(f"\n📤 ENVIANDO PROMPT:\n'{payload['user_input']}'")
    print("\n⏳ Esperando respuesta de la IA (esto puede tardar unos segundos)...")

    try:
        start_time = time.time()
        response = requests.post(url, json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ RESPUESTA RECIBIDA en {end_time - start_time:.2f} segundos")
            print("-" * 40)
            
            # 1. Check Status
            status = data.get('status', 'unknown')
            print(f"STATUS: {status}")
            
            if status == 'blocked':
                print("❌ ERROR: El modo colaborador sigue BLOQUEADO. Revisa la conexión a la IA.")
                return

            # 2. Print Full Response for Analysis
            print("\n🤖 MENSAJE DEL ASISTENTE:\n")
            print(data.get('assistant_message', 'No message'))
            
            print("\n" + "-" * 40)
            
            # 3. Analyze Quality Criteria
            content = data.get('assistant_message', '')
            
            has_markdown = "##" in content or "**" in content
            has_options = "Opción" in content or "Propuesta" in content or "Enfoque" in content
            has_posts = "Post" in content or "Copy" in content
            
            print("\n🧐 ANÁLISIS DE CALIDAD:")
            print(f"   - [ ] Organiza ideas (Estructura Markdown): {'✅ SÍ' if has_markdown else '❌ NO'}")
            print(f"   - [ ] Propone posts concretos: {'✅ SÍ' if has_posts else '❌ NO'}")
            print(f"   - [ ] Rol de Copiloto (Opciones Estratégicas): {'✅ SÍ' if has_options else '❌ NO'}")
            
            if has_markdown and has_posts and has_options:
                print("\n🏆 VEREDICTO: IA DE PRIMERA DIVISIÓN CONFIRMADA")
            else:
                print("\n⚠️ VEREDICTO: RESPUESTA MEJORABLE (Revisar Prompt)")

        else:
            print(f"\n❌ ERROR HTTP {response.status_code}: {response.text}")

    except Exception as e:
        print(f"\n❌ ERROR DE CONEXIÓN: {e}")
        print("Asegúrate de que el backend esté corriendo en el puerto 8000.")

if __name__ == "__main__":
    test_real_ai_collaborator()
