"""
pdf reader terminal version - level 1
author: aditya
project: lynq agentic challenge - round 2
"""

import os
import sys
from pypdf import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def get_key():
    keys = ("GEMINI_API_KEY", "gemini_api_key")
    for k in keys:
        v = os.getenv(k)
        if v and v != "your_api_key_here":
            return v
    raise SystemExit("set gemini api key in .env")

def read_pdf(filepath):
    try:
        reader = PdfReader(filepath)
        text = ""
        pages = len(reader.pages)
        print(f"reading {pages} pages...")
        for i, page in enumerate(reader.pages):
            text += page.extract_text()
            print(f"processed page {i+1}/{pages}", end="\r")
        print()
        return text
    except Exception as e:
        print(f"error: {e}")
        return None

def analyze_pdf(text, model_name="gemini-1.5-flash"):
    genai.configure(api_key=get_key())
    model = genai.GenerativeModel(model_name)
    
    print("\ntype 'quit' to exit")
    print("ask questions about the pdf\n")
    
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
        
        prompt = f"""
        document content:
        {text[:10000]}
        
        question: {query}
        
        answer based on the document. be concise and accurate.
        """
        
        try:
            response = model.generate_content(prompt)
            print("ai:", response.text.strip(), "\n")
        except Exception as e:
            print(f"error: {e}\n")

def main():
    if len(sys.argv) < 2:
        print("usage: python pdf_reader.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"file not found: {pdf_path}")
        sys.exit(1)
    
    print(f"loading {pdf_path}...")
    text = read_pdf(pdf_path)
    
    if text:
        print(f"extracted {len(text)} characters")
        print(f"first 200 chars: {text[:200]}...\n")
        analyze_pdf(text)
    else:
        print("failed to read pdf")

if __name__ == "__main__":
    main()