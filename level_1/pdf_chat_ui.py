# level1/pdf_chat_ui.py
"""
pdf chat UI (streamlit) - level 1
author: aditya (assistant-polish)
project: lynq agentic challenge - round 2

Description:
 - Upload a PDF, ask questions about it.
 - Uses pypdf for extraction and google.generativeai for answering.
 - If GEMINI_API_KEY is not set, UI will offer a mock reply mode.
 - Simple keyword-based chunk retrieval for relevant context (no embeddings required).
"""
import os
import io
from typing import List

# enforce python version early
import python_version_check  # raises SystemExit if Python < 3.10

import streamlit as st
from pypdf import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

KEYS = ("GEMINI_API_KEY", "gemini_api_key")


def get_key() -> str | None:
    """Return first valid GEMINI api key from environment or None if not set."""
    for k in KEYS:
        v = os.getenv(k)
        if v and v != "your_api_key_here":
            return v
    return None


def extract_text_from_pdf(file_like: io.BytesIO) -> str:
    """Extract text from a file-like PDF. Returns concatenated text (may be empty)."""
    try:
        reader = PdfReader(file_like)
        parts = []
        for p in reader.pages:
            parts.append(p.extract_text() or "")
        return "\n".join(parts)
    except Exception as e:
        st.error(f"Error extracting PDF text: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks (by characters)."""
    if not text:
        return []
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0:
            start = 0
    return [c.strip() for c in chunks if c.strip()]


def find_relevant_chunks(chunks: List[str], query: str, max_chunks: int = 4) -> str:
    """Return a snippet formed by chunks that contain query words (simple keyword match).
       If none match, return the first chunk(s) as fallback.
    """
    if not chunks:
        return ""
    qwords = {w.lower() for w in query.strip().split() if w.isalpha()}
    if not qwords:
        # no meaningful words -> return first chunk(s)
        return "\n\n".join(chunks[:max_chunks])

    matched = []
    for chunk in chunks:
        low = chunk.lower()
        if any(w in low for w in qwords):
            matched.append(chunk)
            if len(matched) >= max_chunks:
                break

    if not matched:
        # fallback to first N chunks
        return "\n\n".join(chunks[:max_chunks])
    return "\n\n".join(matched)


def ask_gemini(model_name: str, doc_snippet: str, question: str) -> str:
    """Ask the Gemini model using a concise prompt. Returns textual answer or error string."""
    try:
        m = genai.GenerativeModel(model_name)
        prompt = (
            "You are an assistant that answers questions based only on the provided document snippet.\n\n"
            f"Document snippet:\n{doc_snippet}\n\n"
            f"Question: {question}\n\n"
            "Answer concisely and cite (in-text) the snippet if relevant. If the answer is not in the "
            "document, respond: 'I could not find the answer in the provided document.'"
        )
        resp = m.generate_content(prompt)
        return (getattr(resp, "text", "") or "").strip()
    except Exception as e:
        return f"LLM error: {e}"


def mock_answer(doc_snippet: str, question: str) -> str:
    """Deterministic mock used when no GEMINI key is provided."""
    if not doc_snippet:
        return "No document content available (mock)."
    # return a short, clearly mocked response
    preview = doc_snippet[:200].replace("\n", " ")
    return (
        "MOCK ANSWER: This is a placeholder response because no GEMINI API key was found.\n\n"
        f"Document preview: {preview}...\n\n"
        "Please set GEMINI_API_KEY in your .env to get real answers."
    )


# ---------- Streamlit app ----------
st.set_page_config(page_title="PDF Chat UI", layout="wide")
st.title("PDF Chat — Upload and Ask (streamlit)")
st.write("Upload a PDF, then ask questions about its content. Works best with selectable text PDFs.")

# session state for storing extracted text / chunks
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "chunks" not in st.session_state:
    st.session_state.chunks = []

col1, col2 = st.columns([1, 2])

with col1:
    uploaded = st.file_uploader("Upload PDF", type=["pdf"], accept_multiple_files=False)
    use_mock = st.checkbox("Use mock (no LLM call) if GEMINI key missing", value=True)

    if uploaded is not None:
        # read bytes into BytesIO, because streamlit file-like gets reused
        data = uploaded.read()
        if not data:
            st.error("Uploaded file is empty.")
        else:
            text = extract_text_from_pdf(io.BytesIO(data))
            st.session_state.pdf_text = text
            st.session_state.chunks = chunk_text(text, chunk_size=1500, overlap=300)
            st.success(f"Extracted text ({len(text)} characters). Chunk count: {len(st.session_state.chunks)}")
            if len(text) == 0:
                st.warning("PDF text extraction returned empty. The PDF may be scanned (image-based). Use OCR externally (e.g., Tesseract).")

    if st.session_state.pdf_text:
        if st.button("Show extracted text (diagnostic)"):
            st.text_area("Extracted text", value=st.session_state.pdf_text[:50000], height=400)

with col2:
    st.header("Ask a question")
    question = st.text_area("Your question", value="", height=120)
    model_name = st.text_input("Model name (optional)", value="gemini-1.5-flash")
    ask_btn = st.button("Ask")

    if ask_btn:
        if not st.session_state.pdf_text:
            st.error("Upload a PDF first.")
        elif not question.strip():
            st.error("Type a question.")
        else:
            # Decide LLM vs mock
            key = get_key()
            if key:
                genai.configure(api_key=key)
                # prepare context
                snippet = find_relevant_chunks(st.session_state.chunks, question, max_chunks=4)
                with st.spinner("Querying model..."):
                    answer = ask_gemini(model_name or "gemini-1.5-flash", snippet, question)
                st.markdown("**Answer:**")
                st.write(answer)
                st.markdown("**Document snippet used:**")
                st.text_area("Doc snippet", value=snippet, height=200)
            else:
                if use_mock:
                    snippet = find_relevant_chunks(st.session_state.chunks, question, max_chunks=2)
                    answer = mock_answer(snippet, question)
                    st.markdown("**(Mock) Answer:**")
                    st.write(answer)
                    st.markdown("**Document snippet used (mock):**")
                    st.text_area("Doc snippet (mock)", value=snippet, height=200)
                else:
                    st.error("No GEMINI_API_KEY found. Set GEMINI_API_KEY in .env or enable mock mode.")
