from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.auto_publisher import AutoPublisherService
from app.schemas.common.base import StandardResponse
from app.schemas.posts.post import PostRead
from app.schemas.jobs.job import JobCreate, JobRead
from app.models.domain import AutoPublisherJob, Project
from app.core.config import get_settings
from app.services.ai_client import MockAIClient, OpenAICompatibleClient

router = APIRouter()

def get_publisher_service():
    settings = get_settings()
    
    if settings.AI_PROVIDER == "mock":
        client = MockAIClient()
    else:
        client = OpenAICompatibleClient(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
            model=settings.AI_MODEL
        )
        
    return AutoPublisherService(ai_client=client)

@router.post("/", response_model=StandardResponse[JobRead])
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    # Validar project
    project = db.query(Project).filter(Project.id == job.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_job = AutoPublisherJob(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return StandardResponse(data=db_job)

@router.post("/run/{job_id}", response_model=StandardResponse[PostRead])
def run_job_manually(job_id: int, db: Session = Depends(get_db)):
    """
    Ejecuta manualmente un ciclo del Auto Publisher.
    Útil para testing y demostraciones.
    """
    publisher_service = get_publisher_service()
    try:
        new_post = publisher_service.run(db, job_id)
        return StandardResponse(
            message="Post generated successfully",
            data=new_post
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
