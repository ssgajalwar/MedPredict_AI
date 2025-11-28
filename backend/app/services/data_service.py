import pandas as pd
import os
from pathlib import Path
from typing import Dict, List

class DataService:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent.parent / "media"
        self.data_path = self.base_path / "data" / "hospital_data"
        
    def get_latest_patient_data(self) -> Dict:
        """Fetch latest patient visit data"""
        try:
            df = pd.read_csv(self.data_path / "patient_visits.csv")
            df['visit_date'] = pd.to_datetime(df['visit_date'])
            
            # Get latest data
            latest_date = df['visit_date'].max()
            latest_data = df[df['visit_date'] == latest_date]
            
            # Count admissions (severity proxy)
            admissions = latest_data[latest_data['admission_flag'] == True] if 'admission_flag' in latest_data.columns else pd.DataFrame()
            
            return {
                "total_patients": len(latest_data),
                "latest_date": latest_date.strftime("%Y-%m-%d"),
                "admissions": len(admissions),
                "by_department": latest_data.groupby('department_id').size().to_dict()
            }
        except Exception as e:
            print(f"Error loading patient data: {e}")
            return {"total_patients": 0, "latest_date": None}
    
    def get_weather_data(self) -> Dict:
        """Fetch latest weather/AQI data"""
        try:
            weather_df = pd.read_csv(self.data_path / "weather_data.csv")
            aqi_df = pd.read_csv(self.data_path / "air_quality_data.csv")
            
            # Get latest records
            latest_weather = weather_df.iloc[-1]
            latest_aqi = aqi_df.iloc[-1]
            
            return {
                "aqi": int(latest_aqi.get('aqi', 3)),
                "pm2_5": float(latest_aqi.get('pm2_5', 150)),
                "pm10": float(latest_aqi.get('pm10', 200)),
                "temp": float(latest_weather.get('temperature', 30)),
                "humidity": int(latest_weather.get('humidity', 70)),
                "description": latest_weather.get('weather_condition', 'Clear')
            }
        except Exception as e:
            print(f"Error loading weather data: {e}")
            return {
                "aqi": 3,
                "pm2_5": 150.0,
                "pm10": 200.0,
                "temp": 30.0,
                "humidity": 70,
                "description": "Data unavailable"
            }
    
    def get_events_data(self) -> List[Dict]:
        """Fetch upcoming events"""
        try:
            df = pd.read_csv(self.data_path / "events.csv")
            df['event_date'] = pd.to_datetime(df['event_date'])
            
            # Get upcoming events
            today = pd.Timestamp.now()
            upcoming = df[df['event_date'] >= today].sort_values('event_date').head(5)
            
            events = []
            for _, row in upcoming.iterrows():
                days_until = (row['event_date'] - today).days
                events.append({
                    "name": row['event_name'],
                    "date": row['event_date'].strftime("%Y-%m-%d"),
                    "days_until": int(days_until),
                    "impact": row.get('impact_level', 'medium'),
                    "type": row.get('event_type', 'festival')
                })
            
            return events
        except Exception as e:
            print(f"Error loading events data: {e}")
            return []
    
    def get_staff_data(self) -> Dict:
        """Fetch staff availability data"""
        try:
            staff_df = pd.read_csv(self.data_path / "staff.csv")
            availability_df = pd.read_csv(self.data_path / "staff_availability.csv")
            
            total_staff = len(staff_df)
            
            # Calculate available staff from latest snapshot
            if len(availability_df) > 0:
                availability_df['snapshot_date'] = pd.to_datetime(availability_df['snapshot_date'])
                latest_snapshot = availability_df[availability_df['snapshot_date'] == availability_df['snapshot_date'].max()]
                
                # Sum all available staff types
                available_staff = (
                    latest_snapshot['doctors_available'].sum() +
                    latest_snapshot['nurses_available'].sum() +
                    latest_snapshot['technicians_available'].sum()
                )
            else:
                available_staff = 0
            
            return {
                "total_staff": total_staff,
                "available_staff": int(available_staff),
                "by_role": staff_df.groupby('role').size().to_dict() if 'role' in staff_df.columns else {}
            }
        except Exception as e:
            print(f"Error loading staff data: {e}")
            return {"total_staff": 0, "available_staff": 0}
    
    def get_inventory_data(self) -> Dict:
        """Fetch inventory data"""
        try:
            df = pd.read_csv(self.data_path / "supply_inventory.csv")
            
            # Get latest snapshot
            df['snapshot_date'] = pd.to_datetime(df['snapshot_date'])
            latest_date = df['snapshot_date'].max()
            latest_inventory = df[df['snapshot_date'] == latest_date]
            
            # Check for critical items (qty_on_hand < reorder_level)
            critical_items = latest_inventory[latest_inventory['qty_on_hand'] < latest_inventory['reorder_level']]
            
            return {
                "total_items": len(latest_inventory),
                "critical_count": len(critical_items),
                "critical_items": critical_items['item_name'].tolist() if len(critical_items) > 0 else []
            }
        except Exception as e:
            print(f"Error loading inventory data: {e}")
            return {"total_items": 0, "critical_count": 0, "critical_items": []}

data_service = DataService()
