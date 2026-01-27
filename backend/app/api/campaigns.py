from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.models.domain import Campaign, Project, Post, ContentStatus
from app.schemas.campaigns.campaign import CampaignCreate, CampaignRead, CampaignUpdate
from app.schemas.common.base import StandardResponse
from app.services.ai_generator import AIGeneratorService
from app.services.tracking_service import TrackingService

router = APIRouter()

ai_service = AIGeneratorService() # Instancia global por ahora

@router.post("/{campaign_id}/generate", status_code=status.HTTP_201_CREATED)
async def generate_campaign_posts(
    campaign_id: int, 
    payload: Dict[str, Any] = Body(...), 
    db: Session = Depends(get_db)
):
    """
    Genera borradores de posts para una campaña usando IA.
    Payload: {"count": 3, "platform": "linkedin"}
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    count = payload.get("count", 1)
    platform = payload.get("platform", "linkedin")

    # 1. Llamar al Generador
    try:
        generated_data = await ai_service.generate_posts(campaign, count=count, platform=platform)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")

    # 2. Guardar como Borradores (PENDING)
    created_posts = []
    for item in generated_data:
        # Convert hashtags list to string/json if needed, or store as simple string for now
        # El generador ahora devuelve hashtags como string JSON si lo normalizó, o lista si no.
        # Aseguramos que sea string para la DB.
        hashtags_val = item.get("hashtags")
        if isinstance(hashtags_val, list):
            hashtags_str = " ".join(hashtags_val)
        else:
            hashtags_str = str(hashtags_val)
        
        new_post = Post(
            project_id=campaign.project_id,
            campaign_id=campaign.id,
            title=item.get("title"),
            content_text=item.get("content"),
            hashtags=hashtags_str,
            cta=item.get("cta"),
            platform=item.get("platform", platform),
            status=ContentStatus.PENDING,
            ai_model="multi-provider-v1", # En el futuro vendrá del servicio
            tokens_used=0
        )
        db.add(new_post)
        created_posts.append(new_post)
    
    db.commit()

    # Tracking Loop
    try:
        tracker = TrackingService(db)
        for p in created_posts:
            db.refresh(p)
            tracker.record_generation({
                "user_id": "campaign-generator",
                "project_id": campaign.project_id,
                "project_name": "Campaign Run",
                "objective": campaign.objective,
                "topic": "Campaign Content",
                "platform": p.platform,
                "content_type": "text",
                "ai_agent": p.ai_model,
                "generated_url": f"/posts/{p.id}",
                "status": "generated",
                "correlation_id": f"campaign-{campaign.id}-post-{p.id}"
            })
    except Exception as e:
        print(f"Tracking failed: {e}")
    
    return {
        "status": "success",
        "generated_count": len(created_posts),
        "message": f"Generated {len(created_posts)} drafts for campaign '{campaign.name}'"
    }

@router.post("/", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """
    Create a new campaign for a project.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == campaign.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_campaign = Campaign(
        project_id=campaign.project_id,
        name=campaign.name,
        objective=campaign.objective,
        tone=campaign.tone,
        identity_id=campaign.identity_id,
        # topics, posts_per_day, schedule_strategy removed from ORM
        status=campaign.status
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@router.get("/", response_model=List[CampaignRead])
def list_campaigns(project_id: int, db: Session = Depends(get_db)):
    """
    List all campaigns for a specific project.
    """
    campaigns = db.query(Campaign).filter(Campaign.project_id == project_id).all()
    return campaigns

@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """
    Get a specific campaign by ID.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.put("/{campaign_id}", response_model=CampaignRead)
def update_campaign(campaign_id: int, campaign_update: CampaignUpdate, db: Session = Depends(get_db)):
    """
    Update a campaign.
    """
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    update_data = campaign_update.dict(exclude_unset=True)
    
    # Filter out fields that don't exist in the ORM model anymore
    valid_fields = ["name", "objective", "tone", "status", "identity_id"]
    for key, value in update_data.items():
        if key in valid_fields:
            setattr(db_campaign, key, value)

    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """
    Delete a campaign.
    """
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    db.delete(db_campaign)
    db.commit()
    return None
