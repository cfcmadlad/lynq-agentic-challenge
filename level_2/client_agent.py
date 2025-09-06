# level2/client_agent.py
import os
import asyncio

# enforce python version early
import python_version_check  # raises SystemExit if Python < 3.10

from dotenv import load_dotenv
import httpx
import google.generativeai as genai

load_dotenv()


class WeatherAgent:
    def __init__(self):
        self.mcp_url = os.getenv("MCP_URL", "http://localhost:8000")
        self.setup_gemini()

    def setup_gemini(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise SystemExit("set GEMINI_API_KEY in .env")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def call_weather_tool(self, city: str):
        """Call the MCP tool endpoint and return the raw result string."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    response = await client.post(
                        f"{self.mcp_url}/tools/get_weather",
                        json={"city": city},
                    )
                except httpx.RequestError as e:
                    # networking-level problems (DNS, refused connection, etc)
                    return f"network error calling weather service: {e}"

                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    # non-2xx response
                    return f"weather service returned {e.response.status_code}: {e.response.text}"

                # try JSON first, fall back to text
                try:
                    data = response.json()
                    if isinstance(data, dict) and "result" in data:
                        return data["result"]
                    return data.get("result") if isinstance(data, dict) else str(data)
                except ValueError:
                    # not JSON, return plain text
                    return response.text
        except Exception as e:
            return f"unexpected error calling weather service: {e}"

    def extract_city(self, query: str) -> str | None:
        """
        Use the LLM to extract a city name. Returns None when no city is found.
        """
        prompt = (
            f'extract the city name from this query: "{query}"\n'
            "respond with just the city name, nothing else.\n"
            'if no city is mentioned, respond with "none"'
        )
        try:
            response = self.model.generate_content(prompt)
            city = (getattr(response, "text", "") or "").strip().lower()
            if city == "none" or city == "":
                return None
            return city
        except Exception:
            # if extraction fails, return None and let the user rephrase
            return None

    async def process_query(self, query: str) -> str:
        city = self.extract_city(query)

        if not city:
            return "please specify a city to get weather information"

        weather_data = await self.call_weather_tool(city)

        if weather_data is None:
            return (
                "couldn't connect to weather service. "
                "make sure weather_mcp.py is running on port 8000 (or set MCP_URL)"
            )

        if isinstance(weather_data, str) and "error" in weather_data.lower():
            return weather_data

        # allow the model to rewrite the response for conversational output
        prompt = (
            f'user asked: "{query}"\n'
            f'weather data: {weather_data}\n\n'
            "provide a natural response to the user's question using the weather data. "
            "be conversational and helpful."
        )

        try:
            response = self.model.generate_content(prompt)
            return (getattr(response, "text", "") or "").strip()
        except Exception:
            # fallback textual response
            return f"according to the weather api, {weather_data}"

    async def run(self):
        print("weather agent ready")
        print("ask about weather in any city")
        print("example: 'is it raining in hyderabad today?'")
        print("type 'quit' to exit\n")

        while True:
            try:
                query = input("you: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nbye!")
                break

            if not query:
                continue
            if query.lower() in {"quit", "exit", "bye"}:
                print("bye!")
                break

            response = await self.process_query(query)
            print(f"agent: {response}\n")


async def main():
    agent = WeatherAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
