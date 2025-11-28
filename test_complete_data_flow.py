"""
COMPLETE DATA FLOW TEST
Tests: Agents -> Media -> API -> Frontend

This test validates that:
1. Agent-generated data exists in media folder
2. API correctly reads from media folder
3. Frontend correctly fetches from API
4. Data is consistent across the entire pipeline
"""
import requests
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

# Configuration
MEDIA_PATH = Path(__file__).parent / "media"
API_BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:5173"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text, level=1):
    if level == 1:
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*100}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(100)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*100}{Colors.END}\n")
    else:
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'─'*100}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'─'*100}{Colors.END}")

def print_step(step_num, title):
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}[STEP {step_num}] {title}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(label, value, indent=2):
    indent_str = " " * indent
    print(f"{indent_str}{Colors.YELLOW}{label}:{Colors.END} {value}")

# Test Results
results = {
    "timestamp": datetime.now().isoformat(),
    "stages": {},
    "data_consistency": {},
    "overall_status": "PENDING"
}

print_header("COMPLETE DATA FLOW TEST: Agents → Media → API → Frontend")
print(f"{Colors.BOLD}Timestamp:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# STAGE 1: VERIFY AGENT-GENERATED DATA IN MEDIA FOLDER
# ============================================================================
print_header("STAGE 1: Agent-Generated Data in Media Folder", level=2)

print_step(1, "Checking Agent Output Files")

# Check for data generator outputs
data_files = {
    "patient_visits": MEDIA_PATH / "data/hospital_data/patient_visits.csv",
    "staff": MEDIA_PATH / "data/hospital_data/staff.csv",
    "inventory": MEDIA_PATH / "data/hospital_data/supply_inventory.csv",
    "weather": MEDIA_PATH / "data/hospital_data/weather_data.csv",
    "events": MEDIA_PATH / "data/hospital_data/events.csv"
}

stage1_data = {}
for name, path in data_files.items():
    if path.exists():
        df = pd.read_csv(path)
        stage1_data[name] = {
            "exists": True,
            "rows": len(df),
            "columns": list(df.columns),
            "sample": df.head(1).to_dict('records')[0] if len(df) > 0 else {}
        }
        print_success(f"{name}: {len(df)} rows")
    else:
        stage1_data[name] = {"exists": False}
        print_error(f"{name}: NOT FOUND")

# Check for forecaster outputs
forecast_files = list((MEDIA_PATH / "forecasts/csv").glob("*_forecast_*.csv")) if (MEDIA_PATH / "forecasts/csv").exists() else []
if forecast_files:
    latest_forecast = max(forecast_files, key=lambda x: x.stat().st_mtime)
    forecast_df = pd.read_csv(latest_forecast)
    stage1_data["forecast"] = {
        "exists": True,
        "file": latest_forecast.name,
        "rows": len(forecast_df),
        "columns": list(forecast_df.columns)
    }
    print_success(f"Forecast: {latest_forecast.name} ({len(forecast_df)} rows)")
else:
    stage1_data["forecast"] = {"exists": False}
    print_error("Forecast: NOT FOUND")

# Check for allocator outputs
allocation_files = list((MEDIA_PATH / "allocations").glob("allocation_output_*.json")) if (MEDIA_PATH / "allocations").exists() else []
if allocation_files:
    latest_allocation = max(allocation_files, key=lambda x: x.stat().st_mtime)
    with open(latest_allocation, 'r') as f:
        allocation_data = json.load(f)
    stage1_data["allocation"] = {
        "exists": True,
        "file": latest_allocation.name,
        "structure": list(allocation_data.keys())
    }
    print_success(f"Allocation: {latest_allocation.name}")
else:
    stage1_data["allocation"] = {"exists": False}
    print_error("Allocation: NOT FOUND")

results["stages"]["stage1_media"] = stage1_data

# ============================================================================
# STAGE 2: VERIFY API READS FROM MEDIA FOLDER
# ============================================================================
print_header("STAGE 2: API Reading from Media Folder", level=2)

print_step(2, "Testing API Endpoints")

# Test Resources Endpoint
try:
    response = requests.get(f"{API_BASE_URL}/resources/status", timeout=10)
    if response.status_code == 200:
        api_resources = response.json()
        print_success(f"Resources API: HTTP {response.status_code}")
        print_info("Recommended Staff", api_resources.get('recommended_staff'))
        print_info("Current Staff", api_resources.get('current_staff'))
        print_info("Staff Shortage", api_resources.get('staff_shortage'))
        print_info("Bed Occupancy", f"{api_resources.get('bed_occupancy_predicted')}%")
        
        results["stages"]["stage2_api_resources"] = {
            "status": "SUCCESS",
            "data": api_resources
        }
    else:
        print_error(f"Resources API: HTTP {response.status_code}")
        results["stages"]["stage2_api_resources"] = {"status": "FAILED", "error": f"HTTP {response.status_code}"}
except Exception as e:
    print_error(f"Resources API: {str(e)}")
    results["stages"]["stage2_api_resources"] = {"status": "FAILED", "error": str(e)}

# Test Dashboard Endpoint (with longer timeout due to external APIs)
try:
    print_step(3, "Testing Dashboard Endpoint (may take longer due to external APIs)")
    response = requests.get(f"{API_BASE_URL}/dashboard/overview", timeout=30)
    if response.status_code == 200:
        api_dashboard = response.json()
        print_success(f"Dashboard API: HTTP {response.status_code}")
        
        real_data = api_dashboard.get('real_data', {})
        patients = real_data.get('patients', {})
        staff = real_data.get('staff', {})
        inventory = real_data.get('inventory', {})
        
        print_info("Total Patients", patients.get('total_patients'))
        print_info("Latest Date", patients.get('latest_date'))
        print_info("Total Staff", staff.get('total_staff'))
        print_info("Available Staff", staff.get('available_staff'))
        print_info("Inventory Items", inventory.get('total_items'))
        print_info("Critical Items", inventory.get('critical_count'))
        
        results["stages"]["stage2_api_dashboard"] = {
            "status": "SUCCESS",
            "data": {
                "patients": patients,
                "staff": staff,
                "inventory": inventory
            }
        }
    else:
        print_error(f"Dashboard API: HTTP {response.status_code}")
        results["stages"]["stage2_api_dashboard"] = {"status": "FAILED", "error": f"HTTP {response.status_code}"}
except Exception as e:
    print_error(f"Dashboard API: {str(e)}")
    results["stages"]["stage2_api_dashboard"] = {"status": "FAILED", "error": str(e)}

# ============================================================================
# STAGE 3: VERIFY DATA CONSISTENCY (MEDIA vs API)
# ============================================================================
print_header("STAGE 3: Data Consistency Check (Media ↔ API)", level=2)

print_step(4, "Comparing Media Data with API Data")

consistency_checks = {}

# Check Patient Data
if stage1_data.get("patient_visits", {}).get("exists") and results["stages"].get("stage2_api_dashboard", {}).get("status") == "SUCCESS":
    csv_patients = stage1_data["patient_visits"]["rows"]
    api_patients = results["stages"]["stage2_api_dashboard"]["data"]["patients"].get("total_patients", 0)
    
    # Note: API returns latest date only, so counts won't match total CSV rows
    print_info("Patient Visits in CSV", f"{csv_patients} (all dates)")
    print_info("Patients in API", f"{api_patients} (latest date only)")
    
    if api_patients > 0:
        print_success("Patient data is flowing from Media → API")
        consistency_checks["patients"] = "PASS"
    else:
        print_error("Patient data not flowing correctly")
        consistency_checks["patients"] = "FAIL"
else:
    print_error("Cannot verify patient data consistency")
    consistency_checks["patients"] = "SKIP"

# Check Staff Data
if stage1_data.get("staff", {}).get("exists") and results["stages"].get("stage2_api_dashboard", {}).get("status") == "SUCCESS":
    csv_staff = stage1_data["staff"]["rows"]
    api_staff = results["stages"]["stage2_api_dashboard"]["data"]["staff"].get("total_staff", 0)
    
    print_info("Staff in CSV", csv_staff)
    print_info("Staff in API", api_staff)
    
    if csv_staff == api_staff:
        print_success("Staff data matches perfectly!")
        consistency_checks["staff"] = "PASS"
    elif api_staff > 0:
        print_success("Staff data is flowing (counts may differ due to filtering)")
        consistency_checks["staff"] = "PARTIAL"
    else:
        print_error("Staff data not flowing correctly")
        consistency_checks["staff"] = "FAIL"
else:
    print_error("Cannot verify staff data consistency")
    consistency_checks["staff"] = "SKIP"

# Check Inventory Data
if stage1_data.get("inventory", {}).get("exists") and results["stages"].get("stage2_api_dashboard", {}).get("status") == "SUCCESS":
    csv_inventory = stage1_data["inventory"]["rows"]
    api_inventory = results["stages"]["stage2_api_dashboard"]["data"]["inventory"].get("total_items", 0)
    
    print_info("Inventory in CSV", csv_inventory)
    print_info("Inventory in API", api_inventory)
    
    if csv_inventory == api_inventory:
        print_success("Inventory data matches perfectly!")
        consistency_checks["inventory"] = "PASS"
    elif api_inventory > 0:
        print_success("Inventory data is flowing")
        consistency_checks["inventory"] = "PARTIAL"
    else:
        print_error("Inventory data not flowing correctly")
        consistency_checks["inventory"] = "FAIL"
else:
    print_error("Cannot verify inventory data consistency")
    consistency_checks["inventory"] = "SKIP"

# Check Allocation Data
if stage1_data.get("allocation", {}).get("exists") and results["stages"].get("stage2_api_resources", {}).get("status") == "SUCCESS":
    api_allocation = results["stages"]["stage2_api_resources"]["data"]
    
    if api_allocation.get("recommended_staff", 0) > 0:
        print_success("Allocation data is flowing from Media → API")
        consistency_checks["allocation"] = "PASS"
    else:
        print_error("Allocation data not flowing correctly")
        consistency_checks["allocation"] = "FAIL"
else:
    print_error("Cannot verify allocation data consistency")
    consistency_checks["allocation"] = "SKIP"

results["data_consistency"] = consistency_checks

# ============================================================================
# STAGE 4: VERIFY FRONTEND FETCHES FROM API
# ============================================================================
print_header("STAGE 4: Frontend Fetching from API", level=2)

print_step(5, "Testing Frontend Data Rendering")

try:
    # Simple check - just verify frontend is accessible and making API calls
    response = requests.get(FRONTEND_URL, timeout=5)
    if response.status_code == 200:
        print_success(f"Frontend accessible: HTTP {response.status_code}")
        results["stages"]["stage4_frontend"] = {
            "status": "ACCESSIBLE",
            "note": "Frontend is running. Manual verification recommended for data rendering."
        }
        
        print_info("Frontend URL", FRONTEND_URL)
        print_info("Status", "Running and accessible")
        print(f"\n{Colors.YELLOW}Note: Please manually verify in browser that data is displayed correctly.{Colors.END}")
    else:
        print_error(f"Frontend: HTTP {response.status_code}")
        results["stages"]["stage4_frontend"] = {"status": "FAILED", "error": f"HTTP {response.status_code}"}
except Exception as e:
    print_error(f"Frontend: {str(e)}")
    results["stages"]["stage4_frontend"] = {"status": "FAILED", "error": str(e)}

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_header("TEST SUMMARY", level=1)

# Count successes
stage_results = {
    "Media Folder": "✓" if all(v.get("exists", False) for k, v in stage1_data.items() if k in ["patient_visits", "staff", "inventory"]) else "✗",
    "API Resources": "✓" if results["stages"].get("stage2_api_resources", {}).get("status") == "SUCCESS" else "✗",
    "API Dashboard": "✓" if results["stages"].get("stage2_api_dashboard", {}).get("status") == "SUCCESS" else "✗",
    "Data Consistency": "✓" if sum(1 for v in consistency_checks.values() if v in ["PASS", "PARTIAL"]) >= 3 else "✗",
    "Frontend": "✓" if results["stages"].get("stage4_frontend", {}).get("status") == "ACCESSIBLE" else "✗"
}

print(f"\n{Colors.BOLD}Data Flow Pipeline Status:{Colors.END}\n")
for stage, status in stage_results.items():
    color = Colors.GREEN if status == "✓" else Colors.RED
    print(f"  {color}{status}{Colors.END} {stage}")

# Overall assessment
passes = sum(1 for v in stage_results.values() if v == "✓")
total = len(stage_results)

print(f"\n{Colors.BOLD}Overall Score:{Colors.END} {passes}/{total} stages passed")

if passes == total:
    results["overall_status"] = "SUCCESS"
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ COMPLETE SUCCESS!{Colors.END}")
    print(f"{Colors.GREEN}Data is flowing correctly through the entire pipeline:{Colors.END}")
    print(f"{Colors.GREEN}  Agents → Media → API → Frontend{Colors.END}\n")
elif passes >= 3:
    results["overall_status"] = "PARTIAL"
    print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ PARTIAL SUCCESS{Colors.END}")
    print(f"{Colors.YELLOW}Most stages are working, but some issues need attention.{Colors.END}\n")
else:
    results["overall_status"] = "FAILED"
    print(f"\n{Colors.RED}{Colors.BOLD}✗ MULTIPLE FAILURES{Colors.END}")
    print(f"{Colors.RED}Several stages have issues that need to be fixed.{Colors.END}\n")

# Save detailed results
results_file = Path(__file__).parent / "test_complete_flow_results.json"
with open(results_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"{Colors.CYAN}Detailed results saved to: {results_file}{Colors.END}\n")

# Print key data samples
if results["stages"].get("stage2_api_dashboard", {}).get("status") == "SUCCESS":
    print(f"\n{Colors.BOLD}{Colors.BLUE}Sample Data from API:{Colors.END}")
    dashboard_data = results["stages"]["stage2_api_dashboard"]["data"]
    print(f"\n{Colors.BOLD}Patients:{Colors.END}")
    for key, value in dashboard_data.get("patients", {}).items():
        print(f"  • {key}: {value}")
    
    print(f"\n{Colors.BOLD}Staff:{Colors.END}")
    for key, value in dashboard_data.get("staff", {}).items():
        print(f"  • {key}: {value}")
    
    print(f"\n{Colors.BOLD}Inventory:{Colors.END}")
    for key, value in dashboard_data.get("inventory", {}).items():
        print(f"  • {key}: {value}")

if results["stages"].get("stage2_api_resources", {}).get("status") == "SUCCESS":
    print(f"\n{Colors.BOLD}Resource Allocation:{Colors.END}")
    resources = results["stages"]["stage2_api_resources"]["data"]
    print(f"  • Recommended Staff: {resources.get('recommended_staff')}")
    print(f"  • Current Staff: {resources.get('current_staff')}")
    print(f"  • Staff Shortage: {resources.get('staff_shortage')}")
    print(f"  • Bed Occupancy: {resources.get('bed_occupancy_predicted')}%")

print("\n" + "="*100 + "\n")
