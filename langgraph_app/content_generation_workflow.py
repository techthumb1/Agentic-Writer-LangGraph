# File: langgraph_app/content_generation_workflow.py
"""
Content Generation Workflow - Enterprise Orchestrator Wrapper
Legacy compatibility wrapper that delegates to enhanced_orchestration.py
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from .enhanced_orchestration import EnhancedOrchestrator, create_enhanced_orchestrator
from .cache_system import create_cache_manager
from .job_queue import create_enterprise_job_manager

logger = logging.getLogger(__name__)

class ContentGenerationWorkflow:
    """Legacy workflow wrapper that uses enterprise orchestrator"""
    
    def __init__(self):
        self.orchestrator: EnhancedOrchestrator = None
        self.initialized = False
        
    async def _ensure_initialized(self):
        """Lazy initialization of enterprise components"""
        if not self.initialized:
            try:
                # Initialize cache manager
                cache_manager = await create_cache_manager("redis")
                
                # Create orchestrator with dependencies
                self.orchestrator = await create_enhanced_orchestrator(
                    cache_manager=cache_manager
                )
                
                self.initialized = True
                logger.info("Content workflow initialized with enterprise orchestrator")
                
            except Exception as e:
                logger.error(f"Failed to initialize enterprise workflow: {e}")
                # Fallback to basic orchestrator
                self.orchestrator = EnhancedOrchestrator()
                self.initialized = True
    
    async def generate_content(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for content generation
        Converts legacy format to enterprise format and delegates to orchestrator
        """
        try:
            await self._ensure_initialized()
            
            # Convert legacy request format to enterprise format
            enterprise_request = self._convert_legacy_request(request)
            
            logger.info(f"Starting enterprise content generation: {enterprise_request.get('template', 'unknown')}")
            
            # Delegate to enterprise orchestrator
            result = await self.orchestrator.generate_content(enterprise_request)
            
            # Convert back to legacy response format
            legacy_response = self._convert_to_legacy_response(result, request)
            
            return legacy_response
            
        except Exception as e:
            logger.error(f"Content generation workflow failed: {e}")
            return {
                "content": "",
                "metadata": {
                    "generation_id": f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "error": str(e)
                },
                "status": "error",
                "error": f"Workflow execution failed: {str(e)}",
            }
    
    def _convert_legacy_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legacy request format to enterprise orchestrator format"""
        try:
            prompt = request.get("prompt", {})
            preferences = request.get("preferences", {})
            
            # Extract content requirements
            content_req = prompt.get("content_requirements", {})
            user_params = prompt.get("user_parameters", {})
            
            # Create enterprise request
            enterprise_request = {
                "template": user_params.get("template", "1"),
                "style_profile": user_params.get("style_profile", "1"), 
                "dynamic_parameters": {
                    "topic": content_req.get("title", "Untitled Content"),
                    "audience": content_req.get("target_audience", "general"),
                    "difficulty": content_req.get("difficulty", "intermediate"),
                    "category": content_req.get("category", "general"),
                    "sections": content_req.get("sections", []),
                    
                    # Style preferences
                    "tone": prompt.get("style_requirements", {}).get("tone", "professional"),
                    "voice": prompt.get("style_requirements", {}).get("voice", "authoritative"),
                    "formality": prompt.get("style_requirements", {}).get("formality", "formal"),
                    "technical_level": prompt.get("style_requirements", {}).get("technical_level", "intermediate"),
                    
                    # Structure preferences
                    "use_headings": prompt.get("structure_requirements", {}).get("use_headings", True),
                    "use_bullet_points": prompt.get("structure_requirements", {}).get("use_bullet_points", True),
                    "include_examples": prompt.get("structure_requirements", {}).get("include_examples", True),
                    "paragraph_length": prompt.get("structure_requirements", {}).get("paragraph_length", "medium"),
                    
                    # Language preferences
                    "vocabulary_level": prompt.get("language_requirements", {}).get("vocabulary_level", "intermediate"),
                    "sentence_complexity": prompt.get("language_requirements", {}).get("sentence_complexity", "mixed"),
                    "use_jargon": prompt.get("language_requirements", {}).get("use_jargon", False),
                    
                    # Formatting preferences
                    "markdown_enabled": prompt.get("formatting_requirements", {}).get("markdown_enabled", True),
                    "emoji_usage": prompt.get("formatting_requirements", {}).get("emoji_usage", "none"),
                    
                    # Generation preferences
                    "max_tokens": preferences.get("maxTokens", 2000),
                    "temperature": preferences.get("temperature", 0.7),
                    "model": preferences.get("model", "gpt-4-turbo"),
                    
                    # Pass through all user parameters
                    **user_params
                }
            }
            
            return enterprise_request
            
        except Exception as e:
            logger.error(f"Failed to convert legacy request: {e}")
            # Return minimal valid request
            return {
                "template": "1",
                "style_profile": "1", 
                "dynamic_parameters": {
                    "topic": "Content Generation",
                    "audience": "general"
                }
            }
    
    def _convert_to_legacy_response(self, enterprise_result: Dict[str, Any], original_request: Dict[str, Any]) -> Dict[str, Any]:
        """Convert enterprise response back to legacy format"""
        try:
            if enterprise_result.get("success"):
                # Successful generation
                metadata = enterprise_result.get("metadata", {})
                
                return {
                    "content": enterprise_result.get("content", ""),
                    "metadata": {
                        "model_used": original_request.get("preferences", {}).get("model", "gpt-4-turbo"),
                        "tokens_consumed": metadata.get("word_count", 0) * 1.3,  # Rough estimate
                        "generation_time": metadata.get("actual_generation_time", 0),
                        "generation_id": enterprise_result.get("generation_id", "unknown"),
                        "template_used": metadata.get("template_id", "unknown"),
                        "style_profile_used": metadata.get("style_profile", "unknown"),
                        "completed_agents": metadata.get("completed_agents", []),
                        "failed_agents": metadata.get("failed_agents", []),
                        "word_count": metadata.get("word_count", 0),
                        "quality_score": enterprise_result.get("quality_score", {}),
                        "seo_metadata": metadata.get("seo_metadata", {}),
                        "innovation_report": metadata.get("innovation_report", {}),
                    },
                    "status": "success",
                    "errors": None,
                }
            else:
                # Failed generation
                return {
                    "content": "",
                    "metadata": {
                        "generation_id": enterprise_result.get("generation_id", "error"),
                        "error": enterprise_result.get("error", "Unknown error")
                    },
                    "status": "error",
                    "error": enterprise_result.get("error", "Generation failed"),
                    "errors": [enterprise_result.get("error", "Unknown error")]
                }
                
        except Exception as e:
            logger.error(f"Failed to convert enterprise response: {e}")
            return {
                "content": "",
                "metadata": {
                    "generation_id": "conversion_error",
                    "error": str(e)
                },
                "status": "error",
                "error": f"Response conversion failed: {str(e)}"
            }

# Async wrapper for backward compatibility
class AsyncContentWorkflow:
    """Async wrapper for the content workflow"""
    
    def __init__(self):
        self.workflow = ContentGenerationWorkflow()
    
    async def generate_content(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Async content generation"""
        return await self.workflow.generate_content(request)

# Global instances for backward compatibility
content_workflow = ContentGenerationWorkflow()
async_content_workflow = AsyncContentWorkflow()

# Legacy compatibility functions
async def generate_content_async(request: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy async function for content generation"""
    return await content_workflow.generate_content(request)

def generate_content_sync(request: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy sync function for content generation"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(content_workflow.generate_content(request))
    finally:
        loop.close()

# Export for main.py compatibility
class EnhancedWorkflow:
    """Enhanced workflow class for main.py integration"""
    
    def __init__(self):
        self.workflow = ContentGenerationWorkflow()
    
    async def generate_content(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using enterprise orchestrator"""
        return await self.workflow.generate_content(request)

# Create instance that main.py expects
enhanced_workflow = EnhancedWorkflow()