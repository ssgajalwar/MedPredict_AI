import os
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import Dict
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
            name="Lilavati Hospital & Research Centre - Mumbai Suburban",
            beds=350,
            daily_opd=210,  # Adjusted to match 0.6 * beds
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
        
        if disease_category == "Vector-Borne":  # Malaria, Dengue
            # Peak in Monsoon (June-Sept) and post-monsoon (Oct)
            if month in [6, 7, 8, 9]:
                return 3.5  # Massive spike during monsoon
            elif month in [10]:
                return 2.0  # Tapering off
            else:
                return 0.5  # Low during dry season
                
        elif disease_category == "Respiratory":  # Asthma, Pneumonia
            # Peak in Winter (Nov-Jan) due to smog/AQI
            if month in [11, 12, 1]:
                return 2.5
            else:
                return 0.8
                
        elif disease_category == "Water-Borne":  # Typhoid, Gastroenteritis
            # Peak in Monsoon (July-Aug)
            if month in [7, 8]:
                return 3.0
            else:
                return 0.6
                
        return 1.0

class LilavatiMumbaiDataGenerator:
    def __init__(self,
                 start_date: str = "2020-01-01",
                 end_date: str = "2024-11-22",
                 random_seed: int = 42,
                 scale_factor: float = 1.0,
                 profile: HospitalProfile = None):
        """
        Initialize the comprehensive hospital data generator
        
        Parameters:
        - start_date: Start date for data generation
        - end_date: End date for data generation
        - random_seed: Random seed for reproducibility
        - scale_factor: Multiply counts by this (0.1 = 10% size for quick tests, 1.0 = full size)
        - profile: HospitalProfile instance (defaults to LilavatiHospitalProfile)
        """
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.random_seed = random_seed
        self.scale_factor = float(scale_factor)
        self.profile = profile if profile else LilavatiHospitalProfile()
        
        np.random.seed(random_seed)
        random.seed(random_seed)

        self.data = {}
        self.locations = []
        self.hospitals = []
        self.departments = []
        self.staff_list = []
        
        print(f"Initialized Generator with Profile: {self.profile.name} ({self.profile.beds} beds), scale={self.scale_factor}")

    def generate_locations(self) -> pd.DataFrame:
        locations_data = [{
            'location_id': 1,
            'name': 'Mumbai Suburban',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'region': 'West',
            'latitude': 19.1136,
            'longitude': 72.8697,
            'population': 9356962,
            'urban_rural': 'Urban'
        }]
        self.locations = locations_data
        return pd.DataFrame(locations_data)

    def generate_hospitals(self) -> pd.DataFrame:
        hospitals_data = []
        # Generate hospital based on profile
        location = [l for l in self.locations if l['city'] == self.profile.city][0]
        
        hospitals_data.append({
            'hospital_id': 1,
            'hospital_name': self.profile.name,
            'location_id': location['location_id'],
            'hospital_type': self.profile.type,
            'total_beds': self.profile.beds,
            'address': 'A-1, Bandstand Road, Bandra West, Mumbai',
            'contact_phone': '+91-022-26400000'
        })
        self.hospitals = hospitals_data
        return pd.DataFrame(hospitals_data)

    def generate_departments(self) -> pd.DataFrame:
        departments_data = []
        department_id = 1

        # realistic set for a tertiary hospital
        department_templates = [
            {'code': 'ER', 'name': 'Emergency', 'floor': 0},
            {'code': 'CARD', 'name': 'Cardiology', 'floor': 6},
            {'code': 'ORTHO', 'name': 'Orthopedics', 'floor': 7},
            {'code': 'PEDS', 'name': 'Pediatrics', 'floor': 5},
            {'code': 'OBG', 'name': 'Obstetrics & Gynaecology', 'floor': 8},
            {'code': 'ICU', 'name': 'Intensive Care Unit', 'floor': 9},
            {'code': 'SURG', 'name': 'General Surgery', 'floor': 7},
            {'code': 'MED', 'name': 'Internal Medicine', 'floor': 6},
            {'code': 'RESP', 'name': 'Respiratory Medicine', 'floor': 6},
            {'code': 'NEURO', 'name': 'Neurology', 'floor': 10},
            {'code': 'ENT', 'name': 'ENT', 'floor': 4},
            {'code': 'RAD', 'name': 'Radiology', 'floor': 3},
            {'code': 'LAB', 'name': 'Clinical Lab', 'floor': 2},
        ]

        for hosp in self.hospitals:
            selected_depts = department_templates
            for tmpl in selected_depts:
                departments_data.append({
                    'department_id': department_id,
                    'hospital_id': hosp['hospital_id'],
                    'department_code': f"{tmpl['code']}-H{hosp['hospital_id']}-D{department_id}",
                    'department_name': tmpl['name'],
                    'floor_number': tmpl['floor'],
                    'head_doctor_id': None,
                    'contact_ext': f"x{random.randint(100, 999)}"
                })
                department_id += 1

        self.departments = departments_data
        return pd.DataFrame(departments_data)

    def generate_staff(self) -> pd.DataFrame:
        staff_data = []
        staff_id = 1

        first_names = ['Rajesh', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anjali', 'Rahul', 'Kavita',
                       'Suresh', 'Meera', 'Arjun', 'Pooja', 'Nitin', 'Deepa', 'Karan', 'Ritu',
                       'Rohit', 'Asha', 'Sunita', 'Mohan']
        last_names = ['Sharma', 'Patel', 'Kumar', 'Singh', 'Desai', 'Mehta', 'Gupta', 'Reddy',
                      'Iyer', 'Joshi', 'Nair', 'Rao', 'Kulkarni', 'Chopra', 'Malhotra', 'Verma']

        # scaled realistic counts
        doctors_per_hospital = max(5, int(60 * self.scale_factor))
        nurses_per_hospital = max(10, int(200 * self.scale_factor))
        technicians_per_hospital = max(3, int(50 * self.scale_factor))
        admin_per_hospital = max(3, int(40 * self.scale_factor))

        roles = [
            ('doctor', doctors_per_hospital, ['Cardiology', 'Orthopedics', 'Pediatrics', 'General Medicine', 'Surgery', 'Neurology', 'Respiratory', 'Endocrinology']),
            ('nurse', nurses_per_hospital, ['ICU', 'ER', 'General', 'Pediatric', 'Maternity']),
            ('technician', technicians_per_hospital, ['Radiology', 'Lab', 'Respiratory', 'Cardiac', 'Anaesthesia']),
            ('admin', admin_per_hospital, ['Reception', 'Billing', 'Records', 'Management'])
        ]

        for hospital in self.hospitals:
            for role, count, specialties in roles:
                for _ in range(max(1, count)):
                    fname = random.choice(first_names)
                    lname = random.choice(last_names)
                    staff_data.append({
                        'staff_id': staff_id,
                        'hospital_id': hospital['hospital_id'],
                        'first_name': fname,
                        'last_name': lname,
                        'role': role,
                        'specialty': random.choice(specialties),
                        'phone': f"+91-{random.randint(7000000000, 9999999999)}",
                        'email': f"{fname.lower()}.{lname.lower()}{staff_id}@lilavati.in"
                    })
                    staff_id += 1

        self.staff_list = staff_data

        # assign department heads: pick from doctors
        doctors = [s for s in staff_data if s['role'] == 'doctor']
        for i, dept in enumerate(self.departments):
            if doctors:
                head = doctors[i % len(doctors)]
                dept['head_doctor_id'] = head['staff_id']

        return pd.DataFrame(staff_data)

    def generate_weather_data(self) -> pd.DataFrame:
        weather_data = []
        for loc in self.locations:
            current = self.start_date
            while current <= self.end_date:
                m = current.month
                if m in [12,1,2]:
                    temp_avg = np.random.normal(25, 2)
                    rainfall = np.random.exponential(1) if random.random() < 0.05 else 0
                elif m in [3,4,5]:
                    temp_avg = np.random.normal(32, 3)
                    rainfall = np.random.exponential(3) if random.random() < 0.1 else 0
                elif m in [6,7,8,9]:
                    temp_avg = np.random.normal(28, 2)
                    rainfall = np.random.exponential(60) if random.random() < 0.7 else 0
                else:
                    temp_avg = np.random.normal(29, 2)
                    rainfall = np.random.exponential(8) if random.random() < 0.15 else 0

                weather_data.append({
                    'location_id': loc['location_id'],
                    'record_date': current.date(),
                    'temperature_avg': round(float(temp_avg),2),
                    'temperature_min': round(float(temp_avg - np.random.uniform(3,6)),2),
                    'temperature_max': round(float(temp_avg + np.random.uniform(3,6)),2),
                    'humidity_percent': round(float(max(30, min(100, np.random.normal(70,12)))),2),
                    'rainfall_mm': round(float(max(0, rainfall)),2),
                    'wind_speed_kmh': round(float(np.random.normal(12,4)),2)
                })
                current += timedelta(days=1)
        return pd.DataFrame(weather_data)

    def generate_air_quality_data(self) -> pd.DataFrame:
        aqi_data = []
        for loc in self.locations:
            current = self.start_date
            while current <= self.end_date:
                m = current.month
                if m in [11,12,1,2]:
                    base = 180
                elif m in [6,7,8,9]:
                    base = 80
                else:
                    base = 120
                aqi_level = int(max(10, min(500, np.random.normal(base, 35))))
                pm25 = round(max(0, aqi_level * 0.45 + np.random.normal(0,10)),2)
                pm10 = round(max(0, aqi_level * 0.7 + np.random.normal(0,15)),2)
                aqi_data.append({
                    'location_id': loc['location_id'],
                    'record_date': current.date(),
                    'aqi_level': aqi_level,
                    'pm25': pm25,
                    'pm10': pm10,
                    'no2': round(float(np.random.normal(35,10)),2),
                    'so2': round(float(np.random.normal(12,6)),2),
                    'co': round(float(np.random.normal(1.0,0.4)),2),
                    'ozone': round(float(np.random.normal(40,15)),2),
                    'pollen_count': int(np.random.exponential(80)) if m in [2,3,4] else int(np.random.exponential(25))
                })
                current += timedelta(days=1)
        return pd.DataFrame(aqi_data)

    def generate_events(self) -> pd.DataFrame:
        events = []
        event_id = 1
        annual_templates = [
            {'name':'Ganesh Chaturthi', 'month':9, 'duration':10, 'impact':1.6, 'is_holiday':True},
            {'name':'Diwali', 'month':10, 'duration':4, 'impact':1.4, 'is_holiday':True},
            {'name':'Holi', 'month':3, 'duration':2, 'impact':1.25, 'is_holiday':True},
            {'name':'Mumbai Marathon', 'month':2, 'duration':1, 'impact':1.2, 'is_holiday':False},
            {'name':'Monsoon Peak', 'month':7, 'duration':30, 'impact':1.3, 'is_holiday':False},
            {'name':'Shivaji Jayanti', 'month':2, 'duration':1, 'impact':1.05, 'is_holiday':True},
            {'name':'Republic Day', 'month':1, 'duration':1, 'impact':1.05, 'is_holiday':True},
            {'name':'Independence Day', 'month':8, 'duration':1, 'impact':1.05, 'is_holiday':True},
            {'name':'Christmas', 'month':12, 'duration':1, 'impact':1.1, 'is_holiday':True},
        ]

        for year in range(self.start_date.year, self.end_date.year + 1):
            for t in annual_templates:
                start_day = min(25, max(1, random.randint(1, 25)))
                try:
                    start = datetime(year, t['month'], start_day)
                except Exception:
                    start = datetime(year, t['month'], 1)
                end = start + timedelta(days=t['duration'] - 1)
                if start.date() > self.end_date.date() or end.date() < self.start_date.date():
                    continue
                events.append({
                    'event_id': event_id,
                    'event_name': f"{t['name']} {year}",
                    'event_type': 'festival' if 'festival' in t.get('type','festival') or t['is_holiday'] else 'event',
                    'start_date': start.date(),
                    'end_date': end.date(),
                    'location_id': 1,
                    'impact_multiplier': t['impact'],
                    'is_public_holiday': t['is_holiday'],
                    'notes': f"{t['name']} in Mumbai ({year})"
                })
                event_id += 1
        return pd.DataFrame(events)

    def generate_epidemic_surveillance(self) -> pd.DataFrame:
        surveillance = []
        diseases = [
            {'name':'Dengue', 'months':[6,7,8,9], 'severity':'high'},
            {'name':'Malaria', 'months':[6,7,8,9], 'severity':'medium'},
            {'name':'Influenza', 'months':[12,1,2,3], 'severity':'medium'},
            {'name':'Typhoid', 'months':[5,6,7,8], 'severity':'medium'},
            {'name':'COVID-19', 'months':list(range(1,13)), 'severity':'high'}
        ]
        for loc in self.locations:
            cur = self.start_date
            while cur <= self.end_date:
                for d in diseases:
                    if cur.month in d['months']:
                        if random.random() < (0.25 if d['severity']=='medium' else 0.35):
                            base = 40 if d['severity']=='high' else 15
                            confirmed = int(np.random.exponential(base) * self.scale_factor)
                            suspected = int(confirmed * np.random.uniform(1.2,2.5))
                            deaths = int(confirmed * np.random.uniform(0.01, 0.05)) if d['severity']=='high' else int(confirmed * np.random.uniform(0.0,0.02))
                            surveillance.append({
                                'location_id': loc['location_id'],
                                'date': cur.date(),
                                'disease_name': d['name'],
                                'confirmed_cases': confirmed,
                                'suspected_cases': suspected,
                                'deaths': deaths
                            })
                cur += timedelta(days=1)
        return pd.DataFrame(surveillance)

    def generate_patient_visits(self, events_df: pd.DataFrame) -> pd.DataFrame:
        visits = []
        visit_id = 1
        patient_counter = 200000  # synthetic patient id seed

        diagnoses_pool = [
            {'code':'A09','desc':'Gastroenteritis','severity':2,'disease':'Gastroenteritis','category':'Water-Borne'},
            {'code':'J18.9','desc':'Pneumonia','severity':3,'disease':'Pneumonia','category':'Respiratory'},
            {'code':'A90','desc':'Dengue Fever','severity':3,'disease':'Dengue','category':'Vector-Borne'},
            {'code':'E11.9','desc':'Type 2 Diabetes','severity':2,'disease':'Type 2 Diabetes','category':'Chronic'},
            {'code':'I10','desc':'Hypertension','severity':2,'disease':'Hypertension','category':'Chronic'},
            {'code':'J45.9','desc':'Asthma','severity':2,'disease':'Asthma','category':'Respiratory'},
            {'code':'N39.0','desc':'Urinary Tract Infection','severity':2,'disease':'UTI','category':'Other'},
            {'code':'S82.9','desc':'Fracture','severity':3,'disease':'Fracture','category':'Other'},
            {'code':'R50.9','desc':'Fever','severity':2,'disease':'Fever','category':'General'},
            {'code':'I21.9','desc':'Acute Myocardial Infarction','severity':5,'disease':'AMI','category':'Cardiac'},
            {'code':'U07.1','desc':'COVID-19','severity':4,'disease':'COVID-19','category':'Other'}
        ]

        for hosp in self.hospitals:
            hosp_depts = [d for d in self.departments if d['hospital_id'] == hosp['hospital_id']]
            cur = self.start_date
            while cur <= self.end_date:
                base_daily_patients = int(hosp['total_beds'] * 0.6 * self.scale_factor)
                dow_multiplier = 1.15 if cur.weekday() in [0,1] else 0.95
                month = cur.month
                seasonal_multiplier = 1.35 if month in [6,7,8,9] else 1.0  # monsoon
                event_multiplier = 1.0
                if not events_df.empty:
                    for _, ev in events_df.iterrows():
                        if ev['start_date'] <= cur.date() <= ev['end_date'] and ev['location_id'] == hosp['location_id']:
                            event_multiplier = max(event_multiplier, ev['impact_multiplier'])
                
                # Apply seasonality to diagnosis selection
                daily_patients = int(max(5, base_daily_patients * dow_multiplier * seasonal_multiplier * event_multiplier * np.random.normal(1, 0.12)))
                hour_weights = [0.01]*24
                for h in range(6,22):
                    hour_weights[h] = 0.06
                hour_weights = [w / sum(hour_weights) for w in hour_weights]

                for _ in range(daily_patients):
                    hour = np.random.choice(range(24), p=hour_weights)
                    minute = random.randint(0,59)
                    visit_dttm = cur.replace(hour=hour, minute=minute, second=0)

                    # Select diagnosis based on seasonality
                    weights = []
                    for diag in diagnoses_pool:
                        multiplier = SeasonalityEngine.get_disease_multiplier(cur, diag['category'])
                        weights.append(multiplier)
                    
                    # Normalize weights
                    total_weight = sum(weights)
                    probs = [w / total_weight for w in weights]
                    diag = np.random.choice(diagnoses_pool, p=probs)

                    dept = random.choice(hosp_depts)
                    severity = diag['severity']
                    admission_flag = (severity >= 3 and random.random() < 0.5) or (diag['disease'] in ['AMI','COVID-19'] and random.random() < 0.7)

                    wait_minutes = int(np.random.exponential(25))
                    admission_dttm = None
                    discharge_dttm = None
                    if admission_flag:
                        admission_gap = wait_minutes + random.randint(30, 180)
                        admission_dttm = visit_dttm + timedelta(minutes=admission_gap)
                        los_hours = max(6, int(np.random.exponential(48) * (1 + (severity-3)*0.5)))
                        discharge_dttm = admission_dttm + timedelta(hours=los_hours)
                    else:
                        discharge_dttm = visit_dttm + timedelta(minutes=wait_minutes + random.randint(20,240))

                    visits.append({
                        'visit_id': visit_id,
                        'patient_id': patient_counter,
                        'hospital_id': hosp['hospital_id'],
                        'department_id': dept['department_id'],
                        'visit_date': cur.date(),
                        'visit_dttm': visit_dttm,
                        'admission_dttm': admission_dttm,
                        'discharge_dttm': discharge_dttm,
                        'severity_level': severity,
                        'primary_diag_code': diag['code'],
                        'diagnosis_summary': diag['desc'],
                        'age': int(min(100, max(0, np.random.exponential(35)))),
                        'gender': random.choice(['M','F','Other']),
                        'wait_minutes': wait_minutes,
                        'admission_flag': admission_flag,
                        'associated_event_id': None
                    })
                    visit_id += 1
                    patient_counter += 1

                cur += timedelta(days=1)
        return pd.DataFrame(visits)

    def generate_diagnoses(self, patient_visits_df: pd.DataFrame) -> pd.DataFrame:
        diagnoses = []
        diag_id = 1
        disease_list = [
            {'disease_name':'Dengue','code':'A90','icd':'A90'},
            {'disease_name':'Malaria','code':'B54','icd':'B54'},
            {'disease_name':'Typhoid Fever','code':'A01.0','icd':'A01.0'},
            {'disease_name':'Pneumonia','code':'J18.9','icd':'J18.9'},
            {'disease_name':'Asthma','code':'J45.9','icd':'J45.9'},
            {'disease_name':'COPD','code':'J44.9','icd':'J44.9'},
            {'disease_name':'Hypertension','code':'I10','icd':'I10'},
            {'disease_name':'Type 2 Diabetes','code':'E11.9','icd':'E11.9'},
            {'disease_name':'Gastroenteritis','code':'A09','icd':'A09'},
            {'disease_name':'UTI','code':'N39.0','icd':'N39.0'},
            {'disease_name':'Acute Myocardial Infarction','code':'I21.9','icd':'I21.9'},
            {'disease_name':'Fracture','code':'S82.9','icd':'S82.9'},
            {'disease_name':'COVID-19','code':'U07.1','icd':'U07.1'},
        ]

        clinicians = [s for s in self.staff_list if s['role'] == 'doctor']
        if not clinicians:
            clinician_ids = [None]
        else:
            clinician_ids = [c['staff_id'] for c in clinicians]

        for _, visit in patient_visits_df.iterrows():
            num_diag = random.choices([1,2,3], weights=[0.75,0.2,0.05])[0]
            selected = random.sample(disease_list, num_diag)
            for i, d in enumerate(selected):
                is_primary = (i == 0)
                diagnosis_time = visit['visit_dttm'] + timedelta(minutes=random.randint(10, 240))
                diagnoses.append({
                    'diagnosis_id': diag_id,
                    'visit_id': visit['visit_id'],
                    'clinician_id': random.choice(clinician_ids),
                    'diagnosis_time': diagnosis_time,
                    'disease_name': d['disease_name'],
                    'diagnosis_code': d['code'],
                    'icd_code': d['icd'],
                    'diagnosis_desc': f"Patient diagnosed with {d['disease_name']}",
                    'is_primary': is_primary
                })
                diag_id += 1

        return pd.DataFrame(diagnoses)

    def generate_staff_availability(self) -> pd.DataFrame:
        availability = []
        shifts = ['Morning','Evening','Night']
        for hosp in self.hospitals:
            hosp_depts = [d for d in self.departments if d['hospital_id'] == hosp['hospital_id']]
            cur = self.start_date
            while cur <= self.end_date:
                for dept in hosp_depts:
                    for s in shifts:
                        base_doctors = max(1, int(5 * self.scale_factor))
                        base_nurses = max(2, int(12 * self.scale_factor))
                        base_techs = max(1, int(3 * self.scale_factor))
                        if cur.weekday() in [5,6]:
                            base_doctors = int(base_doctors * 0.8)
                            base_nurses = int(base_nurses * 0.85)
                        if s == 'Night':
                            base_doctors = int(base_doctors * 0.6)
                            base_nurses = int(base_nurses * 0.75)
                        availability.append({
                            'hospital_id': hosp['hospital_id'],
                            'department_id': dept['department_id'],
                            'snapshot_date': cur.date(),
                            'snapshot_ts': cur,
                            'shift_type': s,
                            'doctors_available': base_doctors,
                            'nurses_available': base_nurses,
                            'technicians_available': base_techs
                        })
                cur += timedelta(days=1)
        return pd.DataFrame(availability)

    def generate_supply_inventory(self) -> pd.DataFrame:
        items = [
            {'code':'MED-PARA-500','name':'Paracetamol 500mg','reorder':5000,'lead_days':3},
            {'code':'PPE-MASK-SURG','name':'Surgical Masks','reorder':10000,'lead_days':2},
            {'code':'SUP-OXYGEN','name':'Oxygen Cylinders','reorder':50,'lead_days':7},
            {'code':'SUP-IV-FLUID','name':'IV Fluid Bags','reorder':1000,'lead_days':3},
            {'code':'SUP-SYRINGE','name':'Disposable Syringes','reorder':8000,'lead_days':2},
        ]
        inventory = []
        for hosp in self.hospitals:
            stock = {it['code']: it['reorder']*3 for it in items}
            pending = {}
            cur = self.start_date
            while cur <= self.end_date:
                for it in items:
                    code = it['code']
                    base_usage = int(it['reorder'] * 0.05 * self.scale_factor)
                    usage = max(0, int(base_usage * np.random.normal(1, 0.25)))
                    stock[code] = max(0, stock[code] - usage)
                    if code in pending and pending[code]['delivery_date'] == cur.date():
                        stock[code] += pending[code]['quantity']
                        del pending[code]
                    if stock[code] <= it['reorder'] and code not in pending:
                        qty = it['reorder'] * 4
                        delivery = cur + timedelta(days=it['lead_days'])
                        pending[code] = {'quantity': qty, 'delivery_date': delivery.date()}
                    inventory.append({
                        'hospital_id': hosp['hospital_id'],
                        'item_code': code,
                        'item_name': it['name'],
                        'snapshot_date': cur.date(),
                        'qty_on_hand': stock[code],
                        'reorder_level': it['reorder'],
                        'estimated_lead_days': it['lead_days']
                    })
                cur += timedelta(days=1)
        return pd.DataFrame(inventory)

    def run_full(self) -> Dict[str, pd.DataFrame]:
        print("="*60)
        print("Starting Lilavati Hospital (Mumbai) synthetic data generation")
        print("="*60)
        print(f"Date range: {self.start_date.date()} to {self.end_date.date()}")
        print(f"Hospital: {self.profile.name} ({self.profile.beds} beds)")
        print(f"Scale factor: {self.scale_factor}")
        print("="*60)
        
        self.data['locations'] = self.generate_locations()
        print("[1/12] Generated locations")
        self.data['hospitals'] = self.generate_hospitals()
        print("[2/12] Generated hospitals")
        self.data['departments'] = self.generate_departments()
        print(f"[3/12] Generated {len(self.data['departments'])} departments")
        self.data['staff'] = self.generate_staff()
        print(f"[4/12] Generated {len(self.data['staff'])} staff members")
        self.data['weather_data'] = self.generate_weather_data()
        print(f"[5/12] Generated {len(self.data['weather_data'])} weather records")
        self.data['air_quality_data'] = self.generate_air_quality_data()
        print(f"[6/12] Generated {len(self.data['air_quality_data'])} AQI records")
        self.data['events'] = self.generate_events()
        print(f"[7/12] Generated {len(self.data['events'])} Mumbai events")
        self.data['epidemic_surveillance'] = self.generate_epidemic_surveillance()
        print(f"[8/12] Generated {len(self.data['epidemic_surveillance'])} surveillance records")
        self.data['patient_visits'] = self.generate_patient_visits(self.data['events'])
        print(f"[9/12] Generated {len(self.data['patient_visits'])} patient visits")
        self.data['diagnoses'] = self.generate_diagnoses(self.data['patient_visits'])
        print(f"[10/12] Generated {len(self.data['diagnoses'])} diagnoses (disease_name included)")
        self.data['staff_availability'] = self.generate_staff_availability()
        print(f"[11/12] Generated {len(self.data['staff_availability'])} staff availability records")
        self.data['supply_inventory'] = self.generate_supply_inventory()
        print(f"[12/12] Generated {len(self.data['supply_inventory'])} supply inventory records")
        print("\n" + "="*60)
        print("Data generation finished")
        print("="*60)
        return self.data

    def export_csv(self, out_dir: str = 'media/hospital_data_csv'):
        os.makedirs(out_dir, exist_ok=True)
        for name, df in self.data.items():
            path = f"{out_dir}/{name}.csv"
            df.to_csv(path, index=False)
            print(f"Exported {path} ({len(df)} rows)")

    def display_summary(self):
        print("\n" + "="*60)
        print("DATA SUMMARY")
        print("="*60)
        for name, df in self.data.items():
            try:
                cols = len(df.columns)
            except Exception:
                cols = 0
            print(f"\n{name.upper()}")
            print(f"  Rows: {len(df):,}")
            print(f"  Columns: {cols}")
            date_cols = [c for c in df.columns if 'date' in c.lower() or 'dttm' in c.lower()]
            if date_cols and len(df)>0:
                try:
                    sample_col = date_cols[0]
                    rng = pd.to_datetime(df[sample_col])
                    print(f"  Date Range: {rng.min()} -> {rng.max()}")
                except:
                    pass

if __name__ == "__main__":
    # --- instantiate and run for 3-year window ending 2025-10-10 ---
    start_date = "2022-10-11"   # 3-year window (inclusive) -> 2022-10-11 .. 2025-10-10
    end_date = "2025-10-10"
    gen = LilavatiMumbaiDataGenerator(start_date=start_date, end_date=end_date, random_seed=42, scale_factor=0.5)
    data = gen.run_full()
    gen.display_summary()

    # export to local data directory
    out_dir = "media/hospital_data_csv"
    gen.export_csv(out_dir)

    # Save a small README in the output directory
    readme = f"""Lilavati (Mumbai) synthetic dataset
Date range: {start_date} to {end_date}
Scale factor: {gen.scale_factor}
Hospital: {gen.profile.name}
Generated files (CSV) in this folder.
Generated on: {datetime.utcnow().isoformat()} UTC
"""
    with open(os.path.join(out_dir, "README.txt"), "w") as fh:
        fh.write(readme)

    print(f"\nDone. CSVs exported to {out_dir}")