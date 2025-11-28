import json
from pathlib import Path
from typing import Dict

class AllocationService:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent.parent / "media"
        self.allocation_path = self.base_path / "allocations"
        
    def get_latest_allocation(self) -> Dict:
        """Fetch latest resource allocation data"""
        try:
            # Find the most recent allocation file
            allocation_files = list(self.allocation_path.glob("allocation_output_*.json"))
            
            if allocation_files:
                latest_file = max(allocation_files, key=lambda x: x.stat().st_mtime)
                
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                
                # Parse the logistics_action_plan structure
                plan = data.get("logistics_action_plan", {})
                staffing_actions = plan.get("staffing_actions", [])
                summary_stats = plan.get("summary_statistics", {})
                
                # Calculate total staff needed and current
                total_required = sum(action.get("required_count", 0) for action in staffing_actions)
                total_current = sum(action.get("current_roster_count", 0) for action in staffing_actions)
                
                # Extract key metrics
                return {
                    "timestamp": plan.get("generation_timestamp", ""),
                    "date": plan.get("date", ""),
                    "total_staff_needed": total_required,
                    "current_staff": total_current,
                    "staff_shortage": max(0, total_required - total_current),
                    "predicted_bed_occupancy": 75.0,  # Not in current data
                    "predicted_patient_count": plan.get("predicted_patient_count", 0),
                    "surge_context": plan.get("surge_context", ""),
                    "inventory_alerts": [action for action in plan.get("inventory_actions", [])],
                    "staffing_actions": staffing_actions,
                    "department_allocations": self._parse_department_allocations(staffing_actions),
                    "summary_statistics": summary_stats
                }
            else:
                return self._generate_mock_allocation()
                
        except Exception as e:
            print(f"Error loading allocation data: {e}")
            return self._generate_mock_allocation()
    
    def _parse_department_allocations(self, staffing_actions):
        """Parse department allocations from staffing actions"""
        dept_alloc = {}
        for action in staffing_actions:
            dept = action.get("target_dept", "Unknown")
            if dept not in dept_alloc:
                dept_alloc[dept] = {"staff_needed": 0, "roles": []}
            dept_alloc[dept]["staff_needed"] += action.get("required_count", 0)
            dept_alloc[dept]["roles"].append({
                "role": action.get("role"),
                "count": action.get("required_count"),
                "action": action.get("action")
            })
        return dept_alloc

    
    def _generate_mock_allocation(self) -> Dict:
        """Generate mock allocation if no data available"""
        return {
            "timestamp": "2024-11-22",
            "total_staff_needed": 150,
            "current_staff": 135,
            "staff_shortage": 15,
            "bed_occupancy_predicted": 85.0,
            "inventory_alerts": ["Oxygen Cylinders"],
            "department_allocations": {
                "Emergency": {"staff": 30, "beds": 20},
                "ICU": {"staff": 25, "beds": 15},
                "General": {"staff": 40, "beds": 50}
            }
        }

allocation_service = AllocationService()
