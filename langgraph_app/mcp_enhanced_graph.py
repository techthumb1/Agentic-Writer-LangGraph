# File: langgraph_app/mcp_enhanced_graph.py
"""
MCP Enhanced Graph (Object-Only) - Fixed State Normalization
FIXED: Preserve template_config and style_config during state normalization
"""

from __future__ import annotations
import copy
import json
import logging
from typing import Dict, Any, Optional, Tuple, Union
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph_app.agents.enhanced_editor_integrated import EnhancedEditorAgent
from langgraph_app.core.enriched_content_state import ContentSpec, ContentPhase
from langgraph_app.style_profile_loader import get_dynamic_style_profile_loader
from langgraph_app.template_loader import get_template_loader

from langgraph_app.core.enriched_content_state import (
    EnrichedContentState,
    ContentSpec,
    AgentType,
    ContentPhase,
)

# Define GenerationStatus enum
from enum import Enum


# In mcp_enhanced_graph.py or studio config
studio_input_schema = {
    "type": "object",
    "properties": {
        "topic": {"type": "string", "required": True},
        "template_id": {"type": "string", "required": True},
        "style_profile_id": {"type": "string", "required": True}
    }
}

class GenerationStatus(Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class MCPEnhancedContentGraph:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) if hasattr(super(), "__init__") else None
        # Initialize agents to None - create on-demand
        self._load_agents()
        self.graph = None
        self.execution_metrics: Dict[str, Any] = {}
        self._initialize_graph()

    def _load_agents(self) -> None:
        """Initialize agent references to None - create on-demand in nodes"""
        self.planner_agent = None
        self.researcher_agent = None
        self.call_writer_agent = None
        self.writer_agent = None
        self.editor_agent = None
        self.formatter_agent = None
        self.seo_agent = None
        self.publisher_agent = None
        self.image_agent = None
        # Code agent removed

    def _initialize_graph(self) -> None:
        """Initialize the StateGraph with EnrichedContentState"""
        workflow: StateGraph = StateGraph(EnrichedContentState)

        # Register nodes (code agent removed)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("call_writer", self._call_writer_node)
        workflow.add_node("writer", self._writer_node)
        workflow.add_node("editor", self._editor_node)
        workflow.add_node("image", self._image_node)
        workflow.add_node("formatter", self._formatter_node)
        workflow.add_node("seo", self._seo_node)
        workflow.add_node("publisher", self._publisher_node)

        # Entry and main sequence
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "call_writer")
        workflow.add_edge("call_writer", "writer")
        workflow.add_edge("writer", "editor")
        workflow.add_edge("editor", "image")
        workflow.add_edge("image", "formatter")

        # Simplified conditional branches (code paths removed)
        workflow.add_conditional_edges(
            "formatter",
            self._determine_specialized_agents,
            {
                "seo_only": "seo",
                "publisher": "publisher",
            },
        )

        # Direct flow without code agent
        workflow.add_edge("seo", "publisher")
        workflow.add_edge("publisher", END)

        self.graph = workflow.compile()
        logger.info("MCP Enhanced Content Graph initialized without code agent")
    # ----------------------------- Nodes with On-Demand Creation -------------
    
    # File: langgraph_app/mcp_enhanced_graph.py
    # Replace _planner_node method

    def _planner_node(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute planner agent with strict template validation - NO FALLBACKS"""

        # ENTERPRISE: Validate template_config exists
        if not hasattr(state, 'template_config') or not isinstance(state.template_config, dict) or not state.template_config:
            raise RuntimeError(
                "ENTERPRISE: template_config required in state. "
                "Studio must provide valid template selection."
            )

        # ENTERPRISE: Validate template_id
        template_id = state.template_config.get('id') or state.template_config.get('slug')
        if not template_id or template_id in ['default', 'studio_fallback', 'studio_generated']:
            from langgraph_app.template_loader import get_template_loader
            available = get_template_loader().list_templates()
            raise RuntimeError(
                f"ENTERPRISE: Invalid template_id '{template_id}'. "
                f"Must be one of: {available}"
            )

        # ENTERPRISE: Validate style_config exists
        if not hasattr(state, 'style_config') or not isinstance(state.style_config, dict) or not state.style_config:
            raise RuntimeError(
                "ENTERPRISE: style_config required in state. "
                "Studio must provide valid style profile."
            )

        # Create planner agent
        if self.planner_agent is None:
            from .agents.enhanced_planner_integrated import EnhancedPlannerAgent
            self.planner_agent = EnhancedPlannerAgent()
            logger.info("Created planner agent on-demand")

        # Execute with validated configs
        result = self.planner_agent.execute(state)
        self._calculate_overall_confidence(result)
        return result   
    
    def _researcher_node(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute researcher agent with on-demand creation"""
        self._require_state(state)
        
        if self.researcher_agent is None:
            try:
                from .agents.enhanced_researcher_integrated import EnhancedResearcherAgent
                self.researcher_agent = EnhancedResearcherAgent()
                logger.info("Created researcher agent on-demand")
            except Exception as e:
                raise RuntimeError(f"Researcher Agent creation failed: {e}")
        
        try:
            result = self.researcher_agent.execute(state)
            self._calculate_overall_confidence(result)
            return result
        except Exception as e:
            logger.error(f"Researcher execution failed: {e}")
            raise RuntimeError(f"Researcher execution failed: {e}")

    def _call_writer_node(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute call writer agent with on-demand creation"""
        self._require_state(state)
        
        if self.call_writer_agent is None:
            try:
                from .agents.enhanced_call_writer_integrated import EnhancedCallWriterAgent
                self.call_writer_agent = EnhancedCallWriterAgent()
                logger.info("Created call writer agent on-demand")
            except Exception as e:
                raise RuntimeError(f"Call Writer Agent creation failed: {e}")
        
        try:
            result = self.call_writer_agent.execute(state)
            self._calculate_overall_confidence(result)
            return result
        except Exception as e:
            logger.error(f"Call Writer execution failed: {e}")
            raise RuntimeError(f"Call Writer execution failed: {e}")

    def _get_editor_agent(self):
        # Prefer existing instance; otherwise create and cache one
        if getattr(self, "editor_agent", None) is None:
            from langgraph_app.agents.enhanced_editor_integrated import EnhancedEditorAgent
            self.editor_agent = EnhancedEditorAgent()
        return self.editor_agent

    def _image_node(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute image agent with template-aware triggering - FIXED"""
        self._require_state(state)

        # FIXED: Extract template information for decision making
        template_id = state.template_config.get('id', '') if state.template_config else ''
        template_type = state.template_config.get('template_type', '') if state.template_config else ''

        # CRITICAL FIX: Use template loader to determine image generation
        from langgraph_app.template_loader import should_include_image_agent
        should_generate_images = should_include_image_agent(template_id)

        # ADDITIONAL CHECK: Template type-based decision
        visual_content_types = {'blog_article', 'social_media', 'press_release', 'content_marketing', 'product_launch'}
        type_based_decision = template_type in visual_content_types

        # FINAL DECISION: Either template loader OR type-based
        final_decision = should_generate_images or type_based_decision

        logger.info(f"IMAGE AGENT DECISION: template_id='{template_id}', type='{template_type}'")
        logger.info(f"IMAGE AGENT: loader_decision={should_generate_images}, type_decision={type_based_decision}, final={final_decision}")

        if not final_decision:
            logger.info(f"IMAGE AGENT: Skipping image generation for {template_id} ({template_type})")
            # Set image status for downstream agents
            if not hasattr(state, 'image_generation_status'):
                state.image_generation_status = 'skipped'
            return state

        # PROCEED WITH IMAGE GENERATION
        if self.image_agent is None:
            try:
                from .agents.enhanced_image_agent_integrated import EnhancedImageAgent
                self.image_agent = EnhancedImageAgent()
                logger.info("IMAGE AGENT: Created image agent on-demand")
            except Exception as e:
                logger.warning(f"IMAGE AGENT: Creation failed, skipping: {e}")
                if not hasattr(state, 'image_generation_status'):
                    state.image_generation_status = 'failed_creation'
                return state

        try:
            logger.info(f"IMAGE AGENT: Executing for {template_type} content (template: {template_id})")

            # Ensure content exists for image generation
            content_for_images = (
                getattr(state, 'edited_content', '') or 
                getattr(state, 'content', '') or 
                getattr(state, 'draft_content', '') or
                ''
            )

            if not content_for_images or len(content_for_images.strip()) < 100:
                logger.warning("IMAGE AGENT: Insufficient content for image generation")
                if not hasattr(state, 'image_generation_status'):
                    state.image_generation_status = 'insufficient_content'
                return state

            result = self.image_agent.execute(state)
            self._calculate_overall_confidence(result)

            # Mark successful image generation
            if not hasattr(result, 'image_generation_status'):
                result.image_generation_status = 'completed'

            logger.info(f"IMAGE AGENT: Successfully completed for {template_type}")
            return result

        except Exception as e:
            logger.warning(f"IMAGE AGENT: Execution failed for {template_id}: {e}")
            # Continue pipeline but mark image generation as failed
            if not hasattr(state, 'image_generation_status'):
                state.image_generation_status = 'failed_execution'
            return state

    def _writer_node(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute simplified writer agent - no blocking validation"""
        self._require_state(state)

        # Create writer agent on-demand
        if self.writer_agent is None:
            try:
                from .agents.writer import WriterAgent
                self.writer_agent = WriterAgent()
                logger.info("Created simplified writer agent on-demand")
            except Exception as e:
                raise RuntimeError(f"Writer Agent creation failed: {e}")

        try:
            # Execute simplified writer
            result = self.writer_agent.execute(state)
            self._calculate_overall_confidence(result)

            logger.info(f"Writer completed successfully: {len(result.content)} characters")
            return result

        except Exception as e:
            logger.error(f"Writer execution failed: {e}")
            raise RuntimeError(f"Writer execution failed: {e}")


    def _editor_node(self, state):
        try:
            for key in ("edited_content", "content", "draft_content"):
                v = getattr(state, key, None)
                if isinstance(v, dict):
                    cand = v.get("draft") or v.get("content") or v.get("text") or v.get("body")
                    if isinstance(cand, str):
                        setattr(state, key, cand)

            editor_agent = self._get_editor_agent()
            return editor_agent.execute(state)

        except Exception as e:
            raise RuntimeError(f"Editor execution failed: {e}")



    def _formatter_node(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute formatter agent with on-demand creation"""
        self._require_state(state)
        
        if self.formatter_agent is None:
            try:
                from .agents.enhanced_formatter_integrated import EnhancedFormatterAgent
                self.formatter_agent = EnhancedFormatterAgent()
                logger.info("Created formatter agent on-demand")
            except Exception as e:
                raise RuntimeError(f"Formatter Agent creation failed: {e}")
        
        try:
            result = self.formatter_agent.execute(state)
            self._calculate_overall_confidence(result)
            return result
        except Exception as e:
            logger.error(f"Formatter execution failed: {e}")
            raise RuntimeError(f"Formatter execution failed: {e}")

    def _seo_node(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute SEO agent with on-demand creation"""
        self._require_state(state)
        
        if self.seo_agent is None:
            try:
                from .agents.enhanced_seo_agent_integrated import EnhancedSeoAgent
                self.seo_agent = EnhancedSeoAgent()
                logger.info("Created SEO agent on-demand")
            except Exception as e:
                logger.warning(f"SEO agent unavailable, skipping: {e}")
                return state
        
        try:
            result = self.seo_agent.execute(state)
            self._calculate_overall_confidence(result)
            return result
        except Exception as e:
            logger.warning(f"SEO execution failed, continuing: {e}")
            return state

    def _code_node(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute code agent with on-demand creation (optional)"""
        self._require_state(state)
        
        if self.code_agent is None:
            try:
                from .agents.enhanced_code_agent_integrated import EnhancedCodeAgent
                self.code_agent = EnhancedCodeAgent()
                logger.info("Created code agent on-demand")
            except Exception as e:
                logger.info(f"Code agent unavailable, skipping: {e}")
                return state
        
        try:
            result = self.code_agent.execute(state)
            self._calculate_overall_confidence(result)
            return result
        except Exception as e:
            logger.warning(f"Code execution failed, continuing: {e}")
            return state
    
    def _publisher_node(self, state: EnrichedContentState) -> EnrichedContentState:
        logger.info("Publisher Executing Publisher Agent")

        try:
            # Always import+instantiate fresh to avoid stale class definitions on reload
            from .agents.enhanced_publisher_integrated import EnhancedPublisherAgent
            publisher = EnhancedPublisherAgent()

            # Contract checks (fail fast)
            if not hasattr(publisher, "_set_engagement_expectations"):
                raise RuntimeError("EnhancedPublisherAgent missing required method: _set_engagement_expectations")
            if not hasattr(publisher, "execute"):
                raise RuntimeError("EnhancedPublisherAgent missing required method: execute")

            result = publisher.execute(state)
            if result is None:
                raise RuntimeError("Publisher returned no result")
            if not isinstance(result, EnrichedContentState):
                raise RuntimeError("Publisher must return EnrichedContentState")

            # CRITICAL FIX: Ensure content_spec exists before other operations
            if not hasattr(result, 'content_spec') or not result.content_spec:
                logger.warning("Restoring missing content_spec from template_config")
                result.content_spec = ContentSpec(
                    topic=result.template_config.get("dynamic_overrequest_ides", {}).get("topic", "General Content"),
                    template_id=result.template_config.get("id", "default"),
                    target_audience=result.template_config.get("dynamic_overrequest_ides", {}).get("target_audience", "general"),
                    template_type=result.template_config.get("template_type", "article")
                )

            # State contract checks
            if not hasattr(result, "update_phase"):
                raise RuntimeError("EnrichedContentState missing update_phase")
            if not hasattr(result, "log_agent_execution"):
                raise RuntimeError("EnrichedContentState missing log_agent_execution")

            # Mark complete and log success
            result.update_phase(ContentPhase.COMPLETED)
            result.log_agent_execution(AgentType.PUBLISHER, {
                "status": "completed",
                "publication_ready": True
            })

            # Ensure final status
            result.status = GenerationStatus.COMPLETED
            result.completion_time = datetime.now().isoformat()

            logger.info("Publisher Agent completed - Content generation finished!")
            return result

        except Exception as e:
            logger.error(f"Publisher Agent failed: {e}")
            # Best-effort logging into state (no graph-level logger calls)
            try:
                if hasattr(state, "log_agent_execution"):
                    state.log_agent_execution(AgentType.PUBLISHER, {
                        "status": "failed",
                        "error": str(e)
                    })
            except Exception:
                pass  # do not mask the original failure
            raise RuntimeError(f"Publisher execution failed: {e}")

    # File: langgraph_app/mcp_enhanced_graph.py
    # Replace _normalize_initial_state method (lines ~265-337)

    # File: langgraph_app/mcp_enhanced_graph.py
    # Replace _normalize_initial_state method (lines ~265-337)

    def _normalize_initial_state(self, initial_state: Union[Dict, EnrichedContentState]) -> EnrichedContentState:
        """FIXED: Load template/style configs from IDs when not provided"""

        logger.info(f"DEBUG: _normalize_initial_state called with type: {type(initial_state)}")

        # 1) Already EnrichedContentState - preserve everything
        if isinstance(initial_state, EnrichedContentState):
            self._validate_state(initial_state)
            return initial_state

        # 2) Handle dict input (LangGraph Studio format)
        if not isinstance(initial_state, dict):
            raise TypeError("Initial state must be EnrichedContentState or dict")

        logger.info(f"DEBUG: Input dict keys: {list(initial_state.keys())}")

        # Extract from nested "input" wrapper if present
        working_data = initial_state.get("input", initial_state)
        logger.info(f"DEBUG: Working data keys: {list(working_data.keys())}")

        # CRITICAL FIX: Load configs from IDs if not provided as objects
        template_config = working_data.get("template_config")
        style_config = working_data.get("style_config")

        # STUDIO COMPATIBILITY: Load from IDs when configs not provided
        if not template_config or not isinstance(template_config, dict):
            template_id = working_data.get("template_id")
            if not template_id:
                raise ValueError(
                    "ENTERPRISE: Must provide either 'template_config' object or 'template_id'. "
                    f"Received keys: {list(working_data.keys())}"
                )

            # Load template from ID
            template_loader = get_template_loader()
            template_config = template_loader.load_template(template_id)
            if not template_config:
                available = template_loader.list_templates()
                raise ValueError(
                    f"ENTERPRISE: Invalid template_id '{template_id}'. "
                    f"Available: {available}"
                )
            logger.info(f"DEBUG: Loaded template_config from ID: {template_id}")

        if not style_config or not isinstance(style_config, dict):
            style_profile_id = working_data.get("style_profile_id")
            if not style_profile_id:
                raise ValueError(
                    "ENTERPRISE: Must provide either 'style_config' object or 'style_profile_id'. "
                    f"Received keys: {list(working_data.keys())}"
                )

            # Load style from ID
            style_loader = get_dynamic_style_profile_loader()
            style_config = style_loader.load_profile(style_profile_id)
            if not style_config:
                available = style_loader.list_profiles()
                raise ValueError(
                    f"ENTERPRISE: Invalid style_profile_id '{style_profile_id}'. "
                    f"Available: {available}"
                )
            logger.info(f"DEBUG: Loaded style_config from ID: {style_profile_id}")

        # Extract topic from multiple possible locations
        topic = None

        # Path 1: Top-level topic
        topic = working_data.get("topic")

        # Path 2: content_spec.topic (when state is reused)
        if not topic:
            content_spec_data = working_data.get("content_spec", {})
            if hasattr(content_spec_data, 'topic'):
                topic = content_spec_data.topic
            elif isinstance(content_spec_data, dict):
                topic = content_spec_data.get("topic")

        # Path 3: template_config.dynamic_overrides
        if not topic:
            dynamic_overrides = template_config.get("dynamic_overrides", {})
            if isinstance(dynamic_overrides, dict):
                topic = dynamic_overrides.get("topic")
                # Handle nested dynamic_overrides
                if not topic and "dynamic_overrides" in dynamic_overrides:
                    topic = dynamic_overrides["dynamic_overrides"].get("topic")

        # Path 4: dynamic_parameters (common in internal state)
        if not topic:
            dynamic_params = working_data.get("dynamic_parameters", {})
            if isinstance(dynamic_params, dict):
                topic = dynamic_params.get("topic")

        if not topic or not isinstance(topic, str) or not topic.strip():
            raise ValueError(
                "ENTERPRISE: 'topic' required. Searched: working_data['topic'], "
                f"content_spec.topic, template_config.dynamic_overrides.topic. "
                f"Available keys: {list(working_data.keys())}"
            )

        # Build ContentSpec
        content_spec = ContentSpec(
            topic=topic.strip(),
            template_id=template_config.get("id", "unknown"),
            template_type=template_config.get("template_type", "article"),
            platform=working_data.get("platform", "web"),
            target_audience=working_data.get("target_audience", "general")
        )

        # Create EnrichedContentState
        state = EnrichedContentState(
            content_spec=content_spec,
            template_config=copy.deepcopy(template_config),
            style_config=copy.deepcopy(style_config),
            request_id=working_data.get("request_id"),
            current_agent="start"
        )

        # Set initial phase
        state.update_phase(ContentPhase.PLANNING)

        # FINAL VALIDATION
        if not state.template_config or not state.template_config.get("id"):
            raise ValueError("CRITICAL: template_config validation failed after normalization")

        if not state.content_spec.topic.strip():
            raise ValueError("CRITICAL: content_spec.topic is empty after normalization")

        logger.info(f"DEBUG: Successfully normalized state - topic: '{state.content_spec.topic}'")
        return state    

    #### Emergency recovery method (not used in current flow. Fallback) ####
#    def _build_minimal_configs(self, topic: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
#        """Build minimal template and style configs when missing - emergency recovery"""
#        
#        template_config = {
#            "id": "emergency_template",
#            "slug": "emergency-template",
#            "name": f"Emergency Template for {topic}",
#            "template_type": "article",
#            "structure": {
#                "sections": ["Introduction", "Main Content", "Conclusion"],
#                "format": "markdown"
#            },
#            "research": {},
#            "parameters": {},
#            "defaults": {
#                "template_type": "article",
#                "target_audience": "general"
#            },
#            "distribution_channels": ["web"],
#            "generation_mode": "standard",
#            "platform": "web",
#            "dynamic_overrides": {
#                "topic": topic,
#                "target_audience": "general audience"
#            },
#            "_fingerprint": "emergency_recovery"
#        }
#        
#        style_config = {
#            "id": "emergency_style",
#            "name": "Emergency Professional Style",
#            "category": "professional",
#            "platform": "web",
#            "tone": "professional",
#            "voice": "authoritative",
#            "structure": "standard",
#            "audience": "general",
#            "length_limit": {},
#            "settings": {
#                "formality": "professional",
#                "complexity": "medium"
#            },
#            "formatting": {
#                "style": "markdown",
#                "structure": "sections"
#            },
#            "system_prompt": f"You are a professional content writer creating high-quality content about {topic} for a general audience. Write in a clear, authoritative, and engaging style.",
#            "_filename": "emergency_recovery"
#        }
#        
#        logger.warning(f"Emergency recovery: built minimal configs for topic '{topic}'")
#        return template_config, style_config

    def _determine_specialized_agents(self, state: EnrichedContentState) -> str:
        self._require_state(state)
        spec = state.content_spec
        
        template_type = str(spec.template_type or "").lower()
        topic = str(spec.topic or "").lower()
        
        needs_code = any(word in template_type + " " + topic for word in 
                        ['api', 'code', 'technical', 'programming', 'development'])
        
        # Force SEO always, ignore code
        return "seo_only"


    # ----------------------------- Public API --------------------------------
    async def execute_coordinated_generation(
        self,
        initial_state: EnrichedContentState | Dict[str, Any],
        mcp_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        logger.info(f"DEBUG: Received state type: {type(initial_state)}")
        start_ts = datetime.now()
        state_obj = self._normalize_initial_state(initial_state)

        logger.info(f"DEBUG: After normalization template_config: {bool(getattr(state_obj, 'template_config', None))}")
        if mcp_options:
            if isinstance(mcp_options, dict):
                setattr(state_obj, "mcp_context", mcp_options)
            else:
                setattr(state_obj, "mcp_context", {})

        config = {"configurable": {"thread_id": "mcp_generation"}}

        try:
            result_state = await self.graph.ainvoke(state_obj, config=config)
            
            # CRITICAL FIX: Extract content from AddableValuesDict FIRST
            extracted_content = ""
            if hasattr(result_state, '__getitem__'):  # AddableValuesDict
                # Extract content before any conversion
                extracted_content = (
                    result_state.get('content') or 
                    result_state.get('final_content') or 
                    result_state.get('draft_content') or
                    ""
                )
                logger.info(f"DEBUG: Extracted content from AddableValuesDict: {len(extracted_content)} chars")
            
            # Convert AddableValuesDict back to EnrichedContentState if needed
            if not hasattr(result_state, 'content_spec'):
                logger.info(f"DEBUG: Converting {type(result_state)} back to EnrichedContentState")
                state_dict = dict(result_state)
                # PRESERVE the extracted content during conversion
                if extracted_content:
                    state_dict['content'] = extracted_content
                result_state = self._normalize_initial_state(state_dict)
            
            
            # ENTERPRISE: Fail fast if required attributes missing
            if not hasattr(result_state, 'content_spec'):
                raise RuntimeError("ENTERPRISE: result_state missing required content_spec attribute")
            
            spec = result_state.content_spec
            if not spec:
                raise RuntimeError("ENTERPRISE: result_state.content_spec is None or empty")
            
            # CRITICAL FIX: Use extracted content as primary source
            final_content = extracted_content
            
            if not final_content:
                # Log available fields for debugging
                available_fields = [attr for attr in dir(result_state) if not attr.startswith('_')]
                logger.error(f"ENTERPRISE: No content found in fields: {available_fields}")
                raise RuntimeError("ENTERPRISE: No content generated - all content fields missing or empty")
            
            # Validate content is substantial
            if not isinstance(final_content, str) or len(final_content.strip()) < 50:
                raise RuntimeError(f"ENTERPRISE: Generated content insufficient: {len(str(final_content))} chars")
            
            logger.info(f"DEBUG: Successfully extracted content: {len(final_content)} characters")
            
            # Build return structure with guaranteed content
            return {
                "status": "completed",
                "content": final_content,  # Use the extracted content
                "final_content": final_content,  # Backup location
                "metadata": {
                    "topic": getattr(spec, 'topic', 'Unknown Topic'),
                    "template_type": getattr(spec, 'template_type', 'article'),
                    "audience": getattr(spec, 'target_audience', 'general'),
                    "platform": getattr(spec, 'platform', 'web'),
                    "generation_time": datetime.now().isoformat(),
                    "content_length": len(final_content),
                    "content_words": len(final_content.split()),
                },
                "errors": [],
                "warnings": [],
                "metrics": {
                    "total_execution_time": (datetime.now() - start_ts).total_seconds(),
                },
                "progress": 1.0,
            }

        except Exception as e:
            logger.error(f"MCP coordinated generation failed: {e}")
            raise RuntimeError(f"ENTERPRISE: Generation pipeline failed - {str(e)}")
   
    # ----------------------------- Helpers -----------------------------------

    def _calculate_overall_confidence(self, state: EnrichedContentState) -> None:
        self._require_state(state)
        log = getattr(state, "agent_execution_log", []) or []

        confidences = []
        for entry in log:
            if isinstance(entry, dict):
                c = entry.get("confidence")
                if isinstance(c, (int, float)):
                    confidences.append(float(c))

        if not confidences and getattr(state, "planning_output", None):
            c = getattr(state.planning_output, "planning_confidence", None)
            if isinstance(c, (int, float)):
                confidences.append(float(c))

        overall = (sum(confidences) / len(confidences)) if confidences else 0.75
        setattr(state, "overall_confidence", round(overall, 3))



    def _validate_state(self, state: EnrichedContentState) -> None:
        """Validate state structure"""
        self._require_state(state)
        spec = getattr(state, "content_spec", None)
        if spec is None:
            raise AttributeError("state.content_spec is required")
            
        required = ("topic", "template_type", "target_audience", "platform")
        missing = [r for r in required if not getattr(spec, r, None)]
        if missing:
            raise AttributeError(f"content_spec missing required fields: {missing}")

    @staticmethod
    def _require_state(state: EnrichedContentState) -> None:
        if not isinstance(state, EnrichedContentState):
            raise TypeError("Graph expects EnrichedContentState throughout")

    def get_execution_metrics(self) -> Dict[str, Any]:
        return dict(self.execution_metrics)

    async def finalize_content(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure content is properly stored in final state"""
        if isinstance(state, dict) and "content" in state and state["content"]:
            # Store content in multiple locations for retrieval
            final_content = state["content"]

            return {
                **state,
                "content": final_content,
                "final_content": final_content,  # Backup location
                "status": GenerationStatus.COMPLETED.value,
                "completion_time": datetime.now().isoformat(),
                "content_length": len(final_content),
                "generation_successful": True
            }

        logger.error(f"No content found in final state. Keys: {list(state.keys())}")
        return {
            **state,
            "status": GenerationStatus.FAILED.value,
            "errors": ["Content generation failed - no content produced"],
            "generation_successful": False
        }

__all__ = ["MCPEnhancedContentGraph"]
