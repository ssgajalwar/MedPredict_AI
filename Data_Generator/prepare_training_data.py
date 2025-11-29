import pandas as pd
import numpy as np
import os

def prepare_model1_training_data(data_dir='media/hospital_data_csv', output_file='media/modal_train_data/training_data.csv'):
    """
    Prepare training data for Patient Volume Forecasting
    
    This function:
    1. Aggregates patient visits by date (daily patient count)
    2. Merges with weather, AQI, and event data
    3. Engineers time-based features (day of week, month, holidays)
    4. Saves the final dataset
    """
    print("="*60)
    print("PREPARING TRAINING DATA")
    print("Patient Volume Forecasting")
    print("="*60)
    
    # Load data
    print("\n[1/5] Loading data...")
    patient_visits_df = pd.read_csv(os.path.join(data_dir, 'patient_visits.csv'))
    weather_df = pd.read_csv(os.path.join(data_dir, 'weather_data.csv'))
    aqi_df = pd.read_csv(os.path.join(data_dir, 'air_quality_data.csv'))
    events_df = pd.read_csv(os.path.join(data_dir, 'events.csv'))
    
    print(f"  ✓ Loaded patient_visits: {len(patient_visits_df):,} rows")
    print(f"  ✓ Loaded weather_data: {len(weather_df):,} rows")
    print(f"  ✓ Loaded air_quality_data: {len(aqi_df):,} rows")
    print(f"  ✓ Loaded events: {len(events_df):,} rows")

    # Convert date columns to datetime
    print("\n[2/5] Converting date columns...")
    patient_visits_df['visit_date'] = pd.to_datetime(patient_visits_df['visit_date'])
    weather_df['record_date'] = pd.to_datetime(weather_df['record_date'])
    aqi_df['record_date'] = pd.to_datetime(aqi_df['record_date'])
    events_df['start_date'] = pd.to_datetime(events_df['start_date'])
    events_df['end_date'] = pd.to_datetime(events_df['end_date'])

    # Aggregate patient visits by date (daily patient count)
    print("\n[3/5] Aggregating patient visits by date...")
    daily_visits = patient_visits_df.groupby('visit_date').agg({
        'visit_id': 'count',  # Total patient count
        'admission_flag': 'sum',  # Number of admissions
        'severity_level': 'mean',  # Average severity
        'wait_minutes': 'mean'  # Average wait time
    }).reset_index()
    
    daily_visits.columns = ['date', 'patient_volume', 'admissions_count', 'avg_severity', 'avg_wait_minutes']
    print(f"  ✓ Aggregated to {len(daily_visits):,} daily records")
    
    # Merge with weather data
    print("\n[4/5] Merging with weather and AQI data...")
    merged_df = pd.merge(daily_visits, weather_df, left_on='date', right_on='record_date', how='left')
    merged_df = pd.merge(merged_df, aqi_df, left_on='date', right_on='record_date', how='left')
    
    # Drop redundant columns
    merged_df.drop(columns=['record_date_x', 'record_date_y', 'location_id_x', 'location_id_y'], inplace=True, errors='ignore')
    
    # Engineer time-based features
    print("\n[5/5] Engineering time-based features...")
    merged_df['day_of_week'] = merged_df['date'].dt.dayofweek  # Monday=0, Sunday=6
    merged_df['day_name'] = merged_df['date'].dt.day_name()
    merged_df['month'] = merged_df['date'].dt.month
    merged_df['month_name'] = merged_df['date'].dt.month_name()
    merged_df['year'] = merged_df['date'].dt.year
    merged_df['day_of_month'] = merged_df['date'].dt.day
    merged_df['week_of_year'] = merged_df['date'].dt.isocalendar().week
    merged_df['quarter'] = merged_df['date'].dt.quarter
    merged_df['is_weekend'] = merged_df['day_of_week'].isin([5, 6]).astype(int)
    merged_df['is_month_start'] = merged_df['date'].dt.is_month_start.astype(int)
    merged_df['is_month_end'] = merged_df['date'].dt.is_month_end.astype(int)
    
    # Event features (holidays, event impact)
    merged_df['is_holiday'] = 0
    merged_df['event_impact'] = 1.0
    merged_df['event_name'] = ''
    
    # Iterate through events to mark holidays and impact
    for _, event in events_df.iterrows():
        mask = (merged_df['date'] >= event['start_date']) & (merged_df['date'] <= event['end_date'])
        if event['is_public_holiday']:
            merged_df.loc[mask, 'is_holiday'] = 1
        
        # Take the max impact if multiple events overlap
        current_impacts = merged_df.loc[mask, 'event_impact']
        new_impact = event['impact_multiplier']
        merged_df.loc[mask, 'event_impact'] = np.maximum(current_impacts, new_impact)
        
        # Concatenate event names for overlapping events
        for idx in merged_df[mask].index:
            if merged_df.loc[idx, 'event_name']:
                merged_df.loc[idx, 'event_name'] += f"; {event['event_name']}"
            else:
                merged_df.loc[idx, 'event_name'] = event['event_name']
    
    # Seasonal indicators
    merged_df['is_monsoon'] = merged_df['month'].isin([6, 7, 8, 9]).astype(int)
    merged_df['is_winter'] = merged_df['month'].isin([11, 12, 1, 2]).astype(int)
    merged_df['is_summer'] = merged_df['month'].isin([3, 4, 5]).astype(int)
    
    # Fill any missing values
    print("\n  Handling missing values...")
    numeric_columns = merged_df.select_dtypes(include=[np.number]).columns
    merged_df[numeric_columns] = merged_df[numeric_columns].fillna(method='ffill').fillna(method='bfill')
    
    # Sort by date
    merged_df.sort_values('date', inplace=True)
    merged_df.reset_index(drop=True, inplace=True)
    
    # Save the result
    print(f"\n[SAVE] Saving training data to {output_file}...")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    merged_df.to_csv(output_file, index=False)
    
    print("\n" + "="*60)
    print("TRAINING DATA PREPARATION COMPLETE")
    print("="*60)
    print(f"  Output file: {output_file}")
    print(f"  Total rows: {len(merged_df):,}")
    print(f"  Total columns: {len(merged_df.columns)}")
    print(f"  Date range: {merged_df['date'].min()} to {merged_df['date'].max()}")
    print(f"  Avg daily patients: {merged_df['patient_volume'].mean():.1f}")
    print(f"  Max daily patients: {merged_df['patient_volume'].max()}")
    print(f"  Min daily patients: {merged_df['patient_volume'].min()}")
    
    # Display sample
    print("\nSample of prepared data (first 5 rows):")
    print(merged_df.head().to_string())
    
    print("\nColumn names:")
    for i, col in enumerate(merged_df.columns, 1):
        print(f"  {i}. {col}")
    
    return merged_df

if __name__ == "__main__":
    prepare_model1_training_data()
