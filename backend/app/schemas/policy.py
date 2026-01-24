from pydantic import BaseModel
from typing import List, Optional, Dict, Union

class ImageCapabilities(BaseModel):
    enabled: bool
    max_per_day: Optional[int] = 0
    resolution: Optional[str] = None

class VideoCapabilities(BaseModel):
    enabled: bool
    max_per_day: Optional[int] = 0
    max_duration_seconds: Optional[int] = 0
    formats: Optional[List[str]] = []

class AgentCapabilities(BaseModel):
    text: bool
    images: ImageCapabilities
    video: VideoCapabilities

class AgentMode(BaseModel):
    max_risk_allowed: str
    tone: str
    actions: List[str]
    capabilities: AgentCapabilities
