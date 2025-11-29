"""
Train Model 4: Anomaly Detection
Trains an Isolation Forest model to detect unusual spikes or patterns in hospital data.
"""

import pandas as pd
import numpy as np
import os
import pickle
import warnings
from sklearn.ensemble import IsolationForest

warnings.filterwarnings('ignore')

class AnomalyDetector:
    def __init__(self, data_path='media/modal_train_data/severity_training_data.csv', output_dir='Agent'):
        self.data_path = data_path
        self.output_dir = output_dir
        self.model = None
        self.feature_columns = None
        
        os.makedirs(output_dir, exist_ok=True)
        
    def train(self):
        print("="*60)
        print("TRAINING MODEL 4: ANOMALY DETECTOR")
        print("="*60)
        
        # Load Data
        if not os.path.exists(self.data_path):
            print(f"❌ Data file not found: {self.data_path}")
            return
            
        df = pd.read_csv(self.data_path)
        print(f"✓ Loaded data: {df.shape}")
        
        # Define Features (exclude target and date columns)
        exclude_cols = ['date', 'daily_alert_level', 'location_id']
        feature_cols = [c for c in df.columns if c not in exclude_cols]
        
        self.feature_columns = feature_cols
        print(f"Features ({len(feature_cols)}): {feature_cols[:10]} ...")
        
        X = df[feature_cols].fillna(0)
        
        # Sort chronologically for proper train/test split
        df_sorted = df.sort_values('date')
        X_sorted = df_sorted[feature_cols].fillna(0)
        
        # Use 80% for training
        split_idx = int(len(X_sorted) * 0.8)
        X_train = X_sorted.iloc[:split_idx]
        X_test = X_sorted.iloc[split_idx:]
        
        print(f"\nTraining on {len(X_train)} samples")
        
        # Train Isolation Forest
        # contamination = expected proportion of outliers (5%)
        model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train)
        print("✓ Model trained")
        
        # Evaluate (optional - just to see how many anomalies detected)
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_anomalies = (train_pred == -1).sum()
        test_anomalies = (test_pred == -1).sum()
        
        print(f"\nAnomalies detected:")
        print(f"  Training set: {train_anomalies}/{len(X_train)} ({train_anomalies/len(X_train)*100:.1f}%)")
        print(f"  Test set:     {test_anomalies}/{len(X_test)} ({test_anomalies/len(X_test)*100:.1f}%)")
        
        self.model = model
        
        # Save Model
        model_path = f'{self.output_dir}/anomaly_detector.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'feature_columns': feature_cols
            }, f)
            
        print(f"\n✓ Model saved to {model_path}")

if __name__ == "__main__":
    detector = AnomalyDetector()
    detector.train()
