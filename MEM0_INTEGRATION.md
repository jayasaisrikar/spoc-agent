# Mem0 Integration with Codebase Agent

This document explains how mem0 (long-term memory) has been integrated into your Codebase Agent to provide context-aware, personalized interactions.

## 🧠 What is Mem0?

Mem0 is a memory layer for AI applications that enables:
- **Persistent Conversations**: Remember user preferences and context across sessions
- **Semantic Search**: Find relevant memories based on meaning, not just keywords  
- **Personalized Responses**: Generate contextually aware responses based on user history
- **Repository-Specific Memory**: Maintain different memory contexts for different projects

## 🏗️ Architecture

The mem0 integration adds several new components to your codebase:

```
codebase-agent/
├── memory_manager.py          # Core mem0 functionality
├── conversation_manager.py    # Enhanced with memory capabilities
├── main.py                   # New memory-enabled API endpoints
├── mem0_demo.ipynb          # Interactive demonstration notebook
├── test_memory.py           # Integration test script
└── requirements.txt         # Updated with mem0 dependencies
```

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```powershell
# PowerShell
$env:GOOGLE_API_KEY="your-google-api-key-here"

# Or add to .env file
GOOGLE_API_KEY=your-google-api-key-here
```

### 3. Test the Integration

```bash
python test_memory.py
```

### 4. Start the Enhanced API Server

```bash
python main.py
```

## 🚀 New Features

### Memory-Enabled API Endpoints

#### 1. Chat with Memory
```http
POST /chat-with-memory
Content-Type: application/x-www-form-urlencoded

repo_name=my-project&message=How should I implement authentication?&user_id=developer123
```

#### 2. Repository Analysis with Memory
```http
POST /analyze-repo-with-memory
Content-Type: multipart/form-data

repo_name: my-project
file: [uploaded zip file]
user_id: developer123
```

#### 3. Feature Suggestions with Memory
```http
POST /suggest-feature-with-memory
Content-Type: application/x-www-form-urlencoded

repo_name=my-project&feature_description=real-time notifications&user_id=developer123
```

#### 4. Memory Search
```http
GET /memory-search?query=authentication preferences&user_id=developer123&limit=5
```

### Core Classes

#### MemoryManager

```python
from memory_manager import MemoryManager

# Initialize with Gemini
memory_manager = MemoryManager()

# Add conversation to memory
messages = [
    {"role": "user", "content": "I prefer TypeScript for large projects"},
    {"role": "assistant", "content": "Great choice! TypeScript provides better type safety."}
]
memory_manager.add_conversation(messages, user_id="developer123")

# Search memories
memories = memory_manager.search_memories("TypeScript preferences", "developer123")

# Generate response with memory context
response = memory_manager.generate_with_memory(
    "What language should I use?", 
    "developer123"
)
```

#### Enhanced ConversationManager

```python
from conversation_manager import ConversationManager

conv_manager = ConversationManager()

# Chat with memory
response = conv_manager.chat_with_memory(
    repo_name="my-project",
    message="How should I structure my API?",
    user_id="developer123"
)

# Analyze repository with memory context
analysis = conv_manager.analyze_with_memory(
    repo_name="my-project",
    repo_data=repo_data,
    mermaid_diagram=diagram,
    user_id="developer123"
)
```

## 💡 Use Cases

### 1. Personalized Code Reviews
The AI remembers your coding preferences and provides consistent feedback:
- Naming conventions you prefer
- Architecture patterns you use
- Testing strategies you follow

### 2. Context-Aware Feature Suggestions
When suggesting where to add new features, the AI considers:
- Your project's existing structure
- Your preferred tech stack
- Patterns you've used before

### 3. Learning User Preferences
Over time, the system learns:
- Your preferred libraries and frameworks
- How you organize code
- Your documentation style
- Your testing approaches

### 4. Project-Specific Contexts
Different memory contexts for different repositories:
- Frontend projects vs. backend projects
- Microservices vs. monolithic architectures
- Different programming languages

## 🔍 Example Interaction

**First Session:**
```
User: I'm building a FastAPI project and prefer modular architecture with separate services.
AI: I'll help you structure your FastAPI project with a modular approach...

[Memory stores: prefers FastAPI, modular architecture, separate services]
```

**Later Session:**
```
User: How should I add authentication to my project?
AI: Based on your FastAPI project with modular architecture, I recommend creating a separate auth service module. This aligns with your preference for modular design...

[AI remembers the user's tech stack and architectural preferences]
```

## 🛠️ Configuration

### Memory Configuration

The system uses Gemini for both LLM and embedding:

```python
config = {
    "embedder": {
        "provider": "gemini",
        "config": {
            "model": "models/text-embedding-004",
        }
    },
    "llm": {
        "provider": "gemini", 
        "config": {
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "max_tokens": 2000,
        }
    },
    "vector_store": {
        "config": {
            "embedding_model_dims": 768,
        }
    }
}
```

### User ID Strategy

User IDs can be:
- Explicit: `user_id="developer123"`
- Repository-based: `user_id="repo_my-project"`
- Session-based: Generated automatically

## 📊 Benefits

### For Users
- **Personalized Experience**: Responses tailored to your preferences
- **Context Continuity**: Maintains project context across sessions
- **Learning System**: Gets better at understanding your needs over time
- **Efficient Interactions**: No need to re-explain preferences

### For Developers
- **Enhanced API**: Memory-enabled endpoints for richer interactions
- **Flexible Architecture**: Easy to extend and customize
- **Modular Design**: Memory system is cleanly separated
- **Comprehensive Logging**: Track memory operations and performance

## 🚨 Troubleshooting

### Common Issues

1. **Memory System Not Available**
   - Check if `GOOGLE_API_KEY` is set
   - Verify mem0ai package is installed
   - Check network connectivity

2. **Dependency Conflicts**
   - Update FastAPI: `pip install fastapi --upgrade`
   - Check anyio version compatibility

3. **API Key Issues**
   - Ensure API key has proper permissions
   - Check for rate limiting
   - Verify key is correctly formatted

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 Future Enhancements

- **Vector Store Options**: Support for other vector databases
- **Memory Clustering**: Group related memories
- **Memory Expiration**: Automatic cleanup of old memories
- **Multi-User Support**: Shared memories for teams
- **Memory Analytics**: Insights into memory usage patterns

## 📝 Demo Notebook

Check out `mem0_demo.ipynb` for an interactive demonstration of all features, including:
- Step-by-step setup
- Example conversations
- Memory search demonstrations
- Comparison of responses with/without memory
- Interactive chatbot example

Run the notebook to see mem0 in action!
