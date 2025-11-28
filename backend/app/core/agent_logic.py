import random
from typing import Dict, List

class AgentLogic:
    def calculate_surge_prediction(self, weather_data: Dict, news_data: List[Dict], events_data: List[Dict]) -> Dict:
        """
        The 'Brain' that combines sensory data to predict patient surge and resource needs.
        """
        base_patients = 1200 # Average daily patients
        surge_factor = 1.0
        reasons = []
        
        # 1. Weather Impact (AQI)
        aqi = weather_data.get('aqi', 1)
        if aqi >= 4:
            surge_factor += 0.15
            reasons.append("High AQI (Respiratory Spike)")
        elif aqi == 3:
            surge_factor += 0.05
            reasons.append("Moderate Pollution")
            
        # 2. News Impact
        high_severity_news = sum(1 for item in news_data if item.get('severity') == 'high')
        if high_severity_news > 0:
            surge_factor += (0.10 * high_severity_news)
            reasons.append(f"Critical Health News ({high_severity_news} alerts)")
            
        # 3. Event Impact
        for event in events_data:
            if event['impact'] == 'high':
                surge_factor += 0.20
                reasons.append(f"Upcoming Event: {event['name']}")
            elif event['impact'] == 'medium':
                surge_factor += 0.10
                reasons.append(f"Upcoming Event: {event['name']}")
                
        predicted_patients = int(base_patients * surge_factor)
        
        # Resource Calculations
        staff_ratio = 1/8 # 1 nurse per 8 patients
        bed_occupancy_rate = 0.75 # Base occupancy
        
        if surge_factor > 1.2:
            bed_occupancy_rate = min(0.95, bed_occupancy_rate * surge_factor)
        
        recommended_staff = int(predicted_patients * staff_ratio)
        current_staff = int(base_patients * staff_ratio) # Assuming staffed for average
        
        staff_shortage = max(0, recommended_staff - current_staff)
        
        return {
            "prediction": {
                "total_patients": predicted_patients,
                "surge_percentage": round((surge_factor - 1) * 100, 1),
                "reasons": reasons
            },
            "resources": {
                "recommended_staff": recommended_staff,
                "current_staff": current_staff,
                "staff_shortage": staff_shortage,
                "bed_occupancy_predicted": round(bed_occupancy_rate * 100, 1),
                "inventory_alert": "Oxygen Cylinders" if aqi >= 4 else "Normal"
            }
        }

agent_logic = AgentLogic()
