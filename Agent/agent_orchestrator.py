"""
Agent Orchestrator

Coordinates all 3 agents to work together in sequence:
1. Data Generator Agent → Generates hospital data
2. Forecaster Agent → Runs forecasting models
3. Resource Allocator Agent → Generates logistics directives
"""

import json
from datetime import datetime
from data_generator_agent import DataGeneratorAgent
from forecaster_agent import ForecasterAgent
from resource_allocator_agent import ResourceAllocatorAgent


class AgentOrchestrator:
    """
    Orchestrates the complete pipeline of all 3 agents
    """
    
    def __init__(self):
        self.data_agent = DataGeneratorAgent()
        self.forecast_agent = ForecasterAgent()
        self.allocator_agent = ResourceAllocatorAgent()
        
        self.pipeline_results = {}
        self.status = "initialized"
    
    def run_complete_pipeline(self, 
                              generate_data=True,
                              run_forecasts=True,
                              allocate_resources=True,
                              start_date="2022-01-01",
                              end_date="2024-11-22",
                              target_column='total_patients',
                              horizon_days=7):
        """
        Run the complete agent pipeline
        
        Parameters:
        - generate_data: Whether to run Data Generator Agent
        - run_forecasts: Whether to run Forecaster Agent
        - allocate_resources: Whether to run Resource Allocator Agent
        - start_date: Data generation start date
        - end_date: Data generation end date
        - target_column: Forecasting target column
        - horizon_days: Forecast horizon
        
        Returns:
        - Dict with complete pipeline results
        """
        print("\n" + "=" * 80)
        print(" " * 20 + "HOSPITAL DEMAND FORECASTING SYSTEM")
        print(" " * 25 + "Multi-Agent Pipeline")
        print("=" * 80)
        print(f"\nPipeline Configuration:")
        print(f"  Generate Data: {generate_data}")
        print(f"  Run Forecasts: {run_forecasts}")
        print(f"  Allocate Resources: {allocate_resources}")
        print("\n" + "=" * 80)
        
        pipeline_start = datetime.now()
        
        # Phase 1: Data Generation
        if generate_data:
            print("\n\n" + "=" * 80)
            print("=" + " " * 25 + "PHASE 1: DATA GENERATION" + " " * 30 + "=")
            print("=" * 80)
            
            data_result = self.data_agent.generate_data(
                start_date=start_date,
                end_date=end_date
            )
            self.pipeline_results['data_generation'] = data_result
            
            if data_result['status'] != 'success':
                print("\n[X] Data generation failed. Aborting pipeline.")
                return self._compile_results(pipeline_start, "failed")
        
        # Phase 2: Forecasting
        if run_forecasts:
            print("\n\n" + "=" * 80)
            print("=" + " " * 28 + "PHASE 2: FORECASTING" + " " * 31 + "=")
            print("=" * 80)
            
            forecast_result = self.forecast_agent.run_forecasts(
                target_column=target_column,
                horizon_days=horizon_days
            )
            self.pipeline_results['forecasting'] = forecast_result
            
            if forecast_result['status'] != 'success':
                print("\n[!] Forecasting had issues but continuing...")
        
        # Phase 3: Resource Allocation
        if allocate_resources:
            print("\n\n" + "=" * 80)
            print("=" + " " * 24 + "PHASE 3: RESOURCE ALLOCATION" + " " * 27 + "=")
            print("=" * 80)
            
            allocation_result = self.allocator_agent.allocate_resources()
            self.pipeline_results['resource_allocation'] = allocation_result
            
            if allocation_result['status'] != 'success':
                print("\n[!] Resource allocation had issues...")
        
        # Compile final results
        self.status = "completed"
        return self._compile_results(pipeline_start, "success")
    
    def _compile_results(self, pipeline_start, status):
        """Compile all results into final report"""
        pipeline_end = datetime.now()
        duration = (pipeline_end - pipeline_start).total_seconds()
        
        final_report = {
            "pipeline_execution": {
                "status": status,
                "start_time": pipeline_start.isoformat(),
                "end_time": pipeline_end.isoformat(),
                "duration_seconds": duration,
                "agents_executed": len(self.pipeline_results)
            },
            "agent_results": self.pipeline_results,
            "summary": {
                "data_generated": self.pipeline_results.get('data_generation', {}).get('status') == 'success',
                "forecasts_completed": self.pipeline_results.get('forecasting', {}).get('models_successful', 0),
                "allocations_generated": self.pipeline_results.get('resource_allocation', {}).get('status') == 'success'
            }
        }
        
        return final_report
        
    def save_pipeline_report(self, results):
        """Save pipeline results to JSON file"""
        import os
        
        output_dir = "media"
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, "pipeline_report.json")
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)
            
        print(f"\nSaved pipeline report to: {output_path}")
    def print_final_summary(self, results):
        """Print final pipeline summary"""
        print("\n\n" + "=" * 80)
        print(" " * 25 + "PIPELINE EXECUTION SUMMARY")
        print("=" * 80)
        
        exec_info = results['pipeline_execution']
        print(f"\nStatus: {exec_info['status'].upper()}")
        print(f"Duration: {exec_info['duration_seconds']:.2f} seconds")
        print(f"Agents Executed: {exec_info['agents_executed']}")
        
        summary = results['summary']
        print(f"\nResults:")
        print(f"  [OK] Data Generated: {summary['data_generated']}")
        print(f"  [OK] Forecasts Completed: {summary['forecasts_completed']}/3 models")
        print(f"  [OK] Allocations Generated: {summary['allocations_generated']}")
        
        print("\n" + "=" * 80)
        print(" " * 20 + "[OK] PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        print("\nOutput Locations:")
        print("  [DIR] Hospital Data: media/hospital_data_csv/")
        print("  [DIR] Forecasts: media/forecast/")
        print("  [DIR] Allocations: media/resource_allocation/")
        print("  [FILE] Pipeline Report: media/pipeline_report.json")


if __name__ == "__main__":
    # Test the orchestrator
    orchestrator = AgentOrchestrator()
    
    results = orchestrator.run_complete_pipeline(
        generate_data=False,  # Skip data generation if already done
        run_forecasts=True,
        allocate_resources=True
    )
    
    orchestrator.print_final_summary(results)
    orchestrator.save_pipeline_report(results)
