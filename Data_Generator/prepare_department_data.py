"""
Prepare Training Data for Model 2: Department-wise Patient Volume Forecasting
This script aggregates patient visits by department and merges with environmental/event data.
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

def prepare_department_data(data_dir='media/hospital_data_csv', output_dir='media/modal_train_data'):
    print("="*60)
    print("MODEL 2 DATA PREPARATION (Department-wise)")
    print("="*60)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load Data
    print("\n[1/5] Loading data...")
    patient_visits = pd.read_csv(f'{data_dir}/patient_visits.csv', parse_dates=['visit_date'])
    departments = pd.read_csv(f'{data_dir}/departments.csv')
    weather = pd.read_csv(f'{data_dir}/weather_data.csv', parse_dates=['record_date'])
    air_quality = pd.read_csv(f'{data_dir}/air_quality_data.csv', parse_dates=['record_date'])
    events = pd.read_csv(f'{data_dir}/events.csv', parse_dates=['start_date', 'end_date'])
    
    print(f"  ✓ Loaded {len(patient_visits)} visits, {len(departments)} departments")
    
    # 2. Aggregate by Date and Department
    print("\n[2/5] Aggregating by department...")
    daily_dept_counts = patient_visits.groupby(['visit_date', 'department_id']).size().reset_index(name='patient_count')
    
    # Pivot to get one column per department
    # First, map department IDs to names or codes for better column names
    dept_map = dict(zip(departments['department_id'], departments['department_name']))
    daily_dept_counts['dept_name'] = daily_dept_counts['department_id'].map(dept_map)
    
    # Clean department names for column headers
    daily_dept_counts['dept_col'] = daily_dept_counts['dept_name'].str.replace(' ', '_').str.lower().str.replace('&', 'and')
    
    # Pivot
    pivoted_df = daily_dept_counts.pivot(index='visit_date', columns='dept_col', values='patient_count').fillna(0)
    pivoted_df.reset_index(inplace=True)
    pivoted_df.rename(columns={'visit_date': 'date'}, inplace=True)
    
    print(f"  ✓ Pivoted shape: {pivoted_df.shape}")
    
    # 3. Process Events (Daily Expansion)
    print("\n[3/5] Processing events...")
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
    
    # 4. Merge Data
    print("\n[4/5] Merging environmental and event data...")
    merged_df = pivoted_df.copy()
    
    # Merge Weather
    weather.rename(columns={'record_date': 'date'}, inplace=True)
    merged_df = pd.merge(merged_df, weather, on='date', how='left')
    
    # Merge AQI
    air_quality.rename(columns={'record_date': 'date'}, inplace=True)
    merged_df = pd.merge(merged_df, air_quality, on='date', how='left')
    
    # Merge Events
    if not daily_events.empty:
        merged_df = pd.merge(merged_df, daily_events, on='date', how='left')
    
    # Fill NaNs
    merged_df['is_public_holiday'] = merged_df['is_public_holiday'].fillna(False).astype(int)
    merged_df['event_impact_multiplier'] = merged_df['event_impact_multiplier'].fillna(1.0)
    
    # 5. Feature Engineering
    print("\n[5/5] Engineering time features...")
    merged_df['day_of_week'] = merged_df['date'].dt.dayofweek
    merged_df['month'] = merged_df['date'].dt.month
    merged_df['day_of_year'] = merged_df['date'].dt.dayofyear
    merged_df['week_of_year'] = merged_df['date'].dt.isocalendar().week.astype(int)
    merged_df['quarter'] = merged_df['date'].dt.quarter
    merged_df['is_weekend'] = (merged_df['date'].dt.dayofweek >= 5).astype(int)
    
    # Save
    output_path = f'{output_dir}/department_training_data.csv'
    merged_df.to_csv(output_path, index=False)
    print(f"\n✓ Saved to {output_path}")
    print(f"  Shape: {merged_df.shape}")
    
    return merged_df

if __name__ == "__main__":
    prepare_department_data()
