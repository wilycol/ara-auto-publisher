from fastapi import APIRouter
from app.services.ai_provider_service import ai_provider_service

router = APIRouter()

@router.get("/ai")
async def check_ai_health():
    """
    Verifica el estado de conexión con el proveedor de IA.
    Retorna si está conectado, qué proveedor se está usando y si es IA real.
    """
    return await ai_provider_service.check_health()
