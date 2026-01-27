import sys
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.domain import Base, Campaign, FunctionalIdentity, Project
from app.services.ai_generator import AIGeneratorService

# Setup In-Memory DB for speed
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_prompt_generation():
    print("🚀 Testing AI Prompt Generation with Identity...")
    
    # Create Tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        # 1. Setup Data
        project = Project(name="Test Project", id=1)
        db.add(project)
        
        identity = FunctionalIdentity(
            project_id=1,
            name="Elon Musk Bot",
            role="Visionary Tech Leader",
            purpose="Inspire innovation",
            tone="Bold, direct, and slightly chaotic",
            status="active"
        )
        db.add(identity)
        db.commit()
        db.refresh(identity)
        
        campaign = Campaign(
            project_id=1,
            name="Mars Colony Campaign",
            objective="Promote Mars colonization",
            tone="Inspirational", # Generic tone
            identity_id=identity.id,
            status="active"
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        # 2. Test Prompt Construction
        service = AIGeneratorService()
        
        # We need to ensure relationship is loaded
        # Since we are in same session, it should be fine, but let's access it to be sure
        print(f"Campaign Identity: {campaign.identity.name}")
        
        prompt = service._build_prompt(campaign, "twitter")
        
        print("\n--- Generated Prompt ---")
        print(prompt)
        print("------------------------\n")
        
        # 3. Assertions
        assert "Elon Musk Bot" in prompt, "❌ Identity Name missing from prompt"
        assert "Visionary Tech Leader" in prompt, "❌ Identity Role missing from prompt"
        assert "Inspire innovation" in prompt, "❌ Identity Purpose missing from prompt"
        assert "Bold, direct, and slightly chaotic" in prompt, "❌ Identity Tone missing from prompt"
        assert "Tono (Override campaña): Inspirational" in prompt, "❌ Campaign Tone missing (as override context)"
        
        print("✅ SUCCESS: Prompt contains all identity elements!")
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    test_prompt_generation()
