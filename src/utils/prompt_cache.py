import hashlib
import json
import os
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


class PromptCache:
    """Simple file-based cache for AI responses to avoid redundant API calls"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, prompt: str, model: str = "default") -> str:
        """Generate a cache key from prompt and model"""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get the file path for a cache key"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, prompt: str, model: str = "default") -> Optional[str]:
        """Retrieve cached response if available and not expired"""
        try:
            cache_key = self._get_cache_key(prompt, model)
            cache_path = self._get_cache_path(cache_key)
            
            if not os.path.exists(cache_path):
                return None
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                # Cache expired, remove file
                os.remove(cache_path)
                return None
            
            # Check if the cached prompt is actually relevant to the current one
            cached_prompt = cache_data.get('prompt', '')
            
            # For conversation-based prompts, check if they're from the same context
            if self._is_conversation_relevant(prompt, cached_prompt):
                print(f"Cache hit for prompt: {prompt[:50]}...")
                return cache_data['response']
            else:
                print(f"Cache found but not relevant for current context: {prompt[:50]}...")
                return None
            
        except Exception as e:
            print(f"Error reading cache: {e}")
            return None
    
    def _is_conversation_relevant(self, current_prompt: str, cached_prompt: str) -> bool:
        """Check if cached response is relevant to current prompt context"""
        
        # Extract repository/user context from prompts
        def extract_context_markers(prompt: str):
            markers = set()
            
            # Look for repository names
            import re
            repo_pattern = r"(?:repository|repo)['\s]*[\"'`]?([a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+)[\"'`]?"
            repo_matches = re.findall(repo_pattern, prompt.lower())
            markers.update(repo_matches)
            
            # Look for user IDs
            user_pattern = r"user[_\s]*id['\s]*[\"'`]?([a-zA-Z0-9\-_]+)[\"'`]?"
            user_matches = re.findall(user_pattern, prompt.lower())
            markers.update(user_matches)
            
            # Look for specific project names
            project_pattern = r"[\"'`]([a-zA-Z0-9\-_]{3,})[\"'`]"
            project_matches = re.findall(project_pattern, prompt)
            markers.update([m.lower() for m in project_matches if len(m) > 3])
            
            return markers
        
        current_markers = extract_context_markers(current_prompt)
        cached_markers = extract_context_markers(cached_prompt)
        
        # If no specific markers found, allow cache (for general questions)
        if not current_markers and not cached_markers:
            return True
            
        # If markers exist, they should overlap significantly
        if current_markers and cached_markers:
            overlap = len(current_markers.intersection(cached_markers))
            total_unique = len(current_markers.union(cached_markers))
            similarity = overlap / total_unique if total_unique > 0 else 0
            return similarity > 0.5  # At least 50% similarity
        
        # If one has markers and other doesn't, they're likely not relevant
        return False
    
    def set(self, prompt: str, response: str, model: str = "default") -> None:
        """Store response in cache"""
        try:
            # Limit response size to prevent huge cache files
            max_response_size = 50000  # 50KB limit
            if len(response) > max_response_size:
                print(f"Response too large for cache ({len(response)} chars), truncating...")
                response = response[:max_response_size] + "\n\n[Response truncated for caching...]"
            
            cache_key = self._get_cache_key(prompt, model)
            cache_path = self._get_cache_path(cache_key)
            
            cache_data = {
                'prompt': prompt,
                'response': response,
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            print(f"Cached response for prompt: {prompt[:50]}...")
            
        except Exception as e:
            print(f"Error writing cache: {e}")
    
    def clear_expired(self) -> int:
        """Remove expired cache files and return count of removed files"""
        removed_count = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.cache_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        cached_time = datetime.fromisoformat(cache_data['timestamp'])
                        if datetime.now() - cached_time > self.ttl:
                            os.remove(filepath)
                            removed_count += 1
                    except Exception:
                        # If we can't read the file, remove it
                        os.remove(filepath)
                        removed_count += 1
        except Exception as e:
            print(f"Error clearing expired cache: {e}")
        
        if removed_count > 0:
            print(f"Removed {removed_count} expired cache files")
        
        return removed_count
    
    def clear_all(self) -> int:
        """Remove all cache files and return count of removed files"""
        removed_count = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.cache_dir, filename)
                    os.remove(filepath)
                    removed_count += 1
        except Exception as e:
            print(f"Error clearing cache: {e}")
        
        if removed_count > 0:
            print(f"Removed {removed_count} cache files")
        
        return removed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            total_size = sum(
                os.path.getsize(os.path.join(self.cache_dir, f)) 
                for f in cache_files
            )
            
            return {
                'total_entries': len(cache_files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_dir': self.cache_dir
            }
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {'error': str(e)}
