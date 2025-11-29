"""
Validate Data Realism

This script analyzes the generated hospital data to verify it matches 
the expected Mumbai seasonal trends and Lilavati Hospital profile.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

def validate_realism(data_dir='../media/hospital_data_csv'):
    print("=" * 60)
    print("DATA REALISM VALIDATION (MUMBAI/LILAVATI)")
    print("=" * 60)
    
    # Load data
    try:
        visits_df = pd.read_csv(os.path.join(data_dir, 'patient_visits.csv'))
        hospitals_df = pd.read_csv(os.path.join(data_dir, 'hospitals.csv'))
    except FileNotFoundError:
        print("❌ Data files not found. Run the pipeline first.")
        return
    
    # 1. Validate Hospital Profile
    print("\n[1] Validating Hospital Profile (Lilavati)")
    lilavati = hospitals_df[hospitals_df['hospital_name'].str.contains('Lilavati')]
    
    if not lilavati.empty:
        beds = lilavati.iloc[0]['total_beds']
        print(f"  ✓ Hospital Found: {lilavati.iloc[0]['hospital_name']}")
        print(f"  ✓ Bed Count: {beds} (Expected: 350)")
        if beds == 350:
            print("  ✅ Bed count matches configured profile.")
        else:
            print("  ⚠ Bed count mismatch.")
    else:
        print("  ❌ Lilavati Hospital not found in data.")
        
    # 2. Validate Seasonality (Malaria/Dengue)
    print("\n[2] Validating Monsoon Seasonality (Vector-Borne)")
    visits_df['visit_date'] = pd.to_datetime(visits_df['visit_date'])
    visits_df['month'] = visits_df['visit_date'].dt.month
    
    vector_borne = visits_df[visits_df['diagnosis_summary'].isin(['Dengue Fever', 'Malaria'])]
    monthly_counts = vector_borne.groupby('month').size()
    
    monsoon_avg = monthly_counts[monthly_counts.index.isin([6, 7, 8, 9])].mean()
    non_monsoon_avg = monthly_counts[~monthly_counts.index.isin([6, 7, 8, 9])].mean()
    
    print(f"  ✓ Monsoon Avg Cases (Jun-Sep): {monsoon_avg:.0f}")
    print(f"  ✓ Non-Monsoon Avg Cases: {non_monsoon_avg:.0f}")
    
    ratio = monsoon_avg / non_monsoon_avg if non_monsoon_avg > 0 else 0
    print(f"  ✓ Seasonal Ratio: {ratio:.1f}x")
    
    if ratio > 2.0:
        print("  ✅ Strong monsoon spike detected (Matches Mumbai trends).")
    else:
        print("  ⚠ Weak seasonality detected.")

    # 3. Validate Respiratory Seasonality
    print("\n[3] Validating Winter Seasonality (Respiratory)")
    respiratory = visits_df[visits_df['diagnosis_summary'].isin(['Asthma', 'Pneumonia'])]
    resp_monthly = respiratory.groupby('month').size()
    
    winter_avg = resp_monthly[resp_monthly.index.isin([11, 12, 1])].mean()
    other_avg = resp_monthly[~resp_monthly.index.isin([11, 12, 1])].mean()
    
    print(f"  ✓ Winter Avg Cases (Nov-Jan): {winter_avg:.0f}")
    print(f"  ✓ Other Months Avg Cases: {other_avg:.0f}")
    
    resp_ratio = winter_avg / other_avg if other_avg > 0 else 0
    print(f"  ✓ Seasonal Ratio: {resp_ratio:.1f}x")
    
    if resp_ratio > 1.5:
        print("  ✅ Winter spike detected (Matches Mumbai AQI trends).")
    else:
        print("  ⚠ Weak respiratory seasonality.")

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    # Check if path argument provided
    path = sys.argv[1] if len(sys.argv) > 1 else '../media/hospital_data_csv'
    validate_realism(path)
