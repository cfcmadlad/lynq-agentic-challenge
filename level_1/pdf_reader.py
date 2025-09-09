"""
PDF Reader Module - Level 1
Author: Professional PDF Processing System
Handles PDF text extraction and AI-powered document analysis.
"""

import io
import os
from typing import List, Tuple, Optional

try:
    from pypdf import PdfReader
    import google.generativeai as genai
except ImportError as e:
    raise ImportError(f"Missing package: {e}. Run: pip install pypdf google-generativeai")


class PDFProcessor:
    """Handles PDF text extraction and intelligent chunking."""
    
    def __init__(self, chunk_size: int = 1500, overlap: int = 300):
        self.chunk_size = max(chunk_size, 500)  # Minimum chunk size
        self.overlap = min(overlap, chunk_size // 2)  # Max 50% overlap
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
            'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
            'would', 'could', 'should', 'may', 'might', 'can', 'must'
        }
    
    def extract_text(self, file_content: bytes) -> Tuple[str, List[str]]:
        """
        Extract text from PDF with comprehensive error handling.
        Returns: (extracted_text, warnings_list)
        """
        if not file_content:
            return "", ["Empty file provided"]
        
        warnings = []
        
        try:
            reader = PdfReader(io.BytesIO(file_content))
            total_pages = len(reader.pages)
            
            if total_pages == 0:
                return "", ["PDF contains no pages"]
            
            text_parts = []
            failed_pages = 0
            
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        # Clean and normalize text
                        cleaned = ' '.join(page_text.strip().split())
                        if len(cleaned) > 10:  # Minimum meaningful content
                            text_parts.append(cleaned)
                    else:
                        failed_pages += 1
                        
                except Exception as e:
                    warnings.append(f"Page {page_num} extraction failed: {str(e)[:50]}")
                    failed_pages += 1
            
            if failed_pages > 0:
                warnings.append(f"Unable to process {failed_pages} of {total_pages} pages")
            
            if not text_parts:
                return "", ["No readable text found. May be a scanned/image PDF"]
            
            full_text = "\n\n".join(text_parts)
            return full_text, warnings
            
        except Exception as e:
            return "", [f"PDF processing error: {str(e)[:100]}"]
    
    def create_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks with smart boundary detection."""
        if not text or not text.strip():
            return []
        
        text = text.strip()
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings in last 100 chars
                search_start = max(end - 100, start)
                best_break = end
                
                for i in range(end - 1, search_start - 1, -1):
                    if text[i] in '.!?' and i + 1 < len(text):
                        if text[i + 1].isspace() or text[i + 1].isupper():
                            best_break = i + 1
                            break
                
                end = best_break
            
            chunk = text[start:end].strip()
            if chunk and len(chunk) > 20:  # Skip very short chunks
                chunks.append(chunk)
            
            if end >= len(text):
                break
            
            # Ensure progress and apply overlap
            start = max(end - self.overlap, start + 1)
        
        return chunks
    
    def find_relevant_chunks(self, chunks: List[str], query: str, max_chunks: int = 4) -> str:
        """Find most relevant chunks using keyword scoring algorithm."""
        if not chunks:
            return ""
        
        if not query or not query.strip():
            return "\n\n".join(chunks[:max_chunks])
        
        # Extract meaningful query terms
        query_terms = []
        for word in query.lower().split():
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) > 2 and clean_word not in self.stop_words:
                query_terms.append(clean_word)
        
        if not query_terms:
            return "\n\n".join(chunks[:max_chunks])
        
        # Score each chunk
        scored_chunks = []
        for chunk in chunks:
            score = 0
            chunk_lower = chunk.lower()
            
            for term in query_terms:
                # Count occurrences and weight by term length
                count = chunk_lower.count(term)
                weight = 1 + (len(term) - 3) * 0.1  # Longer terms get more weight
                score += count * weight
            
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Sort by relevance and select top chunks
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        selected_chunks = [chunk for _, chunk in scored_chunks[:max_chunks]]
        
        # Fallback to first chunks if no matches
        if not selected_chunks:
            selected_chunks = chunks[:max_chunks]
        
        return "\n\n".join(selected_chunks)


class GeminiClient:
    """Manages Gemini API interactions for document Q&A."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._get_api_key()
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
            except Exception:
                self.api_key = None  # Invalid key
    
    def _get_api_key(self) -> Optional[str]:
        """Retrieve API key from environment variables."""
        possible_keys = ["GEMINI_API_KEY", "gemini_api_key", "GOOGLE_API_KEY"]
        
        for key_name in possible_keys:
            value = os.getenv(key_name)
            if value and value.strip() and not value.startswith("your_"):
                return value.strip()
        return None
    
    def is_available(self) -> bool:
        """Check if API is configured and ready."""
        return bool(self.api_key)
    
    def query(self, model_name: str, context: str, question: str) -> str:
        """
        Query Gemini model with document context and user question.
        Returns AI response or fallback to mock mode.
        """
        if not self.api_key:
            return self.generate_mock_response(context, question)
        
        if not context or not context.strip():
            return "No relevant document content found for analysis."
        
        if not question or not question.strip():
            return "Please provide a specific question to analyze."
        
        try:
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""You are a professional document analyst. Answer the question based strictly on the provided document content.

DOCUMENT CONTENT:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Use only information from the document above
- Provide specific, accurate answers
- Quote relevant sections when helpful
- If information is not in the document, state this clearly
- Be concise but comprehensive

ANALYSIS:"""
            
            response = model.generate_content(prompt)
            
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                return "No response generated. Please try rephrasing your question."
                
        except Exception as e:
            error_message = str(e).lower()
            
            # Handle specific API errors
            if any(term in error_message for term in ["429", "quota", "rate limit"]):
                return "API quota exceeded. Please wait or try the Flash model for better limits."
            elif any(term in error_message for term in ["api", "key", "auth"]):
                return "API authentication failed. Please verify your GEMINI_API_KEY."
            elif any(term in error_message for term in ["blocked", "safety"]):
                return "Response blocked by safety filters. Try rephrasing your question."
            elif "404" in error_message:
                return f"Model '{model_name}' not available. Try 'gemini-1.5-flash' instead."
            else:
                return f"Query failed: {str(e)[:100]}"
    
    def generate_mock_response(self, context: str, question: str) -> str:
        """Generate informative mock response when API is unavailable."""
        if not context or not context.strip():
            return "No document content available for mock analysis."
        
        # Create content preview
        preview = context[:300].replace("\n", " ").strip()
        if len(context) > 300:
            preview += "..."
        
        return f"""🔧 DEMO MODE - API Key Required for AI Analysis

Your Question: {question}

Sample Analysis: Based on the document content, the AI would provide detailed, contextual answers here. The system has successfully processed your document and identified relevant sections.

Document Preview:
"{preview}"

To Enable Full AI Analysis:
1. Visit: https://makersuite.google.com/app/apikey
2. Generate a free Gemini API key
3. Set environment variable: GEMINI_API_KEY=your_key_here
4. Restart the application

Document Statistics: {len(context):,} characters processed and ready for AI analysis."""