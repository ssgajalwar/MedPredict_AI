from fastapi import APIRouter
from ...services.data_service import data_service

router = APIRouter()

@router.get("/status")
async def get_inventory_status():
    """Get current inventory status and critical items"""
    
    inventory_data = data_service.get_inventory_data()
    
    # Enrich with some mock categories if not present
    items = inventory_data.get('items', [])
    
    # Categorize items for better frontend display
    categorized_items = {
        "Medicines": [],
        "Equipment": [],
        "Consumables": [],
        "PPE": []
    }
    
    for item in items:
        # Simple keyword based categorization
        name = item.get('name', '').lower()
        if any(x in name for x in ['mask', 'glove', 'gown', 'ppe']):
            categorized_items["PPE"].append(item)
        elif any(x in name for x in ['ventilator', 'monitor', 'bed', 'pump']):
            categorized_items["Equipment"].append(item)
        elif any(x in name for x in ['syringe', 'bandage', 'cotton']):
            categorized_items["Consumables"].append(item)
        else:
            categorized_items["Medicines"].append(item)
            
    return {
        "summary": {
            "total_items": len(items),
            "critical_items": len(inventory_data.get('critical_items', [])),
            "value_at_risk": "High" if len(inventory_data.get('critical_items', [])) > 5 else "Low"
        },
        "critical_list": inventory_data.get('critical_items', []),
        "categories": categorized_items,
        "all_items": items
    }

@router.get("/forecast")
async def get_inventory_forecast():
    """Get inventory usage forecast based on patient predictions"""
    
    # This would ideally use the forecast service to predict consumption
    # For now returning mock forecast based on current trends
    
    return {
        "predicted_shortages": [
            {"item": "N95 Masks", "days_left": 3, "predicted_depletion": "2024-11-05"},
            {"item": "Oxygen Cylinders", "days_left": 5, "predicted_depletion": "2024-11-07"}
        ],
        "recommended_orders": [
            {"item": "N95 Masks", "quantity": 5000, "priority": "High"},
            {"item": "Oxygen Cylinders", "quantity": 50, "priority": "High"},
            {"item": "Paracetamol IV", "quantity": 200, "priority": "Medium"}
        ]
    }
