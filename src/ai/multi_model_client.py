"""
Multi-Model AI Client
Tries different AI models when one fails (Gemini, OpenAI, etc.)
"""
import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from openai import OpenAI
from ..utils.prompt_cache import PromptCache


class MultiModelClient:
    """
    AI client that tries multiple models as fallbacks
    """
    
    def __init__(self):
        self.models = []
        self.cache = PromptCache()
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
    
    def analyze_repository(self, repo_data: Dict, mermaid_diagram: str) -> Dict:
        """Try to analyze repository with available models"""
        
        # Create detailed repository overview
        file_list = []
        code_snippets = []
        
        for file_path, file_info in repo_data.items():
            file_list.append(f"- {file_path} ({file_info.get('type', 'unknown')})")
            
            # Include code snippets for important files
            if file_info.get('content') and len(file_info.get('content', '')) < 2000:
                code_snippets.append(f"\n--- {file_path} ---\n{file_info.get('content', '')[:1000]}")
        
        more_files_text = (f"... and {len(repo_data) - 50} more files" 
                           if len(repo_data) > 50 else "")
        
        prompt = f"""
        You are analyzing a repository that has been ALREADY UPLOADED and extracted. 
        You have COMPLETE access to the codebase content below. DO NOT suggest 
        accessing external repositories or GitHub links - analyze ONLY the provided 
        files.
        
        COMPLETE REPOSITORY DATA PROVIDED:
        - Total files available: {len(repo_data)}
        - File structure (all files listed):
        {chr(10).join(file_list[:50])}  # Showing first 50 files
        {more_files_text}
        
        ARCHITECTURE DIAGRAM GENERATED:
        {mermaid_diagram}
        
        ACTUAL FILE CONTENTS (samples):
        {chr(10).join(code_snippets[:10])}  # Showing first 10 code files
        
        TASK: Analyze the PROVIDED repository data above and give:
        1. Detailed architecture summary based on the actual files shown
        2. Key components and their relationships (reference actual file names)
        3. Data flow patterns and API structure (from actual code)
        4. Integration points and dependencies (from actual files)
        5. Specific feature addition recommendations (exact file locations)
        
        Base your analysis ONLY on the files and code provided above.
        Do NOT mention accessing external repositories.
        """
        
        # Try each model until one works
        for model_info in self.models:
            try:
                print(f"Trying {model_info['name']} for analysis...")
                
                if model_info['type'] == 'gemini':
                    response = model_info['client'].generate_content(prompt)
                    return {
                        "architecture_summary": response.text,
                        "model_used": model_info['name']
                    }
                
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
                        "architecture_summary": response.choices[0].message.content,
                        "model_used": model_info['name']
                    }
                    
            except Exception as e:
                print(f"❌ {model_info['name']} failed: {e}")
                continue
        
        # All models failed, return mock response
        return self._mock_analysis(repo_data, mermaid_diagram)
    
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
                    response = model_info['client'].generate_content(prompt)
                    return {
                        "suggestions": response.text,
                        "model_used": model_info['name']
                    }
                
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
                    response = model_info['client'].generate_content(prompt)
                    result = response.text
                elif model_info['name'] in ['OpenAI GPT-4', 'OpenAI GPT-3.5']:
                    response = model_info['client'].chat.completions.create(
                        model=model_info['model_id'],
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=4000,
                        temperature=0.7
                    )
                    result = response.choices[0].message.content
                else:
                    continue
                
                # Cache the successful response
                self.cache.set(prompt, result, model_info['name'])
                print(f"✅ {model_info['name']} response generated and cached")
                return result
                
            except Exception as e:
                print(f"❌ {model_info['name']} failed: {e}")
                continue
        
        # If all models fail, return a fallback response
        fallback_response = self._generate_fallback_response(prompt)
        self.cache.set(prompt, fallback_response, "fallback")
        return fallback_response
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when all AI models fail"""
        if "visualization" in prompt.lower() or "add" in prompt.lower():
            return """Based on common software architecture patterns, here are some suggestions for adding visualizations:

## Common Locations for Visualizations:

1. **Frontend Components Directory**
   - `src/components/charts/` or `src/components/visualizations/`
   - Create reusable chart components (LineChart, BarChart, etc.)

2. **Dashboard/Analytics Section**
   - `src/pages/dashboard/` or `src/views/analytics/`
   - Dedicated pages for data visualization

3. **Shared UI Library**
   - `src/shared/components/` or `lib/components/`
   - If building a component library

## Recommended Tech Stack:
- **React**: Recharts, Chart.js, D3.js, or Victory
- **Vue**: Vue-ChartJS, D3.js
- **Angular**: Chart.js, D3.js, ng2-charts

## Files to Create/Modify:
1. Create chart component files
2. Add dependencies to package.json
3. Update routing (if new pages)
4. Add data fetching services
5. Update main layout to include new sections

*Note: For more specific recommendations, please analyze your actual codebase.*"""
        
        return """I apologize, but I'm currently unable to access the AI models to provide a detailed response. Please try again later, or consider:

1. Checking your internet connection
2. Verifying API keys are configured correctly
3. Trying a different question

For architectural questions, I recommend:
- Following established patterns in your existing codebase
- Consulting documentation for your framework/libraries
- Looking at similar projects for inspiration"""
    
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
