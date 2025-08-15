"""
Multi-Model AI Client
Tries different AI models when one fails (Gemini, OpenAI, etc.)
"""
import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from openai import OpenAI
from ..utils.prompt_cache import PromptCache
from ..utils.model_error_handler import ModelErrorHandler


class MultiModelClient:
    """
    AI client that tries multiple models as fallbacks
    """
    
    def __init__(self):
        self.models = []
        self.cache = PromptCache()
        self.error_handler = ModelErrorHandler()
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available AI models"""
        
        # Gemini - prioritize GOOGLE_API_KEY since it's more reliable
        gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            try:
                # Store the API key and configure
                genai.configure(api_key=gemini_key)
                self.models.append({
                    'name': 'Gemini',
                    'client': genai.GenerativeModel('gemini-1.5-flash'),
                    'type': 'gemini',
                    'api_key': gemini_key  # Store the key for later use
                })
                print("✅ Gemini model initialized")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
        
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_key_here":
            try:
                openai_client = OpenAI(api_key=openai_key)
                self.models.append({
                    'name': 'OpenAI',
                    'client': openai_client,
                    'type': 'openai'
                })
                print("✅ OpenAI model initialized")
            except Exception as e:
                print(f"⚠️ OpenAI initialization failed: {e}")
        
        # Azure OpenAI
        azure_key = os.getenv("AZURE_OPENAI_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if azure_key and azure_key != "your_azure_key_here" and azure_endpoint:
            try:
                azure_client = OpenAI(
                    api_key=azure_key,
                    azure_endpoint=azure_endpoint,
                    api_version="2024-02-01"
                )
                self.models.append({
                    'name': 'Azure OpenAI',
                    'client': azure_client,
                    'type': 'azure_openai'
                })
                print("✅ Azure OpenAI model initialized")
            except Exception as e:
                print(f"⚠️ Azure OpenAI initialization failed: {e}")
        
        if not self.models:
            print("⚠️ No AI models available - will use mock responses")
    
    def analyze_repository(self, repo_knowledge: Dict, mermaid_diagram: str) -> Dict:
        """Analyze repository with curated, lightweight context and caching for speed."""

        # Normalize inputs (support both knowledge payload and raw file map)
        file_structure = []
        file_contents = {}
        analysis_prev = {}
        if isinstance(repo_knowledge, dict):
            if 'file_structure' in repo_knowledge or 'file_contents' in repo_knowledge:
                file_structure = repo_knowledge.get('file_structure') or []
                file_contents = repo_knowledge.get('file_contents') or {}
                analysis_prev = repo_knowledge.get('analysis') or {}
            else:
                file_structure = list(repo_knowledge.keys())
                file_contents = repo_knowledge

        # Curate file list to reduce prompt size
        def rank(path: str) -> int:
            p = path.lower()
            score = 0
            if any(k in p for k in ["main.py", "app.py", "server", "api/", "routes", "controllers", "views", "pages", "handler"]):
                score += 5
            if any(k in p for k in ["model", "schema", "entity", "dto"]):
                score += 3
            if any(k in p for k in ["service", "usecase", "repository/"]):
                score += 3
            if any(k in p for k in ["config", "settings", "env", "docker", "compose", "requirements.txt", "package.json"]):
                score += 2
            if any(p.endswith(ext) for ext in [".py", ".ts", ".tsx", ".js", ".jsx"]):
                score += 1
            return -score

        ranked_files = sorted(file_structure, key=rank)[:80]
        file_list = [f"- {path}" for path in ranked_files]

        # Sample code from smaller/key files with shorter snippets to cut tokens
        def content_size(item):
            _, info = item
            if isinstance(info, dict):
                return len(info.get('content', '') or '')
            return len(str(info) or '')

        samples = []
        for path in ranked_files:
            if path in file_contents:
                samples.append((path, file_contents[path]))
        if len(samples) < 15:
            for path, info in file_contents.items():
                if path not in dict(samples):
                    samples.append((path, info))
                if len(samples) >= 15:
                    break
        samples = sorted(samples, key=content_size)[:12]

        code_snippets = []
        for path, info in samples:
            content = info.get('content', '') if isinstance(info, dict) else str(info)
            snippet = (content or '')[:1200]
            if snippet:
                code_snippets.append(f"\n--- {path} ---\n{snippet}")

        prev_summary = ""
        if analysis_prev:
            tech = analysis_prev.get('tech_stack') or {}
            comps = analysis_prev.get('components') or []
            prev_summary = f"Tech stack: {tech}\nComponents (sample): {comps[:10]}\n"

        more_files_text = (f"... and {max(0, len(file_structure) - len(ranked_files))} more files"
                           if len(file_structure) > len(ranked_files) else "")

        prompt = f"""
        You are analyzing an ALREADY UPLOADED repository. Analyze ONLY the provided files.

        SUMMARY CONTEXT (existing knowledge):
        {prev_summary}

        ARCHITECTURE DIAGRAM (Mermaid):
        {mermaid_diagram}

        CURATED FILE LIST (top {len(ranked_files)} by importance):
        {chr(10).join(file_list)}
        {more_files_text}

        ACTUAL CODE SAMPLES ({len(code_snippets)} files):
        {chr(10).join(code_snippets)}

        TASK: Provide:
        1) Architecture summary with file references
        2) Data flow/API structure citing files/functions
        3) Integration points and dependencies
        4) Specific recommendations with exact file paths

        Only use the provided context. Do not suggest accessing external repositories.
        """

        # Fast-path cache (cheap and coarse key)
        cache_key = f"analyze::{len(file_structure)}::{bool(mermaid_diagram)}::{len(code_snippets)}"
        cached = self.cache.get(cache_key, "summary")
        if cached:
            return {"architecture_summary": cached, "model_used": "cache"}

        # Model attempts (favor fast settings)
        for model_info in self.models:
            try:
                if model_info['type'] == 'gemini':
                    import time
                    max_retries = 1
                    base_delay = 1
                    for attempt in range(max_retries + 1):
                        try:
                            resp = model_info['client'].generate_content(prompt)
                            summary = resp.text
                            if summary:
                                self.cache.set(cache_key, summary, "summary")
                            return {"architecture_summary": summary, "model_used": model_info['name']}
                        except Exception as e:
                            if attempt < max_retries and ("504" in str(e) or "deadline" in str(e).lower()):
                                time.sleep(base_delay)
                                continue
                            break
                elif model_info['type'] in ['openai', 'azure_openai']:
                    response = model_info['client'].chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert software architect."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=600,
                        temperature=0.2
                    )
                    summary = response.choices[0].message.content
                    if summary:
                        self.cache.set(cache_key, summary, "summary")
                    return {"architecture_summary": summary, "model_used": model_info['name']}
            except Exception as e:
                print(f"❌ {model_info['name']} failed: {e}")
                continue

        # Fallback
        fallback = self._mock_analysis(repo_knowledge, mermaid_diagram)
        self.cache.set(cache_key, fallback.get("architecture_summary", ""), "summary")
        return fallback
    
    def suggest_feature_placement(self, feature_description: str, knowledge_base: Dict) -> Dict:
        """Suggest feature placement using available models"""
        
        # Extract detailed information from knowledge base
        repo_structure = knowledge_base.get('file_structure', {})
        file_contents = knowledge_base.get('file_contents', {})
        analysis = knowledge_base.get('analysis', {})
        mermaid_diagram = knowledge_base.get('mermaid_diagram', '')
        
        # Create detailed file structure overview
        file_details = []
        component_files = []
        config_files = []
        
        # Use file_contents for detailed analysis
        all_files = {**repo_structure, **file_contents}
        
        for file_path, file_info in all_files.items():
            if isinstance(file_info, dict):
                file_type = file_info.get('type', 'unknown')
                file_size = len(file_info.get('content', ''))
                file_details.append(f"- {file_path} ({file_type}, {file_size} chars)")
            else:
                # Handle direct content
                file_size = len(str(file_info))
                file_details.append(f"- {file_path} ({file_size} chars)")
            
            # Categorize important files
            if any(keyword in file_path.lower() for keyword in ['component', 'page', 'view', 'controller']):
                component_files.append(file_path)
            elif any(keyword in file_path.lower() for keyword in ['config', 'env', 'setting', 'package.json']):
                config_files.append(file_path)
        
        # Include actual code samples from key files (prioritize file_contents)
        code_examples = []
        files_to_sample = file_contents if file_contents else repo_structure
        
        for file_path, file_info in list(files_to_sample.items())[:15]:  # First 15 files
            if isinstance(file_info, dict):
                content = file_info.get('content', '')
            else:
                content = str(file_info)
                
            if content and len(content) < 3000:
                code_examples.append(f"\n=== {file_path} ===\n{content[:1500]}")
            elif content:
                # For larger files, include more context
                code_examples.append(f"\n=== {file_path} (excerpt) ===\n{content[:2000]}...")
        
        prompt = f"""
        You are an expert software architect with COMPLETE ACCESS to the full codebase.
        
        IMPORTANT: You are NOT working with a "high-level description" - you have the COMPLETE source code below.
        
        TASK: Analyze this COMPLETE codebase and provide SPECIFIC, actionable recommendations for implementing this feature: "{feature_description}"
        
        === COMPLETE CODEBASE ANALYSIS ===
        
        FULL REPOSITORY STRUCTURE ({len(all_files)} files):
        {chr(10).join(file_details)}
        
        KEY COMPONENT FILES:
        {chr(10).join(component_files)}
        
        CONFIGURATION FILES:
        {chr(10).join(config_files)}
        
        ARCHITECTURE DIAGRAM:
        {mermaid_diagram}
        
        EXISTING ANALYSIS:
        {str(analysis)[:1000]}
        
        === ACTUAL SOURCE CODE FROM THE REPOSITORY ===
        {''.join(code_examples)}
        
        === END OF CODEBASE ANALYSIS ===
        
        CRITICAL: You have been provided with the COMPLETE codebase analysis above, including actual source code from {len(code_examples)} files. 
        This is NOT a high-level description - you have full access to the implementation details.
        
        Based on this COMPLETE codebase analysis, provide SPECIFIC recommendations:
        
        1. EXACT FILE PATHS where code should be added/modified (reference actual files you see above)
        2. SPECIFIC FUNCTIONS/CLASSES to modify (look at the actual code samples provided)
        3. NEW FILES to create with exact paths and purposes
        4. INTEGRATION POINTS with existing code patterns (reference the actual code you see)
        5. DEPENDENCIES that might need to be added
        6. STEP-BY-STEP implementation plan with specific code changes
        
        Be extremely specific and reference the actual files, functions, and patterns you see in the codebase above.
        Do NOT give generic responses - you have the full codebase context.
        """
        
        # Try each model
        for model_info in self.models:
            try:
                print(f"Trying {model_info['name']} for feature placement...")
                
                if model_info['type'] == 'gemini':
                    # Add timeout and retry logic for Gemini
                    import time
                    max_retries = 2
                    base_delay = 1
                    
                    for attempt in range(max_retries + 1):
                        try:
                            response = model_info['client'].generate_content(prompt)
                            return {
                                "suggestions": response.text,
                                "model_used": model_info['name']
                            }
                        except Exception as gemini_error:
                            if "504" in str(gemini_error) or "deadline" in str(gemini_error).lower():
                                if attempt < max_retries:
                                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                                    print(f"❌ {model_info['name']} timeout (attempt {attempt + 1}/{max_retries + 1}), retrying in {delay}s...")
                                    time.sleep(delay)
                                    continue
                                else:
                                    print(f"❌ {model_info['name']} failed after {max_retries + 1} attempts: {gemini_error}")
                                    break
                            else:
                                print(f"❌ {model_info['name']} failed: {gemini_error}")
                                break
                
                elif model_info['type'] in ['openai', 'azure_openai']:
                    response = model_info['client'].chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert software architect."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.3
                    )
                    return {
                        "suggestions": response.choices[0].message.content,
                        "model_used": model_info['name']
                    }
                    
            except Exception as e:
                print(f"❌ {model_info['name']} failed: {e}")
                continue
        
        # All models failed
        return {
            "suggestions": f"Unable to analyze due to API issues. Consider adding {feature_description} to the main application files.",
            "model_used": "fallback"
        }
    
    async def generate_response(self, prompt: str, model_preference: str = None) -> str:
        """
        Generate a response using available AI models with caching
        """
        # Check cache first
        cached_response = self.cache.get(prompt, model_preference or "default")
        if cached_response:
            return cached_response
        
        # Clear expired cache entries periodically
        self.cache.clear_expired()
        
        # Try to generate response
        models_to_try = self.models.copy()
        
        # If model preference is specified, try it first
        if model_preference:
            preferred_models = [m for m in models_to_try if m['name'].lower() == model_preference.lower()]
            if preferred_models:
                models_to_try = preferred_models + [m for m in models_to_try if m not in preferred_models]
        
        for model_info in models_to_try:
            try:
                print(f"Trying {model_info['name']} model...")
                
                if model_info['name'] == 'Gemini':
                    # Ensure API key is configured before making the call
                    if 'api_key' in model_info:
                        genai.configure(api_key=model_info['api_key'])
                    
                    # Add timeout and retry logic for Gemini
                    import time
                    max_retries = 2
                    base_delay = 1
                    
                    for attempt in range(max_retries + 1):
                        try:
                            response = model_info['client'].generate_content(prompt)
                            result = response.text
                            
                            # Cache the successful response
                            self.cache.set(prompt, result, model_info['name'])
                            print(f"✅ {model_info['name']} response generated and cached")
                            return result
                            
                        except Exception as gemini_error:
                            self.error_handler.record_error(model_info['name'], gemini_error, {'attempt': attempt + 1})
                            
                            if "504" in str(gemini_error) or "deadline" in str(gemini_error).lower():
                                if attempt < max_retries:
                                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                                    print(f"❌ {model_info['name']} timeout (attempt {attempt + 1}/{max_retries + 1}), retrying in {delay}s...")
                                    time.sleep(delay)
                                    continue
                                else:
                                    print(f"❌ {model_info['name']} failed after {max_retries + 1} attempts: {gemini_error}")
                                    
                                    # Check if we have a recent relevant cache for this type of request
                                    cached_response = self.cache.get(prompt, model_info['name'])
                                    if cached_response:
                                        print(f"🔄 Using relevant cached response due to timeout")
                                        return cached_response
                                    break
                            else:
                                print(f"❌ {model_info['name']} failed: {gemini_error}")
                                break
                
                elif model_info['name'] in ['OpenAI GPT-4', 'OpenAI GPT-3.5']:
                    response = model_info['client'].chat.completions.create(
                        model=model_info['model_id'],
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=4000,
                        temperature=0.7
                    )
                    result = response.choices[0].message.content
                    
                    # Cache the successful response
                    self.cache.set(prompt, result, model_info['name'])
                    print(f"✅ {model_info['name']} response generated and cached")
                    return result
                else:
                    continue
                
                
            except Exception as e:
                self.error_handler.record_error(model_info['name'], e)
                print(f"❌ {model_info['name']} failed: {e}")
                continue

        # If all models fail, return a contextual fallback response
        failed_models = [model['name'] for model in models_to_try]
        fallback_response = self.error_handler.generate_contextual_fallback(prompt, failed_models)
        self.cache.set(prompt, fallback_response, "enhanced_fallback")
        return fallback_response

    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when all AI models fail"""
        
        # Analyze the prompt to provide more contextual fallback
        prompt_lower = prompt.lower()
        
        # Check for specific types of requests
        if any(keyword in prompt_lower for keyword in ["crypto", "blockchain", "bitcoin", "ethereum", "solana", "defi"]):
            return """I apologize, but I'm currently unable to access AI models to provide detailed crypto/blockchain analysis. 

For building a crypto analysis agent with news and data fetching:

## Recommended Approach:
1. **Data Sources Integration:**
   - CoinGecko API for price/market data
   - News APIs (NewsAPI, Alpha Vantage) for sentiment analysis
   - Twitter API v2 for social sentiment
   - Blockchain APIs (Etherscan, Solana API) for on-chain data

2. **Implementation Strategy:**
   - Use the HTTP request tools for API integrations
   - Create custom tools for each data source
   - Implement data aggregation and analysis logic
   - Use the agent builder to orchestrate different analysis tasks

3. **Architecture Suggestions:**
   - Separate data collection, analysis, and reporting agents
   - Use shared memory for cross-agent communication
   - Implement caching for expensive API calls
   - Add error handling for API rate limits

Please try again later for more detailed assistance, or check the examples directory for HTTP integration patterns."""

        elif any(keyword in prompt_lower for keyword in ["next.js", "nextjs", "react", "frontend"]):
            return """I'm currently unable to access AI models for detailed Next.js guidance.

For integrating with Next.js:
- The SDK appears to support Next.js based on the tsconfig/nextjs.json configuration
- Check the examples directory for integration patterns
- Use the agent builder in your Next.js API routes
- Consider server-side agent execution for better performance

Please try again later for specific implementation details."""

        elif any(keyword in prompt_lower for keyword in ["visualization", "chart", "graph", "dashboard"]):
            return """I'm unable to provide detailed visualization guidance right now.

For adding visualizations:
1. **Frontend Components:**
   - Create reusable chart components
   - Use libraries like Recharts, Chart.js, or D3.js

2. **Data Integration:**
   - Connect to your analysis agents via API
   - Implement real-time data updates
   - Add filtering and interaction capabilities

3. **Common Locations:**
   - `src/components/charts/` for reusable components
   - `src/pages/dashboard/` for visualization pages
   - Update routing and navigation as needed

Please try again later for more specific recommendations."""

        elif "sdk" in prompt_lower or "adk" in prompt_lower:
            return """I'm currently unable to access AI models for detailed SDK analysis.

Based on the repository structure, the ADK (Agent Development Kit) provides:
- Multi-LLM support (Gemini, OpenAI, Anthropic)
- Agent builder with fluent API
- Tool creation framework
- Session management
- Memory services
- Code execution capabilities

Key capabilities for your use case:
- HTTP request tools for API integration
- Agent orchestration and workflow management
- Tool composition and reuse
- Authentication handling

Check the apps/examples directory for implementation patterns and starter templates.

Please try again later for more detailed guidance."""

        else:
            return """I apologize, but I'm currently unable to access the AI models to provide a detailed response. This appears to be a temporary issue.

## Troubleshooting Steps:
1. Check your internet connection
2. Verify API keys are configured correctly
3. Try again in a few moments
4. Check the console for specific error messages

## General Recommendations:
- Follow established patterns in your existing codebase
- Consult documentation for your framework/libraries
- Look at similar projects for inspiration
- Check the examples directory for implementation patterns

If the issue persists, consider:
- Checking API service status
- Reviewing rate limiting policies
- Ensuring proper authentication configuration

Please try your request again later."""
    
    def _mock_analysis(self, repo_data: Dict, mermaid_diagram: str) -> Dict:
        """Generate mock analysis when all AI models fail"""
        file_count = len(repo_data)
        
        # Identify tech stack from files
        tech_stack = []
        js_files = any('.js' in f or '.jsx' in f or '.ts' in f or '.tsx' in f
                       for f in repo_data.keys())
        if js_files:
            tech_stack.append('JavaScript/TypeScript')
        if any('.py' in f for f in repo_data.keys()):
            tech_stack.append('Python')
        if any('.java' in f for f in repo_data.keys()):
            tech_stack.append('Java')
        if any('.go' in f for f in repo_data.keys()):
            tech_stack.append('Go')
        
        # Look for common framework files
        frameworks = []
        if 'package.json' in repo_data:
            frameworks.append('Node.js project')
        if 'requirements.txt' in repo_data or 'pyproject.toml' in repo_data:
            frameworks.append('Python project')
        if any('dockerfile' in f.lower() for f in repo_data.keys()):
            frameworks.append('Containerized application')
        
        return {
            "architecture_summary": f"""
## Repository Analysis (Based on Available Files)

**Project Overview:**
- Total files analyzed: {file_count}
- Technologies detected: {', '.join(tech_stack) if tech_stack else 'Multiple technologies'}
- Project type: {', '.join(frameworks) if frameworks else 'Mixed/General purpose'}

**Architecture Summary:**
This appears to be a {frameworks[0] if frameworks else 'software'} project with the following structure:

**Key Components Identified:**
{chr(10).join(f'• {file}' for file in list(repo_data.keys())[:10])}
{'• ... and more files' if file_count > 10 else ''}

**Recommendations for Feature Development:**
1. Follow the existing file organization patterns
2. Add new features in appropriate directories based on the current structure
3. Maintain consistency with the existing codebase style

**Note:** This analysis is based on the files available in the uploaded
codebase. For more detailed recommendations, please ensure your AI API keys
are configured correctly.

**System Diagram:**
```mermaid
{mermaid_diagram}
```
            """,
            "model_used": "fallback_analysis"
        }
