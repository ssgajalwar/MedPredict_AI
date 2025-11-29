import httpx
from ..core.config import settings
import random
import joblib
import pandas as pd
import os

class NewsService:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml', 'advisory_model.pkl')
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                print("Advisory Model loaded successfully")
            else:
                print(f"Advisory Model not found at {model_path}")
        except Exception as e:
            print(f"Error loading Advisory Model: {e}")

    async def get_health_news(self, query: str = "health india"):
        if settings.NEWS_API_KEY == "mock_news_key":
            return [
                {"title": "Flu cases rise in Mumbai due to changing weather", "source": "Mock News", "severity": "medium"},
                {"title": "New guidelines issued for dengue prevention", "source": "Health Daily", "severity": "low"},
                {"title": "Air quality worsens, respiratory cases expected to spike", "source": "City Watch", "severity": "high"}
            ]

        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={settings.NEWS_API_KEY}&sortBy=publishedAt&language=en"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                data = response.json()
                articles = data.get('articles', [])[:5] # Get top 5
                
                # Simple keyword based severity analysis
                results = []
                for art in articles:
                    severity = "low"
                    title_lower = art['title'].lower()
                    if any(x in title_lower for x in ['outbreak', 'epidemic', 'surge', 'spike', 'severe', 'death']):
                        severity = "high"
                    elif any(x in title_lower for x in ['rise', 'alert', 'warning', 'spread']):
                        severity = "medium"
                        
                    results.append({
                        "title": art['title'],
                        "source": art['source']['name'],
                        "url": art['url'],
                        "severity": severity
                    })
                return results
            except Exception as e:
                print(f"Error fetching news: {e}")
                return []

    def get_patient_advisory(self, aqi: int, rainfall: int, temperature: int, waiting_time: int):
        """
        Predict advisory level using the trained model
        """
        if not self.model:
            # Fallback logic if model is not loaded
            score = 0
            if aqi > 200: score += 2
            elif aqi > 100: score += 1
            if rainfall > 50: score += 1
            if waiting_time > 60: score += 2
            elif waiting_time > 30: score += 1
            
            risk = 'High' if score >= 4 else 'Moderate' if score >= 2 else 'Low'
        else:
            # Predict using model
            input_data = pd.DataFrame([[aqi, rainfall, temperature, waiting_time]], 
                                    columns=['aqi', 'rainfall', 'temperature', 'waiting_time'])
            risk = self.model.predict(input_data)[0]
            
        # Generate Advisory Content (to be fed to LLM)
        advisory_data = {
            "risk_level": risk,
            "metrics": {
                "aqi": aqi,
                "rainfall": rainfall,
                "temperature": temperature,
                "hospital_waiting_time": waiting_time
            },
            "context": f"Current AQI is {aqi}, Rainfall is {rainfall}mm, Waiting time is {waiting_time} mins.",
            "recommended_action": "Stay indoors" if risk == "High" else "Wear mask" if risk == "Moderate" else "Normal activity",
            "sms_template_prompt": f"Generate a short, urgent SMS for patients about {risk} health risk due to AQI {aqi} and high hospital load."
        }
        
        return advisory_data

news_service = NewsService()
