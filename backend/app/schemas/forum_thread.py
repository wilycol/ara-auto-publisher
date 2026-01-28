from pydantic import BaseModel
import uuid

class ForumThreadCreate(BaseModel):
    title: str
    content: str
    author: str | None = None
    url: str | None = None

class ForumThreadOut(ForumThreadCreate):
    id: uuid.UUID
    forum_id: uuid.UUID

    class Config:
        from_attributes = True
