from datetime import date, timedelta

class CalendarService:
    async def get_upcoming_events(self):
        # Mocking Indian Holidays and Events logic
        # In a real app, this could connect to a Google Calendar API or a dedicated holiday API
        
        today = date.today()
        events = []
        
        # Mock events database
        mock_events = [
            {"name": "Diwali", "date": date(2025, 10, 20), "impact": "high", "type": "festival"},
            {"name": "Monsoon Season Start", "date": date(2025, 6, 10), "impact": "medium", "type": "seasonal"},
            {"name": "New Year", "date": date(2025, 1, 1), "impact": "high", "type": "festival"},
            {"name": "Holi", "date": date(2025, 3, 14), "impact": "high", "type": "festival"},
             {"name": "Ganesh Chaturthi", "date": date(2025, 8, 27), "impact": "high", "type": "festival"}
        ]
        
        for event in mock_events:
            # Check if event is within next 30 days
            days_until = (event['date'] - today).days
            if 0 <= days_until <= 30:
                events.append({
                    "name": event['name'],
                    "date": event['date'].isoformat(),
                    "days_until": days_until,
                    "impact": event['impact'],
                    "type": event['type']
                })
        
        # If no events found in mock DB, return a generic one for demo purposes if requested
        if not events:
             events.append({
                "name": "Local Festival (Mock)",
                "date": (today + timedelta(days=5)).isoformat(),
                "days_until": 5,
                "impact": "medium",
                "type": "festival"
            })

        return events

calendar_service = CalendarService()
