"""
Patient Volume Forecasting Service
Handles model loading and predictions for patient volume forecasting
"""

import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

class PatientVolumeForecastingService:
    """Service for predicting patient volumes using trained model"""
    
    def __init__(self, model_path='Agent/patient_volume_forecaster.pkl', 
                 data_dir='media/hospital_data_csv'):
        """
        Initialize the forecasting service
        
        Args:
            model_path: Path to the trained model pickle file
            data_dir: Directory containing historical data CSVs
        """
        self.model_path = model_path
        self.data_dir = data_dir
        self.model = None
        self.feature_columns = None
        self.historical_data = None
        self.events_data = None
        
        # Load model and data
        self._load_model()
        self._load_historical_data()
    
    def _load_model(self):
        """Load the trained forecasting model"""
        try:
            with open(self.model_path, 'rb') as f:
                model_package = pickle.load(f)
            
            self.model = model_package['model']
            self.feature_columns = model_package['feature_columns']
            print(f"✓ Model loaded from {self.model_path}")
            print(f"  Features: {len(self.feature_columns)}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def _load_historical_data(self):
        """Load historical training data and events"""
        try:
            # Load training data (for monthly averages)
            training_data_path = os.path.join('Agent', 'patient_volume_training_data.csv')
            self.historical_data = pd.read_csv(training_data_path, parse_dates=['date'])
            
            # Load events data
            events_path = os.path.join(self.data_dir, 'events.csv')
            self.events_data = pd.read_csv(events_path, parse_dates=['start_date', 'end_date'])
            
            print(f"✓ Historical data loaded: {len(self.historical_data)} records")
            print(f"✓ Events data loaded: {len(self.events_data)} events")
        except Exception as e:
            print(f"❌ Error loading historical data: {e}")
            raise
    
    def generate_future_features(self, start_date: Optional[str] = None, 
                                 end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Generate features for future dates
        
        Args:
            start_date: Start date (YYYY-MM-DD). If None, starts day after last historical date
            end_date: End date (YYYY-MM-DD). If None, predicts one year ahead
            
        Returns:
            DataFrame with engineered features for future dates
        """
        # Determine prediction period
        if start_date is None or end_date is None:
            last_historical_date = self.historical_data['date'].max()
            start_prediction_date = last_historical_date + pd.Timedelta(days=1)
            end_prediction_date = start_prediction_date + pd.Timedelta(days=364)
        else:
            start_prediction_date = pd.to_datetime(start_date)
            end_prediction_date = pd.to_datetime(end_date)
        
        # Create future dates
        future_dates = pd.date_range(start=start_prediction_date, end=end_prediction_date, freq='D')
        future_df = pd.DataFrame({'date': future_dates})
        
        # Time-based features
        future_df['day_of_week'] = future_df['date'].dt.dayofweek
        future_df['month'] = future_df['date'].dt.month
        future_df['day_of_year'] = future_df['date'].dt.dayofyear
        future_df['week_of_year'] = future_df['date'].dt.isocalendar().week.astype(int)
        future_df['quarter'] = future_df['date'].dt.quarter
        future_df['is_weekend'] = (future_df['date'].dt.dayofweek >= 5).astype(int)
        future_df['is_month_start'] = future_df['date'].dt.is_month_start.astype(int)
        future_df['is_month_end'] = future_df['date'].dt.is_month_end.astype(int)
        
        # Seasonal indicators
        future_df['is_monsoon'] = future_df['month'].isin([6, 7, 8, 9]).astype(int)
        future_df['is_winter'] = future_df['month'].isin([11, 12, 1, 2]).astype(int)
        future_df['is_summer'] = future_df['month'].isin([3, 4, 5]).astype(int)
        
        # Environmental features - use historical monthly averages
        environmental_features = [
            'temperature_avg', 'temperature_min', 'temperature_max', 'humidity_percent',
            'rainfall_mm', 'wind_speed_kmh', 'aqi_level', 'pm25', 'pm10', 
            'no2', 'so2', 'co', 'ozone', 'pollen_count'
        ]
        
        # Only use features that exist in historical data
        available_env_features = [f for f in environmental_features if f in self.historical_data.columns]
        historical_monthly_avg = self.historical_data.groupby('month')[available_env_features].mean().reset_index()
        future_df = pd.merge(future_df, historical_monthly_avg, on='month', how='left')
        
        # Event features
        future_event_records = []
        for future_year in range(start_prediction_date.year, end_prediction_date.year + 1):
            for _, event in self.events_data.iterrows():
                event_start = event['start_date'].replace(year=future_year)
                event_end = event['end_date'].replace(year=future_year)
                
                if event_start <= end_prediction_date and event_end >= start_prediction_date:
                    current_date = event_start
                    while current_date <= event_end:
                        if start_prediction_date <= current_date <= end_prediction_date:
                            future_event_records.append({
                                'date': current_date.date(),
                                'is_public_holiday': event['is_public_holiday'],
                                'event_impact_multiplier': event['impact_multiplier']
                            })
                        current_date += pd.Timedelta(days=1)
        
        # Merge events
        if future_event_records:
            future_events_df = pd.DataFrame(future_event_records)
            future_events_df['date'] = pd.to_datetime(future_events_df['date'])
            future_events_agg = future_events_df.groupby('date').agg({
                'is_public_holiday': 'max',
                'event_impact_multiplier': 'max'
            }).reset_index()
            future_df = pd.merge(future_df, future_events_agg, on='date', how='left')
        
        if 'is_public_holiday' not in future_df.columns:
            future_df['is_public_holiday'] = 0
        future_df['is_public_holiday'] = future_df['is_public_holiday'].fillna(0).astype(int)
        
        if 'event_impact_multiplier' not in future_df.columns:
            future_df['event_impact_multiplier'] = 1.0
        future_df['event_impact_multiplier'] = future_df['event_impact_multiplier'].fillna(1.0)
        
        # Lag features - use recent historical values
        last_volume = self.historical_data['daily_patient_volume'].iloc[-1]
        last_7_avg = self.historical_data['daily_patient_volume'].iloc[-7:].mean()
        
        future_df['patient_volume_lag_1'] = last_volume
        future_df['patient_volume_lag_7'] = last_volume  # Simplified
        future_df['patient_volume_rolling_7'] = last_7_avg
        
        return future_df
    
    def predict(self, start_date: Optional[str] = None, 
               end_date: Optional[str] = None) -> List[Dict]:
        """
        Predict patient volumes for future dates
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of dictionaries with date and predicted patient count
        """
        # Generate features
        future_features = self.generate_future_features(start_date, end_date)
        
        # Ensure feature columns exist
        missing_cols = [c for c in self.feature_columns if c not in future_features.columns]
        if missing_cols:
            for c in missing_cols:
                future_features[c] = 0
                
        X_future = future_features[self.feature_columns]
        
        # Handle any missing values
        X_future = X_future.fillna(X_future.mean())
        
        # Make predictions
        predictions = self.model.predict(X_future)
        
        # Format results
        results = []
        for i, row in future_features.iterrows():
            results.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'predicted_patient_volume': int(round(predictions[i])),
                'day_of_week': int(row['day_of_week']),
                'is_weekend': bool(row['is_weekend']),
                'is_holiday': bool(row['is_public_holiday']),
                'is_monsoon': bool(row['is_monsoon'])
            })
        
        return results
    
    def get_summary_statistics(self, predictions: List[Dict]) -> Dict:
        """
        Calculate summary statistics for predictions
        
        Args:
            predictions: List of prediction dictionaries
            
        Returns:
            Dictionary with summary statistics
        """
        volumes = [p['predicted_patient_volume'] for p in predictions]
        
        return {
            'total_days': len(predictions),
            'avg_daily_patients': round(np.mean(volumes), 2),
            'max_daily_patients': int(max(volumes)),
            'min_daily_patients': int(min(volumes)),
            'total_predicted_patients': int(sum(volumes)),
            'date_range': {
                'start': predictions[0]['date'],
                'end': predictions[-1]['date']
            }
        }

# Example usage
if __name__ == "__main__":
    service = PatientVolumeForecastingService()
    
    # Predict next 30 days
    predictions = service.predict(
        start_date=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        end_date=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    )
    
    print(f"\nPredictions for next 30 days:")
    for pred in predictions[:5]:
        print(f"  {pred['date']}: {pred['predicted_patient_volume']} patients")
    
    stats = service.get_summary_statistics(predictions)
    print(f"\nSummary Statistics:")
    print(f"  Average: {stats['avg_daily_patients']} patients/day")
    print(f"  Max: {stats['max_daily_patients']} patients")
    print(f"  Min: {stats['min_daily_patients']} patients")
