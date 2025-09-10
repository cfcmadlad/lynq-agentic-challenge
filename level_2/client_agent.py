# level_2/client_agent.py
"""Client agent that connects to MCP weather server."""
import os
import asyncio
from dotenv import load_dotenv
import httpx
import google.generativeai as genai
import json

load_dotenv()


class WeatherAgent:
    """Agent that processes weather queries using MCP and Gemini."""
    
    def __init__(self):
        self.mcp_url = "http://localhost:8000"
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise SystemExit("ERROR: Set GEMINI_API_KEY in .env file")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    async def call_weather_tool(self, city: str) -> str:
        """Call MCP weather endpoint using correct FastMCP 2.0 format."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Correct FastMCP 2.0 tool calling format
                response = await client.post(
                    f"{self.mcp_url}/tools/call",
                    json={
                        "name": "get_weather",
                        "arguments": {"city": city}
                    },
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
                
                # Handle different response formats
                if "content" in data and isinstance(data["content"], list):
                    # Extract text from content array
                    for item in data["content"]:
                        if item.get("type") == "text":
                            return item.get("text", str(data))
                
                # Fallback for other formats
                return data.get("content", data.get("result", str(data)))
                
        except httpx.ConnectError:
            return "ERROR: Cannot connect to weather server. Is weather_mcp.py running?"
        except httpx.TimeoutException:
            return "ERROR: Weather service timeout. Please try again."
        except httpx.HTTPStatusError as e:
            return f"ERROR: Weather service returned {e.response.status_code}"
        except json.JSONDecodeError:
            return "ERROR: Invalid response format from weather service"
        except Exception as e:
            return f"ERROR: {str(e)[:100]}"
    
    def extract_city(self, query: str) -> str | None:
        """Extract city name from query using LLM."""
        prompt = f'''Extract the city name from this weather query: "{query}"

Rules:
- Return only the city name (e.g., "London", "New York", "Hyderabad")
- If no city is mentioned, return "NONE"
- Don't include country names unless necessary for disambiguation

Examples:
- "Weather in Paris" → "Paris"
- "Is it raining in Tokyo today?" → "Tokyo"
- "What's the weather like?" → "NONE"

City name:'''
        
        try:
            response = self.model.generate_content(prompt)
            city = response.text.strip().strip('"\'')
            return None if city.upper() == "NONE" else city
        except Exception:
            # Fallback: simple keyword extraction
            query_lower = query.lower()
            common_cities = ["hyderabad", "bangalore", "bengaluru", "delhi", "mumbai", 
                           "chennai", "kolkata", "pune", "london", "paris", "tokyo", "new york"]
            for city in common_cities:
                if city in query_lower:
                    return city.title()
            return None
    
    async def process_query(self, query: str) -> str:
        """Process weather query end-to-end."""
        if not query.strip():
            return "Please ask me about the weather in a specific city."
        
        # Extract city name
        city = self.extract_city(query)
        if not city:
            return "I need a city name to check the weather. Try: 'What's the weather in Hyderabad?'"
        
        print(f"Looking up weather for: {city}")
        
        # Get weather data from MCP server
        weather_data = await self.call_weather_tool(city)
        if weather_data.startswith("ERROR"):
            return weather_data
        
        # Generate natural response using LLM
        prompt = f'''You are a helpful weather assistant. 

User asked: "{query}"
Weather data: {weather_data}

Provide a natural, conversational response about the weather. Keep it brief and friendly.

Response:'''
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Fallback response
            return f"Here's what I found: {weather_data}"
    
    async def check_server_status(self) -> bool:
        """Check if MCP server is running."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.mcp_url}/tools/list")
                return response.status_code == 200
        except Exception:
            return False
    
    async def run(self):
        """Run interactive chat loop."""
        print("Weather Agent Starting")
        print("=" * 40)
        
        # Check server status
        if not await self.check_server_status():
            print("WARNING: Weather MCP server not responding!")
            print("Make sure to run: python level_2/weather_mcp.py")
            print("Then restart this agent.")
            print()
        
        print("Ask me about weather in any city!")
        print("Examples:")
        print("  'What's the weather in Hyderabad?'")
        print("  'Is it raining in London today?'")
        print("  'How's the weather in Tokyo?'")
        print("\nType 'quit' to exit")
        print("-" * 40)
        
        while True:
            try:
                query = input("\nYou: ").strip()
                
                if not query:
                    continue
                    
                if query.lower() in {"quit", "exit", "bye", "q"}:
                    print("\nGoodbye!")
                    break
                
                # Process the query
                print("Agent: Processing...", end=" ", flush=True)
                response = await self.process_query(query)
                print(f"\rAgent: {response}")
                
            except (KeyboardInterrupt, EOFError):
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again or type 'quit' to exit.")


async def main():
    """Main entry point."""
    try:
        agent = WeatherAgent()
        await agent.run()
    except SystemExit as e:
        print(f"\nStartup Error: {e}")
        print("\nSetup Instructions:")
        print("1. Create a .env file with: GEMINI_API_KEY=your_api_key_here")
        print("2. Get a free API key from: https://makersuite.google.com/app/apikey")
        print("3. Optionally add: OPENWEATHER_API_KEY=your_weather_api_key")
    except Exception as e:
        print(f"\nUnexpected Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())