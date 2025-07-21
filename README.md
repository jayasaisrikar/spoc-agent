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
- **🧠 Conversation Memory**: Persistent memory system using Mem0 that learns from every interaction and provides context-aware responses
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
- `mem0ai>=0.1.114` - Long-term memory system for persistent AI conversations
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

**What is Mem0?**
[Mem0](https://github.com/mem0ai/mem0) is a powerful memory layer for AI applications that enables persistent, context-aware conversations. Unlike traditional chatbots that forget previous interactions, Mem0 creates a long-term memory system that learns from every conversation.

**How Mem0 Works:**
- **Vector Storage**: Stores conversation history and context in a vector database
- **Semantic Search**: Retrieves relevant memories based on meaning, not just keywords  
- **Personalization**: Learns user preferences, coding patterns, and project-specific context
- **Cross-Session Memory**: Maintains context across different conversation sessions

**In This Agent:**
The agent includes a sophisticated memory system that:

- **Remembers Preferences**: Your coding style, preferred frameworks, and architectural patterns
- **Maintains Context**: Conversation history across sessions for each repository
- **Personalizes Responses**: Tailored suggestions based on past interactions and learned preferences
- **Project-Specific Memory**: Different memory contexts for different repositories
- **Learning Capability**: Improves recommendations over time based on your feedback

### Memory Features
- **User Preference Learning**: Adapts to your coding style and technology preferences
- **Project-Specific Context**: Separate memory contexts for different codebases
- **Cross-Session Continuity**: Remembers conversations even after restarting the application
- **Intelligent Context Retrieval**: Automatically finds relevant past discussions when analyzing new code
- **Feedback Integration**: Learns from your feedback to improve future suggestions

### Getting Started with Mem0
For a hands-on demonstration of Mem0 integration, see the [Mem0 Demo Notebook](./mem0_demo.ipynb) which shows how to:
- Set up Mem0 with Google Gemini
- Store and retrieve conversation memories
- Implement project-specific memory contexts
- Use memory for enhanced code analysis

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
