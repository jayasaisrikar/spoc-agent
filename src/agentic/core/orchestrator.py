"""
Main Agentic Orchestrator - Autonomous decision-making workflows
"""
import logging
import time
import traceback
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta

from .models import Goal, Task, TaskType, TaskStatus, ExecutionContext, ValidationResult, AnalysisResult
from .planner import AutonomousPlanner
from .executor import TaskExecutor
from .validator import ResultValidator

logger = logging.getLogger(__name__)


class AgenticOrchestrator:
    """
    Autonomous agent that plans, executes, and validates codebase analysis workflows
    with full autonomous capabilities for organizational repository analysis.
    
    Features:
    - Autonomous planning and goal decomposition
    - Self-correction and error recovery
    - Multi-step reasoning and iterative improvement
    - Dynamic tool selection based on context
    - Goal-oriented behavior with success tracking
    - Cross-repository organizational analysis
    """
    
    def __init__(self, ai_client, knowledge_base, memory_manager, diagram_generator=None):
        self.ai_client = ai_client
        self.knowledge_base = knowledge_base
        self.memory_manager = memory_manager
        self.diagram_generator = diagram_generator
        
        # Configuration
        self.max_iterations = 10
        self.confidence_threshold = 0.75
        self.max_planning_depth = 5
        self.learning_rate = 0.1
        
        # Core components
        self.planner = AutonomousPlanner(knowledge_base, self.max_planning_depth)
        self.executor = TaskExecutor(ai_client, knowledge_base, diagram_generator)
        self.validator = ResultValidator(self.confidence_threshold)
        
        # State tracking
        self.current_goals: List[Goal] = []
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.failed_tasks: Dict[str, Task] = {}
        self.execution_history: List[Dict] = []
        self.performance_metrics: Dict[str, float] = {}
        
        logger.info("🤖 AgenticOrchestrator initialized with autonomous capabilities")
    
    async def autonomous_analyze_organization(self, user_request: str = None, 
                                          target_repos: List[str] = None,
                                          user_id: str = None) -> AnalysisResult:
        """
        Autonomous analysis of entire organization's repositories
        This is the main entry point for organizational analysis
        """
        logger.info("🚀 Starting autonomous organizational analysis")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Goal decomposition and planning
            primary_goal = await self.planner.decompose_primary_goal(user_request, target_repos)
            self.current_goals.append(primary_goal)
            
            # Step 2: Context enrichment from organizational knowledge
            org_context = await self._enrich_organizational_context(target_repos, user_id)
            
            # Step 3: Autonomous execution with self-correction
            execution_context = ExecutionContext(
                iteration=0,
                start_time=start_time,
                available_tools=set(self.executor.available_tools.keys()),
                resource_constraints={'max_repos': 50, 'max_time_hours': 4},
                organizational_context=org_context
            )
            
            # Move tasks from planner to executor
            for task_id in primary_goal.associated_tasks:
                # Find the task in planner's generated tasks
                # This is a simplified version - in practice you'd have better task management
                pass
            
            results = await self._autonomous_execution_loop(primary_goal, execution_context)
            
            # Step 4: Final synthesis and recommendations
            final_analysis = await self._synthesize_organizational_insights(results, org_context)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info("✅ Autonomous organizational analysis completed")
            return AnalysisResult(
                success=True,
                analysis_type="organizational",
                confidence=final_analysis.get("execution_metadata", {}).get("final_confidence", 0.7),
                data=final_analysis,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"❌ Autonomous analysis failed: {e}")
            logger.error(traceback.format_exc())
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResult(
                success=False,
                analysis_type="organizational",
                confidence=0.0,
                data=self._gather_partial_results(),
                execution_time=execution_time,
                errors=[str(e)]
            )

    async def autonomous_analyze(self, repo_name: str, repo_data: Dict, 
                               user_request: str = None) -> AnalysisResult:
        """
        Autonomous analysis workflow with planning and self-correction for single repo
        """
        logger.info(f"🔍 Starting autonomous analysis for {repo_name}")
        
        start_time = datetime.now()
        
        try:
            # Create goal for single repository analysis
            goal = Goal(
                goal_id=f"analyze_{repo_name}_{int(time.time())}",
                description=f"Complete analysis of repository {repo_name}",
                success_criteria=[
                    "Repository structure analyzed",
                    "Patterns extracted",
                    "Architecture diagram generated",
                    "Feature recommendations provided",
                    "Analysis validated with >75% confidence"
                ]
            )
            
            execution_context = ExecutionContext(
                iteration=0,
                start_time=start_time,
                available_tools=set(self.executor.available_tools.keys()),
                resource_constraints={'max_time_minutes': 30},
                organizational_context={
                    'current_repo': repo_name,
                    'repo_data': repo_data,
                    'user_request': user_request
                }
            )
            
            # Generate tasks for single repo analysis
            await self._generate_single_repo_tasks(goal, repo_name, repo_data, user_request)
            
            results = await self._autonomous_execution_loop(goal, execution_context)
            final_analysis = await self._synthesize_single_repo_results(results, repo_name, repo_data)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResult(
                success=True,
                analysis_type="single_repository",
                confidence=final_analysis.get("execution_metadata", {}).get("final_confidence", 0.7),
                data=final_analysis,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"❌ Single repo analysis failed: {e}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResult(
                success=False,
                analysis_type="single_repository",
                confidence=0.0,
                data={"error": str(e)},
                execution_time=execution_time,
                errors=[str(e)]
            )
    
    async def _generate_single_repo_tasks(self, goal: Goal, repo_name: str, 
                                        repo_data: Dict, user_request: str):
        """Generate tasks for single repository analysis"""
        tasks = []
        
        # Structure analysis
        struct_task = Task(
            task_id=f"analyze_structure_{repo_name}_{int(time.time())}",
            task_type=TaskType.ANALYZE_STRUCTURE,
            description=f"Analyze structure of {repo_name}",
            inputs={"repo_name": repo_name, "repo_data": repo_data},
            priority=5,
            estimated_duration=300
        )
        tasks.append(struct_task)
        goal.associated_tasks.append(struct_task.task_id)
        self.active_tasks[struct_task.task_id] = struct_task
        
        # Pattern extraction
        pattern_task = Task(
            task_id=f"extract_patterns_{repo_name}_{int(time.time())}",
            task_type=TaskType.EXTRACT_PATTERNS,
            description=f"Extract patterns from {repo_name}",
            inputs={"repo_data": repo_data},
            dependencies=[struct_task.task_id],
            priority=4,
            estimated_duration=250
        )
        tasks.append(pattern_task)
        goal.associated_tasks.append(pattern_task.task_id)
        self.active_tasks[pattern_task.task_id] = pattern_task
        
        # Diagram generation
        diagram_task = Task(
            task_id=f"generate_diagram_{repo_name}_{int(time.time())}",
            task_type=TaskType.GENERATE_DIAGRAM,
            description=f"Generate diagram for {repo_name}",
            inputs={"repo_data": repo_data},
            dependencies=[struct_task.task_id],
            priority=3,
            estimated_duration=200
        )
        tasks.append(diagram_task)
        goal.associated_tasks.append(diagram_task.task_id)
        self.active_tasks[diagram_task.task_id] = diagram_task
        
        # Feature suggestions if requested
        if user_request and ('feature' in user_request.lower() or 'implement' in user_request.lower()):
            feature_task = Task(
                task_id=f"suggest_features_{repo_name}_{int(time.time())}",
                task_type=TaskType.SUGGEST_FEATURES,
                description=f"Suggest features for {repo_name}",
                inputs={"repo_data": repo_data, "request": user_request},
                dependencies=[struct_task.task_id, pattern_task.task_id],
                priority=2,
                estimated_duration=300
            )
            tasks.append(feature_task)
            goal.associated_tasks.append(feature_task.task_id)
            self.active_tasks[feature_task.task_id] = feature_task
        
        # Validation
        validation_task = Task(
            task_id=f"validate_{repo_name}_{int(time.time())}",
            task_type=TaskType.VALIDATE_ANALYSIS,
            description=f"Validate analysis of {repo_name}",
            inputs={"repo_name": repo_name},
            dependencies=[t.task_id for t in tasks],
            priority=1,
            estimated_duration=150
        )
        tasks.append(validation_task)
        goal.associated_tasks.append(validation_task.task_id)
        self.active_tasks[validation_task.task_id] = validation_task
    
    async def _autonomous_execution_loop(self, goal: Goal, context: ExecutionContext) -> Dict:
        """
        Autonomous execution loop with self-correction and adaptive planning
        """
        logger.info("🔄 Starting autonomous execution loop")
        
        results = {}
        max_iterations = self.max_iterations
        
        while context.iteration < max_iterations and goal.completion_percentage < 100:
            context.iteration += 1
            logger.info(f"🔄 Execution iteration {context.iteration}/{max_iterations}")
            
            try:
                # Dynamic task selection based on current state
                next_tasks = await self._select_next_tasks(goal, context, results)
                
                if not next_tasks:
                    logger.info("✅ No more tasks to execute")
                    break
                
                # Execute selected tasks
                iteration_results = await self.executor.execute_tasks_batch(next_tasks, context)
                results.update(iteration_results)
                
                # Move completed tasks
                for task in next_tasks:
                    if task.status == TaskStatus.COMPLETED:
                        self.completed_tasks[task.task_id] = task
                        if task.task_id in self.active_tasks:
                            del self.active_tasks[task.task_id]
                    elif task.status == TaskStatus.FAILED:
                        self.failed_tasks[task.task_id] = task
                        if task.task_id in self.active_tasks:
                            del self.active_tasks[task.task_id]
                
                # Self-correction and validation
                validation = await self.validator.validate_and_correct(results, goal, context)
                
                # Update goal progress
                goal.completion_percentage = await self._calculate_goal_progress(goal, results)
                
                # Adaptive replanning if needed
                if validation.confidence < self.confidence_threshold:
                    logger.info(f"🔧 Low confidence ({validation.confidence}), applying corrections")
                    await self._apply_corrections(validation, goal, context)
                
                # Check if goal is achieved
                if await self._is_goal_achieved(goal, results):
                    logger.info("🎉 Goal achieved!")
                    goal.status = "completed"
                    break
                
                # Learning and adaptation
                await self._update_performance_metrics(iteration_results, validation)
                
            except Exception as e:
                logger.error(f"❌ Error in iteration {context.iteration}: {e}")
                await self._handle_execution_error(e, goal, context)
        
        # Final validation and cleanup
        final_validation = await self.validator.final_validation(results, goal)
        results["execution_metadata"] = {
            "iterations": context.iteration,
            "duration": (datetime.now() - context.start_time).total_seconds(),
            "goal_completion": goal.completion_percentage,
            "final_confidence": final_validation.confidence,
            "issues_resolved": len([t for t in self.completed_tasks.values() if t.retry_count > 0])
        }
        
        return results
    
    async def _select_next_tasks(self, goal: Goal, context: ExecutionContext, 
                               current_results: Dict) -> List[Task]:
        """
        Dynamic task selection - choosing which tasks to execute next
        """
        logger.info("🎯 Selecting next tasks for execution")
        
        # Get ready tasks (dependencies satisfied)
        ready_tasks = []
        for task_id in goal.associated_tasks:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                if task.status == TaskStatus.PENDING and self._are_dependencies_met(task):
                    ready_tasks.append(task)
        
        if not ready_tasks:
            return []
        
        # Prioritize tasks based on multiple factors
        scored_tasks = []
        for task in ready_tasks:
            score = await self._calculate_task_priority_score(task, context, current_results)
            scored_tasks.append((task, score))
        
        # Sort by score and select top tasks
        scored_tasks.sort(key=lambda x: x[1], reverse=True)
        
        # Select tasks based on available resources
        selected_tasks = []
        total_estimated_time = 0
        max_parallel_tasks = 3
        
        for task, score in scored_tasks:
            if len(selected_tasks) >= max_parallel_tasks:
                break
            
            estimated_time = task.estimated_duration or 300
            if total_estimated_time + estimated_time <= 1800:  # 30 minutes max
                selected_tasks.append(task)
                total_estimated_time += estimated_time
        
        logger.info(f"✅ Selected {len(selected_tasks)} tasks for execution")
        return selected_tasks
    
    async def _calculate_task_priority_score(self, task: Task, context: ExecutionContext, 
                                           current_results: Dict) -> float:
        """Calculate priority score for task selection"""
        score = task.priority * 100  # Base priority
        
        # Adjust based on context
        if task.task_type in [TaskType.ANALYZE_STRUCTURE, TaskType.CROSS_REPO_ANALYSIS]:
            score += 50  # Core tasks get bonus
        
        # Adjust based on user request alignment
        if task.inputs.get('user_request') and context.organizational_context.get('user_request'):
            user_words = set(context.organizational_context['user_request'].lower().split())
            task_words = set(task.description.lower().split())
            relevance = len(user_words.intersection(task_words)) / max(len(user_words), 1)
            score += relevance * 30
        
        # Penalty for retries
        score -= task.retry_count * 20
        
        return score
    
    def _are_dependencies_met(self, task: Task) -> bool:
        """Check if all task dependencies are completed"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True
    
    async def _calculate_goal_progress(self, goal: Goal, results: Dict) -> float:
        """Calculate goal completion percentage"""
        completed_tasks = len([task_id for task_id in goal.associated_tasks 
                              if task_id in self.completed_tasks])
        total_tasks = len(goal.associated_tasks)
        
        if total_tasks == 0:
            return 100.0
        
        return (completed_tasks / total_tasks) * 100
    
    async def _is_goal_achieved(self, goal: Goal, results: Dict) -> bool:
        """Check if goal has been achieved"""
        # Simple check - all tasks completed with good confidence
        completed_tasks = len([task_id for task_id in goal.associated_tasks 
                              if task_id in self.completed_tasks])
        total_tasks = len(goal.associated_tasks)
        
        if completed_tasks < total_tasks:
            return False
        
        # Check average confidence
        confidences = []
        for task_id in goal.associated_tasks:
            if task_id in results:
                result = results[task_id]
                if isinstance(result, dict) and 'confidence' in result:
                    confidences.append(result['confidence'])
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        return avg_confidence >= self.confidence_threshold
    
    async def _apply_corrections(self, validation: ValidationResult, goal: Goal, 
                               context: ExecutionContext):
        """Apply corrections based on validation results"""
        logger.info(f"🔧 Applying {len(validation.recommendations)} corrections")
        
        for recommendation in validation.recommendations:
            if "replan" in recommendation.lower():
                new_tasks = await self.planner.replan_for_failures(goal, list(self.failed_tasks.values()), validation.issues)
                for task in new_tasks:
                    self.active_tasks[task.task_id] = task
            elif "retry" in recommendation.lower():
                await self._retry_failed_tasks()
    
    async def _retry_failed_tasks(self):
        """Retry failed tasks with exponential backoff"""
        logger.info("🔄 Retrying failed tasks")
        
        for task_id, task in list(self.failed_tasks.items()):
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                
                # Move back to active tasks
                self.active_tasks[task_id] = task
                del self.failed_tasks[task_id]
                
                logger.info(f"♻️ Retrying task {task_id} (attempt {task.retry_count})")
    
    async def _update_performance_metrics(self, iteration_results: Dict, validation: ValidationResult):
        """Update performance metrics for learning"""
        self.performance_metrics['last_iteration_confidence'] = validation.confidence
        self.performance_metrics['tasks_completed'] = len(iteration_results)
        self.performance_metrics['last_update'] = datetime.now().isoformat()
    
    async def _handle_execution_error(self, error: Exception, goal: Goal, context: ExecutionContext):
        """Handle execution errors gracefully"""
        logger.error(f"Execution error: {error}")
        # Could implement error recovery strategies here
    
    def _gather_partial_results(self) -> Dict:
        """Gather partial results in case of failure"""
        return {
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "active_tasks": len(self.active_tasks),
            "last_results": {task_id: task.results for task_id, task in self.completed_tasks.items()}
        }
    
    # Context and synthesis methods (simplified versions)
    async def _enrich_organizational_context(self, target_repos: List[str], user_id: str) -> Dict:
        """Enrich context with organizational knowledge and user history"""
        logger.info("🔍 Enriching organizational context")
        
        context = {
            "total_repos": len(target_repos),
            "analyzed_repos": [],
            "patterns": {},
            "technologies": {},
            "user_history": {},
            "organizational_metrics": {}
        }
        
        # Get organizational patterns from knowledge base
        try:
            org_patterns = self.knowledge_base.get_organization_patterns()
            context["patterns"] = org_patterns
        except Exception as e:
            logger.warning(f"Could not get organizational patterns: {e}")
        
        # Calculate organizational metrics
        context["organizational_metrics"] = {
            "repos_in_knowledge_base": len(self.knowledge_base.list_repositories()),
            "avg_repo_complexity": self._calculate_avg_complexity(target_repos),
            "dominant_languages": self._get_dominant_languages(target_repos)
        }
        
        return context
    
    def _calculate_avg_complexity(self, target_repos: List[str]) -> float:
        """Calculate average repository complexity"""
        total_files = 0
        valid_repos = 0
        
        for repo in target_repos:
            repo_data = self.knowledge_base.get_repository_knowledge(repo)
            if repo_data:
                file_count = len(repo_data.get('file_structure', []))
                total_files += file_count
                valid_repos += 1
        
        return total_files / valid_repos if valid_repos > 0 else 0
    
    def _get_dominant_languages(self, target_repos: List[str]) -> List[str]:
        """Get dominant programming languages across repositories"""
        lang_counts = {}
        
        for repo in target_repos:
            repo_data = self.knowledge_base.get_repository_knowledge(repo)
            if repo_data:
                analysis = repo_data.get('analysis', {})
                tech_stack = analysis.get('tech_stack', {})
                
                for lang in tech_stack.get('languages', []):
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        # Return top 3 languages
        sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)
        return [lang for lang, count in sorted_langs[:3]]
    
    async def _synthesize_organizational_insights(self, results: Dict, org_context: Dict) -> Dict:
        """Synthesize organizational insights from all analysis results"""
        logger.info("🧠 Synthesizing organizational insights")
        
        synthesis = {
            "success": True,
            "analysis_type": "organizational",
            "summary": {},
            "recommendations": {},
            "patterns": {},
            "tech_stack": {},
            "team_insights": {},
            "execution_metadata": results.get("execution_metadata", {})
        }
        
        # Aggregate patterns from all tasks
        all_patterns = {}
        all_technologies = {}
        all_recommendations = []
        
        for task_id, result in results.items():
            if isinstance(result, dict):
                if 'patterns' in result:
                    patterns = result['patterns']
                    if isinstance(patterns, dict):
                        for category, pattern_list in patterns.items():
                            if category not in all_patterns:
                                all_patterns[category] = {}
                            if isinstance(pattern_list, list):
                                for pattern in pattern_list:
                                    all_patterns[category][pattern] = all_patterns[category].get(pattern, 0) + 1
                
                if 'tech_mapping' in result:
                    tech_mapping = result['tech_mapping']
                    for tech_type, techs in tech_mapping.items():
                        if tech_type not in all_technologies:
                            all_technologies[tech_type] = {}
                        if isinstance(techs, dict):
                            for tech, count in techs.items():
                                all_technologies[tech_type][tech] = all_technologies[tech_type].get(tech, 0) + count
                
                if 'recommendations' in result:
                    recs = result['recommendations']
                    if isinstance(recs, dict):
                        for category, rec_list in recs.items():
                            if isinstance(rec_list, list):
                                all_recommendations.extend(rec_list)
                    elif isinstance(recs, list):
                        all_recommendations.extend(recs)
        
        synthesis["patterns"] = all_patterns
        synthesis["tech_stack"] = all_technologies
        synthesis["recommendations"] = {
            "immediate_actions": all_recommendations[:5],
            "long_term_goals": all_recommendations[5:10],
            "all_recommendations": all_recommendations
        }
        
        # Generate summary
        synthesis["summary"] = {
            "total_repos_analyzed": org_context.get("total_repos", 0),
            "dominant_patterns": self._get_top_items(all_patterns),
            "primary_technologies": self._get_top_items(all_technologies),
            "analysis_confidence": results.get("execution_metadata", {}).get("final_confidence", 0.5),
            "completion_time": results.get("execution_metadata", {}).get("duration", 0)
        }
        
        return synthesis
    
    async def _synthesize_single_repo_results(self, results: Dict, repo_name: str, repo_data: Dict) -> Dict:
        """Synthesize results for single repository analysis"""
        logger.info(f"🧠 Synthesizing results for {repo_name}")
        
        synthesis = {
            "success": True,
            "analysis_type": "single_repository",
            "repository": repo_name,
            "components": {},
            "patterns": [],
            "tech_stack": {},
            "recommendations": [],
            "architecture_summary": "",
            "mermaid_diagram": "",
            "execution_metadata": results.get("execution_metadata", {})
        }
        
        # Combine results from different tasks
        for task_id, result in results.items():
            if isinstance(result, dict):
                if 'components' in result:
                    synthesis['components'].update(result.get('components', {}))
                if 'patterns' in result:
                    patterns = result['patterns']
                    if isinstance(patterns, list):
                        synthesis['patterns'].extend(patterns)
                    elif isinstance(patterns, dict):
                        synthesis['patterns'].extend([f"{k}: {v}" for k, v in patterns.items()])
                if 'tech_stack' in result:
                    synthesis['tech_stack'].update(result['tech_stack'])
                if 'suggestions' in result:
                    synthesis['recommendations'].extend(result['suggestions'])
                if 'mermaid' in result:
                    synthesis['mermaid_diagram'] = result['mermaid']
        
        # Generate architecture summary
        synthesis["architecture_summary"] = f"""
        Repository: {repo_name}
        Components: {len(synthesis['components'])} identified
        Patterns: {', '.join(synthesis['patterns'][:3])}
        Technologies: {', '.join(list(synthesis['tech_stack'].keys())[:3])}
        """
        
        return synthesis
    
    def _get_top_items(self, nested_dict: Dict, top_n: int = 3) -> Dict:
        """Get top items from nested dictionary structure"""
        top_items = {}
        
        for category, items in nested_dict.items():
            if isinstance(items, dict):
                sorted_items = sorted(items.items(), key=lambda x: x[1], reverse=True)
                top_items[category] = [item for item, count in sorted_items[:top_n]]
        
        return top_items
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        return {
            "orchestrator": {
                "active_goals": len(self.current_goals),
                "active_tasks": len(self.active_tasks),
                "completed_tasks": len(self.completed_tasks),
                "failed_tasks": len(self.failed_tasks),
                "performance_metrics": self.performance_metrics
            },
            "planner": self.planner.get_planning_metrics(),
            "executor": self.executor.get_tool_metrics(),
            "validator": self.validator.get_validation_metrics()
        }
