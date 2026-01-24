import sys
import os
import json
import uuid

# Add backend path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import engine, SessionLocal
from app.models.domain import Base
from app.models.billing import BillingEvent
from app.services.billing_service import BillingService

def setup_db():
    print("🛠️  [QA Billing] Initializing Database Schema...")
    # Aseguramos que el modelo BillingEvent esté registrado en Base.metadata
    Base.metadata.create_all(bind=engine)

def run_test():
    print("🚀 [QA Billing] Starting Billing Flow Verification...\n")
    
    db = SessionLocal()
    service = BillingService(db, policy_version="v1.0")
    
    # Escenario 1: Usuario FREE (Costo 0)
    print("🧪 TEST 1: Free Plan Usage (Should be $0.00)")
    user_free = "user_qa_free"
    job_id_1 = str(uuid.uuid4())
    
    evt1 = service.record_usage_event(
        user_id=user_free,
        plan="free",
        media_type="image",
        provider="mock",
        units=1,
        unit_type="image",
        correlation_id=job_id_1
    )
    
    print(f"   Event ID: {evt1.id} | Cost: ${evt1.cost_estimated}")
    if evt1.cost_estimated == 0.0:
        print("   ✅ PASS: Cost is 0.0 for free plan")
    else:
        print(f"   ❌ FAIL: Expected 0.0, got {evt1.cost_estimated}")

    # Escenario 2: Usuario PRO (Costo > 0)
    print("\n🧪 TEST 2: Pro Plan Image Usage (Should be $0.04)")
    user_pro = "user_qa_pro"
    job_id_2 = str(uuid.uuid4())
    
    evt2 = service.record_usage_event(
        user_id=user_pro,
        plan="pro",
        media_type="image",
        provider="openai",
        units=1,
        unit_type="image",
        correlation_id=job_id_2
    )
    
    print(f"   Event ID: {evt2.id} | Cost: ${evt2.cost_estimated}")
    if evt2.cost_estimated == 0.04:
        print("   ✅ PASS: Cost is 0.04 for pro plan")
    else:
        print(f"   ❌ FAIL: Expected 0.04, got {evt2.cost_estimated}")

    # Escenario 3: Usuario ENTERPRISE - Video (Costo variable)
    print("\n🧪 TEST 3: Enterprise Video Usage (15s * $0.08 = $1.20)")
    user_ent = "user_qa_ent"
    job_id_3 = str(uuid.uuid4())
    duration = 15
    
    evt3 = service.record_usage_event(
        user_id=user_ent,
        plan="enterprise",
        media_type="video",
        provider="runway",
        units=duration,
        unit_type="second",
        correlation_id=job_id_3
    )
    
    print(f"   Event ID: {evt3.id} | Cost: ${evt3.cost_estimated}")
    # 15 * 0.08 = 1.2
    if abs(evt3.cost_estimated - 1.2) < 0.0001:
        print("   ✅ PASS: Cost calculation is correct (1.20)")
    else:
        print(f"   ❌ FAIL: Expected 1.20, got {evt3.cost_estimated}")

    db.close()
    print("\n🏁 [QA Billing] Tests Completed.")

if __name__ == "__main__":
    setup_db()
    run_test()
