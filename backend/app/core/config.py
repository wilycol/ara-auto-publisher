from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ara Neuro Post Core"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    # Default to SQLite for local dev, but ready for Postgres (Supabase) via env var
    DATABASE_URL: str = "sqlite:///./ara_neuro_post.db" 
    
    # Supabase (Auth & Storage)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = "" # Anon key
    SUPABASE_JWT_SECRET: str = "" # Required for validating JWTs
    
    # AI Engine Service URL
    AI_ENGINE_URL: str = "http://localhost:8001"
    
    # AI Configuration (Multi-Provider)
    AI_PROVIDER_PRIORITY: str = "openai,openrouter,gemini,grok" # Orden de prioridad
    AI_HEALTH_STRICT: bool = True
    
    # Provider Keys (Fallback Chain)
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROK_API_KEY: str = ""

    # Legacy (Mantener por compatibilidad temporal si es necesario)
    AI_PROVIDER: str = "auto" 
    AI_API_KEY: str = "" # Deprecated in favor of specific keys
    AI_BASE_URL: str = ""
    AI_MODEL: str = ""

    # Feature Flags (Defaults to FALSE for safety)
    FEATURE_LINKEDIN_ENABLED: bool = False
    FEATURE_FACEBOOK_ENABLED: bool = False
    FEATURE_INSTAGRAM_ENABLED: bool = False
    FEATURE_TIKTOK_ENABLED: bool = False

    # LinkedIn & Security
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_REDIRECT_URI: str = "" # Must be set in .env
    ENCRYPTION_KEY: str = "" # Fernet key (32 url-safe base64-encoded bytes)

    # Autonomy (Fase 10)
    AUTONOMY_ENABLED: bool = True  # Master Kill Switch

    # Deployment
    ENVIRONMENT: str = "development" # development, production
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
