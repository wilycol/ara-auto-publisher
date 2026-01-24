import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine
from app.models.domain import Base
from app.models.automation import CampaignAutomation
from app.services.campaign_automation_service import CampaignAutomationService
from app.services.tracking_service import TrackingService

def test_automation_flow():
    print("\n🚀 [QA Automation] Starting Automation Verification...\n")
    
    # Ensure tables exist (CampaignAutomation might be new)
    print("🛠️  Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Crear Automatización
        print("👉 1. Creating Automation Rule...")
        service = CampaignAutomationService(db)
        
        rule_data = {
            "project_id": 999,
            "name": "QA Daily News",
            "trigger_type": "manual",
            "trigger_config": {"schedule": "manual"},
            "rules": {
                "platform": "twitter",
                "topic": "Tech News",
                "audience": "Developers"
            },
            "status": "active"
        }
        
        automation = service.create_automation(rule_data)
        print(f"   ✅ Automation Created: ID {automation.id} | Name: {automation.name}")
        
        # 2. Disparar Manualmente
        print("👉 2. Triggering Automation Manually...")
        result = service.trigger_campaign(automation.id, manual_override=True)
        print(f"   ✅ Trigger Result: {result['status']}")
        
        assert result["status"] == "success", "Trigger failed"
        content_id = result["content_id"]
        
        # 3. Verificar Tracking
        print("👉 3. Verifying Generated Content...")
        tracking_service = TrackingService(db)
        # Using internal repo method or similar to fetch by id, 
        # but tracking_service doesn't expose get_by_id directly in public interface?
        # Actually repo does.
        content = tracking_service.repo.get_by_id(content_id)
        
        assert content is not None, "Content not found in tracking"
        assert content.project_id == 999, "Project ID mismatch"
        assert content.platform == "twitter", "Platform mismatch"
        assert content.user_id == "system_automation", "User ID mismatch"
        
        print(f"   ✅ Content Verified: ID {content.tracking_id} | Platform: {content.platform}")
        
        # 4. Verificar Last Run
        print("👉 4. Verifying Automation State...")
        db.refresh(automation)
        assert automation.last_run_at is not None, "last_run_at should be set"
        print(f"   ✅ Last Run Updated: {automation.last_run_at}")
        
        print("\n🏁 [QA Automation] All Tests Passed Successfully!")
        
    except Exception as e:
        print(f"\n❌ [QA Automation] FAILED: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_automation_flow()
