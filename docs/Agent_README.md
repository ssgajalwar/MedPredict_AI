
### Run Complete Pipeline
```bash
cd Agent
python run_pipeline.py
```

This executes all 3 agents in sequence:
1. Generates hospital data → `media/data/hospital_data/`
2. Runs forecasting models → `media/forecasts/`
3. Generates resource allocations → `media/allocations/`
4. Creates pipeline report → `media/pipeline_report.json`

### Skip Data Generation (Use Existing Data)
```bash
python run_pipeline.py --skip-data
```

### Run Only Specific Phases
```bash
# Only forecasting and allocation
python run_pipeline.py --skip-data

# Only data generation
python run_pipeline.py --skip-forecast --skip-allocation

# Only resource allocation
python run_pipeline.py --skip-data --skip-forecast
```

### Custom Parameters
```bash
python run_pipeline.py --target admissions --horizon 14 --start-date 2023-01-01
```

## 📁 Files

- **`data_generator_agent.py`** - Wraps Data_Generator functionality
- **`forecaster_agent.py`** - Wraps Forecaster functionality
- **`resource_allocator_agent.py`** - Wraps Resource_Allocator functionality
- **`agent_orchestrator.py`** - Coordinates all agents
- **`run_pipeline.py`** - Main entry point with CLI

## 🎯 Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR                        │
│                  (agent_orchestrator.py)                     │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┬───────────────────┐
        │                       │                   │
        ▼                       ▼                   ▼
┌───────────────┐      ┌────────────────┐   ┌──────────────────┐
│ DATA          │      │ FORECASTER     │   │ RESOURCE         │
│ GENERATOR     │─────▶│ AGENT          │──▶│ ALLOCATOR        │
│ AGENT         │      │                │   │ AGENT            │
└───────┬───────┘      └────────┬───────┘   └────────┬─────────┘
        │                       │                     │
        ▼                       ▼                     ▼
   media/data/          media/forecasts/      media/allocations/
```

## 📊 Data Flow

1. **Data Generator Agent**
   - Generates 12 CSV files with synthetic hospital data
   - Outputs to `media/data/hospital_data/`
   - Includes: patients, staff, inventory, weather, events, etc.

2. **Forecaster Agent**
   - Loads data from `media/data/hospital_data/`
   - Runs 3 models: LightGBM, XGBoost, Random Forest
   - Outputs forecasts to `media/forecasts/csv/`
   - Outputs visualizations to `media/forecasts/visualizations/`

3. **Resource Allocator Agent**
   - Loads forecasts from `media/forecasts/`
   - Generates inventory purchase orders
   - Generates staffing directives
   - Outputs JSON to `media/allocations/`

## 💻 Python API

### Run Individual Agents

```python
from data_generator_agent import DataGeneratorAgent
from forecaster_agent import ForecasterAgent
from resource_allocator_agent import ResourceAllocatorAgent

# Run Data Generator
data_agent = DataGeneratorAgent()
data_result = data_agent.generate_data()

# Run Forecaster
forecast_agent = ForecasterAgent()
forecast_result = forecast_agent.run_forecasts(target_column='total_patients', horizon_days=7)

# Run Resource Allocator
allocator_agent = ResourceAllocatorAgent()
allocation_result = allocator_agent.allocate_resources()
```

### Run Complete Pipeline

```python
from agent_orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

results = orchestrator.run_complete_pipeline(
    generate_data=True,
    run_forecasts=True,
    allocate_resources=True,
    target_column='total_patients',
    horizon_days=7
)

orchestrator.print_final_summary(results)
orchestrator.save_pipeline_report(results)
```

## 📈 Output Structure

```
media/
├── data/
│   ├── hospital_data/          # 12 CSV files
│   └── analysis_results/       # 4 analysis CSV files
├── forecasts/
│   ├── csv/                    # Forecast CSV files (3 models)
│   └── visualizations/         # Forecast PNG files (9+ images)
├── allocations/                # Allocation JSON files
└── pipeline_report.json        # Complete pipeline execution report
```

## 🎛️ Command-Line Options

```bash
python run_pipeline.py [OPTIONS]

Options:
  --skip-data              Skip data generation
  --skip-forecast          Skip forecasting
  --skip-allocation        Skip resource allocation
  --start-date YYYY-MM-DD  Data generation start date
  --end-date YYYY-MM-DD    Data generation end date
  --target COLUMN          Forecasting target column
  --horizon DAYS           Forecast horizon in days
```

## 📝 Pipeline Report

The system generates a comprehensive JSON report:

```json
{
  "pipeline_execution": {
    "status": "success",
    "start_time": "2025-11-22T17:30:00",
    "end_time": "2025-11-22T17:35:00",
    "duration_seconds": 300,
    "agents_executed": 3
  },
  "agent_results": {
    "data_generation": {...},
    "forecasting": {...},
    "resource_allocation": {...}
  },
  "summary": {
    "data_generated": true,
    "forecasts_completed": 3,
    "allocations_generated": true
  }
}
```

## 🔧 Configuration

Each agent can be configured independently:

**Data Generator Agent**:
- Output directory: `media/data/hospital_data/`
- Date range: Configurable via parameters

**Forecaster Agent**:
- Input: `media/data/hospital_data/`
- Output: `media/forecasts/`
- Models: LightGBM, XGBoost, Random Forest

**Resource Allocator Agent**:
- Input forecasts: `media/forecasts/`
- Input data: `media/data/hospital_data/`
- Output: `media/allocations/`

## 🎯 Use Cases

### Daily Operations
```bash
# Run forecasting and allocation with existing data
python run_pipeline.py --skip-data
```

### Full System Test
```bash
# Generate new data and run complete pipeline
python run_pipeline.py
```

### Custom Forecast
```bash
# 30-day forecast for admissions
python run_pipeline.py --skip-data --target admissions --horizon 30
```

## 🐛 Troubleshooting

**Issue: "No data found"**
- Run with data generation: `python run_pipeline.py` (without --skip-data)

**Issue: "Forecast files not found"**
- Ensure forecasting completed successfully
- Check `media/forecasts/csv/` for forecast files

**Issue: "Import errors"**
- Ensure you're in the Agent directory: `cd Agent`
- Activate virtual environment if needed

## 📚 Integration

The agent system integrates with:
- **Data_Generator** folder - Data generation logic
- **Forecaster** folder - Forecasting models
- **Resource_Allocator** folder - Resource optimization logic
- **media** folder - Centralized output storage

---

**Created:** 2025-11-22  
**Version:** 1.0  
**Agents:** 3 (Data Generator, Forecaster, Resource Allocator)
