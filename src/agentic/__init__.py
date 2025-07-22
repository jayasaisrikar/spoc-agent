"""
Agentic Orchestrator Package

This package implements autonomous decision-making workflows for organizational 
repository analysis with full autonomous capabilities:
- Autonomous planning (breaking down complex tasks)
- Self-correction (detecting and fixing errors)
- Multi-step reasoning (iterative problem solving)
- Dynamic tool selection (choosing which tools to use when)
- Goal-oriented behavior (working towards objectives autonomously)
"""

from .core.orchestrator import AgenticOrchestrator
from .core.models import Task, Goal, TaskType, ValidationResult, ExecutionContext
from .core.planner import AutonomousPlanner
from .core.executor import TaskExecutor
from .core.validator import ResultValidator

__version__ = "1.0.0"
__author__ = "AI Code Architecture Agent"

__all__ = [
    "AgenticOrchestrator",
    "Task",
    "Goal", 
    "TaskType",
    "ValidationResult",
    "ExecutionContext",
    "AutonomousPlanner",
    "TaskExecutor",
    "ResultValidator"
]
