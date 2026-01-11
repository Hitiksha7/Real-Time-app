
# 🤖 Real-Time AI Chat with Intelligent Web Search
A streaming AI chat application that intelligently decides when to search the web for current information. Built with LangGraph for agentic workflows, FastAPI for high-performance backend, and Streamlit for interactive UI.

#### 🎯 Overview

This application demonstrates a single-agent architecture with dynamic tool-calling capabilities. The AI agent autonomously decides when to search the web for current information versus answering from its training data, providing real-time, accurate responses with source citations.

## Demo Video

[![Watch Demo](https://img.shields.io/badge/▶️-Watch%20Demo%20Video-red?style=for-the-badge)]([paste-your-link-here](https://drive.google.com/file/d/1bBhj34tv4UnK8j7j5m5K1NHfMXPJl-XT/view?usp=sharing))

##### Use Cases:
- Research assistance with current information
- News and updates on recent events
- General question-answering with fact-checking

🚀 Core Functionality

- Real-time Streaming: Word-by-word response generation using Server-Sent Events (SSE)
- Intelligent Tool Calling: Agent decides autonomously when to search the web
- Conversation Memory: Maintains context across multiple messages using thread-based sessions
- Source Attribution: Displays clickable URLs from search results in organized 2x2 grid

🛠️ Technical Highlights

- Async Architecture: Non-blocking I/O for high concurrency
- State Management: LangGraph's checkpoint system for conversation persistence
- Agent Orchestration: Conditional routing based on tool requirements
- Error Handling: Graceful degradation with comprehensive error recovery

#### 🔄 How It Works
1. User Query Processing
```
User → Streamlit UI → FastAPI Endpoint → LangGraph Agent
```
2. Intelligent Decision Making
The agent analyzes the query and determines:

- Known Information: Responds directly from training data
- Current Events: Triggers web search via Tavily API
- Ambiguous: Combines knowledge with verification
3. Response Generation

```
Agent Decision → Tool Execution → Result Processing → Streaming to User
```
4. Memory Management
- Each conversation gets a unique thread_id for maintaining context across messages.

#### 🏗️ Architecture
<img width="461" height="1072" alt="Image" src="https://github.com/user-attachments/assets/b380017a-6be8-4999-a3ac-b903744f0154" />

#### System Overview

🔧 Technical Architecture
Core Modules
1. State Management (app/state.py)
- Maintains conversation history
- Uses LangGraph's [add_messages] reducer for automatic message aggregation
- Thread-based isolation for concurrent users

2. Agent Orchestration (app/graph.py)
- Agent Node: LLM-powered decision maker using GPT-4o-mini
- Tool Node: Executes web search via Tavily
- Conditional Edges: Dynamic routing based on tool requirements
- Cyclic Flow: Tools return to agent for result processing

3. Tool Integration (app/tools.py)
- Tavily Search API for real-time web information
- Returns structured results with URLs, titles, and content

4. API Layer (main.py)
- Async Generators: Memory-efficient streaming
- Server-Sent Events: Real-time updates to client
##### Event Types:
- `on_chat_model_stream`: Text chunks
- `on_chat_model_end`: Tool call detection
- `on_tool_end`: Search results

5. Frontend Interface (streamlit.py)
- Real-time UI updates
- Session state management
- URL display with hover effects
#### Key Files:

| File  | Purpose     | Key Components                |
| :-------- | :------- | :------------------------- |
| `app/graph.py` | Agent Orchestration | State graph, nodes, edges, memory |
| `app/state.py` | State schema | Message history, type definitions |
| `app/tools.py` | External tools| Tavily Search integartion|
| `main.py` | Backend API | FastAPI endpoints, streaming logic |
| `streamlit.py` | Frontend UI| Chat interface, session management |

## Installation

    Install my-project
    - Python 3.11+
    - OpenAI API Key
    - Tavily API Key 

Step 1: Clone Repository git clone 
```
https://github.com/yourusername/real-time-app.git
cd real-time-app
   ```

Step 2: Create Virtual Environment
```
python -m venv venv

Windows
venv\Scripts\activate

Linux/Mac
source venv/bin/activate
```

Step 3: Install Dependencies

```
pip install -r requirements.txt
```

Step 4: Configure Environment Variables

Create a`.env` file in the project root:
```
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here
```










        
## 💻 Usage
#### Start Backend (Terminal 1)
```
uvicorn main:app --reload
```

Backend will run on: `http://localhost:8000
`

#### Start Frontend (Terminal 2)
```
streamlit run streamlit.py
```
Frontend will open at: ` http://localhost:8501
`

#### Test the Application
1. Simple Question (No Search)
```
Q: "What is Python?"
→ Direct answer from training data
```
2. Current Information (Triggers Search)
```
Q: "What are the latest AI developments?"
→ Searches web → Returns answer with sources
```
3. Follow-up Question (Uses Memory)
```
Q: "Tell me more about the first one"
→ Remembers context from previous answer
```

## 🛠️ Tech Stack
#### Backend

- FastAPI: High-performance async web framework
- Uvicorn: ASGI server for FastAPI
- Pydantic: Data validation and settings management
#### AI & Agent Framework

- LangGraph: Agent orchestration and state management
- LangChain: LLM integration and tool abstractions
- LangChain-OpenAI: OpenAI API integration
- OpenAI GPT-4o-mini: Language model for agent reasoning

#### Tools & APIs

- Tavily Search: Real-time web search API
- LangChain-Tavily: Tavily integration for LangChain

#### Frontend

- Streamlit: Interactive web UI
- HTTPX: Async HTTP client for streaming

#### Utilities

- python-dotenv: Environment variable management
- asyncio: Asynchronous programming support


## 🙏 Acknowledgements

 - [OpenAI for GPT models](https://platform.openai.com/docs/models)
 - [Tavily for web search API](https://www.tavily.com/)
 - [FastAPI community](https://fastapi.tiangolo.com/)
 - [Streamlit community](https://streamlit.io/)
