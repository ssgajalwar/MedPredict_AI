# Hospital Demand Forecasting Models

This folder contains three separate forecasting models for hospital demand prediction: **LightGBM**, **XGBoost**, and **Random Forest**. Each model provides complete training, prediction, and visualization capabilities with History + Forecast graphs.

## 📁 Files Overview

### Core Models (in `modals/` subfolder)
- **`modals/lightgbm_forecast.py`** - LightGBM-based forecasting model
- **`modals/xgboost_forecast.py`** - XGBoost-based forecasting model
- **`modals/random_forest_forecast.py`** - Random Forest-based forecasting model
- **`modals/__init__.py`** - Package initialization

### Utilities
- **`data_loader.py`** - Data loading and preprocessing utilities
- **`visualization.py`** - Visualization functions for History + Forecast graphs
- **`run_forecasts.py`** - Main runner to execute all models and compare results

## 🚀 Quick Start

### Run All Models
```bash
cd Forecaster
python run_forecasts.py
```

This will:
1. Load and preprocess hospital data from CSV files
2. Train all three models (LightGBM, XGBoost, Random Forest)
3. Generate 7-day forecasts
4. Create visualizations showing History + Forecast
5. Save comparison reports

### Run Individual Models

**LightGBM:**
```bash
python modals/lightgbm_forecast.py
```

**XGBoost:**
```bash
python modals/xgboost_forecast.py
```

**Random Forest:**
```bash
python modals/random_forest_forecast.py
```

## 📊 Output Files

All results are saved to the `./results/` directory:

### Visualizations
- `lightgbm_forecast_7day.png` - LightGBM History + Forecast graph
- `xgboost_forecast_7day.png` - XGBoost History + Forecast graph
- `random_forest_forecast_7day.png` - Random Forest History + Forecast graph
- `model_comparison.png` - All models compared on one graph
- `*_actual_vs_predicted.png` - Actual vs Predicted scatter plots
- `*_feature_importance.png` - Feature importance bar charts
- `*_residuals.png` - Residual analysis plots

### Data Files
- `lightgbm_forecast_7day.csv` - LightGBM forecast data
- `xgboost_forecast_7day.csv` - XGBoost forecast data
- `random_forest_forecast_7day.csv` - Random Forest forecast data
- `model_comparison_report.csv` - Performance comparison table
- `model_comparison_report.json` - Detailed comparison report

## 🎯 Forecast Targets

The models can forecast multiple hospital metrics:
- `total_patients` - Daily patient count (default)
- `admissions` - Daily admissions
- `occupied_beds` - Bed occupancy
- `avg_wait_minutes` - Average wait time
- `avg_severity` - Average severity level

### Custom Target Example
```python
from run_forecasts import run_all_forecasts

results, comparison = run_all_forecasts(
    target_column='admissions',
    horizon_days=14,
    output_dir='./results_admissions'
)
```

## 📈 Features

### Data Processing
- Loads data from `../Data_Generator/hospital_data_csv/`
- Merges patient visits, weather, air quality, events, epidemic surveillance, staff availability, and supply inventory
- Creates daily aggregations
- Generates lag features (1-30 days)
- Computes rolling statistics (7, 14, 30 day windows)
- Adds temporal features (day of week, month, seasonality)

### Model Training
- Train/validation/test split (70/15/15)
- Early stopping for gradient boosting models
- Out-of-bag error estimation for Random Forest
- Performance metrics: MAE, RMSE, R², MAPE

### Visualizations
- **History + Forecast graphs** showing:
  - Last 60 days of historical data (blue line)
  - Forecast for next 7/14/30 days (red/orange line)
  - 95% confidence intervals (shaded region)
- **Actual vs Predicted** scatter plots
- **Feature Importance** bar charts
- **Residual Analysis** plots

## 🔧 Configuration

### Modify Forecast Horizon
```python
# In any model file
forecaster, results = run_lightgbm_forecast(
    target_column='total_patients',
    horizon_days=14,  # Change to 14-day forecast
    output_dir='./results'
)
```

### Adjust Feature Engineering
```python
# In data_loader.py, modify create_features()
feature_data = loader.create_features(
    target_column='total_patients',
    lag_days=60,  # More lag features
    rolling_windows=[7, 14, 30, 60]  # More rolling windows
)
```

### Model Hyperparameters
Each model file has hyperparameters that can be adjusted:

**LightGBM** (`lightgbm_forecast.py`):
```python
self.model = lgb.LGBMRegressor(
    n_estimators=1000,
    learning_rate=0.05,
    max_depth=8,
    # ... modify as needed
)
```

**XGBoost** (`xgboost_forecast.py`):
```python
self.model = xgb.XGBRegressor(
    n_estimators=1000,
    learning_rate=0.05,
    max_depth=8,
    # ... modify as needed
)
```

**Random Forest** (`random_forest_forecast.py`):
```python
self.model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    # ... modify as needed
)
```

## 📦 Dependencies

Required Python packages:
```
pandas
numpy
lightgbm
xgboost
scikit-learn
matplotlib
seaborn
```

Install with:
```bash
cd c:/Users/Shree/Desktop/MCA/hackathon/MumbaiHacks/Project
pip install -r requirements.txt
```

## 📝 Example Usage

### Python Script
```python
from run_forecasts import run_all_forecasts

# Run all models
results, comparison = run_all_forecasts(
    target_column='total_patients',
    horizon_days=7,
    data_dir='../Data_Generator/hospital_data_csv',
    output_dir='./results'
)

# Access individual model results
lightgbm_forecast = results['lightgbm']['forecast']
print(f"LightGBM forecast: {lightgbm_forecast['forecast_values']}")

# View comparison
print(comparison)
```

### Jupyter Notebook
```python
import sys
sys.path.append('./Forecaster')

from lightgbm_forecast import LightGBMForecaster

# Initialize and run
forecaster = LightGBMForecaster()
forecaster.load_data()
forecaster.train(target_column='total_patients')
forecast = forecaster.forecast(horizon_days=7)
forecaster.visualize_results(forecast)
```

## 🎨 Visualization Examples

The models generate professional-quality graphs with:
- Clear distinction between historical (blue) and forecast (red) data
- Confidence intervals as shaded regions
- Proper labels, titles, and legends
- High-resolution output (300 DPI)

## 🏆 Model Comparison

The `run_forecasts.py` script automatically compares all models and identifies the best performer based on:
- **MAE** (Mean Absolute Error) - Lower is better
- **RMSE** (Root Mean Squared Error) - Lower is better
- **R²** (Coefficient of Determination) - Higher is better
- **MAPE** (Mean Absolute Percentage Error) - Lower is better

## 📚 Reference

This implementation is based on the reference file:
- `Data_Generator_old/forecaster.py`

Key improvements:
- Separate files for each model
- Enhanced visualization with History + Forecast graphs
- Comprehensive data loading and preprocessing
- Model comparison and reporting
- Modular and reusable code structure

## 🐛 Troubleshooting

**Issue: "FileNotFoundError: CSV files not found"**
- Ensure you've generated the hospital data first:
  ```bash
  cd Data_Generator
  python hospital_data_generator.py
  ```

**Issue: "Not enough data for forecasting"**
- Check that CSV files contain sufficient historical data (at least 60 days recommended)

**Issue: "Memory error during training"**
- Reduce `lag_days` or `rolling_windows` in feature engineering
- Use a smaller subset of data for testing

## 📧 Support

For questions or issues, refer to the implementation plan or contact the development team.

---

**Created:** 2025-11-22  
**Version:** 1.0  
**Models:** LightGBM, XGBoost, Random Forest
