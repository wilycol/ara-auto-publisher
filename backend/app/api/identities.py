from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.domain import FunctionalIdentity, Project
from app.schemas.identity import IdentityCreate, IdentityResponse, IdentityUpdate
import json

router = APIRouter()

@router.get("/", response_model=List[IdentityResponse])
def get_identities(
    db: Session = Depends(get_db),
    project_id: int = 1 # Default MVP
):
    return db.query(FunctionalIdentity).filter(
        (FunctionalIdentity.project_id == project_id) | (FunctionalIdentity.project_id == None)
    ).order_by(FunctionalIdentity.created_at.desc()).all()

@router.post("/", response_model=IdentityResponse)
def create_identity(
    identity: IdentityCreate,
    db: Session = Depends(get_db),
    project_id: int = 1
):
    # Validate platforms is json serializable if list
    platforms_str = identity.preferred_platforms
    if isinstance(identity.preferred_platforms, list):
        platforms_str = json.dumps(identity.preferred_platforms)
    
    db_identity = FunctionalIdentity(
        project_id=project_id,
        name=identity.name,
        purpose=identity.purpose,
        tone=identity.tone,
        preferred_platforms=platforms_str,
        status=identity.status,
        role=identity.role or "custom",
        # MVP PRO Fields
        identity_type=identity.identity_type,
        campaign_objective=identity.campaign_objective,
        target_audience=identity.target_audience,
        language=identity.language,
        preferred_cta=identity.preferred_cta,
        frequency=identity.frequency
    )
    db.add(db_identity)
    db.commit()
    db.refresh(db_identity)
    return db_identity

@router.put("/{identity_id}", response_model=IdentityResponse)
def update_identity(
    identity_id: str,
    identity_update: IdentityUpdate,
    db: Session = Depends(get_db)
):
    db_identity = db.query(FunctionalIdentity).filter(FunctionalIdentity.id == identity_id).first()
    if not db_identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    
    update_data = identity_update.dict(exclude_unset=True)
    
    if "preferred_platforms" in update_data and isinstance(update_data["preferred_platforms"], list):
        update_data["preferred_platforms"] = json.dumps(update_data["preferred_platforms"])

    for key, value in update_data.items():
        setattr(db_identity, key, value)

    db.commit()
    db.refresh(db_identity)
    return db_identity
