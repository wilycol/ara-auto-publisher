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
# 🛡️ FASE 1.1: VALIDACIÓN ESTRICTA DE CONFIGURACIÓN DE SEGURIDAD
# -----------------------------------------------------------------------------
def validate_security_config():
    missing_vars = []
    
    # LinkedIn OAuth Critical Vars
    if not settings.LINKEDIN_CLIENT_ID:
        missing_vars.append("LINKEDIN_CLIENT_ID")
    if not settings.LINKEDIN_CLIENT_SECRET:
        missing_vars.append("LINKEDIN_CLIENT_SECRET")
    if not settings.LINKEDIN_REDIRECT_URI:
        missing_vars.append("LINKEDIN_REDIRECT_URI")
        
    # Security / Encryption
    if not settings.ENCRYPTION_KEY:
        missing_vars.append("ENCRYPTION_KEY")
        
    if missing_vars:
        logger.critical("!"*60)
        logger.critical("FATAL SECURITY ERROR: MISCONFIGURED BACKEND")
        logger.critical("The application cannot start because critical security variables are missing:")
        for var in missing_vars:
            logger.critical(f"❌  {var}")
        logger.critical("👉 Please configure these in your .env file immediately.")
        logger.critical("The system refuses to start in an insecure state.")
        logger.critical("!"*60)
        sys.exit(1)
    
    logger.info("✅ Security configuration validated successfully.")

# Execute validation before creating the app
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
# En producción, permitir lista específica de dominios
allow_origins = [
    "http://localhost:5173", # Frontend Vite Dev
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:8000",
]
if settings.ENVIRONMENT == "production":
    allow_origins = [settings.FRONTEND_URL] if settings.FRONTEND_URL else allow_origins

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
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
