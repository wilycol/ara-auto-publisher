import sys
import os
import time
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine
from app.models.domain import Base
from app.models.automation import CampaignAutomation, AutonomousDecisionLog
from app.models.tracking import ContentTracking, ImpactMetric
from app.models.optimization import OptimizationRecommendation, RecommendationType, RecommendationStatus
from app.services.autonomous_decision_service import AutonomousDecisionService
from app.services.autonomy_policy import DecisionType, AutonomyState
from app.services.campaign_automation_service import CampaignAutomationService

def test_feedback_loop():
    print("\n🔄 [QA Feedback Loop] Starting Verification...\n")
    
    # Ensure tables exist (OptimizationRecommendation is new)
    print("🛠️  Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Setup: Crear Campaña Activa
        print("👉 1. Setup: Creating Active Automation & Content...")
        service = CampaignAutomationService(db)
        rule_data = {
            "project_id": 888, # Dedicated ID for this test
            "name": "QA Feedback Test",
            "trigger_type": "interval",
            "trigger_config": {"minutes": 10},
            "rules": {"platform": "linkedin"},
            "status": "active"
        }
        automation = service.create_automation(rule_data)
        # Force ready to run
        automation.next_run_at = datetime.utcnow() - timedelta(minutes=1)
        automation.autonomy_status = AutonomyState.ACTIVE
        db.commit()
        
        # Create Content V1 (High Performance)
        content_v1 = ContentTracking(
            user_id="qa_user",
            project_id=888,
            topic="AI Trends",
            platform="linkedin",
            content_type="text",
            status="published",
            version_number=1,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.add(content_v1)
        db.commit()
        
        # Add Metrics for V1 (CTR 2.0%, Engagement 1.0%) -> Score = 1.4 + 0.3 = 1.7
        metric_v1 = ImpactMetric(
            tracking_id=content_v1.tracking_id,
            impressions=1000,
            clicks=20, # 2% CTR
            reactions=10, # 1% Engagement
            comments=0,
            shares=0,
            captured_at=datetime.utcnow(),
            source="manual"
        )
        db.add(metric_v1)
        db.commit()

        # Create Content V2 (Low Performance) - Child of V1
        content_v2 = ContentTracking(
            user_id="qa_user",
            project_id=888,
            topic="AI Trends",
            platform="linkedin",
            content_type="text",
            status="published",
            version_number=2,
            parent_content_id=content_v1.tracking_id, # Link Lineage
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        db.add(content_v2)
        db.commit()
        
        # Add Metrics for V2 (CTR 0.5%, Engagement 0.1%) -> Score = 0.35 + 0.03 = 0.38
        # Ratio = 0.38 / 1.7 = 0.22 (Huge Drop)
        metric_v2 = ImpactMetric(
            tracking_id=content_v2.tracking_id,
            impressions=1000,
            clicks=5, # 0.5% CTR
            reactions=1, # 0.1% Engagement
            comments=0,
            shares=0,
            captured_at=datetime.utcnow(),
            source="manual"
        )
        db.add(metric_v2)
        db.commit()

        print(f"   ✅ Data Setup Complete: Automation #{automation.id}, Content V1 #{content_v1.tracking_id}, Content V2 #{content_v2.tracking_id}")

        # 2. Test: Ejecutar DecisionService (Trigger Analysis)
        print("\n👉 2. Test: Triggering Decision Service (Should detect Regression)...")
        decision_service = AutonomousDecisionService(db)
        
        # This call should:
        # 1. Call PerformanceFeedbackService.analyze_automation_performance
        # 2. Detect the regression between V1 and V2
        # 3. Create a Recommendation (ROLLBACK)
        # 4. Decide to BLOCK_PERFORMANCE because of the rollback recommendation
        
        result = decision_service.evaluate_execution(automation.id)
        
        # 3. Verify Recommendation Created
        rec = db.query(OptimizationRecommendation).filter(
            OptimizationRecommendation.automation_id == automation.id,
            OptimizationRecommendation.type == RecommendationType.VERSION_ROLLBACK
        ).first()
        
        assert rec is not None
        print(f"   ✅ Recommendation Created: {rec.type} | {rec.reasoning}")
        assert rec.suggested_value["rollback_to_version"] == 1

        # 4. Verify Decision Blocked
        print(f"   ✅ Decision Result: {result['decision']} (Reason: {result.get('reason')})")
        assert result["decision"] == DecisionType.BLOCK_PERFORMANCE
        
        # 5. Verify Automation Auto-Paused
        db.refresh(automation)
        assert automation.autonomy_status == AutonomyState.PAUSED
        print(f"   ✅ Automation Status: {automation.autonomy_status}")

        print("\n🏁 [QA Feedback Loop] All Tests Passed Successfully!")
        
    except Exception as e:
        print(f"\n❌ [QA Feedback Loop] FAILED: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_feedback_loop()
