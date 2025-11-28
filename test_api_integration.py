"""
API Integration Test Suite
Tests if API is correctly fetching data from media folder and serving it
"""
import requests
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
MEDIA_PATH = Path(__file__).parent / "media"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_test(test_name, status, details=""):
    """Print test result"""
    status_symbol = f"{Colors.GREEN}✓{Colors.END}" if status else f"{Colors.RED}✗{Colors.END}"
    print(f"{status_symbol} {Colors.BOLD}{test_name}{Colors.END}")
    if details:
        print(f"  {Colors.YELLOW}{details}{Colors.END}")

def print_data(label, data, indent=2):
    """Print formatted data"""
    indent_str = " " * indent
    print(f"{indent_str}{Colors.BLUE}{label}:{Colors.END} {data}")

# Test Results Storage
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def run_test(test_name, test_func):
    """Run a test and record results"""
    global test_results
    test_results["total"] += 1
    
    try:
        result = test_func()
        if result["success"]:
            test_results["passed"] += 1
            print_test(test_name, True, result.get("message", ""))
        else:
            test_results["failed"] += 1
            print_test(test_name, False, result.get("message", ""))
        
        test_results["tests"].append({
            "name": test_name,
            "success": result["success"],
            "details": result
        })
        
        return result
    except Exception as e:
        test_results["failed"] += 1
        print_test(test_name, False, f"Exception: {str(e)}")
        test_results["tests"].append({
            "name": test_name,
            "success": False,
            "error": str(e)
        })
        return {"success": False, "message": str(e)}

# ============================================================================
# BACKEND TESTS - Media Folder Data Reading
# ============================================================================

def test_media_folder_exists():
    """Test if media folder exists and has expected structure"""
    expected_folders = ["data/hospital_data", "allocations", "forecasts"]
    
    if not MEDIA_PATH.exists():
        return {"success": False, "message": f"Media folder not found at {MEDIA_PATH}"}
    
    missing_folders = []
    for folder in expected_folders:
        if not (MEDIA_PATH / folder).exists():
            missing_folders.append(folder)
    
    if missing_folders:
        return {"success": False, "message": f"Missing folders: {', '.join(missing_folders)}"}
    
    return {"success": True, "message": f"Media folder structure is correct"}

def test_csv_files_exist():
    """Test if required CSV files exist in media folder"""
    required_files = [
        "data/hospital_data/patient_visits.csv",
        "data/hospital_data/staff.csv",
        "data/hospital_data/supply_inventory.csv",
        "data/hospital_data/weather_data.csv",
        "data/hospital_data/events.csv"
    ]
    
    missing_files = []
    file_info = []
    
    for file_path in required_files:
        full_path = MEDIA_PATH / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            # Get file info
            df = pd.read_csv(full_path)
            file_info.append(f"{file_path.split('/')[-1]}: {len(df)} rows")
    
    if missing_files:
        return {"success": False, "message": f"Missing files: {', '.join(missing_files)}"}
    
    return {"success": True, "message": f"All CSV files found. {', '.join(file_info)}"}

def test_allocation_json_exists():
    """Test if allocation JSON file exists"""
    allocation_path = MEDIA_PATH / "allocations"
    json_files = list(allocation_path.glob("allocation_output_*.json"))
    
    if not json_files:
        return {"success": False, "message": "No allocation JSON files found"}
    
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return {"success": True, "message": f"Found allocation file: {latest_file.name}, Keys: {list(data.keys())}"}

# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

def test_dashboard_overview_endpoint():
    """Test /dashboard/overview endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/overview", timeout=10)
        
        if response.status_code != 200:
            return {"success": False, "message": f"HTTP {response.status_code}: {response.text}"}
        
        data = response.json()
        
        # Check for expected keys
        expected_keys = ["sensory_data", "real_data", "forecast", "analysis"]
        missing_keys = [key for key in expected_keys if key not in data]
        
        if missing_keys:
            return {"success": False, "message": f"Missing keys: {', '.join(missing_keys)}"}
        
        # Check if real_data contains actual data from media folder
        real_data = data.get("real_data", {})
        patients = real_data.get("patients", {})
        
        if patients.get("total_patients", 0) == 0:
            return {"success": False, "message": "No patient data loaded from media folder"}
        
        return {
            "success": True, 
            "message": f"API returned data. Patients: {patients.get('total_patients')}, Latest Date: {patients.get('latest_date')}",
            "data": data
        }
        
    except requests.exceptions.ConnectionError:
        return {"success": False, "message": "Cannot connect to API. Is the backend running on port 8000?"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def test_resources_status_endpoint():
    """Test /resources/status endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/resources/status", timeout=10)
        
        if response.status_code != 200:
            return {"success": False, "message": f"HTTP {response.status_code}"}
        
        data = response.json()
        
        # Check for expected data
        if "staff" not in data and "inventory" not in data:
            return {"success": False, "message": "Missing staff or inventory data"}
        
        return {
            "success": True,
            "message": f"Resources endpoint working. Staff: {data.get('staff', {}).get('total_staff')}, Inventory items: {data.get('inventory', {}).get('total_items')}",
            "data": data
        }
        
    except requests.exceptions.ConnectionError:
        return {"success": False, "message": "Cannot connect to API"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

def test_patient_data_from_csv():
    """Test if patient data from API matches CSV file"""
    try:
        # Read from CSV
        csv_path = MEDIA_PATH / "data/hospital_data/patient_visits.csv"
        df = pd.read_csv(csv_path)
        df['visit_date'] = pd.to_datetime(df['visit_date'])
        latest_date = df['visit_date'].max()
        latest_data = df[df['visit_date'] == latest_date]
        csv_patient_count = len(latest_data)
        
        # Get from API
        response = requests.get(f"{API_BASE_URL}/dashboard/overview", timeout=10)
        api_data = response.json()
        api_patient_count = api_data.get("real_data", {}).get("patients", {}).get("total_patients", 0)
        
        if csv_patient_count == api_patient_count:
            return {
                "success": True,
                "message": f"Patient count matches! CSV: {csv_patient_count}, API: {api_patient_count}"
            }
        else:
            return {
                "success": False,
                "message": f"Mismatch! CSV: {csv_patient_count}, API: {api_patient_count}"
            }
            
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def test_staff_data_from_csv():
    """Test if staff data from API matches CSV file"""
    try:
        # Read from CSV
        csv_path = MEDIA_PATH / "data/hospital_data/staff.csv"
        df = pd.read_csv(csv_path)
        csv_staff_count = len(df)
        
        # Get from API
        response = requests.get(f"{API_BASE_URL}/resources/status", timeout=10)
        api_data = response.json()
        api_staff_count = api_data.get("staff", {}).get("total_staff", 0)
        
        if csv_staff_count == api_staff_count:
            return {
                "success": True,
                "message": f"Staff count matches! CSV: {csv_staff_count}, API: {api_staff_count}"
            }
        else:
            return {
                "success": False,
                "message": f"Mismatch! CSV: {csv_staff_count}, API: {api_staff_count}"
            }
            
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def test_inventory_data_from_csv():
    """Test if inventory data from API matches CSV file"""
    try:
        # Read from CSV
        csv_path = MEDIA_PATH / "data/hospital_data/supply_inventory.csv"
        df = pd.read_csv(csv_path)
        csv_item_count = len(df)
        
        # Get from API
        response = requests.get(f"{API_BASE_URL}/resources/status", timeout=10)
        api_data = response.json()
        api_item_count = api_data.get("inventory", {}).get("total_items", 0)
        
        if csv_item_count == api_item_count:
            return {
                "success": True,
                "message": f"Inventory count matches! CSV: {csv_item_count}, API: {api_item_count}"
            }
        else:
            return {
                "success": False,
                "message": f"Mismatch! CSV: {csv_item_count}, API: {api_item_count}"
            }
            
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

# ============================================================================
# FRONTEND CONNECTIVITY TEST
# ============================================================================

def test_frontend_running():
    """Test if frontend is accessible"""
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            return {"success": True, "message": "Frontend is running on port 5173"}
        else:
            return {"success": False, "message": f"Frontend returned status {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "message": "Frontend not accessible on port 5173"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    print_header("API INTEGRATION TEST SUITE")
    print(f"{Colors.BOLD}Testing if API correctly fetches data from media folder{Colors.END}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Section 1: Media Folder Tests
    print(f"\n{Colors.BOLD}{Colors.BLUE}[1] MEDIA FOLDER STRUCTURE TESTS{Colors.END}")
    print("-" * 80)
    run_test("Media folder exists with correct structure", test_media_folder_exists)
    run_test("Required CSV files exist", test_csv_files_exist)
    run_test("Allocation JSON file exists", test_allocation_json_exists)
    
    # Section 2: API Endpoint Tests
    print(f"\n{Colors.BOLD}{Colors.BLUE}[2] API ENDPOINT TESTS{Colors.END}")
    print("-" * 80)
    dashboard_result = run_test("Dashboard overview endpoint", test_dashboard_overview_endpoint)
    resources_result = run_test("Resources status endpoint", test_resources_status_endpoint)
    
    # Section 3: Data Validation Tests
    print(f"\n{Colors.BOLD}{Colors.BLUE}[3] DATA VALIDATION TESTS (CSV vs API){Colors.END}")
    print("-" * 80)
    run_test("Patient data matches CSV", test_patient_data_from_csv)
    run_test("Staff data matches CSV", test_staff_data_from_csv)
    run_test("Inventory data matches CSV", test_inventory_data_from_csv)
    
    # Section 4: Frontend Tests
    print(f"\n{Colors.BOLD}{Colors.BLUE}[4] FRONTEND CONNECTIVITY TEST{Colors.END}")
    print("-" * 80)
    run_test("Frontend is running", test_frontend_running)
    
    # Print detailed data samples
    if dashboard_result.get("success") and dashboard_result.get("data"):
        print(f"\n{Colors.BOLD}{Colors.BLUE}[5] SAMPLE DATA FROM API{Colors.END}")
        print("-" * 80)
        data = dashboard_result["data"]
        
        print(f"\n{Colors.BOLD}Real Data from Media Folder:{Colors.END}")
        real_data = data.get("real_data", {})
        print_data("Total Patients", real_data.get("patients", {}).get("total_patients"))
        print_data("Latest Date", real_data.get("patients", {}).get("latest_date"))
        print_data("Total Staff", real_data.get("staff", {}).get("total_staff"))
        print_data("Available Staff", real_data.get("staff", {}).get("available_staff"))
        print_data("Total Inventory Items", real_data.get("inventory", {}).get("total_items"))
        print_data("Critical Items", real_data.get("inventory", {}).get("critical_count"))
        
        print(f"\n{Colors.BOLD}Forecast Data:{Colors.END}")
        forecast = data.get("forecast", {})
        print_data("Forecast Available", bool(forecast))
        if forecast:
            print_data("Forecast Keys", list(forecast.keys()))
    
    # Final Summary
    print_header("TEST SUMMARY")
    total = test_results["total"]
    passed = test_results["passed"]
    failed = test_results["failed"]
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"{Colors.BOLD}Total Tests:{Colors.END} {total}")
    print(f"{Colors.GREEN}{Colors.BOLD}Passed:{Colors.END} {passed}")
    print(f"{Colors.RED}{Colors.BOLD}Failed:{Colors.END} {failed}")
    print(f"{Colors.BOLD}Pass Rate:{Colors.END} {pass_rate:.1f}%\n")
    
    if pass_rate == 100:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED! API is correctly fetching data from media folder.{Colors.END}\n")
    elif pass_rate >= 70:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ MOST TESTS PASSED. Some issues need attention.{Colors.END}\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ MULTIPLE FAILURES. Please check the errors above.{Colors.END}\n")
    
    # Save results to JSON
    results_file = Path(__file__).parent / "test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": pass_rate
            },
            "tests": test_results["tests"]
        }, f, indent=2)
    
    print(f"{Colors.CYAN}Results saved to: {results_file}{Colors.END}\n")

if __name__ == "__main__":
    main()
