"""
Memory Manager using mem0 for long-term memory in conversations
"""
from typing import List, Dict
from google import genai
from mem0 import Memory
import os
import logging
import json

logger = logging.getLogger(__name__)


class MemoryManager:
    def __init__(self, api_key: str = None):
        """Initialize Memory Manager with enhanced local memory and optional mem0"""
        # Get API key from environment
        api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        # Initialize enhanced local memory
        self.local_memory = {}  # user_id -> list of memories
        self.memory_index = {}  # user_id -> search index
        
        # Try to initialize mem0 as optional enhancement
        self.memory = None
        if api_key:
            try:
                # Set the API key as an environment variable for mem0
                os.environ["GEMINI_API_KEY"] = api_key
                
                # Initialize Google GenAI client
                self.client = genai.Client(api_key=api_key)

                # Configure mem0 with local embeddings and Gemini LLM
                config = {
                    "embedder": {
                        "provider": "huggingface",
                        "config": {
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
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
                        "provider": "chroma",
                        "config": {
                            "collection_name": "codebase_agent_memories",
                            "path": "./mem0_storage"
                        }
                    }
                }

                self.memory = Memory.from_config(config)
                logger.info("Memory system initialized with mem0 enhancement")
                
            except Exception as e:
                logger.warning(f"Failed to initialize mem0, using local memory only: {e}")
                self.memory = None
        else:
            logger.info("No API key provided, using local memory only")
        
        if not self.memory:
            logger.info("Using enhanced local memory system")

    def add_conversation(self, messages: List[Dict], user_id: str) -> bool:
        """Add a conversation to memory with enhanced context"""
        success = False
        
        # Try mem0 first
        if self.memory:
            try:
                # Add individual messages as separate memories for better search
                for msg in messages:
                    content = msg.get("content", "")
                    role = msg.get("role", "user")
                    
                    if role == "user":
                        # Add user questions as searchable memories
                        self.memory.add(
                            f"User asked: {content}",
                            user_id=user_id,
                            metadata={"type": "question", "timestamp": self._get_timestamp()}
                        )
                    elif role == "assistant":
                        # Add assistant responses as searchable memories
                        response_text = content[:1000]  # Limit length
                        self.memory.add(
                            f"Assistant responded: {response_text}",
                            user_id=user_id,
                            metadata={"type": "response", "timestamp": self._get_timestamp()}
                        )
                
                success = True
                logger.info(f"Added conversation to mem0 for user {user_id}")
                
            except Exception as e:
                logger.error(f"Failed to add conversation to mem0: {e}")
        
        # Fallback to local memory
        if not success:
            if user_id not in self.local_memory:
                self.local_memory[user_id] = []
            
            for msg in messages:
                memory_entry = {
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                    "timestamp": self._get_timestamp(),
                    "metadata": msg.get("metadata", {})
                }
                self.local_memory[user_id].append(memory_entry)
            
            logger.info(f"Added conversation to local memory for user {user_id}")
            success = True
        
        return success

    def search_memories(self, query: str, user_id: str,
                        limit: int = 5) -> List[Dict]:
        """Search relevant memories with enhanced context"""
        results = []
        
        # Try mem0 first
        if self.memory:
            try:
                # Primary search for the exact query
                related_memories = self.memory.search(
                    query=query,
                    user_id=user_id,
                    limit=limit
                )
                
                results = related_memories.get("results", [])
                
                # If we don't have enough results, try broader searches
                if len(results) < limit:
                    # Extract key terms from the query for expanded search
                    key_terms = self._extract_key_terms(query)
                    
                    for term in key_terms:
                        if len(results) >= limit:
                            break
                            
                        additional_memories = self.memory.search(
                            query=term,
                            user_id=user_id,
                            limit=limit - len(results)
                        )
                        
                        # Add new memories (avoid duplicates)
                        existing_memories = {r.get('memory', '') for r in results}
                        for mem in additional_memories.get("results", []):
                            if mem.get('memory', '') not in existing_memories:
                                results.append(mem)
                
                if results:
                    logger.info(f"Found {len(results)} relevant memories from mem0 for query: {query}")
                    return results
                    
            except Exception as e:
                logger.error(f"Failed to search mem0 memories: {e}")
        
        # Fallback to enhanced local memory search
        if user_id in self.local_memory:
            local_memories = self.local_memory[user_id]
            query_terms = query.lower().split()
            scored_memories = []
            
            # Enhanced text matching with scoring
            for memory in local_memories:
                content = memory.get('content', '').lower()
                score = 0
                
                # Exact phrase match gets highest score
                if query.lower() in content:
                    score += 10
                
                # Individual word matches
                for term in query_terms:
                    if term in content:
                        score += 1
                
                # Partial word matches
                for term in query_terms:
                    if any(term in word for word in content.split()):
                        score += 0.5
                
                if score > 0:
                    scored_memories.append((score, memory))
            
            # Sort by score and return top results
            scored_memories.sort(key=lambda x: x[0], reverse=True)
            
            for score, memory in scored_memories[:limit]:
                results.append({
                    'memory': memory.get('content', ''),
                    'score': score,
                    'metadata': memory.get('metadata', {})
                })
            
            if results:
                logger.info(f"Found {len(results)} relevant memories from enhanced local storage for query: {query}")
            else:
                logger.info(f"No relevant memories found for query: {query}")
        
        return results
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query for expanded search"""
        # Simple keyword extraction - remove common words
        stop_words = {'how', 'to', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'for', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'ours', 'theirs', 'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'yourselves', 'themselves'}
        
        words = query.lower().split()
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms[:3]  # Return top 3 key terms

    def get_memories_context(self, query: str, user_id: str,
                             limit: int = 5) -> str:
        """Get formatted memory context for AI prompts"""
        memories = self.search_memories(query, user_id, limit)

        if not memories:
            return ""

        memories_str = "\n".join(f"- {entry['memory']}" for entry in memories)
        return f"User Memories:\n{memories_str}"

    def generate_with_memory(self, prompt: str, user_id: str,
                             system_instruction: str = None,
                             conversation_history: List[Dict] = None) -> str:
        """Generate response using memories and conversation history"""
        try:
            # Get relevant memories
            memory_context = self.get_memories_context(prompt, user_id)

            # Default system instruction
            if not system_instruction:
                system_instruction = "You are a helpful AI assistant."

            # Enhance system instruction with memories
            if memory_context:
                enhanced_system = f"{system_instruction}\n\n{memory_context}"
            else:
                enhanced_system = system_instruction

            # Prepare conversation history in Gemini format
            if conversation_history:
                # Convert to Gemini format
                contents = []
                for msg in conversation_history:
                    if msg.get("role") == "user":
                        contents.append({
                            "role": "user",
                            "parts": [{"text": msg["content"]}]
                        })
                    elif msg.get("role") == "assistant":
                        contents.append({
                            "role": "model",
                            "parts": [{"text": msg["content"]}]
                        })

                # Add current prompt
                contents.append({
                    "role": "user",
                    "parts": [{"text": prompt}]
                })
            else:
                contents = prompt

            # Generate response
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config={
                    "system_instruction": enhanced_system
                }
            )

            # Store conversation in memory
            if conversation_history:
                # Add the new exchange to conversation history
                updated_history = conversation_history + [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": response.text}
                ]
                self.add_conversation(updated_history, user_id)
            else:
                # Store single exchange
                self.add_conversation([
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": response.text}
                ], user_id)

            return response.text

        except Exception as e:
            logger.error(f"Failed to generate response with memory: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

    def analyze_repository_with_memory(self, repo_data: Dict,
                                       mermaid_diagram: str,
                                       user_id: str, repo_name: str) -> Dict:
        """Analyze repository with memory context"""
        prompt = f"""
        Analyze this repository structure and Mermaid diagram:

        Repository: {repo_name}
        Repository Data: {repo_data}

        Mermaid Diagram:
        {mermaid_diagram}

        Please provide:
        1. Architecture summary
        2. Key components and their relationships
        3. Data flow patterns
        4. Integration points
        5. Potential areas for feature additions

        Consider any previous context about this repository from our
        conversation history.
        """

        system_instruction = ("You are an expert software architect analyzing "
                              "codebases. Use your knowledge of software "
                              "patterns and the user's previous interactions "
                              "to provide comprehensive analysis.")

        response = self.generate_with_memory(prompt, user_id,
                                             system_instruction)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"analysis": response, "repo_name": repo_name}

    def suggest_feature_with_memory(self, feature_description: str,
                                    knowledge_base: Dict,
                                    user_id: str, repo_name: str) -> Dict:
        """Suggest feature placement with memory context"""
        prompt = f"""
        Based on this codebase knowledge for repository '{repo_name}':
        {knowledge_base}

        I want to add this feature: {feature_description}

        Please suggest:
        1. Exact file paths where code should be added
        2. Specific functions/classes to modify
        3. New files that need to be created
        4. Dependencies that need to be updated
        5. Integration points with existing code

        Consider our previous conversations about this codebase and any
        patterns you've observed.
        Be specific about repository, file, and line numbers where possible.
        """

        system_instruction = ("You are an expert software architect. Provide "
                              "specific, actionable recommendations for "
                              "implementing features based on the codebase "
                              "structure and previous conversation context.")

        response = self.generate_with_memory(prompt, user_id,
                                             system_instruction)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"suggestions": response, "feature": feature_description}

    def chat_with_memory(self, message: str, user_id: str,
                         repo_name: str = None) -> str:
        """General chat with memory context"""
        context = f" about repository '{repo_name}'" if repo_name else ""
        system_instruction = (f"You are a helpful AI assistant specializing "
                              f"in software development and architecture. You "
                              f"remember previous conversations and can "
                              f"provide context-aware assistance{context}.")

        return self.generate_with_memory(message, user_id, system_instruction)

    def _get_timestamp(self) -> str:
        """Get current timestamp for memory metadata"""
        from datetime import datetime
        return datetime.now().isoformat()

    def debug_memory_status(self, user_id: str) -> Dict:
        """Debug memory system status"""
        if not self.memory:
            return {"status": "Memory system not available"}
        
        try:
            # Try a simple search instead of get_all
            test_memories = self.memory.search(
                query="test",
                user_id=user_id,
                limit=10
            )
            
            return {
                "status": "Memory system active",
                "search_results": len(test_memories.get("results", [])),
                "user_id": user_id,
                "sample_results": test_memories.get("results", [])[:2]
            }
        except Exception as e:
            return {
                "status": "Error checking memory",
                "error": str(e),
                "user_id": user_id
            }
