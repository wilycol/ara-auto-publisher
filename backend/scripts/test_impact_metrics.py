import sys
import os
import uuid
from datetime import datetime
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal, engine
from app.models.domain import Base
from app.services.tracking_service import TrackingService
from app.services.impact_service import ImpactService
from app.models.tracking import ContentTracking, ImpactMetric

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QA_IMPACT")

def test_impact_flow():
    print("\n🚀 [QA Impact] Starting Impact Metrics Verification...\n")
    
    # Ensure tables exist
    print("🛠️  Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Crear un contenido dummy para trackear
        print("👉 1. Creating dummy content tracking...")
        tracking_service = TrackingService(db)
        content = tracking_service.record_generation({
            "user_id": f"qa_user_{uuid.uuid4().hex[:6]}",
            "project_id": 999,
            "project_name": "QA Project",
            "platform": "linkedin",
            "content_type": "text",
            "generated_url": "https://example.com/post/qa",
            "status": "published",
            "correlation_id": str(uuid.uuid4())
        })
        print(f"   ✅ Content Created: ID {content.tracking_id}")
        
        # 2. Registrar Impacto (Snapshot 1 - Early)
        print("👉 2. Recording Impact Snapshot 1 (Early)...")
        impact_service = ImpactService(db)
        snap1 = impact_service.record_snapshot(content.tracking_id, {
            "impressions": 100,
            "clicks": 2,
            "reactions": 5,
            "source": "manual"
        })
        print(f"   ✅ Snapshot 1 Recorded: ID {snap1.id} (CTR: 2.0%)")
        
        # 3. Registrar Impacto (Snapshot 2 - Later)
        print("👉 3. Recording Impact Snapshot 2 (Later)...")
        snap2 = impact_service.record_snapshot(content.tracking_id, {
            "impressions": 500,
            "clicks": 25,
            "reactions": 40,
            "comments": 5,
            "shares": 2,
            "source": "manual"
        })
        print(f"   ✅ Snapshot 2 Recorded: ID {snap2.id} (Expected CTR: 5.0%)")
        
        # 4. Validar Cálculos
        print("👉 4. Validating Performance Calculations...")
        perf = impact_service.get_content_performance(content.tracking_id)
        
        metrics = perf["metrics"]
        kpis = perf["kpis"]
        
        print(f"   📊 Data Retrieved: {metrics}")
        print(f"   📈 KPIs: {kpis}")
        
        assert metrics["impressions"] == 500, "Latest impressions mismatch"
        assert metrics["clicks"] == 25, "Latest clicks mismatch"
        assert kpis["ctr_percent"] == 5.0, f"CTR mismatch. Got {kpis['ctr_percent']}, expected 5.0"
        
        expected_engagement = 40 + 5 + 2 # 47
        assert metrics["engagement"] == expected_engagement, f"Engagement mismatch. Got {metrics['engagement']}, expected {expected_engagement}"
        
        print("   ✅ Calculations Verified!")
        
        print("\n🏁 [QA Impact] All Tests Passed Successfully!")
        
    except Exception as e:
        print(f"\n❌ [QA Impact] FAILED: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_impact_flow()
