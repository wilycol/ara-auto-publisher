from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.models.domain import Project
from app.schemas.common.base import StandardResponse
from app.api.deps import get_current_user_id

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: str = None

class ConnectedAccountRead(BaseModel):
    id: int
    provider: str
    provider_name: str | None = None
    
    class Config:
        from_attributes = True

class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    owner_id: str | None = None
    connected_accounts: list[ConnectedAccountRead] = []
    
    class Config:
        from_attributes = True

@router.get("/", response_model=StandardResponse[list[ProjectRead]])
def list_projects(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    projects = db.query(Project).filter(Project.owner_id == current_user_id).all()
    return StandardResponse(data=projects)

@router.post("/", response_model=StandardResponse[ProjectRead])
def create_project(
    project: ProjectCreate, 
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    db_project = Project(
        name=project.name, 
        description=project.description,
        owner_id=current_user_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return StandardResponse(data=db_project)
