from fastapi import APIRouter
from ...services.data_service import data_service
from ...services.forecast_service import forecast_service
from ...services.allocation_service import allocation_service
from ...services.weather_service import weather_service
from ...services.news_service import news_service
from ...services.calendar_service import calendar_service
from ...core.agent_logic import agent_logic

router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview():
    """
    Get comprehensive dashboard overview combining real data from media folder
    with external API data (weather, news, events)
    """
    # 1. Fetch real data from media folder
    patient_data = data_service.get_latest_patient_data()
    staff_data = data_service.get_staff_data()
    inventory_data = data_service.get_inventory_data()
    forecast_data = forecast_service.get_latest_forecast()
    allocation_data = allocation_service.get_latest_allocation()
    
    # 2. Fetch external sensory data
    weather = await weather_service.get_aqi()
    news = await news_service.get_health_news()
    events = await calendar_service.get_upcoming_events()
    
    # If no events from CSV, use calendar service
    if not events:
        events = data_service.get_events_data()
    
    # 3. Process via Agent Logic
    analysis = agent_logic.calculate_surge_prediction(weather, news, events)
    
    # 4. Enhance with real data
    # Override with actual patient count if available
    if patient_data.get('total_patients', 0) > 0:
        base_patients = patient_data['total_patients']
        surge_factor = 1 + (analysis['prediction']['surge_percentage'] / 100)
        analysis['prediction']['total_patients'] = int(base_patients * surge_factor)
        analysis['prediction']['current_patients'] = base_patients
    
    # Use real allocation data
    analysis['resources'] = {
        "recommended_staff": allocation_data.get('total_staff_needed', analysis['resources']['recommended_staff']),
        "current_staff": allocation_data.get('current_staff', analysis['resources']['current_staff']),
        "staff_shortage": allocation_data.get('staff_shortage', analysis['resources']['staff_shortage']),
        "bed_occupancy_predicted": allocation_data.get('bed_occupancy_predicted', analysis['resources']['bed_occupancy_predicted']),
        "inventory_alert": inventory_data['critical_items'][0] if inventory_data['critical_items'] else "Normal"
    }
    
    return {
        "sensory_data": {
            "weather": weather,
            "active_events": events,
            "latest_news": news[:3]
        },
        "real_data": {
            "patients": patient_data,
            "staff": staff_data,
            "inventory": inventory_data,
            "latest_date": patient_data.get('latest_date')
        },
        "forecast": forecast_data,
        "analysis": analysis
    }

@router.get("/history")
async def get_patient_history(days: int = 30):
    """Get historical patient data"""
    return {
        "history": forecast_service.get_historical_data(days)
    }

