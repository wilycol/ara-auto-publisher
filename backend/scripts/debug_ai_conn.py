
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load env manually to be sure
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.services.ai_provider_service import ai_provider_service

import httpx

async def list_gemini_models(api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={"key": api_key})
        print(f"   Gemini Models List Status: {resp.status_code}")
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            names = [m['name'] for m in models]
            print(f"   Available Models: {names}")
        else:
            print(f"   Error listing models: {resp.text}")

async def test_providers():
    print("🔍 Testing AI Providers Connectivity & Generation...")
    print(f"Loaded Providers: {[p.name for p in ai_provider_service.providers]}")
    
    prompt = "Hi, are you working?"
    
    for provider in ai_provider_service.providers:
        print(f"\n👉 Testing Provider: {provider.name}")
        
        # 1. Health Check
        try:
            is_healthy = await provider.check_health()
            print(f"   Health Check: {'✅ PASS' if is_healthy else '❌ FAIL'}")
        except Exception as e:
            print(f"   Health Check Error: {e}")
            
        if provider.name == "gemini" and not is_healthy:
             print("   🕵️ Investigating Gemini Models...")
             await list_gemini_models(provider.api_key)
            
        # 2. Generation Check (only if not local fallback, or test it anyway)
        if provider.name == "local_fallback":
            print("   Skipping generation for local fallback (it always works)")
            continue
            
        try:
            print("   Attempting Generation...")
            response = await provider.generate(prompt)
            print(f"   Generation: ✅ SUCCESS")
            print(f"   Response Preview: {response[:50]}...")
        except Exception as e:
            print(f"   Generation Error: ❌ {e}")

if __name__ == "__main__":
    asyncio.run(test_providers())
