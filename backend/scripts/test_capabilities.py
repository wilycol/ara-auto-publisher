import sys
import os

# Add backend path to sys.path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.capability_resolver import CapabilityResolverService
from app.services.media_stubs import ImageGeneratorStub, VideoGeneratorStub

def run_tests():
    print("🚀 Starting Capability & Monetization QA Test...\n")
    
    resolver = CapabilityResolverService(policy_version="v1.1")
    img_gen = ImageGeneratorStub(resolver)
    vid_gen = VideoGeneratorStub(resolver)

    # ---------------------------------------------------------
    # TEST 1: Strict Plan (Free) - Image Quota
    # ---------------------------------------------------------
    print("🧪 TEST 1: Strict Plan Image Quota (Max 3)...")
    user_id = "user_free"
    plan = "strict"
    
    # Intentar 3 permitidas
    try:
        for i in range(3):
            img_gen.generate(user_id, plan, f"prompt {i}")
        print("   ✅ First 3 images allowed")
    except Exception as e:
        print(f"   ❌ Unexpected failure: {e}")

    # Intentar la 4ta (Debe fallar)
    try:
        img_gen.generate(user_id, plan, "prompt 4")
        print("   ❌ FAIL: 4th image should have been blocked")
    except PermissionError:
        print("   ✅ PASS: 4th image blocked correctly (Quota Exceeded)")

    # ---------------------------------------------------------
    # TEST 2: Strict Plan (Free) - Video Not Allowed
    # ---------------------------------------------------------
    print("\n🧪 TEST 2: Strict Plan Video Capability...")
    try:
        vid_gen.generate(user_id, plan, "video prompt", duration=10)
        print("   ❌ FAIL: Video should be disabled for strict plan")
    except PermissionError:
        print("   ✅ PASS: Video request denied correctly")

    # ---------------------------------------------------------
    # TEST 3: Educational Plan - Video Duration Limit
    # ---------------------------------------------------------
    print("\n🧪 TEST 3: Educational Plan Video Duration...")
    user_id = "user_edu"
    plan = "educational" # Max duration 30s
    
    # Intento válido (20s)
    try:
        vid_gen.generate(user_id, plan, "video valid", duration=20)
        print("   ✅ 20s video allowed")
    except Exception as e:
        print(f"   ❌ Unexpected failure: {e}")

    # Intento inválido (45s)
    try:
        vid_gen.generate(user_id, plan, "video too long", duration=45)
        print("   ❌ FAIL: 45s video should be blocked (Max 30s)")
    except PermissionError:
        print("   ✅ PASS: 45s video blocked correctly (Duration Limit)")

    print("\n🏁 Capability QA Tests Completed.")

if __name__ == "__main__":
    run_tests()
