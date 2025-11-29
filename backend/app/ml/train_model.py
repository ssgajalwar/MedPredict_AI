import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def generate_and_train():
    # 1. Generate Synthetic Data
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'aqi': np.random.randint(50, 500, n_samples),
        'rainfall': np.random.randint(0, 100, n_samples), # mm
        'temperature': np.random.randint(10, 45, n_samples), # Celsius
        'waiting_time': np.random.randint(5, 120, n_samples) # minutes
    }
    
    df = pd.DataFrame(data)
    
    # Define Logic for Target (Advisory Level)
    # 0: Low Risk, 1: Moderate Risk, 2: High Risk
    def get_risk(row):
        score = 0
        if row['aqi'] > 200: score += 2
        elif row['aqi'] > 100: score += 1
        
        if row['rainfall'] > 50: score += 1
        
        if row['waiting_time'] > 60: score += 2
        elif row['waiting_time'] > 30: score += 1
        
        if score >= 4: return 'High'
        elif score >= 2: return 'Moderate'
        else: return 'Low'

    df['risk_level'] = df.apply(get_risk, axis=1)
    
    # Save Master CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'advisory_data.csv')
    df.to_csv(csv_path, index=False)
    print(f"Master CSV saved to {csv_path}")
    
    # 2. Train Model
    X = df[['aqi', 'rainfall', 'temperature', 'waiting_time']]
    y = df['risk_level']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    accuracy = model.score(X_test, y_test)
    print(f"Model Accuracy: {accuracy:.2f}")
    
    # 3. Save Model
    model_path = os.path.join(os.path.dirname(__file__), 'advisory_model.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    generate_and_train()
