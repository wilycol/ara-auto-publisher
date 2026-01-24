from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.common.base import MediaRead

class PostBase(BaseModel):
    title: Optional[str] = None
    content_text: str
    topic_id: Optional[int] = None
    
class PostCreate(PostBase):
    project_id: int

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content_text: Optional[str] = None
    hashtags: Optional[str] = None
    cta: Optional[str] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None

class PostRead(PostBase):
    id: int
    project_id: int
    campaign_id: Optional[int] = None
    status: str
    platform: str = "linkedin"
    hashtags: Optional[str] = None
    cta: Optional[str] = None
    ai_model: Optional[str] = None
    generation_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    created_at: datetime
    scheduled_for: Optional[datetime]
    published_at: Optional[datetime]
    media: List[MediaRead] = []

    class Config:
        from_attributes = True

class TopicBase(BaseModel):
    name: str
    keywords: str
    weight: int = 1

class TopicCreate(TopicBase):
    project_id: int

class TopicRead(TopicBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True
