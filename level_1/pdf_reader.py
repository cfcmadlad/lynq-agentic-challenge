# level1/pdf_reader.py
import os
import sys

# enforce python version early
if sys.version_info < (3, 10):
    raise SystemExit("Python 3.10+ is required. Upgrade Python or change type hints.")

from pypdf import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


def get_key() -> str:
    keys = ("GEMINI_API_KEY", "gemini_api_key")
    for k in keys:
        v = os.getenv(k)
        if v and v != "your_api_key_here":
            return v
    raise SystemExit("set GEMINI_API_KEY in .env")


def read_pdf(filepath: str) -> str | None:
    """Read a PDF file and return the extracted text (concatenated)."""
    try:
        reader = PdfReader(filepath)
        text_parts = []
        pages = len(reader.pages)
        print(f"reading {pages} pages...")
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""  # safe if None
            text_parts.append(page_text)
            print(f"processed page {i+1}/{pages}", end="\r")
        print()
        return "\n".join(text_parts)
    except Exception as e:
        print(f"error reading pdf: {e}")
        return None


def analyze_pdf(text: str, model_name: str = "gemini-1.5-flash"):
    """Interactive loop to ask questions about the pdf text using Gemini."""
    genai.configure(api_key=get_key())
    model = genai.GenerativeModel(model_name)

    print("\ntype 'quit' to exit")
    print("ask questions about the pdf\n")

    # keep prompts reasonable in length for the model
    max_doc_snippet = 10000

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

        doc_snippet = text[:max_doc_snippet]
        prompt = (
            "document content:\n"
            f"{doc_snippet}\n\n"
            f"question: {query}\n\n"
            "answer based on the document. be concise and accurate."
        )

        try:
            response = model.generate_content(prompt)
            print("ai:", (getattr(response, "text", "") or "").strip(), "\n")
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
