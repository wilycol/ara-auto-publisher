from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class JobBase(BaseModel):
    name: str
    active: bool = False
    posts_per_day: int = Field(default=1, ge=1, le=24)
    time_window_start: str = "09:00"
    time_window_end: str = "18:00"

class JobCreate(JobBase):
    project_id: int

class JobUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None
    posts_per_day: Optional[int] = None
    time_window_start: Optional[str] = None
    time_window_end: Optional[str] = None

class JobRead(JobBase):
    id: int
    project_id: int
    last_run: Optional[datetime] = None

    class Config:
        from_attributes = True
