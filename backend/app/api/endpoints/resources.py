from fastapi import APIRouter
from ...services.allocation_service import allocation_service
from ...services.data_service import data_service

router = APIRouter()

@router.get("/status")
async def get_resource_status():
    """Get resource allocation status from media folder"""
    # Get real allocation data
    allocation_data = allocation_service.get_latest_allocation()
    inventory_data = data_service.get_inventory_data()
    staff_data = data_service.get_staff_data()
    
    return {
        "recommended_staff": allocation_data.get('total_staff_needed', 150),
        "current_staff": allocation_data.get('current_staff', staff_data.get('available_staff', 135)),
        "staff_shortage": allocation_data.get('staff_shortage', 15),
        "bed_occupancy_predicted": allocation_data.get('bed_occupancy_predicted', 85.0),
        "inventory_alert": inventory_data['critical_items'][0] if inventory_data['critical_items'] else "Normal",
        "inventory_critical_count": inventory_data['critical_count'],
        "department_allocations": allocation_data.get('department_allocations', {})
    }

