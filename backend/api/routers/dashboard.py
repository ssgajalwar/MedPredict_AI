"""
Dashboard Router
Provides dashboard overview and aggregated metrics.
"""

from fastapi import APIRouter, HTTPException
from backend.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

# Initialize service
dashboard_service = DashboardService()

@router.get("/overview")
async def get_dashboard_overview():
    """Get comprehensive dashboard overview"""
    try:
        return dashboard_service.get_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
