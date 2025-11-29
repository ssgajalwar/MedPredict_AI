"""
Patient Volume Forecasting API
FastAPI endpoint for patient volume predictions
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import service
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Forecaster.forecast_service import PatientVolumeForecastingService

# Initialize FastAPI app
app = FastAPI(
    title="Patient Volume Forecasting API",
    description="API for predicting daily patient volumes at Lilavati Hospital",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize forecasting service globally
forecast_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize the forecasting service on startup"""
    global forecast_service
    try:
        forecast_service = PatientVolumeForecastingService()
        print("✓ Forecasting service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize forecasting service: {e}")
        raise


# Response Models
class PredictionResponse(BaseModel):
    date: str
    predicted_patient_volume: int
    day_of_week: int
    is_weekend: bool
    is_holiday: bool
    is_monsoon: bool

class SummaryStatistics(BaseModel):
    total_days: int
    avg_daily_patients: float
    max_daily_patients: int
    min_daily_patients: int
    total_predicted_patients: int
    date_range: Dict[str, str]

class ForecastResult(BaseModel):
    predictions: List[PredictionResponse]
    summary: SummaryStatistics


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "api": "Patient Volume Forecasting API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "/predict": "Get patient volume predictions",
            "/predict/summary": "Get predictions with summary statistics",
            "/health": "Health check endpoint",
            "/docs": "API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if forecast_service is None:
        raise HTTPException(status_code=503, detail="Forecasting service not initialized")
    
    return {
        "status": "healthy",
        "model_loaded": forecast_service.model is not None,
        "data_loaded": forecast_service.historical_data is not None
    }

@app.get("/predict", response_model=List[PredictionResponse])
async def predict_patient_volume(
    start_date: Optional[str] = Query(
        None,
        description="Start date for predictions (YYYY-MM-DD). Default: tomorrow",
        example="2025-11-29"
    ),
    end_date: Optional[str] = Query(
        None,
        description="End date for predictions (YYYY-MM-DD). Default: 1 year ahead",
        example="2026-11-28"
    ),
    days: Optional[int] = Query(
        None,
        description="Number of days to predict (alternative to end_date)",
        ge=1,
        le=365
    )
):
    """
    Predict daily patient volumes for a given date range
    
    Parameters:
    - start_date: Start date (YYYY-MM-DD). If not provided, starts tomorrow
    - end_date: End date (YYYY-MM-DD). If not provided, predicts 1 year ahead
    - days: Alternative to end_date - number of days to predict
    
    Returns:
    - List of predictions with date and patient volume
    """
    if forecast_service is None:
        raise HTTPException(status_code=503, detail="Forecasting service not initialized")
    
    try:
        # Handle 'days' parameter
        if days is not None:
            if start_date is None:
                start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=days-1)).strftime('%Y-%m-%d')
        
        # Validate dates if provided
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Make predictions
        predictions = forecast_service.predict(start_date, end_date)
        
        return predictions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/predict/summary", response_model=ForecastResult)
async def predict_with_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days: Optional[int] = Query(30, description="Number of days to predict", ge=1, le=365)
):
    """
    Predict patient volumes with summary statistics
    
    Returns predictions along with summary statistics like averages, totals, etc.
    """
    if forecast_service is None:
        raise HTTPException(status_code=503, detail="Forecasting service not initialized")
    
    try:
        # Handle 'days' parameter
        if days is not None:
            if start_date is None:
                start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=days-1)).strftime('%Y-%m-%d')
        
        # Make predictions
        predictions = forecast_service.predict(start_date, end_date)
        
        # Get summary statistics
        summary = forecast_service.get_summary_statistics(predictions)
        
        return {
            "predictions": predictions,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/predict/quick")
async def quick_forecast(
    days: int = Query(7, description="Number of days to predict (1-30)", ge=1, le=30)
):
    """
    Quick forecast for next N days (default: 7 days)
    
    Simplified endpoint for quick predictions
    """
    if forecast_service is None:
        raise HTTPException(status_code=503, detail="Forecasting service not initialized")
    
    try:
        start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        predictions = forecast_service.predict(start_date, end_date)
        summary = forecast_service.get_summary_statistics(predictions)
        
        return {
            "forecast_period": f"Next {days} days",
            "start_date": start_date,
            "end_date": end_date,
            "avg_daily_patients": summary['avg_daily_patients'],
            "total_predicted_patients": summary['total_predicted_patients'],
            "predictions": predictions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# Run instructions
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
