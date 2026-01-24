import requests
import sys
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_generator():
    print("🚀 Iniciando Test Generador IA (F2.1)...")

    # 1. Obtener una campaña existente (o crearla)
    print("\n1. Buscando campaña activa...")
    # Asumimos que existe el proyecto 1 del test anterior
    project_id = 1
    
    res = requests.get(f"{BASE_URL}/campaigns/?project_id={project_id}")
    campaigns = res.json()
    
    if not campaigns:
        print("❌ No hay campañas. Ejecuta primero scripts/test_campaigns.py")
        sys.exit(1)
        
    campaign = campaigns[0]
    campaign_id = campaign["id"]
    print(f"   ✅ Usando Campaña ID: {campaign_id} ({campaign['name']})")

    # 2. Invocar Endpoint de Generación
    print(f"\n2. Solicitando generación de 2 borradores para LinkedIn...")
    payload = {
        "count": 2,
        "platform": "linkedin"
    }
    
    url = f"{BASE_URL}/campaigns/{campaign_id}/generate"
    try:
        res = requests.post(url, json=payload)
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el backend?")
        sys.exit(1)

    if res.status_code != 201:
        print(f"❌ Error en generación: {res.status_code} - {res.text}")
        sys.exit(1)
        
    data = res.json()
    print(f"   ✅ Respuesta recibida: {json.dumps(data, indent=2)}")
    
    if data["generated_count"] != 2:
        print("❌ El conteo de posts generados no coincide.")
        sys.exit(1)

    # 3. Verificar que los posts existen en la BD (via endpoint de posts)
    # Nota: Aún no tenemos endpoint GET /posts filtrado por campaña, pero podemos listar todos o verificar la respuesta anterior.
    # Por ahora confiamos en la respuesta del generador que confirma creación.
    
    print("\n🎉 TEST GENERATOR COMPLETADO EXITOSAMENTE")
    print("   Los borradores han sido creados en estado PENDING.")

if __name__ == "__main__":
    test_generator()
