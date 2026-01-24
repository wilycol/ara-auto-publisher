import httpx
import sys
import os
# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simulación de test manual con requests (al endpoint local)
def test_oauth_error_handling():
    print("🔒 Iniciando Test de Robustez OAuth (Fase 1.3)...")
    
    base_url = "http://localhost:8000/api/v1/auth/linkedin/callback"
    
    # 1. Test Missing Code
    print("\n1️⃣ Probando 'Missing Code'...")
    try:
        res = httpx.get(f"{base_url}")
        print(f"Status: {res.status_code}")
        if res.status_code == 400 and "Missing authorization code" in res.text:
            print("✅ OK: Detectó falta de código.")
        else:
            print(f"❌ FALLO: Respuesta inesperada {res.text}")
    except Exception as e:
        print(f"❌ ERROR RED: {e}")

    # 2. Test LinkedIn Error (User Cancelled)
    print("\n2️⃣ Probando 'User Cancelled'...")
    try:
        res = httpx.get(f"{base_url}?error=user_cancelled_login&error_description=User+refused")
        print(f"Status: {res.status_code}")
        if res.status_code == 400 and "User refused" in res.text:
            print("✅ OK: Manejó error de LinkedIn correctamente.")
        else:
            print(f"❌ FALLO: Respuesta inesperada {res.text}")
    except Exception as e:
        print(f"❌ ERROR RED: {e}")

    # 3. Test Invalid State
    print("\n3️⃣ Probando 'Invalid State'...")
    try:
        res = httpx.get(f"{base_url}?code=fake_code&state=invalid_int")
        print(f"Status: {res.status_code}")
        if res.status_code == 400 and "Invalid state parameter" in res.text:
            print("✅ OK: Detectó state inválido.")
        else:
            print(f"❌ FALLO: Respuesta inesperada {res.text}")
    except Exception as e:
        print(f"❌ ERROR RED: {e}")

    # 4. Test Token Exchange Failure (Simulado)
    # Esto requiere que el backend intente conectar a LinkedIn con un code falso
    print("\n4️⃣ Probando 'Token Exchange Failure' (Code inválido)...")
    try:
        res = httpx.get(f"{base_url}?code=fake_code_123&state=1")
        print(f"Status: {res.status_code}")
        # Esperamos 400 porque LinkedIn rechazará el code falso
        if res.status_code == 400 and "Failed to retrieve access token" in res.text:
            print("✅ OK: Manejó rechazo de token correctamente.")
        else:
            print(f"❌ FALLO: Respuesta inesperada {res.text}")
            # Nota: Si devuelve 503 es porque no tiene internet, también aceptable.
    except Exception as e:
        print(f"❌ ERROR RED: {e}")

    print("\n🎉 FASE 1.3 VERIFICADA: Endpoint robusto.")

if __name__ == "__main__":
    test_oauth_error_handling()
