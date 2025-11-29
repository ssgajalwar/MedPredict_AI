"""
Analytics Router
Provides analytics endpoints for surge patterns, environmental impact, etc.
"""

from fastapi import APIRouter, HTTPException, Query
from backend.services.dashboard_service import DashboardService
from backend.services.model2_service import DepartmentDistributionService

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

# Initialize services
dashboard_service = DashboardService()
dept_service = DepartmentDistributionService()

@router.get("/surge-patterns")
async def get_surge_patterns():
    """Get surge pattern analysis including festivals and epidemics"""
    try:
        return dashboard_service.get_surge_patterns()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/department-trends")
async def get_department_trends():
    """Get department utilization trends"""
    try:
        utilization = dept_service.get_department_utilization()
        return {
            'departments': utilization,
            'timestamp': None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admission-predictions")
async def get_admission_predictions(days: int = Query(7, ge=1, le=30)):
    """Get admission predictions for next N days"""
    try:
        return dashboard_service.get_admission_predictions(days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/environmental-impact")
async def get_environmental_impact():
    """Get environmental impact data (AQI, weather, health advisory)"""
    try:
        return dashboard_service.get_environmental_impact()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
