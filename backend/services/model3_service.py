"""
Model 3 Service: Severity Classification
Loads severity_classifier.pkl and provides alert level predictions.
"""

import pandas as pd
import pickle
from pathlib import Path

class SeverityClassificationService:
    def __init__(self, models_dir='backend/models'):
        self.models_dir = Path(models_dir)
        self.model = None
        self.encoder = None
        
        self._load_model()
        
    def _load_model(self):
        """Load the severity classifier and label encoder"""
        model_path = self.models_dir / 'severity_classifier.pkl'
        encoder_path = self.models_dir / 'severity_label_encoder.pkl'
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        if not encoder_path.exists():
            raise FileNotFoundError(f"Encoder not found: {encoder_path}")
            
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
            
        with open(encoder_path, 'rb') as f:
            self.encoder = pickle.load(f)
            
        print(f"✓ Loaded severity classifier from {model_path}")
        print(f"  Classes: {list(self.encoder.classes_)}")
        
    def classify(self, features_df):
        """Classify severity level for given features"""
        # Expected features
        feature_cols = [
            'total_daily_patient_count', 'average_daily_severity',
            'total_confirmed_cases', 'total_suspected_cases', 'total_deaths',
            'temperature_avg', 'temperature_min', 'temperature_max', 'humidity_percent',
            'rainfall_mm', 'wind_speed_kmh',
            'aqi_level', 'pm25', 'pm10', 'no2', 'so2', 'co', 'ozone', 'pollen_count',
            'is_public_holiday', 'event_impact_multiplier',
            'day_of_week', 'month', 'day_of_year', 'week_of_year', 'quarter', 'is_weekend'
        ]
        
        # Filter available features
        available_features = [col for col in feature_cols if col in features_df.columns]
        X = features_df[available_features].fillna(0)
        
        # Predict
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        # Decode labels
        labels = self.encoder.inverse_transform(predictions)
        
        # Create result
        result = []
        for i, (label, probs) in enumerate(zip(labels, probabilities)):
            result.append({
                'alert_level': label,
                'confidence': float(max(probs)),
                'probabilities': {
                    cls: float(prob) 
                    for cls, prob in zip(self.encoder.classes_, probs)
                }
            })
            
        return result
        
    def get_alert_summary(self, alert_level):
        """Get human-readable summary for alert level"""
        summaries = {
            'Normal': {
                'status': 'Normal Operations',
                'color': 'green',
                'message': 'Hospital operations are within normal parameters.',
                'actions': []
            },
            'Alert': {
                'status': 'Elevated Alert',
                'color': 'yellow',
                'message': 'Increased patient volume or severity detected.',
                'actions': [
                    'Monitor resource availability',
                    'Prepare additional staff if needed',
                    'Review supply inventory'
                ]
            },
            'Critical': {
                'status': 'Critical Alert',
                'color': 'red',
                'message': 'High patient volume, severe cases, or epidemic outbreak detected.',
                'actions': [
                    'Activate emergency protocols',
                    'Call in additional staff',
                    'Coordinate with other facilities',
                    'Ensure adequate supply levels'
                ]
            }
        }
        
        return summaries.get(alert_level, summaries['Normal'])
