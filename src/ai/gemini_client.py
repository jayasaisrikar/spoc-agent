import google.generativeai as genai
from typing import Dict
import json


class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def analyze_repository(self, repo_data: Dict, mermaid_diagram: str) -> Dict:
        """Analyze repository with Gemini and build knowledge base"""
        
        prompt = f"""
        Analyze this repository structure and Mermaid diagram:
        
        Repository Data: {json.dumps(repo_data, indent=2)}
        
        Mermaid Diagram:
        {mermaid_diagram}
        
        Please provide:
        1. Architecture summary
        2. Key components and their relationships
        3. Data flow patterns
        4. Integration points
        5. Potential areas for feature additions
        
        Format as JSON for easy parsing.
        """
        
        response = self.model.generate_content(prompt)
        return self._parse_analysis(response.text)
    
    def suggest_feature_placement(self, feature_description: str, knowledge_base: Dict) -> Dict:
        """Suggest where to place a new feature"""
        
        prompt = f"""
        You are an expert software architect with COMPLETE ACCESS to the full codebase.
        
        IMPORTANT: You are NOT working with a "high-level description" - you have the COMPLETE source code below.
        
        COMPLETE CODEBASE KNOWLEDGE:
        {json.dumps(knowledge_base, indent=2)}
        
        TASK: I want to add this feature: {feature_description}
        
        Based on the COMPLETE codebase knowledge above (including full source code), please suggest:
        1. Exact file paths where code should be added
        2. Specific functions/classes to modify
        3. New files that need to be created
        4. Dependencies that need to be updated
        5. Integration points with existing code
        
        Be specific about repository, file, and line numbers where possible.
        Reference the actual code you see in the knowledge base above.
        
        Format the response as JSON with the following structure:
        {{
            "file_modifications": [
                {{"file": "path/to/file.py", "description": "what to modify"}}
            ],
            "new_files": [
                {{"path": "path/to/new_file.py", "purpose": "what this file does"}}
            ],
            "dependencies": ["list", "of", "new", "dependencies"]
        }}
        """
        
        response = self.model.generate_content(prompt)
        return self._parse_suggestions(response.text)
    
    def _parse_analysis(self, response_text: str) -> Dict:
        """Parse Gemini response into structured data"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            return {"raw_response": response_text}
    
    def _parse_suggestions(self, response_text: str) -> Dict:
        """Parse feature placement suggestions"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"raw_suggestions": response_text}
