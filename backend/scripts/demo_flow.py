import requests
import time
import sys
import json

API_URL = "http://localhost:8000/api/v1"

def log(msg):
    print(f"[DEMO] {msg}")

def run_demo():
    print("""
    ================================================
    Ara Neuro Post - Validation Script
    ================================================
    """)
    
    # 1. Check health
    try:
        r = requests.get("http://localhost:8000/health")
        if r.status_code != 200:
            log("❌ API not healthy. Exiting.")
            return
        log("✅ API is online and healthy.")
    except Exception:
        log("❌ Cannot connect to API. Is it running? (Run 'uvicorn app.main:app' in backend folder)")
        return

    # 2. Create Project
    log("Creating Demo Project...")
    project_payload = {"name": f"Demo Project {int(time.time())}", "description": "Auto-generated for demo"}
    r = requests.post(f"{API_URL}/projects/", json=project_payload)
    if r.status_code != 200:
        log(f"❌ Error creating project: {r.text}")
        return
    project = r.json()["data"]
    project_id = project["id"]
    log(f"✅ Project created: ID {project_id} - {project['name']}")

    # 3. Create Topic
    log("Creating Topic 'Artificial Intelligence'...")
    topic_payload = {
        "project_id": project_id,
        "name": "Artificial Intelligence",
        "keywords": "future, neural networks, automation, deepseek",
        "weight": 10
    }
    r = requests.post(f"{API_URL}/topics/", json=topic_payload)
    if r.status_code != 200:
        log(f"❌ Error creating topic: {r.text}")
        return
    topic = r.json()["data"]
    log(f"✅ Topic created: ID {topic['id']} - {topic['name']}")

    # 4. Create Job
    log("Configuring Auto Publisher Job...")
    job_payload = {
        "project_id": project_id,
        "name": "Morning AI Posts",
        "active": True,
        "posts_per_day": 3,
        "time_window_start": "08:00",
        "time_window_end": "11:00"
    }
    r = requests.post(f"{API_URL}/jobs/", json=job_payload)
    if r.status_code != 200:
        log(f"❌ Error creating job: {r.text}")
        return
    job = r.json()["data"]
    job_id = job["id"]
    log(f"✅ Job created: ID {job_id} - {job['name']}")

    # 5. Run Job Manually
    log(f"🚀 EXECUTING Auto Publisher for Job {job_id}...")
    r = requests.post(f"{API_URL}/jobs/run/{job_id}")
    if r.status_code != 200:
        log(f"❌ Error running job: {r.text}")
        return
    
    generated_post = r.json()["data"]
    log("✅ Job executed successfully!")
    print(f"\n📄 GENERATED POST CONTENT:\n{'-'*40}")
    print(f"Title: {generated_post['title']}")
    print(f"Status: {generated_post['status']}")
    print(f"Content:\n{generated_post['content_text']}")
    print(f"{'-'*40}\n")

    # 6. Verify Post in List
    log("Verifying post persistence in DB...")
    r = requests.get(f"{API_URL}/posts/?project_id={project_id}")
    posts = r.json()["data"]
    log(f"✅ Found {len(posts)} posts for this project in database.")
    
    print("""
    ================================================
    DEMO COMPLETED SUCCESSFULLY
    ================================================
    """)

if __name__ == "__main__":
    run_demo()
