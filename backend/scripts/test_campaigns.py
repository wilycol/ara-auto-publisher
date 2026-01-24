import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_campaign_crud():
    print("🚀 Iniciando Test CRUD de Campañas...")

    # 1. Crear/Obtener Proyecto
    print("\n1. Obteniendo Proyecto...")
    projects = requests.get(f"{BASE_URL}/projects").json().get("data", [])
    if not projects:
        print("   Creando proyecto 'Test Project'...")
        res = requests.post(f"{BASE_URL}/projects", json={"name": "Test Project"})
        if res.status_code != 200:
            print(f"❌ Error creando proyecto: {res.text}")
            sys.exit(1)
        project = res.json()["data"]
    else:
        project = projects[0]
    
    project_id = project["id"]
    print(f"   ✅ Proyecto ID: {project_id}")

    # 2. Crear Campaña
    print("\n2. Creando Campaña 'Lanzamiento Q1'...")
    campaign_data = {
        "project_id": project_id,
        "name": "Lanzamiento Q1",
        "objective": "Vender",
        "tone": "Persuasivo",
        "topics": "IA, Productividad, Futuro",
        "posts_per_day": 2,
        "schedule_strategy": "blocks"
    }
    
    res = requests.post(f"{BASE_URL}/campaigns/", json=campaign_data)
    if res.status_code != 201:
        print(f"❌ Error creando campaña: {res.status_code} - {res.text}")
        sys.exit(1)
    
    campaign = res.json()
    campaign_id = campaign["id"]
    print(f"   ✅ Campaña creada: ID {campaign_id} - {campaign['name']}")
    assert campaign["status"] == "active"

    # 3. Listar Campañas
    print("\n3. Listando Campañas del Proyecto...")
    res = requests.get(f"{BASE_URL}/campaigns/?project_id={project_id}")
    campaigns = res.json()
    print(f"   Encontradas: {len(campaigns)}")
    found = any(c["id"] == campaign_id for c in campaigns)
    if not found:
        print("❌ La campaña creada no aparece en la lista.")
        sys.exit(1)
    print("   ✅ Listado correcto.")

    # 4. Actualizar Campaña
    print("\n4. Actualizando Campaña (Pausar)...")
    update_data = {"status": "paused", "tone": "Más formal"}
    res = requests.put(f"{BASE_URL}/campaigns/{campaign_id}", json=update_data)
    if res.status_code != 200:
        print(f"❌ Error actualizando: {res.text}")
        sys.exit(1)
    
    updated = res.json()
    print(f"   Nuevo estado: {updated['status']}")
    print(f"   Nuevo tono: {updated['tone']}")
    
    if updated["status"] != "paused" or updated["tone"] != "Más formal":
        print("❌ La actualización no se reflejó correctamente.")
        sys.exit(1)
    print("   ✅ Actualización correcta.")

    # 5. Get Campaña Individual
    print("\n5. Consultando Campaña Individual...")
    res = requests.get(f"{BASE_URL}/campaigns/{campaign_id}")
    if res.status_code != 200:
        print("❌ Error get campaign")
        sys.exit(1)
    print("   ✅ Get correcto.")

    # 6. Eliminar Campaña (Opcional, dejar comentado para verla en DB si se quiere)
    # print("\n6. Eliminando Campaña...")
    # res = requests.delete(f"{BASE_URL}/campaigns/{campaign_id}")
    # if res.status_code != 204:
    #     print("❌ Error delete campaign")
    #     sys.exit(1)
    # print("   ✅ Eliminada correctamente.")

    print("\n🎉 TEST CAMPAIGNS COMPLETADO EXITOSAMENTE")

if __name__ == "__main__":
    test_campaign_crud()
