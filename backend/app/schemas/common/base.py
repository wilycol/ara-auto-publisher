from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, List
from datetime import datetime

T = TypeVar('T')

class MediaBase(BaseModel):
    media_type: str = "image"
    public_url: Optional[str] = None

class MediaCreate(MediaBase):
    local_path: str

class MediaRead(MediaBase):
    id: int
    
    class Config:
        from_attributes = True

class StandardResponse(BaseModel, Generic[T]):
    """Contrato estándar de respuesta API"""
    success: bool = True
    message: str = "OK"
    data: Optional[T] = None
