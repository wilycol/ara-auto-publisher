import sys
import os
import time
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine
from app.models.domain import Base
from app.models.automation import CampaignAutomation
from app.services.campaign_automation_service import CampaignAutomationService
from app.services.scheduler_service import SchedulerService

def test_scheduler_flow():
    print("\n🚀 [QA Scheduler] Starting Verification...\n")
    
    # Ensure tables exist
    print("🛠️  Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Crear Automatización con ejecución inmediata (vencida)
        print("👉 1. Creating 'Due Now' Automation Rule...")
        service = CampaignAutomationService(db)
        
        # next_run_at en el pasado para que el scheduler lo tome ya
        past_time = datetime.utcnow() - timedelta(minutes=5)
        
        rule_data = {
            "project_id": 999,
            "name": "QA Scheduled News",
            "trigger_type": "interval",
            "trigger_config": {"minutes": 60}, # cada hora
            "rules": {"platform": "linkedin"},
            "status": "active"
        }
        
        automation = service.create_automation(rule_data)
        # Forzar next_run_at al pasado manualmente porque el create lo pone en futuro
        automation.next_run_at = past_time
        db.commit()
        
        print(f"   ✅ Automation Created: ID {automation.id}")
        print(f"   ⏰ Next Run Force Set To: {automation.next_run_at} (Should be picked up)")
        
        # 2. Iniciar Scheduler (manualmente la función scan para no esperar el intervalo)
        # En prod corre solo, pero aquí simulamos el "tick" del scheduler
        print("👉 2. Simulating Scheduler Tick...")
        scheduler = SchedulerService()
        # No llamamos start() para no abrir threads background, llamamos directo a _scan_due_jobs
        scheduler._scan_due_jobs()
        
        # 3. Verificar Ejecución
        print("👉 3. Verifying Execution...")
        db.refresh(automation)
        
        # last_run_at debe ser reciente (ahora)
        assert automation.last_run_at is not None, "last_run_at should be updated"
        time_since_run = (datetime.utcnow() - automation.last_run_at).total_seconds()
        assert time_since_run < 10, "Execution should have happened just now"
        
        # next_run_at debe ser futuro (+60 min)
        assert automation.next_run_at > datetime.utcnow(), "next_run_at should be in future"
        
        print(f"   ✅ Last Run: {automation.last_run_at}")
        print(f"   ✅ Next Run: {automation.next_run_at}")
        
        # 4. Verificar Idempotencia (Ejecutar de nuevo, no debe hacer nada)
        print("👉 4. Verifying Idempotency (Running Tick Again)...")
        old_last_run = automation.last_run_at
        
        scheduler._scan_due_jobs()
        db.refresh(automation)
        
        assert automation.last_run_at == old_last_run, "Should not have run again"
        print("   ✅ Idempotency Verified (Job skipped as not due)")

        print("\n🏁 [QA Scheduler] All Tests Passed Successfully!")
        
    except Exception as e:
        print(f"\n❌ [QA Scheduler] FAILED: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_scheduler_flow()
