# langgraph_app/core/generation_engine.py
"""
Content generation engine with MCP and Universal system integration
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from ..config.settings import settings
from ..models.api_models import GenerationStatus, ContentTemplate, StyleProfile, GenerateRequest
from ..utils.content_extraction import extract_content_from_langgraph_result, extract_sources_from_langgraph_result
from ..utils.yaml_utils import safe_yaml_load, validate_template_structure
from ..mcp_server_extension import enhance_generation_with_mcp

logger = logging.getLogger(__name__)

class GenerationEngine:
    """Handles content generation orchestration."""
    
    def __init__(self):
        self.generation_tasks: Dict[str, GenerationStatus] = {}
    
    def should_use_universal_system(
        self,
        template_config: Dict[str, Any], 
        style_config: Dict[str, Any], 
        dynamic_parameters: Dict[str, Any]
    ) -> bool:
        """
        Determine if Universal System should be activated based on content complexity,
        novelty, and template characteristics.
        """
        
        # Force Universal for specific template types
        universal_template_triggers = [
            'universal', 'dynamic', 'adaptive', 'novel', 'custom',
            'comprehensive', 'advanced', 'research', 'analysis'
        ]
        
        template_name = template_config.get('name', '').lower()
        template_id = template_config.get('id', '').lower()
        
        # Check template-based triggers
        if any(trigger in template_name or trigger in template_id for trigger in universal_template_triggers):
            logger.info("Universal activated: Template-based trigger detected")
            return True
        
        # Check for novel/complex topics in parameters
        topic_fields = ['topic', 'subject', 'title', 'content_area', 'domain', 'field']
        novel_indicators = [
            'underwater basket weaving', 'urban message delivery', 'vertical hydroponic',
            'experimental', 'innovative', 'cutting-edge', 'emerging', 'breakthrough',
            'novel', 'unique', 'custom', 'specialized', 'niche', 'advanced'
        ]
        
        for field in topic_fields:
            if field in dynamic_parameters:
                topic_content = str(dynamic_parameters[field]).lower()
                if any(indicator in topic_content for indicator in novel_indicators):
                    logger.info(f"Universal activated: Novel topic detected in {field}: {topic_content[:50]}...")
                    return True
        
        # Check content complexity requirements
        complexity_indicators = [
            'multi-section', 'comprehensive', 'detailed analysis', 'research-based',
            'in-depth', 'technical documentation', 'white paper', 'case study'
        ]
        
        all_text = ' '.join([
            str(v) for v in dynamic_parameters.values() if isinstance(v, str)
        ]).lower()
        
        if any(indicator in all_text for indicator in complexity_indicators):
            logger.info("Universal activated: Complex content requirements detected")
            return True
        
        # Force Universal for specific style profiles that benefit from dynamic generation
        dynamic_style_profiles = [
            'research', 'academic', 'technical', 'experimental', 'innovative'
        ]
        
        style_name = style_config.get('name', '').lower()
        style_id = style_config.get('id', '').lower()
        
        if any(profile in style_name or profile in style_id for profile in dynamic_style_profiles):
            logger.info("Universal activated: Dynamic style profile detected")
            return True
        
        # Parameter count threshold - complex requests likely need Universal
        if len(dynamic_parameters) >= 5:
            logger.info(f"Universal activated: High parameter count ({len(dynamic_parameters)} params)")
            return True
        
        # Check for enterprise/premium generation modes
        generation_mode = template_config.get('generation_mode', '')
        if generation_mode in ['premium', 'enterprise']:
            logger.info(f"Universal activated: Premium generation mode ({generation_mode})")
            return True
        
        return False
    
    def determine_generation_approach(
        self,
        template: ContentTemplate,
        profile: StyleProfile,
        request_data: GenerateRequest,
        app_state
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Determine whether to use Universal system or direct MCP generation
        Returns: (approach_type, enhanced_config)
        """
        
        template_config = template.dict()
        template_config.update(request_data.dynamic_parameters)
        style_config = profile.dict()
        
        # Initialize Universal system if needed
        if not hasattr(app_state, 'universal_integration'):
            try:
                from ..universal_system.universal_integration import LangGraphUniversalIntegration
                app_state.universal_integration = LangGraphUniversalIntegration()
                logger.info("Universal Integration initialized on-demand")
            except ImportError as e:
                logger.error(f"Failed to import Universal Integration: {e}")
                app_state.universal_integration = None
        
        # Determine if Universal should be used
        use_universal = self.should_use_universal_system(template_config, style_config, request_data.dynamic_parameters)
        
        if use_universal and app_state.universal_integration:
            # Enhanced Universal configuration
            enhanced_config = {
                'approach': 'universal_mcp',
                'universal_context': {
                    'template_preference': template.id,
                    'complexity_level': 'high',
                    'research_depth': 'comprehensive',
                    'generation_mode': template_config.get('generation_mode', 'premium'),
                    'user_parameters': request_data.dynamic_parameters,
                    'user_preferences': {
                        'preferred_style': profile.id
                    }
                },
                'mcp_options': {
                    'enable_mcp': True,
                    'research_depth': 'comprehensive',
                    'memory_namespace': 'universal_generation',
                    'timeout_seconds': request_data.timeout_seconds,
                    'priority': request_data.priority,
                    'advanced_features': True,
                    'tool_selection': 'dynamic'
                }
            }

            return 'universal', enhanced_config
        else:
            # Direct MCP configuration
            enhanced_config = {
                'approach': 'direct_mcp',
                'template_config': template_config,
                'style_config': style_config,
                'mcp_options': {
                    'enable_mcp': True,
                    'research_depth': 'moderate',
                    'memory_namespace': 'standard_generation',
                    'timeout_seconds': request_data.timeout_seconds,
                    'priority': request_data.priority
                }
            }
            return 'direct', enhanced_config
    
    async def execute_content_generation(
        self,
        request_id: str,
        template_config: Dict[str, Any],
        style_config: Dict[str, Any],
        app_state,
        mcp_options: Optional[Dict[str, Any]] = None
    ) -> GenerationStatus:
        """Execute content generation via MCP pipeline with LangGraph agents."""
        start_time = datetime.now()
        mcp_options = mcp_options or {}

        def _persist_and_return(status: GenerationStatus) -> GenerationStatus:
            self.generation_tasks[request_id] = status
            return status

        try:
            logger.info(f"Starting LangGraph+MCP generation [request_id={request_id}, template={template_config.get('name')}, style={style_config.get('name')}]")

            # ENTERPRISE: Strict validation - no fallbacks
            if not getattr(app_state, "mcp_available", False):
                err = "MCP system not available - LangGraph agents require MCP tools"
                logger.error(f"{err} [request_id={request_id}]")
                return _persist_and_return(GenerationStatus(
                    request_id=request_id, status="failed", progress=0.0, current_step="MCP Unavailable",
                    content="", metadata={"error_details": err}, errors=[err], warnings=[],
                    metrics={"error_time": datetime.now().isoformat()}, created_at=start_time,
                    updated_at=datetime.now(), completed_at=datetime.now()
                ))

            # ENTERPRISE: Template validation
            if not template_config or not template_config.get("name"):
                err = "Invalid template configuration - LangGraph requires template specification"
                logger.error(f"{err} [request_id={request_id}]")
                return _persist_and_return(GenerationStatus(
                    request_id=request_id, status="failed", progress=0.0, current_step="Template Invalid",
                    content="", metadata={"error_details": err}, errors=[err], warnings=[],
                    metrics={"error_time": datetime.now().isoformat()}, created_at=start_time,
                    updated_at=datetime.now(), completed_at=datetime.now()
                ))

            # ENTERPRISE: Style validation
            if not style_config or not style_config.get("name"):
                err = "Invalid style configuration - LangGraph requires style specification"
                logger.error(f"{err} [request_id={request_id}]")
                return _persist_and_return(GenerationStatus(
                    request_id=request_id, status="failed", progress=0.0, current_step="Style Invalid",
                    content="", metadata={"error_details": err}, errors=[err], warnings=[],
                    metrics={"error_time": datetime.now().isoformat()}, created_at=start_time,
                    updated_at=datetime.now(), completed_at=datetime.now()
                ))

            # Execute LangGraph+MCP generation
            logger.info(f"Executing LangGraph+MCP generation [request_id={request_id}]")
            
            # Import the enhanced MCP integration
            from ..mcp_server_extension import execute_enhanced_mcp_generation
            
            result = await execute_enhanced_mcp_generation(
                request_id=request_id,
                template_config=template_config,
                style_config=style_config,
                app_state=app_state,
                mcp_options=mcp_options or {}
            )

            # Validate result
            if not isinstance(result, dict):
                err = "LangGraph generation returned invalid result structure"
                logger.error(f"{err} [request_id={request_id}]")
                return _persist_and_return(GenerationStatus(
                    request_id=request_id, status="failed", progress=0.0, current_step="Invalid Result",
                    content="", metadata={"error_details": err}, errors=[err], warnings=[],
                    metrics={"error_time": datetime.now().isoformat()}, created_at=start_time,
                    updated_at=datetime.now(), completed_at=datetime.now()
                ))

            # Extract status and content
            status_value = result.get("status", "failed")
            content_value = extract_content_from_langgraph_result(result)
            
            logger.info(f"Content extraction [request_id={request_id}]:")
            logger.info(f"   - Content length: {len(content_value)}")
            logger.info(f"   - Result keys: {list(result.keys())}")
            logger.info(f"   - Content preview: {content_value[:100]}..." if content_value else "   - No content extracted")

            # Validate content was generated
            if status_value == "completed" and not content_value:
                err = f"LangGraph agents completed but produced no content - check agent workflow execution"
                logger.error(f"{err} [request_id={request_id}]")

                debug_info = {
                    "result_keys": list(result.keys()),
                    "result_types": {k: type(v).__name__ for k, v in result.items()},
                    "extraction_strategies_tried": [
                        "direct_content", "final_output", "writer_output", "messages", 
                        "agent_state", "workflow_output", "mcp_results", "deep_search"
                    ],
                    "template_name": template_config.get("name"),
                    "style_name": style_config.get("name")
                }

                return _persist_and_return(GenerationStatus(
                    request_id=request_id, status="failed", progress=0.0, current_step="No Content Generated",
                    content="", metadata={"error_details": err, "debug_info": debug_info}, 
                    errors=[err], warnings=[], metrics={"error_time": datetime.now().isoformat()},
                    created_at=start_time, updated_at=datetime.now(), completed_at=datetime.now()
                ))

            # Validate progress
            progress_value = result.get("progress", 0.0)
            try:
                progress_value = float(progress_value)
                progress_value = max(0.0, min(1.0, progress_value))
            except Exception:
                progress_value = 0.0

            # Extract metadata and metrics
            metadata_value = result.get("metadata", {})
            errors_value = result.get("errors", [])
            warnings_value = result.get("warnings", [])
            metrics_value = result.get("metrics", {})

            # Evidence validation
            evidence_container = (
                result.get("mcp_results")
                or (getattr(app_state, "mcp_evidence_store", {}) or {}).get(request_id)
                or result
            )
            
            evidence_dict = evidence_container if isinstance(evidence_container, dict) else {}
            sources = extract_sources_from_langgraph_result(evidence_dict)
            source_count = len(sources)

            # Minimum evidence requirements
            min_sources_required = settings.EVIDENCE_CONFIG["minimum_required"]
            
            if source_count < min_sources_required:
                err = f"LangGraph agents failed to collect sufficient evidence (found {source_count}, required {min_sources_required})"
                logger.error(f"{err} [request_id={request_id}]")
                
                debug_info = {
                    "evidence_container_keys": list(evidence_dict.keys()),
                    "sources_found": sources,
                    "mcp_tools_executed": evidence_dict.get("mcp_tools_executed", []),
                    "agent_workflow_status": evidence_dict.get("workflow_status", "unknown")
                }
                
                return _persist_and_return(GenerationStatus(
                    request_id=request_id, status="failed", progress=0.0, current_step="Insufficient Evidence",
                    content="", metadata={"error_details": err, "debug_info": debug_info},
                    errors=[err], warnings=[], metrics={"min_sources": min_sources_required, "source_count": source_count},
                    created_at=start_time, updated_at=datetime.now(), completed_at=datetime.now()
                ))

            # Quality validation
            word_count = len(re.findall(r"\b\w+\b", content_value))
            min_words = 100  # Minimum for any real content
            
            # Check for template-specific requirements
            template_requirements = template_config.get("requirements", {})
            if "min_words" in template_requirements:
                try:
                    min_words = max(min_words, int(template_requirements["min_words"]))
                except:
                    pass
                    
            style_length = style_config.get("length_limit", {})
            if "min" in style_length:
                try:
                    min_words = max(min_words, int(style_length["min"]))
                except:
                    pass

            if word_count < min_words:
                err = f"Generated content too short (found {word_count} words, required {min_words})"
                logger.error(f"{err} [request_id={request_id}]")
                return _persist_and_return(GenerationStatus(
                    request_id=request_id, status="failed", progress=0.0, current_step="Quality Check Failed",
                    content="", metadata={"error_details": err},
                    errors=[err], warnings=[], metrics={"word_count": word_count, "min_words": min_words},
                    created_at=start_time, updated_at=datetime.now(), completed_at=datetime.now()
                ))

            # SUCCESS: Real content generated by LangGraph agents
            logger.info(f"LangGraph+MCP generation successful [request_id={request_id}, content_length={len(content_value)}, word_count={word_count}, sources={source_count}]")

            # Add LangGraph-specific metadata
            metadata_value.update({
                "generation_approach": "langgraph_mcp",
                "agent_workflow": "multi_agent",
                "mcp_tools_used": evidence_dict.get("mcp_tools_executed", []),
                "evidence_sources": source_count,
                "content_quality": {
                    "word_count": word_count,
                    "min_words_met": word_count >= min_words,
                    "evidence_sufficient": source_count >= min_sources_required
                }
            })

            status = GenerationStatus(
                request_id=request_id, status=status_value, progress=progress_value,
                current_step="Completed" if status_value == "completed" else "Processing",
                content=content_value, metadata=metadata_value, errors=errors_value,
                warnings=warnings_value, metrics=metrics_value,
                created_at=start_time, updated_at=datetime.now(),
                completed_at=datetime.now() if status_value in ["completed", "failed"] else None
            )
            return _persist_and_return(status)

        except Exception as e:
            logger.error(f"LangGraph+MCP generation failed [request_id={request_id}, error={str(e)}]", exc_info=True)
            return _persist_and_return(GenerationStatus(
                request_id=request_id, status="failed", progress=0.0, current_step="Exception",
                content="", metadata={"error_details": str(e)}, errors=[f"Generation failed: {str(e)}"],
                warnings=[], metrics={"error_time": datetime.now().isoformat()},
                created_at=start_time, updated_at=datetime.now(), completed_at=datetime.now()
            ))
    
    async def execute_universal_content_generation(
        self,
        request_id: str,
        user_request: str,
        template_id: Optional[str],
        style_profile: Optional[str],
        user_context: Optional[Dict[str, Any]],
        app_state
    ) -> GenerationStatus:
        """Execute Universal content generation with LangGraph agents."""
        start_time = datetime.now()
        
        try:
            # ENTERPRISE: Universal integration must be available
            if not hasattr(app_state, 'universal_integration') or not app_state.universal_integration:
                raise Exception("Universal integration not available - LangGraph workflow required")
            
            # STRICT: User request must be substantial
            if not user_request or len(user_request.strip()) < 10:
                raise Exception("User request too short - Universal system requires detailed specifications")
            
            # Use Universal Integration for intelligent template/style selection
            enhanced_context = user_context or {}
            if template_id:
                enhanced_context['template_preference'] = template_id
            if style_profile:
                enhanced_context['style_preference'] = style_profile
            
            # Execute Universal system processing
            logger.info(f"Universal system processing request [request_id={request_id}, request_length={len(user_request)}]")
            
            result = await app_state.universal_integration.process_content_request(
                user_request=user_request,
                user_context=enhanced_context
            )
            
            # STRICT: Validate Universal system response
            if not result or not isinstance(result, dict):
                raise Exception("Universal system returned invalid response")
            
            required_fields = ['template', 'style_profile', 'parameters']
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                raise Exception(f"Universal system response missing required fields: {missing_fields}")
            
            # Extract selections from Universal System
            template_yaml = result['template'].get('yaml_content', '')
            if not template_yaml:
                raise Exception("Universal system failed to generate template YAML")
                
            selected_style = result['style_profile']
            parameters = result['parameters']
            
            logger.info(f"Universal system selected: {selected_style}, domain: {result['template']['metadata'].get('topic_domain', 'dynamic')}")
            
            # Parse generated template with safe loading
            template_data = safe_yaml_load(template_yaml, f"universal_generation_{request_id}")
            template_data = validate_template_structure(template_data)
            
            template_config = {
                'name': template_data.get('name', f"Dynamic {result['template']['metadata'].get('topic_domain', 'Content')}"),
                'system_prompt': template_data.get('system_prompt', ''),
                'instructions': template_data.get('instructions', ''),
                **template_data
            }
            template_config.update(parameters)
            
            # Load style profile for MCP
            from ..core.content_manager import content_manager
            profiles = content_manager.load_style_profiles()
            profile = next((p for p in profiles if p.id == selected_style), None)
            if not profile:
                raise Exception(f"Style profile not found: {selected_style}")
            
            # Execute MCP generation with Universal selections
            logger.info(f"Executing Universal+LangGraph+MCP generation [request_id={request_id}]")
            
            mcp_result = await self.execute_content_generation(
                request_id, 
                template_config, 
                profile.dict(), 
                app_state, 
                {
                    'enable_mcp': True, 
                    'research_depth': 'comprehensive',
                    'universal_mode': True,
                    'template_source': 'universal_generated',
                    'dynamic_parameters': parameters
                }
            )
            
            # Validate result
            if not mcp_result or mcp_result.status == "failed":
                raise Exception(f"Universal+LangGraph+MCP generation failed: {mcp_result.errors if mcp_result else 'No result'}")
            
            # Add Universal metadata
            if hasattr(mcp_result, 'metadata'):
                mcp_result.metadata.update({
                    "generation_approach": "universal_langgraph_mcp",
                    "universal_template": result['template']['metadata'].get('topic_domain'),
                    "universal_style": selected_style,
                    "estimated_length": result['generation_info'].get('estimated_length', 'unknown'),
                    "template_dynamically_generated": True,
                    "no_fallbacks_used": True
                })
            
            logger.info(f"Universal+LangGraph+MCP generation successful [request_id={request_id}, content_length={len(mcp_result.content)}]")
            return mcp_result
            
        except Exception as e:
            logger.error(f"Universal+LangGraph+MCP generation failed: {e}")
            
            error_status = GenerationStatus(
                request_id=request_id,
                status="failed",
                progress=0.0,
                current_step="Universal Generation Failed",
                content="",
                metadata={"error_details": str(e), "no_fallbacks_attempted": True},
                errors=[f"Universal generation failed: {str(e)}"],
                warnings=[],
                metrics={},
                created_at=start_time,
                updated_at=datetime.now(),
                completed_at=datetime.now()
            )
            
            self.generation_tasks[request_id] = error_status
            
            # ENTERPRISE: Always fail fast, no fallbacks
            raise e
    
    async def execute_universal_content_generation(
        self,
        request_id: str,
        user_request: str,
        template_id: Optional[str],
        style_profile: Optional[str],
        user_context: Optional[Dict[str, Any]],
        app_state
    ) -> GenerationStatus:
        """Execute Universal content generation with LangGraph agents."""
        start_time = datetime.now()
        
        try:
            # ENTERPRISE: Universal integration must be available
            if not hasattr(app_state, 'universal_integration') or not app_state.universal_integration:
                raise Exception("Universal integration not available - LangGraph workflow required")
            
            # STRICT: User request must be substantial
            if not user_request or len(user_request.strip()) < 10:
                raise Exception("User request too short - Universal system requires detailed specifications")
            
            # Use Universal Integration for intelligent template/style selection
            enhanced_context = user_context or {}
            if template_id:
                enhanced_context['template_preference'] = template_id
            if style_profile:
                enhanced_context['style_preference'] = style_profile
            
            # Execute Universal system processing
            logger.info(f"Universal system processing request [request_id={request_id}, request_length={len(user_request)}]")
            
            result = await app_state.universal_integration.process_content_request(
                user_request=user_request,
                user_context=enhanced_context
            )
            
            # STRICT: Validate Universal system response
            if not result or not isinstance(result, dict):
                raise Exception("Universal system returned invalid response")
            
            required_fields = ['template', 'style_profile', 'parameters']
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                raise Exception(f"Universal system response missing required fields: {missing_fields}")
            
            # Extract selections from Universal System
            template_yaml = result['template'].get('yaml_content', '')
            if not template_yaml:
                raise Exception("Universal system failed to generate template YAML")
                
            selected_style = result['style_profile']
            parameters = result['parameters']
            
            logger.info(f"Universal system selected: {selected_style}, domain: {result['template']['metadata'].get('topic_domain', 'dynamic')}")
            
            # Parse generated template with safe loading            
            template_data = safe_yaml_load(template_yaml, f"universal_generation_{request_id}")
            template_data = validate_template_structure(template_data)
            
            template_config = {
                'name': template_data.get('name', f"Dynamic {result['template']['metadata'].get('topic_domain', 'Content')}"),
                'system_prompt': template_data.get('system_prompt', ''),
                'instructions': template_data.get('instructions', ''),
                **template_data
            }
            template_config.update(parameters)
            
            # Load style profile for MCP
            from ..core.content_manager import content_manager
            profiles = content_manager.load_style_profiles()
            profile = next((p for p in profiles if p.id == selected_style), None)
            if not profile:
                raise Exception(f"Style profile not found: {selected_style}")
            
            # Execute MCP generation with Universal selections
            logger.info(f"Executing Universal+LangGraph+MCP generation [request_id={request_id}]")
            
            mcp_result = await self.execute_content_generation(
                request_id, 
                template_config, 
                profile.dict(), 
                app_state, 
                {
                    'enable_mcp': True, 
                    'research_depth': 'comprehensive',
                    'universal_mode': True,
                    'template_source': 'universal_generated',
                    'dynamic_parameters': parameters
                }
            )
            
            # Validate result
            if not mcp_result or mcp_result.status == "failed":
                raise Exception(f"Universal+LangGraph+MCP generation failed: {mcp_result.errors if mcp_result else 'No result'}")
            
            # Add Universal metadata
            if hasattr(mcp_result, 'metadata'):
                mcp_result.metadata.update({
                    "generation_approach": "universal_langgraph_mcp",
                    "universal_template": result['template']['metadata'].get('topic_domain'),
                    "universal_style": selected_style,
                    "estimated_length": result['generation_info'].get('estimated_length', 'unknown'),
                    "template_dynamically_generated": True,
                    "no_fallbacks_used": True
                })
            
            logger.info(f"Universal+LangGraph+MCP generation successful [request_id={request_id}, content_length={len(mcp_result.content)}]")
            return mcp_result
            
        except Exception as e:
            logger.error(f"Universal+LangGraph+MCP generation failed: {e}")
            
            error_status = GenerationStatus(
                request_id=request_id,
                status="failed",
                progress=0.0,
                current_step="Universal Generation Failed",
                content="",
                metadata={"error_details": str(e), "no_fallbacks_attempted": True},
                errors=[f"Universal generation failed: {str(e)}"],
                warnings=[],
                metrics={},
                created_at=start_time,
                updated_at=datetime.now(),
                completed_at=datetime.now()
            )
            
            self.generation_tasks[request_id] = error_status
            
            # ENTERPRISE: Always fail fast, no fallbacks
            raise e
    
    def get_generation_status(self, request_id: str) -> Optional[GenerationStatus]:
        """Get generation status by request ID."""
        return self.generation_tasks.get(request_id)
    
    def update_generation_status(self, request_id: str, status: GenerationStatus):
        """Update generation status."""
        self.generation_tasks[request_id] = status
    
    def cancel_generation(self, request_id: str) -> bool:
        """Cancel an ongoing generation."""
        if request_id in self.generation_tasks:
            status = self.generation_tasks[request_id]
            if status.status not in ["completed", "failed"]:
                status.status = "cancelled"
                status.updated_at = datetime.now()
                status.completed_at = datetime.now()
                self.generation_tasks[request_id] = status
                return True
        return False
    
    def clear_completed_tasks(self) -> int:
        """Clear completed generation tasks from memory."""
        completed_statuses = ['completed', 'failed', 'cancelled']
        completed_tasks = [
            request_id for request_id, status in self.generation_tasks.items()
            if status.status in completed_statuses
        ]
        
        for request_id in completed_tasks:
            del self.generation_tasks[request_id]
        
        return len(completed_tasks)
    
    def get_active_generations(self) -> Dict[str, GenerationStatus]:
        """Get all active (non-completed) generations."""
        active_statuses = ['pending', 'processing']
        return {
            request_id: status for request_id, status in self.generation_tasks.items()
            if status.status in active_statuses
        }
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        total = len(self.generation_tasks)
        by_status = {}
        
        for status in self.generation_tasks.values():
            status_key = status.status
            by_status[status_key] = by_status.get(status_key, 0) + 1
        
        return {
            "total_generations": total,
            "by_status": by_status,
            "active_count": len(self.get_active_generations()),
            "cache_size": total
        }

# Global generation engine instance
generation_engine = GenerationEngine()