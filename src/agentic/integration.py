"""
Integration adapter to connect agentic orchestrator with existing systems
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import os

from .core.orchestrator import AgenticOrchestrator
from .core.models import Goal, TaskType

logger = logging.getLogger(__name__)


class AgenticIntegrationAdapter:
    """Adapter to integrate agentic orchestrator with existing FastAPI application"""
    
    def __init__(self):
        self.orchestrator = None
        self._initialized = False
        # Keep direct references to components for convenience
        self.knowledge_base = None
        self.ai_client = None
        self.memory_manager = None
        self.diagram_generator = None
        
    async def initialize(self) -> bool:
        """Initialize the agentic orchestrator with existing system components"""
        try:
            # Ensure package root is importable (usually already true when running FastAPI)
            package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # src/
            if package_root not in sys.path:
                sys.path.insert(0, package_root)
            
            # Try to import existing components
            knowledge_base = None
            ai_client = None
            memory_manager = None
            diagram_generator = None
            
            try:
                # Prefer absolute package imports to match the rest of the app
                from src.data.knowledge_base import KnowledgeBase
                knowledge_base = KnowledgeBase()
            except Exception as e:
                logger.warning("KnowledgeBase not available, using mock")
                logger.debug(f"KnowledgeBase import error: {e}")
                knowledge_base = self._create_mock_knowledge_base()
                
            try:
                from src.ai.multi_model_client import MultiModelClient  
                ai_client = MultiModelClient()
            except Exception as e:
                logger.warning("MultiModelClient not available, using mock")
                logger.debug(f"MultiModelClient import error: {e}")
                ai_client = self._create_mock_ai_client()
                
            try:
                from src.ai.memory_manager import MemoryManager
                memory_manager = MemoryManager()
            except Exception as e:
                logger.warning("MemoryManager not available, using mock")
                logger.debug(f"MemoryManager import error: {e}")
                memory_manager = self._create_mock_memory_manager()
                
            try:
                from src.core.diagram_generator import DiagramGenerator
                diagram_generator = DiagramGenerator()
            except Exception as e:
                logger.warning("DiagramGenerator not available, using mock")
                logger.debug(f"DiagramGenerator import error: {e}")
                diagram_generator = self._create_mock_diagram_generator()
            
            # Create orchestrator
            self.orchestrator = AgenticOrchestrator(
                knowledge_base=knowledge_base,
                ai_client=ai_client,
                memory_manager=memory_manager,
                diagram_generator=diagram_generator
            )
            # Save direct references
            self.knowledge_base = knowledge_base
            self.ai_client = ai_client
            self.memory_manager = memory_manager
            self.diagram_generator = diagram_generator
            
            self._initialized = True
            logger.info("Agentic orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agentic orchestrator: {e}")
            return False
            
    def _create_mock_knowledge_base(self):
        """Create a mock knowledge base for testing"""
        class MockKnowledgeBase:
            def list_repositories(self):
                return []
            def get_repository_knowledge(self, repo_name):
                return {}
            def get_all_repositories_knowledge(self):
                return {}
            def get_organization_patterns(self):
                return {"common_patterns": [], "notes": "mock"}
            
        return MockKnowledgeBase()
        
    def _create_mock_ai_client(self):
        """Create a mock AI client for testing"""
        class MockAIClient:
            def analyze_repository(self, repo_data, mermaid_diagram):
                return {
                    "components": [],
                    "architecture_patterns": [],
                    "tech_stack": {},
                    "analysis_note": "mock"
                }
            async def generate_response(self, prompt):
                return "Mock response"
            
        return MockAIClient()
        
    def _create_mock_memory_manager(self):
        """Create a mock memory manager for testing"""
        class MockMemoryManager:
            async def store_context(self, context): return True
            async def retrieve_relevant_context(self, query): return {}
            
        return MockMemoryManager()
        
    def _create_mock_diagram_generator(self):
        """Create a mock diagram generator for testing"""
        class MockDiagramGenerator:
            async def generate_mermaid_async(self, repo_data):
                return "graph TD\n  A[Mock Diagram]"
            def optimize_for_context(self, mermaid_code: str) -> str:
                return mermaid_code
            
        return MockDiagramGenerator()
            
    async def analyze_organization_autonomous(self, organization: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Autonomously analyze an organization using the agentic workflow"""
        if not self._initialized:
            await self.initialize()
            
        if not self.orchestrator:
            raise RuntimeError("Agentic orchestrator not initialized")
            
        try:
            # Execute autonomous analysis
            result = await self.orchestrator.autonomous_analyze_organization(
                user_request=f"Analyze {organization} organization",
                target_repos=options.get("target_repos") if options else None,
                user_id=options.get("user_id") if options else None
            )
            
            # Convert result to API response format
            return self._format_analysis_result(result)
            
        except Exception as e:
            logger.error(f"Autonomous organization analysis failed: {e}")
            raise
            
    async def analyze_repository_autonomous(self, repo_name: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Autonomously analyze a single repository"""
        if not self._initialized:
            await self.initialize()
            
        if not self.orchestrator:
            raise RuntimeError("Agentic orchestrator not initialized")
            
        try:
            # Get repository data
            repo_data = self.orchestrator.knowledge_base.get_repository_knowledge(repo_name)
            if not repo_data:
                repo_data = {"error": "Repository not found in knowledge base"}
            
            # Execute autonomous analysis
            result = await self.orchestrator.autonomous_analyze(
                repo_name=repo_name,
                repo_data=repo_data,
                user_request=f"Comprehensive analysis with options: {options}"
            )
            
            # Convert result to API response format
            return self._format_analysis_result(result)
            
        except Exception as e:
            logger.error(f"Autonomous repository analysis failed: {e}")
            raise
            
    async def suggest_feature_implementation(self, feature_request: str, repo_name: str = None) -> Dict[str, Any]:
        """Autonomously suggest feature implementation"""
        if not self._initialized:
            await self.initialize()
            
        if not self.orchestrator:
            raise RuntimeError("Agentic orchestrator not initialized")
            
        try:
            # Get repository data if repo_name provided
            repo_data = {}
            if repo_name:
                repo_data = self.orchestrator.knowledge_base.get_repository_knowledge(repo_name)
                if not repo_data:
                    repo_data = {"error": "Repository not found in knowledge base"}
            
            # Execute autonomous suggestion
            result = await self.orchestrator.autonomous_analyze(
                repo_name=repo_name or "unknown",
                repo_data=repo_data,
                user_request=f"Feature suggestion: {feature_request}"
            )
            
            return self._format_analysis_result(result)
            
        except Exception as e:
            logger.error(f"Autonomous feature suggestion failed: {e}")
            raise
            
    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current status of the agentic orchestrator"""
        if not self._initialized or not self.orchestrator:
            return {"status": "not_initialized", "active_tasks": 0}
            
        return {
            "status": "active",
            "active_tasks": len(self.orchestrator.active_tasks) if hasattr(self.orchestrator, 'active_tasks') else 0,
            "total_executed": getattr(self.orchestrator, 'total_tasks_executed', 0),
            "success_rate": getattr(self.orchestrator, 'success_rate', 0.0)
        }
        
    def _format_analysis_result(self, result) -> Dict[str, Any]:
        """Format agentic orchestrator result for API response"""
        
        # Handle AnalysisResult objects
        if hasattr(result, 'success'):
            # This is an AnalysisResult object
            formatted = {
                "success": result.success,
                "execution_time": result.execution_time,
                "tasks_completed": result.metadata.get("tasks_completed", 0),
                "analysis": result.data,
                "diagrams": result.data.get("diagrams", []),
                "recommendations": result.data.get("recommendations", []),
                "metadata": {
                    "autonomous_execution": True,
                    "confidence_score": result.confidence,
                    "analysis_type": result.analysis_type,
                    "timestamp": result.timestamp.isoformat(),
                    "errors": result.errors,
                    "warnings": result.warnings,
                    **result.metadata
                }
            }
            return formatted
        
        # Fallback for dictionary results (backward compatibility)
        if isinstance(result, dict):
            formatted = {
                "success": result.get("success", False),
                "execution_time": result.get("execution_time", 0),
                "tasks_completed": result.get("tasks_completed", 0),
                "analysis": {},
                "diagrams": [],
                "recommendations": [],
                "metadata": {}
            }
            
            # Extract analysis data
            if "results" in result:
                results = result["results"]
                
                # Structure analysis
                if "structure_analysis" in results:
                    formatted["analysis"]["structure"] = results["structure_analysis"]
                    
                # Pattern analysis
                if "pattern_analysis" in results:
                    formatted["analysis"]["patterns"] = results["pattern_analysis"]
                    
                # Tech stack
                if "tech_stack" in results:
                    formatted["analysis"]["technology"] = results["tech_stack"]
                    
                # Cross-repo insights
                if "cross_repo_analysis" in results:
                    formatted["analysis"]["cross_repository"] = results["cross_repo_analysis"]
                    
            # Extract diagrams
            if "diagrams" in result:
                formatted["diagrams"] = result["diagrams"]
                
            # Extract recommendations
            if "recommendations" in result:
                formatted["recommendations"] = result["recommendations"]
                
            # Add metadata
            formatted["metadata"] = {
                "autonomous_execution": True,
                "goal_achieved": result.get("goal_achieved", False),
                "confidence_score": result.get("confidence_score", 0.0),
                "validation_passed": result.get("validation_passed", False)
            }
            
            return formatted
        
        # Fallback for unknown result types
        return {
            "success": False,
            "error": f"Unknown result type: {type(result)}",
            "analysis": {},
            "diagrams": [],
            "recommendations": [],
            "metadata": {"autonomous_execution": True}
        }


# FastAPI integration functions
async def create_agentic_endpoints(app):
    """Add agentic endpoints to FastAPI application"""
    adapter = AgenticIntegrationAdapter()
    
    @app.post("/api/agentic/analyze/organization/{organization}")
    async def autonomous_analyze_organization(organization: str, options: Dict[str, Any] = None):
        """Autonomously analyze an entire organization"""
        try:
            result = await adapter.analyze_organization_autonomous(organization, options)
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Autonomous organization analysis failed: {e}")
            return {"status": "error", "message": str(e)}
            
    @app.post("/api/agentic/analyze/repository/{repo_name}")
    async def autonomous_analyze_repository(repo_name: str, options: Dict[str, Any] = None):
        """Autonomously analyze a single repository"""
        try:
            result = await adapter.analyze_repository_autonomous(repo_name, options)
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Autonomous repository analysis failed: {e}")
            return {"status": "error", "message": str(e)}
            
    @app.post("/api/agentic/suggest/feature")
    async def autonomous_suggest_feature(request: Dict[str, Any]):
        """Autonomously suggest feature implementation"""
        try:
            feature_request = request.get("feature_request")
            repo_name = request.get("repository")
            
            if not feature_request:
                return {"status": "error", "message": "feature_request is required"}
                
            result = await adapter.suggest_feature_implementation(feature_request, repo_name)
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Autonomous feature suggestion failed: {e}")
            return {"status": "error", "message": str(e)}
            
    @app.get("/api/agentic/status")
    async def get_agentic_status():
        """Get agentic orchestrator status"""
        try:
            status = await adapter.get_orchestrator_status()
            return {"status": "success", "data": status}
        except Exception as e:
            logger.error(f"Failed to get agentic status: {e}")
            return {"status": "error", "message": str(e)}
            
    return adapter


# Utility functions for backward compatibility
async def autonomous_analyze_wrapper(organization: str = None, repository: str = None, **kwargs) -> Dict[str, Any]:
    """Backward compatible wrapper for autonomous analysis"""
    adapter = AgenticIntegrationAdapter()
    await adapter.initialize()
    
    if organization:
        return await adapter.analyze_organization_autonomous(organization, kwargs)
    elif repository:
        return await adapter.analyze_repository_autonomous(repository, kwargs)
    else:
        raise ValueError("Either organization or repository must be specified")


# Export the main adapter
agentic_adapter = AgenticIntegrationAdapter()
