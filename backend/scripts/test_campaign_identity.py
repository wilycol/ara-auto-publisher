import sys
import os
import requests
import json
import uuid

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
PROJECT_ID = 1

def test_flow():
    print("🚀 Testing Campaign Identity Flow...")

    # 1. Create Identity
    identity_payload = {
        "name": f"Test Identity {uuid.uuid4().hex[:8]}",
        "purpose": "Testing integration",
        "tone": "Technical",
        "preferred_platforms": ["linkedin"],
        "status": "active"
    }
    
    print(f"1. Creating Identity: {identity_payload['name']}...")
    try:
        res = requests.post(f"{BASE_URL}/identities/?project_id={PROJECT_ID}", json=identity_payload)
        if res.status_code != 200:
            print(f"❌ Failed to create identity: {res.text}")
            return
        identity = res.json()
        identity_id = identity['id']
        print(f"✅ Identity Created: {identity_id}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    # 2. Create Campaign with Identity
    campaign_payload = {
        "project_id": PROJECT_ID,
        "name": f"Campaign with Identity {uuid.uuid4().hex[:6]}",
        "objective": "Verify identity linkage",
        "tone": "Professional",
        "identity_id": identity_id,
        "status": "active",
        "start_date": "2026-01-01"
    }
    
    print(f"2. Creating Campaign linked to Identity...")
    try:
        res = requests.post(f"{BASE_URL}/campaigns/", json=campaign_payload)
        if res.status_code != 201:
            print(f"❌ Failed to create campaign: {res.text}")
            return
        campaign = res.json()
        print(f"✅ Campaign Created: {campaign['id']}")
        
        # 3. Verify Linkage
        if campaign.get('identity_id') == identity_id:
            print(f"✅ SUCCESS: Campaign is linked to Identity {identity_id}")
        else:
            print(f"❌ FAILURE: Campaign identity_id mismatch. Expected {identity_id}, got {campaign.get('identity_id')}")
            
    except Exception as e:
        print(f"❌ Error creating campaign: {e}")

if __name__ == "__main__":
    test_flow()
