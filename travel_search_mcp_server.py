"""
Destination Search MCP Server
Provides tourist attractions, landmarks, and activities for destinations.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="Travel Search MCP Server")

class DestinationRequest(BaseModel):
    destination: str

class DestinationResponse(BaseModel):
    destination: str
    attractions: List[str]
    activities: List[str]
    landmarks: List[str]

# Mock database of destinations
DESTINATIONS_DB = {
    "paris": {
        "attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", "Arc de Triomphe"],
        "activities": ["Seine River Cruise", "Wine Tasting", "Cooking Classes", "Shopping on Champs-Élysées"],
        "landmarks": ["Sacré-Cœur", "Versailles Palace", "Panthéon"]
    },
    "barcelona": {
        "attractions": ["Sagrada Familia", "Park Güell", "Gothic Quarter", "Casa Batlló"],
        "activities": ["Beach Activities", "Tapas Tours", "Flamenco Shows", "Wine Tours"],
        "landmarks": ["La Rambla", "Camp Nou", "Montjuïc"]
    },
    "tokyo": {
        "attractions": ["Tokyo Tower", "Senso-ji Temple", "Imperial Palace", "Shibuya Crossing"],
        "activities": ["Sushi Making Class", "Tea Ceremony", "Sumo Wrestling", "Karaoke"],
        "landmarks": ["Mount Fuji", "Meiji Shrine", "Tokyo Skytree"]
    },
    "new york": {
        "attractions": ["Statue of Liberty", "Central Park", "Times Square", "Empire State Building"],
        "activities": ["Broadway Shows", "Museum Tours", "Food Tours", "Shopping"],
        "landmarks": ["Brooklyn Bridge", "One World Trade Center", "Rockefeller Center"]
    },
    "london": {
        "attractions": ["Big Ben", "Tower of London", "British Museum", "Buckingham Palace"],
        "activities": ["Thames River Cruise", "Afternoon Tea", "West End Shows", "Pub Tours"],
        "landmarks": ["London Eye", "Tower Bridge", "Westminster Abbey"]
    },
    "morocco": {
        "attractions": ["Marrakech Medina", "Hassan II Mosque", "Jardin Majorelle", "Bahia Palace"],
        "activities": ["Desert Safari", "Hammam Experience", "Cooking Classes", "Souk Shopping"],
        "landmarks": ["Chefchaouen", "Fes Medina", "Atlas Mountains"]
    },
    "sidi bennour": {
        "attractions": ["Local Markets", "Traditional Architecture", "Agricultural Sites"],
        "activities": ["Cultural Tours", "Local Cuisine Tasting", "Countryside Walks"],
        "landmarks": ["Historic Center", "Regional Farmlands"]
    }
}

@app.get("/")
def root():
    return {"message": "Travel Search MCP Server", "version": "1.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/tools/search_destination", response_model=DestinationResponse)
def search_destination(request: DestinationRequest) -> DestinationResponse:
    """Search for tourist information about a destination"""
    destination = request.destination.lower().strip()
    
    # Try exact match first
    if destination in DESTINATIONS_DB:
        data = DESTINATIONS_DB[destination]
        return DestinationResponse(
            destination=request.destination,
            attractions=data["attractions"],
            activities=data["activities"],
            landmarks=data["landmarks"]
        )
    
    # Try partial match
    for key in DESTINATIONS_DB:
        if key in destination or destination in key:
            data = DESTINATIONS_DB[key]
            return DestinationResponse(
                destination=request.destination,
                attractions=data["attractions"],
                activities=data["activities"],
                landmarks=data["landmarks"]
            )
    
    # Default response for unknown destinations
    return DestinationResponse(
        destination=request.destination,
        attractions=["Local Museums", "City Center", "Historical Sites"],
        activities=["Cultural Tours", "Local Cuisine", "Walking Tours", "Shopping"],
        landmarks=["Main Square", "Local Parks", "Historic Buildings"]
    )

if __name__ == "__main__":
    print("🌍 Starting Travel Search MCP Server on port 3334...")
    uvicorn.run(app, host="0.0.0.0", port=3334)
