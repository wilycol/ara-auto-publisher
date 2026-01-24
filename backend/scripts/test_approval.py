import requests
import sys
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def test_approval_flow():
    log("🚀 Iniciando prueba de flujo de aprobación...")
    
    # Wait for server to be up?
    # Assumes server is up.
    
    # Get a post (should be seeded)
    try:
        # Check projects first to ensure server is reachable
        requests.get(f"{BASE_URL}/projects")
    except Exception:
        log("❌ Servidor no responde. Asegúrate de que esté corriendo.")
        sys.exit(1)

    posts_res = requests.get(f"{BASE_URL}/posts/")
    if posts_res.status_code != 200:
        log(f"❌ Error obteniendo posts: {posts_res.text}")
        sys.exit(1)
        
    posts = posts_res.json().get("data", [])
    if not posts:
        log("❌ No hay posts para probar. Ejecuta seed_post.py primero.")
        sys.exit(1)
        
    post = posts[0]
    post_id = post["id"]
    log(f"📝 Usando Post ID: {post_id} (Status: {post['status']})")
    
    # TEST 1: Edit Content (PENDING) -> Should Success
    log("🔹 Test 1: Editar contenido en PENDING")
    new_title = "Titulo Editado"
    res = requests.put(f"{BASE_URL}/posts/{post_id}", json={"title": new_title, "cta": "Click me"})
    if res.status_code == 200 and res.json()["data"]["title"] == new_title:
        log("✅ Edición exitosa")
    else:
        log(f"❌ Falló edición: {res.text}")
        
    # TEST 2: Approve WITHOUT date -> Should Fail
    log("🔹 Test 2: Aprobar SIN fecha -> Debe fallar")
    res = requests.put(f"{BASE_URL}/posts/{post_id}", json={"status": "approved"})
    if res.status_code == 400:
        log("✅ Falló correctamente (400 Bad Request)")
    else:
        log(f"❌ Falló validación: {res.status_code} {res.text}")
        
    # TEST 3: Approve WITH date -> Should Success
    log("🔹 Test 3: Aprobar CON fecha -> Debe funcionar")
    future_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
    res = requests.put(f"{BASE_URL}/posts/{post_id}", json={
        "status": "approved",
        "scheduled_for": future_date
    })
    if res.status_code == 200 and res.json()["data"]["status"] == "approved":
        log("✅ Aprobación exitosa")
    else:
        log(f"❌ Falló aprobación: {res.text}")
        
    # TEST 4: Edit Content (APPROVED) -> Should Fail
    log("🔹 Test 4: Editar contenido en APPROVED -> Debe fallar")
    res = requests.put(f"{BASE_URL}/posts/{post_id}", json={"content_text": "Hacked content"})
    if res.status_code == 400:
        log("✅ Bloqueo de edición exitoso")
    else:
        log(f"❌ Falló bloqueo: {res.status_code} {res.text}")
        
    # TEST 5: Revert to PENDING -> Should Success
    log("🔹 Test 5: Revertir a PENDING -> Debe funcionar")
    res = requests.put(f"{BASE_URL}/posts/{post_id}", json={"status": "pending"})
    if res.status_code == 200 and res.json()["data"]["status"] == "pending":
        log("✅ Reversión exitosa")
    else:
        log(f"❌ Falló reversión: {res.text}")

if __name__ == "__main__":
    test_approval_flow()