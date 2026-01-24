from pydantic import BaseModel
from typing import List, Optional, Any, Dict, Union
from enum import Enum

class GuideMode(str, Enum):
    GUIDED = "guided"
    COLLABORATOR = "collaborator"
    EXPERT = "expert"

class GuideOption(BaseModel):
    label: str
    value: str

class UserProfile(BaseModel):
    profession: Optional[str] = None
    specialty: Optional[str] = None
    target_audience_profile: Optional[str] = None
    bio_summary: Optional[str] = None
    has_uploaded_cv: bool = False

class GuideState(BaseModel):
    step: int
    user_profile: Optional[UserProfile] = None
    objective: Optional[str] = None
    audience: Optional[str] = None
    platform: Optional[str] = None
    tone: Optional[str] = None
    topics: Optional[List[str]] = None
    postsPerDay: Optional[int] = None
    scheduleStrategy: Optional[str] = None
    extra_context: Optional[str] = None
    conversation_summary: Optional[str] = ""

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
