# Agent C: The Logistics Commander

**Resource Optimization & Allocation Engine**

Agent C translates forecast predictions into concrete resource allocation decisions, generating structured directives for inventory orders and staffing rosters.

## Overview

Agent C is the operational layer that converts probabilistic forecasts from the Forecaster models into actionable logistics directives. It manages:

1. **Intelligent Inventory Management** - Automated purchase orders based on predicted demand
2. **Dynamic Staffing Allocation** - Roster optimization and on-call activation
3. **Operational Advisories** - Recommendations for elective procedure rescheduling

## 📁 Files

### Core Modules
- **`resource_mapping.py`** - Knowledge base mapping conditions to resources
- **`inventory_manager.py`** - Gap analysis and purchase order generation
- **`staffing_optimizer.py`** - Dynamic roster allocation with 3-level mitigation
- **`allocation_engine.py`** - Main orchestration engine
- **`forecast_loader.py`** - Loads forecasts from Forecaster models
- **`data_connector.py`** - Connects to hospital data sources
- **`run_allocator.py`** - Main runner script

## 🚀 Quick Start

```bash
cd Resource_Allocator
python run_allocator.py
```

This will:
1. Load forecasts from Forecaster models
2. Detect condition type
3. Load current inventory and staffing
4. Generate inventory actions (purchase orders)
5. Generate staffing actions (reallocations, on-call)
6. Save structured JSON output

## 📊 Output Format

The system generates a structured JSON file with:

```json
{
  "logistics_action_plan": {
    "date": "2025-11-04",
    "surge_context": "respiratory_surge",
    "predicted_patient_count": 150,
    "forecast_confidence": 0.85,
    
    "inventory_actions": [
      {
        "item_name": "Nebulizer Masks",
        "current_stock": 50,
        "predicted_demand": 300,
        "action": "GENERATE_PO",
        "quantity": 350,
        "priority": "CRITICAL",
        "vendor_id": "MEDEQUIP_A"
      }
    ],
    
    "staffing_actions": [
      {
        "role": "respiratory_therapist",
        "current_roster_count": 5,
        "required_count": 15,
        "action": "REALLOCATE",
        "source_dept": "OPD",
        "target_dept": "Emergency",
        "count": 10
      }
    ],
    
    "operational_advisories": [
      "Recommendation: Cancel elective procedures to free beds."
    ]
  }
}
```

## 🎯 Key Features

### 1. Resource Mapping Knowledge Base

Comprehensive mappings for:
- **Respiratory Surge** (smog/air quality)
- **Burn Trauma** (festivals/Diwali)
- **Dengue Outbreak** (monsoon)
- **General Surge** (default)

Each mapping includes:
- Staffing requirements (role, ratio, priority)
- Inventory requirements (SKU, consumption rate, lead time)

### 2. Intelligent Inventory Management

**Gap Analysis Algorithm**:
```
Required_Units = Predicted_Patients × Avg_Consumption_Per_Patient
Stock_Gap = Current_Stock - Required_Units
If Stock_Gap < Safety_Buffer: TRIGGER_ORDER
```

**Features**:
- SKU mapping for medical supplies
- Lead time awareness (emergency inter-hospital loans)
- Vendor prioritization
- Automatic purchase order generation
- Urgency scoring

### 3. Dynamic Staffing Optimization

**3-Level Mitigation Strategy**:
1. **Internal Reallocation** - Move staff from low to high priority departments
2. **On-Call Activation** - Automated notifications to on-call personnel
3. **Agency Requests** - Generate temporary staffing requests

**Elective Reduction**:
- Identifies non-critical procedures during surge periods
- Recommends rescheduling to free beds and staff

## 💻 Usage Examples

### Basic Usage
```bash
python run_allocator.py
```

### Specify Condition Type
```bash
python run_allocator.py --condition respiratory
python run_allocator.py --condition burn
python run_allocator.py --condition dengue
```

### Specify Department
```bash
python run_allocator.py --department ICU
```

### Custom Output Path
```bash
python run_allocator.py --output ./results/allocation.json
```

### Python API
```python
from allocation_engine import AllocationEngine
from resource_mapping import ConditionType

engine = AllocationEngine()
results = engine.run_complete_allocation(
    condition_type=ConditionType.RESPIRATORY_SURGE,
    target_department="Emergency"
)

engine.print_summary()
engine.save_results('./allocation_output.json')
```

## 🔧 Configuration

### Department Priorities

Set in `staffing_optimizer.py`:
```python
priorities = {
    'Emergency': 1,  # Highest priority
    'ICU': 1,
    'Surgery': 2,
    'OPD': 4,
    'Dermatology': 5  # Lowest priority
}
```

### Safety Buffer

Set in `inventory_manager.py`:
```python
manager = InventoryManager(safety_buffer_multiplier=1.2)  # 20% buffer
```

## 📈 Validation

### Test Scenarios

1. **Inventory Simulation**:
   ```bash
   python inventory_manager.py
   ```
   Expected: Generate PO when predicted demand > current stock

2. **Shift Leveling**:
   ```bash
   python staffing_optimizer.py
   ```
   Expected: Reallocate staff from OPD to ER before hiring agency

3. **Complete Pipeline**:
   ```bash
   python run_allocator.py
   ```
   Expected: Generate complete JSON with inventory + staffing actions

## 📝 Data Sources

- **Forecasts**: `../Forecaster/results/*.csv`
- **Inventory**: `../Data_Generator/hospital_data_csv/supply_inventory.csv`
- **Staffing**: `../Data_Generator/hospital_data_csv/staff_availability.csv`

## 🎨 Integration

Agent C integrates with:
- **Forecaster Models** (LightGBM, XGBoost, Random Forest)
- **Hospital Data Generator** (inventory and staffing data)
- **Dashboard/BI Tools** (consumes JSON output)

## 🐛 Troubleshooting

**Issue: "No forecast data found"**
- Ensure Forecaster models have been run first
- Check `../Forecaster/results/` for CSV files

**Issue: "Inventory data not found"**
- Run `Data_Generator/hospital_data_generator.py` first
- Check CSV files exist in `Data_Generator/hospital_data_csv/`

## 📚 Architecture

```
Forecaster Models → Forecast CSVs
                         ↓
                  Forecast Loader
                         ↓
Historical Data → Data Connector → Allocation Engine → JSON Output
                         ↓              ↓
                  Resource Mapping  Inventory Manager
                                       ↓
                                 Staffing Optimizer
```

---

**Created:** 2025-11-22  
**Version:** 1.0  
**Agent:** C - The Logistics Commander
