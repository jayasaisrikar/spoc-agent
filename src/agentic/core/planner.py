"""
Autonomous planner for breaking down complex tasks and creating execution plans
"""
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .models import Goal, Task, TaskType, ExecutionContext

logger = logging.getLogger(__name__)


class AutonomousPlanner:
    """
    Autonomous planner that breaks down complex organizational analysis tasks
    into manageable, executable sub-tasks with proper dependency management.
    """
    
    def __init__(self, knowledge_base, max_planning_depth: int = 5):
        self.knowledge_base = knowledge_base
        self.max_planning_depth = max_planning_depth
        self.planning_history: List[Dict] = []
        
    async def decompose_primary_goal(self, user_request: str, target_repos: List[str]) -> Goal:
        """
        Autonomous goal decomposition - breaking down complex organizational analysis tasks
        """
        logger.info("🎯 Decomposing primary goal")
        
        # Get all repositories if not specified
        if not target_repos:
            all_repos = self.knowledge_base.list_repositories()
            target_repos = [repo['name'] for repo in all_repos[:20]]  # Limit for performance
        
        primary_goal = Goal(
            goal_id=f"org_analysis_{int(time.time())}",
            description=f"Analyze organization's {len(target_repos)} repositories and provide insights",
            success_criteria=[
                "All target repositories analyzed",
                "Cross-repository patterns identified", 
                "Technology stack mapping completed",
                "Team recommendations generated",
                "Organizational insights synthesized"
            ],
            deadline=datetime.now() + timedelta(hours=2)
        )
        
        # Create sub-goals for different aspects
        sub_goals = await self._create_sub_goals(target_repos, user_request)
        primary_goal.sub_goals = sub_goals
        
        # Generate tasks for each sub-goal
        await self._generate_tasks_for_goals(primary_goal, target_repos, user_request)
        
        logger.info(f"✅ Goal decomposed into {len(sub_goals)} sub-goals with {len(primary_goal.associated_tasks)} tasks")
        return primary_goal
    
    async def _create_sub_goals(self, target_repos: List[str], user_request: str) -> List[Goal]:
        """Create sub-goals based on analysis requirements"""
        sub_goals = []
        
        # Individual repository analysis
        individual_goal = Goal(
            goal_id=f"individual_analysis_{int(time.time())}",
            description="Analyze individual repositories",
            success_criteria=[f"Repository {repo} analyzed" for repo in target_repos],
            priority=3
        )
        sub_goals.append(individual_goal)
        
        # Cross-repository analysis
        cross_repo_goal = Goal(
            goal_id=f"cross_repo_patterns_{int(time.time())}",
            description="Identify cross-repository patterns",
            success_criteria=["Architectural patterns mapped", "Common technologies identified"],
            priority=2
        )
        sub_goals.append(cross_repo_goal)
        
        # Organizational recommendations
        org_goal = Goal(
            goal_id=f"org_recommendations_{int(time.time())}",
            description="Generate organizational recommendations",
            success_criteria=["Team structure analyzed", "Development recommendations provided"],
            priority=1
        )
        sub_goals.append(org_goal)
        
        # User-specific goals
        if user_request:
            user_goals = await self._create_user_specific_goals(user_request, target_repos)
            sub_goals.extend(user_goals)
        
        return sub_goals
    
    async def _create_user_specific_goals(self, user_request: str, target_repos: List[str]) -> List[Goal]:
        """Create goals specific to user request"""
        goals = []
        
        if any(keyword in user_request.lower() for keyword in ['frontend', 'ui', 'react', 'vue', 'angular']):
            frontend_goal = Goal(
                goal_id=f"frontend_analysis_{int(time.time())}",
                description="Analyze frontend architecture and patterns",
                success_criteria=["Frontend frameworks identified", "UI patterns analyzed"],
                priority=2
            )
            goals.append(frontend_goal)
        
        if any(keyword in user_request.lower() for keyword in ['security', 'auth', 'authentication']):
            security_goal = Goal(
                goal_id=f"security_analysis_{int(time.time())}",
                description="Analyze security patterns and authentication",
                success_criteria=["Security patterns identified", "Authentication mechanisms analyzed"],
                priority=2
            )
            goals.append(security_goal)
        
        return goals
    
    async def _generate_tasks_for_goals(self, goal: Goal, target_repos: List[str], user_request: str):
        """Generate specific tasks to achieve the goals"""
        tasks = []
        
        # Individual repository analysis tasks
        for repo in target_repos:
            repo_data = self.knowledge_base.get_repository_knowledge(repo)
            if repo_data:
                task_id = f"analyze_{repo}_{int(time.time())}"
                tasks.append(Task(
                    task_id=task_id,
                    task_type=TaskType.ANALYZE_STRUCTURE,
                    description=f"Analyze structure of {repo}",
                    inputs={"repo_name": repo, "repo_data": repo_data},
                    priority=3,
                    estimated_duration=300  # 5 minutes
                ))
                goal.associated_tasks.append(task_id)
        
        # Cross-repository analysis tasks
        if len(tasks) > 1:  # Only if we have multiple repos
            cross_repo_task = Task(
                task_id=f"cross_repo_{int(time.time())}",
                task_type=TaskType.CROSS_REPO_ANALYSIS,
                description="Analyze patterns across repositories",
                inputs={"repos": target_repos},
                dependencies=[t.task_id for t in tasks],  # Depends on individual analysis
                priority=2,
                estimated_duration=600  # 10 minutes
            )
            tasks.append(cross_repo_task)
            goal.associated_tasks.append(cross_repo_task.task_id)
        
        # Technology mapping task
        tech_task = Task(
            task_id=f"tech_mapping_{int(time.time())}",
            task_type=TaskType.TECH_STACK_MAPPING,
            description="Map technology stack across organization",
            inputs={"repos": target_repos},
            dependencies=[t.task_id for t in tasks if t.task_type == TaskType.CROSS_REPO_ANALYSIS],
            priority=2,
            estimated_duration=400
        )
        tasks.append(tech_task)
        goal.associated_tasks.append(tech_task.task_id)
        
        # Team recommendations task
        team_task = Task(
            task_id=f"team_recommendations_{int(time.time())}",
            task_type=TaskType.TEAM_RECOMMENDATIONS,
            description="Generate team and development recommendations",
            inputs={"repos": target_repos, "user_request": user_request},
            dependencies=[tech_task.task_id],
            priority=1,
            estimated_duration=450
        )
        tasks.append(team_task)
        goal.associated_tasks.append(team_task.task_id)
        
        # Validation task
        validation_task = Task(
            task_id=f"validate_analysis_{int(time.time())}",
            task_type=TaskType.VALIDATE_ANALYSIS,
            description="Validate analysis results for consistency",
            inputs={"repos": target_repos},
            dependencies=[t.task_id for t in tasks if t.task_type != TaskType.VALIDATE_ANALYSIS],
            priority=1,
            estimated_duration=200
        )
        tasks.append(validation_task)
        goal.associated_tasks.append(validation_task.task_id)
        
        # Store planning decision
        self.planning_history.append({
            "timestamp": datetime.now().isoformat(),
            "goal_id": goal.goal_id,
            "tasks_generated": len(tasks),
            "total_estimated_time": sum(t.estimated_duration or 0 for t in tasks),
            "repositories": target_repos,
            "user_request": user_request
        })
        
        return tasks
    
    async def replan_for_failures(self, goal: Goal, failed_tasks: List[Task], 
                                issues: List[str]) -> List[Task]:
        """
        Create new tasks to address failures and issues
        """
        logger.info("📋 Replanning for failures")
        
        new_tasks = []
        
        for issue in issues:
            if "missing components" in issue:
                task_id = f"reanalyze_structure_{int(time.time())}"
                new_task = Task(
                    task_id=task_id,
                    task_type=TaskType.ANALYZE_STRUCTURE,
                    description="Re-analyze repository structure with focus on components",
                    inputs={"focus": "components", "detailed": True},
                    priority=5,  # High priority for corrections
                    estimated_duration=200
                )
                new_tasks.append(new_task)
                goal.associated_tasks.append(task_id)
            
            elif "missing patterns" in issue:
                task_id = f"reextract_patterns_{int(time.time())}"
                new_task = Task(
                    task_id=task_id,
                    task_type=TaskType.EXTRACT_PATTERNS,
                    description="Re-extract architectural patterns",
                    inputs={"deep_analysis": True},
                    priority=5,
                    estimated_duration=300
                )
                new_tasks.append(new_task)
                goal.associated_tasks.append(task_id)
            
            elif "cross-repo analysis" in issue:
                task_id = f"enhanced_cross_repo_{int(time.time())}"
                new_task = Task(
                    task_id=task_id,
                    task_type=TaskType.CROSS_REPO_ANALYSIS,
                    description="Enhanced cross-repository analysis",
                    inputs={"enhanced": True, "focus_areas": ["patterns", "technologies"]},
                    priority=4,
                    estimated_duration=450
                )
                new_tasks.append(new_task)
                goal.associated_tasks.append(task_id)
        
        logger.info(f"✅ Generated {len(new_tasks)} correction tasks")
        return new_tasks
    
    def get_planning_metrics(self) -> Dict[str, Any]:
        """Get metrics about planning performance"""
        if not self.planning_history:
            return {"total_plans": 0}
        
        total_plans = len(self.planning_history)
        avg_tasks_per_plan = sum(p["tasks_generated"] for p in self.planning_history) / total_plans
        avg_estimated_time = sum(p["total_estimated_time"] for p in self.planning_history) / total_plans
        
        return {
            "total_plans": total_plans,
            "avg_tasks_per_plan": avg_tasks_per_plan,
            "avg_estimated_time_minutes": avg_estimated_time / 60,
            "last_plan_timestamp": self.planning_history[-1]["timestamp"]
        }
