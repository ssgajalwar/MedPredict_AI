"""
Patient Volume Forecasting - Data Preparation and Model Training
This script prepares the training data and trains a forecasting model for daily patient volumes.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import pickle
import warnings
warnings.filterwarnings('ignore')

# Optional: ML libraries for training
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  scikit-learn not available. Install with: pip install scikit-learn")

class PatientVolumeForecaster:
    """
    Patient Volume Forecasting Pipeline
    Prepares data and trains models to predict daily patient volumes
    """
    
    def __init__(self, data_dir='media/hospital_data_csv', output_dir='Agent'):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.training_data = None
        self.model = None
        self.feature_columns = None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def load_and_prepare_data(self):
        """
        Load CSV files and prepare training data with feature engineering
        """
        print("="*60)
        print("PATIENT VOLUME FORECASTING - DATA PREPARATION")
        print("="*60)
        
        # 1. Load CSV files
        print("\n[1/7] Loading data...")
        patient_visits_df = pd.read_csv(
            os.path.join(self.data_dir, 'patient_visits.csv'),
            parse_dates=['visit_date', 'visit_dttm', 'admission_dttm', 'discharge_dttm']
        )
        weather_df = pd.read_csv(
            os.path.join(self.data_dir, 'weather_data.csv'),
            parse_dates=['record_date']
        )
        air_quality_df = pd.read_csv(
            os.path.join(self.data_dir, 'air_quality_data.csv'),
            parse_dates=['record_date']
        )
        events_df = pd.read_csv(
            os.path.join(self.data_dir, 'events.csv'),
            parse_dates=['start_date', 'end_date']
        )
        
        print(f"  ✓ Loaded patient_visits: {len(patient_visits_df):,} rows")
        print(f"  ✓ Loaded weather_data: {len(weather_df):,} rows")
        print(f"  ✓ Loaded air_quality_data: {len(air_quality_df):,} rows")
        print(f"  ✓ Loaded events: {len(events_df):,} rows")
        
        # 2. Aggregate patient visits by date
        print("\n[2/7] Aggregating patient visits by date...")
        patient_visits_df['visit_date_only'] = patient_visits_df['visit_date'].dt.date
        daily_patient_counts = patient_visits_df.groupby('visit_date_only').size().reset_index(name='daily_patient_volume')
        daily_patient_counts.rename(columns={'visit_date_only': 'date'}, inplace=True)
        daily_patient_counts['date'] = pd.to_datetime(daily_patient_counts['date'])
        print(f"  ✓ Aggregated to {len(daily_patient_counts):,} daily records")
        
        # 3. Process events data - expand to daily records
        print("\n[3/7] Processing events data...")
        daily_event_records = []
        for _, event in events_df.iterrows():
            current_date = event['start_date']
            while current_date <= event['end_date']:
                daily_event_records.append({
                    'date': current_date.date(),
                    'is_public_holiday': event['is_public_holiday'],
                    'event_impact_multiplier': event['impact_multiplier']
                })
                current_date += pd.Timedelta(days=1)
        
        daily_events_df = pd.DataFrame(daily_event_records)
        daily_events_df['date'] = pd.to_datetime(daily_events_df['date'])
        
        # Aggregate events by date (in case of overlapping events, take max)
        daily_events_agg = daily_events_df.groupby('date').agg({
            'is_public_holiday': 'max',
            'event_impact_multiplier': 'max'
        }).reset_index()
        print(f"  ✓ Processed {len(daily_events_agg):,} event days")
        
        # 4. Merge all data sources
        print("\n[4/7] Merging data sources...")
        forecast_data = daily_patient_counts.copy()
        
        # Merge weather data
        weather_df.rename(columns={'record_date': 'date'}, inplace=True)
        forecast_data = pd.merge(forecast_data, weather_df, on='date', how='left')
        
        # Merge air quality data
        air_quality_df.rename(columns={'record_date': 'date'}, inplace=True)
        forecast_data = pd.merge(forecast_data, air_quality_df, on='date', how='left')
        
        # Merge events data
        forecast_data = pd.merge(forecast_data, daily_events_agg, on='date', how='left')
        
        # Fill NaN values for event columns
        forecast_data['is_public_holiday'].fillna(False, inplace=True)
        forecast_data['event_impact_multiplier'].fillna(1.0, inplace=True)
        
        print(f"  ✓ Merged dataset shape: {forecast_data.shape}")
        
        # 5. Feature engineering - time-based features
        print("\n[5/7] Engineering time-based features...")
        forecast_data['day_of_week'] = forecast_data['date'].dt.dayofweek  # 0=Monday, 6=Sunday
        forecast_data['month'] = forecast_data['date'].dt.month
        forecast_data['day_of_year'] = forecast_data['date'].dt.dayofyear
        forecast_data['week_of_year'] = forecast_data['date'].dt.isocalendar().week.astype(int)
        forecast_data['quarter'] = forecast_data['date'].dt.quarter
        forecast_data['is_weekend'] = (forecast_data['date'].dt.dayofweek >= 5).astype(int)
        forecast_data['is_month_start'] = forecast_data['date'].dt.is_month_start.astype(int)
        forecast_data['is_month_end'] = forecast_data['date'].dt.is_month_end.astype(int)
        
        # Seasonal indicators
        forecast_data['is_monsoon'] = forecast_data['month'].isin([6, 7, 8, 9]).astype(int)
        forecast_data['is_winter'] = forecast_data['month'].isin([11, 12, 1, 2]).astype(int)
        forecast_data['is_summer'] = forecast_data['month'].isin([3, 4, 5]).astype(int)
        
        print(f"  ✓ Added {forecast_data.shape[1] - daily_patient_counts.shape[1]} engineered features")
        
        # 6. Create lag features (previous days' patient volumes)
        print("\n[6/7] Creating lag features...")
        forecast_data = forecast_data.sort_values('date').reset_index(drop=True)
        forecast_data['patient_volume_lag_1'] = forecast_data['daily_patient_volume'].shift(1)
        forecast_data['patient_volume_lag_7'] = forecast_data['daily_patient_volume'].shift(7)
        forecast_data['patient_volume_rolling_7'] = forecast_data['daily_patient_volume'].rolling(window=7).mean()
        
        # 7. Clean up and save
        print("\n[7/7] Finalizing dataset...")
        # Drop rows with NaN (due to lag features)
        forecast_data = forecast_data.dropna()
        
        # Sort by date
        forecast_data = forecast_data.sort_values('date').reset_index(drop=True)
        
        self.training_data = forecast_data
        
        print("\n" + "="*60)
        print("DATA PREPARATION COMPLETE")
        print("="*60)
        print(f"  Final shape: {forecast_data.shape}")
        print(f"  Date range: {forecast_data['date'].min()} to {forecast_data['date'].max()}")
        print(f"  Avg daily patients: {forecast_data['daily_patient_volume'].mean():.1f}")
        print(f"  Features: {forecast_data.shape[1]}")
        
        return forecast_data
    
    def save_training_data(self, filename='patient_volume_training_data.csv'):
        """Save prepared training data to CSV"""
        if self.training_data is None:
            print("⚠️  No training data to save. Run load_and_prepare_data() first.")
            return
        
        output_path = os.path.join(self.output_dir, filename)
        self.training_data.to_csv(output_path, index=False)
        print(f"\n✓ Training data saved to: {output_path}")
        return output_path
    
    def train_model(self, model_type='random_forest'):
        """
        Train a forecasting model
        
        Args:
            model_type: 'random_forest' or 'gradient_boosting'
        """
        if not ML_AVAILABLE:
            print("❌ Cannot train model - scikit-learn not installed")
            return None
        
        if self.training_data is None:
            print("⚠️  No training data. Run load_and_prepare_data() first.")
            return None
        
        print("\n" + "="*60)
        print("TRAINING PATIENT VOLUME FORECASTING MODEL")
        print("="*60)
        
        # Define features and target
        exclude_cols = ['date', 'daily_patient_volume', 'location_id']
        feature_cols = [col for col in self.training_data.columns if col not in exclude_cols]
        
        X = self.training_data[feature_cols]
        y = self.training_data['daily_patient_volume']
        
        self.feature_columns = feature_cols
        
        print(f"\nFeatures: {len(feature_cols)}")
        print(f"Target: daily_patient_volume")
        print(f"Samples: {len(X):,}")
        
        # Train-test split (80-20, time-aware)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"\nTrain set: {len(X_train):,} samples")
        print(f"Test set: {len(X_test):,} samples")
        
        # Select and train model
        print(f"\nTraining {model_type} model...")
        if model_type == 'random_forest':
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        else:  # gradient_boosting
            model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, y_pred_train)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        
        print("\n" + "="*60)
        print("MODEL EVALUATION")
        print("="*60)
        print(f"\nTrain Set:")
        print(f"  MAE:  {train_mae:.2f} patients")
        print(f"  RMSE: {train_rmse:.2f} patients")
        print(f"  R²:   {train_r2:.4f}")
        
        print(f"\nTest Set:")
        print(f"  MAE:  {test_mae:.2f} patients")
        print(f"  RMSE: {test_rmse:.2f} patients")
        print(f"  R²:   {test_r2:.4f}")
        
        # Feature importance
        if hasattr(model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': feature_cols,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\nTop 10 Most Important Features:")
            for idx, row in feature_importance.head(10).iterrows():
                print(f"  {row['feature']:30s}: {row['importance']:.4f}")
        
        self.model = model
        return model
    
    def save_model(self, filename='patient_volume_forecaster.pkl'):
        """Save trained model to pickle file"""
        if self.model is None:
            print("⚠️  No model to save. Train a model first.")
            return None
        
        model_path = os.path.join(self.output_dir, filename)
        
        # Save model and metadata
        model_package = {
            'model': self.model,
            'feature_columns': self.feature_columns,
            'trained_date': datetime.now().isoformat(),
            'data_date_range': {
                'start': str(self.training_data['date'].min()),
                'end': str(self.training_data['date'].max())
            }
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_package, f)
        
        print(f"\n✓ Model saved to: {model_path}")
        return model_path

def main():
    """Main execution function"""
    print("Starting Patient Volume Forecasting Pipeline...\n")
    
    # Initialize forecaster
    forecaster = PatientVolumeForecaster(
        data_dir='media/hospital_data_csv',
        output_dir='Agent'
    )
    
    # Step 1: Prepare data
    training_data = forecaster.load_and_prepare_data()
    
    # Step 2: Save training data
    forecaster.save_training_data('patient_volume_training_data.csv')
    
    # Step 3: Train model (if scikit-learn available)
    if ML_AVAILABLE:
        forecaster.train_model(model_type='random_forest')
        
        # Step 4: Save model
        forecaster.save_model('patient_volume_forecaster.pkl')
    else:
        print("\n⚠️  Skipping model training - install scikit-learn to train models")
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE")
    print("="*60)
    print(f"\nGenerated files in 'Agent' directory:")
    print("  - patient_volume_training_data.csv")
    if ML_AVAILABLE:
        print("  - patient_volume_forecaster.pkl")

if __name__ == "__main__":
    main()
