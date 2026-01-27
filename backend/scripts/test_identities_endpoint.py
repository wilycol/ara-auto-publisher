import requests

try:
    response = requests.get("http://localhost:8000/api/v1/identities/?project_id=1")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
