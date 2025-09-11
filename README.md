# Lynq Agentic Challenge - Complete Solution

A professional implementation of AI-powered document analysis and weather agent systems, featuring LLM integration, PDF processing capabilities, and MCP (Model Context Protocol) server architecture.

## Solution Overview

This repository provides complete implementations for both levels of the Lynq Round 2 Challenge:

- **Level 1**: LLM integration with interactive chat interface and AI-powered PDF document analysis
- **Level 2**: MCP-based weather agent system with natural language processing capabilities

## Prerequisites

- **Python**: Version 3.10 or higher
- **API Keys**: Google Gemini API key (required for AI functionality)
- **Optional**: OpenWeatherMap API key for live weather data
- **System Requirements**: 4GB RAM minimum, internet connectivity

## Quick Setup Guide

### 1. Clone and Navigate
```bash
git clone https://github.com/yourusername/lynq-agentic-challenge
cd lynq-agentic-challenge
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

### 4. Obtain API Keys

**Google Gemini API (Required)**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key to your `.env` file

**OpenWeatherMap API (Optional)**
1. Register at [OpenWeatherMap](https://openweathermap.org/api)
2. Generate a free API key
3. Add to your `.env` file

## Project Structure

```
lynq-agentic-challenge/
├── level_1/
│   ├── llm_call.py          # Interactive LLM chat interface
│   ├── pdf_reader.py        # PDF processing and analysis engine
│   └── pdf_chat_ui.py       # Web-based PDF analyzer interface
├── level_2/
│   ├── weather_mcp.py       # MCP weather server implementation
│   └── client_agent.py      # Weather agent client with NLP
├── requirements.txt         # Python dependencies
├── .env                     # Environment configuration (create this)
├── .gitignore              # Version control exclusions
└── README.md               # This documentation
```

## Running the Applications

### Level 1: LLM Chat Interface

Launch the terminal-based chat application:

```bash
cd level_1
python llm_call.py
```

**Usage:**
- Type messages to interact with the AI
- Use natural language for any queries
- Type `quit`, `exit`, or press Ctrl+C to exit

**Example Session:**
```
You: Explain quantum computing in simple terms
Gemini: [Detailed explanation provided]

You: Write a Python function for sorting
Gemini: [Code example with explanation]

You: quit
```

### Level 1: PDF Document Analyzer

Launch the web-based PDF analysis interface:

```bash
cd level_1
streamlit run pdf_chat_ui.py
```

The application will be available at `http://localhost:8501`

**Features:**
- Upload PDF documents through the web interface
- Ask questions about document content
- Get AI-powered analysis and insights
- View document processing statistics
- Access analysis history

**Supported Query Types:**
- Document summarization
- Key information extraction
- Personnel and entity identification
- Conclusion and recommendation analysis

### Level 2: Weather Agent System

The Level 2 system requires running two components simultaneously.

#### Step 1: Start the Weather Server

In your first terminal:
```bash
cd level_2
python weather_mcp.py
```

You should see:
```
Weather MCP Server Starting
Mode: MOCK DATA / LIVE API
Running on http://0.0.0.0:8000
Available endpoints:
  POST /tools/call
  GET  /tools/list
```

#### Step 2: Start the Weather Agent Client

In a second terminal:
```bash
cd level_2
python client_agent.py
```

**Usage Examples:**
```
You: What's the weather in Hyderabad?
Agent: According to current conditions, it's cloudy with light rain, 27°C in Hyderabad.

You: Is it raining in London today?
Agent: London is currently experiencing rainy conditions at 18°C.

You: quit
```

## Configuration Options

### Environment Variables

The system supports the following configuration options:

```env
# Required - AI functionality
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - live weather data
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Optional - server configuration
MCP_URL=http://localhost:8000
HOST=0.0.0.0
PORT=8000
```

### Model Selection

The system automatically selects the optimal Gemini model:
1. `gemini-1.5-flash` (recommended for efficiency and quota limits)
2. `gemini-1.5-pro` (enhanced capabilities)
3. `gemini-pro` (fallback option)

## Troubleshooting

### Common Issues

**Missing API Key**
```
ERROR: Set GEMINI_API_KEY in .env file
```
Solution: Ensure your API key is correctly added to the `.env` file

**Import Errors**
```
ImportError: No module named 'google.generativeai'
```
Solution: Run `pip install -r requirements.txt`

**Python Version**
```
Python 3.10+ is required
```
Solution: Upgrade to Python 3.10 or higher

**PDF Processing Issues**
```
No readable text found in PDF
```
Solution: Ensure the PDF contains selectable text, not scanned images

**Server Connection**
```
Cannot connect to weather server
```
Solution: Verify `weather_mcp.py` is running in a separate terminal

### Verification Commands

**Test API Configuration:**
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Gemini API Key:', 'CONFIGURED' if os.getenv('GEMINI_API_KEY') else 'NOT SET')
print('Weather API Key:', 'CONFIGURED' if os.getenv('OPENWEATHER_API_KEY') else 'NOT SET')
"
```

**Test MCP Server:**
```bash
curl -X GET http://localhost:8000/tools/list
```

Expected response: `{"tools": ["get_weather"]}`

## System Testing

### Complete System Validation

Execute this sequence to test all components:

```bash
# 1. Test Level 1 Chat Interface
cd level_1 && python llm_call.py
# Input: "Hello" then "quit"

# 2. Test Level 1 PDF Analyzer (new terminal)
cd level_1 && streamlit run pdf_chat_ui.py
# Upload a test PDF and submit queries

# 3. Test Level 2 Weather Server (new terminal)
cd level_2 && python weather_mcp.py

# 4. Test Level 2 Weather Agent (new terminal)
cd level_2 && python client_agent.py
# Input: "Weather in Delhi" then "quit"
```

## Technical Architecture

### Level 1 Components

**LLM Chat Interface (`llm_call.py`)**
- Direct integration with Google Gemini models
- Intelligent error handling and retry mechanisms
- Cross-platform terminal compatibility

**PDF Processor (`pdf_reader.py`)**
- Advanced text extraction using PyPDF
- Intelligent content chunking with overlap management
- Relevance scoring for context matching

**Web Interface (`pdf_chat_ui.py`)**
- Streamlit-based professional interface
- Real-time processing feedback
- Session state management

### Level 2 Components

**MCP Server (`weather_mcp.py`)**
- FastAPI-based HTTP server
- RESTful API following MCP specifications
- Support for both live API and mock data

**Weather Agent (`client_agent.py`)**
- Natural language processing for queries
- Intelligent city name extraction
- Conversational AI response generation

## Performance Considerations

The system is optimized for:
- **Efficiency**: Smart API usage with quota management
- **Reliability**: Comprehensive error handling and fallback mechanisms
- **User Experience**: Responsive interfaces with real-time feedback
- **Scalability**: Modular architecture supporting future enhancements

## Security Features

- Environment variable isolation for sensitive data
- Input validation and sanitization
- Secure API communication
- Error message sanitization

## Development Notes

### Code Quality
- Comprehensive type hints throughout
- Extensive inline documentation
- Standardized error handling patterns
- Modular component architecture

### Extension Points
The codebase supports easy extension for:
- Additional LLM providers
- Enhanced document processing formats
- Extended weather data sources
- Custom MCP tool implementations

## API Usage Information

**LLM API Used:** Google Gemini (gemini-1.5-flash recommended)
**Weather API Used:** OpenWeatherMap (optional, falls back to mock data)

## Sample Inputs and Outputs

### Level 1 Examples

**Chat Interface:**
```
Input: "Explain machine learning in technical terms"
Output: [Comprehensive technical explanation of ML concepts]
```

**PDF Analyzer:**
```
Input: "What are the key findings in this research paper?"
Output: [Structured analysis of document findings with relevant quotes]
```

### Level 2 Examples

**Weather Queries:**
```
Input: "Is it raining in Hyderabad today?"
Output: "According to current conditions, it's cloudy with light rain, 27°C in Hyderabad."
```

## Support

For technical issues:
1. Verify all prerequisites are met
2. Check API key configuration
3. Review error messages for specific guidance
4. Test individual components in isolation

The system includes comprehensive fallback modes to ensure functionality even with limited API access.