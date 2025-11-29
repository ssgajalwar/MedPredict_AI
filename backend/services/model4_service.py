"""
Model 4 Service: Anomaly Detection
Loads anomaly_detector.pkl and provides anomaly detection capabilities.
"""

import pandas as pd
import pickle
from pathlib import Path

class AnomalyDetectionService:
    def __init__(self, models_dir='backend/models'):
        self.models_dir = Path(models_dir)
        self.model = None
        self.feature_columns = None
        
        self._load_model()
        
    def _load_model(self):
        """Load the anomaly detector model"""
        model_path = self.models_dir / 'anomaly_detector.pkl'
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
            
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            self.model = model_data['model']
            self.feature_columns = model_data['feature_columns']
            
        print(f"✓ Loaded anomaly detector from {model_path}")
        
    def detect(self, features_df):
        """Detect anomalies in the given data"""
        # Ensure all required features are present
        X = features_df[self.feature_columns].fillna(0)
        
        # Predict (-1 for anomalies, 1 for normal)
        predictions = self.model.predict(X)
        scores = self.model.score_samples(X)
        
        # Create result
        result = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            is_anomaly = pred == -1
            result.append({
                'is_anomaly': bool(is_anomaly),
                'anomaly_score': float(score),
                'severity': self._get_severity(score) if is_anomaly else 'normal'
            })
            
        return result
        
    def _get_severity(self, score):
        """Determine anomaly severity based on score"""
        # Lower scores indicate more anomalous
        if score < -0.5:
            return 'high'
        elif score < -0.3:
            return 'medium'
        else:
            return 'low'
            
    def get_anomaly_summary(self, anomalies):
        """Get summary of detected anomalies"""
        total = len(anomalies)
        anomaly_count = sum(1 for a in anomalies if a['is_anomaly'])
        
        if anomaly_count == 0:
            return {
                'total_records': total,
                'anomaly_count': 0,
                'anomaly_percentage': 0.0,
                'status': 'No anomalies detected',
                'message': 'All data points are within normal patterns.'
            }
            
        severity_counts = {}
        for a in anomalies:
            if a['is_anomaly']:
                sev = a['severity']
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                
        return {
            'total_records': total,
            'anomaly_count': anomaly_count,
            'anomaly_percentage': round((anomaly_count / total) * 100, 2),
            'severity_breakdown': severity_counts,
            'status': 'Anomalies detected',
            'message': f'{anomaly_count} unusual patterns detected. Review recommended.'
        }
