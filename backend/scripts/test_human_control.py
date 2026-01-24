import sys
import os
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine
from app.models.domain import Base
from app.models.automation import CampaignAutomation, AutonomousDecisionLog
from app.models.optimization import OptimizationRecommendation, RecommendationStatus, RecommendationType
from app.services.autonomous_decision_service import AutonomousDecisionService
from app.services.autonomy_policy import AutonomyState, DecisionType
from app.api.internal_control import control_recommendation, manual_override, get_dashboard_stats

def test_human_control():
    print("\n👮 [QA Human Control] Starting Verification...\n")
    
    # Ensure tables
    print("🛠️  Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Setup Campaign
        print("👉 1. Setup: Creating Paused Automation...")
        automation = CampaignAutomation(
            project_id=999,
            name="QA Human Control Campaign",
            status="paused",
            autonomy_status="autonomous_paused",
            last_run_at=datetime.utcnow() - timedelta(days=1), # Ensure cooldown passes
            is_manually_overridden=False
        )
        db.add(automation)
        db.commit()
        db.refresh(automation)
        aid = automation.id
        print(f"   ✅ Created Campaign #{aid} (Paused)")

        # 2. Test Manual Override: Force Resume
        print("\n👉 2. Test: Force Resume (Override)...")
        res = manual_override(aid, "force_resume", reason="QA Force Start", db=db)
        print(f"   ✅ Override Result: Status={res['automation_status']}, Autonomy={res['autonomy_status']}, Overridden={res['is_manually_overridden']}")
        
        assert res["automation_status"] == "active"
        assert res["autonomy_status"] == AutonomyState.ACTIVE
        assert res["is_manually_overridden"] is True
        
        # Verify Log
        log = db.query(AutonomousDecisionLog).filter(
            AutonomousDecisionLog.automation_id == aid,
            AutonomousDecisionLog.decision == "MANUAL_OVERRIDE_FORCE_RESUME"
        ).first()
        assert log is not None
        print(f"   ✅ Audit Log Found: {log.decision} | {log.reason}")

        # 3. Test Safety Rule: "Una campaña en override manual no puede ser pausada por autonomía"
        print("\n👉 3. Test: Safety Rule (Override Protection)...")
        # We simulate a decision check that SHOULD fail (e.g., performance regression)
        
        rec = OptimizationRecommendation(
            automation_id=aid,
            type=RecommendationType.VERSION_ROLLBACK,
            reasoning="Critical failure simulated",
            status=RecommendationStatus.PENDING
        )
        db.add(rec)
        db.commit()
        
        # Mock feedback service to return this recommendation
        service = AutonomousDecisionService(db)
        original_method = service.feedback_service.analyze_automation_performance
        service.feedback_service.analyze_automation_performance = lambda x: [rec]
        
        decision = service.evaluate_execution(aid)
        print(f"   ✅ Decision Result: {decision['decision']} | {decision['reason']}")
        
        # It should NOT be BLOCK_PERFORMANCE or PAUSE_CAMPAIGN.
        # It should be ALLOW_EXECUTION because of override.
        
        assert decision['decision'] == DecisionType.ALLOW_EXECUTION
        assert "Manual Override Active" in decision['reason']
        print("   ✅ Safety Rule Verified: Campaign was NOT paused despite rollback recommendation.")
        
        # Restore method
        service.feedback_service.analyze_automation_performance = original_method

        # 4. Test Recommendation Control
        print("\n👉 4. Test: Recommendation Control (Approve)...")
        # Use the rec created above
        ctrl_res = control_recommendation(rec.id, "APPROVE", db=db)
        print(f"   ✅ Control Result: Status={ctrl_res['recommendation_status']}")
        
        db.refresh(rec)
        assert rec.status == RecommendationStatus.APPLIED
        assert rec.handled_by == "human_operator"
        assert rec.handled_at is not None
        print("   ✅ Recommendation Approved & Audited.")

        # 5. Dashboard Stats
        print("\n👉 5. Test: Dashboard Stats...")
        stats = get_dashboard_stats(db=db)
        print(f"   ✅ Stats: Overridden={stats['autonomy_states']['manually_overridden']}")
        assert stats['autonomy_states']['manually_overridden'] >= 1
        
        print("\n🏁 [QA Human Control] All Tests Passed Successfully!")

    except Exception as e:
        print(f"\n❌ [QA Human Control] FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    test_human_control()
