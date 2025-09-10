# level_1/llm_call.py
import os
import sys
import time

# Enforce python version early
if sys.version_info < (3, 10):
    raise SystemExit("Python 3.10+ is required. Upgrade Python or change type hints.")

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

KEYS = ("GEMINI_API_KEY", "gemini_api_key")


def get_key() -> str:
    """Return first valid GEMINI api key from environment or exit."""
    for k in KEYS:
        v = os.getenv(k)
        if v and v != "your_api_key_here" and len(v.strip()) > 10:
            return v.strip()
    raise SystemExit("Set your GEMINI API key in .env (GEMINI_API_KEY)")


def choose_model() -> str:
    """
    Choose a Gemini model automatically if available.
    Falls back to gemini-1.5-flash to avoid quota issues.
    """
    genai.configure(api_key=get_key())
    try:
        models = genai.list_models()
        avail = []
        for m in models:
            # Support SDK returning objects or dicts
            name = getattr(m, "name", None) or (m.get("name") if isinstance(m, dict) else None)
            if name:
                avail.append(name)
    except Exception:
        # Listing may be disabled for some API keys; fallback to flash
        print("Could not list models, using gemini-1.5-flash")
        return "gemini-1.5-flash"

    # Filter out unwanted values
    avail = [a for a in avail if a not in {"gemini-pro", "models/gemini-pro"}]

    # Prioritize flash over pro to avoid quota issues
    for prefer in ("gemini-1.5-flash", "gemini-1.5-pro"):
        for a in avail:
            if prefer in a:
                return a

    for a in avail:
        if a.startswith("gemini"):
            return a

    return "gemini-1.5-flash"


def test_gemini(model_name: str) -> bool:
    """Basic smoke test for the model; returns True on success."""
    prompt = (
        "Provide a concise six-sentence summary of Chelsea FC that includes the founding year "
        "and the home stadium. Respond in plain text."
    )
    try:
        m = genai.GenerativeModel(model_name)
        resp = m.generate_content(prompt)
        text = getattr(resp, "text", None)
        if text and text.strip():
            print("Test reply:", text.strip())
            return True
        else:
            print("Test failed: no response text received")
            return False
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "quota" in error_str.lower():
            print("Quota exceeded. Try again later or use gemini-1.5-flash.")
        elif "404" in error_str or "not found" in error_str.lower():
            print("Model not found. Check if the model name is valid.")
        elif "api" in error_str.lower() and "key" in error_str.lower():
            print("API key error. Check your GEMINI_API_KEY.")
        else:
            print("Test error:", e)
        return False


def chat_with_gemini(model_name: str):
    """Interactive chat loop with Gemini."""
    model = genai.GenerativeModel(model_name)
    print(f"\nUsing model: {model_name}")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
            
        if not user_input:
            continue
            
        if user_input.lower() in {"quit", "exit", "bye"}:
            print("Goodbye!")
            break
            
        try:
            r = model.generate_content(user_input)
            response_text = getattr(r, "text", "") or ""
            if response_text.strip():
                print("Gemini:", response_text.strip(), "\n")
            else:
                print("Gemini: No response generated. Please try rephrasing.\n")
            
            # Add small delay to avoid hitting rate limits
            time.sleep(0.5)
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                print("Hit quota limit. Waiting 60 seconds...")
                print("Consider switching to gemini-1.5-flash model if using pro.")
                time.sleep(2)
            elif "blocked" in error_str.lower() or "safety" in error_str.lower():
                print("Response blocked by safety filters. Try rephrasing your question.\n")
            else:
                print("Error:", e, "\n")
                time.sleep(1)


if __name__ == "__main__":
    try:
        model = choose_model()
        if test_gemini(model):
            chat_with_gemini(model)
        else:
            print("\nFix the API key or model access and try again")
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)