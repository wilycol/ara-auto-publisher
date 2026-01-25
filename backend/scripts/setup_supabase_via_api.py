import os
import requests
import json
from dotenv import load_dotenv

# Load env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") # Anon
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # We need this if available, otherwise Anon

# If SERVICE_ROLE_KEY is missing in env but we have it in memory/chat history, we should use it.
# The user provided: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB6YXVzd2NlcmZ1cHV5cXJlcWRyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTIwMjEzOCwiZXhwIjoyMDg0Nzc4MTM4fQ.DMtT_eesx-osm2junG5BfzpNnot1EwdRyeSMvrxGz6s
# I will hardcode it here for the script to ensure it works, then remove it.
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB6YXVzd2NlcmZ1cHV5cXJlcWRyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTIwMjEzOCwiZXhwIjoyMDg0Nzc4MTM4fQ.DMtT_eesx-osm2junG5BfzpNnot1EwdRyeSMvrxGz6s"

def check_health():
    print(f"Checking Supabase Health: {SUPABASE_URL}")
    try:
        # Just check a public endpoint or root
        resp = requests.get(f"{SUPABASE_URL}/rest/v1/", headers={"apikey": SUPABASE_KEY})
        print(f"Health Status: {resp.status_code}")
        # 200 is good (even if empty list of tables)
        return resp.status_code == 200
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return False

def get_or_create_user():
    print("\n--- Managing Users via Admin API ---")
    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. List Users
    try:
        resp = requests.get(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers)
        if resp.status_code == 200:
            users = resp.json().get("users", [])
            if users:
                print(f"Found {len(users)} existing users.")
                user = users[0]
                print(f"Using existing user: {user['email']} ({user['id']})")
                return user['id']
        else:
            print(f"List users failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"List users error: {e}")

    # 2. Create User if none
    print("Creating new seed user...")
    payload = {
        "email": "dev_seed@araneropost.com",
        "password": "TempPassword123!",
        "email_confirm": True
    }
    try:
        resp = requests.post(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers, json=payload)
        if resp.status_code == 200 or resp.status_code == 201:
            user = resp.json()
            print(f"Created user: {user['email']} ({user['id']})")
            return user['id']
        else:
            print(f"Create user failed: {resp.status_code} {resp.text}")
            return None
    except Exception as e:
        print(f"Create user error: {e}")
        return None

if __name__ == "__main__":
    if check_health():
        uid = get_or_create_user()
        if uid:
            print(f"\nSUCCESS! User ID for Seeding: {uid}")
            # Write to a temp file so we can read it or just output it
            with open("seed_user_id.txt", "w") as f:
                f.write(uid)
    else:
        print("Supabase seems unreachable via REST. Check URL.")
