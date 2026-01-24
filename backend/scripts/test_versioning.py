import sys
import os
import uuid
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal, engine
from app.models.domain import Base
from app.services.tracking_service import TrackingService
from app.services.versioning_service import VersioningService
from app.models.tracking import ContentTracking

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QA_VERSIONING")

def test_versioning_flow():
    print("\n🚀 [QA Versioning] Starting Versioning System Verification...\n")
    
    # Ensure tables exist
    print("🛠️  Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Crear V1 (Raíz)
        print("👉 1. Creating Root Content (V1)...")
        tracker = TrackingService(db)
        v1 = tracker.record_generation({
            "user_id": f"qa_ver_{uuid.uuid4().hex[:6]}",
            "project_id": 101,
            "project_name": "Versioning QA",
            "platform": "linkedin",
            "content_type": "text",
            "generated_url": "http://v1.com",
            "status": "generated",
            "correlation_id": str(uuid.uuid4()) # Important for lineage
        })
        print(f"   ✅ V1 Created: ID {v1.tracking_id} | Ver {v1.version_number} | Parent {v1.parent_content_id}")
        assert v1.version_number == 1
        assert v1.parent_content_id is None
        
        # 2. Crear V2 (Iteración)
        print("👉 2. Creating Version 2 (Edit)...")
        versioner = VersioningService(db)
        v2 = versioner.create_version(
            v1.tracking_id,
            changes={"notes": "Fixed typo", "status": "approved"},
            change_reason="Typo fix"
        )
        print(f"   ✅ V2 Created: ID {v2.tracking_id} | Ver {v2.version_number} | Parent {v2.parent_content_id}")
        assert v2.version_number == 2
        assert v2.parent_content_id == v1.tracking_id
        assert v2.correlation_id == v1.correlation_id
        assert v2.notes == "Fixed typo"
        
        # 3. Crear V3 (Iteración sobre V2)
        print("👉 3. Creating Version 3 (Refinement)...")
        v3 = versioner.create_version(
            v2.tracking_id,
            changes={"generated_url": "http://v3.com", "status": "published"},
            change_reason="Final URL update"
        )
        print(f"   ✅ V3 Created: ID {v3.tracking_id} | Ver {v3.version_number} | Parent {v3.parent_content_id}")
        assert v3.version_number == 3
        assert v3.parent_content_id == v2.tracking_id
        assert v3.correlation_id == v1.correlation_id
        
        # 4. Verificar Historial Completo
        print("👉 4. Verifying Full Lineage...")
        history = versioner.get_versions(v1.tracking_id)
        print(f"   📊 Found {len(history)} versions in history.")
        
        # Should find v1, v2, v3
        versions_found = [h.version_number for h in history]
        print(f"   Versions: {sorted(versions_found)}")
        
        assert 1 in versions_found
        assert 2 in versions_found
        assert 3 in versions_found
        assert len(history) >= 3
        
        print("   ✅ Lineage Verified!")
        
        print("\n🏁 [QA Versioning] All Tests Passed Successfully!")
        
    except Exception as e:
        print(f"\n❌ [QA Versioning] FAILED: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_versioning_flow()
