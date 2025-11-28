from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Med Predict AI"
    API_V1_STR: str = "/api/v1"
    
    # External API Keys (Load from environment variables)
    NEWS_API_KEY: str = "mock_news_key"
    OPENWEATHER_API_KEY: str = "mock_weather_key"
    
    # Defaults for Mumbai
    DEFAULT_LAT: float = 19.0760
    DEFAULT_LON: float = 72.8777

    class Config:
        env_file = ".env"

settings = Settings()
