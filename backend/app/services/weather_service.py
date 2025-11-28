import httpx
from ..core.config import settings
import random

class WeatherService:
    async def get_aqi(self, lat: float = settings.DEFAULT_LAT, lon: float = settings.DEFAULT_LON):
        # Mock implementation if no key is provided or for testing
        if settings.OPENWEATHER_API_KEY == "mock_weather_key":
            return {
                "aqi": random.randint(1, 5),
                "pm2_5": random.uniform(10.0, 300.0),
                "pm10": random.uniform(20.0, 400.0),
                "temp": random.uniform(25.0, 35.0),
                "humidity": random.randint(40, 90),
                "description": "Mock Data: Haze"
            }
            
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={settings.OPENWEATHER_API_KEY}"
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.OPENWEATHER_API_KEY}&units=metric"
        
        async with httpx.AsyncClient() as client:
            try:
                # Fetch AQI
                aqi_response = await client.get(url)
                aqi_data = aqi_response.json()
                
                # Fetch Weather
                weather_response = await client.get(weather_url)
                weather_data = weather_response.json()
                
                return {
                    "aqi": aqi_data['list'][0]['main']['aqi'],
                    "pm2_5": aqi_data['list'][0]['components']['pm2_5'],
                    "pm10": aqi_data['list'][0]['components']['pm10'],
                    "temp": weather_data['main']['temp'],
                    "humidity": weather_data['main']['humidity'],
                    "description": weather_data['weather'][0]['description']
                }
            except Exception as e:
                print(f"Error fetching weather data: {e}")
                # Fallback to mock data on error
                return {
                    "aqi": 3,
                    "pm2_5": 150.0,
                    "pm10": 200.0,
                    "temp": 30.0,
                    "humidity": 70,
                    "description": "Error fetching data, using fallback"
                }

weather_service = WeatherService()
