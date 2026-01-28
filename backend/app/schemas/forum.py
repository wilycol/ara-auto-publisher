from pydantic import BaseModel
import uuid

class ForumCreate(BaseModel):
    name: str
    source_type: str
    base_url: str
    is_active: bool = True

class ForumOut(ForumCreate):
    id: uuid.UUID

    class Config:
        from_attributes = True
