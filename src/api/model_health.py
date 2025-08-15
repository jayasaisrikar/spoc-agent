"""
API endpoint for monitoring model health and error status
"""
from fastapi import APIRouter
from typing import Dict, Any
import json

router = APIRouter()

@router.get("/model-health")
async def get_model_health() -> Dict[str, Any]:
    """Get the current health status of AI models"""
    try:
        # Import here to avoid circular imports
        from src.ai.multi_model_client import MultiModelClient
        
        client = MultiModelClient()
        
        # Get model availability
        available_models = []
        for model_info in client.models:
            available_models.append({
                'name': model_info['name'],
                'type': model_info['type'],
                'healthy': client.error_handler.is_model_healthy(model_info['name'])
            })
        
        # Get error summary
        error_summary = client.error_handler.get_error_summary()
        
        # Get cache stats
        cache_stats = client.cache.get_stats()
        
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

@router.post("/clear-model-errors")
async def clear_model_errors() -> Dict[str, Any]:
    """Clear recorded model errors (admin endpoint)"""
    try:
        from src.ai.multi_model_client import MultiModelClient
        
        client = MultiModelClient()
        client.error_handler.error_count.clear()
        client.error_handler.last_errors.clear()
        
        return {
            'success': True,
            'message': 'Model error history cleared'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@router.post("/clear-cache")
async def clear_cache() -> Dict[str, Any]:
    """Clear the response cache (admin endpoint)"""
    try:
        from src.ai.multi_model_client import MultiModelClient
        
        client = MultiModelClient()
        cleared_count = client.cache.clear_all()
        
        return {
            'success': True,
            'message': f'Cleared {cleared_count} cache entries'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def _get_health_recommendations(models: list, error_summary: Dict) -> list:
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
