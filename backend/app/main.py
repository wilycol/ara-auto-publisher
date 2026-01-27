from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.api.router import api_router
from app.core.database import engine
from app.models.domain import Base
import sys
from app.core.logging import setup_logging
from app.services.scheduler_service import SchedulerService

# Setup Global Logging
logger = setup_logging()

# Crear tablas automáticamente (Solo para DEV - En prod usar Alembic)
Base.metadata.create_all(bind=engine)

settings = get_settings()

# -----------------------------------------------------------------------------
# 🛡️ FASE 1.1: VALIDACIÓN DE SEGURIDAD (HARDENING - NO BLOCKING)
# -----------------------------------------------------------------------------
def validate_security_config():
    missing_vars = []
    
    # 1. Feature Flags Check
    logger.info("🔧 Feature Flags Configuration:")
    logger.info(f"   - LinkedIn: {'ENABLED' if settings.FEATURE_LINKEDIN_ENABLED else 'DISABLED'}")
    logger.info(f"   - Facebook: {'ENABLED' if settings.FEATURE_FACEBOOK_ENABLED else 'DISABLED'}")
    
    # 2. LinkedIn Validation (Only if Enabled)
    if settings.FEATURE_LINKEDIN_ENABLED:
        if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_CLIENT_SECRET:
            logger.warning("⚠️  LINKEDIN ENABLED BUT CREDENTIALS MISSING!")
            logger.warning("    Auto-publishing will fail, but manual mode is available.")
    
    # 3. Encryption Key (Core Security)
    if not settings.ENCRYPTION_KEY:
        logger.warning("⚠️  ENCRYPTION_KEY MISSING!")
        logger.warning("    Secure token storage is disabled. Integration tokens cannot be saved.")
        # No sys.exit() - We allow running in "Manual Mode" only.
        
    logger.info("✅ Backend initialized in HARDENED mode (Integrations Optional).")

# Execute validation
validate_security_config()
# -----------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Scheduler Service...")
    scheduler = SchedulerService()
    scheduler.start()
    yield
    # Shutdown
    logger.info("🛑 Stopping Scheduler Service...")
    scheduler.shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend Core para Orquestación de Publicaciones y Gestión de Contenido",
    lifespan=lifespan
)

# Configurar CORS para permitir peticiones desde el Frontend
allow_origins = [
    "http://localhost:5173", # Frontend Vite Dev
    "http://localhost:5174", # Frontend Vite Dev (Backup Port)
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://ara-auto-publisher-frontend.vercel.app", # Vercel Production
    "http://192.168.1.4:5173", # LAN Access
    "http://192.168.1.4:5174", # LAN Access Backup
]
if settings.ENVIRONMENT == "production":
    if settings.FRONTEND_URL:
        allow_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "system": "Ara Neuro Post Core",
        "status": "online",
        "mode": "hardened",
        "version": settings.VERSION,
        "integrations": {
            "linkedin": settings.FEATURE_LINKEDIN_ENABLED
        },
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
