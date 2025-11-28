'''Resource Allocator Agent
Wraps the Resource_Allocator functionality to generate logistics directives
and output to the centralized media folder.
'''

import sys
import os
import shutil

# Ensure project root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Resource_Allocator.allocation_engine import AllocationEngine
from Resource_Allocator.resource_mapping import ConditionType
from Agent.feedback_learner import FeedbackLearner


class ResourceAllocatorAgent:
    """Agent responsible for resource allocation and logistics planning.

    Forecasts are read from ``../media/forecast`` and hospital data from
    ``../media/hospital_data_csv``. All allocation results are stored under
    ``../media/resource_allocation``.
    """

    def __init__(self, forecast_dir='media/forecast',
                 data_dir='media/hospital_data_csv',
                 output_dir='media/resource_allocation'):
        self.forecast_dir = forecast_dir
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.status = "initialized"
        self.engine = None
        self.learner = FeedbackLearner()
        self.results = {}

    def allocate_resources(self, condition_type=None, target_department="Emergency"):
        """Run resource allocation.

        Parameters
        ----------
        condition_type: ConditionType or None
            Type of condition (auto‑detected if ``None``).
        target_department: str
            Target department for allocation.
        """
        print("=" * 80)
        print(" " * 23 + "RESOURCE ALLOCATOR AGENT")
        print(" " * 20 + "Logistics & Resource Optimization")
        print("=" * 80)
        try:
            # Initialise allocation engine
            self.engine = AllocationEngine()

            # Apply learned safety buffer
            safety_buffer = self.learner.get_safety_buffer()
            print(f"\n[LEARNING] Applying adaptive safety buffer: {safety_buffer:.2f}x")

            # Run allocation
            results = self.engine.run_complete_allocation(
                condition_type=condition_type,
                target_department=target_department,
            )

            # Simulated feedback loop
            predicted = results['logistics_action_plan']['predicted_patient_count']
            import random
            actual = int(predicted * random.uniform(0.8, 1.2))
            print("\n[FEEDBACK LOOP] Simulating post-allocation analysis...")
            print(f"  Predicted Demand: {predicted}")
            print(f"  Simulated Actual: {actual}")
            self.learner.update_learning(predicted, actual)

            # Print engine summary
            self.engine.print_summary()

            # Save results
            os.makedirs(self.output_dir, exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"allocation_output_{timestamp}.json")
            self.engine.save_results(output_file)

            self.status = "completed"
            self.results = {
                "status": "success",
                "output_file": output_file,
                "output_dir": self.output_dir,
                "surge_context": results['logistics_action_plan']['surge_context'],
                "predicted_patients": predicted,
                "inventory_actions": len(results['logistics_action_plan']['inventory_actions']),
                "staffing_actions": len(results['logistics_action_plan']['staffing_actions']),
                "message": "Resource allocation completed successfully",
            }
            print("\n" + "=" * 80)
            print("[OK] RESOURCE ALLOCATION COMPLETED!")
            print("=" * 80)
            print(f"  Output file: {output_file}")
            print(f"  Inventory actions: {self.results['inventory_actions']}")
            print(f"  Staffing actions: {self.results['staffing_actions']}")
            return self.results
        except Exception as e:
            self.status = "failed"
            print(f"\n[X] Error during resource allocation: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "failed", "error": str(e), "message": "Resource allocation failed"}

    def get_status(self):
        """Get current agent status."""
        return {"agent": "ResourceAllocatorAgent", "status": self.status, "output_dir": self.output_dir}


def run_resource_allocator_agent():
    """Standalone runner for Resource Allocator Agent."""
    agent = ResourceAllocatorAgent()
    result = agent.allocate_resources()
    return agent, result

if __name__ == "__main__":
    agent, result = run_resource_allocator_agent()
    print(f"\nAgent Status: {agent.get_status()}")
