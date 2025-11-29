"""
Departments Router (Model 2)
Department-wise patient distribution endpoints.
"""

from fastapi import APIRouter, HTTPException
from backend.services.model2_service import DepartmentDistributionService

router = APIRouter(prefix="/api/v1/departments", tags=["Departments"])

# Initialize service
dept_service = DepartmentDistributionService()

@router.get("/utilization")
async def get_department_utilization():
    """Get current department utilization"""
    try:
        utilization = dept_service.get_department_utilization()
        return {
            'departments': utilization,
            'total_departments': len(utilization)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
