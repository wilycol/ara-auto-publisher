from pydantic import BaseModel, UUID4
from typing import Optional, List, Union
from datetime import datetime

class IdentityBase(BaseModel):
    name: str
    purpose: Optional[str] = None
    tone: Optional[str] = None
    preferred_platforms: Optional[Union[List[str], str]] = None # List or JSON string
    communication_style: Optional[str] = None
    content_limits: Optional[str] = None
    status: Optional[str] = "active"
    role: Optional[str] = None # Legacy/Optional
    
    # MVP PRO Fields
    identity_type: Optional[str] = None
    campaign_objective: Optional[str] = None
    target_audience: Optional[str] = None
    language: Optional[str] = "es"
    preferred_cta: Optional[str] = None
    frequency: Optional[str] = "medium"

class IdentityCreate(IdentityBase):
    pass

class IdentityUpdate(IdentityBase):
    name: Optional[str] = None

class IdentityResponse(IdentityBase):
    id: UUID4
    project_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
