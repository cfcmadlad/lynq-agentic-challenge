# level1/llm_call.py
import os
import sys
import time

# enforce python version early
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
        if v and v != "your_api_key_here":
            return v
    raise SystemExit("set your GEMINI API key in .env (GEMINI_API_KEY)")


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
        # Listing may be disabled for some API keys; fallback to flash.
        print("Could not list models, using gemini-1.5-flash")
        return "gemini-1.5-flash"

    # filter out a few known unwanted values
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
            print("test reply:", text.strip())
            return True
        else:
            print("test failed: no response text received")
            return False
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "quota" in error_str.lower():
            print("Quota exceeded. Try again later or use gemini-1.5-flash.")
        elif "404" in error_str or "not found" in error_str.lower():
            print("Model not found. Check if the model name is valid.")
        else:
            print("test error:", e)
        return False


def chat_with_gemini(model_name: str):
    model = genai.GenerativeModel(model_name)
    print(f"\nusing model: {model_name}")
    print("type 'quit' to exit\n")
    while True:
        try:
            user_input = input("you: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\ngoodbye!")
            break
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "bye"}:
            print("goodbye!")
            break
        try:
            r = model.generate_content(user_input)
            print("gemini:", (getattr(r, "text", "") or "").strip(), "\n")
            # Add small delay to avoid hitting rate limits
            time.sleep(1)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                print("Hit quota limit. Waiting 60 seconds before you can try again...")
                print("Consider switching to gemini-1.5-flash model if using pro.")
                time.sleep(2)
            else:
                print("error:", e, "\n")
                time.sleep(1)


if __name__ == "__main__":
    model = choose_model()
    if test_gemini(model):
        chat_with_gemini(model)
    else:
        print("\nfix the api/key or model access and try again")