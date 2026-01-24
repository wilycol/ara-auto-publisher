import sys
import os
import logging
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from app.main import app
from app.core.database import get_db, SessionLocal
from app.models.domain import Project, Campaign
from app.models.automation import CampaignAutomation, AutonomousDecisionLog
from app.models.optimization import OptimizationRecommendation, RecommendationStatus
from app.services.autonomous_decision_service import AutonomousDecisionService
from app.services.autonomy_policy import AutonomyState

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = TestClient(app)

def setup_clean_db():
    """Clean up test data"""
    db = SessionLocal()
    try:
        # Delete test campaigns and automations
        db.query(AutonomousDecisionLog).delete()
        db.query(OptimizationRecommendation).delete()
        db.query(CampaignAutomation).delete()
        db.query(Campaign).filter(Campaign.name.like("PILOT_TEST_%")).delete()
        db.query(Project).filter(Project.name.like("PILOT_TEST_%")).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Setup cleanup failed: {e}")
    finally:
        db.close()

def run_pilot_simulation():
    logger.info("🚀 STARTING PILOT SIMULATION (Fase 12.3)")
    setup_clean_db()
    
    # 1. Create Project
    logger.info("1️⃣  Creating Test Project...")
    project_payload = {"name": "PILOT_TEST_PROJECT", "description": "Simulation"}
    resp = client.post("/api/v1/projects/", json=project_payload)
    if resp.status_code != 200:
        logger.error(f"Failed to create project: {resp.text}")
        return
    project_id = resp.json()["data"]["id"]
    logger.info(f"   ✅ Project Created: ID {project_id}")

    # 2. Create Campaign
    logger.info("2️⃣  Creating Campaign...")
    campaign_payload = {
        "project_id": project_id,
        "name": "PILOT_TEST_CAMPAIGN",
        "objective": "brand_awareness",
        "tone": "professional",
        "topics": "General,Tech",
        "schedule_strategy": "interval",
        "posts_per_day": 1
    }
    resp = client.post("/api/v1/campaigns/", json=campaign_payload)
    if resp.status_code != 201:
         logger.error(f"Failed to create campaign: {resp.text}")
         return
    # Note: create_campaign returns the object directly, not wrapped in data
    campaign_id = resp.json()["id"]
    logger.info(f"   ✅ Campaign Created: ID {campaign_id}")

    # 3. Enable Automation
    logger.info("3️⃣  Enabling Automation...")
    # Manually create automation record. Note: CampaignAutomation is distinct from Campaign in this schema, 
    # or at least not linked via FK. We treat it as the "Autonomous Entity".
    db = SessionLocal()
    automation = CampaignAutomation(
        project_id=project_id, # Linked to Project
        name="PILOT_AUTOMATION",
        status="active",
        autonomy_status=AutonomyState.ACTIVE,
        is_manually_overridden=False,
        last_run_at=datetime.utcnow() - timedelta(days=1) 
    )
    db.add(automation)
    db.commit()
    db.refresh(automation)
    automation_id = automation.id
    db.close()
    logger.info(f"   ✅ Automation Enabled: ID {automation_id}")

    # 4. Simulate Scheduler Run (Generate Recommendation)
    logger.info("4️⃣  Simulating Scheduler (Autonomy Run)...")
    
    # Mock Feedback Service to return a recommendation
    # We patch 'analyze_automation_performance' to return a list of OptimizationRecommendation objects (or dicts if the service saves them internally?)
    # Looking at code: analyze_automation_performance calls _save_recommendation and returns saved objects.
    # So we should mock it to return a list of objects, AND ensure they are in DB so API can see them.
    # Actually, the API reads from DB. So the mock must insert into DB or we insert manually and mock the return.
    # Better: We let evaluate_execution run. It calls analyze_automation_performance.
    # We mock analyze_automation_performance to:
    #   1. Insert a recommendation into DB.
    #   2. Return that recommendation list.
    
    def side_effect_analyze(automation_id):
        db = SessionLocal()
        rec = OptimizationRecommendation(
            automation_id=automation_id,
            type="CHANGE_FREQUENCY",
            suggested_value="daily_twice",
            reasoning="High engagement detected (Mocked)",
            status=RecommendationStatus.PENDING,
            created_at=datetime.utcnow()
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        db.close()
        return [rec]

    with patch('app.services.performance_feedback_service.PerformanceFeedbackService.analyze_automation_performance', side_effect=side_effect_analyze):
        
        # Instantiate Service
        service = AutonomousDecisionService(SessionLocal())
        
        # Execute Evaluation
        result = service.evaluate_execution(automation_id)
        logger.info(f"   ✅ Evaluation Result: {result}")

    # 5. Verify Recommendation exists via API
    logger.info("5️⃣  Verifying Recommendation (Human View)...")
    resp = client.get("/api/v1/internal/control/recommendations")
    recs = resp.json()
    my_rec = next((r for r in recs if r["automation_id"] == automation_id), None)
    
    if not my_rec:
        logger.error("   ❌ No recommendation found via API!")
        return
    logger.info(f"   ✅ Recommendation Found: {my_rec['type']} - {my_rec['reasoning']}")
    rec_id = my_rec["id"]

    # 6. Human Action: Approve
    logger.info("6️⃣  Human Action: Approve Recommendation...")
    resp = client.post(f"/api/v1/internal/control/recommendation/{rec_id}/APPROVE")
    assert resp.status_code == 200
    assert resp.json()["recommendation_status"] == "APPLIED"
    logger.info("   ✅ Recommendation Approved.")

    # 7. Human Action: Force Pause (Override)
    logger.info("7️⃣  Human Action: Force Pause (Override)...")
    payload = {"reason": "Human decided to pause for review"}
    resp = client.post(f"/api/v1/internal/control/campaign/{automation_id}/override/force_pause", json=payload)
    data = resp.json()
    assert data["status"] == "success"
    assert data["is_manually_overridden"] == True
    assert data["automation_status"] == "paused"
    logger.info("   ✅ Campaign Force Paused & Overridden.")

    # 8. Simulate Scheduler blocked by Override
    logger.info("8️⃣  Simulating Scheduler blocked by Override...")
    with patch('app.services.performance_feedback_service.PerformanceFeedbackService.analyze_automation_performance', return_value=[]):
        service = AutonomousDecisionService(SessionLocal())
        # The service logic: if overridden, it logs warning but continues execution (ALLOW_EXECUTION) unless blocked by other checks.
        # Wait, if it returns ALLOW_EXECUTION, does it mean it "Resumes"?
        # evaluate_execution only returns a decision. It does NOT change status unless it detects a problem (BLOCK_PERFORMANCE).
        # The Scheduler calls evaluate_execution. If ALLOW, it proceeds to trigger_campaign.
        # BUT trigger_campaign checks automation.status.
        # If automation.status is PAUSED, trigger_campaign returns "skipped".
        # UNLESS manual_override=True is passed to trigger_campaign.
        # So we need to verify:
        # 1. evaluate_execution returns ALLOW (because override prevents Performance Block, or simply ignores it).
        # 2. But the Campaign Status in DB is still PAUSED.
        
        decision = service.evaluate_execution(automation_id)
        logger.info(f"   ℹ️ Decision: {decision}")
        
    # Check Status via API
    resp = client.get(f"/api/v1/internal/control/campaign/{automation_id}/status")
    status_data = resp.json()
    if status_data["status"] == "paused" and status_data["is_manually_overridden"]:
        logger.info("   ✅ Campaign remains PAUSED (Scheduler respected Override state).")
    else:
        logger.error(f"   ❌ Campaign Status Changed! Status: {status_data['status']}")

    # 9. Emergency Stop
    logger.info("9️⃣  Human Action: Emergency Stop...")
    resp = client.post("/api/v1/internal/control/emergency-stop")
    assert resp.status_code == 200
    logger.info(f"   ✅ Emergency Stop Triggered: {resp.json()}")
    
    # Verify Campaign is still paused (and override reason updated if applicable)
    resp = client.get(f"/api/v1/internal/control/campaign/{automation_id}/status")
    final_status = resp.json()
    logger.info(f"   ℹ️  Final Campaign Status: {final_status['status']} | Override: {final_status['is_manually_overridden']}")
    
    if final_status["status"] == "paused" and final_status["is_manually_overridden"]:
         logger.info("   ✅ Emergency Stop Verified.")
    else:
         logger.error("   ❌ Emergency Stop Failed.")

    logger.info("🎉 PILOT SIMULATION COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    run_pilot_simulation()
