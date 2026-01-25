from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import ForumThread
from app.schemas.forum_thread import ForumThreadCreate, ForumThreadOut
import uuid

router = APIRouter()

@router.post("/{forum_id}/threads", response_model=ForumThreadOut)
def create_thread(
    forum_id: uuid.UUID,
    payload: ForumThreadCreate,
    db: Session = Depends(get_db)
):
    thread = ForumThread(
        forum_id=forum_id,
        title=payload.title,
        content=payload.content,
        author=payload.author,
        thread_url=payload.url or "",
        status="pending"
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    
    return ForumThreadOut(
        id=thread.id,
        forum_id=thread.forum_id,
        title=thread.title,
        content=thread.content,
        author=thread.author,
        url=thread.thread_url
    )

@router.get("/{forum_id}/threads", response_model=list[ForumThreadOut])
def list_threads(forum_id: uuid.UUID, db: Session = Depends(get_db)):
    threads = db.query(ForumThread).filter(
        ForumThread.forum_id == forum_id
    ).all()
    
    return [
        ForumThreadOut(
            id=t.id,
            forum_id=t.forum_id,
            title=t.title,
            content=t.content,
            author=t.author,
            url=t.thread_url
        ) for t in threads
    ]
