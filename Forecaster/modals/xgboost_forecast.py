import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime, timedelta
import warnings
import os
import sys
warnings.filterwarnings('ignore')

# Add parent Forecaster directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_loader import HospitalDataLoader
from visualization import (plot_history_and_forecast, plot_actual_vs_predicted,
                           plot_feature_importance, plot_residuals)


class XGBoostForecaster:
    """
    XGBoost-based forecasting model for hospital demand prediction
    """
    
    def __init__(self, data_dir='../Data_Generator/hospital_data_csv'):
        """
        Initialize the XGBoost forecaster
        
        Parameters:
        - data_dir: Directory containing hospital CSV files
        """
        self.data_dir = data_dir
        self.loader = HospitalDataLoader(data_dir)
        self.model = None
        self.feature_columns = None
        self.target_column = None
        
    def load_data(self):
        """Load and prepare data"""
        print("=" * 60)
        print("XGBOOST FORECASTER - DATA LOADING")
        print("=" * 60)
        self.daily_data = self.loader.load_and_merge_data()
        return self.daily_data
    
    def train(self, target_column='total_patients', lag_days=30, 
              rolling_windows=[7, 14, 30], test_size=0.2, val_size=0.1):
        """
        Train the XGBoost forecasting model
        
        Parameters:
        - target_column: Column to forecast
        - lag_days: Number of lag features
        - rolling_windows: Window sizes for rolling statistics
        - test_size: Proportion for testing
        - val_size: Proportion for validation
        
        Returns:
        - Dictionary with training results
        """
        print("\n" + "=" * 60)
        print("XGBOOST FORECASTER - MODEL TRAINING")
        print("=" * 60)
        
        self.target_column = target_column
        
        # Create features
        feature_data = self.loader.create_features(
            target_column, lag_days=lag_days, rolling_windows=rolling_windows
        )
        
        # Split data
        X_train, X_val, X_test, y_train, y_val, y_test = self.loader.get_train_test_split(
            feature_data, target_column, test_size=test_size, val_size=val_size
        )
        
        self.feature_columns = X_train.columns.tolist()
        
        # Store test data for later evaluation
        self.X_test = X_test
        self.y_test = y_test
        self.test_dates = X_test.index
        
        # Train XGBoost model
        print("\nTraining XGBoost model...")
        self.model = xgb.XGBRegressor(
            n_estimators=1000,
            learning_rate=0.05,
            max_depth=8,
            min_child_weight=3,
            subsample=0.8,
            colsample_bytree=0.8,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            importance_type='gain',
            verbosity=0
        )
        
        # Train with early stopping
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        # Evaluate on validation set
        y_val_pred = self.model.predict(X_val)
        val_mae = mean_absolute_error(y_val, y_val_pred)
        val_rmse = np.sqrt(mean_squared_error(y_val, y_val_pred))
        val_r2 = r2_score(y_val, y_val_pred)
        val_mape = np.mean(np.abs((y_val - y_val_pred) / y_val)) * 100
        
        # Evaluate on test set
        y_test_pred = self.model.predict(X_test)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_r2 = r2_score(y_test, y_test_pred)
        test_mape = np.mean(np.abs((y_test - y_test_pred) / y_test)) * 100
        
        print("\n" + "-" * 60)
        print("MODEL PERFORMANCE")
        print("-" * 60)
        print(f"Validation Set:")
        print(f"  MAE:  {val_mae:.2f}")
        print(f"  RMSE: {val_rmse:.2f}")
        print(f"  R²:   {val_r2:.4f}")
        print(f"  MAPE: {val_mape:.2f}%")
        print(f"\nTest Set:")
        print(f"  MAE:  {test_mae:.2f}")
        print(f"  RMSE: {test_rmse:.2f}")
        print(f"  R²:   {test_r2:.4f}")
        print(f"  MAPE: {test_mape:.2f}%")
        
        results = {
            'val_mae': val_mae,
            'val_rmse': val_rmse,
            'val_r2': val_r2,
            'val_mape': val_mape,
            'test_mae': test_mae,
            'test_rmse': test_rmse,
            'test_r2': test_r2,
            'test_mape': test_mape,
            'y_val': y_val,
            'y_val_pred': y_val_pred,
            'y_test': y_test,
            'y_test_pred': y_test_pred
        }
        
        return results
    
    def forecast(self, horizon_days=7):
        """
        Generate forecast for future days
        
        Parameters:
        - horizon_days: Number of days to forecast
        
        Returns:
        - Dictionary with forecast results
        """
        print("\n" + "=" * 60)
        print(f"XGBOOST FORECASTER - GENERATING {horizon_days}-DAY FORECAST")
        print("=" * 60)
        
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Get the latest data point
        latest_date = self.daily_data.index[-1]
        print(f"Latest data date: {latest_date}")
        
        # Create forecast dates
        forecast_dates = [latest_date + timedelta(days=i) for i in range(1, horizon_days + 1)]
        
        # Generate forecasts
        forecasts = []
        confidence_intervals = []
        
        # Use the last known data as starting point
        current_data = self.daily_data.copy()
        
        for i, future_date in enumerate(forecast_dates):
            # Create features for this future date
            future_features = self._create_future_features(
                current_data, future_date, self.target_column
            )
            
            # Make prediction
            pred = self.model.predict(future_features)[0]
            forecasts.append(pred)
            
            # Simple confidence interval using test set error
            if hasattr(self, 'y_test'):
                test_error = np.std(self.y_test - self.model.predict(self.X_test))
                ci_width = 1.96 * test_error  # 95% CI
                confidence_intervals.append((pred - ci_width, pred + ci_width))
            else:
                confidence_intervals.append((pred * 0.9, pred * 1.1))
            
            # Update current_data with the prediction for next iteration
            new_row = current_data.iloc[[-1]].copy()
            new_row.index = [future_date]
            new_row[self.target_column] = pred
            current_data = pd.concat([current_data, new_row])
        
        print(f"\n+ Generated {horizon_days}-day forecast")
        print(f"  Forecast range: {forecast_dates[0]} to {forecast_dates[-1]}")
        print(f"  Mean forecast: {np.mean(forecasts):.2f}")
        print(f"  Min forecast:  {np.min(forecasts):.2f}")
        print(f"  Max forecast:  {np.max(forecasts):.2f}")
        
        results = {
            'forecast_dates': forecast_dates,
            'forecast_values': forecasts,
            'confidence_intervals': confidence_intervals
        }
        
        return results
    
    def _create_future_features(self, data, future_date, target_column):
        """
        Create feature set for future prediction
        
        Parameters:
        - data: Historical data
        - future_date: Date to predict
        - target_column: Target variable name
        
        Returns:
        - DataFrame with features for prediction
        """
        # Create a new row with temporal features
        future_features = pd.DataFrame(index=[future_date])
        
        # Temporal features
        future_features['day_of_week'] = future_date.dayofweek
        future_features['day_of_month'] = future_date.day
        future_features['month'] = future_date.month
        future_features['quarter'] = (future_date.month - 1) // 3 + 1
        future_features['year'] = future_date.year
        future_features['is_weekend'] = int(future_date.dayofweek >= 5)
        future_features['day_of_year'] = future_date.dayofyear
        future_features['sin_day_of_year'] = np.sin(2 * np.pi * future_date.dayofyear / 365)
        future_features['cos_day_of_year'] = np.cos(2 * np.pi * future_date.dayofyear / 365)
        
        # For other features, use the most recent available values
        for col in self.feature_columns:
            if col not in future_features.columns:
                if col in data.columns:
                    future_features[col] = data[col].iloc[-1]
                else:
                    future_features[col] = 0
        
        # Ensure all required features are present
        for col in self.feature_columns:
            if col not in future_features.columns:
                future_features[col] = 0
        
        return future_features[self.feature_columns]
    
    def visualize_results(self, forecast_results, output_dir='./results'):
        """
        Create visualizations of forecast results
        
        Parameters:
        - forecast_results: Dictionary from forecast() method
        - output_dir: Directory to save plots
        """
        print("\n" + "=" * 60)
        print("XGBOOST FORECASTER - GENERATING VISUALIZATIONS")
        print("=" * 60)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. History + Forecast plot
        print("\n1. Creating History + Forecast plot...")
        historical_data = self.daily_data[self.target_column]
        lower_ci = [ci[0] for ci in forecast_results['confidence_intervals']]
        upper_ci = [ci[1] for ci in forecast_results['confidence_intervals']]
        
        plot_history_and_forecast(
            historical_data,
            forecast_results['forecast_values'],
            self.target_column,
            forecast_results['forecast_dates'],
            confidence_intervals=(lower_ci, upper_ci),
            model_name="XGBoost",
            horizon_days=len(forecast_results['forecast_dates']),
            save_path=f"{output_dir}/xgboost_forecast_{len(forecast_results['forecast_dates'])}day.png",
            show_plot=False
        )
        
        # 2. Actual vs Predicted (on test set)
        if hasattr(self, 'y_test'):
            print("2. Creating Actual vs Predicted plot...")
            y_test_pred = self.model.predict(self.X_test)
            plot_actual_vs_predicted(
                self.y_test,
                y_test_pred,
                self.target_column,
                model_name="XGBoost",
                save_path=f"{output_dir}/xgboost_actual_vs_predicted.png",
                show_plot=False
            )
        
        # 3. Feature Importance
        print("3. Creating Feature Importance plot...")
        plot_feature_importance(
            self.feature_columns,
            self.model.feature_importances_,
            top_n=15,
            model_name="XGBoost",
            save_path=f"{output_dir}/xgboost_feature_importance.png",
            show_plot=False
        )
        
        # 4. Residuals plot
        if hasattr(self, 'y_test'):
            print("4. Creating Residuals plot...")
            plot_residuals(
                self.y_test,
                y_test_pred,
                self.target_column,
                model_name="XGBoost",
                save_path=f"{output_dir}/xgboost_residuals.png",
                show_plot=False
            )
        
        print(f"\n+ All visualizations saved to: {output_dir}/")
    
    def save_forecast_to_csv(self, forecast_results, output_path='xgboost_forecast.csv'):
        """
        Save forecast results to CSV
        
        Parameters:
        - forecast_results: Dictionary from forecast() method
        - output_path: Path to save CSV file
        """
        forecast_df = pd.DataFrame({
            'date': forecast_results['forecast_dates'],
            'forecast': forecast_results['forecast_values'],
            'lower_ci': [ci[0] for ci in forecast_results['confidence_intervals']],
            'upper_ci': [ci[1] for ci in forecast_results['confidence_intervals']]
        })
        
        forecast_df.to_csv(output_path, index=False)
        print(f"\n+ Forecast saved to: {output_path}")
        
        return forecast_df


def run_xgboost_forecast(target_column='total_patients', horizon_days=7, 
                         data_dir='../Data_Generator/hospital_data_csv',
                         output_dir='./results'):
    """
    Complete XGBoost forecasting pipeline
    
    Parameters:
    - target_column: Column to forecast
    - horizon_days: Forecast horizon
    - data_dir: Data directory
    - output_dir: Output directory for results
    
    Returns:
    - Tuple of (forecaster, forecast_results)
    """
    print("=" * 60)
    print("XGBOOST HOSPITAL DEMAND FORECASTING")
    print("=" * 60)
    
    # Initialize forecaster
    forecaster = XGBoostForecaster(data_dir)
    
    # Load data
    forecaster.load_data()
    
    # Train model
    training_results = forecaster.train(target_column=target_column)
    
    # Generate forecast
    forecast_results = forecaster.forecast(horizon_days=horizon_days)
    
    # Create visualizations
    forecaster.visualize_results(forecast_results, output_dir=output_dir)
    
    # Save forecast to CSV
    forecaster.save_forecast_to_csv(
        forecast_results, 
        output_path=f"{output_dir}/xgboost_forecast_{horizon_days}day.csv"
    )
    
    print("\n" + "=" * 60)
    print("✓ XGBOOST FORECASTING COMPLETED SUCCESSFULLY!".replace("✓", "+"))
    print("=" * 60)
    
    return forecaster, forecast_results


if __name__ == "__main__":
    # Run XGBoost forecasting
    forecaster, results = run_xgboost_forecast(
        target_column='total_patients',
        horizon_days=7,
        output_dir='./results'
    )
