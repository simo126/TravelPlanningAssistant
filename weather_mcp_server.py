"""
Weather MCP Server
Provides weather information for destinations and travel dates.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime

app = FastAPI(title="Weather MCP Server")

class WeatherRequest(BaseModel):
    destination: str
    date: Optional[str] = None  # Optional date in YYYY-MM-DD format

class WeatherResponse(BaseModel):
    destination: str
    date: Optional[str]
    temperature: str
    conditions: str
    recommendation: str

# Mock weather database
WEATHER_DB = {
    "paris": {
        "winter": {"temp": "5-10°C", "conditions": "Cold and rainy", "rec": "Bring warm coat and umbrella"},
        "spring": {"temp": "12-18°C", "conditions": "Mild and pleasant", "rec": "Light jacket recommended"},
        "summer": {"temp": "20-28°C", "conditions": "Warm and sunny", "rec": "Perfect for outdoor activities"},
        "fall": {"temp": "10-16°C", "conditions": "Cool and crisp", "rec": "Bring layers"}
    },
    "barcelona": {
        "winter": {"temp": "10-15°C", "conditions": "Mild and sunny", "rec": "Light jacket sufficient"},
        "spring": {"temp": "15-22°C", "conditions": "Pleasant", "rec": "Great for beach and sightseeing"},
        "summer": {"temp": "25-30°C", "conditions": "Hot and sunny", "rec": "Sunscreen and hydration essential"},
        "fall": {"temp": "18-24°C", "conditions": "Warm", "rec": "Ideal weather for all activities"}
    },
    "tokyo": {
        "winter": {"temp": "2-10°C", "conditions": "Cold and dry", "rec": "Heavy coat needed"},
        "spring": {"temp": "10-18°C", "conditions": "Cherry blossom season", "rec": "Perfect time to visit"},
        "summer": {"temp": "25-32°C", "conditions": "Hot and humid", "rec": "Stay hydrated, indoor activities recommended"},
        "fall": {"temp": "15-22°C", "conditions": "Pleasant", "rec": "Beautiful autumn colors"}
    },
    "morocco": {
        "winter": {"temp": "12-20°C", "conditions": "Mild and pleasant", "rec": "Light layers recommended"},
        "spring": {"temp": "18-26°C", "conditions": "Warm and sunny", "rec": "Great for desert tours"},
        "summer": {"temp": "28-38°C", "conditions": "Very hot", "rec": "Early morning activities, stay hydrated"},
        "fall": {"temp": "20-28°C", "conditions": "Warm", "rec": "Ideal travel season"}
    }
}

def get_season(month: int) -> str:
    """Determine season from month"""
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "fall"

@app.get("/")
def root():
    return {"message": "Weather MCP Server", "version": "1.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/tools/get_weather", response_model=WeatherResponse)
def get_weather(request: WeatherRequest) -> WeatherResponse:
    """Get weather information for a destination"""
    destination = request.destination.lower().strip()
    
    # Determine season
    if request.date:
        try:
            date_obj = datetime.strptime(request.date, "%Y-%m-%d")
            season = get_season(date_obj.month)
        except:
            season = get_season(datetime.now().month)
    else:
        season = get_season(datetime.now().month)
    
    # Find weather data
    weather_data = None
    for key in WEATHER_DB:
        if key in destination or destination in key:
            weather_data = WEATHER_DB[key][season]
            break
    
    # Default weather if not found
    if not weather_data:
        weather_data = {
            "temp": "15-25°C",
            "conditions": "Generally pleasant",
            "rec": "Check local forecast before departure"
        }
    
    return WeatherResponse(
        destination=request.destination,
        date=request.date,
        temperature=weather_data["temp"],
        conditions=weather_data["conditions"],
        recommendation=weather_data["rec"]
    )

if __name__ == "__main__":
    print("🌤️  Starting Weather MCP Server on port 3335...")
    uvicorn.run(app, host="0.0.0.0", port=3335)
