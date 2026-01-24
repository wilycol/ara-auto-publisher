from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.domain import Topic, Project
from app.schemas.posts.post import TopicCreate, TopicRead
from app.schemas.common.base import StandardResponse

router = APIRouter()

@router.post("/", response_model=StandardResponse[TopicRead])
def create_topic(topic: TopicCreate, db: Session = Depends(get_db)):
    # Validar project
    project = db.query(Project).filter(Project.id == topic.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db_topic = Topic(**topic.model_dump())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    
    return StandardResponse(data=db_topic)

@router.get("/", response_model=StandardResponse[List[TopicRead]])
def list_topics(project_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Topic)
    if project_id:
        query = query.filter(Topic.project_id == project_id)
        
    topics = query.all()
    return StandardResponse(data=topics)
