# level_2/client_agent.py
"""Client agent that connects to MCP weather server."""
import os
import asyncio
from dotenv import load_dotenv
import httpx
import google.generativeai as genai

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
        """Call MCP weather endpoint."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.mcp_url}/tools/get_weather",
                    json={"city": city}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("result", str(data))
        except httpx.ConnectError:
            return "ERROR: Cannot connect. Is weather_mcp.py running?"
        except Exception as e:
            return f"ERROR: {str(e)[:50]}"
    
    def extract_city(self, query: str) -> str | None:
        """Extract city name from query using LLM."""
        prompt = f'Extract only city name from: "{query}"\nReply with city name or NONE'
        try:
            response = self.model.generate_content(prompt)
            city = response.text.strip()
            return None if city.upper() == "NONE" else city
        except:
            return None
    
    async def process_query(self, query: str) -> str:
        """Process weather query."""
        city = self.extract_city(query)
        if not city:
            return "Please specify a city (e.g., 'Weather in Hyderabad?')"
        
        weather_data = await self.call_weather_tool(city)
        if "ERROR" in weather_data:
            return weather_data
        
        # Generate natural response
        prompt = f"User: '{query}'\nData: {weather_data}\nGive brief conversational response."
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return f"According to the weather API, {weather_data}"
    
    async def run(self):
        """Run interactive chat loop."""
        print("\n🌤️  WEATHER AGENT READY")
        print("Example: 'Is it raining in Hyderabad today?'")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                query = input("You: ").strip()
                if not query:
                    continue
                if query.lower() in {"quit", "exit"}:
                    print("Goodbye!")
                    break
                
                response = await self.process_query(query)
                print(f"Agent: {response}\n")
                
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    asyncio.run(WeatherAgent().run())