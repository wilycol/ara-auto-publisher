import sys
import os
import uuid
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal, engine
from app.models.domain import Base
from app.services.tracking_service import TrackingService
from app.models.tracking import ContentTracking

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QA_TRACKING")

def test_tracking_system():
    print("\n🚀 [QA Tracking] Starting Tracking System Verification...\n")
    
    # Ensure tables exist
    print("🛠️  Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    service = TrackingService(db)
    
    try:
        # 1. Simulate Content Generation
        print("👉 1. Recording Generated Content...")
        
        entry_data = {
            "user_id": f"user_track_{uuid.uuid4().hex[:6]}",
            "project_id": 1,
            "project_name": "QA Project",
            "objective": "Brand Awareness",
            "topic": "AI News",
            "platform": "linkedin",
            "content_type": "text",
            "ai_agent": "editorial_v1",
            "generated_url": "https://ara.local/posts/123",
            "correlation_id": str(uuid.uuid4())
        }
        
        entry = service.record_generation(entry_data)
        print(f"   ✅ Recorded Entry ID: {entry.tracking_id}")
        
        # 2. Query Data
        print("\n👉 2. Querying Reports...")
        results = service.get_report_data(project_id=1)
        assert len(results) > 0
        print(f"   ✅ Found {len(results)} entries for Project 1")
        
        # 3. Test Export (JSON)
        print("\n👉 3. Testing Export (JSON)...")
        buffer, filename = service.export_data("json", project_id=1)
        content = buffer.read().decode('utf-8')
        assert "QA Project" in content
        print(f"   ✅ JSON Export OK ({len(content)} bytes)")
        
        # 4. Test Export (CSV)
        print("\n👉 4. Testing Export (CSV)...")
        buffer, filename = service.export_data("csv", project_id=1)
        content = buffer.read().decode('utf-8-sig')
        assert "ID,Date,Project" in content
        print(f"   ✅ CSV Export OK ({len(content)} bytes)")
        
        # 5. Test Export (XLSX)
        print("\n👉 5. Testing Export (XLSX)...")
        try:
            buffer, filename = service.export_data("xlsx", project_id=1)
            print(f"   ✅ XLSX Export OK ({buffer.getbuffer().nbytes} bytes)")
        except ImportError:
             print("   ⚠️ XLSX Skipped (openpyxl not installed in test env)")
        
        print("\n🏁 [QA Tracking] All Tests Passed Successfully!")

    except Exception as e:
        print(f"\n❌ TRACKING FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_tracking_system()
