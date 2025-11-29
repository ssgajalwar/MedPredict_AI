"""
Train Model 2: Department-wise Patient Volume Forecasting
Trains a MultiOutput Regressor to predict patient volumes for all departments simultaneously.
"""

import pandas as pd
import numpy as np
import os
import pickle
import warnings
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

warnings.filterwarnings('ignore')

class DepartmentVolumeForecaster:
    def __init__(self, data_path='media/modal_train_data/department_training_data.csv', output_dir='Agent'):
        self.data_path = data_path
        self.output_dir = output_dir
        self.model = None
        self.feature_columns = None
        self.target_columns = None
        
        os.makedirs(output_dir, exist_ok=True)
        
    def train(self):
        print("="*60)
        print("TRAINING MODEL 2: DEPARTMENT-WISE FORECASTER")
        print("="*60)
        
        # Load Data
        if not os.path.exists(self.data_path):
            print(f"❌ Data file not found: {self.data_path}")
            return
            
        df = pd.read_csv(self.data_path)
        print(f"✓ Loaded data: {df.shape}")
        
        # Identify Target Columns (Department Columns)
        # We assume department columns are those that are NOT in the feature set
        # But a better way is to exclude known feature columns
        
        known_features = [
            'date', 'location_id', 'record_date', 
            'temperature_avg', 'temperature_min', 'temperature_max', 'humidity_percent',
            'rainfall_mm', 'wind_speed_kmh', 
            'aqi_level', 'pm25', 'pm10', 'no2', 'so2', 'co', 'ozone', 'pollen_count',
            'is_public_holiday', 'event_impact_multiplier',
            'day_of_week', 'month', 'day_of_year', 'week_of_year', 'quarter', 'is_weekend'
        ]
        
        # Targets are columns NOT in known_features (and not 'date' or IDs)
        # Actually, let's explicitly identify them from the dataframe columns
        # In prepare_department_data.py, we pivoted department names.
        # Let's assume any column that is NOT in the standard feature list is a target.
        
        feature_cols = [c for c in df.columns if c in known_features and c != 'date' and c != 'location_id']
        target_cols = [c for c in df.columns if c not in known_features and c != 'date' and c != 'location_id']
        
        print(f"Features ({len(feature_cols)}): {feature_cols[:5]} ...")
        print(f"Targets ({len(target_cols)}): {target_cols}")
        
        self.feature_columns = feature_cols
        self.target_columns = target_cols
        
        X = df[feature_cols].fillna(0) # Handle any remaining NaNs
        y = df[target_cols].fillna(0)
        
        # Train-Test Split
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        print(f"\nTraining on {len(X_train)} samples, Testing on {len(X_test)} samples")
        
        # Initialize MultiOutput Regressor
        # Using RandomForest as base estimator
        base_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model = MultiOutputRegressor(base_model)
        
        print("Training model...")
        model.fit(X_train, y_train)
        
        # Evaluate
        print("\nEvaluation:")
        y_pred = model.predict(X_test)
        
        avg_mae = mean_absolute_error(y_test, y_pred)
        avg_r2 = r2_score(y_test, y_pred)
        
        print(f"  Average MAE: {avg_mae:.2f}")
        print(f"  Average R²:  {avg_r2:.4f}")
        
        # Per-target metrics
        print("\nPer-Department Performance (MAE):")
        for i, col in enumerate(target_cols):
            mae = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
            print(f"  {col:30s}: {mae:.2f}")
            
        self.model = model
        
        # Save Model
        output_path = f'{self.output_dir}/department_distribution_predictor.pkl'
        with open(output_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'feature_columns': feature_cols,
                'target_columns': target_cols
            }, f)
            
        print(f"\n✓ Model saved to {output_path}")

if __name__ == "__main__":
    forecaster = DepartmentVolumeForecaster()
    forecaster.train()
