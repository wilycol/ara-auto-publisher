from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Forum
from app.schemas.forum import ForumCreate, ForumOut

router = APIRouter()

@router.post("/", response_model=ForumOut)
def create_forum(payload: ForumCreate, db: Session = Depends(get_db)):
    forum = Forum(
        name=payload.name,
        platform=payload.source_type,
        base_url=payload.base_url,
        is_active=payload.is_active
    )
    db.add(forum)
    db.commit()
    db.refresh(forum)
    
    return ForumOut(
        id=forum.id,
        name=forum.name,
        source_type=forum.platform,
        base_url=forum.base_url,
        is_active=forum.is_active
    )

@router.get("/", response_model=list[ForumOut])
def list_forums(db: Session = Depends(get_db)):
    forums = db.query(Forum).filter(Forum.is_active == True).all()
    return [
        ForumOut(
            id=f.id,
            name=f.name,
            source_type=f.platform,
            base_url=f.base_url,
            is_active=f.is_active
        ) for f in forums
    ]
