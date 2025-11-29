"""
Prepare Training Data for Model 3: Severity Classification
This script aggregates daily severity metrics and defines alert levels (Normal/Alert/Critical).
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

def prepare_severity_data(data_dir='media/hospital_data_csv', output_dir='media/modal_train_data'):
    print("="*60)
    print("MODEL 3 DATA PREPARATION (Severity Classification)")
    print("="*60)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load Data
    print("\n[1/5] Loading data...")
    patient_visits = pd.read_csv(f'{data_dir}/patient_visits.csv', parse_dates=['visit_date'])
    surveillance = pd.read_csv(f'{data_dir}/epidemic_surveillance.csv', parse_dates=['date'])
    weather = pd.read_csv(f'{data_dir}/weather_data.csv', parse_dates=['record_date'])
    air_quality = pd.read_csv(f'{data_dir}/air_quality_data.csv', parse_dates=['record_date'])
    events = pd.read_csv(f'{data_dir}/events.csv', parse_dates=['start_date', 'end_date'])
    
    # 2. Aggregate Patient Data (Daily Severity & Volume)
    print("\n[2/5] Aggregating patient metrics...")
    daily_patient_metrics = patient_visits.groupby('visit_date').agg({
        'visit_id': 'count',
        'severity_level': 'mean'
    }).reset_index()
    daily_patient_metrics.rename(columns={
        'visit_date': 'date', 
        'visit_id': 'total_daily_patient_count',
        'severity_level': 'average_daily_severity'
    }, inplace=True)
    
    # 3. Aggregate Surveillance Data
    print("\n[3/5] Aggregating surveillance data...")
    daily_surveillance = surveillance.groupby('date').agg({
        'confirmed_cases': 'sum',
        'suspected_cases': 'sum',
        'deaths': 'sum'
    }).reset_index()
    daily_surveillance.rename(columns={
        'confirmed_cases': 'total_confirmed_cases',
        'suspected_cases': 'total_suspected_cases',
        'deaths': 'total_deaths'
    }, inplace=True)
    
    # 4. Process Events
    daily_event_records = []
    for _, event in events.iterrows():
        current = event['start_date']
        while current <= event['end_date']:
            daily_event_records.append({
                'date': current,
                'is_public_holiday': event['is_public_holiday'],
                'event_impact_multiplier': event['impact_multiplier']
            })
            current += pd.Timedelta(days=1)
            
    daily_events = pd.DataFrame(daily_event_records)
    if not daily_events.empty:
        daily_events = daily_events.groupby('date').agg({
            'is_public_holiday': 'max', 
            'event_impact_multiplier': 'max'
        }).reset_index()
        
    # 5. Merge All Data
    print("\n[4/5] Merging all datasets...")
    merged_df = daily_patient_metrics.copy()
    
    merged_df = pd.merge(merged_df, daily_surveillance, on='date', how='left').fillna(0)
    
    weather.rename(columns={'record_date': 'date'}, inplace=True)
    merged_df = pd.merge(merged_df, weather, on='date', how='left')
    
    air_quality.rename(columns={'record_date': 'date'}, inplace=True)
    merged_df = pd.merge(merged_df, air_quality, on='date', how='left')
    
    if not daily_events.empty:
        merged_df = pd.merge(merged_df, daily_events, on='date', how='left')
        
    merged_df['is_public_holiday'] = merged_df['is_public_holiday'].fillna(False).astype(int)
    merged_df['event_impact_multiplier'] = merged_df['event_impact_multiplier'].fillna(1.0)
    
    # 6. Define Target: Daily Alert Level
    # Logic: 
    # - Critical: High severity OR High cases OR High volume
    # - Alert: Moderate severity/cases/volume
    # - Normal: Otherwise
    
    print("\n[5/5] Defining alert levels...")
    
    # Calculate thresholds (using quantiles for dynamic thresholds)
    vol_q75 = merged_df['total_daily_patient_count'].quantile(0.75)
    vol_q90 = merged_df['total_daily_patient_count'].quantile(0.90)
    
    sev_q75 = merged_df['average_daily_severity'].quantile(0.75)
    sev_q90 = merged_df['average_daily_severity'].quantile(0.90)
    
    cases_q75 = merged_df['total_confirmed_cases'].quantile(0.75)
    cases_q90 = merged_df['total_confirmed_cases'].quantile(0.90)
    
    def get_alert_level(row):
        if (row['total_daily_patient_count'] > vol_q90) or \
           (row['average_daily_severity'] > sev_q90) or \
           (row['total_confirmed_cases'] > cases_q90):
            return 'Critical'
        elif (row['total_daily_patient_count'] > vol_q75) or \
             (row['average_daily_severity'] > sev_q75) or \
             (row['total_confirmed_cases'] > cases_q75):
            return 'Alert'
        else:
            return 'Normal'
            
    merged_df['daily_alert_level'] = merged_df.apply(get_alert_level, axis=1)
    
    # Time Features
    merged_df['day_of_week'] = merged_df['date'].dt.dayofweek
    merged_df['month'] = merged_df['date'].dt.month
    merged_df['day_of_year'] = merged_df['date'].dt.dayofyear
    merged_df['week_of_year'] = merged_df['date'].dt.isocalendar().week.astype(int)
    merged_df['quarter'] = merged_df['date'].dt.quarter
    merged_df['is_weekend'] = (merged_df['date'].dt.dayofweek >= 5).astype(int)
    
    # Save
    output_path = f'{output_dir}/severity_training_data.csv'
    merged_df.to_csv(output_path, index=False)
    print(f"\n✓ Saved to {output_path}")
    print(f"  Shape: {merged_df.shape}")
    print(f"  Alert Distribution:\n{merged_df['daily_alert_level'].value_counts()}")
    
    return merged_df

if __name__ == "__main__":
    prepare_severity_data()
