"""
Main Runner for Agent C: The Logistics Commander

Run complete resource allocation pipeline and generate logistics directives.
"""

import argparse
from datetime import datetime
from allocation_engine import AllocationEngine
from resource_mapping import ConditionType


def run_allocator(condition: str = "auto", department: str = "Emergency", output: str = None):
    """
    Run complete allocation pipeline
    
    Parameters:
    - condition: Condition type (auto, respiratory, burn, dengue, general)
    - department: Target department
    - output: Output JSON file path
    """
    # Map condition string to enum
    condition_map = {
        "auto": None,
        "respiratory": ConditionType.RESPIRATORY_SURGE,
        "burn": ConditionType.BURN_TRAUMA,
        "dengue": ConditionType.DENGUE_OUTBREAK,
        "general": ConditionType.GENERAL_SURGE
    }
    
    condition_type = condition_map.get(condition.lower())
    
    # Initialize and run engine
    engine = AllocationEngine()
    
    try:
        results = engine.run_complete_allocation(
            condition_type=condition_type,
            target_department=department
        )
        
        # Print summary
        engine.print_summary()
        
        # Save results
        if output is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"../media/resource_allocation/allocation_output_{timestamp}.json"
        
        engine.save_results(output)
        
        print("\n" + "=" * 80)
        print("✓ RESOURCE ALLOCATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        return results
        
    except Exception as e:
        print(f"\n✗ Error during allocation: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent C: Resource Allocation Engine")
    parser.add_argument("--condition", type=str, default="auto",
                       choices=["auto", "respiratory", "burn", "dengue", "general"],
                       help="Condition type (default: auto-detect)")
    parser.add_argument("--department", type=str, default="Emergency",
                       help="Target department (default: Emergency)")
    parser.add_argument("--output", type=str, default=None,
                       help="Output JSON file path")
    
    args = parser.parse_args()
    
    run_allocator(
        condition=args.condition,
        department=args.department,
        output=args.output
    )
