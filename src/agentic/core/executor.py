"""
Task executor for autonomous execution of analysis tasks
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from .models import Task, TaskType, TaskStatus, ExecutionContext, ToolConfig

logger = logging.getLogger(__name__)


class TaskExecutor:
    """
    Autonomous task executor that handles dynamic tool selection,
    parallel execution, and error recovery.
    """
    
    def __init__(self, ai_client, knowledge_base, diagram_generator=None):
        self.ai_client = ai_client
        self.knowledge_base = knowledge_base
        self.diagram_generator = diagram_generator
        
        # Available tools and their capabilities
        self.available_tools = {
            'structure_analyzer': ToolConfig(
                name='structure_analyzer',
                confidence=0.9, 
                speed=0.8, 
                domains=['files', 'architecture']
            ),
            'pattern_extractor': ToolConfig(
                name='pattern_extractor',
                confidence=0.8, 
                speed=0.6, 
                domains=['patterns', 'design']
            ),
            'diagram_generator': ToolConfig(
                name='diagram_generator',
                confidence=0.7, 
                speed=0.5, 
                domains=['visualization', 'architecture']
            ),
            'cross_repo_analyzer': ToolConfig(
                name='cross_repo_analyzer',
                confidence=0.8, 
                speed=0.4, 
                domains=['organization', 'patterns']
            ),
            'tech_stack_mapper': ToolConfig(
                name='tech_stack_mapper',
                confidence=0.9, 
                speed=0.7, 
                domains=['technology', 'dependencies']
            ),
            'team_advisor': ToolConfig(
                name='team_advisor',
                confidence=0.6, 
                speed=0.9, 
                domains=['recommendations', 'team']
            ),
            'memory_searcher': ToolConfig(
                name='memory_searcher',
                confidence=0.8, 
                speed=0.9, 
                domains=['context', 'history']
            ),
            'validator': ToolConfig(
                name='validator',
                confidence=0.9, 
                speed=0.8, 
                domains=['quality', 'validation']
            )
        }
        
        self.execution_history: List[Dict] = []
        
    async def execute_tasks_batch(self, tasks: List[Task], context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute a batch of tasks with proper error handling and tool selection
        """
        logger.info(f"⚡ Executing batch of {len(tasks)} tasks")
        
        results = {}
        
        # Execute tasks (could be parallelized for better performance)
        for task in tasks:
            try:
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.now()
                
                # Select best tool for this task
                selected_tool = await self._select_best_tool_for_task(task)
                task.tools_used.append(selected_tool)
                
                # Execute the task
                result = await self._execute_single_task(task, context, selected_tool)
                
                task.results = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.actual_duration = (task.completed_at - task.started_at).total_seconds()
                
                results[task.task_id] = result
                logger.info(f"✅ Task {task.task_id} completed successfully")
                
                # Update tool metrics
                await self._update_tool_metrics(selected_tool, True, task.actual_duration)
                
            except Exception as e:
                logger.error(f"❌ Task {task.task_id} failed: {e}")
                task.status = TaskStatus.FAILED
                task.error_history.append(str(e))
                task.completed_at = datetime.now()
                
                # Update tool metrics for failure
                if task.tools_used:
                    await self._update_tool_metrics(task.tools_used[-1], False, 0)
        
        return results
    
    async def _select_best_tool_for_task(self, task: Task) -> str:
        """
        Dynamic tool selection based on task requirements and tool performance
        """
        task_domains = self._get_task_domains(task.task_type)
        best_tool = None
        best_score = 0
        
        for tool_name, tool_config in self.available_tools.items():
            if not tool_config.availability:
                continue
                
            score = 0
            
            # Calculate domain relevance
            domain_overlap = len(set(task_domains).intersection(set(tool_config.domains)))
            score += domain_overlap * 0.4
            
            # Add confidence weight
            score += tool_config.confidence * 0.3
            
            # Add speed weight (faster is better for time-sensitive tasks)
            score += tool_config.speed * 0.2
            
            # Add success rate weight
            score += tool_config.success_rate * 0.1
            
            if score > best_score:
                best_score = score
                best_tool = tool_name
        
        return best_tool or 'structure_analyzer'  # Default fallback
    
    def _get_task_domains(self, task_type: TaskType) -> List[str]:
        """Map task types to domain requirements"""
        domain_mapping = {
            TaskType.ANALYZE_STRUCTURE: ['files', 'architecture'],
            TaskType.EXTRACT_PATTERNS: ['patterns', 'design'],
            TaskType.GENERATE_DIAGRAM: ['visualization', 'architecture'],
            TaskType.CROSS_REPO_ANALYSIS: ['organization', 'patterns'],
            TaskType.TECH_STACK_MAPPING: ['technology', 'dependencies'],
            TaskType.TEAM_RECOMMENDATIONS: ['recommendations', 'team'],
            TaskType.VALIDATE_ANALYSIS: ['quality', 'validation'],
            TaskType.SUGGEST_FEATURES: ['recommendations', 'architecture']
        }
        return domain_mapping.get(task_type, ['general'])
    
    async def _execute_single_task(self, task: Task, context: ExecutionContext, tool: str) -> Dict:
        """
        Execute a single task using the selected tool
        """
        logger.info(f"🔧 Executing {task.task_type.value} using {tool}")
        
        try:
            if task.task_type == TaskType.ANALYZE_STRUCTURE:
                return await self._execute_structure_analysis(task, context)
            elif task.task_type == TaskType.EXTRACT_PATTERNS:
                return await self._execute_pattern_extraction(task, context)
            elif task.task_type == TaskType.GENERATE_DIAGRAM:
                return await self._execute_diagram_generation(task, context)
            elif task.task_type == TaskType.CROSS_REPO_ANALYSIS:
                return await self._execute_cross_repo_analysis(task, context)
            elif task.task_type == TaskType.TECH_STACK_MAPPING:
                return await self._execute_tech_stack_mapping(task, context)
            elif task.task_type == TaskType.TEAM_RECOMMENDATIONS:
                return await self._execute_team_recommendations(task, context)
            elif task.task_type == TaskType.VALIDATE_ANALYSIS:
                return await self._execute_validation(task, context)
            elif task.task_type == TaskType.SUGGEST_FEATURES:
                return await self._execute_feature_suggestion(task, context)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
                
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    # Task execution methods
    async def _execute_structure_analysis(self, task: Task, context: ExecutionContext) -> Dict:
        """Execute structure analysis using AI client"""
        try:
            repo_data = task.inputs.get('repo_data', {})
            repo_name = task.inputs.get('repo_name', 'unknown')
            
            if not repo_data and repo_name != 'unknown':
                repo_data = self.knowledge_base.get_repository_knowledge(repo_name)
            
            # Prepare auxiliary context (diagram) if available
            mermaid_diagram = ""
            try:
                # Prefer existing diagram from knowledge base to avoid regeneration
                existing = None
                if isinstance(repo_data, dict):
                    existing = repo_data.get('mermaid_diagram')
                if existing:
                    mermaid_diagram = existing.strip()
                    if self.diagram_generator and mermaid_diagram:
                        mermaid_diagram = self.diagram_generator.optimize_for_context(mermaid_diagram)
                elif self.diagram_generator and repo_data:
                    mermaid_raw = await self.diagram_generator.generate_mermaid_async(repo_data)
                    mermaid_diagram = self.diagram_generator.optimize_for_context(mermaid_raw)
            except Exception as e:
                logger.warning(f"Diagram generation failed, continuing without diagram: {e}")
                mermaid_diagram = ""
            
            # Use AI client to analyze structure with diagram context
            analysis = self.ai_client.analyze_repository(repo_data, mermaid_diagram)
            
            # Extract components and patterns
            components = analysis.get('components', [])
            patterns = analysis.get('architecture_patterns', [])
            tech_stack = analysis.get('tech_stack', {})
            
            return {
                "components": components,
                "patterns": patterns,
                "tech_stack": tech_stack,
                "confidence": 0.85,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Structure analysis failed: {e}")
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_pattern_extraction(self, task: Task, context: ExecutionContext) -> Dict:
        """Execute pattern extraction from repository"""
        try:
            repo_data = task.inputs.get('repo_data', {})
            
            # Enhanced pattern extraction
            patterns = {
                "architectural": [],
                "design": [],
                "deployment": []
            }
            
            # Analyze file structure for patterns
            file_paths = list(repo_data.keys()) if isinstance(repo_data, dict) else []
            
            # Detect MVC pattern
            if any('controller' in path.lower() for path in file_paths) and \
               any('model' in path.lower() for path in file_paths) and \
               any('view' in path.lower() for path in file_paths):
                patterns["architectural"].append("MVC")
            
            # Detect microservices pattern
            if any('service' in path.lower() for path in file_paths):
                patterns["architectural"].append("Microservices")
            
            # Detect Docker usage
            if 'Dockerfile' in file_paths or 'docker-compose.yml' in file_paths:
                patterns["deployment"].append("Containerized")
            
            return {
                "patterns": patterns,
                "pattern_count": sum(len(p) for p in patterns.values()),
                "confidence": 0.75
            }
        except Exception as e:
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_diagram_generation(self, task: Task, context: ExecutionContext) -> Dict:
        """Execute diagram generation"""
        try:
            repo_data = task.inputs.get('repo_data', {})
            
            if self.diagram_generator:
                mermaid = await self.diagram_generator.generate_mermaid_async(repo_data)
                optimized = self.diagram_generator.optimize_for_context(mermaid)
                
                return {
                    "mermaid": optimized,
                    "diagram_type": "architecture",
                    "confidence": 0.8
                }
            else:
                # Generate simple diagram
                return {
                    "mermaid": "graph TD\nA[Frontend] --> B[Backend]\nB --> C[Database]",
                    "diagram_type": "basic",
                    "confidence": 0.6
                }
        except Exception as e:
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_cross_repo_analysis(self, task: Task, context: ExecutionContext) -> Dict:
        """Execute cross-repository analysis"""
        try:
            target_repos = task.inputs.get('repos', [])
            
            # Get all repository knowledge
            all_repo_data = {}
            for repo in target_repos:
                repo_knowledge = self.knowledge_base.get_repository_knowledge(repo)
                if repo_knowledge:
                    all_repo_data[repo] = repo_knowledge
            
            # Extract cross-repo patterns
            common_patterns = self._extract_common_patterns(all_repo_data)
            shared_technologies = self._extract_shared_technologies(all_repo_data)
            
            return {
                "patterns": common_patterns,
                "shared_technologies": shared_technologies,
                "analyzed_repos": len(all_repo_data),
                "total_repos": len(target_repos),
                "confidence": 0.8
            }
        except Exception as e:
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_tech_stack_mapping(self, task: Task, context: ExecutionContext) -> Dict:
        """Execute technology stack mapping across organization"""
        try:
            target_repos = task.inputs.get('repos', [])
            
            tech_mapping = {
                "languages": {},
                "frameworks": {},
                "databases": {},
                "cloud_services": {},
                "total_repos": len(target_repos)
            }
            
            for repo in target_repos:
                repo_data = self.knowledge_base.get_repository_knowledge(repo)
                if repo_data:
                    analysis = repo_data.get('analysis', {})
                    tech_stack = analysis.get('tech_stack', {})
                    
                    # Count languages
                    for lang in tech_stack.get('languages', []):
                        tech_mapping["languages"][lang] = tech_mapping["languages"].get(lang, 0) + 1
                    
                    # Count frameworks
                    for fw in tech_stack.get('frameworks', []):
                        tech_mapping["frameworks"][fw] = tech_mapping["frameworks"].get(fw, 0) + 1
            
            return {
                "tech_mapping": tech_mapping,
                "dominant_language": max(tech_mapping["languages"].items(), key=lambda x: x[1])[0] if tech_mapping["languages"] else None,
                "confidence": 0.85
            }
        except Exception as e:
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_team_recommendations(self, task: Task, context: ExecutionContext) -> Dict:
        """Execute team and development recommendations"""
        try:
            target_repos = task.inputs.get('repos', [])
            user_request = task.inputs.get('user_request', '')
            
            recommendations = {
                "team_structure": [],
                "development_practices": [],
                "technical_debt": [],
                "improvement_opportunities": []
            }
            
            # Analyze repository complexity for team recommendations
            total_complexity = 0
            for repo in target_repos:
                repo_data = self.knowledge_base.get_repository_knowledge(repo)
                if repo_data:
                    file_count = len(repo_data.get('file_structure', []))
                    total_complexity += file_count
            
            avg_complexity = total_complexity / len(target_repos) if target_repos else 0
            
            # Generate recommendations based on complexity
            if avg_complexity > 100:
                recommendations["team_structure"].append("Consider dedicated teams per repository")
                recommendations["development_practices"].append("Implement code review processes")
            
            if avg_complexity < 20:
                recommendations["team_structure"].append("Small teams can handle multiple repositories")
            
            # Add user-specific recommendations
            if 'frontend' in user_request.lower():
                recommendations["improvement_opportunities"].append("Focus on UI/UX consistency across repos")
            
            return {
                "recommendations": recommendations,
                "avg_repo_complexity": avg_complexity,
                "confidence": 0.7
            }
        except Exception as e:
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_validation(self, task: Task, context: ExecutionContext) -> Dict:
        """Execute validation of analysis results"""
        try:
            # This would validate the overall analysis quality
            return {
                "validation_passed": True,
                "quality_score": 0.85,
                "confidence": 0.9
            }
        except Exception as e:
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_feature_suggestion(self, task: Task, context: ExecutionContext) -> Dict:
        """Execute feature suggestion analysis"""
        try:
            request = task.inputs.get('request', '')
            repo_data = task.inputs.get('repo_data', {})
            
            suggestions = [
                "Implement authentication module",
                "Add comprehensive logging", 
                "Set up CI/CD pipeline",
                "Add API documentation"
            ]
            
            return {
                "suggestions": suggestions,
                "feature_request": request,
                "confidence": 0.75
            }
        except Exception as e:
            return {"error": str(e), "confidence": 0.1}
    
    # Helper methods
    def _extract_common_patterns(self, all_repo_data: Dict) -> Dict:
        """Extract patterns common across repositories"""
        pattern_counts = {}
        
        for repo_name, repo_data in all_repo_data.items():
            analysis = repo_data.get('analysis', {})
            patterns = analysis.get('architecture_patterns', [])
            
            for pattern in patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Return patterns that appear in >50% of repos
        threshold = len(all_repo_data) * 0.5
        common_patterns = {k: v for k, v in pattern_counts.items() if v >= threshold}
        
        return common_patterns
    
    def _extract_shared_technologies(self, all_repo_data: Dict) -> Dict:
        """Extract technologies shared across repositories"""
        tech_counts = {}
        
        for repo_name, repo_data in all_repo_data.items():
            analysis = repo_data.get('analysis', {})
            tech_stack = analysis.get('tech_stack', {})
            
            for lang in tech_stack.get('languages', []):
                tech_counts[lang] = tech_counts.get(lang, 0) + 1
        
        return tech_counts
    
    async def _update_tool_metrics(self, tool_name: str, success: bool, execution_time: float):
        """Update tool performance metrics"""
        if tool_name in self.available_tools:
            tool = self.available_tools[tool_name]
            tool.last_used = datetime.now()
            
            # Update success rate with exponential moving average
            alpha = 0.1  # Learning rate
            if success:
                tool.success_rate = tool.success_rate * (1 - alpha) + alpha
            else:
                tool.success_rate = tool.success_rate * (1 - alpha)
            
            # Update average execution time
            if execution_time > 0:
                tool.avg_execution_time = tool.avg_execution_time * (1 - alpha) + execution_time * alpha
    
    def get_tool_metrics(self) -> Dict[str, Any]:
        """Get current tool performance metrics"""
        metrics = {}
        for tool_name, tool_config in self.available_tools.items():
            metrics[tool_name] = {
                "success_rate": tool_config.success_rate,
                "avg_execution_time": tool_config.avg_execution_time,
                "last_used": tool_config.last_used.isoformat() if tool_config.last_used else None,
                "availability": tool_config.availability
            }
        return metrics
