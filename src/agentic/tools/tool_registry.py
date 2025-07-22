"""
Tool registry for dynamic tool selection and management
"""
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
import inspect
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """Definition of a tool with metadata"""
    name: str
    function: Callable
    description: str
    inputs: List[str]
    outputs: List[str]
    task_types: List[str]  # Which task types this tool supports
    complexity: int  # 1-5 scale
    reliability: float  # 0.0-1.0 confidence score
    execution_time: int  # Estimated execution time in seconds


class ToolRegistry:
    """Registry for managing all available tools with dynamic selection"""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_performance: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()
        
    def register_tool(self, tool_def: ToolDefinition) -> None:
        """Register a new tool"""
        self.tools[tool_def.name] = tool_def
        self.tool_performance[tool_def.name] = {
            "success_rate": 0.8,  # Default success rate
            "avg_execution_time": tool_def.execution_time,
            "usage_count": 0,
            "last_used": None
        }
        logger.info(f"Registered tool: {tool_def.name}")
        
    def get_tools_for_task(self, task_type: str, complexity: int = None) -> List[ToolDefinition]:
        """Get available tools for a specific task type"""
        matching_tools = []
        
        for tool in self.tools.values():
            if task_type in tool.task_types:
                if complexity is None or tool.complexity <= complexity:
                    matching_tools.append(tool)
                    
        # Sort by reliability and performance
        matching_tools.sort(
            key=lambda t: (
                self.tool_performance[t.name]["success_rate"],
                -t.complexity,
                -self.tool_performance[t.name]["avg_execution_time"]
            ),
            reverse=True
        )
        
        return matching_tools
        
    def select_best_tool(self, task_type: str, context: Dict[str, Any] = None) -> Optional[ToolDefinition]:
        """Select the best tool for a task based on context and performance"""
        available_tools = self.get_tools_for_task(task_type)
        
        if not available_tools:
            return None
            
        # Simple selection for now - take the highest rated
        # TODO: Add more sophisticated selection logic based on context
        best_tool = available_tools[0]
        
        logger.info(f"Selected tool {best_tool.name} for task type {task_type}")
        return best_tool
        
    def update_tool_performance(self, tool_name: str, success: bool, execution_time: int) -> None:
        """Update tool performance metrics"""
        if tool_name not in self.tool_performance:
            return
            
        perf = self.tool_performance[tool_name]
        perf["usage_count"] += 1
        
        # Update success rate with exponential moving average
        alpha = 0.1
        current_rate = 1.0 if success else 0.0
        perf["success_rate"] = (1 - alpha) * perf["success_rate"] + alpha * current_rate
        
        # Update average execution time
        perf["avg_execution_time"] = (
            (perf["avg_execution_time"] * (perf["usage_count"] - 1) + execution_time) 
            / perf["usage_count"]
        )
        
        from datetime import datetime
        perf["last_used"] = datetime.now()
        
    def get_tool_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all tools"""
        return self.tool_performance.copy()
        
    def _register_default_tools(self) -> None:
        """Register default tools available in the system"""
        
        # Repository analysis tools
        self.register_tool(ToolDefinition(
            name="analyze_repository_structure",
            function=self._analyze_repo_structure,
            description="Analyze repository file structure and organization",
            inputs=["repo_data"],
            outputs=["structure_analysis"],
            task_types=["ANALYZE_STRUCTURE"],
            complexity=2,
            reliability=0.9,
            execution_time=30
        ))
        
        self.register_tool(ToolDefinition(
            name="extract_architectural_patterns",
            function=self._extract_patterns,
            description="Extract architectural patterns from code",
            inputs=["repo_data", "pattern_types"],
            outputs=["pattern_analysis"],
            task_types=["EXTRACT_PATTERNS"],
            complexity=4,
            reliability=0.8,
            execution_time=60
        ))
        
        self.register_tool(ToolDefinition(
            name="generate_architecture_diagram",
            function=self._generate_diagram,
            description="Generate Mermaid architecture diagrams",
            inputs=["structure_data", "diagram_type"],
            outputs=["mermaid_diagram"],
            task_types=["GENERATE_DIAGRAM"],
            complexity=3,
            reliability=0.85,
            execution_time=45
        ))
        
        self.register_tool(ToolDefinition(
            name="cross_repository_analysis",
            function=self._cross_repo_analysis,
            description="Compare patterns across multiple repositories",
            inputs=["repo_list", "comparison_metrics"],
            outputs=["comparison_results"],
            task_types=["CROSS_REPO_ANALYSIS"],
            complexity=5,
            reliability=0.75,
            execution_time=120
        ))
        
        self.register_tool(ToolDefinition(
            name="map_technology_stack",
            function=self._map_tech_stack,
            description="Map and analyze technology stacks",
            inputs=["repo_data", "include_versions"],
            outputs=["tech_stack_map"],
            task_types=["TECH_STACK_MAPPING"],
            complexity=3,
            reliability=0.9,
            execution_time=40
        ))
        
        self.register_tool(ToolDefinition(
            name="validate_analysis_results",
            function=self._validate_results,
            description="Validate and check consistency of analysis results",
            inputs=["analysis_results", "validation_criteria"],
            outputs=["validation_report"],
            task_types=["VALIDATE_ANALYSIS"],
            complexity=2,
            reliability=0.95,
            execution_time=20
        ))
        
        self.register_tool(ToolDefinition(
            name="generate_team_recommendations",
            function=self._generate_recommendations,
            description="Generate team structure and practice recommendations",
            inputs=["org_analysis", "team_context"],
            outputs=["recommendations"],
            task_types=["TEAM_RECOMMENDATIONS"],
            complexity=4,
            reliability=0.7,
            execution_time=90
        ))
        
        self.register_tool(ToolDefinition(
            name="suggest_feature_implementation",
            function=self._suggest_features,
            description="Suggest how to implement new features",
            inputs=["feature_request", "repo_context"],
            outputs=["implementation_suggestions"],
            task_types=["SUGGEST_FEATURES"],
            complexity=3,
            reliability=0.8,
            execution_time=50
        ))
        
    # Tool implementations (simplified - these would integrate with actual services)
    def _analyze_repo_structure(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze repository structure"""
        # This would integrate with the actual knowledge base
        return {"tool": "analyze_repository_structure", "data": repo_data}
        
    def _extract_patterns(self, repo_data: Dict[str, Any], pattern_types: List[str] = None) -> Dict[str, Any]:
        """Extract architectural patterns"""
        return {"tool": "extract_architectural_patterns", "data": repo_data, "patterns": pattern_types}
        
    def _generate_diagram(self, structure_data: Dict[str, Any], diagram_type: str = "architecture") -> Dict[str, Any]:
        """Generate architecture diagram"""
        return {"tool": "generate_architecture_diagram", "structure": structure_data, "type": diagram_type}
        
    def _cross_repo_analysis(self, repo_list: List[str], comparison_metrics: List[str]) -> Dict[str, Any]:
        """Perform cross-repository analysis"""
        return {"tool": "cross_repository_analysis", "repos": repo_list, "metrics": comparison_metrics}
        
    def _map_tech_stack(self, repo_data: Dict[str, Any], include_versions: bool = False) -> Dict[str, Any]:
        """Map technology stack"""
        return {"tool": "map_technology_stack", "data": repo_data, "versions": include_versions}
        
    def _validate_results(self, analysis_results: Dict[str, Any], validation_criteria: List[str]) -> Dict[str, Any]:
        """Validate analysis results"""
        return {"tool": "validate_analysis_results", "results": analysis_results, "criteria": validation_criteria}
        
    def _generate_recommendations(self, org_analysis: Dict[str, Any], team_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate team recommendations"""
        return {"tool": "generate_team_recommendations", "analysis": org_analysis, "context": team_context}
        
    def _suggest_features(self, feature_request: str, repo_context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest feature implementation"""
        return {"tool": "suggest_feature_implementation", "feature": feature_request, "context": repo_context}


class ToolSelectionStrategy:
    """Strategy for selecting tools based on different criteria"""
    
    @staticmethod
    def reliability_first(tools: List[ToolDefinition], tool_performance: Dict[str, Dict[str, Any]]) -> ToolDefinition:
        """Select tool with highest reliability"""
        return max(tools, key=lambda t: tool_performance[t.name]["success_rate"])
        
    @staticmethod
    def speed_first(tools: List[ToolDefinition], tool_performance: Dict[str, Dict[str, Any]]) -> ToolDefinition:
        """Select fastest tool"""
        return min(tools, key=lambda t: tool_performance[t.name]["avg_execution_time"])
        
    @staticmethod
    def balanced(tools: List[ToolDefinition], tool_performance: Dict[str, Dict[str, Any]]) -> ToolDefinition:
        """Select tool with best balance of speed and reliability"""
        def score(tool: ToolDefinition) -> float:
            perf = tool_performance[tool.name]
            # Normalize and combine metrics
            reliability_score = perf["success_rate"]
            # Invert execution time (lower is better)
            speed_score = 1.0 / (1.0 + perf["avg_execution_time"] / 60.0)
            return (reliability_score + speed_score) / 2.0
            
        return max(tools, key=score)


# Global tool registry instance
tool_registry = ToolRegistry()
