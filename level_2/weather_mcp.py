# level_2/weather_mcp.py
"""MCP Tool Server for weather data using FastMCP."""
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
import httpx

load_dotenv()

mcp = FastMCP("weather-service")
API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Mock weather data
MOCK_DATA = {
    "hyderabad": "cloudy with light rain, 27°C",
    "bengaluru": "partly cloudy, 24°C",
    "delhi": "clear sky, 32°C",
    "mumbai": "humid and warm, 30°C",
    "chennai": "sunny, 35°C",
    "kolkata": "thunderstorm, 28°C",
    "pune": "pleasant, 26°C",
    "london": "rainy, 18°C",
    "new york": "partly cloudy, 22°C",
    "tokyo": "sunny, 25°C",
}


@mcp.tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    if not city:
        return "Error: No city provided"
    
    city = city.strip()
    
    # Use mock data if no API key
    if not API_KEY:
        weather = MOCK_DATA.get(city.lower(), "sunny, 30°C")
        return f"Weather in {city}: {weather}"
    
    # Real API call - synchronous version
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                "http://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": API_KEY, "units": "metric"}
            )
            response.raise_for_status()
            data = response.json()
            
            desc = data["weather"][0]["description"]
            temp = round(data["main"]["temp"])
            humidity = data["main"]["humidity"]
            
            return f"Weather in {city}: {desc}, {temp}°C, humidity: {humidity}%"
    except Exception as e:
        # Fallback to mock data on API error
        weather = MOCK_DATA.get(city.lower(), "sunny, 30°C")
        return f"Weather in {city}: {weather} (API unavailable)"


if __name__ == "__main__":
    print("Weather MCP Server Starting")
    print(f"Mode: {'MOCK DATA' if not API_KEY else 'LIVE API'}")
    print("Running on http://localhost:8000")
    print("Available endpoints:")
    print("  POST /tools/call")
    print("  GET /tools/list")
    print("\nPress Ctrl+C to stop")
    
    # Use the correct method for FastMCP 2.0
    mcp.run(port=8000, host="0.0.0.0")