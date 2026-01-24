import sys
import os
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine
from app.models.domain import Base
from app.services.tracking_service import TrackingService
from app.services.versioning_service import VersioningService
from app.services.impact_service import ImpactService

def test_policy_flow():
    print("\n🚀 [QA Versioning Policy] Starting Verification...\n")
    
    db = SessionLocal()
    
    try:
        # 1. Crear V1
        print("👉 1. Creating Content V1...")
        tracking_service = TrackingService(db)
        v1 = tracking_service.record_generation({
            "user_id": "qa_policy",
            "project_id": 803,
            "project_name": "Policy QA",
            "platform": "linkedin",
            "content_type": "text",
            "generated_url": "http://v1.com",
            "status": "generated",
            "correlation_id": str(uuid.uuid4())
        })
        print(f"   ✅ V1 Created: ID {v1.tracking_id} | Status: {v1.status}")
        
        # 2. Crear V2 (Esto debería archivar V1)
        print("👉 2. Creating Content V2 (Should archive V1)...")
        versioning_service = VersioningService(db)
        v2 = versioning_service.create_version(
            v1.tracking_id, 
            {"generated_url": "http://v2.com"}, 
            "Better tone"
        )
        print(f"   ✅ V2 Created: ID {v2.tracking_id} | Status: {v2.status}")
        
        # Verificar estado de V1
        db.refresh(v1)
        print(f"   🔍 V1 New Status: {v1.status}")
        assert v1.status == "archived", f"V1 should be archived, but is {v1.status}"
        print("   ✅ Policy Checked: V1 is archived.")

        # 3. Intentar Publicar V1 (Debe fallar)
        print("👉 3. Attempting to Publish V1 (Should Fail)...")
        try:
            tracking_service.publish_content(v1.tracking_id)
            assert False, "Should have raised ValueError for publishing obsolete version"
        except ValueError as e:
            print(f"   ✅ Blocked as expected: {str(e)}")
            
        # 4. Publicar V2 (Debe funcionar)
        print("👉 4. Publishing V2 (Should Succeed)...")
        published_v2 = tracking_service.publish_content(v2.tracking_id)
        assert published_v2.status == "published", "V2 status should be published"
        assert published_v2.published_at is not None, "V2 published_at should be set"
        print(f"   ✅ V2 Published at: {published_v2.published_at}")
        
        # 5. Impact Metrics en V2
        print("👉 5. Recording Metrics for V2...")
        impact_service = ImpactService(db)
        metric = impact_service.record_snapshot(v2.tracking_id, {
            "impressions": 1000,
            "clicks": 50,
            "source": "manual"
        })
        print(f"   ✅ Metrics recorded for V2 (ID {v2.tracking_id})")
        
        # Verificar que la métrica apunta a V2
        assert metric.tracking_id == v2.tracking_id, "Metric should be linked to V2"
        
        perf = impact_service.get_content_performance(v2.tracking_id)
        assert perf["metrics"]["impressions"] == 1000, "Metrics retrieval failed for V2"
        print("   ✅ Metrics linked correctly to specific version.")

        print("\n🏁 [QA Versioning Policy] All Tests Passed Successfully!")
        
    except Exception as e:
        print(f"\n❌ [QA Versioning Policy] FAILED: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_policy_flow()
