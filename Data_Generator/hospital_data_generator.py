import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class HospitalProfile:
    """Base profile for hospital configuration"""
    def __init__(self, name, beds, daily_opd, type="Private", city="Mumbai"):
        self.name = name
        self.beds = beds
        self.daily_opd = daily_opd
        self.type = type
        self.city = city

class LilavatiHospitalProfile(HospitalProfile):
    """Specific profile for Lilavati Hospital, Mumbai"""
    def __init__(self):
        super().__init__(
            name="Lilavati Hospital",
            beds=323,
            daily_opd=1500,
            type="Private",
            city="Mumbai"
        )

class SeasonalityEngine:
    """Engine to apply Mumbai-specific seasonal trends"""
    
    @staticmethod
    def get_disease_multiplier(date, disease_category):
        """
        Get multiplier for disease incidence based on date and category.
        Based on Mumbai health trends (Monsoon Malaria, Winter Respiratory).
        """
        month = date.month
        
        if disease_category == "Vector-Borne": # Malaria, Dengue
            # Peak in Monsoon (June-Sept) and post-monsoon (Oct)
            if month in [6, 7, 8, 9]:
                return 3.5  # Massive spike during monsoon
            elif month in [10]:
                return 2.0  # Tapering off
            else:
                return 0.5  # Low during dry season
                
        elif disease_category == "Respiratory": # Asthma, Pneumonia
            # Peak in Winter (Nov-Jan) due to smog/AQI
            if month in [11, 12, 1]:
                return 2.5
            else:
                return 0.8
                
        elif disease_category == "Water-Borne": # Typhoid, Gastroenteritis
            # Peak in Monsoon (July-Aug)
            if month in [7, 8]:
                return 3.0
            else:
                return 0.6
                
        return 1.0

class ComprehensiveHospitalDataGenerator:
    """
    Comprehensive hospital data generator matching the complete database schema.
    Generates data for all 12 tables with Indian context (Mumbai focus).
    """
    
    def __init__(self, start_date="2022-01-01", end_date="2024-11-22", random_seed=42, profile=None):
        """
        Initialize the comprehensive hospital data generator
        
        Parameters:
        - start_date: Start date for data generation
        - end_date: End date for data generation
        - random_seed: Random seed for reproducibility
        - profile: HospitalProfile instance (defaults to LilavatiHospitalProfile)
        """
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.random_seed = random_seed
        self.profile = profile if profile else LilavatiHospitalProfile()
        
        np.random.seed(random_seed)
        random.seed(random_seed)
        
        # Data storage
        self.data = {}
        
        # Master data references (will be populated during generation)
        self.locations = []
        self.hospitals = []
        self.departments = []
        self.staff_list = []
        
        print(f"Initialized Generator with Profile: {self.profile.name} ({self.profile.beds} beds)")
        
    def generate_locations(self) -> pd.DataFrame:
        """Generate locations table - major Indian cities with focus on Mumbai"""
        locations_data = [
            {
                'location_id': 1,
                'name': 'Mumbai Central',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'region': 'West',
                'latitude': 19.0176,
                'longitude': 72.8562,
                'population': 12442373,
                'urban_rural': 'Urban'
            },
            {
                'location_id': 2,
                'name': 'Mumbai Suburban',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'region': 'West',
                'latitude': 19.1136,
                'longitude': 72.8697,
                'population': 9356962,
                'urban_rural': 'Urban'
            },
            {
                'location_id': 3,
                'name': 'Thane',
                'city': 'Thane',
                'state': 'Maharashtra',
                'region': 'West',
                'latitude': 19.2183,
                'longitude': 72.9781,
                'population': 1841488,
                'urban_rural': 'Urban'
            },
            {
                'location_id': 4,
                'name': 'Pune',
                'city': 'Pune',
                'state': 'Maharashtra',
                'region': 'West',
                'latitude': 18.5204,
                'longitude': 73.8567,
                'population': 3124458,
                'urban_rural': 'Urban'
            },
            {
                'location_id': 5,
                'name': 'Nashik',
                'city': 'Nashik',
                'state': 'Maharashtra',
                'region': 'West',
                'latitude': 19.9975,
                'longitude': 73.7898,
                'population': 1486053,
                'urban_rural': 'Urban'
            }
        ]
        
        df = pd.DataFrame(locations_data)
        self.locations = locations_data
        return df
    
    def generate_hospitals(self) -> pd.DataFrame:
        """Generate hospitals table - Single hospital based on profile"""
        hospitals_data = []
        
        # We only generate one hospital for the target profile
        location = [l for l in self.locations if l['city'] == self.profile.city][0]
        
        hospitals_data.append({
            'hospital_id': 1,
            'hospital_name': self.profile.name,
            'location_id': location['location_id'],
            'hospital_type': self.profile.type,
            'total_beds': self.profile.beds,
            'address': f"A-791, Bandra Reclamation, Bandra West, {location['city']}, {location['state']} 400050",
            'contact_phone': "+91-22-26751000" # Real Lilavati phone prefix
        })
        
        df = pd.DataFrame(hospitals_data)
        self.hospitals = hospitals_data
        return df
    
    def generate_departments(self) -> pd.DataFrame:
        """Generate departments table - departments for each hospital"""
        departments_data = []
        department_id = 1
        
        department_templates = [
            {'code': 'ER', 'name': 'Emergency Room', 'floor': 0},
            {'code': 'CARD', 'name': 'Cardiology', 'floor': 2},
            {'code': 'ORTHO', 'name': 'Orthopedics', 'floor': 3},
            {'code': 'PEDS', 'name': 'Pediatrics', 'floor': 1},
            {'code': 'OB', 'name': 'Obstetrics', 'floor': 4},
            {'code': 'ICU', 'name': 'Intensive Care Unit', 'floor': 5},
            {'code': 'SURG', 'name': 'General Surgery', 'floor': 3},
            {'code': 'MED', 'name': 'Internal Medicine', 'floor': 2},
            {'code': 'RESP', 'name': 'Respiratory Medicine', 'floor': 2},
            {'code': 'ENDO', 'name': 'Endocrinology', 'floor': 1}
        ]
        
        for hospital in self.hospitals:
            # Each hospital gets 6-10 departments
            num_depts = random.randint(6, 10)
            selected_depts = random.sample(department_templates, num_depts)
            
            for dept_template in selected_depts:
                departments_data.append({
                    'department_id': department_id,
                    'hospital_id': hospital['hospital_id'],
                    'department_code': f"{dept_template['code']}-H{hospital['hospital_id']}-D{department_id}",
                    'department_name': dept_template['name'],
                    'floor_number': dept_template['floor'],
                    'head_doctor_id': None,  # Will be populated after staff generation
                    'contact_ext': f"x{random.randint(1000, 9999)}"
                })
                department_id += 1
        
        df = pd.DataFrame(departments_data)
        self.departments = departments_data
        return df
    
    def generate_staff(self) -> pd.DataFrame:
        """Generate staff table - doctors, nurses, technicians, admin"""
        staff_data = []
        staff_id = 1
        
        first_names = ['Rajesh', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anjali', 'Rahul', 'Kavita', 
                       'Suresh', 'Meera', 'Arjun', 'Pooja', 'Nitin', 'Deepa', 'Karan', 'Ritu']
        last_names = ['Sharma', 'Patel', 'Kumar', 'Singh', 'Desai', 'Mehta', 'Gupta', 'Reddy',
                      'Iyer', 'Joshi', 'Nair', 'Rao', 'Kulkarni', 'Chopra', 'Malhotra', 'Verma']
        
        roles = [
            {'role': 'doctor', 'count_per_hospital': 30, 'specialties': ['Cardiology', 'Orthopedics', 'Pediatrics', 'General Medicine', 'Surgery']},
            {'role': 'nurse', 'count_per_hospital': 80, 'specialties': ['ICU', 'ER', 'General', 'Pediatric']},
            {'role': 'technician', 'count_per_hospital': 25, 'specialties': ['Radiology', 'Lab', 'Respiratory', 'Cardiac']},
            {'role': 'admin', 'count_per_hospital': 15, 'specialties': ['Reception', 'Billing', 'Records', 'Management']}
        ]
        
        for hospital in self.hospitals:
            for role_config in roles:
                for _ in range(role_config['count_per_hospital']):
                    staff_data.append({
                        'staff_id': staff_id,
                        'hospital_id': hospital['hospital_id'],
                        'first_name': random.choice(first_names),
                        'last_name': random.choice(last_names),
                        'role': role_config['role'],
                        'specialty': random.choice(role_config['specialties']),
                        'phone': f"+91-{random.randint(7000000000, 9999999999)}",
                        'email': f"staff{staff_id}@hospital{hospital['hospital_id']}.in"
                    })
                    staff_id += 1
        
        df = pd.DataFrame(staff_data)
        self.staff_list = staff_data
        return df
    
    def generate_weather_data(self) -> pd.DataFrame:
        """Generate weather_data table - daily weather per location"""
        weather_data = []
        
        for location in self.locations:
            current_date = self.start_date
            
            while current_date <= self.end_date:
                month = current_date.month
                
                # Mumbai weather patterns
                if month in [12, 1, 2]:  # Winter
                    temp_avg = np.random.normal(25, 3)
                    temp_min = temp_avg - np.random.uniform(3, 5)
                    temp_max = temp_avg + np.random.uniform(4, 6)
                    humidity = np.random.normal(60, 10)
                    rainfall = np.random.exponential(2) if random.random() < 0.1 else 0
                elif month in [3, 4, 5]:  # Summer
                    temp_avg = np.random.normal(32, 4)
                    temp_min = temp_avg - np.random.uniform(4, 6)
                    temp_max = temp_avg + np.random.uniform(5, 8)
                    humidity = np.random.normal(70, 12)
                    rainfall = np.random.exponential(5) if random.random() < 0.15 else 0
                elif month in [6, 7, 8, 9]:  # Monsoon
                    temp_avg = np.random.normal(28, 3)
                    temp_min = temp_avg - np.random.uniform(2, 4)
                    temp_max = temp_avg + np.random.uniform(3, 5)
                    humidity = np.random.normal(85, 8)
                    rainfall = np.random.exponential(50) if random.random() < 0.7 else 0
                else:  # Post-monsoon
                    temp_avg = np.random.normal(29, 3)
                    temp_min = temp_avg - np.random.uniform(3, 5)
                    temp_max = temp_avg + np.random.uniform(4, 6)
                    humidity = np.random.normal(75, 10)
                    rainfall = np.random.exponential(10) if random.random() < 0.2 else 0
                
                weather_data.append({
                    'location_id': location['location_id'],
                    'record_date': current_date.date(),
                    'temperature_avg': round(temp_avg, 2),
                    'temperature_min': round(temp_min, 2),
                    'temperature_max': round(temp_max, 2),
                    'humidity_percent': round(max(30, min(100, humidity)), 2),
                    'rainfall_mm': round(max(0, rainfall), 2),
                    'wind_speed_kmh': round(np.random.normal(15, 5), 2)
                })
                
                current_date += timedelta(days=1)
        
        return pd.DataFrame(weather_data)
    
    def generate_air_quality_data(self) -> pd.DataFrame:
        """Generate air_quality_data table - daily AQI per location"""
        aqi_data = []
        
        for location in self.locations:
            current_date = self.start_date
            
            while current_date <= self.end_date:
                month = current_date.month
                
                # Mumbai AQI patterns - worse in winter, better in monsoon
                if month in [11, 12, 1, 2]:  # Winter - high pollution
                    aqi_base = 180
                elif month in [6, 7, 8, 9]:  # Monsoon - better air quality
                    aqi_base = 80
                else:
                    aqi_base = 120
                
                aqi_level = int(max(0, min(500, np.random.normal(aqi_base, 40))))
                
                # Pollutant levels correlated with AQI
                pm25 = round(aqi_level * 0.4 + np.random.normal(0, 10), 2)
                pm10 = round(aqi_level * 0.6 + np.random.normal(0, 15), 2)
                
                aqi_data.append({
                    'location_id': location['location_id'],
                    'record_date': current_date.date(),
                    'aqi_level': aqi_level,
                    'pm25': max(0, pm25),
                    'pm10': max(0, pm10),
                    'no2': round(np.random.normal(40, 15), 2),
                    'so2': round(np.random.normal(15, 8), 2),
                    'co': round(np.random.normal(1.2, 0.5), 2),
                    'ozone': round(np.random.normal(50, 20), 2),
                    'pollen_count': int(np.random.exponential(100)) if month in [2, 3, 4] else int(np.random.exponential(30))
                })
                
                current_date += timedelta(days=1)
        
        return pd.DataFrame(aqi_data)
    
    def generate_events(self) -> pd.DataFrame:
        """Generate events table - Indian festivals, holidays, and major events"""
        events_data = []
        event_id = 1
        
        # Define annual events (will be repeated for each year)
        annual_events = [
            {'name': 'Diwali', 'type': 'festival', 'month': 10, 'duration': 5, 'impact': 1.4, 'is_holiday': True},
            {'name': 'Holi', 'type': 'festival', 'month': 3, 'duration': 2, 'impact': 1.3, 'is_holiday': True},
            {'name': 'Ganesh Chaturthi', 'type': 'festival', 'month': 9, 'duration': 10, 'impact': 1.5, 'is_holiday': True},
            {'name': 'Navratri', 'type': 'festival', 'month': 10, 'duration': 9, 'impact': 1.2, 'is_holiday': False},
            {'name': 'Eid al-Fitr', 'type': 'festival', 'month': 5, 'duration': 3, 'impact': 1.3, 'is_holiday': True},
            {'name': 'Christmas', 'type': 'festival', 'month': 12, 'duration': 2, 'impact': 1.2, 'is_holiday': True},
            {'name': 'Republic Day', 'type': 'public_holiday', 'month': 1, 'duration': 1, 'impact': 1.1, 'is_holiday': True},
            {'name': 'Independence Day', 'type': 'public_holiday', 'month': 8, 'duration': 1, 'impact': 1.1, 'is_holiday': True},
            {'name': 'Monsoon Season Peak', 'type': 'seasonal', 'month': 7, 'duration': 30, 'impact': 1.3, 'is_holiday': False},
        ]
        
        # Generate events for each year in the date range
        current_year = self.start_date.year
        end_year = self.end_date.year
        
        for year in range(current_year, end_year + 1):
            for event_template in annual_events:
                # Calculate approximate dates (simplified)
                start_day = random.randint(1, 28)
                start_date = datetime(year, event_template['month'], start_day)
                end_date = start_date + timedelta(days=event_template['duration'] - 1)
                
                # Only add if within our date range
                if start_date.date() >= self.start_date.date() and start_date.date() <= self.end_date.date():
                    for location in self.locations[:2]:  # Major events in main locations
                        events_data.append({
                            'event_id': event_id,
                            'event_name': f"{event_template['name']} {year}",
                            'event_type': event_template['type'],
                            'start_date': start_date.date(),
                            'end_date': end_date.date(),
                            'location_id': location['location_id'],
                            'impact_multiplier': event_template['impact'],
                            'is_public_holiday': event_template['is_holiday'],
                            'notes': f"Annual {event_template['type']} event"
                        })
                        event_id += 1
        
        if not events_data:
            return pd.DataFrame(columns=['event_id', 'event_name', 'event_type', 'start_date', 'end_date', 'location_id', 'impact_multiplier', 'is_public_holiday', 'notes'])
        
        return pd.DataFrame(events_data)
    
    def generate_epidemic_surveillance(self) -> pd.DataFrame:
        """Generate epidemic_surveillance table - disease outbreak tracking"""
        surveillance_data = []
        
        # Common diseases in India
        diseases = [
            {'name': 'Dengue Fever', 'season_months': [7, 8, 9, 10], 'severity': 'high'},
            {'name': 'Malaria', 'season_months': [6, 7, 8, 9], 'severity': 'medium'},
            {'name': 'Influenza', 'season_months': [12, 1, 2, 3], 'severity': 'medium'},
            {'name': 'Typhoid', 'season_months': [5, 6, 7, 8], 'severity': 'medium'},
            {'name': 'Chikungunya', 'season_months': [7, 8, 9], 'severity': 'medium'},
            {'name': 'COVID-19', 'season_months': list(range(1, 13)), 'severity': 'high'},
        ]
        
        for location in self.locations:
            current_date = self.start_date
            
            while current_date <= self.end_date:
                month = current_date.month
                
                # Check each disease
                for disease in diseases:
                    if month in disease['season_months']:
                        # Higher probability during season
                        if random.random() < 0.3:  # 30% chance of cases on any day during season
                            base_cases = 50 if disease['severity'] == 'high' else 20
                            confirmed = int(np.random.exponential(base_cases))
                            suspected = int(confirmed * np.random.uniform(1.5, 3))
                            deaths = int(confirmed * np.random.uniform(0.01, 0.05)) if disease['severity'] == 'high' else 0
                            
                            surveillance_data.append({
                                'location_id': location['location_id'],
                                'date': current_date.date(),
                                'disease_name': disease['name'],
                                'confirmed_cases': confirmed,
                                'suspected_cases': suspected,
                                'deaths': deaths
                            })
                
                current_date += timedelta(days=1)
        
        return pd.DataFrame(surveillance_data)
    
    def generate_patient_visits(self, events_df: pd.DataFrame) -> pd.DataFrame:
        """Generate patient_visits table - core patient visit records with Mumbai seasonality"""
        patient_visits_data = []
        patient_id = 100000
        visit_id = 1
        
        # Common diagnoses in India with Categories
        diagnoses_pool = [
            {'code': 'A09', 'desc': 'Gastroenteritis', 'severity': 2, 'category': 'Water-Borne'},
            {'code': 'J18.9', 'desc': 'Pneumonia', 'severity': 3, 'category': 'Respiratory'},
            {'code': 'A90', 'desc': 'Dengue Fever', 'severity': 3, 'category': 'Vector-Borne'},
            {'code': 'B54', 'desc': 'Malaria', 'severity': 3, 'category': 'Vector-Borne'},
            {'code': 'E11.9', 'desc': 'Type 2 Diabetes', 'severity': 2, 'category': 'Chronic'},
            {'code': 'I10', 'desc': 'Hypertension', 'severity': 2, 'category': 'Chronic'},
            {'code': 'J45.9', 'desc': 'Asthma', 'severity': 2, 'category': 'Respiratory'},
            {'code': 'N39.0', 'desc': 'Urinary Tract Infection', 'severity': 2, 'category': 'Other'},
            {'code': 'M25.5', 'desc': 'Joint Pain', 'severity': 1, 'category': 'Other'},
            {'code': 'R50.9', 'desc': 'Fever', 'severity': 2, 'category': 'General'},
            {'code': 'I21.9', 'desc': 'Acute Myocardial Infarction', 'severity': 5, 'category': 'Cardiac'},
        ]
        
        for hospital in self.hospitals:
            # Get departments for this hospital
            hospital_depts = [d for d in self.departments if d['hospital_id'] == hospital['hospital_id']]
            
            current_date = self.start_date
            
            while current_date <= self.end_date:
                # Base patient count from Profile
                base_daily_patients = self.profile.daily_opd
                
                # Day of week effect (Sundays less)
                dow_multiplier = 1.1 if current_date.weekday() in [0, 1] else (0.5 if current_date.weekday() == 6 else 0.9)
                
                # Event effect
                event_multiplier = 1.0
                for _, event in events_df.iterrows():
                    if event['start_date'] <= current_date.date() <= event['end_date']:
                        if event['location_id'] == hospital['location_id']:
                            event_multiplier = max(event_multiplier, event['impact_multiplier'])
                
                # Calculate daily total
                daily_patients = int(base_daily_patients * dow_multiplier * event_multiplier * np.random.normal(1, 0.1))
                
                for _ in range(daily_patients):
                    # Select diagnosis based on Seasonality
                    # We weight the random choice by the seasonal multiplier for each disease category
                    weights = []
                    for diag in diagnoses_pool:
                        multiplier = SeasonalityEngine.get_disease_multiplier(current_date, diag['category'])
                        weights.append(multiplier)
                    
                    # Normalize weights
                    total_weight = sum(weights)
                    probs = [w / total_weight for w in weights]
                    
                    diagnosis = np.random.choice(diagnoses_pool, p=probs)
                    
                    # Generate arrival time
                    hour_weights = [0.01, 0.005, 0.005, 0.005, 0.01, 0.02, 0.04, 0.06, 0.08, 0.07, 
                                    0.06, 0.05, 0.05, 0.05, 0.05, 0.05, 0.06, 0.07, 0.06, 0.05, 
                                    0.04, 0.03, 0.02, 0.01]
                    hour_weights = [w / sum(hour_weights) for w in hour_weights]
                    hour = np.random.choice(range(24), p=hour_weights)
                    minute = random.randint(0, 59)
                    visit_dttm = current_date.replace(hour=hour, minute=minute, second=0)
                    
                    # Select department
                    department = random.choice(hospital_depts)
                    
                    severity_level = diagnosis['severity']
                    
                    # Admission flag
                    admission_flag = severity_level >= 3 and random.random() < 0.4
                    
                    # Timestamps
                    admission_dttm = None
                    discharge_dttm = None
                    wait_minutes = int(np.random.exponential(30))
                    
                    if admission_flag:
                        admission_dttm = visit_dttm + timedelta(minutes=wait_minutes + random.randint(30, 120))
                        los_hours = int(np.random.exponential(48))  # Length of stay
                        discharge_dttm = admission_dttm + timedelta(hours=los_hours)
                    else:
                        # Outpatient - discharged same day
                        discharge_dttm = visit_dttm + timedelta(minutes=wait_minutes + random.randint(20, 180))
                    
                    patient_visits_data.append({
                        'visit_id': visit_id,
                        'patient_id': patient_id,
                        'hospital_id': hospital['hospital_id'],
                        'department_id': department['department_id'],
                        'visit_date': current_date.date(),
                        'visit_dttm': visit_dttm,
                        'admission_dttm': admission_dttm,
                        'discharge_dttm': discharge_dttm,
                        'severity_level': severity_level,
                        'primary_diag_code': diagnosis['code'],
                        'diagnosis_summary': diagnosis['desc'],
                        'age': int(np.random.exponential(35)),
                        'gender': random.choice(['M', 'F', 'Other']),
                        'wait_minutes': wait_minutes,
                        'admission_flag': admission_flag,
                        'associated_event_id': None  # Could be linked to events
                    })
                    
                    visit_id += 1
                    patient_id += 1
                
                current_date += timedelta(days=1)
        
        return pd.DataFrame(patient_visits_data)
    
    def generate_diagnoses(self, patient_visits_df: pd.DataFrame) -> pd.DataFrame:
        """Generate diagnoses table - multiple diagnoses per visit"""
        diagnoses_data = []
        diagnosis_id = 1
        
        # Extended disease list with ICD codes
        disease_list = [
            {'disease_name': 'Dengue Fever', 'code': 'A90', 'icd': 'A90'},
            {'disease_name': 'Malaria', 'code': 'B54', 'icd': 'B54'},
            {'disease_name': 'Typhoid Fever', 'code': 'A01.0', 'icd': 'A01.0'},
            {'disease_name': 'Tuberculosis', 'code': 'A15.9', 'icd': 'A15.9'},
            {'disease_name': 'Pneumonia', 'code': 'J18.9', 'icd': 'J18.9'},
            {'disease_name': 'Asthma', 'code': 'J45.9', 'icd': 'J45.9'},
            {'disease_name': 'COPD', 'code': 'J44.9', 'icd': 'J44.9'},
            {'disease_name': 'Hypertension', 'code': 'I10', 'icd': 'I10'},
            {'disease_name': 'Type 2 Diabetes', 'code': 'E11.9', 'icd': 'E11.9'},
            {'disease_name': 'Gastroenteritis', 'code': 'A09', 'icd': 'A09'},
            {'disease_name': 'Urinary Tract Infection', 'code': 'N39.0', 'icd': 'N39.0'},
            {'disease_name': 'Acute Myocardial Infarction', 'code': 'I21.9', 'icd': 'I21.9'},
            {'disease_name': 'Stroke', 'code': 'I64', 'icd': 'I64'},
            {'disease_name': 'Fracture', 'code': 'S82.9', 'icd': 'S82.9'},
            {'disease_name': 'COVID-19', 'code': 'U07.1', 'icd': 'U07.1'},
        ]
        
        for _, visit in patient_visits_df.iterrows():
            # Number of diagnoses per visit (1-3)
            num_diagnoses = random.choices([1, 2, 3], weights=[0.7, 0.25, 0.05])[0]
            
            selected_diseases = random.sample(disease_list, num_diagnoses)
            
            for idx, disease in enumerate(selected_diseases):
                is_primary = (idx == 0)
                
                # Diagnosis time is after visit time
                diagnosis_time = visit['visit_dttm'] + timedelta(minutes=random.randint(10, 120))
                
                diagnoses_data.append({
                    'diagnosis_id': diagnosis_id,
                    'visit_id': visit['visit_id'],
                    'clinician_id': random.choice(self.staff_list)['staff_id'] if self.staff_list else None,
                    'diagnosis_time': diagnosis_time,
                    'disease_name': disease['disease_name'],
                    'diagnosis_code': disease['code'],
                    'icd_code': disease['icd'],
                    'diagnosis_desc': f"Patient diagnosed with {disease['disease_name']}",
                    'is_primary': is_primary
                })
                
                diagnosis_id += 1
        
        return pd.DataFrame(diagnoses_data)
    
    def generate_staff_availability(self) -> pd.DataFrame:
        """Generate staff_availability table - daily staff snapshots"""
        availability_data = []
        
        shift_types = ['Morning', 'Evening', 'Night']
        
        for hospital in self.hospitals:
            # Get departments for this hospital
            hospital_depts = [d for d in self.departments if d['hospital_id'] == hospital['hospital_id']]
            
            current_date = self.start_date
            
            while current_date <= self.end_date:
                for department in hospital_depts:
                    for shift_type in shift_types:
                        # Staff availability varies by shift and day
                        base_doctors = random.randint(3, 8)
                        base_nurses = random.randint(8, 20)
                        base_techs = random.randint(2, 6)
                        
                        # Weekend reduction
                        if current_date.weekday() in [5, 6]:
                            base_doctors = int(base_doctors * 0.7)
                            base_nurses = int(base_nurses * 0.8)
                            base_techs = int(base_techs * 0.7)
                        
                        # Night shift reduction
                        if shift_type == 'Night':
                            base_doctors = int(base_doctors * 0.6)
                            base_nurses = int(base_nurses * 0.7)
                        
                        availability_data.append({
                            'hospital_id': hospital['hospital_id'],
                            'department_id': department['department_id'],
                            'snapshot_date': current_date.date(),
                            'snapshot_ts': current_date,
                            'shift_type': shift_type,
                            'doctors_available': base_doctors,
                            'nurses_available': base_nurses,
                            'technicians_available': base_techs
                        })
                
                current_date += timedelta(days=1)
        
        return pd.DataFrame(availability_data)
    
    def generate_supply_inventory(self) -> pd.DataFrame:
        """Generate supply_inventory table - daily inventory snapshots"""
        inventory_data = []
        
        # Common hospital supplies
        supply_items = [
            {'code': 'MED-PARA-500', 'name': 'Paracetamol 500mg', 'reorder': 5000, 'lead_days': 3},
            {'code': 'MED-AMOX-250', 'name': 'Amoxicillin 250mg', 'reorder': 3000, 'lead_days': 3},
            {'code': 'MED-INSULIN', 'name': 'Insulin Vials', 'reorder': 500, 'lead_days': 5},
            {'code': 'PPE-MASK-SURG', 'name': 'Surgical Masks', 'reorder': 10000, 'lead_days': 2},
            {'code': 'PPE-GLOVE-NIT', 'name': 'Nitrile Gloves', 'reorder': 15000, 'lead_days': 2},
            {'code': 'PPE-GOWN', 'name': 'Isolation Gowns', 'reorder': 2000, 'lead_days': 4},
            {'code': 'SUP-IV-FLUID', 'name': 'IV Fluid Bags', 'reorder': 1000, 'lead_days': 3},
            {'code': 'SUP-SYRINGE', 'name': 'Disposable Syringes', 'reorder': 8000, 'lead_days': 2},
            {'code': 'SUP-OXYGEN', 'name': 'Oxygen Cylinders', 'reorder': 50, 'lead_days': 7},
            {'code': 'SUP-BANDAGE', 'name': 'Sterile Bandages', 'reorder': 5000, 'lead_days': 3},
        ]
        
        for hospital in self.hospitals:
            # Initialize stock levels
            stock_levels = {item['code']: item['reorder'] * 3 for item in supply_items}
            pending_orders = {}
            
            current_date = self.start_date
            
            while current_date <= self.end_date:
                for item in supply_items:
                    item_code = item['code']
                    
                    # Daily usage
                    base_usage = int(item['reorder'] * 0.05)  # 5% of reorder level per day
                    usage = int(base_usage * np.random.normal(1, 0.3))
                    usage = max(0, usage)
                    
                    # Update stock
                    stock_levels[item_code] -= usage
                    
                    # Check for deliveries
                    if item_code in pending_orders and pending_orders[item_code]['delivery_date'] == current_date.date():
                        stock_levels[item_code] += pending_orders[item_code]['quantity']
                        del pending_orders[item_code]
                    
                    # Reorder if needed
                    if stock_levels[item_code] <= item['reorder'] and item_code not in pending_orders:
                        order_qty = item['reorder'] * 4
                        delivery_date = current_date + timedelta(days=item['lead_days'])
                        pending_orders[item_code] = {
                            'quantity': order_qty,
                            'delivery_date': delivery_date.date()
                        }
                    
                    inventory_data.append({
                        'hospital_id': hospital['hospital_id'],
                        'item_code': item_code,
                        'item_name': item['name'],
                        'snapshot_date': current_date.date(),
                        'qty_on_hand': max(0, stock_levels[item_code]),
                        'reorder_level': item['reorder'],
                        'estimated_lead_days': item['lead_days']
                    })
                
                current_date += timedelta(days=1)
        
        return pd.DataFrame(inventory_data)
    
    def run_complete_generation(self) -> Dict[str, pd.DataFrame]:
        """Run complete data generation pipeline for all tables"""
        print("=" * 60)
        print("STARTING COMPREHENSIVE DATA GENERATION")
        print("=" * 60)
        
        # 1. Locations
        print("\n[1/12] Generating Locations...")
        self.data['locations'] = self.generate_locations()
        
        # 2. Hospitals
        print("[2/12] Generating Hospitals...")
        self.data['hospitals'] = self.generate_hospitals()
        
        # 3. Departments
        print("[3/12] Generating Departments...")
        self.data['departments'] = self.generate_departments()
        
        # 4. Staff
        print("[4/12] Generating Staff...")
        self.data['staff'] = self.generate_staff()
        
        # 5. Weather
        print("[5/12] Generating Weather Data...")
        self.data['weather_data'] = self.generate_weather_data()
        
        # 6. Air Quality
        print("[6/12] Generating Air Quality Data...")
        self.data['air_quality_data'] = self.generate_air_quality_data()
        
        # 7. Events
        print("[7/12] Generating Events...")
        self.data['events'] = self.generate_events()
        
        # 8. Epidemic Surveillance
        print("[8/12] Generating Epidemic Surveillance...")
        self.data['epidemic_surveillance'] = self.generate_epidemic_surveillance()
        
        # 9. Patient Visits (Core)
        print("[9/12] Generating Patient Visits (this may take a moment)...")
        self.data['patient_visits'] = self.generate_patient_visits(self.data['events'])
        
        # 10. Diagnoses
        print("[10/12] Generating Diagnoses...")
        self.data['diagnoses'] = self.generate_diagnoses(self.data['patient_visits'])
        
        # 11. Staff Availability
        print("[11/12] Generating Staff Availability...")
        self.data['staff_availability'] = self.generate_staff_availability()
        
        # 12. Supply Inventory
        print("[12/12] Generating Supply Inventory...")
        self.data['supply_inventory'] = self.generate_supply_inventory()
        
        print("\n" + "=" * 60)
        print("GENERATION COMPLETE")
        print("=" * 60)
        
        return self.data
    
    def export_data(self, output_dir='./media/hospital_data_csv'):
        """Export all generated data to CSV files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nExporting data to {output_dir}...")
        print("-" * 60)
        
        for table_name, dataframe in self.data.items():
            filename = f"{output_dir}/{table_name}.csv"
            dataframe.to_csv(filename, index=False)
            print(f"  + Exported {table_name}.csv ({len(dataframe)} rows)")
        
        print("-" * 60)
        print(f"All {len(self.data)} tables exported successfully!")
        print(f"Output directory: {output_dir}")
    
    def display_summary(self):
        """Display summary statistics for generated data"""
        print("\n" + "=" * 60)
        print("DATA SUMMARY")
        print("=" * 60)
        
        for table_name, dataframe in self.data.items():
            print(f"\n{table_name.upper()}")
            print(f"  Rows: {len(dataframe):,}")
            print(f"  Columns: {len(dataframe.columns)}")
            print(f"  Memory: {dataframe.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            
            # Show date range if applicable
            date_cols = [col for col in dataframe.columns if 'date' in col.lower() or 'dttm' in col.lower()]
            if date_cols:
                date_col = date_cols[0]
                try:
                    dates = pd.to_datetime(dataframe[date_col])
                    print(f"  Date Range: {dates.min()} to {dates.max()}")
                except:
                    pass


# Example usage
if __name__ == "__main__":
    # Initialize generator
    generator = ComprehensiveHospitalDataGenerator(
        start_date="2022-01-01",
        end_date="2024-11-22",
        random_seed=42
    )
    
    # Generate all data
    data = generator.run_complete_generation()
    
    # Display summary
    generator.display_summary()
    
    # Export to CSV
    generator.export_data(output_dir='../media/hospital_data_csv')
    
    print("\n✓ All done! Check the hospital_data_csv directory for CSV files.")