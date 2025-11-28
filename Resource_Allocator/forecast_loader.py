"""
Forecast Loader for Agent C

Loads forecast data from Forecaster models and prepares it for resource allocation.
"""

import pandas as pd
import os
from typing import Dict, Tuple
from datetime import datetime


class ForecastLoader:
    """Load and process forecast data from Forecaster models"""
    
    def __init__(self, forecast_dir='../media/forecast'):
        self.forecast_dir = forecast_dir
        self.forecasts = {}
    
    def load_all_forecasts(self) -> Dict[str, pd.DataFrame]:
        """Load forecasts from all models"""
        models = ['lightgbm', 'xgboost', 'random_forest']
        
        for model in models:
            csv_path = os.path.join(self.forecast_dir, f'{model}_forecast_7day.csv')
            if os.path.exists(csv_path):
                self.forecasts[model] = pd.read_csv(csv_path, parse_dates=['date'])
        
        return self.forecasts
    
    def get_consensus_forecast(self) -> Tuple[pd.DataFrame, float]:
        """
        Get consensus forecast from all models
        
        Returns:
        - Tuple of (forecast_df, confidence_score)
        """
        if not self.forecasts:
            self.load_all_forecasts()
        
        if not self.forecasts:
            raise ValueError("No forecast data found")
        
        # Average forecasts from all models
        all_forecasts = []
        for model, df in self.forecasts.items():
            all_forecasts.append(df['forecast'].values)
        
        consensus = pd.DataFrame({
            'date': self.forecasts[list(self.forecasts.keys())[0]]['date'],
            'forecast': sum(all_forecasts) / len(all_forecasts),
            'lower_ci': min([df['lower_ci'].values for df in self.forecasts.values()]),
            'upper_ci': max([df['upper_ci'].values for df in self.forecasts.values()])
        })
        
        # Calculate confidence (inverse of CI width)
        ci_width = (consensus['upper_ci'] - consensus['lower_ci']).mean()
        confidence = 1.0 / (1.0 + ci_width / consensus['forecast'].mean())
        
        return consensus, confidence
    
    def get_peak_demand(self) -> Tuple[int, datetime]:
        """Get peak predicted demand and date"""
        consensus, _ = self.get_consensus_forecast()
        peak_idx = consensus['forecast'].idxmax()
        return int(consensus.loc[peak_idx, 'forecast']), consensus.loc[peak_idx, 'date']


if __name__ == "__main__":
    loader = ForecastLoader()
    try:
        forecasts = loader.load_all_forecasts()
        print(f"Loaded {len(forecasts)} forecast models")
        
        consensus, conf = loader.get_consensus_forecast()
        print(f"\nConsensus forecast (confidence: {conf:.3f}):")
        print(consensus)
        
        peak, peak_date = loader.get_peak_demand()
        print(f"\nPeak demand: {peak} patients on {peak_date}")
    except Exception as e:
        print(f"Error: {e}")
