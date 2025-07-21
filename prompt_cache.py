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
            
            print(f"Cache hit for prompt: {prompt[:50]}...")
            return cache_data['response']
            
        except Exception as e:
            print(f"Error reading cache: {e}")
            return None
    
    def set(self, prompt: str, response: str, model: str = "default") -> None:
        """Store response in cache"""
        try:
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
