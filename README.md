# AI Code Architecture Agent

An intelligent AI assistant that analyzes codebases, provides architectural insights, and offers precise guidance for implementing new features. The system combines multi-model AI capabilities with conversation memory to deliver personalized and context-aware development assistance.

## 🚀 Overview

This agent leverages advanced AI models (Gemini, OpenAI, Azure OpenAI) to understand your codebase architecture, maintain conversation context with memory, and provide intelligent recommendations for feature implementation and code organization.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Repository    │───▶│   File Parser   │───▶│  Architecture   │
│ Upload/Analysis │    │   & Processor   │    │   Generator     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Knowledge     │◀───│  Multi-Model    │───▶│ Feature/Code    │
│   Base (SQLite) │    │  AI Engine      │    │  Suggestions    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                      ┌─────────┼─────────┐
                      ▼         ▼         ▼
              ┌──────────┐ ┌─────────┐ ┌──────────┐
              │ Gemini   │ │ OpenAI  │ │ Azure    │
              │ 1.5 Pro  │ │ GPT-4   │ │ OpenAI   │
              └──────────┘ └─────────┘ └──────────┘
                      │
                      ▼
              ┌─────────────────┐
              │ Mem0 Memory     │
              │ System          │
              └─────────────────┘
```

## ✨ Key Features

- **🔍 Repository Analysis**: Deep analysis of GitHub repositories via ZIP upload or URL
- **🤖 Multi-Model AI**: Automatic fallback between Gemini, OpenAI, and Azure OpenAI
- **🧠 Conversation Memory**: Persistent memory system using Mem0 for personalized interactions
- **📊 Architecture Visualization**: Generates Mermaid.js diagrams for system understanding
- **💾 Knowledge Base**: SQLite-based storage for repository insights and conversation history
- **🎯 Smart Feature Placement**: Precise recommendations for implementing new features
- **💬 Interactive Chat**: Conversational interface with context awareness
- **🔧 Modern Frontend**: React-based UI with real-time interactions
- **⚡ Performance Optimized**: Efficient token usage and caching strategies

## 🛠️ Technology Stack

### Backend
- **Python 3.11+** with FastAPI
- **Multi-AI Integration**: Gemini 1.5 Pro, OpenAI GPT-4, Azure OpenAI
- **Memory System**: Mem0 for persistent conversation context
- **Database**: SQLite for knowledge storage
- **APIs**: GitHub API with fallback mechanisms

### Frontend  
- **React 18** with modern hooks and components
- **Vite** for fast development and building
- **Tailwind CSS** for responsive styling
- **Framer Motion** for smooth animations
- **Mermaid.js** for diagram visualization

### Core Dependencies
- `fastapi>=0.116.0` - High-performance web framework
- `google-generativeai>=0.3.1` - Gemini AI integration
- `mem0ai>=0.1.114` - Long-term memory system
- `openai>=1.0.0` - OpenAI API client
- `PyGithub==1.59.1` - GitHub API integration
- `python-multipart==0.0.6` - File upload support

## 📦 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ (for frontend development)
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-code-architecture-agent
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   # AI Model APIs (at least one required)
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_key_here          # Optional
   AZURE_OPENAI_KEY=your_azure_key_here         # Optional
   AZURE_OPENAI_ENDPOINT=your_azure_endpoint    # Optional
   
   # GitHub Integration (optional, for private repos)
   GITHUB_TOKEN=your_github_token_here
   
   # Mem0 Configuration (optional, for memory features)
   MEM0_API_KEY=your_mem0_api_key_here
   ```

4. **Start the backend server**
   ```bash
   python main.py
   ```
   Server will run on `http://localhost:8000`

### Frontend Setup (Optional - for development)

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   Frontend will run on `http://localhost:3000`

## 🚀 Usage

### Web Interface

1. **Access the application** at `http://localhost:8000`
2. **Analyze Repository**: Upload a ZIP file or provide a GitHub URL
3. **Interactive Chat**: Ask questions about your codebase
4. **Feature Suggestions**: Get recommendations for implementing new features
5. **View Knowledge Base**: Browse analyzed repositories and insights

### API Endpoints

#### Repository Analysis
```bash
curl -X POST "http://localhost:8000/analyze-repo" \
  -F "repo_name=my-project" \
  -F "file=@repository.zip"
```

#### Interactive Chat
```bash
curl -X POST "http://localhost:8000/ask-question" \
  -F "question=How should I implement user authentication?" \
  -F "repo_context=my-project"
```

#### Feature Suggestions
```bash
curl -X POST "http://localhost:8000/suggest-feature" \
  -F "repo_name=my-project" \
  -F "feature_description=Add real-time notifications"
```

#### Memory-Enhanced Chat
```bash
curl -X POST "http://localhost:8000/chat-with-memory" \
  -F "repo_name=my-project" \
  -F "message=Based on our previous discussion, how should I proceed?" \
  -F "user_id=developer123"
```

## 🧠 Memory System (Mem0 Integration)

The agent includes a sophisticated memory system that:

- **Remembers Preferences**: Your coding style, preferred frameworks, and architectural patterns
- **Maintains Context**: Conversation history across sessions
- **Personalizes Responses**: Tailored suggestions based on past interactions
- **Project-Specific Memory**: Different contexts for different repositories

### Memory Features
- User preference learning
- Project-specific context retention
- Cross-session conversation continuity
- Intelligent context retrieval

## 📊 Core Components

### Repository Handler (`repo_handler.py`)
- Processes ZIP uploads and GitHub URLs
- Extracts file structures and content
- Handles various file types and encodings

### Multi-Model AI Client (`multi_model_client.py`)
- Manages multiple AI providers with automatic fallback
- Optimizes prompts for different models
- Handles rate limiting and error recovery

### Knowledge Base (`knowledge_base.py`)
- SQLite-based storage for repository data
- Efficient indexing and retrieval
- Conversation history management

### Conversation Manager (`conversation_manager.py`)
- Manages chat sessions and context
- Integrates with Mem0 memory system
- Handles repository switching and context switching

### Diagram Generator (`diagram_generator.py`)
- Creates Mermaid.js architectural diagrams
- Optimizes diagrams for token efficiency
- Supports various diagram types

## 🔧 Advanced Configuration

### Custom AI Model Integration
```python
# Extend MultiModelClient for custom models
class CustomModelClient(MultiModelClient):
    def add_custom_model(self, model_config):
        self.models.append(model_config)
```

### Memory Configuration
```python
# Configure Mem0 settings
MEMORY_CONFIG = {
    "vector_store": {
        "provider": "chroma",
        "config": {"path": "./mem0_storage"}
    },
    "embedder": {
        "provider": "openai",
        "config": {"model": "text-embedding-ada-002"}
    }
}
```

## 🔍 Development & Debugging

### Debug Endpoints
- `GET /debug/repository/{repo_name}` - Inspect repository knowledge
- `GET /api/knowledge-base/tables` - View database structure
- `GET /memory-search` - Search memory contents

### Logging
The application includes comprehensive logging:
```python
# Configure logging level
logging.basicConfig(level=logging.INFO)
```

## 📈 Performance Optimizations

- **Async Processing**: FastAPI's async capabilities for concurrent requests
- **Token Optimization**: Efficient prompt engineering and context management
- **Caching**: SQLite-based caching for frequent queries
- **Memory Management**: Intelligent context pruning and optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Documentation & Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Mem0 Documentation](https://docs.mem0.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

---

**AI Code Architecture Agent** - Empowering developers with intelligent codebase analysis and personalized development assistance.

A sophisticated AI agent that analyzes GitHub repositories, generates architectural diagrams, and provides intelligent code placement recommendations for new features.

## 🚀 Project Overview

This agent leverages multiple AI models (Gemini, OpenAI, Azure OpenAI) to understand your codebase architecture, generate visual flow diagrams, and provide precise guidance on where to implement new features across your organization's repositories.

## 🏗️ Architecture

```ascii
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│ Local GitDiagram│───▶│   Mermaid JS    │
│ ZIP Upload/URL  │    │   Generator     │    │   Flow Chart    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Knowledge     │◀───│  Multi-Model    │───▶│   Feature      │
│   Base          │    │  AI Client      │    │   Placement     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                      ┌─────────┼─────────┐
                      ▼         ▼         ▼
                 ┌─────────┐ ┌─────┐ ┌─────────┐
                 │ Gemini  │ │ GPT │ │ Azure   │
                 │   API   │ │ API │ │ OpenAI  │
                 └─────────┘ └─────┘ └─────────┘
```

## 📋 Features

- **Repository Analysis**: Processes GitHub repositories via ZIP upload or URL
- **Multi-Model AI Support**: Automatic fallback between Gemini, OpenAI, and Azure OpenAI
- **GitHub Fallback**: Handles API rate limits with web scraping fallback
- **Architectural Visualization**: Generates Mermaid.js diagrams using local GitDiagram engine
- **Knowledge Base**: Stores and indexes repository information
- **Intelligent Feature Placement**: Recommends exact file locations for new features
- **Context Optimization**: Efficient token usage to stay within API limits
- **Local Processing**: Everything runs locally for security and privacy
- **Robust Error Handling**: Graceful degradation when APIs are unavailable

## 🛠️ Tech Stack

- **Backend**: Python (FastAPI)
- **AI Models**: Gemini 1.5 (primary), OpenAI GPT (fallback), Azure OpenAI (fallback)
- **APIs**: GitHub API with fallback scraping, Multi-Model AI Client
- **Storage**: SQLite database for knowledge base
- **Frontend**: Web interface for interaction
- **Diagram Generation**: Local GitDiagram core for secure processing

## 📦 Installation

### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Environment Setup

```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here      # Optional - for private repos
OPENAI_API_KEY=your_openai_key_here      # Optional - fallback AI model
AZURE_OPENAI_KEY=your_azure_key_here     # Optional - fallback AI model
AZURE_OPENAI_ENDPOINT=your_azure_endpoint # Optional - if using Azure OpenAI
```

**Note**: At least one AI API key is required. The system will automatically use the first available model and fall back to others if needed.

## 🔧 Core Components

### 1. Repository Handler (`repo_handler.py`)

Handles repository processing from multiple sources:
- **ZIP File Processing**: Extracts and analyzes uploaded repository ZIP files
- **GitHub API Integration**: Fetches repository data using GitHub API with authentication
- **File Structure Analysis**: Recursively analyzes repository structure and extracts file metadata
- **Content Extraction**: Processes various file types (Python, JavaScript, TypeScript, Java, C++, C)
- **Error Handling**: Graceful fallback mechanisms for API rate limits and access issues

### 2. GitDiagram Integration (`diagram_generator.py`)

Generates architectural diagrams using local GitDiagram engine:
- **Local Processing**: Secure, offline diagram generation
- **Mermaid.js Output**: Creates visual flow charts and architecture diagrams
- **Token Optimization**: Efficient context usage for AI models
- **Multiple Diagram Types**: Supports flowcharts, sequence diagrams, and architectural views

### 3. Multi-Model AI Client (`multi_model_client.py`)

Manages multiple AI providers with intelligent fallback:
- **Primary Model**: Gemini 1.5 Pro for advanced analysis
- **Fallback Support**: OpenAI GPT-4 and Azure OpenAI integration
- **Automatic Switching**: Seamless failover when APIs are unavailable
- **Rate Limiting**: Handles API quotas and throttling gracefully

### 4. Knowledge Base Manager (`knowledge_base.py`)

Manages repository knowledge storage and retrieval:
- **SQLite Database**: Efficient local storage for repository insights
- **Knowledge Indexing**: Structured storage of analysis results and diagrams
- **Feature Tracking**: Stores feature implementation suggestions and history
- **Hash-based Deduplication**: Prevents duplicate analysis of identical repositories

### 5. Main Agent (`main.py`)

Central FastAPI application that orchestrates all components:
- **RESTful API**: Clean API endpoints for repository analysis and feature suggestions
- **File Upload Support**: Handles ZIP file uploads and GitHub URL processing
- **Error Handling**: Robust error management and graceful degradation
- **Static File Serving**: Serves the web interface and assets

### 6. Web Interface (`static/index.html`)

Modern, responsive web interface featuring:
- **Multi-tab Design**: Repository analysis, feature suggestions, and repository management
- **File Upload Support**: Drag-and-drop ZIP file uploads
- **Real-time Results**: Live updates during analysis process
- **Error Handling**: User-friendly error messages and status indicators
- **Interactive Forms**: Validated input forms with helpful tooltips

### 7. Requirements and Configuration

#### Core Dependencies
- `fastapi>=0.116.0` - High-performance web framework
- `google-generativeai>=0.3.1` - Gemini AI integration
- `mem0ai>=0.1.114` - Long-term memory system
- `openai>=1.0.0` - OpenAI API client
- `PyGithub==1.59.1` - GitHub API integration
- `python-multipart==0.0.6` - File upload support

#### Docker Support
Ready-to-deploy Docker configuration with optimized Python 3.11 base image, efficient dependency caching, and proper port exposure for production deployment.

## 🚀 Usage Guide

### 1. Initial Setup

1. **Clone the repository**
2. **Install Python dependencies** using `pip install -r requirements.txt`
3. **Set up environment variables** in a `.env` file with your API keys

### 2. Running the Agent

Start the server with `python main.py`

### 3. Using the Web Interface

1. **Navigate to** `http://localhost:8000`
2. **Analyze Repository**: Upload a ZIP file or provide GitHub URL
3. **Add Feature**: Describe your feature and get placement suggestions
4. **View Repositories**: See all analyzed repositories

### 4. API Usage Examples

#### Analyze Repository via API

Use POST requests to `/analyze-repo` with either ZIP file upload or GitHub URL

#### Get Feature Suggestions

Use POST requests to `/suggest-feature` with repository name and feature description

## 🔧 Advanced Configuration

### Custom Model Integration

The system supports extending multi-model AI client for custom models with automatic fallback mechanisms.

### Context Optimization

Intelligent context management prioritizes important files and optimizes token usage to fit within API limits.

## 📊 Performance Optimizations

### 1. Caching Strategy

Implements Redis-based caching with configurable expiration times for frequent queries.

### 2. Batch Processing

Processes multiple repositories in configurable batches to optimize performance.

```python
class BatchProcessor:
    def __init__(self, batch_size: int = 5):
        self.batch_size = batch_size
        self.queue = []
    
    async def process_repositories(self, repos: List[str]):
        """Process multiple repositories in batches"""
        for i in range(0, len(repos), self.batch_size):
            batch = repos[i:i + self.batch_size]
            await asyncio.gather(*[self.process_single_repo(repo) for repo in batch])
```

## 🔍 Troubleshooting

### Common Issues

1. **API Rate Limits**: Implement exponential backoff
2. **Large Repository Handling**: Use file filtering and chunking
3. **Memory Issues**: Implement streaming for large files
4. **Context Limits**: Optimize token usage with summarization

### Debug Mode

```python
# Add to main.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add detailed logging throughout the application
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- [Gemini API Documentation](https://ai.google.dev/docs)
- [GitDiagram API](https://gitdiagram.com/docs)
- [Mermaid.js Documentation](https://mermaid.js.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

This AI Code Architecture Agent provides a comprehensive solution for understanding and extending your codebase with intelligent suggestions powered by Gemini 1.5. The modular architecture allows for easy customization and extension based on your specific needs.
