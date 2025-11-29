"""
Forecast Router (Model 1)
Patient volume forecasting endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from backend.services.model1_service import PatientVolumeService
from typing import Optional

router = APIRouter(prefix="/api/v1/forecast", tags=["Forecast"])

# Initialize service
volume_service = PatientVolumeService()

@router.get("/predict")
async def predict_patient_volume(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Predict patient volume for a date range"""
    try:
        predictions = volume_service.predict(start_date=start_date, end_date=end_date)
        return {
            'predictions': predictions,
            'count': len(predictions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quick")
async def quick_forecast(days: int = Query(7, ge=1, le=30)):
    """Get quick forecast for next N days"""
    try:
        predictions = volume_service.get_quick_forecast(days=days)
        return {
            'predictions': predictions,
            'period_days': days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
