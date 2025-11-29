import requests
import time
import sys

def test_api():
    print("Testing Patient Volume Forecasting API...")
    base_url = "http://127.0.0.1:8000"
    
    # Wait for server to start
    print("Waiting for server to start...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/health")
            if response.status_code == 200:
                print("Server is up!")
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            print(f"Retrying... ({i+1}/10)")
    else:
        print("Failed to connect to server.")
        sys.exit(1)

    # Test Health Check
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Response: {data}")
        if data['model_loaded'] and data['data_loaded']:
            print("✅ Health check passed: Model and Data loaded.")
        else:
            print("❌ Health check failed: Model or Data not loaded.")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

    # Test Prediction (Quick)
    print("\n2. Testing /predict/quick endpoint...")
    try:
        response = requests.get(f"{base_url}/predict/quick?days=7")
        if response.status_code == 200:
            data = response.json()
            print("✅ Prediction successful!")
            print(f"Forecast Period: {data['forecast_period']}")
            print(f"Avg Daily Patients: {data['avg_daily_patients']}")
            print(f"First Prediction: {data['predictions'][0]}")
        else:
            print(f"❌ Prediction failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")

    # Test Prediction (Specific Date)
    print("\n3. Testing /predict endpoint (specific dates)...")
    try:
        response = requests.get(f"{base_url}/predict?start_date=2025-12-01&end_date=2025-12-05")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Specific date prediction successful! Got {len(data)} days.")
            print(f"Sample: {data[0]}")
        else:
            print(f"❌ Specific date prediction failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Specific date prediction failed: {e}")

if __name__ == "__main__":
    test_api()
