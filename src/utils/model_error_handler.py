"""
Enhanced error handling and context management for AI model failures
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime


class ModelErrorHandler:
    """Handles errors and provides contextual fallbacks for AI model failures"""
    
    def __init__(self):
        self.error_count = {}
        self.last_errors = {}
        self.logger = logging.getLogger(__name__)
    
    def record_error(self, model_name: str, error: Exception, context: Dict[str, Any] = None):
        """Record an error for a specific model"""
        error_key = f"{model_name}_{type(error).__name__}"
        
        if error_key not in self.error_count:
            self.error_count[error_key] = 0
        
        self.error_count[error_key] += 1
        self.last_errors[model_name] = {
            'error': str(error),
            'type': type(error).__name__,
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        self.logger.warning(f"Model {model_name} error: {error}")
    
    def should_retry(self, model_name: str, error: Exception) -> bool:
        """Determine if we should retry a failed model"""
        error_str = str(error).lower()
        
        # Don't retry on authentication errors
        if any(term in error_str for term in ['auth', 'key', 'token', 'permission']):
            return False
        
        # Don't retry on quota exceeded
        if any(term in error_str for term in ['quota', 'limit', 'billing']):
            return False
        
        # Retry on timeout and server errors
        if any(term in error_str for term in ['timeout', '504', '502', '503', 'deadline']):
            return True
        
        # Check error frequency
        error_key = f"{model_name}_{type(error).__name__}"
        if self.error_count.get(error_key, 0) > 3:
            return False
        
        return True
    
    def get_retry_delay(self, attempt: int) -> float:
        """Get exponential backoff delay"""
        return min(2 ** attempt, 30)  # Cap at 30 seconds
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        return {
            'error_counts': self.error_count.copy(),
            'last_errors': self.last_errors.copy(),
            'total_errors': sum(self.error_count.values())
        }
    
    def is_model_healthy(self, model_name: str) -> bool:
        """Check if a model is currently healthy"""
        if model_name not in self.last_errors:
            return True
        
        last_error = self.last_errors[model_name]
        error_time = datetime.fromisoformat(last_error['timestamp'])
        
        # Consider model healthy if no errors in last 10 minutes
        time_since_error = (datetime.now() - error_time).total_seconds()
        return time_since_error > 600
    
    def generate_contextual_fallback(self, prompt: str, failed_models: list) -> str:
        """Generate a contextual fallback response based on the prompt and failed models"""
        prompt_lower = prompt.lower()
        
        # Analyze what models failed and why
        failure_summary = []
        for model in failed_models:
            if model in self.last_errors:
                error_info = self.last_errors[model]
                failure_summary.append(f"{model}: {error_info['type']}")
        
        failure_text = ", ".join(failure_summary) if failure_summary else "Multiple model failures"
        
        # Generate response based on prompt content
        if any(keyword in prompt_lower for keyword in ["crypto", "blockchain", "bitcoin"]):
            return f"""I apologize, but I'm experiencing technical difficulties with AI models ({failure_text}).

For crypto analysis development, consider these approaches:

**Data Integration:**
- CoinGecko API: Real-time price data
- NewsAPI/Alpha Vantage: Market news
- Twitter API v2: Social sentiment  
- Blockchain APIs: On-chain metrics

**Implementation Pattern:**
```python
# Example structure for your agent
from src.ai.multi_model_client import MultiModelClient
from src.utils.http_client import HttpClient

class CryptoAnalysisAgent:
    def __init__(self):
        self.ai_client = MultiModelClient()
        self.http_client = HttpClient()
    
    async def analyze_market(self, symbol: str):
        # Fetch data from multiple sources
        price_data = await self.fetch_price_data(symbol)
        news_data = await self.fetch_news(symbol)
        sentiment = await self.analyze_sentiment(news_data)
        
        # Combine and analyze
        return await self.generate_analysis(price_data, news_data, sentiment)
```

Please try again in a few minutes once the AI services recover."""

        elif any(keyword in prompt_lower for keyword in ["next.js", "react", "frontend"]):
            return f"""I'm experiencing AI model issues ({failure_text}), but I can provide general guidance:

**Next.js Integration:**
The SDK supports Next.js (see packages/tsconfig/nextjs.json). Key integration points:

1. **API Routes** (`pages/api/` or `app/api/`):
```javascript
// pages/api/agent.js
import {{{{ AgentBuilder }}}} from '@iqai/adk';

export default async function handler(req, res) {{{{
  const agent = new AgentBuilder()
    .withModel('gemini-2.0-flash')
    .withName('assistant')
    .build();
    
  const response = await agent.run(req.body.message);
  res.json({{{{ response }}}});
}}}}
```

2. **Frontend Integration**:
```javascript
// components/ChatInterface.jsx
const sendMessage = async (message) => {{{{
  const response = await fetch('/api/agent', {{{{
    method: 'POST',
    headers: {{{{ 'Content-Type': 'application/json' }}}},
    body: JSON.stringify({{{{ message }}}})
  }}}});
  return response.json();
}}}};
```

Please retry your request once AI services are restored."""

        else:
            return f"""I'm currently experiencing technical difficulties with AI models ({failure_text}).

**Temporary Workaround:**
1. Check the examples directory for implementation patterns
2. Review the documentation for your specific use case
3. Try again in a few minutes

**If this persists:**
- Verify API keys are properly configured
- Check network connectivity
- Review rate limiting policies

The issue appears to be temporary. Please try your request again shortly."""
