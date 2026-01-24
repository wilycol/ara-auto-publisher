import sys
import os
import uuid
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal, engine
from app.models.domain import Base, MediaUsage
from app.models.billing import BillingEvent
from app.repositories.usage_repository import UsageRepository
from app.repositories.billing_repository import BillingRepository
from app.services.usage_snapshot_service import UsageSnapshotService

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QA_SNAPSHOT")

def test_usage_snapshot():
    print("\n🚀 [QA Snapshot] Starting Usage Snapshot Verification...\n")
    
    db = SessionLocal()
    user_id = f"user_snapshot_{uuid.uuid4().hex[:8]}"
    plan = "pro"
    
    try:
        # 1. Setup Initial State (Clean slate for this user)
        # (Assuming unique user_id is enough)
        
        # 2. Simulate Usage (Technical Usage)
        print(f"👉 Simulating Usage for {user_id}...")
        usage_repo = UsageRepository(db)
        # 5 Images
        for _ in range(5):
            usage_repo.increment_usage(user_id, "image")
        
        # 1 Video (Technically 1 usage count)
        usage_repo.increment_usage(user_id, "video")
        
        # 3. Simulate Billing (Financial Impact)
        print("👉 Simulating Billing Events...")
        billing_repo = BillingRepository(db)
        
        # 5 Images * $0.04 = $0.20
        for i in range(5):
            billing_repo.create_event(BillingEvent(
                user_id=user_id,
                plan=plan,
                media_type="image",
                provider="mock",
                units=1.0,
                unit_type="image",
                cost_estimated=0.04,
                currency="USD",
                correlation_id=str(uuid.uuid4()),
                pricing_version="v1.0"
            ))
            
        # 1 Video (30 seconds) * $0.08 = $2.40
        billing_repo.create_event(BillingEvent(
            user_id=user_id,
            plan=plan,
            media_type="video",
            provider="mock",
            units=30.0,
            unit_type="second",
            cost_estimated=2.40,
            currency="USD",
            correlation_id=str(uuid.uuid4()),
            pricing_version="v1.0"
        ))
        
        # 4. Generate Snapshot
        print("👉 Generating Snapshot...")
        service = UsageSnapshotService(db)
        snapshot = service.generate_daily_snapshot(user_id, plan)
        
        print("\n📸 SNAPSHOT RESULT:")
        print(snapshot)
        
        # 5. Verify Data
        print("\n🧪 Verifying Data Integrity...")
        
        # Check Image
        img_data = snapshot["usage"].get("image")
        assert img_data["count"] == 5, f"Image count mismatch. Expected 5, got {img_data['count']}"
        assert abs(img_data["cost"] - 0.20) < 0.001, f"Image cost mismatch. Expected 0.20, got {img_data['cost']}"
        print("   ✅ Image Data OK")
        
        # Check Video
        vid_data = snapshot["usage"].get("video")
        assert vid_data["count"] == 1, f"Video count mismatch. Expected 1, got {vid_data['count']}"
        assert vid_data["seconds"] == 30.0, f"Video seconds mismatch. Expected 30.0, got {vid_data['seconds']}"
        assert abs(vid_data["cost"] - 2.40) < 0.001, f"Video cost mismatch. Expected 2.40, got {vid_data['cost']}"
        print("   ✅ Video Data OK")
        
        # Check Total
        expected_total = 2.60
        assert abs(snapshot["total_cost"] - expected_total) < 0.001, f"Total cost mismatch. Expected {expected_total}, got {snapshot['total_cost']}"
        print("   ✅ Total Cost OK")
        
        print("\n🏁 [QA Snapshot] All Tests Passed Successfully!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_usage_snapshot()
