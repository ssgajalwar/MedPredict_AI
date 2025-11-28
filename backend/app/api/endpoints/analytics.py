from fastapi import APIRouter
from ...services.data_service import data_service
from ...services.forecast_service import forecast_service
from ...services.weather_service import weather_service
from ...services.news_service import news_service
from ...services.calendar_service import calendar_service
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/surge-patterns")
async def get_surge_patterns():
    """Get surge patterns analysis based on festivals, pollution, and epidemics"""
    
    # Get historical data
    patient_data = data_service.get_latest_patient_data()
    forecast_data = forecast_service.get_latest_forecast()
    weather = await weather_service.get_aqi()
    events = await calendar_service.get_upcoming_events()
    news = await news_service.get_health_news()
    
    # Analyze surge causes
    surge_causes = {
        "festivals": [],
        "pollution": {
            "current_aqi": weather.get("aqi", 0),
            "impact_level": "High" if weather.get("aqi", 0) > 300 else "Medium" if weather.get("aqi", 0) > 150 else "Low"
        },
        "epidemics": [],
        "seasonal": "Winter" if datetime.now().month in [11, 12, 1, 2] else "Summer"
    }
    
    # Extract festival info from events
    for event in events[:5]:
        surge_causes["festivals"].append({
            "name": event.get("summary", "Unknown Event"),
            "date": event.get("date", ""),
            "expected_surge": event.get("surge_factor", 1.2)
        })
    
    # Extract epidemic info from news
    epidemic_keywords = ["flu", "dengue", "malaria", "covid", "respiratory", "infection"]
    for article in news[:10]:
        title_lower = article.get("title", "").lower()
        if any(keyword in title_lower for keyword in epidemic_keywords):
            surge_causes["epidemics"].append({
                "type": next((kw for kw in epidemic_keywords if kw in title_lower), "general"),
                "source": article.get("source", {}).get("name", "Unknown"),
                "published": article.get("publishedAt", "")
            })
    
    return {
        "surge_causes": surge_causes,
        "current_trend": "upward" if patient_data.get("total_patients", 0) > 500 else "stable",
        "forecast_summary": {
            "next_3_days": forecast_data.get("forecasts", [])[:3],
            "peak_expected": forecast_data.get("peak_date", "Not determined")
        }
    }

@router.get("/department-trends")
async def get_department_trends():
    """Get department-wise patient trends and resource utilization"""
    
    patient_data = data_service.get_latest_patient_data()
    
    # Department wise breakdown
    departments = patient_data.get("by_department", {})
    
    department_analysis = []
    department_names = {
        "1": "Emergency",
        "2": "Cardiology", 
        "3": "Pediatrics",
        "4": "Orthopedics",
        "5": "General Medicine"
    }
    
    for dept_id, count in departments.items():
        dept_name = department_names.get(str(dept_id), f"Department {dept_id}")
        department_analysis.append({
            "id": dept_id,
            "name": dept_name,
            "current_patients": count,
            "capacity": count + int(count * 0.3),  # Assume 30% buffer
            "utilization": min(100, int((count / (count + count * 0.3)) * 100)),
            "trend": "increasing" if count > 50 else "stable"
        })
    
    return {
        "departments": sorted(department_analysis, key=lambda x: x["current_patients"], reverse=True),
        "total_departments": len(department_analysis),
        "highest_utilization": max([d["utilization"] for d in department_analysis]) if department_analysis else 0
    }

@router.get("/admission-predictions")
async def get_admission_predictions():
    """Get predicted admissions for next 7 days"""
    
    forecast_data = forecast_service.get_latest_forecast()
    weather = await weather_service.get_aqi()
    
    predictions = []
    forecasts = forecast_data.get("forecasts", [])[:7]
    
    for i, forecast in enumerate(forecasts):
        # Adjust predictions based on AQI
        aqi_factor = 1.0
        if weather.get("aqi", 0) > 300:
            aqi_factor = 1.15
        elif weather.get("aqi", 0) > 200:
            aqi_factor = 1.1
        
        predicted_patients = int(forecast.get("predicted_patients", 0) * aqi_factor)
        
        predictions.append({
            "date": forecast.get("date", f"Day +{i+1}"),
            "predicted_admissions": predicted_patients,
            "confidence_interval": {
                "lower": forecast.get("lower_bound", predicted_patients - 50),
                "upper": forecast.get("upper_bound", predicted_patients + 50)
            },
            "department_breakdown": {
                "emergency": int(predicted_patients * 0.35),
                "cardiology": int(predicted_patients * 0.20),
                "pediatrics": int(predicted_patients * 0.15),
                "orthopedics": int(predicted_patients * 0.15),
                "general": int(predicted_patients * 0.15)
            }
        })
    
    return {
        "predictions": predictions,
        "total_predicted_week": sum([p["predicted_admissions"] for p in predictions]),
        "peak_day": max(predictions, key=lambda x: x["predicted_admissions"]) if predictions else None
    }

@router.get("/environmental-impact")
async def get_environmental_impact():
    """Get environmental factors impact on patient surge"""
    
    weather = await weather_service.get_aqi()
    patient_data = data_service.get_latest_patient_data()
    
    aqi = weather.get("aqi", 0)
    
    # Calculate respiratory cases correlation
    respiratory_impact = {
        "aqi_level": aqi,
        "category": "Severe" if aqi > 300 else "Very Unhealthy" if aqi > 200 else "Unhealthy" if aqi > 150 else "Moderate",
        "estimated_respiratory_cases": int((aqi / 50) * 10) if aqi > 150 else 5,
        "cardiovascular_cases": int((aqi / 100) * 8) if aqi > 200 else 3,
        "pediatric_cases": int((aqi / 60) * 12) if aqi > 150 else 4
    }
    
    seasonal_factors = {
        "season": "Winter" if datetime.now().month in [11, 12, 1, 2] else "Monsoon" if datetime.now().month in [6, 7, 8, 9] else "Summer",
        "typical_diseases": ["Respiratory infections", "Asthma", "COPD"] if datetime.now().month in [11, 12, 1, 2] else ["Dengue", "Malaria", "Gastroenteritis"] if datetime.now().month in [6, 7, 8, 9] else ["Heat stroke", "Dehydration"],
        "impact_multiplier": 1.3 if datetime.now().month in [11, 12, 1, 2] else 1.2
    }
    
    return {
        "air_quality": respiratory_impact,
        "seasonal_factors": seasonal_factors,
        "weather_conditions": {
            "temperature": weather.get("temperature", 25),
            "humidity": weather.get("humidity", 60),
            "description": weather.get("description", "Clear")
        },
        "health_advisory": "High risk due to pollution" if aqi > 200 else "Moderate risk" if aqi > 100 else "Low risk"
    }
