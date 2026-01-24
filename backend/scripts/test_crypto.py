import sys
import os
# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import encrypt_token, decrypt_token, get_fernet
from app.core.config import get_settings

def test_crypto():
    print("🔒 Iniciando Test de Cifrado (Fase 1.2)...")
    
    settings = get_settings()
    original_token = "test_token_secret_123"
    
    # 1. Test Encryption
    encrypted = encrypt_token(original_token)
    print(f"✅ Token original: {original_token}")
    print(f"✅ Token cifrado:  {encrypted}")
    
    if encrypted == original_token:
        print("❌ ERROR: El token no se cifró (texto plano).")
        sys.exit(1)
        
    if "test_token" in encrypted:
        print("❌ ERROR: El cifrado es débil (contiene parte del original).")
        sys.exit(1)

    # 2. Test Decryption
    decrypted = decrypt_token(encrypted)
    print(f"✅ Token descifrado: {decrypted}")
    
    if decrypted != original_token:
        print("❌ ERROR: El token descifrado no coincide con el original.")
        sys.exit(1)
        
    # 3. Test Invalid Key (Simulación)
    print("\n🧪 Probando fallo con clave incorrecta...")
    real_key = settings.ENCRYPTION_KEY
    
    # Temporarily corrupt the key in memory (conceptually, though Fernet instance is cached)
    # Instead, we'll try to decrypt with a different Fernet instance
    from cryptography.fernet import Fernet
    wrong_key = Fernet.generate_key()
    wrong_fernet = Fernet(wrong_key)
    
    try:
        wrong_fernet.decrypt(encrypted.encode())
        print("❌ ERROR: Se pudo descifrar con una clave incorrecta!")
        sys.exit(1)
    except Exception as e:
        print(f"✅ Éxito: Falló como se esperaba ({str(e)})")

    print("\n🎉 FASE 1.2 VERIFICADA: Cifrado robusto y funcional.")

if __name__ == "__main__":
    test_crypto()
