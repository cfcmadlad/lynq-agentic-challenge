# Lynq Agentic Challenge - Solutions

This repository contains comprehensive solutions for the Lynq Round 2 Agentic Challenge, implementing advanced LLM integrations, PDF document analysis capabilities, and MCP (Model Context Protocol) weather agent functionality.

## Overview

The solution is architected in two distinct levels:

**Level 1** focuses on foundational LLM integration and document processing, featuring an interactive chat interface and a sophisticated PDF analysis system with AI-powered question-answering capabilities.

**Level 2** implements a complete MCP-based weather agent system, demonstrating advanced tool integration patterns and natural language processing for weather queries.

## Prerequisites

- Python 3.10 or higher
- Google Gemini API key (available free from Google AI Studio)
- OpenWeatherMap API key (optional, for live weather data in Level 2)
- Internet connectivity for API operations

## Installation

### Dependencies

Install all required packages using the provided requirements file:

```bash
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

Alternatively, set environment variables directly:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
export OPENWEATHER_API_KEY="your_openweather_api_key_here"
```

### API Key Acquisition

**Google Gemini API Key:**
1. Navigate to Google AI Studio at https://makersuite.google.com/app/apikey
2. Authenticate with your Google account
3. Generate a new API key
4. Copy the key to your environment configuration

**OpenWeatherMap API Key (Optional):**
1. Visit https://openweathermap.org/api
2. Create a free account
3. Generate an API key from your dashboard
4. Add the key to your environment configuration

## Project Architecture

```
lynq-agentic-challenge/
├── level_1/
│   ├── llm_call.py          # Interactive LLM chat interface
│   ├── pdf_reader.py        # PDF processing and analysis backend
│   └── pdf_chat_ui.py       # Streamlit-based PDF analyzer interface
├── level_2/
│   ├── weather_mcp.py       # MCP weather server implementation
│   └── client_agent.py      # Weather agent client with NLP
├── requirements.txt         # Python dependencies
├── .gitignore              # Version control exclusions
└── README.md               # Documentation
```

## Level 1: LLM Integration and PDF Analysis

### Interactive LLM Chat Interface

Execute the terminal-based chat interface:

```bash
cd level_1
python llm_call.py
```

**Features:**
- Direct integration with Google Gemini models
- Intelligent model selection with quota optimization
- Comprehensive error handling and automatic retry mechanisms
- Support for multiple conversation patterns
- Graceful shutdown with standard exit commands

**Usage Example:**
```
You: Explain the principles of machine learning in technical terms
Gemini: [Detailed technical explanation]

You: Generate a Python function for data validation
Gemini: [Code implementation with explanation]

You: quit
```

### PDF Document Analyzer

Launch the web-based PDF analysis interface:

```bash
cd level_1
streamlit run pdf_chat_ui.py
```

This command initializes a Streamlit application accessible at `http://localhost:8501`

**Capabilities:**
- Advanced PDF text extraction with error recovery
- Intelligent document chunking and segmentation
- Context-aware question-answering system
- Professional web interface with real-time feedback
- Demo mode functionality for testing without API access
- Comprehensive document processing statistics
- Analysis history and session management

**Supported Query Types:**
- Document summarization requests
- Specific information extraction
- Key personnel and entity identification
- Recommendation and conclusion analysis
- Cross-reference and citation queries

## Level 2: MCP Weather Agent System

### Weather Server Initialization

Start the MCP-compliant weather server:

```bash
cd level_2
python weather_mcp.py
```

The server initializes on `http://localhost:8000` with the following endpoints:
- `GET /tools/list` - Available tool enumeration
- `POST /tools/call` - Tool execution interface

### Weather Agent Client

In a separate terminal session, initialize the weather agent client:

```bash
cd level_2
python client_agent.py
```

**System Architecture:**
- Natural language query processing
- Intelligent city name extraction and validation
- Real-time weather data integration (with API key)
- Fallback to comprehensive mock data
- Conversational AI response generation
- Robust error handling and connection management

**Query Examples:**
```
You: What are the current weather conditions in Hyderabad?
Agent: [Detailed weather information with temperature, conditions, and humidity]

You: Is precipitation expected in London today?
Agent: [Weather analysis with precipitation forecasts]
```

## Configuration Management

### Environment Variables

The system supports flexible configuration through environment variables:

```env
# Core LLM functionality
GEMINI_API_KEY=your_gemini_api_key_here

# Weather data integration
OPENWEATHER_API_KEY=your_openweather_api_key_here

# MCP server configuration
MCP_URL=http://localhost:8000
HOST=0.0.0.0
PORT=8000
```

### Model Selection

The system automatically selects optimal Gemini models with preference for:
1. `gemini-1.5-flash` (recommended for quota efficiency)
2. `gemini-1.5-pro` (enhanced capabilities)
3. `gemini-pro` (fallback option)

## Error Handling and Troubleshooting

### Common Issues and Resolutions

**API Authentication Failures:**
```
ERROR: Set GEMINI_API_KEY in .env file
```
Verify that your API key is correctly configured in environment variables or the `.env` file.

**Dependency Resolution:**
```
ImportError: No module named 'google.generativeai'
```
Execute `pip install -r requirements.txt` to install all required packages.

**Python Version Compatibility:**
```
Python 3.10+ is required
```
Upgrade to Python 3.10 or higher to ensure compatibility.

**PDF Processing Limitations:**
```
No readable text found in PDF
```
Ensure uploaded PDFs contain selectable text rather than scanned images.

**MCP Server Connectivity:**
```
Cannot connect to weather server
```
Verify that `weather_mcp.py` is running in a separate terminal session.

**API Quota Management:**
```
API quota exceeded
```
The system automatically implements quota management and will retry with optimized models.

### System Verification

Test API connectivity and configuration:

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Gemini API Key:', 'CONFIGURED' if os.getenv('GEMINI_API_KEY') else 'NOT SET')
print('Weather API Key:', 'CONFIGURED' if os.getenv('OPENWEATHER_API_KEY') else 'NOT SET')
"
```

Verify MCP server availability:

```bash
curl -X GET http://localhost:8000/tools/list
```

## Testing and Validation

### Comprehensive System Test

Execute the following sequence to validate all components:

```bash
# Configure environment
export GEMINI_API_KEY="your_key_here"

# Test Level 1 - LLM Chat
cd level_1 && python llm_call.py
# Input: "Hello, how are you?" followed by "quit"

# Test Level 1 - PDF Analyzer (new terminal)
cd level_1 && streamlit run pdf_chat_ui.py
# Upload a test PDF document and submit queries

# Test Level 2 - Weather Server (new terminal)
cd level_2 && python weather_mcp.py

# Test Level 2 - Weather Agent (new terminal)
cd level_2 && python client_agent.py
# Input: "Weather in Delhi" followed by "quit"
```

## Technical Specifications

### Level 1 Components

**LLM Chat Interface (`llm_call.py`):**
- Synchronous chat implementation with async-ready architecture
- Intelligent error recovery and retry logic
- Memory-efficient conversation handling
- Cross-platform terminal compatibility

**PDF Processor (`pdf_reader.py`):**
- Advanced text extraction with PyPDF integration
- Intelligent content chunking with overlap management
- Relevance scoring algorithm for context matching
- Comprehensive error handling for malformed documents

**Web Interface (`pdf_chat_ui.py`):**
- Professional Streamlit implementation
- Real-time document processing feedback
- Session state management
- Responsive design with mobile compatibility

### Level 2 Components

**MCP Server (`weather_mcp.py`):**
- FastAPI-based HTTP server implementation
- RESTful API design following MCP specifications
- Asynchronous request handling
- Comprehensive logging and monitoring

**Weather Agent (`client_agent.py`):**
- Natural language processing for query interpretation
- Intelligent city name extraction with fallback mechanisms
- HTTP client with connection pooling and timeout management
- Conversational AI integration with context awareness

## Performance Considerations

The system is optimized for:
- **Latency**: Efficient API call patterns with intelligent caching
- **Throughput**: Asynchronous processing where applicable
- **Resource Usage**: Memory-efficient document processing
- **Reliability**: Comprehensive error handling and graceful degradation
- **Scalability**: Modular architecture supporting horizontal scaling

## Security Implementation

- Environment variable isolation for sensitive data
- Input validation and sanitization
- API key rotation support
- Secure HTTP client configurations
- Error message sanitization to prevent information disclosure

## Development and Extension

The codebase is designed for extensibility with:
- Clean separation of concerns
- Comprehensive type hints for IDE support
- Modular component architecture
- Standardized error handling patterns
- Extensive inline documentation

For custom implementations, refer to the individual module documentation and follow the established patterns for API integration, error handling, and user interface design.

## Support and Documentation

For technical support:
1. Verify all prerequisites are met
2. Confirm API key configuration
3. Review error messages for specific guidance
4. Test individual components in isolation
5. Consult module-specific documentation for advanced configuration options

The system includes comprehensive fallback modes to ensure functionality even with limited API access, making it suitable for development, testing, and production environments.