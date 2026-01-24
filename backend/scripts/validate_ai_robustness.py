import sys
import os
import time
from unittest.mock import patch, MagicMock
import httpx
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.services.auto_publisher import AutoPublisherService
from app.services.ai_client import OpenAICompatibleClient
from app.models.domain import Post, AutoPublisherJob

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def log(msg):
    print(f"[ROBUSTNESS_TEST] {msg}")

def test_scenario(name, client, db, job_id, expected_error_substr=None):
    log(f"--- Testing Scenario: {name} ---")
    
    # Count posts before
    initial_count = db.query(Post).count()
    
    service = AutoPublisherService(ai_client=client)
    
    try:
        service.run(db, job_id)
        log("❌ Unexpected Success! (Should have failed)")
    except Exception as e:
        error_msg = str(e)
        log(f"✅ Caught Expected Exception: {error_msg}")
        if expected_error_substr and expected_error_substr.lower() not in error_msg.lower():
            log(f"⚠️ Warning: Exception message did not contain '{expected_error_substr}'")
    
    # Verify DB consistency
    final_count = db.query(Post).count()
    if final_count == initial_count:
        log("✅ DB Consistency Verified: No corrupt posts created.")
    else:
        log(f"❌ DB INCONSISTENCY: Post count changed from {initial_count} to {final_count}!")

def run_tests():
    log("Starting AI Connector Robustness Validation...")
    
    db = next(get_db())
    
    # Ensure we have a job
    job = db.query(AutoPublisherJob).first()
    if not job:
        log("❌ No jobs found in DB. Please run demo_flow.py first to seed data.")
        return

    job_id = job.id
    log(f"Using Job ID: {job_id}")

    # 1. Test: Base URL Invalid (Real Network Attempt)
    # This will actually try to connect to a non-existent URL
    log("\n[1] Testing Invalid Base URL (Real Network Call)")
    client_invalid_url = OpenAICompatibleClient(
        api_key="dummy",
        base_url="http://non-existent-url-xyz-123.local",
        model="test"
    )
    test_scenario("Invalid Base URL", client_invalid_url, db, job_id, expected_error_substr="ConnectError")

    # 2. Test: API Key Invalid (Mocked 401)
    # We mock the response because we don't want to hit real OpenAI/DeepSeek with bad keys repeatedly
    log("\n[2] Testing Invalid API Key (Simulated 401)")
    client_auth_error = OpenAICompatibleClient(
        api_key="invalid-key",
        base_url="https://api.deepseek.com/v1",
        model="test"
    )
    
    with patch("httpx.Client.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", request=MagicMock(), response=mock_response
        )
        mock_post.return_value = mock_response
        
        test_scenario("Auth Error (401)", client_auth_error, db, job_id, expected_error_substr="401")

    # 3. Test: Timeout (Simulated)
    # We mock the timeout because the hardcoded timeout is 30s
    log("\n[3] Testing Timeout (Simulated)")
    client_timeout = OpenAICompatibleClient(
        api_key="valid-key",
        base_url="https://api.deepseek.com/v1",
        model="test"
    )
    
    with patch("httpx.Client.post") as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Request timed out")
        
        test_scenario("Timeout", client_timeout, db, job_id, expected_error_substr="timed out")

    log("\n--- Robustness Validation Complete ---")

if __name__ == "__main__":
    run_tests()
