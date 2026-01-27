import asyncio
import sys
import os
import uuid
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.services.guide_orchestrator import GuideOrchestratorService
from app.schemas.guide import GuideNextRequest, GuideMode, GuideState, UserProfile
from app.models.domain import Campaign, Post, ContentStatus, FunctionalIdentity

async def test_collaborator_flow():
    print("🚀 Testing Collaborator Flow (Chat -> Campaign/Post Creation)...")
    
    db = SessionLocal()
    service = GuideOrchestratorService()
    session_id = str(uuid.uuid4())
    
    # Setup: Ensure a Functional Identity exists
    identity = db.query(FunctionalIdentity).filter_by(name="Collaborator Test Bot").first()
    if not identity:
        identity = FunctionalIdentity(
            project_id=1,
            name="Collaborator Test Bot",
            role="expert",
            purpose="Testing collaborator mode",
            status="active"
        )
        db.add(identity)
        db.commit()
        print(f"✅ Created test identity: {identity.id}")
    else:
        print(f"ℹ️ Using existing identity: {identity.id}")

    # Step 1: Initialize Chat (Collaborator Mode)
    state = GuideState(
        step=1,
        user_profile=UserProfile(profession="Software Engineer", specialty="AI Agents"),
        identity_id=str(identity.id) # Pre-select identity
    )
    
    print("\n--- STEP 1: Init ---")
    req = GuideNextRequest(
        current_step=1, 
        mode=GuideMode.COLLABORATOR, 
        state=state, 
        user_input="Quiero crear una campaña para vender mis servicios de consultoría AI",
        guide_session_id=session_id
    )
    res = await service.process_next_step(req, db)
    print(f"🤖 AI: {res.assistant_message}")
    
    # Simulate AI inferred objective
    state.objective = "Vender servicios de consultoría AI"
    state.audience = "CTOs y Tech Leads"
    state.platform = "linkedin"
    
    # Step 2: Confirm Creation
    print("\n--- STEP 2: Confirm Creation ---")
    req = GuideNextRequest(
        current_step=1, 
        mode=GuideMode.COLLABORATOR, 
        state=state, 
        user_value="confirm_create", # Simulate clicking "Sí, crear"
        guide_session_id=session_id
    )
    
    # Mocking AI Generator Service internally or just relying on it working if keys are present
    # If keys are missing, it might fail or return fallback if not mocked.
    # But GuideOrchestrator uses AIGeneratorService which uses ai_provider_service.
    # We hope it works or fails gracefully.
    
    try:
        res = await service.process_next_step(req, db)
        print(f"🤖 AI: {res.assistant_message}")
        
        # Verify DB
        campaign = db.query(Campaign).order_by(Campaign.id.desc()).first()
        print(f"\n✅ Last Campaign: {campaign.name} (ID: {campaign.id})")
        print(f"   Objective: {campaign.objective}")
        print(f"   Identity: {campaign.identity_id}")
        
        posts = db.query(Post).filter(Post.campaign_id == campaign.id).all()
        print(f"✅ Generated Posts: {len(posts)}")
        for p in posts:
            print(f"   - Post {p.id}: {p.title} (Status: {p.status})")
            
        if len(posts) > 0:
            print("\n🎉 SUCCESS: Flow completed end-to-end.")
        else:
            print("\n⚠️ WARNING: Campaign created but no posts generated (Check AI logs).")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n❌ ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_collaborator_flow())
