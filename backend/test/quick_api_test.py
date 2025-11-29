import requests
import json

print("Testing MedPredict AI API Endpoints\n" + "="*50)

# Test 1: Root
print("\n[Test 1] Root Endpoint")
try:
    r = requests.get('http://localhost:8000/')
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Health
print("\n[Test 2] Health Check")
try:
    r = requests.get('http://localhost:8000/health')
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Dashboard Overview
print("\n[Test 3] Dashboard Overview")
try:
    r = requests.get('http://localhost:8000/api/v1/dashboard/overview')
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print("✓ SUCCESS - Dashboard data retrieved")
        print(f"  Total Patients: {data.get('analysis', {}).get('prediction', {}).get('total_patients', 'N/A')}")
        print(f"  Bed Occupancy: {data.get('analysis', {}).get('resources', {}).get('bed_occupancy_predicted', 'N/A')}%")
    else:
        print(f"✗ FAILED - {r.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Forecast Quick
print("\n[Test 4] Quick Forecast")
try:
    r = requests.get('http://localhost:8000/api/v1/forecast/quick?days=3')
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✓ SUCCESS - Got {len(data.get('predictions', []))} day forecast")
        if data.get('predictions'):
            print(f"  First day: {data['predictions'][0]}")
    else:
        print(f"✗ FAILED - {r.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 5: Department Utilization
print("\n[Test 5] Department Utilization")
try:
    r = requests.get('http://localhost:8000/api/v1/departments/utilization')
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✓ SUCCESS - Got {data.get('total_departments', 0)} departments")
        if data.get('departments'):
            print(f"  Top department: {data['departments'][0]}")
    else:
        print(f"✗ FAILED - {r.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50)
print("API Testing Complete!")
