from typing import List, Dict, Optional
from datetime import datetime
from .memory_manager import MemoryManager
from ..data.knowledge_base import KnowledgeBase
import logging
import os
import uuid

logger = logging.getLogger(__name__)


class ConversationManager:
    def __init__(self):
        self.conversations = {}  # repo_name -> conversation history (in-memory cache)
        self.knowledge_base = KnowledgeBase()  # Database storage
        
        # Initialize memory manager
        try:
            # Get API key from environment
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            self.memory_manager = MemoryManager(api_key=api_key)
            logger.info("Memory manager initialized in conversation manager")
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            self.memory_manager = None

    def start_conversation(self, repo_name: str, repo_context: Dict = None):
        """Start a new conversation for a repository"""
        session_id = str(uuid.uuid4())
        
        self.conversations[repo_name] = {
            'session_id': session_id,
            'messages': [],
            'repo_context': repo_context,
            'created_at': datetime.now().isoformat()
        }
        
        return session_id

    def add_message(self, repo_name: str, role: str, content: str,
                    metadata: Dict = None, session_id: str = None):
        """Add a message to the conversation history"""
        if repo_name not in self.conversations:
            session_id = self.start_conversation(repo_name)
        else:
            session_id = session_id or self.conversations[repo_name].get('session_id', str(uuid.uuid4()))

        message_id = str(uuid.uuid4())
        message = {
            'message_id': message_id,
            'role': role,  # 'user', 'assistant', 'system'
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        # Add to in-memory cache
        self.conversations[repo_name]['messages'].append(message)
        
        # Store in database
        self.knowledge_base.store_chat_message(
            repo_name=repo_name,
            session_id=session_id,
            message_id=message_id,
            role=role,
            content=content,
            metadata=metadata
        )

        # Add to memory if available
        if self.memory_manager:
            user_id = f"repo_{repo_name}"
            # Add this specific message to memory
            self.memory_manager.add_conversation([{
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }], user_id)

    def load_conversation_from_db(self, repo_name: str, session_id: str = None):
        """Load conversation history from database"""
        try:
            messages = self.knowledge_base.get_chat_history(repo_name, session_id)
            
            # Load into in-memory cache
            if messages:
                # Use the session_id from the first message or create new one
                actual_session_id = session_id or str(uuid.uuid4())
                
                self.conversations[repo_name] = {
                    'session_id': actual_session_id,
                    'messages': messages,
                    'repo_context': {},
                    'created_at': messages[0]['timestamp'] if messages else datetime.now().isoformat()
                }
                
                logger.info(f"Loaded {len(messages)} messages for {repo_name}")
                return messages
            else:
                # No messages found, start new conversation
                session_id = self.start_conversation(repo_name)
                return []
                
        except Exception as e:
            logger.error(f"Error loading conversation from DB: {e}")
            return []

    def switch_conversation(self, repo_name: str, session_id: str = None):
        """Switch to a specific repository conversation"""
        try:
            # Load conversation from database
            messages = self.load_conversation_from_db(repo_name, session_id)
            
            return {
                'success': True,
                'repo_name': repo_name,
                'session_id': self.conversations.get(repo_name, {}).get('session_id'),
                'messages': messages,
                'message_count': len(messages)
            }
        except Exception as e:
            logger.error(f"Error switching conversation: {e}")
            return {
                'success': False,
                'error': str(e),
                'repo_name': repo_name
            }

    def get_conversation_history(self, repo_name: str,
                                 max_messages: int = 10) -> List[Dict]:
        """Get conversation history for a repository"""
        if repo_name not in self.conversations:
            return []

        messages = self.conversations[repo_name]['messages']
        # Return last max_messages messages
        if len(messages) > max_messages:
            return messages[-max_messages:]
        else:
            return messages

    def format_conversation_for_ai(self, repo_name: str,
                                   max_messages: int = 10) -> str:
        """Format conversation history for AI context"""
        history = self.get_conversation_history(repo_name, max_messages)

        if not history:
            return ""

        formatted = "## Previous Conversation:\n\n"
        for msg in history:
            role = msg['role'].title()
            content = msg['content']
            if len(content) > 500:
                content = content[:500] + "..."
            formatted += f"**{role}:** {content}\n\n"

        return formatted

    def get_repo_context(self, repo_name: str) -> Optional[Dict]:
        """Get repository context"""
        if repo_name in self.conversations:
            return self.conversations[repo_name].get('repo_context')
        return None

    def chat_with_memory(self, repo_name: str, message: str,
                         user_id: str = None) -> str:
        """Chat with memory context about a specific repository"""
        if not self.memory_manager:
            return "Memory system not available"

        if not user_id:
            user_id = f"repo_{repo_name}"

        # Add user message to conversation
        self.add_message(repo_name, "user", message)

        # Get response from memory manager
        response = self.memory_manager.chat_with_memory(
            message, user_id, repo_name
        )

        # Add assistant response to conversation
        self.add_message(repo_name, "assistant", response)

        return response

    def analyze_with_memory(self, repo_name: str, repo_data: Dict,
                            mermaid_diagram: str, user_id: str = None) -> Dict:
        """Analyze repository with memory context"""
        if not self.memory_manager:
            return {"error": "Memory system not available"}

        if not user_id:
            user_id = f"repo_{repo_name}"

        return self.memory_manager.analyze_repository_with_memory(
            repo_data, mermaid_diagram, user_id, repo_name
        )

    def suggest_feature_with_memory(self, repo_name: str,
                                    feature_description: str,
                                    knowledge_base: Dict,
                                    user_id: str = None) -> Dict:
        """Suggest feature placement with memory context"""
        if not self.memory_manager:
            return {"error": "Memory system not available"}

        if not user_id:
            user_id = f"repo_{repo_name}"

        return self.memory_manager.suggest_feature_with_memory(
            feature_description, knowledge_base, user_id, repo_name
        )

    def get_memory_context(self, repo_name: str, query: str, limit: int = 5) -> str:
        """Get memory-based context for a query"""
        if not self.memory_manager:
            return ""
        
        user_id = f"repo_{repo_name}"
        memories = self.memory_manager.search_memories(query, user_id, limit)
        
        if not memories:
            return ""
        
        context = "Previous conversations about similar topics:\n"
        for memory in memories:
            memory_text = memory.get('memory', '')
            if memory_text:
                context += f"- {memory_text}\n"
        
        return context + "\n"
