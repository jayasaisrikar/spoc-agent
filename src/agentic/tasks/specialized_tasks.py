"""
Specialized task classes for different types of analysis tasks
"""
from typing import Dict, Any, List
from ..core.models import Task, TaskType


class StructureAnalysisTask(Task):
    """Specialized task for repository structure analysis"""
    
    def __init__(self, repo_name: str, repo_data: Dict, **kwargs):
        super().__init__(
            task_id=f"structure_analysis_{repo_name}",
            task_type=TaskType.ANALYZE_STRUCTURE,
            description=f"Analyze repository structure for {repo_name}",
            inputs={"repo_name": repo_name, "repo_data": repo_data},
            **kwargs
        )
        self.repo_name = repo_name
        
    def get_analysis_focus(self) -> List[str]:
        """Get specific focus areas for structure analysis"""
        return ["components", "layers", "dependencies", "entry_points"]


class PatternExtractionTask(Task):
    """Specialized task for pattern extraction"""
    
    def __init__(self, repo_data: Dict, focus_patterns: List[str] = None, **kwargs):
        super().__init__(
            task_id=f"pattern_extraction",
            task_type=TaskType.EXTRACT_PATTERNS,
            description="Extract architectural and design patterns",
            inputs={"repo_data": repo_data, "focus_patterns": focus_patterns or []},
            **kwargs
        )
        self.focus_patterns = focus_patterns or ["mvc", "microservices", "layered", "event-driven"]
        
    def get_pattern_categories(self) -> Dict[str, List[str]]:
        """Get pattern categories to analyze"""
        return {
            "architectural": ["mvc", "microservices", "layered", "hexagonal"],
            "design": ["singleton", "factory", "observer", "strategy"],
            "integration": ["rest", "graphql", "event-driven", "messaging"],
            "deployment": ["containerized", "serverless", "monolithic", "distributed"]
        }


class CrossRepoAnalysisTask(Task):
    """Specialized task for cross-repository analysis"""
    
    def __init__(self, target_repos: List[str], analysis_depth: str = "standard", **kwargs):
        super().__init__(
            task_id=f"cross_repo_analysis",
            task_type=TaskType.CROSS_REPO_ANALYSIS,
            description=f"Analyze patterns across {len(target_repos)} repositories",
            inputs={"repos": target_repos, "analysis_depth": analysis_depth},
            **kwargs
        )
        self.target_repos = target_repos
        self.analysis_depth = analysis_depth
        
    def get_comparison_dimensions(self) -> List[str]:
        """Get dimensions for cross-repo comparison"""
        return [
            "technology_stack",
            "architectural_patterns", 
            "code_organization",
            "dependency_management",
            "testing_strategies",
            "deployment_patterns"
        ]


class TechStackMappingTask(Task):
    """Specialized task for technology stack mapping"""
    
    def __init__(self, target_repos: List[str], include_versions: bool = False, **kwargs):
        super().__init__(
            task_id=f"tech_stack_mapping",
            task_type=TaskType.TECH_STACK_MAPPING,
            description="Map technology stack across organization",
            inputs={"repos": target_repos, "include_versions": include_versions},
            **kwargs
        )
        self.include_versions = include_versions
        
    def get_technology_categories(self) -> Dict[str, List[str]]:
        """Get technology categories to map"""
        return {
            "languages": ["python", "javascript", "java", "typescript", "go", "rust"],
            "frameworks": ["react", "vue", "angular", "spring", "django", "express"],
            "databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch"],
            "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
            "tools": ["webpack", "babel", "jest", "pytest", "gradle", "maven"]
        }


class TeamRecommendationTask(Task):
    """Specialized task for team recommendations"""
    
    def __init__(self, target_repos: List[str], team_context: Dict = None, **kwargs):
        super().__init__(
            task_id=f"team_recommendations",
            task_type=TaskType.TEAM_RECOMMENDATIONS,
            description="Generate team structure and development recommendations",
            inputs={"repos": target_repos, "team_context": team_context or {}},
            **kwargs
        )
        self.team_context = team_context or {}
        
    def get_recommendation_categories(self) -> List[str]:
        """Get categories for team recommendations"""
        return [
            "team_structure",
            "skill_requirements", 
            "development_practices",
            "code_ownership",
            "collaboration_patterns",
            "technical_debt_management"
        ]


class ValidationTask(Task):
    """Specialized task for result validation"""
    
    def __init__(self, validation_scope: str = "comprehensive", **kwargs):
        super().__init__(
            task_id=f"validation_{validation_scope}",
            task_type=TaskType.VALIDATE_ANALYSIS,
            description=f"Validate analysis results - {validation_scope}",
            inputs={"validation_scope": validation_scope},
            **kwargs
        )
        self.validation_scope = validation_scope
        
    def get_validation_checks(self) -> List[str]:
        """Get specific validation checks to perform"""
        return [
            "completeness",
            "consistency", 
            "accuracy",
            "relevance",
            "confidence_levels"
        ]


class FeatureSuggestionTask(Task):
    """Specialized task for feature suggestions"""
    
    def __init__(self, feature_request: str, repo_context: Dict, **kwargs):
        super().__init__(
            task_id=f"feature_suggestion",
            task_type=TaskType.SUGGEST_FEATURES,
            description=f"Suggest implementation for: {feature_request}",
            inputs={"feature_request": feature_request, "repo_context": repo_context},
            **kwargs
        )
        self.feature_request = feature_request
        
    def get_suggestion_aspects(self) -> List[str]:
        """Get aspects to consider for feature suggestions"""
        return [
            "file_placement",
            "code_structure",
            "dependencies",
            "integration_points",
            "testing_strategy",
            "documentation_needs"
        ]


class DiagramGenerationTask(Task):
    """Specialized task for diagram generation"""
    
    def __init__(self, repo_data: Dict, diagram_type: str = "architecture", **kwargs):
        super().__init__(
            task_id=f"diagram_generation_{diagram_type}",
            task_type=TaskType.GENERATE_DIAGRAM,
            description=f"Generate {diagram_type} diagram",
            inputs={"repo_data": repo_data, "diagram_type": diagram_type},
            **kwargs
        )
        self.diagram_type = diagram_type
        
    def get_diagram_elements(self) -> List[str]:
        """Get elements to include in diagram"""
        if self.diagram_type == "architecture":
            return ["components", "relationships", "data_flow", "external_services"]
        elif self.diagram_type == "database":
            return ["entities", "relationships", "constraints", "indexes"]
        elif self.diagram_type == "deployment":
            return ["services", "infrastructure", "network", "security"]
        else:
            return ["basic_structure", "main_components"]
