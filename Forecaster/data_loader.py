import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
import os
warnings.filterwarnings('ignore')

class HospitalDataLoader:
    """
    Data loader and preprocessor for hospital forecasting models.
    Loads data from CSV files and creates a comprehensive daily dataset.
    """
    
    def __init__(self, data_dir='../media/hospital_data_csv'):
        """
        Initialize the data loader
        
        Parameters:
        - data_dir: Directory containing the hospital CSV files
        """
        self.data_dir = data_dir
        self.daily_data = None
        
    def load_and_merge_data(self) -> pd.DataFrame:
        """Load all datasets and merge them into a daily aggregated dataset"""
        print("Loading hospital datasets...")
        
        try:
            # Load all datasets
            print("  Loading patient visits...")
            patient_visits = pd.read_csv(f'{self.data_dir}/patient_visits.csv', 
                                        parse_dates=['visit_date', 'visit_dttm', 'admission_dttm', 'discharge_dttm'])
            
            print("  Loading weather data...")
            weather = pd.read_csv(f'{self.data_dir}/weather_data.csv', 
                                 parse_dates=['record_date'])
            
            print("  Loading air quality data...")
            air_quality = pd.read_csv(f'{self.data_dir}/air_quality_data.csv', 
                                     parse_dates=['record_date'])
            
            print("  Loading events...")
            events = pd.read_csv(f'{self.data_dir}/events.csv', 
                                parse_dates=['start_date', 'end_date'])
            
            print("  Loading epidemic surveillance...")
            epidemic = pd.read_csv(f'{self.data_dir}/epidemic_surveillance.csv', 
                                  parse_dates=['date'])
            
            print("  Loading staff availability...")
            staff_avail = pd.read_csv(f'{self.data_dir}/staff_availability.csv', 
                                     parse_dates=['snapshot_date'])
            
            print("  Loading supply inventory...")
            supply_inv = pd.read_csv(f'{self.data_dir}/supply_inventory.csv', 
                                    parse_dates=['snapshot_date'])
            
            print("+ All datasets loaded successfully")
            
            # Create daily aggregations
            self.daily_data = self._create_daily_dataset(
                patient_visits, weather, air_quality, events, 
                epidemic, staff_avail, supply_inv
            )
            
            return self.daily_data
            
        except FileNotFoundError as e:
            print(f"Error loading data: {e}")
            print(f"Please ensure CSV files exist in: {self.data_dir}")
            raise
    
    def _create_daily_dataset(self, patient_visits, weather, air_quality, 
                             events, epidemic, staff_avail, supply_inv) -> pd.DataFrame:
        """Create a comprehensive daily dataset for forecasting"""
        print("\nCreating daily aggregated dataset...")
        
        # 1. Aggregate patient visits by date
        print("  Aggregating patient visits...")
        daily_patients = patient_visits.groupby('visit_date').agg({
            'visit_id': 'count',
            'admission_flag': 'sum',
            'severity_level': 'mean',
            'wait_minutes': 'mean',
            'age': 'mean'
        }).rename(columns={
            'visit_id': 'total_patients',
            'admission_flag': 'admissions',
            'severity_level': 'avg_severity',
            'wait_minutes': 'avg_wait_minutes',
            'age': 'avg_age'
        })
        
        # Calculate bed occupancy (patients admitted and not yet discharged)
        daily_patients['occupied_beds'] = patient_visits[
            patient_visits['admission_flag'] == True
        ].groupby('visit_date').size()
        daily_patients['occupied_beds'] = daily_patients['occupied_beds'].fillna(0)
        
        # 2. Aggregate weather data by date (average across locations)
        print("  Aggregating weather data...")
        daily_weather = weather.groupby('record_date').agg({
            'temperature_avg': 'mean',
            'temperature_min': 'min',
            'temperature_max': 'max',
            'humidity_percent': 'mean',
            'rainfall_mm': 'sum',
            'wind_speed_kmh': 'mean'
        }).rename(columns={
            'temperature_avg': 'temp_avg',
            'temperature_min': 'temp_min',
            'temperature_max': 'temp_max',
            'humidity_percent': 'humidity',
            'rainfall_mm': 'rainfall',
            'wind_speed_kmh': 'wind_speed'
        })
        
        # 3. Aggregate air quality data
        print("  Aggregating air quality data...")
        daily_aqi = air_quality.groupby('record_date').agg({
            'aqi_level': 'mean',
            'pm25': 'mean',
            'pm10': 'mean',
            'no2': 'mean',
            'so2': 'mean',
            'co': 'mean',
            'ozone': 'mean',
            'pollen_count': 'mean'
        }).rename(columns={
            'aqi_level': 'aqi',
            'pollen_count': 'pollen'
        })
        
        # 4. Process events (create daily flags)
        print("  Processing events...")
        date_range = pd.date_range(
            start=patient_visits['visit_date'].min(),
            end=patient_visits['visit_date'].max(),
            freq='D'
        )
        
        event_flags = pd.DataFrame(index=date_range)
        event_flags['is_holiday'] = 0
        event_flags['is_festival'] = 0
        event_flags['event_impact'] = 1.0
        
        for _, event in events.iterrows():
            mask = (event_flags.index >= event['start_date']) & (event_flags.index <= event['end_date'])
            if event['is_public_holiday']:
                event_flags.loc[mask, 'is_holiday'] = 1
            if event['event_type'] == 'festival':
                event_flags.loc[mask, 'is_festival'] = 1
            event_flags.loc[mask, 'event_impact'] = max(
                event_flags.loc[mask, 'event_impact'].values[0] if mask.sum() > 0 else 1.0,
                event['impact_multiplier']
            )
        
        # 5. Aggregate epidemic data
        print("  Aggregating epidemic surveillance...")
        daily_epidemic = epidemic.groupby('date').agg({
            'confirmed_cases': 'sum',
            'suspected_cases': 'sum',
            'deaths': 'sum'
        }).rename(columns={
            'confirmed_cases': 'epidemic_confirmed',
            'suspected_cases': 'epidemic_suspected',
            'deaths': 'epidemic_deaths'
        })
        
        # 6. Aggregate staff availability
        print("  Aggregating staff availability...")
        daily_staff = staff_avail.groupby('snapshot_date').agg({
            'doctors_available': 'sum',
            'nurses_available': 'sum',
            'technicians_available': 'sum'
        }).rename(columns={
            'doctors_available': 'total_doctors',
            'nurses_available': 'total_nurses',
            'technicians_available': 'total_technicians'
        })
        
        # 7. Aggregate supply inventory
        print("  Aggregating supply inventory...")
        daily_supply = supply_inv.groupby('snapshot_date').agg({
            'qty_on_hand': 'sum'
        }).rename(columns={
            'qty_on_hand': 'total_supply_qty'
        })
        
        # Count items below reorder level
        low_stock = supply_inv[supply_inv['qty_on_hand'] <= supply_inv['reorder_level']]
        daily_low_stock = low_stock.groupby('snapshot_date').size().to_frame('low_stock_items')
        
        # 8. Merge all datasets
        print("  Merging all datasets...")
        merged = daily_patients.join(daily_weather, how='outer')
        merged = merged.join(daily_aqi, how='outer')
        merged = merged.join(event_flags, how='outer')
        merged = merged.join(daily_epidemic, how='outer')
        merged = merged.join(daily_staff, how='outer')
        merged = merged.join(daily_supply, how='outer')
        merged = merged.join(daily_low_stock, how='outer')
        
        # Fill missing values
        merged = merged.fillna(0)
        
        # Add temporal features
        print("  Adding temporal features...")
        merged['day_of_week'] = merged.index.dayofweek
        merged['day_of_month'] = merged.index.day
        merged['month'] = merged.index.month
        merged['quarter'] = merged.index.quarter
        merged['year'] = merged.index.year
        merged['is_weekend'] = (merged.index.dayofweek >= 5).astype(int)
        merged['day_of_year'] = merged.index.dayofyear
        
        # Seasonal features
        merged['sin_day_of_year'] = np.sin(2 * np.pi * merged['day_of_year'] / 365)
        merged['cos_day_of_year'] = np.cos(2 * np.pi * merged['day_of_year'] / 365)
        
        print(f"+ Daily dataset created with {len(merged)} days of data")
        print(f"  Features: {len(merged.columns)} columns")
        
        return merged
    
    def create_features(self, target_column, lag_days=30, rolling_windows=[7, 14, 30]):
        """
        Create time series features for forecasting
        
        Parameters:
        - target_column: Column to forecast
        - lag_days: Number of lag features to create
        - rolling_windows: Window sizes for rolling statistics
        
        Returns:
        - DataFrame with engineered features
        """
        print(f"\nCreating features for {target_column}...")
        
        if self.daily_data is None:
            raise ValueError("Data not loaded. Call load_and_merge_data() first.")
        
        feature_data = self.daily_data.copy()
        
        # Lag features for target variable
        print(f"  Creating {lag_days} lag features...")
        for lag in range(1, lag_days + 1):
            feature_data[f'{target_column}_lag_{lag}'] = feature_data[target_column].shift(lag)
        
        # Rolling statistics for target variable
        print(f"  Creating rolling statistics for windows: {rolling_windows}...")
        for window in rolling_windows:
            feature_data[f'{target_column}_rolling_mean_{window}'] = \
                feature_data[target_column].rolling(window=window).mean()
            feature_data[f'{target_column}_rolling_std_{window}'] = \
                feature_data[target_column].rolling(window=window).std()
            feature_data[f'{target_column}_rolling_min_{window}'] = \
                feature_data[target_column].rolling(window=window).min()
            feature_data[f'{target_column}_rolling_max_{window}'] = \
                feature_data[target_column].rolling(window=window).max()
        
        # External factor interactions
        if 'is_holiday' in feature_data.columns:
            feature_data['holiday_weekend'] = feature_data['is_holiday'] * feature_data['is_weekend']
        
        if 'aqi' in feature_data.columns:
            feature_data['high_aqi'] = (feature_data['aqi'] > 150).astype(int)
            feature_data['very_high_aqi'] = (feature_data['aqi'] > 200).astype(int)
        
        if 'rainfall' in feature_data.columns:
            feature_data['heavy_rain'] = (feature_data['rainfall'] > 50).astype(int)
        
        # Drop rows with NaN values created by lag/rolling features
        initial_len = len(feature_data)
        feature_data = feature_data.dropna()
        print(f"  Dropped {initial_len - len(feature_data)} rows with NaN values")
        
        print(f"+ Feature engineering complete: {len(feature_data.columns)} features")
        
        return feature_data
    
    def get_train_test_split(self, feature_data, target_column, test_size=0.2, val_size=0.1):
        """
        Split data into train, validation, and test sets
        
        Parameters:
        - feature_data: DataFrame with features
        - target_column: Target variable name
        - test_size: Proportion of data for testing
        - val_size: Proportion of training data for validation
        
        Returns:
        - Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        # Exclude target and other target columns from features
        target_columns = ['total_patients', 'admissions', 'occupied_beds', 
                         'avg_severity', 'avg_wait_minutes']
        
        feature_cols = [col for col in feature_data.columns 
                       if col not in target_columns and not col.startswith('target_')]
        
        X = feature_data[feature_cols]
        y = feature_data[target_column]
        
        # Time series split (no shuffling)
        n = len(X)
        test_idx = int(n * (1 - test_size))
        val_idx = int(test_idx * (1 - val_size))
        
        X_train = X.iloc[:val_idx]
        X_val = X.iloc[val_idx:test_idx]
        X_test = X.iloc[test_idx:]
        
        y_train = y.iloc[:val_idx]
        y_val = y.iloc[val_idx:test_idx]
        y_test = y.iloc[test_idx:]
        
        print(f"\nData split:")
        print(f"  Training: {len(X_train)} samples ({len(X_train)/n*100:.1f}%)")
        print(f"  Validation: {len(X_val)} samples ({len(X_val)/n*100:.1f}%)")
        print(f"  Testing: {len(X_test)} samples ({len(X_test)/n*100:.1f}%)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test


def load_and_merge_data(data_dir='../media/hospital_data_csv'):
    """
    Convenience function to load and merge data
    
    Parameters:
    - data_dir: Directory containing CSV files
    
    Returns:
    - DataFrame with daily aggregated data
    """
    loader = HospitalDataLoader(data_dir)
    return loader.load_and_merge_data()


if __name__ == "__main__":
    # Test the data loader
    print("=" * 60)
    print("HOSPITAL DATA LOADER TEST")
    print("=" * 60)
    
    loader = HospitalDataLoader()
    daily_data = loader.load_and_merge_data()
    
    print("\n" + "=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    print(f"Date range: {daily_data.index.min()} to {daily_data.index.max()}")
    print(f"Total days: {len(daily_data)}")
    print(f"Total features: {len(daily_data.columns)}")
    print(f"\nFirst few rows:")
    print(daily_data.head())
    
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING TEST")
    print("=" * 60)
    feature_data = loader.create_features('total_patients', lag_days=7, rolling_windows=[7, 14])
    print(f"\nFeature data shape: {feature_data.shape}")
    
    # Test train/test split
    X_train, X_val, X_test, y_train, y_val, y_test = loader.get_train_test_split(
        feature_data, 'total_patients'
    )
    
    print("\n+ Data loader test completed successfully!")
