"""
Unified FastAPI Application
Main application that includes all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers import dashboard, analytics, forecast, departments

# Create FastAPI app
app = FastAPI(
    title="MedPredict AI API",
    description="Hospital Patient Volume Forecasting and Analytics API",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router)
app.include_router(analytics.router)
app.include_router(forecast.router)
app.include_router(departments.router)

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "MedPredict AI API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "dashboard": "/api/v1/dashboard/overview",
            "analytics": "/api/v1/analytics/*",
            "forecast": "/api/v1/forecast/*",
            "departments": "/api/v1/departments/*"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
