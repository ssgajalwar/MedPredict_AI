import httpx
from ..core.config import settings
import random

class NewsService:
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

news_service = NewsService()
