"""
Result validator for self-correction and quality assurance
"""
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

from .models import Task, Goal, TaskType, ValidationResult, ExecutionContext

logger = logging.getLogger(__name__)


class ResultValidator:
    """
    Self-correction system that detects and fixes errors in analysis results
    """
    
    def __init__(self, confidence_threshold: float = 0.75):
        self.confidence_threshold = confidence_threshold
        self.validation_history: List[Dict] = []
        
    async def validate_and_correct(self, results: Dict, goal: Goal, 
                                 context: ExecutionContext) -> ValidationResult:
        """
        Self-correction - detecting and fixing errors
        """
        logger.info("🔍 Validating results and applying corrections")
        
        issues = []
        recommendations = []
        confidence_scores = []
        
        # Validate completeness
        completeness_validation = await self._validate_completeness(results, goal)
        if not completeness_validation.is_valid:
            issues.extend(completeness_validation.issues)
            recommendations.extend(completeness_validation.recommendations)
        else:
            confidence_scores.append(completeness_validation.confidence)
        
        # Validate individual task results
        for task_id, result in results.items():
            if task_id != "execution_metadata":  # Skip metadata
                task_validation = await self._validate_task_result(task_id, result, goal)
                
                if not task_validation.is_valid:
                    issues.extend(task_validation.issues)
                    recommendations.extend(task_validation.recommendations)
                else:
                    confidence_scores.append(task_validation.confidence)
        
        # Validate cross-task consistency
        consistency_check = await self._validate_result_consistency(results)
        if not consistency_check.is_valid:
            issues.extend(consistency_check.issues)
            recommendations.extend(consistency_check.recommendations)
        else:
            confidence_scores.append(consistency_check.confidence)
        
        # Validate organizational context
        org_validation = await self._validate_organizational_context(results, context)
        if not org_validation.is_valid:
            issues.extend(org_validation.issues)
            recommendations.extend(org_validation.recommendations)
        else:
            confidence_scores.append(org_validation.confidence)
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        validation_result = ValidationResult(
            is_valid=len(issues) == 0,
            confidence=overall_confidence,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "validation_time": datetime.now().isoformat(),
                "tasks_validated": len([k for k in results.keys() if k != "execution_metadata"]),
                "validation_categories": {
                    "completeness": completeness_validation.is_valid,
                    "task_quality": all(v.is_valid for v in [await self._validate_task_result(k, v, goal) 
                                                            for k, v in results.items() if k != "execution_metadata"]),
                    "consistency": consistency_check.is_valid,
                    "organizational_context": org_validation.is_valid
                }
            }
        )
        
        # Store validation history
        self.validation_history.append({
            "timestamp": datetime.now().isoformat(),
            "goal_id": goal.goal_id,
            "overall_confidence": overall_confidence,
            "issues_count": len(issues),
            "recommendations_count": len(recommendations)
        })
        
        return validation_result
    
    async def _validate_completeness(self, results: Dict, goal: Goal) -> ValidationResult:
        """Validate that all required tasks have been completed"""
        issues = []
        recommendations = []
        
        # Check task completion
        completed_tasks = len([task_id for task_id in goal.associated_tasks 
                              if task_id in results and task_id != "execution_metadata"])
        total_tasks = len(goal.associated_tasks)
        
        completion_ratio = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        if completion_ratio < 0.8:
            issues.append(f"Only {completed_tasks}/{total_tasks} tasks completed ({completion_ratio*100:.1f}%)")
            recommendations.append("Continue task execution or replan failed tasks")
        
        # Check for critical missing components
        critical_task_types = [TaskType.ANALYZE_STRUCTURE, TaskType.CROSS_REPO_ANALYSIS]
        for task_id in goal.associated_tasks:
            # This would require task type mapping - simplified for now
            if task_id not in results:
                issues.append(f"Critical task {task_id} not completed")
                recommendations.append(f"Retry or replan task {task_id}")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence=completion_ratio,
            issues=issues,
            recommendations=recommendations
        )
    
    async def _validate_task_result(self, task_id: str, result: Dict, goal: Goal) -> ValidationResult:
        """Validate individual task results"""
        issues = []
        recommendations = []
        confidence = 0.5  # Default confidence
        
        # Check if result has expected structure
        if not result:
            issues.append(f"Task {task_id} returned empty result")
            recommendations.append(f"Retry task {task_id}")
            return ValidationResult(False, 0.0, issues, recommendations)
        
        if not isinstance(result, dict):
            issues.append(f"Task {task_id} returned invalid result format")
            recommendations.append(f"Fix result format for task {task_id}")
            return ValidationResult(False, 0.1, issues, recommendations)
        
        # Check for errors
        if 'error' in result:
            issues.append(f"Task {task_id} returned error: {result['error']}")
            recommendations.append(f"Debug and retry task {task_id}")
            return ValidationResult(False, 0.1, issues, recommendations)
        
        # Extract confidence if available
        if 'confidence' in result:
            confidence = result['confidence']
            if confidence < self.confidence_threshold:
                issues.append(f"Task {task_id} has low confidence: {confidence}")
                recommendations.append(f"Improve or retry task {task_id}")
        
        # Task-specific validation
        task_type = self._infer_task_type(task_id, result)
        type_validation = await self._validate_by_task_type(task_type, result)
        
        if not type_validation.is_valid:
            issues.extend(type_validation.issues)
            recommendations.extend(type_validation.recommendations)
        else:
            confidence = max(confidence, type_validation.confidence)
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations
        )
    
    async def _validate_by_task_type(self, task_type: TaskType, result: Dict) -> ValidationResult:
        """Validate result based on task type"""
        issues = []
        confidence = 0.7
        
        if task_type == TaskType.ANALYZE_STRUCTURE:
            if 'components' not in result and 'analysis' not in result:
                issues.append("Structure analysis missing components or analysis data")
            if 'tech_stack' not in result:
                issues.append("Structure analysis missing technology stack information")
                
        elif task_type == TaskType.EXTRACT_PATTERNS:
            if 'patterns' not in result:
                issues.append("Pattern extraction missing patterns data")
            elif isinstance(result['patterns'], dict):
                total_patterns = sum(len(p) if isinstance(p, list) else 1 for p in result['patterns'].values())
                if total_patterns == 0:
                    issues.append("No patterns detected - may indicate analysis issue")
                    
        elif task_type == TaskType.GENERATE_DIAGRAM:
            if 'mermaid' not in result:
                issues.append("Diagram generation missing mermaid output")
            elif not result['mermaid'] or len(result['mermaid']) < 10:
                issues.append("Generated diagram appears to be empty or invalid")
                
        elif task_type == TaskType.CROSS_REPO_ANALYSIS:
            if 'patterns' not in result and 'shared_technologies' not in result:
                issues.append("Cross-repo analysis missing pattern or technology data")
            if 'analyzed_repos' in result and result['analyzed_repos'] == 0:
                issues.append("Cross-repo analysis found no valid repositories")
                
        elif task_type == TaskType.TECH_STACK_MAPPING:
            if 'tech_mapping' not in result:
                issues.append("Tech stack mapping missing mapping data")
            elif isinstance(result['tech_mapping'], dict):
                total_techs = sum(len(v) if isinstance(v, dict) else 0 for v in result['tech_mapping'].values())
                if total_techs == 0:
                    issues.append("No technologies detected in mapping")
                    
        elif task_type == TaskType.TEAM_RECOMMENDATIONS:
            if 'recommendations' not in result:
                issues.append("Team recommendations missing recommendations data")
            elif isinstance(result['recommendations'], dict):
                total_recs = sum(len(v) if isinstance(v, list) else 0 for v in result['recommendations'].values())
                if total_recs == 0:
                    issues.append("No recommendations generated")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence=confidence if len(issues) == 0 else confidence * 0.5,
            issues=issues,
            recommendations=[]
        )
    
    def _infer_task_type(self, task_id: str, result: Dict) -> TaskType:
        """Infer task type from task ID and result content"""
        task_id_lower = task_id.lower()
        
        if 'analyze' in task_id_lower and 'structure' in task_id_lower:
            return TaskType.ANALYZE_STRUCTURE
        elif 'pattern' in task_id_lower:
            return TaskType.EXTRACT_PATTERNS
        elif 'diagram' in task_id_lower:
            return TaskType.GENERATE_DIAGRAM
        elif 'cross_repo' in task_id_lower:
            return TaskType.CROSS_REPO_ANALYSIS
        elif 'tech' in task_id_lower:
            return TaskType.TECH_STACK_MAPPING
        elif 'team' in task_id_lower:
            return TaskType.TEAM_RECOMMENDATIONS
        elif 'validate' in task_id_lower:
            return TaskType.VALIDATE_ANALYSIS
        elif 'feature' in task_id_lower:
            return TaskType.SUGGEST_FEATURES
        
        # Fallback: infer from result content
        if 'mermaid' in result:
            return TaskType.GENERATE_DIAGRAM
        elif 'patterns' in result and 'shared_technologies' in result:
            return TaskType.CROSS_REPO_ANALYSIS
        elif 'tech_mapping' in result:
            return TaskType.TECH_STACK_MAPPING
        elif 'recommendations' in result:
            return TaskType.TEAM_RECOMMENDATIONS
        
        return TaskType.ANALYZE_STRUCTURE  # Default
    
    async def _validate_result_consistency(self, results: Dict) -> ValidationResult:
        """Validate consistency across task results"""
        issues = []
        confidence = 0.8
        
        # Extract common data elements
        languages_found = set()
        frameworks_found = set()
        patterns_found = set()
        
        for task_id, result in results.items():
            if task_id == "execution_metadata" or not isinstance(result, dict):
                continue
                
            # Extract languages and frameworks from different tasks
            if 'languages' in result:
                if isinstance(result['languages'], list):
                    languages_found.update(result['languages'])
                    
            if 'frameworks' in result:
                if isinstance(result['frameworks'], list):
                    frameworks_found.update(result['frameworks'])
                    
            if 'tech_stack' in result and isinstance(result['tech_stack'], dict):
                if 'languages' in result['tech_stack']:
                    languages_found.update(result['tech_stack']['languages'])
                if 'frameworks' in result['tech_stack']:
                    frameworks_found.update(result['tech_stack']['frameworks'])
                    
            if 'tech_mapping' in result and isinstance(result['tech_mapping'], dict):
                if 'languages' in result['tech_mapping']:
                    languages_found.update(result['tech_mapping']['languages'].keys())
                if 'frameworks' in result['tech_mapping']:
                    frameworks_found.update(result['tech_mapping']['frameworks'].keys())
            
            # Extract patterns
            if 'patterns' in result:
                if isinstance(result['patterns'], list):
                    patterns_found.update(result['patterns'])
                elif isinstance(result['patterns'], dict):
                    for category, pattern_list in result['patterns'].items():
                        if isinstance(pattern_list, list):
                            patterns_found.update(pattern_list)
        
        # Consistency checks
        if len(languages_found) > 15:
            issues.append(f"Too many different languages detected ({len(languages_found)}) - possible inconsistency")
            confidence -= 0.2
            
        if len(frameworks_found) > 20:
            issues.append(f"Too many different frameworks detected ({len(frameworks_found)}) - possible inconsistency")
            confidence -= 0.1
        
        # Check for conflicting technology information
        common_conflicts = [
            (['java', 'python', 'javascript'], "Multiple primary languages"),
            (['react', 'vue', 'angular'], "Multiple frontend frameworks"),
            (['spring', 'django', 'express'], "Multiple backend frameworks")
        ]
        
        for conflict_set, description in common_conflicts:
            found_conflicting = [tech for tech in conflict_set if tech.lower() in [l.lower() for l in languages_found.union(frameworks_found)]]
            if len(found_conflicting) > 2:
                issues.append(f"Potential conflict detected: {description} - {found_conflicting}")
                confidence -= 0.1
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence=max(confidence, 0.1),
            issues=issues,
            recommendations=["Review technology detection accuracy" if issues else ""]
        )
    
    async def _validate_organizational_context(self, results: Dict, context: ExecutionContext) -> ValidationResult:
        """Validate results against organizational context"""
        issues = []
        confidence = 0.8
        
        org_context = context.organizational_context
        
        # Check if results align with organizational metrics
        if 'total_repos' in org_context:
            total_repos = org_context['total_repos']
            analyzed_repos = 0
            
            for task_id, result in results.items():
                if isinstance(result, dict) and 'analyzed_repos' in result:
                    analyzed_repos = max(analyzed_repos, result['analyzed_repos'])
            
            if analyzed_repos < total_repos * 0.5:
                issues.append(f"Only analyzed {analyzed_repos}/{total_repos} repositories")
                confidence -= 0.3
        
        # Check against known organizational patterns
        if 'patterns' in org_context:
            known_patterns = org_context['patterns']
            found_patterns = set()
            
            for task_id, result in results.items():
                if isinstance(result, dict) and 'patterns' in result:
                    patterns = result['patterns']
                    if isinstance(patterns, dict):
                        for category, pattern_list in patterns.items():
                            if isinstance(pattern_list, list):
                                found_patterns.update(pattern_list)
            
            # Check if we found expected patterns
            expected_patterns = set(known_patterns.get('architectural', {}).keys())
            if expected_patterns and not found_patterns.intersection(expected_patterns):
                issues.append("Expected organizational patterns not detected")
                confidence -= 0.2
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence=confidence,
            issues=issues,
            recommendations=["Verify organizational context accuracy" if issues else ""]
        )
    
    async def final_validation(self, results: Dict, goal: Goal) -> ValidationResult:
        """Perform final validation of all results"""
        issues = []
        confidence_scores = []
        
        # Check goal completion
        if goal.completion_percentage < 100:
            issues.append(f"Goal only {goal.completion_percentage:.1f}% complete")
        
        # Check result quality
        for task_id, result in results.items():
            if task_id != "execution_metadata" and isinstance(result, dict):
                if 'confidence' in result:
                    confidence_scores.append(result['confidence'])
                elif 'error' not in result:
                    confidence_scores.append(0.6)  # Default for results without confidence
        
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        # Check for minimum viable results
        required_data_points = ['structure', 'patterns', 'technologies']
        found_data_points = []
        
        for task_id, result in results.items():
            if isinstance(result, dict):
                if any(key in result for key in ['components', 'analysis']):
                    found_data_points.append('structure')
                if 'patterns' in result:
                    found_data_points.append('patterns')
                if any(key in result for key in ['tech_stack', 'tech_mapping']):
                    found_data_points.append('technologies')
        
        found_data_points = list(set(found_data_points))
        missing_data = [dp for dp in required_data_points if dp not in found_data_points]
        
        if missing_data:
            issues.append(f"Missing critical data points: {missing_data}")
        
        return ValidationResult(
            is_valid=len(issues) == 0 and overall_confidence >= self.confidence_threshold,
            confidence=overall_confidence,
            issues=issues,
            recommendations=["Improve analysis depth" if missing_data else ""]
        )
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation performance metrics"""
        if not self.validation_history:
            return {"total_validations": 0}
        
        total_validations = len(self.validation_history)
        avg_confidence = sum(v["overall_confidence"] for v in self.validation_history) / total_validations
        avg_issues = sum(v["issues_count"] for v in self.validation_history) / total_validations
        
        return {
            "total_validations": total_validations,
            "avg_confidence": avg_confidence,
            "avg_issues_per_validation": avg_issues,
            "last_validation": self.validation_history[-1]["timestamp"],
            "confidence_trend": [v["overall_confidence"] for v in self.validation_history[-10:]]  # Last 10
        }
