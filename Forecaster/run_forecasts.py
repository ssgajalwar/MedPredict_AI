import pandas as pd
import numpy as np
import json
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

from modals.lightgbm_forecast import LightGBMForecaster, run_lightgbm_forecast
from modals.xgboost_forecast import XGBoostForecaster, run_xgboost_forecast
from modals.random_forest_forecast import RandomForestForecaster, run_random_forest_forecast
from visualization import plot_multiple_forecasts


def run_all_forecasts(target_column='total_patients', horizon_days=7,
                      data_dir='../media/hospital_data_csv',
                      output_dir='../media/forecast'):
    """
    Run all three forecasting models and compare results
    
    Parameters:
    - target_column: Column to forecast
    - horizon_days: Forecast horizon in days
    - data_dir: Directory containing CSV files
    - output_dir: Output directory for results
    
    Returns:
    - Dictionary with all model results
    """
    print("=" * 80)
    print(" " * 20 + "HOSPITAL DEMAND FORECASTING")
    print(" " * 15 + "Multi-Model Comparison & Analysis")
    print("=" * 80)
    print(f"\nTarget Variable: {target_column}")
    print(f"Forecast Horizon: {horizon_days} days")
    print(f"Data Directory: {data_dir}")
    print(f"Output Directory: {output_dir}")
    print("\n" + "=" * 80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    # 1. Run LightGBM
    print("\n\n" + "#" * 80)
    print("# MODEL 1: LightGBM")
    print("#" * 80)
    try:
        lgb_forecaster, lgb_forecast = run_lightgbm_forecast(
            target_column=target_column,
            horizon_days=horizon_days,
            data_dir=data_dir,
            output_dir=output_dir
        )
        results['lightgbm'] = {
            'forecaster': lgb_forecaster,
            'forecast': lgb_forecast,
            'success': True
        }
    except Exception as e:
        print(f"\n❌ LightGBM failed: {e}")
        results['lightgbm'] = {'success': False, 'error': str(e)}
    
    # 2. Run XGBoost
    print("\n\n" + "#" * 80)
    print("# MODEL 2: XGBoost")
    print("#" * 80)
    try:
        xgb_forecaster, xgb_forecast = run_xgboost_forecast(
            target_column=target_column,
            horizon_days=horizon_days,
            data_dir=data_dir,
            output_dir=output_dir
        )
        results['xgboost'] = {
            'forecaster': xgb_forecaster,
            'forecast': xgb_forecast,
            'success': True
        }
    except Exception as e:
        print(f"\n❌ XGBoost failed: {e}")
        results['xgboost'] = {'success': False, 'error': str(e)}
    
    # 3. Run Random Forest
    print("\n\n" + "#" * 80)
    print("# MODEL 3: Random Forest")
    print("#" * 80)
    try:
        rf_forecaster, rf_forecast = run_random_forest_forecast(
            target_column=target_column,
            horizon_days=horizon_days,
            data_dir=data_dir,
            output_dir=output_dir
        )
        results['random_forest'] = {
            'forecaster': rf_forecaster,
            'forecast': rf_forecast,
            'success': True
        }
    except Exception as e:
        print(f"\n❌ Random Forest failed: {e}")
        results['random_forest'] = {'success': False, 'error': str(e)}
    
    # 4. Compare models
    print("\n\n" + "=" * 80)
    print(" " * 25 + "MODEL COMPARISON")
    print("=" * 80)
    
    comparison = compare_models(results, target_column)
    
    # 5. Create comparison visualization
    print("\nCreating model comparison visualization...")
    create_comparison_plot(results, target_column, output_dir)
    
    # 6. Save comparison report
    print("Saving comparison report...")
    save_comparison_report(comparison, output_dir)
    
    print("\n" + "=" * 80)
    print("✓ ALL FORECASTING MODELS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nResults saved to: {output_dir}/")
    print("\nGenerated files:")
    print("  - lightgbm_forecast_*.png")
    print("  - xgboost_forecast_*.png")
    print("  - random_forest_forecast_*.png")
    print("  - model_comparison.png")
    print("  - model_comparison_report.json")
    print("  - model_comparison_report.csv")
    
    return results, comparison


def compare_models(results, target_column):
    """
    Compare performance of all models
    
    Parameters:
    - results: Dictionary with model results
    - target_column: Target variable name
    
    Returns:
    - DataFrame with comparison metrics
    """
    comparison_data = []
    
    for model_name, model_result in results.items():
        if not model_result.get('success', False):
            continue
        
        forecaster = model_result['forecaster']
        
        # Get test set metrics
        if hasattr(forecaster, 'y_test'):
            y_test = forecaster.y_test
            y_test_pred = forecaster.model.predict(forecaster.X_test)
            
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            
            mae = mean_absolute_error(y_test, y_test_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
            r2 = r2_score(y_test, y_test_pred)
            mape = np.mean(np.abs((y_test - y_test_pred) / y_test)) * 100
            
            comparison_data.append({
                'Model': model_name.replace('_', ' ').title(),
                'MAE': mae,
                'RMSE': rmse,
                'R²': r2,
                'MAPE (%)': mape,
                'Mean Forecast': np.mean(model_result['forecast']['forecast_values']),
                'Forecast Std': np.std(model_result['forecast']['forecast_values'])
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    if len(comparison_df) > 0:
        print("\n" + "-" * 80)
        print("MODEL PERFORMANCE COMPARISON (Test Set)")
        print("-" * 80)
        print(comparison_df.to_string(index=False))
        print("-" * 80)
        
        # Find best model
        best_model_idx = comparison_df['MAE'].idxmin()
        best_model = comparison_df.loc[best_model_idx, 'Model']
        print(f"\n🏆 Best Model (by MAE): {best_model}")
        print(f"   MAE: {comparison_df.loc[best_model_idx, 'MAE']:.2f}")
        print(f"   RMSE: {comparison_df.loc[best_model_idx, 'RMSE']:.2f}")
        print(f"   R²: {comparison_df.loc[best_model_idx, 'R²']:.4f}")
    
    return comparison_df


def create_comparison_plot(results, target_column, output_dir):
    """
    Create a single plot comparing all model forecasts
    
    Parameters:
    - results: Dictionary with model results
    - target_column: Target variable name
    - output_dir: Output directory
    """
    forecasts_dict = {}
    historical_data = None
    
    for model_name, model_result in results.items():
        if not model_result.get('success', False):
            continue
        
        forecaster = model_result['forecaster']
        forecast = model_result['forecast']
        
        if historical_data is None:
            historical_data = forecaster.daily_data[target_column]
        
        # Prepare forecast data
        dates = forecast['forecast_dates']
        values = forecast['forecast_values']
        ci = ([ci[0] for ci in forecast['confidence_intervals']],
              [ci[1] for ci in forecast['confidence_intervals']])
        
        forecasts_dict[model_name.replace('_', ' ').title()] = (dates, values, ci)
    
    if len(forecasts_dict) > 0 and historical_data is not None:
        plot_multiple_forecasts(
            historical_data,
            forecasts_dict,
            target_column,
            save_path=f"{output_dir}/model_comparison.png",
            show_plot=False
        )


def save_comparison_report(comparison_df, output_dir):
    """
    Save comparison report to JSON and CSV
    
    Parameters:
    - comparison_df: DataFrame with comparison metrics
    - output_dir: Output directory
    """
    if len(comparison_df) == 0:
        return
    
    # Save as CSV
    csv_path = f"{output_dir}/model_comparison_report.csv"
    comparison_df.to_csv(csv_path, index=False)
    print(f"  ✓ Saved CSV report to: {csv_path}")
    
    # Save as JSON
    json_path = f"{output_dir}/model_comparison_report.json"
    report = {
        'generation_timestamp': datetime.now().isoformat(),
        'models_compared': len(comparison_df),
        'best_model': comparison_df.loc[comparison_df['MAE'].idxmin(), 'Model'],
        'metrics': comparison_df.to_dict(orient='records')
    }
    
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"  ✓ Saved JSON report to: {json_path}")


def run_quick_forecast(target_column='total_patients', horizon_days=7):
    """
    Quick forecast with default settings
    
    Parameters:
    - target_column: Column to forecast
    - horizon_days: Forecast horizon
    """
    return run_all_forecasts(
        target_column=target_column,
        horizon_days=horizon_days,
        data_dir='../media/hospital_data_csv',
        output_dir='../media/forecast'
    )


if __name__ == "__main__":
    # Run all forecasting models
    results, comparison = run_all_forecasts(
        target_column='total_patients',
        horizon_days=7,
        data_dir='../media/hospital_data_csv',
        output_dir='../media/forecast'
    )
    
    print("\n" + "=" * 80)
    print("FORECASTING COMPLETE!")
    print("=" * 80)
    print("\nTo run forecasts for different targets, use:")
    print("  python run_forecasts.py")
    print("\nOr import and use:")
    print("  from run_forecasts import run_all_forecasts")
    print("  results, comparison = run_all_forecasts(target_column='admissions', horizon_days=14)")
