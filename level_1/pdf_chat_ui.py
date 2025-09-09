"""
PDF Document Analyzer - Professional Streamlit Interface
Provides enterprise-grade PDF analysis with AI-powered Q&A capabilities.
"""

import sys
import os

# Ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    import streamlit as st
    from pdf_reader import PDFProcessor, GeminiClient
except ImportError as e:
    print(f"Import Error: {e}")
    print("Install required packages: pip install streamlit pypdf google-generativeai python-dotenv")
    sys.exit(1)


# Application configuration
st.set_page_config(
    page_title="PDF Document Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def initialize_session_state():
    """Initialize all session state variables with defaults."""
    session_defaults = {
        'pdf_content': '',
        'pdf_chunks': [],
        'pdf_filename': '',
        'pdf_warnings': [],
        'analysis_history': []
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def display_application_header():
    """Render application header with API status."""
    st.title("📄 PDF Document Analyzer")
    st.markdown("**Professional document analysis with AI-powered insights**")
    
    # Check API availability
    gemini_client = GeminiClient()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if gemini_client.is_available():
            st.success("🟢 AI Analysis Active - Gemini API Connected")
        else:
            st.warning("🟡 Demo Mode Active - Add API key for full AI analysis")
    
    with col2:
        if not gemini_client.is_available():
            if st.button("Setup Guide", help="How to configure API key"):
                show_api_setup_guide()


def show_api_setup_guide():
    """Display API configuration instructions."""
    with st.expander("🔧 API Configuration Guide", expanded=True):
        st.markdown("""
        **Quick Setup Steps:**
        
        1. **Get API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. **Create Key**: Click "Create API Key" (it's free!)
        3. **Set Environment Variable**:
           ```bash
           export GEMINI_API_KEY="your_api_key_here"
           ```
        4. **Restart Application**: Close and reopen Streamlit
        
        **Alternative**: Create `.env` file with:
        ```
        GEMINI_API_KEY=your_api_key_here
        ```
        """)


def handle_document_upload():
    """Process PDF document upload with comprehensive error handling."""
    st.subheader("📁 Document Upload")
    
    uploaded_file = st.file_uploader(
        "Choose PDF Document",
        type=["pdf"],
        help="Upload text-based PDF files for analysis",
        key="pdf_uploader"
    )
    
    if uploaded_file is not None:
        # Process new file
        if uploaded_file.name != st.session_state.pdf_filename:
            process_new_document(uploaded_file)
        
        # Show current document status
        display_document_status()


def process_new_document(uploaded_file):
    """Process newly uploaded PDF document."""
    with st.spinner(f"🔄 Processing {uploaded_file.name}..."):
        try:
            # Initialize processor
            processor = PDFProcessor()
            
            # Read and process file
            file_bytes = uploaded_file.read()
            if not file_bytes:
                st.error("❌ Empty file uploaded")
                return
            
            # Extract text
            content, warnings = processor.extract_text(file_bytes)
            
            if content:
                # Create chunks for analysis
                chunks = processor.create_chunks(content)
                
                # Update session state
                st.session_state.pdf_content = content
                st.session_state.pdf_filename = uploaded_file.name
                st.session_state.pdf_warnings = warnings
                st.session_state.pdf_chunks = chunks
                st.session_state.analysis_history = []  # Clear history
                
                # Success feedback
                st.success(f"✅ Successfully processed: {uploaded_file.name}")
                
                # Statistics
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                with stats_col1:
                    st.metric("Characters", f"{len(content):,}")
                with stats_col2:
                    st.metric("Text Segments", len(chunks))
                with stats_col3:
                    st.metric("Pages Processed", len(content.split('\n\n')))
                
            else:
                st.error("❌ No readable text found in PDF")
                st.info("💡 Tip: Ensure PDF contains selectable text, not scanned images")
            
            # Display any processing warnings
            if warnings:
                with st.expander("⚠️ Processing Warnings", expanded=False):
                    for warning in warnings:
                        st.warning(warning)
                        
        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
            reset_document_state()


def display_document_status():
    """Show current document information and controls."""
    if not st.session_state.pdf_filename:
        st.info("📤 Upload a PDF document to begin analysis")
        return
    
    st.markdown("---")
    
    # Document info
    info_col1, info_col2 = st.columns([2, 1])
    
    with info_col1:
        st.markdown("**📋 Current Document**")
        st.text(f"File: {st.session_state.pdf_filename}")
        if st.session_state.pdf_content:
            st.text(f"Size: {len(st.session_state.pdf_content):,} characters")
            st.text(f"Analysis ready: {len(st.session_state.pdf_chunks)} segments")
    
    with info_col2:
        if st.button("🔍 Preview Content", use_container_width=True):
            show_content_preview()
        
        if st.button("🗑️ Clear Document", use_container_width=True):
            reset_document_state()
            st.success("Document cleared successfully")
            st.rerun()


def show_content_preview():
    """Display document content preview."""
    if not st.session_state.pdf_content:
        return
        
    with st.expander("📖 Document Content Preview", expanded=True):
        preview_text = st.session_state.pdf_content[:2000]
        st.text_area(
            "First 2000 characters:",
            value=preview_text,
            height=300,
            disabled=True
        )
        
        remaining = len(st.session_state.pdf_content) - 2000
        if remaining > 0:
            st.caption(f"... and {remaining:,} more characters")


def reset_document_state():
    """Reset all document-related session state."""
    st.session_state.pdf_content = ''
    st.session_state.pdf_chunks = []
    st.session_state.pdf_filename = ''
    st.session_state.pdf_warnings = []
    st.session_state.analysis_history = []


def handle_document_analysis():
    """Main document analysis interface."""
    st.subheader("🤖 AI Document Analysis")
    
    if not st.session_state.pdf_content:
        st.info("📋 Please upload a document to enable analysis")
        return
    
    # Analysis configuration
    setup_analysis_options()
    
    # Question input
    question = st.text_area(
        "💬 Ask a question about your document:",
        placeholder="Examples:\n• What is the main topic of this document?\n• Who are the key people mentioned?\n• What are the main conclusions?\n• Provide a summary of key findings\n• What recommendations are made?",
        height=120,
        key="question_input"
    )
    
    # Analysis execution
    if st.button("🚀 Analyze Document", type="primary", use_container_width=True):
        if not question.strip():
            st.error("❌ Please enter a question to analyze")
            return
        
        execute_analysis(question.strip())


def setup_analysis_options():
    """Configure analysis model and options."""
    config_col1, config_col2 = st.columns([3, 1])
    
    with config_col1:
        model_options = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "gemini-pro"
        ]
        
        selected_model = st.selectbox(
            "🔧 AI Model:",
            options=model_options,
            index=0,
            help="Flash model recommended for better performance and quota limits"
        )
        
        return selected_model
    
    with config_col2:
        gemini_client = GeminiClient()
        force_demo = st.checkbox(
            "Demo Mode",
            value=not gemini_client.is_available(),
            disabled=not gemini_client.is_available(),
            help="Use demo responses instead of AI analysis"
        )
        
        return force_demo


def execute_analysis(question: str):
    """Execute document analysis with the given question."""
    # Get configuration
    selected_model = setup_analysis_options()
    
    # Initialize components
    processor = PDFProcessor()
    gemini_client = GeminiClient()
    
    # Find relevant content
    with st.spinner("🔍 Searching relevant document sections..."):
        relevant_context = processor.find_relevant_chunks(
            st.session_state.pdf_chunks, 
            question,
            max_chunks=4
        )
    
    if not relevant_context:
        st.warning("⚠️ No relevant content found for your question")
        return
    
    # Generate AI response
    force_demo = not gemini_client.is_available() or st.session_state.get('force_demo', False)
    
    if gemini_client.is_available() and not force_demo:
        with st.spinner("🤖 Generating AI analysis..."):
            response = gemini_client.query(selected_model, relevant_context, question)
    else:
        response = gemini_client.generate_mock_response(relevant_context, question)
    
    # Display results
    display_analysis_results(question, response, relevant_context, selected_model, force_demo)


def display_analysis_results(question: str, response: str, context: str, model: str, is_demo: bool):
    """Display analysis results with formatting."""
    st.markdown("### 📊 Analysis Results")
    
    # Main response
    st.markdown(response)
    
    # Source context
    with st.expander("📝 Source Context Used", expanded=False):
        st.text_area(
            "Relevant document sections analyzed:",
            value=context,
            height=250,
            disabled=True,
            help="These sections were used to generate the analysis"
        )
        
        # Analysis metadata
        mode = "Demo Mode" if is_demo else "AI Analysis"
        st.caption(f"**Model**: {model} | **Mode**: {mode}")
    
    # Save to history
    analysis_entry = {
        'question': question,
        'response': response,
        'timestamp': st.session_state.get('current_time', 'Now'),
        'model': model,
        'demo_mode': is_demo
    }
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    st.session_state.analysis_history.append(analysis_entry)


def display_application_footer():
    """Display help information and controls."""
    st.markdown("---")
    
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.markdown("**💡 Usage Tips:**")
        st.markdown("• Works best with text-based PDFs")
        st.markdown("• Ask specific, focused questions")
        st.markdown("• Try different question phrasings")
        st.markdown("• Use Flash model for better limits")
    
    with footer_col2:
        st.markdown("**🔧 Troubleshooting:**")
        st.markdown("• Check API key if responses seem generic")
        st.markdown("• Ensure PDF has selectable text")
        st.markdown("• Try demo mode to test functionality")
        st.markdown("• Refresh if experiencing issues")
    
    with footer_col3:
        st.markdown("**🚀 Quick Actions:**")
        if st.button("🔄 Refresh Application"):
            st.rerun()
        
        if st.session_state.analysis_history:
            if st.button("📜 View Analysis History"):
                show_analysis_history()


def show_analysis_history():
    """Display analysis history."""
    if not st.session_state.analysis_history:
        st.info("No analysis history available")
        return
    
    with st.expander("📜 Analysis History", expanded=True):
        for i, entry in enumerate(reversed(st.session_state.analysis_history), 1):
            st.markdown(f"**Q{i}:** {entry['question']}")
            st.markdown(f"**A{i}:** {entry['response'][:200]}...")
            st.caption(f"Model: {entry['model']} | Mode: {'Demo' if entry['demo_mode'] else 'AI'}")
            st.markdown("---")


def main():
    """Main application entry point."""
    # Initialize application
    initialize_session_state()
    
    # Display header
    display_application_header()
    
    # Main application layout
    main_col1, main_col2 = st.columns([1, 2])
    
    # Left column: Document upload and management  
    with main_col1:
        handle_document_upload()
    
    # Right column: Analysis interface
    with main_col2:
        handle_document_analysis()
    
    # Footer with help and utilities
    display_application_footer()


if __name__ == "__main__":
    main()