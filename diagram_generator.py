from typing import Dict
from gitdiagram_core import GitDiagramCore


class DiagramGenerator:
    def __init__(self, ai_client=None):
        # Note: gitdiagram_path parameter removed as we now use local core
        self.gitdiagram_core = GitDiagramCore(ai_client)
    
    async def generate_mermaid_advanced(self, repo_data: Dict, instructions: str = "") -> Dict[str, str]:
        """
        Generate Mermaid diagram using GitDiagram's advanced three-stage process
        """
        return await self.gitdiagram_core.generate_diagram_three_stage(
            repo_data, instructions
        )
    
    async def generate_mermaid_async(self, repo_data: Dict) -> str:
        """
        Generate Mermaid.js diagram from repository data (async version)
        Falls back to simple generation if GitDiagram core fails
        """
        
        try:
            # Try using GitDiagram core for better diagrams
            result = await self.generate_mermaid_advanced(repo_data)
            
            if result.get('success'):
                return result['diagram']
            else:
                print(f"GitDiagram core failed: {result.get('error', 'Unknown error')}")
                return self._generate_simple_mermaid(repo_data)
                
        except Exception as e:
            print(f"Error with GitDiagram core: {e}")
            return self._generate_simple_mermaid(repo_data)
    
    def generate_mermaid(self, repo_data: Dict) -> str:
        """
        Generate Mermaid.js diagram from repository data (sync fallback)
        """
        # For sync calls, just use simple generation to avoid asyncio issues
        return self._generate_simple_mermaid(repo_data)
    
    def _generate_simple_mermaid(self, repo_data: Dict) -> str:
        """Generate a simple Mermaid diagram as fallback"""
        
        mermaid = "graph TD\n"
        
        # Group files by type
        files_by_type = {}
        for file_path, file_data in repo_data.items():
            file_type = file_data.get('type', 'unknown')
            if file_type not in files_by_type:
                files_by_type[file_type] = []
            files_by_type[file_type].append(file_path)
        
        # Create nodes for each file type
        type_nodes = {}
        for file_type, files in files_by_type.items():
            type_node = f"{file_type}_files"
            type_nodes[file_type] = type_node
            mermaid += f"    {type_node}[{file_type.upper()} Files]\n"
            
            # Add individual files (limit to 3 per type for readability)
            for i, file_path in enumerate(files[:3]):
                if len(file_path) > 30:
                    display_name = "..." + file_path[-27:]
                else:
                    display_name = file_path
                node_name = f"file_{i}_{file_type}".replace('-', '_').replace('.', '_')
                mermaid += f"    {node_name}[{display_name}]\n"
                mermaid += f"    {type_node} --> {node_name}\n"
        
        # Add connections between different file types
        types = list(type_nodes.keys())
        for i in range(len(types) - 1):
            mermaid += f"    {type_nodes[types[i]]} --> {type_nodes[types[i+1]]}\n"
        
        return mermaid
    
    def optimize_for_context(self, mermaid_code: str) -> str:
        """Optimize Mermaid code to reduce token usage"""
        lines = [line.strip() for line in mermaid_code.split('\n') if line.strip()]
        return '\n'.join(lines)
