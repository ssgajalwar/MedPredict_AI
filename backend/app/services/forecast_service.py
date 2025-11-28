import pandas as pd
from pathlib import Path
from typing import Dict, List
import json

class ForecastService:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent.parent / "media"
        self.forecast_path = self.base_path / "forecasts" / "csv"
        
    def get_latest_forecast(self, model: str = "lightgbm") -> Dict:
        """Fetch latest forecast data"""
        try:
            forecast_file = self.forecast_path / f"{model}_forecast_7day.csv"
            
            if not forecast_file.exists():
                # Try alternative model
                forecast_file = self.forecast_path / "xgboost_forecast_7day.csv"
            
            if forecast_file.exists():
                df = pd.read_csv(forecast_file)
                
                # Convert to list of predictions
                forecasts = []
                for _, row in df.iterrows():
                    forecasts.append({
                        "date": row.get('date', row.get('ds', '')),
                        "predicted_patients": int(row.get('prediction', row.get('yhat', 0))),
                        "lower_bound": int(row.get('lower_bound', row.get('yhat_lower', 0))),
                        "upper_bound": int(row.get('upper_bound', row.get('yhat_upper', 0)))
                    })
                
                return {
                    "model": model,
                    "horizon_days": len(forecasts),
                    "forecasts": forecasts,
                    "avg_predicted": int(df['prediction'].mean() if 'prediction' in df.columns else df['yhat'].mean())
                }
            else:
                return self._generate_mock_forecast()
                
        except Exception as e:
            print(f"Error loading forecast data: {e}")
            return self._generate_mock_forecast()
    
    def _generate_mock_forecast(self) -> Dict:
        """Generate mock forecast if no data available"""
        import random
        base = 1200
        forecasts = []
        for i in range(7):
            pred = int(base * (1 + random.uniform(-0.1, 0.2)))
            forecasts.append({
                "date": f"Day {i+1}",
                "predicted_patients": pred,
                "lower_bound": int(pred * 0.9),
                "upper_bound": int(pred * 1.1)
            })
        
        return {
            "model": "mock",
            "horizon_days": 7,
            "forecasts": forecasts,
            "avg_predicted": int(sum(f['predicted_patients'] for f in forecasts) / len(forecasts))
        }
    
    def get_historical_data(self, days: int = 30) -> List[Dict]:
        """Fetch historical patient data for charts"""
        try:
            data_path = self.base_path / "data" / "hospital_data" / "patient_visits.csv"
            df = pd.read_csv(data_path)
            df['visit_date'] = pd.to_datetime(df['visit_date'])
            
            # Group by date and count
            daily_counts = df.groupby('visit_date').size().reset_index(name='count')
            daily_counts = daily_counts.tail(days)
            
            history = []
            for _, row in daily_counts.iterrows():
                history.append({
                    "date": row['visit_date'].strftime("%Y-%m-%d"),
                    "patients": int(row['count'])
                })
            
            return history
        except Exception as e:
            print(f"Error loading historical data: {e}")
            return []

forecast_service = ForecastService()
