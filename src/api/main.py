import asyncio
import logging
import traceback
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.core.repo_handler import RepoHandler
from src.core.diagram_generator import DiagramGenerator
from src.ai.multi_model_client import MultiModelClient
from src.data.knowledge_base import KnowledgeBase
from src.ai.conversation_manager import ConversationManager
# Import new agentic system
from src.agentic.integration import AgenticIntegrationAdapter, create_agentic_endpoints
from src.agentic.core.orchestrator import AgenticOrchestrator
from src.agentic.core.models import Goal, TaskType
import os
from dotenv import load_dotenv
import sqlite3
import json
from typing import Dict, Any, Optional, List
import re

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Code Architecture Agent")

# Add CORS middleware for frontend (driven by env)
_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
]
_frontend_url = os.getenv("FRONTEND_URL")
_extra_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
_allow_origins = _default_origins + ([_frontend_url] if _frontend_url else []) + _extra_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components
repo_handler = RepoHandler(os.getenv("GITHUB_TOKEN"))
diagram_generator = DiagramGenerator()
ai_client = MultiModelClient()
knowledge_base = KnowledgeBase()

# Initialize conversation manager
conversation_manager = ConversationManager()

# Initialize agentic integration adapter
agentic_adapter = AgenticIntegrationAdapter()

async def startup_event():
    """Initialize agentic orchestrator on startup"""
    logger.info("Initializing agentic orchestrator...")
    success = await agentic_adapter.initialize()
    if success:
        logger.info("✅ Agentic orchestrator initialized successfully")
    else:
        logger.warning("⚠️ Agentic orchestrator initialization failed, falling back to basic mode")

# Add startup event
app.add_event_handler("startup", startup_event)


@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve the main interface"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        agentic_status = "✅ Active" if agentic_adapter._initialized else "⚠️ Not Available"
        return HTMLResponse(content=f"""
        <html>
            <head>
                <title>AI Code Architecture Agent</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .status {{ padding: 10px; border-radius: 5px; margin: 10px 0; }}
                    .active {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
                    .inactive {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
                    .endpoint {{ background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>AI Code Architecture Agent</h1>
                <div class="status {'active' if agentic_adapter._initialized else 'inactive'}">
                    <strong>Agentic Orchestrator Status:</strong> {agentic_status}
                </div>
                
                <h2>Available Endpoints:</h2>
                
                <div class="endpoint">
                    <h3>Repository Analysis</h3>
                    <ul>
                        <li><strong>POST /analyze-repo</strong> - Analyze a repository (enhanced with agentic capabilities)</li>
                        <li><strong>POST /api/agentic/analyze/repository/{{repo_name}}</strong> - Full autonomous repository analysis</li>
                        <li><strong>POST /api/agentic/analyze/organization/{{organization}}</strong> - Autonomous organization-wide analysis</li>
                    </ul>
                </div>
                
                <div class="endpoint">
                    <h3>Feature Suggestions</h3>
                    <ul>
                        <li><strong>POST /suggest-feature</strong> - Get feature placement suggestions (enhanced with agentic capabilities)</li>
                        <li><strong>POST /api/agentic/suggest/feature</strong> - Autonomous feature implementation suggestions</li>
                    </ul>
                </div>
                
                <div class="endpoint">
                    <h3>Smart Analysis</h3>
                    <ul>
                        <li><strong>POST /api/agentic/analyze/smart</strong> - Smart analysis with automatic approach selection</li>
                        <li><strong>GET /api/agentic/status</strong> - Get agentic orchestrator status and metrics</li>
                    </ul>
                </div>
                
                <div class="endpoint">
                    <h3>Repository Management</h3>
                    <ul>
                        <li><strong>GET /repositories</strong> - List analyzed repositories</li>
                        <li><strong>POST /ask-question</strong> - Ask questions about repositories</li>
                        <li><strong>GET /health</strong> - Health check</li>
                    </ul>
                </div>
                
                <h2>Agentic Capabilities:</h2>
                <ul>
                    <li>🤖 <strong>Autonomous Planning</strong> - Breaks down complex tasks automatically</li>
                    <li>🔧 <strong>Self-Correction</strong> - Detects and fixes errors during analysis</li>
                    <li>🧠 <strong>Multi-Step Reasoning</strong> - Iterative problem solving</li>
                    <li>⚡ <strong>Dynamic Tool Selection</strong> - Chooses optimal tools for each task</li>
                    <li>🎯 <strong>Goal-Oriented Behavior</strong> - Works towards specific objectives</li>
                    <li>🏢 <strong>Organizational Analysis</strong> - Cross-repository insights</li>
                </ul>
            </body>
        </html>
        """)


@app.post("/analyze-repo")
async def analyze_repository(
    file: UploadFile = File(None),
    repo_url: str = Form(None),
    repo_name: str = Form(...)
):
    """Analyze a repository and build knowledge base"""
    
    try:
        # Debug: Print what we received
        logger.info(f"Received file: {file.filename if file else None}")
        logger.info(f"Received repo_url: {repo_url}")
        logger.info(f"Received repo_name: {repo_name}")
        
        # Process repository
        if file and file.filename:
            # Save uploaded file
            file_path = f"temp_{file.filename}"
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            
            repo_data = repo_handler.process_repo_zip(file_path)
            os.remove(file_path)
        elif repo_url and repo_url.strip():
            repo_data = repo_handler.fetch_github_repo(repo_url)
        else:
            logger.error("No file or repo_url provided")
            return {"error": "Either file or repo_url must be provided"}
        
        # Generate Mermaid diagram using async method
        mermaid_diagram = await diagram_generator.generate_mermaid_async(repo_data)
        optimized_diagram = diagram_generator.optimize_for_context(mermaid_diagram)
        
        # Try autonomous agentic analysis first, fallback to regular analysis
        analysis = None
        agentic_success = False
        
        try:
            if agentic_adapter.orchestrator:
                logger.info(f"🤖 Using agentic analysis for {repo_name}")
                agentic_result = await agentic_adapter.analyze_repository_autonomous(repo_name, {
                    "repo_data": repo_data,
                    "include_diagram": True
                })
                
                if agentic_result.get("success"):
                    analysis = agentic_result.get("data", {})
                    agentic_success = True
                    logger.info("✅ Agentic analysis completed successfully")
                else:
                    logger.warning("⚠️ Agentic analysis failed, falling back to regular analysis")
        except Exception as e:
            logger.warning(f"⚠️ Agentic analysis error, falling back: {e}")
        
        # Fallback to regular AI analysis if agentic failed
        if not agentic_success:
            try:
                logger.info(f"🔄 Using regular AI analysis for {repo_name}")
                analysis = ai_client.analyze_repository(repo_data, optimized_diagram)
            except Exception as e:
                logger.error(f"AI analysis error: {e}")
                # Handle errors gracefully
                analysis = {
                    "architecture_summary": "Analysis failed due to an error.",
                    "error": str(e)
                }
        
        # Store in knowledge base
        knowledge_base.store_repository(repo_name, repo_data, analysis, optimized_diagram)
        
        # Initialize conversation for this repository
        conversation_manager.start_conversation(repo_name, {
            'repo_data': repo_data,
            'analysis': analysis,
            'mermaid_diagram': optimized_diagram
        })
        
        # Add initial analysis message to conversation
        conversation_manager.add_message(
            repo_name, 
            'assistant', 
            analysis.get("architecture_summary", "Repository analysis completed"),
            {'type': 'initial_analysis'}
        )
        
        logger.info(f"Repository {repo_name} analyzed and stored successfully")
        
        return {
            "success": True,
            "message": f"Repository {repo_name} analyzed and stored",
            "analysis_summary": analysis.get("architecture_summary", "Analysis complete"),
            "mermaid_diagram": optimized_diagram
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_repository: {e}")
        logger.debug(traceback.format_exc())
        return {"error": str(e)}


@app.post("/suggest-feature")
async def suggest_feature_placement(
    repo_name: str = Form(...),
    feature_description: str = Form(...)
):
    """Suggest where to place a new feature using agentic workflow when available"""
    
    try:
        # Get repository knowledge
        knowledge = knowledge_base.get_repository_knowledge(repo_name)
        
        if not knowledge:
            logger.warning(f"Repository {repo_name} not found in knowledge base")
            return {"error": f"Repository {repo_name} not found in knowledge base"}
        
        # Try agentic feature suggestion first
        suggestions = None
        agentic_success = False
        
        try:
            if agentic_adapter.orchestrator:
                logger.info(f"🤖 Using agentic feature suggestion for {repo_name}")
                agentic_result = await agentic_adapter.suggest_feature_implementation(
                    feature_description, repo_name
                )
                
                if agentic_result.get("success"):
                    suggestions = agentic_result.get("data", {}).get("analysis", {}).get("suggestions", [])
                    agentic_success = True
                    logger.info("✅ Agentic feature suggestion completed")
        except Exception as e:
            logger.warning(f"⚠️ Agentic feature suggestion failed, falling back: {e}")
        
        # Fallback to regular AI suggestions
        if not agentic_success:
            logger.info(f"🔄 Using regular AI feature suggestion for {repo_name}")
            suggestions = ai_client.suggest_feature_placement(
                feature_description, knowledge
            )
        
        logger.info(f"Feature placement suggestions for {repo_name}: {suggestions}")
        
        return {
            "success": True,
            "feature_description": feature_description,
            "suggestions": suggestions,
            "agentic_analysis": agentic_success
        }
        
    except Exception as e:
        logger.error(f"Error in suggest_feature_placement: {e}")
        logger.debug(traceback.format_exc())
        return {"error": str(e)}


@app.get("/repositories")
async def list_repositories():
    """List all analyzed repositories"""
    repos = knowledge_base.list_repositories()
    logger.info(f"Listing analyzed repositories: {repos}")
    return {"repositories": repos}


# ==================== AGENTIC ENDPOINTS ====================

@app.post("/api/agentic/analyze/organization/{organization}")
async def autonomous_analyze_organization(organization: str, options: Optional[Dict[str, Any]] = None):
    """Autonomously analyze an entire organization using agentic workflow"""
    try:
        logger.info(f"🚀 Starting autonomous organization analysis for: {organization}")
        result = await agentic_adapter.analyze_organization_autonomous(organization, options)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Autonomous organization analysis failed: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/agentic/analyze/repository/{repo_name}")
async def autonomous_analyze_repository(repo_name: str, options: Optional[Dict[str, Any]] = None):
    """Autonomously analyze a single repository using agentic workflow"""
    try:
        logger.info(f"🔍 Starting autonomous repository analysis for: {repo_name}")
        result = await agentic_adapter.analyze_repository_autonomous(repo_name, options)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Autonomous repository analysis failed: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/agentic/suggest/feature")
async def autonomous_suggest_feature(request: Dict[str, Any]):
    """Autonomously suggest feature implementation using agentic workflow"""
    try:
        feature_request = request.get("feature_request")
        repo_name = request.get("repository")
        
        if not feature_request:
            return {"status": "error", "message": "feature_request is required"}
            
        logger.info(f"🎯 Starting autonomous feature suggestion: {feature_request}")
        result = await agentic_adapter.suggest_feature_implementation(feature_request, repo_name)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Autonomous feature suggestion failed: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/agentic/status")
async def get_agentic_status():
    """Get agentic orchestrator status"""
    try:
        status = await agentic_adapter.get_orchestrator_status()
        return {"status": "success", "data": status}
    except Exception as e:
        logger.error(f"Failed to get agentic status: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/agentic/analyze/smart")
async def smart_analyze_with_context(
    repo_name: str = Form(...),
    user_request: str = Form(None),
    analysis_type: str = Form("comprehensive")
):
    """Smart analysis that automatically selects the best approach using agentic workflow"""
    try:
        logger.info(f"🧠 Starting smart agentic analysis for {repo_name}")
        
        # Get repository data
        repo_data = knowledge_base.get_repository_knowledge(repo_name)
        if not repo_data:
            return {"status": "error", "message": f"Repository {repo_name} not found"}
        
        # Create autonomous goal based on user request and analysis type
        if analysis_type == "comprehensive":
            goal = Goal(
                goal_id=f"smart_analysis_{repo_name}_{int(datetime.now().timestamp())}",
                description=f"Comprehensive autonomous analysis of {repo_name}",
                success_criteria=[
                    "Repository structure fully analyzed",
                    "Architectural patterns identified",
                    "Technology stack mapped",
                    "Feature recommendations provided",
                    "Visual diagrams generated",
                    "Team recommendations delivered"
                ],
                context={
                    "repository": repo_name,
                    "user_request": user_request,
                    "analysis_type": analysis_type,
                    "repo_data": repo_data
                }
            )
        else:
            goal = Goal(
                goal_id=f"focused_analysis_{repo_name}_{int(datetime.now().timestamp())}",
                description=f"Focused analysis of {repo_name} for specific request",
                success_criteria=[
                    "User request addressed",
                    "Relevant analysis completed",
                    "Actionable recommendations provided"
                ],
                context={
                    "repository": repo_name,
                    "user_request": user_request,
                    "analysis_type": analysis_type,
                    "repo_data": repo_data
                }
            )
        
        # Execute autonomous analysis
        if agentic_adapter.orchestrator:
            result = await agentic_adapter.orchestrator.autonomous_analyze(goal)
        else:
            # Fallback to regular analysis
            # Include diagram context if available in knowledge base
            kb_mermaid = repo_data.get('mermaid_diagram') if isinstance(repo_data, dict) else None
            result = ai_client.analyze_repository(repo_data, kb_mermaid or (user_request or ""))
            
        return {"status": "success", "data": result}
        
    except Exception as e:
        logger.error(f"Smart agentic analysis failed: {e}")
        return {"status": "error", "message": str(e)}


# ==================== END AGENTIC ENDPOINTS ====================


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check performed")
    return {"status": "healthy", "message": "AI Code Architecture Agent is running"}


@app.get("/api/model-health")
async def get_model_health():
    """Get the current health status of AI models"""
    try:
        # Get model availability
        available_models = []
        for model_info in ai_client.models:
            available_models.append({
                'name': model_info['name'],
                'type': model_info['type'],
                'healthy': ai_client.error_handler.is_model_healthy(model_info['name'])
            })
        
        # Get error summary
        error_summary = ai_client.error_handler.get_error_summary()
        
        # Get cache stats
        cache_stats = ai_client.cache.get_stats()
        
        return {
            'success': True,
            'models': available_models,
            'total_models': len(available_models),
            'healthy_models': len([m for m in available_models if m['healthy']]),
            'error_summary': error_summary,
            'cache_stats': cache_stats,
            'recommendations': _get_health_recommendations(available_models, error_summary)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'models': [],
            'total_models': 0,
            'healthy_models': 0
        }


@app.post("/api/clear-model-errors")
async def clear_model_errors():
    """Clear recorded model errors (admin endpoint)"""
    try:
        ai_client.error_handler.error_count.clear()
        ai_client.error_handler.last_errors.clear()
        
        return {
            'success': True,
            'message': 'Model error history cleared'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@app.post("/api/clear-cache")
async def clear_cache():
    """Clear the response cache (admin endpoint)"""
    try:
        cleared_count = ai_client.cache.clear_all()
        
        return {
            'success': True,
            'message': f'Cleared {cleared_count} cache entries'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def _get_health_recommendations(models: list, error_summary: dict) -> list:
    """Generate health recommendations based on current status"""
    recommendations = []
    
    healthy_count = len([m for m in models if m['healthy']])
    total_count = len(models)
    
    if healthy_count == 0:
        recommendations.append({
            'type': 'critical',
            'message': 'No healthy AI models available. Check API keys and network connectivity.'
        })
    elif healthy_count < total_count:
        unhealthy = [m['name'] for m in models if not m['healthy']]
        recommendations.append({
            'type': 'warning',
            'message': f'Some models are unhealthy: {", ".join(unhealthy)}. Consider checking their configuration.'
        })
    
    total_errors = error_summary.get('total_errors', 0)
    if total_errors > 10:
        recommendations.append({
            'type': 'warning',
            'message': f'High error count ({total_errors}). Consider clearing error history or checking model configurations.'
        })
    
    if not recommendations:
        recommendations.append({
            'type': 'success',
            'message': 'All models are healthy and functioning normally.'
        })
    
    return recommendations


@app.post("/ask-question")
async def ask_question(
    question: str = Form(...),
    repo_context: str = Form(None),
    repo_contexts: str = Form(None)
):
    """
    Ask a question about a previously analyzed repository
    """
    try:
        logger.info(f"Received question: {question}")
        logger.info(f"Received repository context: {repo_context}")
        logger.info(f"Received repository contexts: {repo_contexts}")

        # Parse multi-repo contexts if provided
        contexts: List[str] = []
        if repo_contexts:
            try:
                parsed = json.loads(repo_contexts)
                if isinstance(parsed, list):
                    contexts = [str(x) for x in parsed]
            except Exception:
                # Fallback: comma or space separated
                contexts = [c for c in re.split(r"[,\s]+", repo_contexts) if c]

        if not contexts and repo_context:
            contexts = [repo_context]

        valid_repos: List[str] = [r for r in contexts if knowledge_base.has_repository(r)]

        # If multiple valid repos provided, build a blended context
        if len(valid_repos) > 1:
            all_repos_knowledge = knowledge_base.get_all_repositories_knowledge()
            org_patterns = knowledge_base.get_organization_patterns()

            # Collect conversation and memory per repo
            conversation_sections = []
            memory_sections = []
            files_sections = []
            diagrams_sections = []

            # Limit total files across repos to avoid token blow-up
            max_total_files = 40
            per_repo_limit = max(8, max_total_files // len(valid_repos))
            important_extensions = ('.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.go', '.rs', '.php', '.rb', '.json', '.yaml', '.yml', '.toml', '.md', '.txt', '.html', '.css', '.scss', '.sql')
            config_files = ('package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle', 'tsconfig.json', 'dockerfile', 'docker-compose.yml', '.env.example', 'readme.md', 'license', 'makefile')

            for rname in valid_repos:
                repo_knowledge = knowledge_base.get_repository_knowledge(rname)
                # Conversation history
                conv = conversation_manager.format_conversation_for_ai(rname)
                if conv:
                    conversation_sections.append(f"**Conversation ({rname}):**\n{conv}")

                # Memory context
                mem_section = ""
                if conversation_manager.memory_manager:
                    related_memories = conversation_manager.memory_manager.search_memories(
                        query=question,
                        user_id=f"repo_{rname}",
                        limit=6
                    )
                    if related_memories:
                        mem_section = "\n".join([f"- {m.get('memory','')}" for m in related_memories if m.get('memory')])
                if mem_section:
                    memory_sections.append(f"**Memories ({rname}):**\n{mem_section}")

                # Files and structure
                file_contents = repo_knowledge.get('file_contents', {})
                file_structure = repo_knowledge.get('file_structure', [])
                files_block = ["**File Tree:**"] + [f"- {p}" for p in sorted(file_structure)[:200]]
                files_block.append("\n**File Contents (important excerpts):**")
                selected = 0
                for fpath, finfo in file_contents.items():
                    if selected >= per_repo_limit:
                        break
                    if (fpath.lower().endswith(important_extensions) or any(cfg.lower() in fpath.lower() for cfg in config_files)):
                        content = finfo.get('content', '')[:1500]
                        ftype = finfo.get('type', 'unknown')
                        files_block.append(f"\n--- {fpath} ({ftype}) ---\n{content}")
                        selected += 1
                files_sections.append(f"**Repository ({rname}) Files:**\n" + "\n".join(files_block))

                # Diagrams
                diag = repo_knowledge.get('mermaid_diagram') or ''
                if diag:
                    diagrams_sections.append(f"**System Diagram ({rname}):**\n```mermaid\n{diag}\n```")

            prompt = f"""
You are analyzing a user question across multiple related repositories in the same organization.

Repositories involved: {', '.join(valid_repos)}

Question:
{question}

ORGANIZATION-WIDE CONTEXT:
- Total repositories: {len(all_repos_knowledge)}
- Common Languages: {', '.join([f"{lang} ({count} repos)" for lang, count in list(org_patterns['languages'].items())[:5]])}
- Common Frameworks: {', '.join([f"{fw} ({count} repos)" for fw, count in list(org_patterns['frameworks'].items())[:5]])}
- File Extensions Used: {', '.join([f".{ext} ({count} files)" for ext, count in list(org_patterns['file_patterns'].items())[:10]])}

CONVERSATION HISTORY:
{chr(10).join(conversation_sections) if conversation_sections else 'None'}

MEMORY CONTEXT:
{chr(10).join(memory_sections) if memory_sections else 'None'}

REPOSITORY CONTEXTS (files and structure):
{chr(10).join(files_sections)}

DIAGRAMS:
{chr(10).join(diagrams_sections) if diagrams_sections else 'None'}

Instructions:
1. Provide a unified answer that references the specific repositories by name where relevant.
2. Call out integration points between these repos (APIs, events, contracts, shared types).
3. When suggesting implementation, indicate exact files and locations per repo following their patterns.
4. Note differences in stack or conventions and recommend consistent org-wide patterns where helpful.
5. Keep it concise, structured, and avoid repeating the same info for each repo unless necessary.
"""

            response = await ai_client.generate_response(prompt)

            # Add messages to each involved repo conversation
            for rname in valid_repos:
                conversation_manager.add_message(rname, 'user', question)
                conversation_manager.add_message(rname, 'assistant', response)

            logger.info(f"Question answered with multi-repo context for {', '.join(valid_repos)}")

            return {
                "success": True,
                "message": "Question answered with multi-repo context",
                "analysis_summary": response,
                "repo_contexts": valid_repos
            }

        # Single repository path (backward-compatible)
        if contexts and len(valid_repos) == 1:
            repo_context = valid_repos[0]
            repo_knowledge = knowledge_base.get_repository_knowledge(repo_context)
            # ALSO get all repositories for cross-repo context
            all_repos_knowledge = knowledge_base.get_all_repositories_knowledge()
            org_patterns = knowledge_base.get_organization_patterns()
            
            # Get conversation history
            conversation_history = conversation_manager.format_conversation_for_ai(repo_context)
            
            # **ENHANCED MEMORY INTEGRATION - Search for relevant memories**
            memory_context = ""
            if conversation_manager.memory_manager:
                # Search for memories related to the current question
                related_memories = conversation_manager.memory_manager.search_memories(
                    query=question,
                    user_id=f"repo_{repo_context}",
                    limit=10
                )
                
                if related_memories:
                    memory_context = "\n**RELEVANT CONVERSATION HISTORY:**\n"
                    for memory in related_memories:
                        memory_text = memory.get('memory', '')
                        if memory_text:
                            memory_context += f"- {memory_text}\n"
                    memory_context += "\n"
                    logger.info(f"Found {len(related_memories)} relevant memories for context")
                else:
                    logger.info("No relevant memories found")
            
            # Add user question to conversation
            conversation_manager.add_message(repo_context, 'user', question)
            
            # Build comprehensive context with file structure and contents
            file_contents = repo_knowledge.get('file_contents', {})
            file_structure = repo_knowledge.get('file_structure', [])
            
            # Create detailed file tree with contents
            files_context = "**COMPLETE FILE STRUCTURE AND CONTENTS:**\n\n"
            
            # Add file tree
            files_context += "**File Tree:**\n"
            for file_path in sorted(file_structure):
                files_context += f"- {file_path}\n"
            
            files_context += "\n**File Contents:**\n"
            
            # Add file contents (limit to important files to avoid token limits)
            important_extensions = ('.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.go', '.rs', '.php', '.rb', '.json', '.yaml', '.yml', '.toml', '.md', '.txt', '.html', '.css', '.scss', '.sql')
            config_files = ('package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle', 'tsconfig.json', 'dockerfile', 'docker-compose.yml', '.env.example', 'readme.md', 'license', 'makefile')
            
            for file_path, file_info in file_contents.items():
                # Include file if it's an important extension or config file
                if (file_path.lower().endswith(important_extensions) or 
                    any(config.lower() in file_path.lower() for config in config_files)):
                    
                    content = file_info.get('content', '')[:2000]  # Limit content size
                    file_type = file_info.get('type', 'unknown')
                    
                    files_context += f"\n--- {file_path} ({file_type}) ---\n"
                    files_context += content
                    if len(file_info.get('content', '')) > 2000:
                        files_context += "\n... (content truncated)"
                    files_context += "\n"
            
            # Use the AI client to answer the question with context
            prompt = f"""
Based on the previously analyzed repository '{repo_context}', please answer this question:

{conversation_history}

{memory_context}

**Current Question:** {question}

{files_context}

**ORGANIZATION-WIDE CONTEXT:**
This organization has {len(all_repos_knowledge)} repositories total.

**Organization Patterns:**
- Common Languages: {', '.join([f"{lang} ({count} repos)" for lang, count in list(org_patterns['languages'].items())[:5]])}
- Common Frameworks: {', '.join([f"{fw} ({count} repos)" for fw, count in list(org_patterns['frameworks'].items())[:5]])}
- File Extensions Used: {', '.join([f".{ext} ({count} files)" for ext, count in list(org_patterns['file_patterns'].items())[:10]])}

**Other Repositories in Organization:**
{chr(10).join([f"- {name}: {data['analysis'].get('architecture_summary', 'No summary')[:100]}..." for name, data in list(all_repos_knowledge.items())[:5] if name != repo_context])}

**Architecture Analysis:**
{repo_knowledge.get('analysis', {}).get('architecture_summary', 'No analysis available')}

**System Diagram:**
```mermaid
{repo_knowledge.get('mermaid_diagram', 'No diagram available')}
```

IMPORTANT: Use the relevant conversation history above to maintain context and avoid repeating information. Build upon previous discussions and reference earlier conversations when relevant.

You now have access to the COMPLETE codebase structure and file contents PLUS context from {len(all_repos_knowledge)} other repositories in this organization PLUS relevant conversation history.

When answering:
1. **Reference previous conversations** and build upon them
2. Use patterns from other repos in the organization
3. Suggest consistency with the org's common tech stack
4. Reference similar implementations from other repos when relevant
5. Consider the organization's architectural patterns

When suggesting where to add new features:
1. Follow patterns used across the organization
2. Identify the exact files that would need to be modified
3. Specify the exact locations within those files
4. Provide code examples based on the existing patterns in THIS codebase AND organization patterns
5. Consider the existing architecture and follow the same patterns used across all repos
6. **Build upon previous suggestions** and maintain conversation continuity

Consider the conversation history when answering to maintain context and avoid repeating information already provided.
"""
            
            response = await ai_client.generate_response(prompt)
            
            # Add AI response to conversation
            conversation_manager.add_message(repo_context, 'assistant', response)
            
            logger.info(f"Question answered with repository context for {repo_context}")
            
            return {
                "success": True,
                "message": "Question answered with repository context",
                "analysis_summary": response,
                "repo_context": repo_context
            }
        else:
            # No repository context available
            general_prompt = f"""
The user is asking: {question}

Since no specific codebase context is available, provide general guidance about:
1. Common approaches to this type of question
2. Typical file locations and patterns
3. Best practices and recommendations
4. Suggest that they upload/analyze a specific codebase for more targeted advice

Be helpful but explain that specific codebase analysis would provide better recommendations.
"""
            
            response = await ai_client.generate_response(general_prompt)
            
            logger.info("General guidance provided due to lack of specific context")
            
            return {
                "success": True,
                "message": "General guidance provided",
                "analysis_summary": response,
                "repo_context": None
            }
            
    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        logger.debug(traceback.format_exc())
        return {
            "success": False,
            "message": f"Error processing question: {str(e)}"
        }


@app.get("/conversation/{repo_name}")
async def get_conversation_history(repo_name: str):
    """Get conversation history for a repository"""
    try:
        history = conversation_manager.get_conversation_history(repo_name)
        return {
            "success": True,
            "repo_name": repo_name,
            "conversation_history": history
        }
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return {"error": str(e)}


@app.delete("/conversation/{repo_name}")
async def clear_conversation_history(repo_name: str):
    """Clear conversation history for a repository"""
    try:
        conversation_manager.clear_conversation(repo_name)
        return {
            "success": True,
            "message": f"Conversation history cleared for {repo_name}"
        }
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        return {"error": str(e)}


@app.post("/chat-with-memory")
async def chat_with_memory(
    repo_name: str = Form(...),
    message: str = Form(...),
    user_id: str = Form(None)
):
    """Chat about a repository with memory context"""
    try:
        if not user_id:
            user_id = f"repo_{repo_name}"
        
        # Use conversation manager's memory-enabled chat
        response = conversation_manager.chat_with_memory(
            repo_name, message, user_id
        )
        
        logger.info(f"Memory chat for {repo_name}: {message[:100]}...")
        
        return {
            "success": True,
            "response": response,
            "repo_name": repo_name,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error in chat_with_memory: {e}")
        logger.debug(traceback.format_exc())
        return {"error": str(e)}


@app.post("/analyze-repo-with-memory")
async def analyze_repository_with_memory(
    file: UploadFile = File(None),
    repo_url: str = Form(None),
    repo_name: str = Form(...),
    user_id: str = Form(None)
):
    """Analyze a repository with memory context"""
    try:
        if not user_id:
            user_id = f"repo_{repo_name}"
        
        # First do the regular analysis
        regular_result = await analyze_repository(file, repo_url, repo_name)
        
        if not regular_result.get("success"):
            return regular_result
        
        # Get repository data and diagram for memory analysis
        repo_knowledge = knowledge_base.get_repository_knowledge(repo_name)
        if not repo_knowledge:
            return {"error": "Repository analysis failed"}
        
        # Use memory-enabled analysis
        memory_analysis = conversation_manager.analyze_with_memory(
            repo_name,
            repo_knowledge,
            repo_knowledge.get('mermaid_diagram', ''),
            user_id
        )
        
        # Combine results
        result = regular_result.copy()
        result["memory_analysis"] = memory_analysis
        result["user_id"] = user_id
        
        logger.info(f"Memory-enabled analysis completed for {repo_name}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in analyze_repository_with_memory: {e}")
        logger.debug(traceback.format_exc())
        return {"error": str(e)}


@app.post("/suggest-feature-with-memory")
async def suggest_feature_with_memory(
    repo_name: str = Form(...),
    feature_description: str = Form(...),
    user_id: str = Form(None)
):
    """Suggest feature placement with memory context"""
    try:
        if not user_id:
            user_id = f"repo_{repo_name}"
        
        # Get repository knowledge
        knowledge = knowledge_base.get_repository_knowledge(repo_name)
        
        if not knowledge:
            return {"error": f"Repository {repo_name} not found in knowledge base"}
        
        # Use memory-enabled feature suggestion
        suggestions = conversation_manager.suggest_feature_with_memory(
            repo_name, feature_description, knowledge, user_id
        )
        
        logger.info(f"Memory-enabled feature suggestions for {repo_name}")
        
        return {
            "success": True,
            "feature_description": feature_description,
            "suggestions": suggestions,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error in suggest_feature_with_memory: {e}")
        logger.debug(traceback.format_exc())
        return {"error": str(e)}


@app.get("/memory-search")
async def search_memories(
    query: str,
    user_id: str = None,
    repo_name: str = None,
    limit: int = 5
):
    """Search through user memories"""
    try:
        if not user_id and repo_name:
            user_id = f"repo_{repo_name}"
        
        if not user_id:
            return {"error": "user_id or repo_name is required"}
        
        if conversation_manager.memory_manager:
            memories = conversation_manager.memory_manager.search_memories(
                query, user_id, limit
            )
            return {
                "success": True,
                "memories": memories,
                "query": query,
                "user_id": user_id
            }
        else:
            return {"error": "Memory system not available"}
        
    except Exception as e:
        logger.error(f"Error in memory search: {e}")
        return {"error": str(e)}


@app.get("/debug/repository/{repo_name}")
async def debug_repository_knowledge(repo_name: str):
    """Debug endpoint to inspect what knowledge is stored for a repository"""
    try:
        knowledge = knowledge_base.get_repository_knowledge(repo_name)
        
        if not knowledge:
            return {"error": f"Repository {repo_name} not found in knowledge base"}
        
        # Create a summary of what's available
        summary = {
            "repo_name": repo_name,
            "has_file_structure": bool(knowledge.get('file_structure')),
            "has_file_contents": bool(knowledge.get('file_contents')),
            "has_analysis": bool(knowledge.get('analysis')),
            "has_mermaid_diagram": bool(knowledge.get('mermaid_diagram')),
            "file_structure_count": len(knowledge.get('file_structure', [])),
            "file_contents_count": len(knowledge.get('file_contents', {})),
            "sample_files": list(knowledge.get('file_contents', {}).keys())[:10],
            "analysis_keys": list(knowledge.get('analysis', {}).keys()) if isinstance(knowledge.get('analysis'), dict) else [],
            "mermaid_diagram_length": len(knowledge.get('mermaid_diagram', '')),
        }
        
        return {
            "success": True,
            "summary": summary,
            "sample_file_content": {
                file_path: str(content)[:200] + "..." if len(str(content)) > 200 else str(content)
                for file_path, content in list(knowledge.get('file_contents', {}).items())[:3]
            }
        }
        
    except Exception as e:
        logger.error(f"Error in debug repository knowledge: {e}")
        return {"error": str(e)}


@app.get("/api/knowledge-base/tables")
async def get_knowledge_base_tables():
    """Get all tables and their structure from the knowledge base"""
    try:
        conn = sqlite3.connect(knowledge_base.db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        table_info = {}
        for table in tables:
            table_name = table[0]
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            table_info[table_name] = {
                "columns": [{"name": col[1], "type": col[2], "pk": bool(col[5])} for col in columns],
                "row_count": row_count
            }
        
        conn.close()
        return {"success": True, "tables": table_info}
        
    except Exception as e:
        logger.error(f"Error getting knowledge base tables: {e}")
        return {"error": str(e)}


@app.get("/api/knowledge-base/table/{table_name}")
async def get_table_data(table_name: str, limit: int = 100, offset: int = 0):
    """Get data from a specific table with pagination"""
    try:
        conn = sqlite3.connect(knowledge_base.db_path)
        cursor = conn.cursor()
        
        # Validate table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            return {"error": f"Table {table_name} not found"}
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get data with pagination
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (limit, offset))
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Truncate long JSON strings for display
                if isinstance(value, str) and len(value) > 500:
                    try:
                        # Try to parse as JSON and show summary
                        parsed = json.loads(value)
                        if isinstance(parsed, dict):
                            value = f"{{...}} ({len(parsed)} keys)"
                        elif isinstance(parsed, list):
                            value = f"[...] ({len(parsed)} items)"
                    except:
                        value = value[:500] + "..."
                row_dict[col] = value
            data.append(row_dict)
        
        conn.close()
        return {
            "success": True,
            "table_name": table_name,
            "columns": columns,
            "data": data,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting table data: {e}")
        return {"error": str(e)}


@app.get("/api/knowledge-base/table/{table_name}/all")
async def get_all_table_data(table_name: str):
    """Get ALL data from a specific table without pagination"""
    try:
        conn = sqlite3.connect(knowledge_base.db_path)
        cursor = conn.cursor()
        
        # Validate table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            return {"error": f"Table {table_name} not found"}
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get ALL data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Keep full data for editing
                row_dict[col] = value
            data.append(row_dict)
        
        conn.close()
        return {
            "success": True,
            "table_name": table_name,
            "columns": columns,
            "data": data,
            "total_count": len(data)
        }
        
    except Exception as e:
        logger.error(f"Error getting all table data: {e}")
        return {"error": str(e)}


@app.post("/api/knowledge-base/table/{table_name}/row")
async def add_table_row(table_name: str, row_data: dict):
    """Add a new row to a table"""
    try:
        conn = sqlite3.connect(knowledge_base.db_path)
        cursor = conn.cursor()
        
        # Validate table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            return {"error": f"Table {table_name} not found"}
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        
        # Filter out auto-increment primary key columns
        columns = [col[1] for col in columns_info if not (col[5] == 1 and col[2] == 'INTEGER')]
        
        # Prepare data
        values = []
        placeholders = []
        for col in columns:
            if col in row_data:
                values.append(row_data[col])
                placeholders.append('?')
        
        if not values:
            return {"error": "No valid data provided"}
        
        # Insert row
        columns_str = ', '.join(columns[:len(values)])
        placeholders_str = ', '.join(placeholders)
        
        cursor.execute(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders_str})", values)
        conn.commit()
        
        new_row_id = cursor.lastrowid
        conn.close()
        
        return {
            "success": True,
            "message": f"Row added to {table_name}",
            "row_id": new_row_id
        }
        
    except Exception as e:
        logger.error(f"Error adding row to table: {e}")
        return {"error": str(e)}


@app.put("/api/knowledge-base/table/{table_name}/row/{row_id}")
async def update_table_row(table_name: str, row_id: int, row_data: dict):
    """Update an existing row in a table"""
    try:
        conn = sqlite3.connect(knowledge_base.db_path)
        cursor = conn.cursor()
        
        # Validate table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            return {"error": f"Table {table_name} not found"}
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]
        
        # Prepare update data
        set_clauses = []
        values = []
        for col in columns:
            if col in row_data and col != 'id':  # Don't update id column
                set_clauses.append(f"{col} = ?")
                values.append(row_data[col])
        
        if not set_clauses:
            return {"error": "No valid data provided for update"}
        
        values.append(row_id)
        set_clause = ', '.join(set_clauses)
        
        cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE id = ?", values)
        conn.commit()
        
        if cursor.rowcount == 0:
            return {"error": f"Row with id {row_id} not found"}
        
        conn.close()
        
        return {
            "success": True,
            "message": f"Row {row_id} updated in {table_name}"
        }
        
    except Exception as e:
        logger.error(f"Error updating row in table: {e}")
        return {"error": str(e)}


@app.delete("/api/knowledge-base/table/{table_name}/row/{row_id}")
async def delete_table_row(table_name: str, row_id: int):
    """Delete a row from a table"""
    try:
        conn = sqlite3.connect(knowledge_base.db_path)
        cursor = conn.cursor()
        
        # Validate table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            return {"error": f"Table {table_name} not found"}
        
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return {"error": f"Row with id {row_id} not found"}
        
        conn.close()
        
        return {
            "success": True,
            "message": f"Row {row_id} deleted from {table_name}"
        }
        
    except Exception as e:
        logger.error(f"Error deleting row from table: {e}")
        return {"error": str(e)}


@app.post("/api/knowledge-base/execute-sql")
async def execute_sql_query(request: dict):
    """Execute a custom SQL query (SELECT only for security)"""
    try:
        query = request.get('query', '')
        
        # Security check - only allow SELECT queries
        query_upper = query.upper().strip()
        if not query_upper.startswith('SELECT'):
            return {"error": "Only SELECT queries are allowed"}
        
        conn = sqlite3.connect(knowledge_base.db_path)
        cursor = conn.cursor()
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            data.append(row_dict)
        
        conn.close()
        
        return {
            "success": True,
            "columns": columns,
            "data": data,
            "row_count": len(data)
        }
        
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        return {"error": str(e)}


@app.get("/api/knowledge-base/export")
async def export_database():
    """Export the database as JSON"""
    try:
        conn = sqlite3.connect(knowledge_base.db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        export_data = {}
        for table in tables:
            table_name = table[0]
            
            # Get all data from each table
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Convert to list of dictionaries
            table_data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                table_data.append(row_dict)
            
            export_data[table_name] = table_data
        
        conn.close()
        
        return {
            "success": True,
            "export_data": export_data,
            "exported_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error exporting database: {e}")
        return {"error": str(e)}


@app.get("/api/knowledge-base/repository/{repo_name}/details")
async def get_repository_details(repo_name: str):
    """Get detailed information about a specific repository"""
    try:
        conn = sqlite3.connect(knowledge_base.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, repo_name, repo_hash, file_structure, file_contents, 
                   analysis, mermaid_diagram, created_at 
            FROM repositories 
            WHERE repo_name = ?
        ''', (repo_name,))
        
        result = cursor.fetchone()
        if not result:
            return {"error": f"Repository {repo_name} not found"}
        
        # Parse JSON fields safely
        try:
            file_structure = json.loads(result[3]) if result[3] else []
        except:
            file_structure = []
            
        try:
            file_contents = json.loads(result[4]) if result[4] else {}
        except:
            file_contents = {}
            
        try:
            analysis = json.loads(result[5]) if result[5] else {}
        except:
            analysis = {}
        
        # Get features for this repository
        cursor.execute('''
            SELECT feature_description, suggestions, created_at 
            FROM features 
            WHERE repo_id = ?
            ORDER BY created_at DESC
        ''', (result[0],))
        
        features = cursor.fetchall()
        
        conn.close()
        
        return {
            "success": True,
            "repository": {
                "id": result[0],
                "name": result[1],
                "hash": result[2],
                "file_structure": file_structure,
                "file_contents_count": len(file_contents),
                "file_contents_sample": {k: str(v)[:200] + "..." if len(str(v)) > 200 else str(v) 
                                       for k, v in list(file_contents.items())[:5]},
                "analysis": analysis,
                "mermaid_diagram": result[6],
                "created_at": result[7],
                "features": [{"description": f[0], "suggestions": f[1], "created_at": f[2]} for f in features]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting repository details: {e}")
        return {"error": str(e)}


@app.get("/api/knowledge-base/debug/endpoints")
async def debug_endpoints():
    """Debug endpoint to list all available endpoints"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'N/A')
            })
    return {"routes": routes}


@app.get("/api/conversations")
async def get_all_conversations():
    """Get all conversation sessions"""
    try:
        conversations = []
        for repo_name, conversation_data in conversation_manager.conversations.items():
            conversations.append({
                "repo_name": repo_name,
                "message_count": len(conversation_data.get('messages', [])),
                "created_at": conversation_data.get('created_at'),
                "last_activity": conversation_data.get('messages', [{}])[-1].get('timestamp') if conversation_data.get('messages') else None
            })
        
        return {
            "success": True,
            "conversations": conversations
        }
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return {"error": str(e)}


@app.get("/api/conversations/{repo_name}")
async def get_conversation_history(repo_name: str):
    """Get conversation history for a specific repository"""
    try:
        history = conversation_manager.get_conversation_history(repo_name, max_messages=100)
        repo_context = conversation_manager.get_repo_context(repo_name)
        
        return {
            "success": True,
            "repo_name": repo_name,
            "messages": history,
            "repo_context": repo_context,
            "message_count": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return {"error": str(e)}


@app.post("/api/conversations/{repo_name}/switch")
async def switch_conversation(repo_name: str):
    """Switch to a specific repository conversation"""
    try:
        # Check if conversation exists
        if repo_name not in conversation_manager.conversations:
            # Try to find the repository in knowledge base
            if knowledge_base.has_repository(repo_name):
                repo_knowledge = knowledge_base.get_repository_knowledge(repo_name)
                conversation_manager.start_conversation(repo_name, {
                    'repo_name': repo_name,
                    'knowledge': repo_knowledge
                })
            else:
                return {"error": f"Repository {repo_name} not found"}
        
        history = conversation_manager.get_conversation_history(repo_name, max_messages=100)
        repo_context = conversation_manager.get_repo_context(repo_name)
        
        return {
            "success": True,
            "repo_name": repo_name,
            "messages": history,
            "repo_context": repo_context,
            "message": f"Switched to {repo_name} conversation"
        }
    except Exception as e:
        logger.error(f"Error switching conversation: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
