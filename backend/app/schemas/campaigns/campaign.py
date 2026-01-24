from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.schemas.posts.post import PostRead

class CampaignStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class CampaignBase(BaseModel):
    name: str
    objective: Optional[str] = None
    tone: Optional[str] = None
    topics: Optional[str] = None # Comma-separated or JSON
    posts_per_day: int = 1
    schedule_strategy: Optional[str] = "interval" # interval | blocks
    status: CampaignStatusEnum = CampaignStatusEnum.ACTIVE

class CampaignCreate(CampaignBase):
    project_id: int

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    objective: Optional[str] = None
    tone: Optional[str] = None
    topics: Optional[str] = None
    posts_per_day: Optional[int] = None
    schedule_strategy: Optional[str] = None
    status: Optional[CampaignStatusEnum] = None

class CampaignRead(CampaignBase):
    id: int
    project_id: int
    created_at: datetime
    objective: Optional[str] = None
    tone: Optional[str] = None
    topics: Optional[str] = None
    schedule_strategy: Optional[str] = None
    posts: List[PostRead] = []

    class Config:
        from_attributes = True
