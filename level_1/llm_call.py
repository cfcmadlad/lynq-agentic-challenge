"""
llm api integration - level 1
author: aditya
project: lynq agentic challenge - round 2
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

KEYS = ("GEMINI_API_KEY", "gemini_api_key")

def get_key():
    for k in KEYS:
        v = os.getenv(k)
        if v and v != "your_api_key_here":
            return v
    raise SystemExit("set your gemini api key in .env (GEMINI_API_KEY)")

def choose_model():
    genai.configure(api_key=get_key())
    try:
        avail = [m.name for m in genai.list_models()]
    except Exception:
        return "gemini-1.5-flash"
    avail = [a for a in avail if a not in {"gemini-pro", "models/gemini-pro"}]
    for prefer in ("gemini-1.5-pro", "gemini-1.5-flash"):
        for a in avail:
            if prefer in a:
                return a
    for a in avail:
        if a.startswith("gemini"):
            return a
    return "gemini-1.5-flash"

def test_gemini(model_name):
    prompt = (
        "provide a concise two-sentence summary of chelsea fc "
        "that includes founding year and the home stadium. respond in plain text."
    )
    try:
        m = genai.GenerativeModel(model_name)
        resp = m.generate_content(prompt)
        print("test reply:", (resp.text or "").strip())
        return True
    except Exception as e:
        print("test error:", e)
        return False

def chat_with_gemini(model_name):
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
            print("gemini:", (r.text or "").strip(), "\n")
        except Exception as e:
            print("error:", e, "\n")

if __name__ == "__main__":
    model = choose_model()
    if test_gemini(model):
        chat_with_gemini(model)
    else:
        print("\nfix the api/key or model access and try again")
