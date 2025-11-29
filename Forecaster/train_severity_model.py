"""
Train Model 3: Severity Classification
Trains a RandomForestClassifier to predict daily alert levels (Normal/Alert/Critical).
"""

import pandas as pd
import numpy as np
import os
import pickle
import warnings
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings('ignore')

class SeverityClassifier:
    def __init__(self, data_path='media/modal_train_data/severity_training_data.csv', output_dir='Agent'):
        self.data_path = data_path
        self.output_dir = output_dir
        self.model = None
        self.encoder = None
        self.feature_columns = None
        
        os.makedirs(output_dir, exist_ok=True)
        
    def train(self):
        print("="*60)
        print("TRAINING MODEL 3: SEVERITY CLASSIFIER")
        print("="*60)
        
        # Load Data
        if not os.path.exists(self.data_path):
            print(f"❌ Data file not found: {self.data_path}")
            return
            
        df = pd.read_csv(self.data_path)
        print(f"✓ Loaded data: {df.shape}")
        
        # Define Features and Target
        target_col = 'daily_alert_level'
        
        # Features: Environmental, Event, Time, and aggregated metrics (excluding target)
        # Note: In a real forecasting scenario, we might not have 'total_daily_patient_count' for the future *exactly*,
        # but Model 1 predicts it. So we can use Model 1's output as input here.
        # For training, we use the actuals.
        
        feature_cols = [
            'total_daily_patient_count', 'average_daily_severity', 
            'total_confirmed_cases', 'total_suspected_cases', 'total_deaths',
            'temperature_avg', 'temperature_min', 'temperature_max', 'humidity_percent',
            'rainfall_mm', 'wind_speed_kmh', 
            'aqi_level', 'pm25', 'pm10', 'no2', 'so2', 'co', 'ozone', 'pollen_count',
            'is_public_holiday', 'event_impact_multiplier',
            'day_of_week', 'month', 'day_of_year', 'week_of_year', 'quarter', 'is_weekend'
        ]
        
        # Ensure columns exist
        feature_cols = [c for c in feature_cols if c in df.columns]
        self.feature_columns = feature_cols
        
        print(f"Features ({len(feature_cols)}): {feature_cols}")
        print(f"Target: {target_col}")
        
        X = df[feature_cols].fillna(0)
        y = df[target_col]
        
        # Encode Target
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        self.encoder = le
        
        print(f"Classes: {le.classes_}")
        
        # Train-Test Split
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y_encoded[:split_idx], y_encoded[split_idx:]
        
        print(f"\nTraining on {len(X_train)} samples, Testing on {len(X_test)} samples")
        
        # Train Model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        print("\nEvaluation:")
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        print(f"  Accuracy: {acc:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=le.classes_))
        
        self.model = model
        
        # Save Model and Encoder
        model_path = f'{self.output_dir}/severity_classifier.pkl'
        encoder_path = f'{self.output_dir}/severity_label_encoder.pkl'
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
            
        with open(encoder_path, 'wb') as f:
            pickle.dump(le, f)
            
        print(f"\n✓ Model saved to {model_path}")
        print(f"✓ Encoder saved to {encoder_path}")

if __name__ == "__main__":
    classifier = SeverityClassifier()
    classifier.train()
