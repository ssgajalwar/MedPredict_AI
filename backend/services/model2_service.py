"""
Model 2 Service: Department-wise Distribution
Loads department_distribution_predictor.pkl and provides department predictions.
"""

import pandas as pd
import pickle
from pathlib import Path
from datetime import datetime, timedelta

class DepartmentDistributionService:
    def __init__(self, models_dir='backend/models', data_dir='backend/data'):
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        self.model = None
        self.feature_columns = None
        self.target_columns = None
        self.historical_data = None
        
        self._load_model()
        self._load_data()
        
    def _load_model(self):
        """Load the department distribution model"""
        model_path = self.models_dir / 'department_distribution_predictor.pkl'
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
            
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            self.model = model_data['model']
            self.feature_columns = model_data['feature_columns']
            self.target_columns = model_data['target_columns']
            
        print(f"✓ Loaded department distribution model from {model_path}")
        print(f"  Departments: {len(self.target_columns)}")
        
    def _load_data(self):
        """Load historical department data"""
        data_path = self.data_dir / 'department_training_data.csv'
        if data_path.exists():
            self.historical_data = pd.read_csv(data_path, parse_dates=['date'])
            print(f"✓ Loaded department historical data: {len(self.historical_data)} records")
        else:
            print(f"⚠ Department data not found: {data_path}")
            
    def predict(self, features_df):
        """Predict department-wise patient volumes"""
        X = features_df[self.feature_columns].fillna(0)
        predictions = self.model.predict(X)
        
        # Create result with department names
        result = []
        for i, row in enumerate(predictions):
            dept_predictions = {
                dept: int(pred) for dept, pred in zip(self.target_columns, row)
            }
            result.append(dept_predictions)
            
        return result
        
    def get_department_utilization(self):
        """Get current department utilization percentages"""
        if self.historical_data is None:
            return []
            
        # Get latest data
        latest = self.historical_data.iloc[-1]
        
        # Calculate utilization for each department
        utilization = []
        for dept in self.target_columns:
            if dept in latest:
                count = latest[dept]
                # Assume max capacity is 2x average
                avg = self.historical_data[dept].mean()
                max_capacity = avg * 2
                util_pct = min(100, (count / max_capacity) * 100)
                
                utilization.append({
                    'name': dept.replace('_', ' ').title(),
                    'utilization': round(util_pct, 1),
                    'current_patients': int(count)
                })
                
        return sorted(utilization, key=lambda x: x['utilization'], reverse=True)
