# level1/pdf_chat_ui.py
"""
PDF Chat UI (Streamlit) - Level 1
Author: Assistant
Project: Lynq Agentic Challenge - Round 2

Description:
 - Upload a PDF, ask questions about it.
 - Uses pypdf for extraction and google.generativeai for answering.
 - If GEMINI_API_KEY is not set, UI will offer a mock reply mode.
 - Simple keyword-based chunk retrieval for relevant context (no embeddings required).

Professional UI without emojis for business use.
"""

import os
import io
import time
from typing import List, Optional
import sys

# Check Python version early
if sys.version_info < (3, 8):
    raise SystemExit("Python 3.8+ is required. Please upgrade your Python version.")

try:
    import streamlit as st
    from pypdf import PdfReader
    from dotenv import load_dotenv
    import google.generativeai as genai
except ImportError as e:
    raise SystemExit(f"Missing required package: {e}. Please install with: pip install streamlit pypdf python-dotenv google-generativeai")

load_dotenv()

# Configuration
GEMINI_API_KEYS = ("GEMINI_API_KEY", "gemini_api_key", "GOOGLE_API_KEY")
DEFAULT_CHUNK_SIZE = 1500
DEFAULT_OVERLAP = 300
MAX_CHUNKS_FOR_CONTEXT = 4


def get_gemini_api_key() -> Optional[str]:
    """Return first valid GEMINI API key from environment or None if not set."""
    for key_name in GEMINI_API_KEYS:
        value = os.getenv(key_name)
        if value and value.strip() and value != "your_api_key_here":
            return value.strip()
    return None


def extract_text_from_pdf(file_like: io.BytesIO) -> tuple[str, list[str]]:
    """
    Extract text from a PDF file with multiple fallback strategies.
    Returns (extracted_text, list_of_warnings)
    """
    warnings = []
    try:
        reader = PdfReader(file_like)
        total_pages = len(reader.pages)
        
        if total_pages == 0:
            return "", ["PDF has no pages"]
        
        text_parts = []
        failed_pages = 0
        
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    # Clean up common PDF extraction artifacts
                    cleaned_text = page_text.strip()
                    # Remove excessive whitespace
                    cleaned_text = ' '.join(cleaned_text.split())
                    if cleaned_text:
                        text_parts.append(cleaned_text)
                else:
                    failed_pages += 1
            except Exception as e:
                warnings.append(f"Error extracting text from page {page_num + 1}: {str(e)}")
                failed_pages += 1
                continue
        
        if failed_pages > 0:
            warnings.append(f"Failed to extract text from {failed_pages} out of {total_pages} pages")
        
        if not text_parts:
            warnings.append("No readable text found in any pages. This might be a scanned PDF.")
            return "", warnings
        
        final_text = "\n\n".join(text_parts)
        return final_text, warnings
        
    except Exception as e:
        return "", [f"Critical error reading PDF: {str(e)}"]


def create_text_chunks(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks with smart boundary detection.
    """
    if not text or not text.strip():
        return []
    
    text = text.strip()
    # Ensure overlap is reasonable
    overlap = min(overlap, chunk_size // 2)
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to break at sentence boundaries if possible
        if end < len(text):
            # Look for sentence endings within the last 100 characters
            search_start = max(end - 100, start)
            sentence_ends = []
            
            for i in range(search_start, end):
                if text[i] in '.!?':
                    # Check if it's likely end of sentence (followed by space and capital letter)
                    if i + 1 < len(text) and (text[i + 1].isspace() or text[i + 1].isupper()):
                        sentence_ends.append(i + 1)
            
            if sentence_ends:
                end = sentence_ends[-1]
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Calculate next start position
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)  # Ensure we make progress
    
    return chunks


def find_relevant_chunks(chunks: List[str], query: str, max_chunks: int = MAX_CHUNKS_FOR_CONTEXT) -> str:
    """
    Find and return most relevant chunks based on keyword matching.
    Uses improved scoring algorithm.
    """
    if not chunks:
        return ""
    
    if not query.strip():
        return "\n\n".join(chunks[:max_chunks])
    
    # Extract meaningful query words
    query_words = []
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must'}
    
    for word in query.lower().split():
        clean_word = ''.join(c for c in word if c.isalnum())
        if clean_word and len(clean_word) > 2 and clean_word not in stop_words:
            query_words.append(clean_word)
    
    if not query_words:
        return "\n\n".join(chunks[:max_chunks])
    
    # Score chunks
    chunk_scores = []
    for i, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        score = 0
        
        for word in query_words:
            # Count occurrences of each query word
            word_count = chunk_lower.count(word)
            # Weight by word importance (longer words get higher weight)
            score += word_count * (1 + len(word) / 10)
        
        chunk_scores.append((score, i, chunk))
    
    # Sort by score and select top chunks
    chunk_scores.sort(key=lambda x: x[0], reverse=True)
    
    # Get top scoring chunks
    relevant_chunks = []
    for score, _, chunk in chunk_scores[:max_chunks]:
        if score > 0:  # Only include chunks with positive scores
            relevant_chunks.append(chunk)
    
    # If no chunks scored, return first few chunks as fallback
    if not relevant_chunks:
        relevant_chunks = chunks[:max_chunks]
    
    return "\n\n".join(relevant_chunks)


def query_gemini_model(model_name: str, context: str, question: str) -> str:
    """
    Query Gemini model with improved error handling and response validation.
    """
    if not context.strip():
        return "Error: No relevant document content found to answer your question."
    
    if not question.strip():
        return "Error: Please provide a valid question."
    
    try:
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""You are an AI assistant that answers questions based strictly on the provided document content.

Document Content:
{context}

Question: {question}

Instructions:
- Answer the question using ONLY information from the document content above
- Be concise but comprehensive
- If the answer isn't in the document, clearly state that
- Quote relevant parts when appropriate
- If the question is ambiguous, provide the best possible answer based on available information

Answer:"""
        
        response = model.generate_content(prompt)
        
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            return "Error: No response received from the model. Please try again."
            
    except Exception as e:
        error_msg = str(e).lower()
        
        if "429" in error_msg or "quota" in error_msg or "limit" in error_msg:
            return "Warning: API quota exceeded. Please try again later or switch to gemini-1.5-flash model."
        elif "api" in error_msg and "key" in error_msg:
            return "Error: Invalid API key. Please check your GEMINI_API_KEY."
        elif "blocked" in error_msg or "safety" in error_msg:
            return "Warning: Response blocked by safety filters. Please try rephrasing your question."
        elif "404" in error_msg or "not found" in error_msg:
            return f"Error: Model '{model_name}' not found. Please select a different model."
        else:
            return f"Error: Failed to query model - {str(e)}"


def generate_mock_response(context: str, question: str) -> str:
    """Generate a helpful mock response when API key is not available."""
    if not context.strip():
        return "Error: No document content available for mock response."
    
    # Create a preview of the context
    preview = context[:400].replace("\n", " ").strip()
    if len(context) > 400:
        preview += "..."
    
    return f"""MOCK RESPONSE (No API Key Detected)

Your Question: {question}

Mock Analysis: Based on the document content, I would analyze the text and provide a relevant answer here. 

Document Preview:
{preview}

To get real AI-powered answers:
1. Get a Gemini API key from Google AI Studio
2. Add it to your .env file as GEMINI_API_KEY=your_key_here  
3. Restart the application

Note: This is a placeholder response. The actual AI would provide detailed, contextual answers based on your document content."""


# Initialize Streamlit app
st.set_page_config(
    page_title="PDF Document Analyzer", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # Header
    st.title("PDF Document Analyzer")
    st.markdown("Upload a PDF document and ask questions about its content using AI-powered analysis.")
    
    # Check API key status
    api_key = get_gemini_api_key()
    
    # Status indicator
    if api_key:
        st.success("Status: Gemini API key detected - AI responses enabled")
    else:
        st.warning("Status: No Gemini API key found - using mock mode")
        with st.expander("How to add API key", expanded=False):
            st.markdown("""
            **Setup Instructions:**
            1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Create a new API key
            3. Add it to your `.env` file: `GEMINI_API_KEY=your_key_here`
            4. Restart the application
            """)
    
    # Initialize session state
    if "pdf_content" not in st.session_state:
        st.session_state.pdf_content = ""
    if "pdf_chunks" not in st.session_state:
        st.session_state.pdf_chunks = []
    if "pdf_filename" not in st.session_state:
        st.session_state.pdf_filename = ""
    if "processing_warnings" not in st.session_state:
        st.session_state.processing_warnings = []
    
    # Main layout
    col1, col2 = st.columns([1, 2])
    
    # Left column - PDF Upload
    with col1:
        st.header("Document Upload")
        
        uploaded_file = st.file_uploader(
            "Select a PDF file", 
            type=["pdf"], 
            help="Upload a text-based PDF (not scanned images)"
        )
        
        if uploaded_file is not None:
            # Check if it's a new file
            if uploaded_file.name != st.session_state.pdf_filename:
                with st.spinner("Processing PDF document..."):
                    try:
                        # Read file content
                        file_content = uploaded_file.read()
                        if not file_content:
                            st.error("Error: Empty file uploaded")
                        else:
                            # Extract text
                            extracted_text, warnings = extract_text_from_pdf(io.BytesIO(file_content))
                            
                            # Update session state
                            st.session_state.pdf_content = extracted_text
                            st.session_state.pdf_filename = uploaded_file.name
                            st.session_state.processing_warnings = warnings
                            
                            if extracted_text:
                                # Create chunks
                                chunks = create_text_chunks(extracted_text)
                                st.session_state.pdf_chunks = chunks
                                
                                st.success(f"Successfully processed: {uploaded_file.name}")
                                st.info(f"Statistics: Extracted {len(extracted_text):,} characters in {len(chunks)} chunks")
                            else:
                                st.error("Error: No text could be extracted from this PDF")
                                
                            # Show warnings if any
                            if warnings:
                                for warning in warnings:
                                    st.warning(f"Warning: {warning}")
                                    
                    except Exception as e:
                        st.error(f"Error: Failed to process PDF - {str(e)}")
        
        # Current document info
        if st.session_state.pdf_filename:
            st.markdown("---")
            st.markdown("**Current Document Information**")
            st.text(f"File: {st.session_state.pdf_filename}")
            
            if st.session_state.pdf_content:
                st.text(f"Content: {len(st.session_state.pdf_content):,} characters")
                st.text(f"Chunks: {len(st.session_state.pdf_chunks)} segments")
                
                if st.button("Preview Document Content"):
                    with st.expander("Document Content Preview", expanded=True):
                        preview_text = st.session_state.pdf_content[:2000]
                        st.text_area("First 2000 characters:", preview_text, height=300)
                        if len(st.session_state.pdf_content) > 2000:
                            st.caption(f"... and {len(st.session_state.pdf_content) - 2000:,} more characters")
            
            if st.button("Clear Current Document"):
                st.session_state.pdf_content = ""
                st.session_state.pdf_chunks = []
                st.session_state.pdf_filename = ""
                st.session_state.processing_warnings = []
                st.success("Document cleared successfully")
                st.rerun()
    
    # Right column - Analysis Interface
    with col2:
        st.header("Document Analysis")
        
        if not st.session_state.pdf_content:
            st.info("Please upload a PDF document to begin analysis.")
            return
        
        # Model selection and options
        col2a, col2b = st.columns([2, 1])
        with col2a:
            model_options = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
            selected_model = st.selectbox(
                "AI Model:", 
                options=model_options,
                index=0,
                help="Flash model recommended for better quota limits"
            )
        
        with col2b:
            force_mock = st.checkbox(
                "Mock mode", 
                value=not bool(api_key),
                disabled=not bool(api_key),
                help="Use mock responses instead of AI"
            )
        
        # Question input
        user_question = st.text_area(
            "Enter your question about the document:",
            placeholder="Examples:\n• What is the main topic of this document?\n• Who are the key people mentioned?\n• What are the main conclusions?\n• Summarize the key findings",
            height=120
        )
        
        # Analysis button
        if st.button("Analyze Document", type="primary", use_container_width=True):
            if not user_question.strip():
                st.error("Error: Please enter a question to analyze.")
            else:
                # Find relevant content
                with st.spinner("Finding relevant content..."):
                    relevant_context = find_relevant_chunks(
                        st.session_state.pdf_chunks, 
                        user_question, 
                        max_chunks=4
                    )
                
                # Generate answer
                if api_key and not force_mock:
                    genai.configure(api_key=api_key)
                    with st.spinner("Generating AI analysis..."):
                        answer = query_gemini_model(selected_model, relevant_context, user_question)
                else:
                    answer = generate_mock_response(relevant_context, user_question)
                
                # Display results
                st.markdown("### Analysis Results")
                st.markdown(answer)
                
                # Show context used
                with st.expander("Document Context Used for Analysis", expanded=False):
                    st.text_area(
                        "Relevant sections from your document:", 
                        relevant_context, 
                        height=250,
                        help="These sections were analyzed to answer your question"
                    )
                    st.caption(f"Model: {selected_model}" + (" (Mock Mode)" if (not api_key or force_mock) else " (AI Mode)"))
    
    # Footer
    st.markdown("---")
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("**Usage Tips:**")
        st.markdown("• Works best with text-based PDFs")
        st.markdown("• Ask specific questions for better results") 
        st.markdown("• Try different phrasings if needed")
        st.markdown("• Use the Flash model for better API limits")
    
    with col_info2:
        st.markdown("**Troubleshooting:**")
        if st.button("Refresh Application"):
            st.rerun()
        st.markdown("• Check API key if responses seem generic")
        st.markdown("• Try mock mode to test functionality")
        st.markdown("• Ensure PDF contains selectable text")


if __name__ == "__main__":
    main()