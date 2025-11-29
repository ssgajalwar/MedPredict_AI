"""
Model 1 Service: Patient Volume Forecasting
Loads patient_volume_forecaster.pkl and provides prediction capabilities.
"""

import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
from pathlib import Path

class PatientVolumeService:
    def __init__(self, models_dir='backend/models', data_dir='media/data'):
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        self.model = None
        self.feature_columns = None
        self.historical_data = None
        self.events_data = None
        
        self._load_model()
        self._load_data()
        
    def _load_model(self):
        """Load the patient volume forecaster model"""
        model_path = self.models_dir / 'patient_volume_forecaster.pkl'
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
            
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
            
        print(f"✓ Loaded patient volume forecaster from {model_path}")
        
    def _load_data(self):
        """Load historical training data and events"""
        # Load historical data
        hist_path = self.data_dir / 'patient_volume_training_data.csv'
        if hist_path.exists():
            self.historical_data = pd.read_csv(hist_path, parse_dates=['date'])
            print(f"✓ Loaded historical data: {len(self.historical_data)} records")
        else:
            print(f"⚠ Historical data not found: {hist_path}")
            
        # Load events
        events_path = self.data_dir / 'events.csv'
        if events_path.exists():
            self.events_data = pd.read_csv(events_path, parse_dates=['start_date', 'end_date'])
            print(f"✓ Loaded events data: {len(self.events_data)} events")
        else:
            print(f"⚠ Events data not found: {events_path}")
            
    def generate_future_features(self, start_date=None, end_date=None):
        """Generate features for future dates"""
        if self.historical_data is None:
            raise ValueError("Historical data not loaded")
            
        # Determine prediction period
        if start_date is None or end_date is None:
            last_date = self.historical_data['date'].max()
            start_date = last_date + pd.Timedelta(days=1)
            end_date = start_date + pd.Timedelta(days=6)  # 7-day forecast
        else:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            
        # Create date range
        future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        future_df = pd.DataFrame({'date': future_dates})
        
        # Time features
        future_df['day_of_week'] = future_df['date'].dt.dayofweek
        future_df['month'] = future_df['date'].dt.month
        future_df['day_of_year'] = future_df['date'].dt.dayofyear
        future_df['week_of_year'] = future_df['date'].dt.isocalendar().week.astype(int)
        future_df['quarter'] = future_df['date'].dt.quarter
        future_df['is_weekend'] = (future_df['date'].dt.dayofweek >= 5).astype(int)
        
        # Environmental features (monthly averages from historical data)
        env_features = [
            'temperature_avg', 'temperature_min', 'temperature_max', 'humidity_percent',
            'rainfall_mm', 'wind_speed_kmh', 'aqi_level', 'pm25', 'pm10', 
            'no2', 'so2', 'co', 'ozone', 'pollen_count'
        ]
        
        monthly_avg = self.historical_data.groupby('month')[env_features].mean().reset_index()
        future_df = pd.merge(future_df, monthly_avg, on='month', how='left')
        
        # Event features
        if self.events_data is not None:
            future_df['is_public_holiday'] = 0
            future_df['event_impact_multiplier'] = 1.0
            
            for _, event in self.events_data.iterrows():
                # Project events to future years
                for year in range(start_date.year, end_date.year + 1):
                    try:
                        event_start = event['start_date'].replace(year=year)
                        event_end = event['end_date'].replace(year=year)
                        
                        mask = (future_df['date'] >= event_start) & (future_df['date'] <= event_end)
                        future_df.loc[mask, 'is_public_holiday'] = int(event['is_public_holiday'])
                        future_df.loc[mask, 'event_impact_multiplier'] = event['impact_multiplier']
                    except:
                        continue
        else:
            future_df['is_public_holiday'] = 0
            future_df['event_impact_multiplier'] = 1.0
            
        return future_df
        
    def predict(self, start_date=None, end_date=None):
        """Generate patient volume predictions"""
        future_df = self.generate_future_features(start_date, end_date)
        
        # Feature columns for prediction
        feature_cols = [
            'temperature_avg', 'temperature_min', 'temperature_max', 'humidity_percent',
            'rainfall_mm', 'wind_speed_kmh', 'aqi_level', 'pm25', 'pm10', 
            'no2', 'so2', 'co', 'ozone', 'pollen_count',
            'is_public_holiday', 'event_impact_multiplier',
            'day_of_week', 'month', 'day_of_year', 'week_of_year', 'quarter', 'is_weekend'
        ]
        
        X = future_df[feature_cols].fillna(0)
        predictions = self.model.predict(X)
        
        # Create result dataframe
        result = pd.DataFrame({
            'date': future_df['date'],
            'predicted_patients': predictions.round().astype(int),
            'lower_bound': (predictions * 0.85).round().astype(int),
            'upper_bound': (predictions * 1.15).round().astype(int)
        })
        
        return result.to_dict('records')
        
    def get_quick_forecast(self, days=7):
        """Get a quick forecast for the next N days"""
        return self.predict(end_date=datetime.now() + timedelta(days=days-1))
