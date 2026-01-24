from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.guide import GuideNextRequest, GuideNextResponse
from app.services.guide_orchestrator import GuideOrchestratorService

router = APIRouter()
orchestrator = GuideOrchestratorService()

@router.post("/next", response_model=GuideNextResponse)
async def get_next_guide_step(request: GuideNextRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal para la orquestación de la guía conversacional.
    Recibe el estado actual y devuelve el siguiente paso (contenido + opciones)
    generado por IA o por lógica determinística de fallback.
    """
    return await orchestrator.process_next_step(request, db)
