"""
GitDiagram Core Engine - Extracted and adapted from GitDiagram backend
Implements the three-stage diagram generation process locally
"""
import re
import json
import os
from typing import Dict, List, Optional, AsyncGenerator
from gitdiagram_core_prompts import (
    SYSTEM_FIRST_PROMPT,
    SYSTEM_SECOND_PROMPT,
    SYSTEM_THIRD_PROMPT,
    ADDITIONAL_SYSTEM_INSTRUCTIONS_PROMPT
)


class GitDiagramCore:
    """
    Core GitDiagram functionality extracted for local use
    Implements the three-stage prompting system for diagram generation
    """
    
    def __init__(self, ai_client=None):
        """
        Initialize with an AI client (Gemini, OpenAI, etc.)
        If no client provided, will use mock responses for demo
        """
        self.ai_client = ai_client
        
    def format_user_message(self, data: Dict[str, str]) -> str:
        """
        Format data dictionary into structured message with XML tags
        Adapted from GitDiagram's format_message utility
        """
        parts = []
        for key, value in data.items():
            if key == "file_tree":
                parts.append(f"<file_tree>\n{value}\n</file_tree>")
            elif key == "readme":
                parts.append(f"<readme>\n{value}\n</readme>")
            elif key == "explanation":
                parts.append(f"<explanation>\n{value}\n</explanation>")
            elif key == "component_mapping":
                parts.append(f"<component_mapping>\n{value}\n</component_mapping>")
            elif key == "instructions":
                parts.append(f"<instructions>\n{value}\n</instructions>")
            elif key == "diagram":
                parts.append(f"<diagram>\n{value}\n</diagram>")
        
        return "\n\n".join(parts)
    
    def extract_file_tree_from_repo_data(self, repo_data: Dict) -> str:
        """
        Convert repository data structure to file tree string
        """
        if not repo_data:
            return ""
        
        file_tree_lines = []
        
        # Sort files for consistent output
        sorted_files = sorted(repo_data.keys())
        
        for file_path in sorted_files:
            file_info = repo_data[file_path]
            file_type = file_info.get('type', 'unknown')
            file_size = file_info.get('size', 0)
            
            # Create tree-like structure
            depth = file_path.count('/')
            indent = "  " * depth
            filename = os.path.basename(file_path)
            
            file_tree_lines.append(f"{indent}{filename} ({file_type}, {file_size} bytes)")
        
        return "\n".join(file_tree_lines)
    
    def extract_readme_content(self, repo_data: Dict) -> str:
        """
        Extract README content from repository data
        """
        readme_files = [
            'README.md', 'readme.md', 'README.txt', 'readme.txt',
            'README.rst', 'readme.rst', 'README', 'readme'
        ]
        
        for readme_name in readme_files:
            if readme_name in repo_data:
                return repo_data[readme_name].get('content', '')
            
            # Check for README in subdirectories
            for file_path in repo_data.keys():
                if os.path.basename(file_path) in readme_files:
                    return repo_data[file_path].get('content', '')
        
        return "No README file found in the repository."
    
    def process_click_events(self, diagram: str, repo_name: str = "repo") -> str:
        """
        Process click events in Mermaid diagram to include proper paths
        Adapted from GitDiagram's click event processing
        """
        def replace_path(match):
            # Extract the path from the click event
            node_name = match.group(1)
            path = match.group(2).strip('"')
            
            # For local use, we can keep the path as-is or modify as needed
            # In GitDiagram, this added GitHub URLs, but for local use we keep paths
            return f'click {node_name} "{path}"'
        
        # Pattern to match click events: click NodeName "path"
        click_pattern = r'click\s+(\w+)\s+"([^"]+)"'
        processed_diagram = re.sub(click_pattern, replace_path, diagram)
        
        return processed_diagram
    
    def extract_component_mapping(self, mapping_response: str) -> str:
        """
        Extract component mapping from AI response
        """
        start_tag = "<component_mapping>"
        end_tag = "</component_mapping>"
        
        start_idx = mapping_response.find(start_tag)
        end_idx = mapping_response.find(end_tag)
        
        if start_idx != -1 and end_idx != -1:
            return mapping_response[start_idx + len(start_tag):end_idx].strip()
        
        return mapping_response  # Return full response if tags not found
    
    def clean_mermaid_code(self, mermaid_code: str) -> str:
        """
        Clean up Mermaid code by removing markdown formatting
        """
        # Remove markdown code blocks
        mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "")
        
        # Remove any leading/trailing whitespace
        mermaid_code = mermaid_code.strip()
        
        return mermaid_code
    
    async def generate_diagram_three_stage(
        self, 
        repo_data: Dict, 
        instructions: str = "",
        repo_name: str = "repository"
    ) -> Dict[str, str]:
        """
        Generate diagram using the three-stage GitDiagram process
        
        Returns:
            Dict with 'explanation', 'mapping', 'diagram', and 'success' keys
        """
        try:
            # Prepare data
            file_tree = self.extract_file_tree_from_repo_data(repo_data)
            readme = self.extract_readme_content(repo_data)
            
            if not file_tree:
                return {
                    'success': False,
                    'error': 'No supported files found in repository'
                }
            
            # Stage 1: Generate explanation
            stage1_prompt = SYSTEM_FIRST_PROMPT
            if instructions:
                stage1_prompt += "\n" + ADDITIONAL_SYSTEM_INSTRUCTIONS_PROMPT
            
            stage1_data = {
                "file_tree": file_tree,
                "readme": readme
            }
            if instructions:
                stage1_data["instructions"] = instructions
            
            stage1_message = self.format_user_message(stage1_data)
            
            if self.ai_client:
                explanation = await self._call_ai_client(stage1_prompt, stage1_message)
            else:
                explanation = self._mock_explanation(repo_data, repo_name)
            
            if "BAD_INSTRUCTIONS" in explanation:
                return {
                    'success': False,
                    'error': 'Invalid or unclear instructions provided'
                }
            
            # Stage 2: Generate component mapping
            stage2_data = {
                "explanation": explanation,
                "file_tree": file_tree
            }
            stage2_message = self.format_user_message(stage2_data)
            
            if self.ai_client:
                mapping_response = await self._call_ai_client(SYSTEM_SECOND_PROMPT, stage2_message)
            else:
                mapping_response = self._mock_component_mapping(repo_data)
            
            component_mapping = self.extract_component_mapping(mapping_response)
            
            # Stage 3: Generate Mermaid diagram
            stage3_prompt = SYSTEM_THIRD_PROMPT
            if instructions:
                stage3_prompt += "\n" + ADDITIONAL_SYSTEM_INSTRUCTIONS_PROMPT
            
            stage3_data = {
                "explanation": explanation,
                "component_mapping": component_mapping
            }
            if instructions:
                stage3_data["instructions"] = instructions
            
            stage3_message = self.format_user_message(stage3_data)
            
            if self.ai_client:
                diagram_response = await self._call_ai_client(stage3_prompt, stage3_message)
            else:
                diagram_response = self._mock_mermaid_diagram(repo_data)
            
            if "BAD_INSTRUCTIONS" in diagram_response:
                return {
                    'success': False,
                    'error': 'Invalid or unclear instructions provided'
                }
            
            # Clean and process diagram
            mermaid_code = self.clean_mermaid_code(diagram_response)
            processed_diagram = self.process_click_events(mermaid_code, repo_name)
            
            return {
                'success': True,
                'explanation': explanation,
                'mapping': component_mapping,
                'diagram': processed_diagram
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating diagram: {str(e)}"
            }
    
    async def _call_ai_client(self, system_prompt: str, user_message: str) -> str:
        """
        Call the AI client with system prompt and user message
        Adapt this method based on your AI client interface
        """
        if hasattr(self.ai_client, 'generate_content'):
            # Gemini-style client
            full_prompt = f"{system_prompt}\n\nUser: {user_message}"
            response = self.ai_client.generate_content(full_prompt)
            return response.text
        else:
            # Generic client - adapt as needed
            return await self.ai_client.complete(system_prompt, user_message)
    
    def _mock_explanation(self, repo_data: Dict, repo_name: str) -> str:
        """
        Generate mock explanation for demo purposes
        """
        file_types = set(data.get('type') for data in repo_data.values())
        file_count = len(repo_data)
        
        return f"""
        <explanation>
        This {repo_name} appears to be a software project with {file_count} files across {len(file_types)} different programming languages/file types.

        Based on the file structure, this project follows a modular architecture with the following key components:

        1. Core Application Logic: The main application files that handle primary functionality
        2. Configuration Management: Files that manage application settings and environment variables  
        3. Utility Functions: Helper functions and shared utilities used across the application
        4. Data Layer: Files responsible for data handling, models, and persistence
        5. External Interfaces: API endpoints, user interfaces, or external service integrations

        The architecture appears to follow separation of concerns principles, with distinct files for different responsibilities. The project structure suggests a well-organized codebase suitable for collaborative development.

        For the system design diagram, we should represent:
        - Each major component as a distinct node
        - Data flow between components with directional arrows
        - External dependencies and interfaces
        - Configuration and utility components as supporting elements
        </explanation>
        """
    
    def _mock_component_mapping(self, repo_data: Dict) -> str:
        """
        Generate mock component mapping for demo purposes
        """
        components = []
        
        # Map common file patterns to components
        for file_path, file_data in repo_data.items():
            basename = os.path.basename(file_path)
            file_type = file_data.get('type', '')
            
            if 'main' in basename.lower() or 'app' in basename.lower():
                components.append(f"Main Application: {file_path}")
            elif 'config' in basename.lower():
                components.append(f"Configuration: {file_path}")
            elif 'model' in basename.lower():
                components.append(f"Data Models: {file_path}")
            elif 'util' in basename.lower() or 'helper' in basename.lower():
                components.append(f"Utilities: {file_path}")
            elif file_type in ['py', 'js', 'ts'] and len(components) < 8:
                components.append(f"Core Module: {file_path}")
        
        mapping = "\n".join(f"{i+1}. {comp}" for i, comp in enumerate(components[:10]))
        
        return f"""
        <component_mapping>
        {mapping}
        </component_mapping>
        """
    
    def _mock_mermaid_diagram(self, repo_data: Dict) -> str:
        """
        Generate mock Mermaid diagram for demo purposes
        """
        files = list(repo_data.keys())
        
        diagram = "graph TD\n"
        
        # Create nodes for different file types
        file_groups = {}
        for file_path in files:
            file_type = repo_data[file_path].get('type', 'other')
            if file_type not in file_groups:
                file_groups[file_type] = []
            file_groups[file_type].append(file_path)
        
        # Generate diagram nodes
        node_counter = 1
        for file_type, file_list in file_groups.items():
            group_node = f"group_{file_type}"
            diagram += f"    {group_node}[{file_type.upper()} Files]\n"
            
            # Add individual files (limit to 2 per group for readability)
            for i, file_path in enumerate(file_list[:2]):
                file_node = f"file_{node_counter}"
                filename = os.path.basename(file_path)
                diagram += f"    {file_node}[{filename}]\n"
                diagram += f"    {group_node} --> {file_node}\n"
                diagram += f'    click {file_node} "{file_path}"\n'
                node_counter += 1
        
        # Add some connections between groups
        group_names = list(file_groups.keys())
        for i in range(len(group_names) - 1):
            diagram += f"    group_{group_names[i]} --> group_{group_names[i+1]}\n"
        
        return diagram
