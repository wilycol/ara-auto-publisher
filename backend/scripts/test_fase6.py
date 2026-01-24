import sys
import os
import json
import time

# Add backend path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import engine, SessionLocal
# Import models to ensure they are registered with Base
from app.models.domain import MediaUsage, Base
from app.services.capability_resolver import CapabilityResolverService
from app.services.media_stubs import ImageGeneratorStub

def setup_db():
    print("🛠️ Creating tables if not exist...")
    Base.metadata.create_all(bind=engine)
    
    # Clean up test data
    db = SessionLocal()
    try:
        db.query(MediaUsage).filter(MediaUsage.user_id.like("user_fase6%")).delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        print(f"Warning cleaning DB: {e}")
    finally:
        db.close()

def test_persistence():
    print("\n🧪 TEST 1: Persistence of Usage")
    resolver = CapabilityResolverService()
    stub = ImageGeneratorStub(resolver)
    
    user_id = "user_fase6_persist"
    plan = "strict"
    
    # 1. Get initial usage (Should be 0 after cleanup)
    initial = resolver._get_usage(user_id, "image")
    print(f"   Initial usage: {initial}")
    
    # 2. Generate
    print("   Generating image...")
    try:
        stub.generate(user_id, plan, "Test Persistence")
    except Exception as e:
        print(f"   ❌ Generation failed: {e}")
        return

    # 3. Check increment
    after = resolver._get_usage(user_id, "image")
    print(f"   Usage after gen: {after}")
    
    if after == initial + 1:
        print("   ✅ Usage incremented correctly")
    else:
        print(f"   ❌ FAIL: Usage did not increment (Expected {initial+1}, got {after})")
        
    # 4. New Instance (Simulate restart)
    print("   Creating new Resolver instance (Simulate restart)...")
    resolver2 = CapabilityResolverService()
    after_restart = resolver2._get_usage(user_id, "image")
    
    if after_restart == after:
        print("   ✅ Usage persisted across instances")
    else:
        print(f"   ❌ FAIL: Usage lost! (Got {after_restart})")

def test_providers():
    print("\n🧪 TEST 2: Provider Switching")
    resolver = CapabilityResolverService()
    stub = ImageGeneratorStub(resolver)
    user_id = "user_fase6_prov"
    plan = "educational" # More quota
    
    # 1. Default (Mock)
    print("   🔹 Testing Mock Provider (Default)...")
    # Force Mock
    os.environ["MEDIA_PROVIDER"] = "mock"
    
    try:
        res = stub.generate(user_id, plan, "Mock Test")
        if res.get("provider") == "mock":
            print("   ✅ Mock Provider used")
        else:
            print(f"   ❌ FAIL: Expected mock, got {res.get('provider')}")
    except Exception as e:
        print(f"   ❌ Mock gen failed: {e}")

    # 2. Switch to OpenAI
    print("   🔹 Testing OpenAI Provider (via ENV)...")
    os.environ["MEDIA_PROVIDER"] = "openai"
    
    try:
        res = stub.generate(user_id, plan, "OpenAI Test")
        if res.get("provider") == "openai-dall-e-3":
            print("   ✅ OpenAI Provider used")
        else:
            print(f"   ❌ FAIL: Expected openai-dall-e-3, got {res.get('provider')}")
    except Exception as e:
        print(f"   ❌ OpenAI gen failed: {e}")

    # Reset ENV
    os.environ["MEDIA_PROVIDER"] = "mock"

if __name__ == "__main__":
    setup_db()
    test_persistence()
    test_providers()
