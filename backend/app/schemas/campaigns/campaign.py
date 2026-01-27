from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum
from uuid import UUID
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
    status: CampaignStatusEnum = CampaignStatusEnum.ACTIVE

class CampaignCreate(CampaignBase):
    project_id: int
    identity_id: Optional[Union[UUID, str, int]] = None # UUID usually passed as str
    # Optional fields that might still be sent by frontend but are ignored by backend logic
    topics: Optional[str] = None 
    posts_per_day: Optional[Union[int, str]] = 1
    schedule_strategy: Optional[str] = "interval"

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    objective: Optional[str] = None
    tone: Optional[str] = None
    status: Optional[CampaignStatusEnum] = None
    identity_id: Optional[Union[UUID, str, int]] = None
    # topics, posts_per_day, schedule_strategy removed

class CampaignRead(CampaignBase):
    id: int
    project_id: int
    identity_id: Optional[Union[UUID, str, int]] = None
    created_at: datetime
    posts: List[PostRead] = []

    class Config:
        from_attributes = True
