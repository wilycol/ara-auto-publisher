from cryptography.fernet import Fernet
from app.core.config import get_settings
import base64

settings = get_settings()

def get_fernet():
    key = settings.ENCRYPTION_KEY
    if not key:
        raise ValueError("ENCRYPTION_KEY is missing in configuration.")
    try:
        return Fernet(key.encode())
    except Exception as e:
        raise ValueError(f"Invalid ENCRYPTION_KEY format: {str(e)}")

def encrypt_token(token: str) -> str:
    """
    Encrypts a token using Fernet symmetric encryption.
    """
    if not token:
        return None
    f = get_fernet()
    return f.encrypt(token.encode()).decode()

def decrypt_token(token_enc: str) -> str:
    """
    Decrypts a token using Fernet symmetric encryption.
    Raises exception if decryption fails (e.g. wrong key).
    """
    if not token_enc:
        return None
    f = get_fernet()
    return f.decrypt(token_enc.encode()).decode()
