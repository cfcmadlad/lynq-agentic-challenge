"""
pdf reader with chat interface - level 1
author: aditya
project: lynq agentic challenge - round 2
"""

import os
import sys
from pypdf import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

load_dotenv()

def get_key():
    keys = ("GEMINI_API_KEY", "gemini_api_key")
    for k in keys:
        v = os.getenv(k)
        if v and v != "your_api_key_here":
            return v
    return None

def extract_pdf_text(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"error reading pdf: {e}"

def analyze_with_gemini(text, query):
    key = get_key()
    if not key:
        return "set gemini api key in .env file"
    
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    pdf content:
    {text[:8000]}
    
    question: {query}
    
    provide a clear and concise answer based on the pdf content.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"error: {e}"

def main():
    st.set_page_config(page_title="pdf analyzer", layout="wide")
    st.title("pdf reader & analyzer")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pdf_text" not in st.session_state:
        st.session_state.pdf_text = None
    
    with st.sidebar:
        st.header("upload pdf")
        uploaded_file = st.file_uploader("choose a pdf file", type="pdf")
        
        if uploaded_file:
            if st.button("process pdf"):
                with st.spinner("extracting text..."):
                    text = extract_pdf_text(uploaded_file)
                    st.session_state.pdf_text = text
                    st.success(f"extracted {len(text)} characters")
                    st.session_state.messages.append({
                        "role": "system",
                        "content": f"pdf loaded: {uploaded_file.name}"
                    })
    
    if st.session_state.pdf_text:
        st.info(f"pdf loaded ({len(st.session_state.pdf_text)} chars)")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        if prompt := st.chat_input("ask about the pdf"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("analyzing..."):
                    response = analyze_with_gemini(st.session_state.pdf_text, prompt)
                    st.write(response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
    else:
        st.warning("upload a pdf to begin")

if __name__ == "__main__":
    main()