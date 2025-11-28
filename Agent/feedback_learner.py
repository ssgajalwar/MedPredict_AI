"""
Feedback Learner Module

Implements the adaptive learning mechanism for the Resource Allocator Agent.
It tracks forecast performance and adjusts safety buffers to improve future decisions.
"""

import json
import os
import numpy as np
from datetime import datetime

class FeedbackLearner:
    """
    Manages agent memory and learns from past performance.
    """
    
    def __init__(self, memory_path='agent_memory.json'):
        self.memory_path = memory_path
        self.memory = self._load_memory()
        
    def _load_memory(self):
        """Load agent memory from JSON file"""
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[!] Error loading memory: {e}. Starting fresh.")
        
        # Default memory state
        return {
            "safety_buffer_multiplier": 1.10,  # Start with 10% buffer
            "risk_sensitivity": 0.5,           # Balanced risk taking
            "past_performance": [],
            "last_update": None
        }
    
    def save_memory(self):
        """Save agent memory to JSON file"""
        self.memory["last_update"] = datetime.now().isoformat()
        with open(self.memory_path, 'w') as f:
            json.dump(self.memory, f, indent=2)
            
    def get_safety_buffer(self):
        """Get current safety buffer multiplier"""
        return self.memory.get("safety_buffer_multiplier", 1.10)
    
    def update_learning(self, forecast_val, actual_val):
        """
        Update learning based on forecast vs actual performance.
        
        Logic:
        - If Actual > Forecast (Shortage): Increase buffer (be more safe)
        - If Actual < Forecast (Surplus): Decrease buffer (be more efficient)
        """
        if actual_val is None or forecast_val is None:
            return
            
        error = actual_val - forecast_val
        percent_error = error / forecast_val if forecast_val != 0 else 0
        
        # Record performance
        record = {
            "date": datetime.now().isoformat(),
            "forecast": float(forecast_val),
            "actual": float(actual_val),
            "error": float(error),
            "percent_error": float(percent_error),
            "outcome": "SHORTAGE" if error > 0 else "SURPLUS"
        }
        self.memory["past_performance"].append(record)
        
        # Keep only last 50 records
        if len(self.memory["past_performance"]) > 50:
            self.memory["past_performance"] = self.memory["past_performance"][-50:]
            
        # Adaptive Logic (RL-lite)
        current_buffer = self.memory["safety_buffer_multiplier"]
        learning_rate = 0.01  # Small steps
        
        if error > 0:
            # SHORTAGE: We need more buffer
            # If error was large (>10%), increase buffer more aggressively
            adjustment = learning_rate * (1 + abs(percent_error))
            new_buffer = min(current_buffer + adjustment, 1.50) # Cap at 50% buffer
            print(f"  [LEARNING] Shortage detected (Error: {error:.0f}). Increasing safety buffer: {current_buffer:.3f} -> {new_buffer:.3f}")
        else:
            # SURPLUS: We can reduce buffer
            # Reduce slowly to avoid oscillating
            adjustment = learning_rate * 0.5
            new_buffer = max(current_buffer - adjustment, 1.00) # Floor at 0% buffer
            print(f"  [LEARNING] Surplus detected. Optimizing efficiency: {current_buffer:.3f} -> {new_buffer:.3f}")
            
        self.memory["safety_buffer_multiplier"] = new_buffer
        self.save_memory()
        
        return record
