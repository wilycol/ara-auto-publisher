from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_flow():
    # 1. Create Forum
    print("Creating Forum...")
    forum_data = {
        "name": "Reddit SaaS",
        "source_type": "reddit",
        "base_url": "https://reddit.com/r/saas"
    }
    response = client.post("/api/v1/forums/", json=forum_data) 
    
    if response.status_code != 200:
        print(f"Failed to create forum: {response.status_code} {response.text}")
        return
    
    forum = response.json()
    print(f"Forum created: {forum}")
    forum_id = forum['id']

    # 2. Create Thread
    print(f"Creating Thread in Forum {forum_id}...")
    thread_data = {
        "title": "How do you validate a SaaS MVP?",
        "content": "I'm struggling to get early users...",
        "author": "throwaway123",
        "url": "https://reddit.com/r/saas/comments/xyz/validate"
    }
    response = client.post(f"/api/v1/forums/{forum_id}/threads", json=thread_data)
    
    if response.status_code != 200:
        print(f"Failed to create thread: {response.status_code} {response.text}")
        return
        
    thread = response.json()
    print(f"Thread created: {thread}")
    
    # 3. List Threads
    print("Listing Threads...")
    response = client.get(f"/api/v1/forums/{forum_id}/threads")
    if response.status_code != 200:
        print(f"Failed to list threads: {response.status_code} {response.text}")
        return
    
    threads = response.json()
    print(f"Threads found: {len(threads)}")
    print(threads)

if __name__ == "__main__":
    test_flow()
