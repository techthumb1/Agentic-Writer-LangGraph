# File: langgraph_app/mcp_enhanced_graph.py
"""
MCP Enhanced Graph (Object-Only) - Fixed State Normalization
FIXED: Preserve template_config and style_config during state normalization
"""

from __future__ import annotations
import copy
import json
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph_app.agents.enhanced_editor_integrated import EnhancedEditorAgent
from langgraph_app.core.enriched_content_state import ContentSpec, ContentPhase

from langgraph_app.core.enriched_content_state import (
    EnrichedContentState,
    ContentSpec,
    AgentType,
    ContentPhase,
)

# Define GenerationStatus enum
from enum import Enum

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
        self.code_agent = None

    def _initialize_graph(self) -> None:
        """Initialize the StateGraph with EnrichedContentState"""
        workflow: StateGraph = StateGraph(EnrichedContentState)

        # Register nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("call_writer", self._call_writer_node)
        workflow.add_node("writer", self._writer_node)
        workflow.add_node("editor", self._editor_node)
        workflow.add_node("formatter", self._formatter_node)
        workflow.add_node("seo", self._seo_node)
        workflow.add_node("code", self._code_node)
        workflow.add_node("publisher", self._publisher_node)

        # Entry and main sequence
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "call_writer")
        workflow.add_edge("call_writer", "writer")
        workflow.add_edge("writer", "editor")
        workflow.add_edge("editor", "formatter")

        # Conditional branches
        workflow.add_conditional_edges(
            "formatter",
            self._determine_specialized_agents,
            {
                "seo_only": "seo",
                "code_only": "code",
                "seo_code": "seo",
                "publisher": "publisher",
            },
        )

        workflow.add_edge("seo", "code")
        workflow.add_edge("code", "publisher")
        workflow.add_edge("publisher", END)

        self.graph = workflow.compile()
        logger.info("MCP Enhanced Content Graph initialized (object-only state)")

    def _planner_node(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute planner agent with template_config validation"""
    
        logger.info(f"PLANNER DEBUG: Input state type: {type(state)}")
        logger.info(f"PLANNER DEBUG: Has template_config: {hasattr(state, 'template_config')}")
    
        if hasattr(state, 'template_config'):
            logger.info(f"PLANNER DEBUG: template_config type: {type(state.template_config)}")
            logger.info(f"PLANNER DEBUG: template_config keys: {list(state.template_config.keys()) if isinstance(state.template_config, dict) else 'NOT_DICT'}")
    
        # ENTERPRISE VALIDATION: template_config must exist and be non-empty
        if not hasattr(state, 'template_config') or not isinstance(state.template_config, dict) or not state.template_config:
            raise RuntimeError("ENTERPRISE ERROR: template_config missing/empty at planner entry - cannot proceed")
    
        # ENTERPRISE VALIDATION: style_config must exist and be non-empty  
        if not hasattr(state, 'style_config') or not isinstance(state.style_config, dict) or not state.style_config:
            raise RuntimeError("ENTERPRISE ERROR: style_config missing/empty at planner entry - cannot proceed")
    
        logger.info(f"PLANNER DEBUG: Validated template_config with {len(state.template_config)} keys")
    
        if self.planner_agent is None:
            try:
                from .agents.enhanced_planner_integrated import EnhancedPlannerAgent
                self.planner_agent = EnhancedPlannerAgent()
                logger.info("Created planner agent on-demand")
            except Exception as e:
                raise RuntimeError(f"Planner Agent creation failed: {e}")
    
        try:
            result = self.planner_agent.execute(state)
            self._calculate_overall_confidence(result)
    
            # VERIFY: Ensure template_config preserved after execution
            if not hasattr(result, 'template_config') or not result.template_config:
                raise RuntimeError("CRITICAL: template_config lost during planner execution")
    
            logger.info(f"PLANNER DEBUG: Execution completed, template_config preserved: {len(result.template_config)} keys")
            return result
    
        except Exception as e:
            logger.error(f"Planner execution failed: {e}")
            raise RuntimeError(f"Planner execution failed: {e}")

    # ----------------------------- Nodes with On-Demand Creation -------------
    def _researcher_node(self, state: EnrichedContentState) -> EnrichedContentState:
        state = self._preserve_enterprise_state(state)
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
        state = self._preserve_enterprise_state(state)
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

    def _writer_node(self, state: EnrichedContentState) -> EnrichedContentState:
        state = self._preserve_enterprise_state(state)
        self._require_state(state)

        if self.writer_agent is None:
            try:
                from .agents.writer import TemplateAwareWriterAgent
                self.writer_agent = TemplateAwareWriterAgent()
                logger.info("Created writer agent on-demand")
            except Exception as e:
                raise RuntimeError(f"Writer Agent creation failed: {e}")

        try:
            result = self.writer_agent.execute(state)
            self._calculate_overall_confidence(result)
            return result
        except Exception as e:
            logger.error(f"Writer execution failed: {e}")
            raise RuntimeError(f"Writer execution failed: {e}")

    def _editor_node(self, state):
        state = self._preserve_enterprise_state(state)
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
        state = self._preserve_enterprise_state(state)
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
        state = self._preserve_enterprise_state(state)
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
        state = self._preserve_enterprise_state(state)
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
        state = self._preserve_enterprise_state(state)
        logger.info("Publisher Executing Publisher Agent")

        try:
            from .agents.enhanced_publisher_integrated import EnhancedPublisherAgent
            publisher = EnhancedPublisherAgent()

            result = publisher.execute(state)
            if result is None:
                raise RuntimeError("Publisher returned no result")
            if not isinstance(result, EnrichedContentState):
                raise RuntimeError("Publisher must return EnrichedContentState")

            result.update_phase(ContentPhase.COMPLETED)
            result.log_agent_execution(AgentType.PUBLISHER, {
                "status": "completed",
                "publication_ready": True
            })

            result.status = GenerationStatus.COMPLETED
            result.completion_time = datetime.now().isoformat()

            logger.info("Publisher Agent completed - Content generation finished!")
            return result

        except Exception as e:
            logger.error(f"Publisher Agent failed: {e}")
            raise RuntimeError(f"Publisher execution failed: {e}")    
    
    def _preserve_enterprise_state(self, state: EnrichedContentState) -> EnrichedContentState:
        """Ensure template_config and style_config are preserved across agent transitions"""
        
        # If state is missing configs, this is a LangGraph conversion issue
        if not hasattr(state, 'template_config') or not state.template_config:
            raise RuntimeError("ENTERPRISE: template_config lost during state transition - LangGraph conversion issue")
        if not hasattr(state, 'style_config') or not state.style_config:
            raise RuntimeError("ENTERPRISE: style_config lost during state transition - LangGraph conversion issue")
        
        # Validate configs are still valid dicts
        if not isinstance(state.template_config, dict) or not state.template_config:
            raise RuntimeError(f"ENTERPRISE: template_config corrupted: {type(state.template_config)}")
        if not isinstance(state.style_config, dict) or not state.style_config:
            raise RuntimeError(f"ENTERPRISE: style_config corrupted: {type(state.style_config)}")
        
        logger.info(f"State preservation check passed: template_config={bool(state.template_config)}, style_config={bool(state.style_config)}")
        return state

    def _determine_specialized_agents(self, state: EnrichedContentState) -> str:
        self._require_state(state)
        spec = state.content_spec
        
        template_type = str(spec.template_type or "").lower()
        topic = str(spec.topic or "").lower()
        
        needs_seo = True
        needs_code = any(word in template_type + " " + topic for word in 
                        ['api', 'code', 'technical', 'programming', 'development'])
        
        if needs_seo and needs_code:
            return "seo_code"
        elif needs_seo:
            return "seo_only"
        elif needs_code:
            return "code_only"
        else:
            return "publisher"

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
            setattr(state_obj, "mcp_context", dict(mcp_options))

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

    def _normalize_initial_state(self, initial_state: Union[Dict, EnrichedContentState]) -> EnrichedContentState:
        logger.info(f"DEBUG: _normalize_initial_state called with type: {type(initial_state)}")

        # 1) Already an EnrichedContentState - preserve everything
        if isinstance(initial_state, EnrichedContentState):
            logger.info(f"DEBUG: Input is EnrichedContentState, template_config exists: {hasattr(initial_state, 'template_config')}")
            self._validate_state(initial_state)

            if not (hasattr(initial_state, "template_config") and isinstance(initial_state.template_config, dict) and bool(initial_state.template_config)):
                raise ValueError(f"ENTERPRISE: initial_state.template_config missing or empty - got: {type(getattr(initial_state, 'template_config', None))}")

            return initial_state

        # 2) Handle dict input (LangGraph Studio format)
        if not isinstance(initial_state, dict):
            raise TypeError("Initial state must be EnrichedContentState or dict")   

        logger.info(f"DEBUG: Converting dict to EnrichedContentState, dict keys: {list(initial_state.keys())}")

        # CRITICAL: LangGraph Studio sends nested format or top-level fields
        working_data = initial_state

        # Check for nested "input" wrapper (LangGraph Studio format)
        if len(working_data) == 1 and "input" in working_data:
            working_data = working_data["input"]
            logger.info("DEBUG: Extracted from LangGraph Studio 'input' wrapper")

        # Extract content_spec (required)
        content_spec_data = working_data.get("content_spec", {})

        # FIXED: Handle ContentSpec object vs dict
        if hasattr(content_spec_data, '__dict__'):
            # ContentSpec object - convert to dict for processing
            content_spec_dict = {
                'topic': getattr(content_spec_data, 'topic', ''),
                'template_type': getattr(content_spec_data, 'template_type', ''),
                'target_audience': getattr(content_spec_data, 'target_audience', ''),
                'platform': getattr(content_spec_data, 'platform', 'web')
            }
            logger.info("DEBUG: Converted ContentSpec object to dict")
        else:
            content_spec_dict = content_spec_data or {}

        if not content_spec_dict:
            # DEBUG: Log the actual structure
            template_config = working_data.get("template_config", {})
            print(f"DEBUG: template_config keys: {list(template_config.keys())}")

            dynamic_overrides = template_config.get("dynamic_overrides", {})
            print(f"DEBUG: dynamic_overrides keys: {list(dynamic_overrides.keys())}")
            print(f"DEBUG: dynamic_overrides content: {dynamic_overrides}")

            # Extract topic from wherever it actually is
            topic = None
            if "topic" in dynamic_overrides:
                topic = dynamic_overrides["topic"]
                print(f"DEBUG: Found topic in dynamic_overrides: {topic}")
            elif "dynamic_overrides" in dynamic_overrides:
                nested = dynamic_overrides["dynamic_overrides"]
                topic = nested.get("topic")
                print(f"DEBUG: Found topic in nested dynamic_overrides: {topic}")

            if not topic:
                print(f"DEBUG: No topic found anywhere. Full working_data keys: {list(working_data.keys())}")
                raise ValueError("ENTERPRISE: No topic found in state")

            content_spec_dict = {
                "topic": topic,
                "template_type": template_config.get("template_type", "article"),
                "target_audience": "general",
                "platform": "web"
            }

        # Validate required content_spec fields
        required_fields = ["topic", "template_type", "target_audience"]
        missing = [f for f in required_fields if not content_spec_dict.get(f)]
        if missing:
            # Provide defaults for missing fields
            defaults = {
                "topic": "Content Generation",
                "template_type": "article", 
                "target_audience": "general"
            }
            for field in missing:
                content_spec_dict[field] = defaults[field]
            logger.info(f"DEBUG: Added defaults for missing content_spec fields: {missing}")

        content_spec = ContentSpec(
            topic=content_spec_dict["topic"],
            template_type=content_spec_dict["template_type"],
            target_audience=content_spec_dict["target_audience"],
            platform=content_spec_dict.get("platform", "web"),
        )

        # CRITICAL: Handle template_config (enterprise: no fallbacks)
        tc = working_data.get("template_config", None)
        if not (isinstance(tc, dict) and bool(tc)):
            raise ValueError("ENTERPRISE: template_config must be a non-empty dict in request input")
        logger.info(f"DEBUG: Template config validated with keys: {list(tc.keys())}")

        # Handle style_config
        sc = working_data.get("style_config", None)
        if not (isinstance(sc, dict) and bool(sc)):
            raise ValueError("ENTERPRISE: style_config must be a non-empty dict in request input")

        # Build EnrichedContentState
        print(f"DEBUG: Before setting - tc keys: {list(tc.keys()) if tc else 'None'}")
        state = EnrichedContentState(content_spec=content_spec)
        state.template_config = copy.deepcopy(tc)
        state.style_config = copy.deepcopy(sc)
        print(f"DEBUG: After setting - state.template_config: {bool(getattr(state, 'template_config', None))}")
        print(f"DEBUG: state.template_config keys: {list(getattr(state, 'template_config', {}).keys())}")
        
                # CRITICAL FIX: Copy ALL content fields including 'content'
        content_fields = ["request_id", "current_phase", "completed_phases", "draft_content", "final_content", "content"]
        for attr in content_fields:
            if attr in working_data:
                setattr(state, attr, copy.deepcopy(working_data[attr]))
                logger.info(f"DEBUG: Copied {attr} field from working_data")

        if not getattr(state, "current_phase", None):
            state.update_phase(ContentPhase.PLANNING)   

        # FINAL VERIFICATION
        if not (hasattr(state, 'template_config') and isinstance(state.template_config, dict) and state.template_config):
            raise ValueError(f"CRITICAL: template_config validation failed after normalization: {type(getattr(state, 'template_config', None))}")   

        logger.info(f"DEBUG: Successfully normalized state with template_config keys: {list(state.template_config.keys())}")
        return state

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

    def _get_editor_agent(self):
         # Prefer existing instance; otherwise create and cache one
         if getattr(self, "editor_agent", None) is None:
             from langgraph_app.agents.enhanced_editor_integrated import EnhancedEditorAgent
             self.editor_agent = EnhancedEditorAgent()
         return self.editor_agent


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
