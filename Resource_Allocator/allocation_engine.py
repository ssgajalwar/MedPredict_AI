"""
Main Allocation Engine for Agent C: The Logistics Commander

This module orchestrates the complete resource allocation pipeline,
combining inventory management and staffing optimization to generate
structured JSON directives.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
import os

# Add Resource_Allocator directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from resource_mapping import resource_kb, ConditionType
from inventory_manager import InventoryManager
from staffing_optimizer import StaffingOptimizer
from forecast_loader import ForecastLoader
from data_connector import DataConnector


class AllocationEngine:
    """
    Main orchestration engine for resource allocation
    
    Combines forecasts, inventory, and staffing data to generate
    actionable logistics directives.
    """
    
    def __init__(self):
        self.inventory_manager = InventoryManager()
        self.staffing_optimizer = StaffingOptimizer()
        self.forecast_loader = ForecastLoader()
        self.data_connector = DataConnector()
        
        # Results storage
        self.allocation_results = {}
    
    def run_complete_allocation(self, 
                                condition_type: Optional[ConditionType] = None,
                                target_department: str = "Emergency") -> Dict:
        """
        Run complete allocation pipeline
        
        Parameters:
        - condition_type: Type of condition (auto-detected if None)
        - target_department: Department where surge is expected
        
        Returns:
        - Complete allocation results dictionary
        """
        print("=" * 80)
        print(" " * 20 + "AGENT C: THE LOGISTICS COMMANDER")
        print(" " * 15 + "Resource Optimization & Allocation Engine")
        print("=" * 80)
        
        # Step 1: Load forecast data
        print("\n[1/6] Loading forecast data...")
        try:
            self.forecast_loader.load_all_forecasts()
            consensus_forecast, confidence = self.forecast_loader.get_consensus_forecast()
            peak_demand, peak_date = self.forecast_loader.get_peak_demand()
            
            print(f"  [OK] Loaded forecasts from {len(self.forecast_loader.forecasts)} models")
            print(f"  [OK] Peak demand: {peak_demand} patients on {peak_date.date()}")
            print(f"  [OK] Forecast confidence: {confidence:.2%}")
        except Exception as e:
            print(f"  [X] Error loading forecasts: {e}")
            peak_demand = 100  # Fallback
            peak_date = datetime.now() + timedelta(days=7)
            confidence = 0.5
        
        # Step 2: Detect condition type
        print("\n[2/6] Detecting condition type...")
        if condition_type is None:
            # Auto-detect from context (simplified)
            condition_type = ConditionType.GENERAL_SURGE
        
        print(f"  [OK] Condition: {condition_type.value}")
        
        # Step 3: Load current inventory
        print("\n[3/6] Loading current inventory...")
        try:
            inventory_data = self.data_connector.load_inventory_data()
            self.inventory_manager.load_current_inventory(inventory_data)
            print(f"  [OK] Loaded {len(self.inventory_manager.current_inventory)} inventory items")
        except Exception as e:
            print(f"  [X] Error loading inventory: {e}")
        
        # Step 4: Load current staffing
        print("\n[4/6] Loading current staffing...")
        try:
            # Create mock staffing data for now
            staff_data = pd.DataFrame([
                {'role': 'general_physician', 'department_id': target_department, 'available_count': 10, 'on_call_ids': []},
                {'role': 'general_nurse', 'department_id': target_department, 'available_count': 20, 'on_call_ids': []},
                {'role': 'general_nurse', 'department_id': 'OPD', 'available_count': 15, 'on_call_ids': []},
            ])
            self.staffing_optimizer.load_current_roster(staff_data)
            self.staffing_optimizer.set_department_priorities({
                'Emergency': 1, 'ICU': 1, 'Surgery': 2, 'OPD': 4, 'Dermatology': 5
            })
            print(f"  [OK] Loaded staffing data")
        except Exception as e:
            print(f"  [X] Error loading staffing: {e}")
        
        # Step 5: Generate inventory actions
        print("\n[5/6] Generating inventory actions...")
        days_until_surge = (peak_date - datetime.now()).days
        inventory_actions = self.inventory_manager.generate_inventory_actions(
            condition_type=condition_type,
            predicted_patients=peak_demand,
            days_until_surge=max(1, days_until_surge)
        )
        print(f"  [OK] Generated {len(inventory_actions)} inventory actions")
        
        # Step 6: Generate staffing actions
        print("\n[6/6] Generating staffing actions...")
        staffing_actions = self.staffing_optimizer.generate_staffing_actions(
            condition_type=condition_type,
            predicted_patients=peak_demand,
            target_department=target_department
        )
        print(f"  [OK] Generated {len(staffing_actions)} staffing actions")
        
        # Compile results
        self.allocation_results = self._compile_results(
            condition_type=condition_type,
            peak_demand=peak_demand,
            peak_date=peak_date,
            confidence=confidence,
            inventory_actions=inventory_actions,
            staffing_actions=staffing_actions
        )
        
        return self.allocation_results
    
    def _compile_results(self, condition_type, peak_demand, peak_date, confidence,
                        inventory_actions, staffing_actions) -> Dict:
        """Compile all results into structured JSON format"""
        
        # Generate purchase orders
        purchase_orders = self.inventory_manager.generate_purchase_orders_json(inventory_actions)
        
        # Generate staffing directives
        staffing_directives = self.staffing_optimizer.generate_staffing_json(staffing_actions)
        
        # Generate operational advisories
        advisories = []
        if confidence < 0.6:
            advisories.append("Low forecast confidence. Monitor situation closely.")
        
        # Check for critical alerts
        critical_inv = [a for a in inventory_actions if a.urgency_score > 0.8]
        if critical_inv:
            advisories.append(f"CRITICAL: {len(critical_inv)} inventory items require immediate attention.")
        
        critical_staff = [a for a in staffing_actions if a.urgency_score > 0.8]
        if critical_staff:
            advisories.append(f"CRITICAL: {len(critical_staff)} staffing roles have severe shortages.")
        
        # Compile final output
        output = {
            "logistics_action_plan": {
                "generation_timestamp": datetime.now().isoformat(),
                "date": peak_date.date().isoformat(),
                "surge_context": condition_type.value,
                "predicted_patient_count": peak_demand,
                "forecast_confidence": round(confidence, 3),
                
                "inventory_actions": purchase_orders,
                
                "staffing_actions": staffing_directives,
                
                "operational_advisories": advisories,
                
                "summary_statistics": {
                    "inventory": self.inventory_manager.get_summary_statistics(inventory_actions),
                    "staffing": self.staffing_optimizer.get_summary_statistics(staffing_actions)
                }
            }
        }
        
        return output
    
    def save_results(self, output_path: str = './allocation_output.json'):
        """Save allocation results to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(self.allocation_results, f, indent=2)
        
        print(f"\n[OK] Results saved to: {output_path}")
    
    def print_summary(self):
        """Print human-readable summary"""
        if not self.allocation_results:
            print("No results to display")
            return
        
        plan = self.allocation_results['logistics_action_plan']
        
        print("\n" + "=" * 80)
        print(" " * 25 + "ALLOCATION SUMMARY")
        print("=" * 80)
        
        print(f"\nSurge Context: {plan['surge_context']}")
        print(f"Predicted Patients: {plan['predicted_patient_count']}")
        print(f"Forecast Confidence: {plan['forecast_confidence']:.1%}")
        print(f"Target Date: {plan['date']}")
        
        print("\n" + "-" * 80)
        print("INVENTORY ACTIONS")
        print("-" * 80)
        
        inv_stats = plan['summary_statistics']['inventory']
        print(f"Total Items Analyzed: {inv_stats['total_items_analyzed']}")
        print(f"Items Needing Action: {inv_stats['items_needing_action']}")
        print(f"Purchase Orders: {inv_stats['purchase_orders_generated']}")
        print(f"Critical Alerts: {inv_stats['critical_alerts']}")
        print(f"Emergency Loans: {inv_stats['emergency_loans_required']}")
        
        if plan['inventory_actions']:
            print("\nTop Priority Items:")
            for item in plan['inventory_actions'][:5]:
                print(f"  - {item['item_name']}: {item['action']} ({item['priority']})")
        
        print("\n" + "-" * 80)
        print("STAFFING ACTIONS")
        print("-" * 80)
        
        staff_stats = plan['summary_statistics']['staffing']
        print(f"Total Roles Analyzed: {staff_stats['total_roles_analyzed']}")
        print(f"Roles Needing Action: {staff_stats['roles_needing_action']}")
        print(f"Internal Reallocations: {staff_stats['internal_reallocations']}")
        print(f"On-Call Activations: {staff_stats['on_call_activations']}")
        print(f"Agency Requests: {staff_stats['agency_requests']}")
        print(f"Critical Shortages: {staff_stats['critical_shortages']}")
        
        if plan['staffing_actions']:
            print("\nTop Priority Actions:")
            for action in plan['staffing_actions'][:5]:
                print(f"  - {action['role']}: {action['action']} ({action['priority']})")
        
        if plan['operational_advisories']:
            print("\n" + "-" * 80)
            print("OPERATIONAL ADVISORIES")
            print("-" * 80)
            for advisory in plan['operational_advisories']:
                print(f"  [!] {advisory}")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    # Test the allocation engine
    engine = AllocationEngine()
    
    try:
        results = engine.run_complete_allocation(
            condition_type=ConditionType.RESPIRATORY_SURGE,
            target_department="Emergency"
        )
        
        engine.print_summary()
        engine.save_results('./allocation_output.json')
        
        print(f"\n[OK] Allocation engine test completed!")
        
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
