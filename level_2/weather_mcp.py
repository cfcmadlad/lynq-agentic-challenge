# level2/weather_mcp.py
import os
import sys
# enforce python version early
if sys.version_info < (3, 10):
    raise SystemExit("Python 3.10+ is required. Upgrade Python or change type hints.")

from dotenv import load_dotenv
from fastmcp import FastMCP
import httpx

load_dotenv()

mcp = FastMCP("weather-service")

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
USE_MOCK = not bool(WEATHER_API_KEY)


@mcp.tool()
async def get_weather(city: str) -> str:
    """
    get current weather for a city
    returns weather description and temperature
    """
    if not city:
        return "no city provided"

    if USE_MOCK:
        mock_data = {
            "hyderabad": "cloudy with light rain, 27°C",
            "bengaluru": "partly cloudy, 24°C",
            "delhi": "clear sky, 32°C",
            "mumbai": "humid and warm, 30°C",
            "chennai": "sunny, 35°C",
            "kolkata": "thunderstorm, 28°C",
            "pune": "pleasant, 26°C",
        }
        city_lower = city.strip().lower()
        if city_lower in mock_data:
            return f"weather in {city}: {mock_data[city_lower]}"
        return f"weather in {city}: sunny, 30°C (mock data)"

    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            weather = data.get("weather", [{}])[0].get("description", "unknown")
            temp = round(data.get("main", {}).get("temp", 0))
            feels_like = round(data.get("main", {}).get("feels_like", 0))
            humidity = data.get("main", {}).get("humidity", "unknown")

            return (
                f"weather in {city}: {weather}, {temp}°C "
                f"(feels like {feels_like}°C), humidity: {humidity}%"
            )

    except Exception as e:
        # return mock fallback but include error for debugging
        return f"weather in {city}: sunny, 30°C (mock data - api error: {e})"


if __name__ == "__main__":
    import uvicorn

    print("starting weather mcp server...")
    print(f"using {'mock data' if USE_MOCK else 'openweather api'}")
    print("server running on http://localhost:8000")

    uvicorn.run(
        mcp.get_asgi_app(),
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
