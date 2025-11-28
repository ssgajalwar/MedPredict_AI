"""
Quick test of resources endpoint
"""
import requests
import json

print("Testing /resources/status endpoint...")
response = requests.get("http://localhost:8000/api/v1/resources/status", timeout=5)
print(f"Status Code: {response.status_code}")
print(f"\nResponse:")
print(json.dumps(response.json(), indent=2))
