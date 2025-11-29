"""
Comprehensive API Test Script
Tests all endpoints of the unified API.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, method="GET", data=None):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
            
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS")
            print(f"Response Preview:")
            print(json.dumps(data, indent=2)[:500] + "...")
            return True
        else:
            print(f"✗ FAILED")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ CONNECTION ERROR - Is the server running?")
        return False
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("MedPredict AI - API Test Suite")
    print("="*60)
    print(f"Testing server at: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test Root
    results['root'] = test_endpoint(
        "Root Endpoint",
        f"{BASE_URL}/"
    )
    
    # Test Health
    results['health'] = test_endpoint(
        "Health Check",
        f"{BASE_URL}/health"
    )
    
    # Test Dashboard Overview
    results['dashboard'] = test_endpoint(
        "Dashboard Overview",
        f"{BASE_URL}/api/v1/dashboard/overview"
    )
    
    # Test Analytics - Surge Patterns
    results['surge'] = test_endpoint(
        "Surge Patterns",
        f"{BASE_URL}/api/v1/analytics/surge-patterns"
    )
    
    # Test Analytics - Department Trends
    results['dept_trends'] = test_endpoint(
        "Department Trends",
        f"{BASE_URL}/api/v1/analytics/department-trends"
    )
    
    # Test Analytics - Admission Predictions
    results['admissions'] = test_endpoint(
        "Admission Predictions",
        f"{BASE_URL}/api/v1/analytics/admission-predictions?days=7"
    )
    
    # Test Analytics - Environmental Impact
    results['environment'] = test_endpoint(
        "Environmental Impact",
        f"{BASE_URL}/api/v1/analytics/environmental-impact"
    )
    
    # Test Forecast - Quick
    results['forecast_quick'] = test_endpoint(
        "Quick Forecast",
        f"{BASE_URL}/api/v1/forecast/quick?days=7"
    )
    
    # Test Forecast - Predict
    results['forecast_predict'] = test_endpoint(
        "Forecast Predict",
        f"{BASE_URL}/api/v1/forecast/predict"
    )
    
    # Test Departments - Utilization
    results['dept_util'] = test_endpoint(
        "Department Utilization",
        f"{BASE_URL}/api/v1/departments/utilization"
    )
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\nDetailed Results:")
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name:20s} {status}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED - Check logs above")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
