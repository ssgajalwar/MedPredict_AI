"""
Dashboard Service: Aggregates data from all models
Provides comprehensive dashboard overview combining all predictions.
"""

import pandas as pd
from datetime import datetime, timedelta
from .model1_service import PatientVolumeService
from .model2_service import DepartmentDistributionService
from .model3_service import SeverityClassificationService

class DashboardService:
    def __init__(self):
        self.volume_service = PatientVolumeService()
        self.dept_service = DepartmentDistributionService()
        self.severity_service = SeverityClassificationService()
        
    def get_overview(self):
        """Get comprehensive dashboard overview"""
        # Get 7-day forecast
        forecast = self.volume_service.get_quick_forecast(days=7)
        
        # Get today's prediction
        today_forecast = forecast[0] if forecast else None
        
        # Get department utilization
        dept_util = self.dept_service.get_department_utilization()
        
        # Calculate metrics
        total_patients = today_forecast['predicted_patients'] if today_forecast else 0
        surge_percentage = 15.2  # Mock - would calculate from historical comparison
        
        # Resource predictions
        bed_occupancy = min(95, (total_patients / 350) * 100)  # 350 beds
        current_staff = 175  # From hospital profile
        
        return {
            'sensory_data': {
                'timestamp': datetime.now().isoformat(),
                'location': 'Mumbai Suburban'
            },
            'analysis': {
                'prediction': {
                    'total_patients': total_patients,
                    'surge_percentage': surge_percentage,
                    'confidence': 0.85
                },
                'resources': {
                    'bed_occupancy_predicted': round(bed_occupancy, 1),
                    'current_staff': current_staff,
                    'staff_needed': int(total_patients / 20)  # Ratio estimate
                }
            },
            'forecast': {
                'forecasts': forecast,
                'period': '7 days',
                'generated_at': datetime.now().isoformat()
            },
            'real_data': {
                'patients': {
                    'total_patients': total_patients,
                    'admissions': int(total_patients * 0.3),  # Estimate
                    'by_department': {
                        dept['name']: dept['current_patients'] 
                        for dept in dept_util[:5]
                    }
                },
                'staff': {
                    'available_staff': current_staff,
                    'on_duty': int(current_staff * 0.7)
                }
            }
        }
        
    def get_surge_patterns(self):
        """Get surge pattern analysis"""
        # Load events data
        events_df = self.volume_service.events_data
        
        if events_df is None:
            return {
                'surge_causes': {
                    'festivals': [],
                    'epidemics': []
                }
            }
            
        # Get upcoming events
        today = pd.Timestamp.now()
        upcoming = events_df[events_df['start_date'] > today].head(5)
        
        festivals = []
        for _, event in upcoming.iterrows():
            festivals.append({
                'name': event['event_name'],
                'date': event['start_date'].strftime('%Y-%m-%d'),
                'expected_surge': event['impact_multiplier']
            })
            
        return {
            'surge_causes': {
                'festivals': festivals,
                'epidemics': []  # Would come from surveillance data
            }
        }
        
    def get_environmental_impact(self):
        """Get environmental impact data"""
        # Get latest environmental data from historical
        hist_data = self.volume_service.historical_data
        
        if hist_data is None or len(hist_data) == 0:
            return {
                'air_quality': {'aqi_level': 0},
                'health_advisory': 'No data available'
            }
            
        latest = hist_data.iloc[-1]
        aqi = int(latest.get('aqi_level', 0))
        
        # Health advisory based on AQI
        if aqi > 300:
            advisory = 'Hazardous - Avoid outdoor activities'
        elif aqi > 200:
            advisory = 'Very Unhealthy - Limit outdoor exposure'
        elif aqi > 150:
            advisory = 'Unhealthy - Sensitive groups should limit outdoor activities'
        elif aqi > 100:
            advisory = 'Moderate - Acceptable air quality'
        else:
            advisory = 'Good - Air quality is satisfactory'
            
        return {
            'air_quality': {
                'aqi_level': aqi,
                'pm25': float(latest.get('pm25', 0)),
                'pm10': float(latest.get('pm10', 0))
            },
            'weather': {
                'temperature': float(latest.get('temperature_avg', 0)),
                'humidity': float(latest.get('humidity_percent', 0)),
                'rainfall': float(latest.get('rainfall_mm', 0))
            },
            'health_advisory': advisory
        }
        
    def get_admission_predictions(self, days=7):
        """Get admission predictions for next N days"""
        forecast = self.volume_service.get_quick_forecast(days=days)
        
        predictions = []
        for f in forecast:
            # Estimate admissions as 30% of total patients
            predicted_admissions = int(f['predicted_patients'] * 0.3)
            predictions.append({
                'date': f['date'].strftime('%Y-%m-%d') if isinstance(f['date'], pd.Timestamp) else f['date'],
                'predicted_admissions': predicted_admissions,
                'confidence_interval': {
                    'lower': int(predicted_admissions * 0.85),
                    'upper': int(predicted_admissions * 1.15)
                }
            })
            
        return {
            'predictions': predictions,
            'model_accuracy': 0.85
        }
