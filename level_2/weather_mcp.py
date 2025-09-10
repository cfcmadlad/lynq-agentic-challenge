# level_2/weather_mcp.py
"""Minimal HTTP wrapper for the weather tool.
Provides:
  GET  /tools/list
  POST /tools/call
This calls the local `get_weather` function (so no dependency on FastMCP internals).
"""
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

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


def get_weather(city: str) -> str:
    """Get current weather for a city. Returns a short human-friendly string."""
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
                params={"q": city, "appid": API_KEY, "units": "metric"},
            )
            response.raise_for_status()
            data = response.json()

            desc = data["weather"][0]["description"]
            temp = round(data["main"]["temp"])
            humidity = data["main"]["humidity"]

            return f"Weather in {city}: {desc}, {temp}°C, humidity: {humidity}%"
    except Exception:
        # Fallback to mock data on API error
        weather = MOCK_DATA.get(city.lower(), "sunny, 30°C")
        return f"Weather in {city}: {weather} (API unavailable)"


# ---------- HTTP server (FastAPI) ----------
# This provides the endpoints your client expects:
#  GET  /tools/list  -> {"tools": ["get_weather"]}
#  POST /tools/call  -> {"content": [{"type": "text", "text": "<result>"}]}
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict

app = FastAPI(title="Weather MCP HTTP wrapper")

TOOL_NAMES = ["get_weather"]


@app.get("/tools/list")
async def tools_list():
    return {"tools": TOOL_NAMES}


class CallBody(BaseModel):
    name: str
    arguments: Dict[str, Any] = {}


@app.post("/tools/call")
async def tools_call(body: CallBody):
    if body.name != "get_weather":
        raise HTTPException(status_code=400, detail="Unknown tool")

    # Expecting arguments: {"city": "<city name>"}
    city = None
    if isinstance(body.arguments, dict):
        city = body.arguments.get("city") or body.arguments.get("City") or body.arguments.get("location")

    if not city:
        # Accept query-like call as fallback
        raise HTTPException(status_code=400, detail="Missing 'city' argument")

    # Call the local get_weather function synchronously (fast)
    result_text = get_weather(str(city))

    # Return shape compatible with multiple FastMCP client expectations:
    # Provide both 'result' and 'content' list with a text item.
    return {
        "result": result_text,
        "content": [{"type": "text", "text": result_text}],
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    print("Weather MCP Server Starting")
    print(f"Mode: {'MOCK DATA' if not API_KEY else 'LIVE API'}")
    print(f"Running on http://{host}:{port}")
    print("Available endpoints:")
    print("  POST /tools/call")
    print("  GET  /tools/list")
    print("\nPress Ctrl+C to stop\n")

    import uvicorn

    # Use the app object directly so we don't need to import by module path
    uvicorn.run(app, host=host, port=port)

