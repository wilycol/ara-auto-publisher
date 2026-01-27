from pydantic import BaseModel
from typing import List, Optional, Any, Dict, Union
from enum import Enum

class GuideMode(str, Enum):
    GUIDED = "guided"
    COLLABORATOR = "collaborator"
    EXPERT = "expert"
    IDENTITY_CREATION = "identity_creation"

class GuideOption(BaseModel):
    label: str
    value: str

class UserProfile(BaseModel):
    profession: Optional[str] = None
    specialty: Optional[str] = None
    target_audience_profile: Optional[str] = None
    bio_summary: Optional[str] = None
    has_uploaded_cv: bool = False

class IdentityDraft(BaseModel):
    name: Optional[str] = None
    purpose: Optional[str] = None
    tone: Optional[str] = None
    platforms: Optional[List[str]] = None
    communication_style: Optional[str] = None
    content_limits: Optional[str] = None
    # MVP PRO Fields (kept for compatibility)
    identity_type: Optional[str] = None
    campaign_objective: Optional[str] = None
    target_audience: Optional[str] = None
    language: Optional[str] = None
    preferred_cta: Optional[str] = None
    frequency: Optional[str] = None

class GuideState(BaseModel):
    step: int
    user_profile: Optional[UserProfile] = None
    objective: Optional[str] = None
    audience: Optional[str] = None
    platform: Optional[str] = None
    tone: Optional[str] = None
    topics: Optional[Union[List[str], str]] = None
    postsPerDay: Optional[Union[int, str]] = None
    scheduleStrategy: Optional[str] = None
    extra_context: Optional[str] = None
    conversation_summary: Optional[str] = ""
    identity_draft: Optional[IdentityDraft] = None
    identity_id: Optional[str] = None

class GuideNextRequest(BaseModel):
    current_step: int
    mode: GuideMode = GuideMode.GUIDED
    state: GuideState
    user_input: Optional[str] = None
    user_value: Optional[str] = None
    guide_session_id: Optional[str] = None # Correlation ID for logging

class GuideNextResponse(BaseModel):
    assistant_message: str
    options: List[GuideOption] = []
    next_step: int
    state_patch: Dict[str, Any]
    status: str = "success" # success, blocked, error
