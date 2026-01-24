import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def debug_posts():
    print("🔍 Inspeccionando Posts en BD...")
    
    # We don't have a public GET /posts endpoint that returns everything yet, 
    # but we can check if we can query via project or just add a temp endpoint?
    # Actually, api/posts.py likely has a list endpoint. Let's check api/posts.py content first or just try GET /posts
    
    try:
        res = requests.get(f"{BASE_URL}/posts")
        if res.status_code == 200:
            posts = res.json().get("data", []) # Assuming standard response format
            print(f"   Encontrados {len(posts)} posts.")
            for p in posts:
                print(f"   🆔 {p.get('id')} | 📅 {p.get('status')} | 📢 {p.get('title')}")
                print(f"      Campaign ID: {p.get('campaign_id')} (Should not be None)")
                print(f"      Content: {p.get('content_text')[:50]}...")
        else:
            print(f"❌ Error listing posts: {res.status_code} - {res.text}")
            # If standard endpoint doesn't exist or is different, we might fail here.
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_posts()
