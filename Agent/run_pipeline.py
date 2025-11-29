"""
Main Pipeline Runner

Single entry point to run the complete hospital demand forecasting system.
Coordinates Data Generator, Forecaster, and Resource Allocator agents.
"""

import argparse
from agent_orchestrator import AgentOrchestrator


def main():
    """Main pipeline execution"""
    parser = argparse.ArgumentParser(
        description="Hospital Demand Forecasting System - Multi-Agent Pipeline"
    )
    
    parser.add_argument('--skip-data', action='store_true',
                       help='Skip data generation (use existing data)')
    parser.add_argument('--skip-forecast', action='store_true',
                       help='Skip forecasting')
    parser.add_argument('--skip-allocation', action='store_true',
                       help='Skip resource allocation')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip model training')
    
    parser.add_argument('--start-date', type=str, default="2022-01-01",
                       help='Data generation start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default="2024-11-22",
                       help='Data generation end date (YYYY-MM-DD)')
    
    parser.add_argument('--target', type=str, default='total_patients',
                       help='Forecasting target column')
    parser.add_argument('--horizon', type=int, default=7,
                       help='Forecast horizon in days')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Run pipeline
    results = orchestrator.run_complete_pipeline(
        generate_data=not args.skip_data,
        run_forecasts=not args.skip_forecast,
        allocate_resources=not args.skip_allocation,
        train_models=not args.skip_training,
        start_date=args.start_date,
        end_date=args.end_date,
        target_column=args.target,
        horizon_days=args.horizon
    )
    
    # Print summary
    orchestrator.print_final_summary(results)
    
    # Save report
    orchestrator.save_pipeline_report(results)
    
    return results


if __name__ == "__main__":
    main()
