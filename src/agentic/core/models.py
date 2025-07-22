"""
Core data models for the agentic orchestrator system
"""
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class TaskType(Enum):
    # Core Analysis Tasks
    ANALYZE_STRUCTURE = "analyze_structure"
    EXTRACT_PATTERNS = "extract_patterns"
    VALIDATE_ANALYSIS = "validate_analysis"
    SUGGEST_FEATURES = "suggest_features"
    GENERATE_DIAGRAM = "generate_diagram"
    REFINE_RESULTS = "refine_results"
    
    # Organizational Tasks
    CROSS_REPO_ANALYSIS = "cross_repo_analysis"
    TECH_STACK_MAPPING = "tech_stack_mapping"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    TEAM_RECOMMENDATIONS = "team_recommendations"
    
    # Autonomous Tasks
    GOAL_DECOMPOSITION = "goal_decomposition"
    PLAN_VALIDATION = "plan_validation"
    SELF_CORRECTION = "self_correction"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"
    CONTEXT_ENRICHMENT = "context_enrichment"


class ConfidenceLevel(Enum):
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.9


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class ValidationResult:
    is_valid: bool
    confidence: float
    issues: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    iteration: int
    start_time: datetime
    available_tools: Set[str]
    resource_constraints: Dict[str, Any]
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    organizational_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    task_id: str
    task_type: TaskType
    description: str
    inputs: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    completed: bool = False
    results: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 1  # 1-10, higher is more important
    estimated_duration: Optional[int] = None  # in seconds
    actual_duration: Optional[int] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    error_history: List[str] = field(default_factory=list)


@dataclass
class Goal:
    goal_id: str
    description: str
    success_criteria: List[str]
    deadline: Optional[datetime] = None
    priority: int = 1
    sub_goals: List['Goal'] = field(default_factory=list)
    associated_tasks: List[str] = field(default_factory=list)
    completion_percentage: float = 0.0
    status: str = "active"  # active, completed, failed, paused
    context: Dict[str, Any] = field(default_factory=dict)  # Add context field


@dataclass
class ToolConfig:
    name: str
    confidence: float
    speed: float
    domains: List[str]
    availability: bool = True
    last_used: Optional[datetime] = None
    success_rate: float = 0.8
    avg_execution_time: float = 300.0  # seconds


@dataclass
class OrganizationalMetrics:
    total_repositories: int
    analyzed_repositories: int
    dominant_languages: List[str]
    common_patterns: Dict[str, int]
    team_size_estimate: Optional[int] = None
    complexity_score: float = 0.0
    technical_debt_indicators: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    success: bool
    analysis_type: str
    confidence: float
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
