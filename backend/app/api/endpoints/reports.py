from fastapi import APIRouter
from ...services.data_service import data_service
from ...services.forecast_service import forecast_service
from ...services.allocation_service import allocation_service
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/list")
async def get_reports_list():
    """Get list of available generated reports"""
    
    # In a real app, this would scan a reports directory
    # For now, we return dynamic report metadata
    
    return {
        "daily_reports": [
            {"id": "daily_20241101", "title": "Daily Operations Summary", "date": "2024-11-01", "status": "Ready"},
            {"id": "daily_20241031", "title": "Daily Operations Summary", "date": "2024-10-31", "status": "Ready"},
        ],
        "monthly_reports": [
            {"id": "monthly_oct2024", "title": "October Performance Review", "date": "2024-10-01", "status": "Ready"}
        ],
        "incident_reports": [
            {"id": "inc_001", "title": "Oxygen Supply Critical Low", "date": "2024-10-25", "severity": "High"}
        ]
    }

@router.get("/generate/daily")
async def generate_daily_report():
    """Generate a fresh daily report based on current data"""
    
    patient_data = data_service.get_latest_patient_data()
    allocation_data = allocation_service.get_latest_allocation()
    forecast_data = forecast_service.get_latest_forecast()
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "period": "Daily",
        "summary": {
            "total_patients": patient_data.get('total_patients', 0),
            "admissions": patient_data.get('admissions', 0),
            "discharges": patient_data.get('discharges', 0),
            "occupancy_rate": f"{allocation_data.get('bed_occupancy_predicted', 0)}%"
        },
        "resource_status": {
            "staff_shortage": allocation_data.get('staff_shortage', 0),
            "critical_inventory_count": 0 # Placeholder
        },
        "forecast_highlight": f"Expected {forecast_data.get('forecasts', [{}])[0].get('predicted_patients', 0)} patients tomorrow"
    }
    
    return report
