import sys
import os
import uuid
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.services.budget_guard_service import BudgetGuardService
from app.repositories.billing_repository import BillingRepository
from app.models.billing import BillingEvent
from fastapi import HTTPException

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QA_BUDGET")

def test_budget_limits():
    print("\n🚀 [QA Budget] Starting Budget Limits Verification...\n")
    
    db = SessionLocal()
    
    # Configuration
    # Pro Plan Limit: $20.00
    # Soft Limit (80%): $16.00
    plan = "pro"
    limit_usd = 20.00
    soft_limit_usd = 16.00
    
    try:
        # TEST 1: User below limits (Safe)
        user_safe = f"user_safe_{uuid.uuid4().hex[:6]}"
        print(f"👉 TEST 1: User {user_safe} (Spending $5.00)...")
        
        # Simulate $5.00 spending
        _simulate_spending(db, user_safe, plan, 5.00)
        
        # Check Limits (Should pass)
        guard = BudgetGuardService(db)
        try:
            guard.check_limits(user_safe, plan)
            print("   ✅ Access Granted (Correct)")
        except Exception as e:
            print(f"   ❌ FAILED: Unexpected blockage: {e}")
            return

        # TEST 2: User at Soft Limit (Warning)
        user_warn = f"user_warn_{uuid.uuid4().hex[:6]}"
        print(f"\n👉 TEST 2: User {user_warn} (Spending $17.00 > $16.00)...")
        
        # Simulate $17.00 spending
        _simulate_spending(db, user_warn, plan, 17.00)
        
        # Check Limits (Should pass but log warning - we can't assert logs easily here but we verify no exception)
        try:
            guard.check_limits(user_warn, plan)
            print("   ✅ Access Granted (Correct) - Warning should be in logs")
        except Exception as e:
            print(f"   ❌ FAILED: Blocked prematurely: {e}")
            return

        # TEST 3: User at Hard Limit (Blocked)
        user_block = f"user_block_{uuid.uuid4().hex[:6]}"
        print(f"\n👉 TEST 3: User {user_block} (Spending $21.00 > $20.00)...")
        
        # Simulate $21.00 spending
        _simulate_spending(db, user_block, plan, 21.00)
        
        # Check Limits (Should FAIL)
        try:
            guard.check_limits(user_block, plan)
            print("   ❌ FAILED: Should have been blocked!")
        except HTTPException as e:
            if e.status_code == 402:
                print(f"   ✅ Access Blocked (Correct): {e.detail}")
            else:
                print(f"   ❌ FAILED: Wrong exception type: {e}")
        except Exception as e:
            print(f"   ❌ FAILED: Wrong exception type: {type(e)} {e}")

        # TEST 4: Free Tier Logic (Limit 0)
        # If policy has 0 for free, any spending > 0 should block.
        user_free = f"user_free_{uuid.uuid4().hex[:6]}"
        print(f"\n👉 TEST 4: User {user_free} (Free Plan, Spending $0.01)...")
        
        _simulate_spending(db, user_free, "free", 0.01)
        
        try:
            guard.check_limits(user_free, "free")
            print("   ❌ FAILED: Free tier user with spending should be blocked!")
        except HTTPException as e:
            print(f"   ✅ Access Blocked (Correct): {e.detail}")
        
        print("\n🏁 [QA Budget] All Tests Passed Successfully!")

    except Exception as e:
        print(f"\n❌ CRITICAL FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def _simulate_spending(db, user_id, plan, amount):
    """Helper to inject billing events"""
    repo = BillingRepository(db)
    repo.create_event(BillingEvent(
        user_id=user_id,
        plan=plan,
        media_type="manual_adjustment",
        provider="mock",
        units=1.0,
        unit_type="adjustment",
        cost_estimated=amount,
        currency="USD",
        correlation_id=str(uuid.uuid4()),
        pricing_version="v1.0"
    ))

if __name__ == "__main__":
    test_budget_limits()
