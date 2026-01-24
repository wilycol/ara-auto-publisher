import sys
import os
import time
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine
from app.core.config import get_settings
from app.models.domain import Base
from app.models.automation import CampaignAutomation, AutonomousDecisionLog
from app.services.campaign_automation_service import CampaignAutomationService
from app.services.autonomous_decision_service import AutonomousDecisionService
from app.services.autonomy_policy import DecisionType, AutonomyState

def test_autonomy_flow():
    print("\n🧠 [QA Autonomy] Starting Verification...\n")
    
    # Ensure tables exist
    print("🛠️  Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    settings = get_settings()
    
    try:
        # 1. Setup: Crear Campaña Activa
        print("👉 1. Setup: Creating Active Automation...")
        service = CampaignAutomationService(db)
        rule_data = {
            "project_id": 999,
            "name": "QA Autonomy Test",
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
        print(f"   ✅ Automation Created: ID {automation.id}")

        # 2. Test: Ejecución Permitida (Happy Path)
        print("\n👉 2. Test: Execution ALLOWED (Happy Path)...")
        decision_service = AutonomousDecisionService(db)
        result = decision_service.evaluate_execution(automation.id)
        
        assert result["decision"] == DecisionType.ALLOW_EXECUTION
        print(f"   ✅ Decision: {result['decision']} (Expected: ALLOW_EXECUTION)")
        
        # Verify Audit Log
        log = db.query(AutonomousDecisionLog).filter(AutonomousDecisionLog.automation_id == automation.id).order_by(AutonomousDecisionLog.id.desc()).first()
        assert log is not None
        assert log.decision == DecisionType.ALLOW_EXECUTION
        print("   ✅ Audit Log Verified")

        # 3. Test: Bloqueo por Cooldown
        print("\n👉 3. Test: Blocking by Cooldown...")
        # Simular que corrió hace 1 minuto (Cooldown default 60 min)
        automation.last_run_at = datetime.utcnow() - timedelta(minutes=1)
        db.commit()
        
        result = decision_service.evaluate_execution(automation.id)
        assert result["decision"] == DecisionType.BLOCK_COOLDOWN
        print(f"   ✅ Decision: {result['decision']} (Expected: BLOCK_COOLDOWN)")

        # 4. Test: Bloqueo por Estado (Autonomy Paused)
        print("\n👉 4. Test: Blocking by Status...")
        automation.autonomy_status = AutonomyState.PAUSED
        db.commit()
        
        result = decision_service.evaluate_execution(automation.id)
        assert result["decision"] == DecisionType.BLOCK_STATUS
        print(f"   ✅ Decision: {result['decision']} (Expected: BLOCK_STATUS)")

        # 5. Test: Kill Switch Global
        print("\n👉 5. Test: Global Kill Switch...")
        # Restaurar estado
        automation.autonomy_status = AutonomyState.ACTIVE
        automation.last_run_at = None # Reset cooldown
        db.commit()
        
        # Activar Kill Switch
        original_setting = settings.AUTONOMY_ENABLED
        settings.AUTONOMY_ENABLED = False
        
        result = decision_service.evaluate_execution(automation.id)
        assert result["decision"] == DecisionType.BLOCK_KILLSWITCH
        print(f"   ✅ Decision: {result['decision']} (Expected: BLOCK_KILLSWITCH)")
        
        # Restaurar Kill Switch
        settings.AUTONOMY_ENABLED = original_setting

        print("\n🏁 [QA Autonomy] All Tests Passed Successfully!")
        
    except Exception as e:
        print(f"\n❌ [QA Autonomy] FAILED: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_autonomy_flow()
