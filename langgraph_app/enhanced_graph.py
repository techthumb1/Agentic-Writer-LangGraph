# File: langgraph_app/enhanced_graph.py

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from typing_extensions import TypedDict
from enum import Enum
import json
from datetime import datetime, timedelta

from types import SimpleNamespace
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, tool_validator
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field, validator
import structlog

# Import integrated agents
from langgraph_app.agents.enhanced_planner_integrated import EnhancedPlannerAgent
from langgraph_app.agents.enhanced_researcher_integrated import EnhancedResearcherAgent  
from langgraph_app.agents.enhanced_editor_integrated import EnhancedEditorAgent
from langgraph_app.agents.enhanced_formatter_integrated import EnhancedFormatterAgent
from langgraph_app.agents.writer_integrated import IntegratedWriterAgent
from langgraph_app.agents.enhanced_code_agent_integrated import EnhancedCodeAgent
from langgraph_app.agents.enhanced_publisher_integrated import EnhancedPublisherAgent
from langgraph_app.agents.enhanced_seo_agent_integrated import EnhancedSEOAgent
from langgraph_app.agents.enhanced_image_agent import IntelligentImageAgent
from langgraph_app.agents.writer_integrated import IntegratedWriterAgent
from langgraph_app.agents.enhanced_call_writer_integrated import EnhancedCallWriterAgent


# Structured logging setup
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Metrics and monitoring
class MetricsCollector:
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, name: str):
        self.start_times[name] = time.time()
    
    def end_timer(self, name: str):
        if name in self.start_times:
            duration = time.time() - self.start_times[name]
            self.metrics[name] = duration
            del self.start_times[name]
            return duration
        return None
    
    def increment_counter(self, name: str, value: int = 1):
        self.metrics[name] = self.metrics.get(name, 0) + value
    
    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics.copy()

# Enhanced state management - FIXED for LangGraph compatibility
class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentState(TypedDict):
    """Enhanced state management with validation and typing - LangGraph Compatible"""
    request_id: str
    generation_id: Optional[str]
    content: str
    metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    status: str  # CHANGED: String instead of enum for LangGraph compatibility
    progress: float
    
    # Agent-specific states
    research_data: Dict[str, Any]
    outline: Dict[str, Any]
    draft_content: str
    edited_content: str
    formatted_content: str
    seo_data: Dict[str, Any]
    
    # Performance metrics
    metrics: Dict[str, Any]
    started_at: Optional[str]  # CHANGED: String instead of datetime for LangGraph compatibility
    completed_at: Optional[str]  # CHANGED: String instead of datetime for LangGraph compatibility
    
    # Configuration
    template_config: Dict[str, Any]
    style_config: Dict[str, Any]

# Enhanced content generation graph with integrated agents
class EnhancedContentGraph:
    """Enhanced content generation graph with integrated agent implementation"""
    
    def __init__(self, llm, checkpointer=None):
        self.llm = llm
        self.checkpointer = checkpointer or MemorySaver()
        self.graph = self._build_graph()
        self.metrics = MetricsCollector()
    
    # In the _build_graph method, add code_agent initialization:
    def _build_graph(self) -> StateGraph:
        """Build the enhanced content generation graph with integrated agents"""

        # Initialize integrated agents
        planner_agent = EnhancedPlannerAgent()
        research_agent = EnhancedResearcherAgent()
        writer_agent = IntegratedWriterAgent()
        code_agent = EnhancedCodeAgent()  # ADD THIS LINE
        editor_agent = EnhancedEditorAgent()
        formatter_agent = EnhancedFormatterAgent()

        # Create graph
        workflow = StateGraph(AgentState)

        # Add nodes with integrated agents
        workflow.add_node("plan", self._create_planner_node(planner_agent))
        workflow.add_node("research", self._create_research_node(research_agent))
        workflow.add_node("write", self._create_writer_node(writer_agent))
        workflow.add_node("code", self._create_code_node(code_agent))  # ADD THIS LINE
        workflow.add_node("edit", self._create_editor_node(editor_agent))
        workflow.add_node("format", self._create_formatter_node(formatter_agent))
        workflow.add_node("error_handler", self._handle_error)

        # Add edges with conditional routing
        workflow.set_entry_point("plan")

        workflow.add_conditional_edges(
            "plan",
            self._should_continue_after_planning,
            {
                "continue": "research",
                "error": "error_handler",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "research",
            self._should_continue_after_research,
            {
                "continue": "write",
                "error": "error_handler",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "write",
            self._should_continue_after_writing,
            {
                "continue": "code",  # CHANGE THIS LINE
                "error": "error_handler",
                "end": END
            }
        )

        # ADD THESE NEW CONDITIONAL EDGES:
        workflow.add_conditional_edges(
            "code",
            self._should_continue_after_code,
            {
                "continue": "edit",
                "error": "error_handler",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "edit",
            self._should_continue_after_editing,
            {
                "continue": "format",
                "error": "error_handler",
                "end": END
            }
        )

        workflow.add_edge("format", END)
        workflow.add_edge("error_handler", END)

        return workflow.compile(checkpointer=self.checkpointer)

    # ADD THIS NEW METHOD:
    def _create_code_node(self, code_agent):
        """Create code node with integrated agent"""
        async def code_node(state: AgentState) -> AgentState:
            try:
                logger.info("Starting code agent", request_id=state["request_id"])
                self.metrics.start_timer("code_duration")
                
                state["status"] = "processing"
                state["progress"] = 0.55
                
                # Convert AgentState to EnrichedContentState for integrated agent
                enriched_state = self._convert_to_enriched_state(state)
                
                # Set draft content for code agent
                if state.get("draft_content"):
                    enriched_state.draft_content = state["draft_content"]
                
                # Execute integrated code agent
                result_state = code_agent.execute(enriched_state)
                
                # Convert back to AgentState
                updated_state = self._convert_from_enriched_state(result_state, state)
                updated_state["progress"] = 0.65
                
                # Add metrics
                duration = self.metrics.end_timer("code_duration")
                updated_state["metrics"]["code_duration"] = duration
                
                logger.info("Code generation completed", request_id=state["request_id"], duration=duration)
                return updated_state
                
            except Exception as e:
                logger.error("Code agent failed", error=str(e), request_id=state["request_id"])
                state["errors"].append(f"Code generation failed: {str(e)}")
                state["status"] = "failed"
                return state
        
        return code_node

    # ADD THIS NEW METHOD:
    def _should_continue_after_code(self, state: AgentState) -> str:
        """Decide whether to continue after code generation"""
        if state["status"] == "failed":
            return "error"
        return "continue"
    
    def _create_planner_node(self, planner_agent):
        """Create planner node with integrated agent"""
        async def planner_node(state: AgentState) -> AgentState:
            try:
                logger.info("Starting planning agent", request_id=state["request_id"])
                self.metrics.start_timer("planning_duration")
                
                state["status"] = "processing"
                state["progress"] = 0.1
                
                # Convert AgentState to EnrichedContentState for integrated agent
                enriched_state = self._convert_to_enriched_state(state)
                
                # Execute integrated planner
                result_state = planner_agent.execute(enriched_state)
                
                # Convert back to AgentState
                updated_state = self._convert_from_enriched_state(result_state, state)
                updated_state["progress"] = 0.2
                
                # Add metrics
                duration = self.metrics.end_timer("planning_duration")
                updated_state["metrics"]["planning_duration"] = duration
                
                logger.info("Planning completed", request_id=state["request_id"], duration=duration)
                return updated_state
                
            except Exception as e:
                logger.error("Planning agent failed", error=str(e), request_id=state["request_id"])
                state["errors"].append(f"Planning failed: {str(e)}")
                state["status"] = "failed"
                return state
        
        return planner_node
    
    
    def _create_research_node(self, research_agent):
        """Create research node with integrated agent and real research capabilities"""
        async def research_node(state: AgentState) -> AgentState:
            try:
                logger.info("Starting research agent", request_id=state["request_id"])
                self.metrics.start_timer("research_duration")

                state["status"] = "processing"
                state["progress"] = 0.3

                try:
                    # Try to use enhanced researcher agent
                    from langgraph_app.agents.enhanced_researcher import enhanced_researcher_agent

                    research_request = {
                        **state,
                        "topic": state["template_config"].get("topic", ""),
                        "research_params": {
                            "depth": "moderate",
                            "sources": 3,
                            "focus_areas": ["overview", "key_concepts", "examples"]
                        }
                    }

                    research_result = await enhanced_researcher_agent.intelligent_research(research_request)
                    state["research_data"] = research_result.get("research_data", {})

                except ImportError:
                    logger.warning("Enhanced researcher not available, using integrated agent")

                    # Convert AgentState → EnrichedContentState
                    enriched_state = self._convert_to_enriched_state(state)

                    # Inject planning_output if present
                    if state.get("planning_output") is not None:
                        enriched_state.planning_output = state["planning_output"]
                        enriched_state.research_plan = state["planning_output"]

                    # Execute fallback research
                    print(f"DEBUG researcher fallback enriched_state.research_plan = {enriched_state.research_plan}")

                    result_state = research_agent.execute(enriched_state)

                    # Convert back and update state
                    updated_state = self._convert_from_enriched_state(result_state, state)
                    state.update(updated_state)

                state["progress"] = 0.4

                # Add metrics
                duration = self.metrics.end_timer("research_duration")
                state["metrics"]["research_duration"] = duration
                state["metrics"]["topics_researched"] = len(state.get("research_data", {}).get("findings", []))

                logger.info("Research completed",
                            request_id=state["request_id"],
                            duration=duration,
                            topics_count=state["metrics"]["topics_researched"])

                return state

            except Exception as e:
                logger.error("Research agent failed", error=str(e), request_id=state["request_id"])
                state["errors"].append(f"Research failed: {str(e)}")
                state["status"] = "failed"
                return state

        return research_node

    def _create_writer_node(self, writer_agent):
        """Create writer node with integrated agent and real writing capabilities"""
        async def writer_node(state: AgentState) -> AgentState:
            try:
                logger.info("Starting writer agent", request_id=state["request_id"])
                self.metrics.start_timer("writing_duration")
                
                state["status"] = "processing"
                state["progress"] = 0.5
                
                # Try to use real innovative writer first
                try:
                    from langgraph_app.agents.writer import InnovativeWriterAgent
                    innovative_writer_agent = InnovativeWriterAgent()
                    
                    # Prepare writer input
                    writer_input = {
                        **state,
                        "topic": state["template_config"].get("topic", ""),
                        "audience": state["template_config"].get("audience", "general"),
                        "style_profile": state.get("style_profile", "jason"),
                        "research": state["research_data"],
                        "dynamic_parameters": state["template_config"]
                    }
                    
                    # Execute real writing
                    writing_result = innovative_writer_agent.generate_adaptive_content(writer_input)
                    
                    # Extract content and metadata
                    state["draft_content"] = writing_result.get("draft", "")
                    if writing_result.get("metadata"):
                        state["metadata"].update(writing_result["metadata"])
                        
                except ImportError:
                    logger.warning("Innovative writer not available, using integrated agent")
                    # Fallback to integrated agent
                    enriched_state = self._convert_to_enriched_state(state)
                    result_state = writer_agent.execute(enriched_state)
                    updated_state = self._convert_from_enriched_state(result_state, state)
                    state.update(updated_state)
                
                state["progress"] = 0.6
                
                # Add metrics
                duration = self.metrics.end_timer("writing_duration")
                state["metrics"]["writing_duration"] = duration
                state["metrics"]["word_count"] = len(state["draft_content"].split())
                
                logger.info("Writing completed", 
                           request_id=state["request_id"],
                           duration=duration,
                           word_count=len(state["draft_content"].split()))
                
                return state
                
            except Exception as e:
                logger.error("Writer agent failed", error=str(e), request_id=state["request_id"])
                state["errors"].append(f"Writing failed: {str(e)}")
                state["status"] = "failed"
                return state
        
        return writer_node
    
    def _create_editor_node(self, editor_agent):
        """Create editor node with integrated agent and real editing capabilities"""
        async def editor_node(state: AgentState) -> AgentState:
            try:
                logger.info("Starting editor agent", request_id=state["request_id"])
                self.metrics.start_timer("editing_duration")
                
                state["status"] = "processing"
                state["progress"] = 0.7
                
                draft = state["draft_content"]
                if not draft:
                    raise ValueError("No draft content to edit")
                
                # Try to use real editor first
                try:
                    from langgraph_app.agents.enhanced_editor import enhanced_editor_agent
                    
                    editor_input = {
                        **state,
                        "content": draft,
                        "style_requirements": state["style_config"]
                    }
                    
                    editing_result = await enhanced_editor_agent.intelligent_edit(editor_input)
                    state["edited_content"] = editing_result.get("edited_content", draft)
                    
                except ImportError:
                    logger.warning("Enhanced editor not available, using integrated agent")
                    # Fallback to integrated agent
                    enriched_state = self._convert_to_enriched_state(state)
                    result_state = editor_agent.execute(enriched_state)
                    updated_state = self._convert_from_enriched_state(result_state, state)
                    state.update(updated_state)
                    
                    # Ensure we have edited content
                    if not state.get("edited_content"):
                        state["edited_content"] = self._basic_edit(draft)
                
                state["progress"] = 0.8
                
                # Add metrics
                duration = self.metrics.end_timer("editing_duration")
                state["metrics"]["editing_duration"] = duration
                state["metrics"]["edits_made"] = self._count_edits(draft, state["edited_content"])
                
                logger.info("Editing completed", 
                           request_id=state["request_id"],
                           duration=duration,
                           edits_made=state["metrics"]["edits_made"])
                
                return state
                
            except Exception as e:
                logger.error("Editor agent failed", error=str(e), request_id=state["request_id"])
                state["errors"].append(f"Editing failed: {str(e)}")
                state["status"] = "failed"
                return state
        
        return editor_node
    
    def _create_formatter_node(self, formatter_agent):
        """Create formatter node with integrated agent and real formatting capabilities"""
        async def formatter_node(state: AgentState) -> AgentState:
            try:
                logger.info("Starting formatter agent", request_id=state["request_id"])
                self.metrics.start_timer("formatting_duration")
                
                state["status"] = "processing"
                state["progress"] = 0.9
                
                edited_content = state["edited_content"]
                if not edited_content:
                    raise ValueError("No edited content to format")
                
                # Try to use real formatter first
                try:
                    from langgraph_app.agents.enhanced_formatter import enhanced_formatter_agent
                    
                    formatter_input = {
                        **state,
                        "content": edited_content,
                        "format_requirements": state["template_config"].get("format", {})
                    }
                    
                    formatting_result = await enhanced_formatter_agent.intelligent_format(formatter_input)
                    state["formatted_content"] = formatting_result.get("formatted_content", edited_content)
                    
                except ImportError:
                    logger.warning("Enhanced formatter not available, using integrated agent")
                    # Fallback to integrated agent
                    enriched_state = self._convert_to_enriched_state(state)
                    result_state = formatter_agent.execute(enriched_state)
                    updated_state = self._convert_from_enriched_state(result_state, state)
                    state.update(updated_state)
                    
                    # Ensure we have formatted content
                    if not state.get("formatted_content"):
                        state["formatted_content"] = self._basic_format(edited_content, state)
                
                # Set final content and complete
                state["content"] = state.get("formatted_content", edited_content)
                
                # Generate metadata
                await self._generate_metadata(state)
                
                state["progress"] = 1.0
                state["status"] = "completed"
                state["completed_at"] = datetime.now().isoformat()
                
                # Add metrics
                duration = self.metrics.end_timer("formatting_duration")
                state["metrics"]["formatting_duration"] = duration
                
                logger.info("Formatting completed", 
                           request_id=state["request_id"],
                           duration=duration)
                
                return state
                
            except Exception as e:
                logger.error("Formatter agent failed", error=str(e), request_id=state["request_id"])
                state["errors"].append(f"Formatting failed: {str(e)}")
                state["status"] = "failed"
                return state
        
        return formatter_node
    
    def _convert_to_enriched_state(self, agent_state: AgentState):
       """Convert AgentState to EnrichedContentState for integrated agents - FIXED"""
       # Import here to avoid circular imports
       from langgraph_app.core.enriched_content_state import EnrichedContentState, ContentSpec

       # Create content spec from template and style config
       content_spec = ContentSpec(
           topic=agent_state["template_config"].get("topic", "Generated Content"),
           audience=agent_state["template_config"].get("audience", "general"),
           template_type=agent_state["template_config"].get("template", "article"),
           platform=agent_state["template_config"].get("platform", "web"),
           complexity_level=agent_state["template_config"].get("complexity_level", 5),
           innovation_level=agent_state["template_config"].get("innovation_level", "moderate"),
           business_context=agent_state["template_config"].get("business_context", {})
       )

       # Create enriched state
       enriched_state = EnrichedContentState(
           content_spec=content_spec,
           request_id=agent_state["request_id"]
       )

       # Transfer existing data
       if agent_state.get("draft_content"):
            enriched_state.draft_content = agent_state["draft_content"]
       if agent_state.get("research_data"):
           # Convert research data to research findings if needed
            pass
        
       # CRITICAL FIX: Set research_plan and planning_output attributes
       if agent_state.get("planning_output"):
            enriched_state.planning_output = agent_state["planning_output"]
            enriched_state.research_plan = agent_state["planning_output"]  # Set both for compatibility
       elif agent_state.get("research_plan"):
            enriched_state.research_plan = agent_state["research_plan"]
       else:
            # Create minimal research plan to prevent attribute errors
            from types import SimpleNamespace
            enriched_state.research_plan = SimpleNamespace(
                research_priorities=["overview", "key_concepts", "examples"],
                depth="moderate",
                sources_needed=3,
                focus_areas=["background", "main_concepts", "practical_applications"]
            )

       return enriched_state    
    def _convert_from_enriched_state(self, enriched_state, original_state: AgentState) -> AgentState:
        """Convert EnrichedContentState back to AgentState"""
        # Update original state with enriched state results
        updated_state = original_state.copy()
        
        if hasattr(enriched_state, 'draft_content') and enriched_state.draft_content:
            updated_state["draft_content"] = enriched_state.draft_content
        
        if hasattr(enriched_state, 'formatted_content') and enriched_state.formatted_content:
            updated_state["formatted_content"] = enriched_state.formatted_content
        
        # Transfer other relevant data
        if hasattr(enriched_state, 'research_findings') and enriched_state.research_findings:
            updated_state["research_data"] = {
                "findings": enriched_state.research_findings.primary_insights if enriched_state.research_findings.primary_insights else [],
                "research_completed": True
            }

        if hasattr(enriched_state, 'planning_output') and enriched_state.planning_output:
            updated_state["planning_output"] = enriched_state.planning_output
            updated_state["research_plan"] = enriched_state.research_plan
        
        if not updated_state.get("planning_output"):
            print("WARNING: Missing planning_output in updated_state after planner execution")


        print(f"DEBUG enriched_state.research_plan = {enriched_state.research_plan}")

        return updated_state
    
    def _basic_edit(self, content: str) -> str:
        """Basic content editing"""
        # Remove extra whitespace
        lines = [line.strip() for line in content.split('\n')]
        # Remove empty lines at start/end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        return '\n'.join(lines)
    
    def _count_edits(self, original: str, edited: str) -> int:
        """Count the number of edits made"""
        return abs(len(original.split()) - len(edited.split()))
    
    def _basic_format(self, content: str, state: AgentState) -> str:
        """Basic content formatting"""
        template_config = state["template_config"]
        format_type = template_config.get("format", "markdown")
        
        if format_type == "html":
            # Convert markdown to HTML
            return self._markdown_to_html(content)
        elif format_type == "json":
            # Structure as JSON
            return self._to_json_format(content, state)
        else:
            # Keep as markdown (default)
            return content
    
    def _markdown_to_html(self, content: str) -> str:
        """Convert markdown to HTML"""
        # Simple markdown to HTML conversion
        html = content.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        html = html.replace('\n\n', '</p>\n<p>')
        html = f'<article>\n<p>{html}</p>\n</article>'
        return html
    
    def _to_json_format(self, content: str, state: AgentState) -> str:
        """Convert content to structured JSON"""
        structured = {
            "title": state["outline"].get("title", "Generated Content"),
            "content": content,
            "metadata": state["metadata"],
            "outline": state["outline"],
            "metrics": state["metrics"],
            "generated_at": datetime.now().isoformat()
        }
        return json.dumps(structured, indent=2)
    
    async def _generate_metadata(self, state: AgentState):
        """Generate content metadata"""
        content = state["content"]
        
        metadata = {
            "word_count": len(content.split()),
            "character_count": len(content),
            "reading_time_minutes": max(1, len(content.split()) // 200),
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        # Merge with existing metadata
        state["metadata"].update(metadata)
    
    def _should_continue_after_planning(self, state: AgentState) -> str:
        """Decide whether to continue after planning"""
        if state["status"] == "failed":
            return "error"
        return "continue"
    
    def _should_continue_after_research(self, state: AgentState) -> str:
        """Decide whether to continue after research"""
        if state["status"] == "failed":
            return "error"
        # Always continue to writing - research is optional for some content types
        return "continue"
    
    def _should_continue_after_writing(self, state: AgentState) -> str:
        """Decide whether to continue after writing"""
        if state["status"] == "failed":
            return "error"
        if not state["draft_content"] or len(state["draft_content"].strip()) < 10:
            return "error"
        return "continue"
    
    def _should_continue_after_editing(self, state: AgentState) -> str:
        """Decide whether to continue after editing"""
        if state["status"] == "failed":
            return "error"
        if not state.get("edited_content") and not state.get("draft_content"):
            return "error"
        return "continue"
    
    async def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors and attempt recovery"""
        logger.error("Handling error state", 
                    request_id=state["request_id"],
                    errors=state["errors"])
        
        state["status"] = "failed"
        state["completed_at"] = datetime.now().isoformat()
        
        # Attempt to provide partial results
        if state["draft_content"] and not state["content"]:
            state["content"] = state["draft_content"]
            state["warnings"].append("Returning draft content due to processing errors")
        
        return state
    
    async def generate_content(self, 
                             request_id: str,
                             template_config: Dict[str, Any],
                             style_config: Dict[str, Any]) -> AgentState:
        """Generate content with comprehensive monitoring using integrated agents"""
        
        logger.info("Starting content generation", request_id=request_id)
        self.metrics.start_timer("total_generation_time")
        
        # Initialize state
        initial_state = AgentState(
            request_id=request_id,
            generation_id=None,
            content="",
            metadata={},
            errors=[],
            warnings=[],
            status="pending",
            progress=0.0,
            research_data={},
            outline={},
            draft_content="",
            edited_content="",
            formatted_content="",
            seo_data={},
            metrics={},
            started_at=datetime.now().isoformat(),
            completed_at=None,
            template_config=template_config,
            style_config=style_config
        )
        
        try:
            # Run the graph
            config = RunnableConfig(
                configurable={"thread_id": request_id},
                tags=[f"request:{request_id}"]
            )
            
            final_state = await self.graph.ainvoke(initial_state, config)
            
            # Add final metrics
            total_time = self.metrics.end_timer("total_generation_time")
            final_state["metrics"]["total_generation_time"] = total_time
            
            logger.info("Content generation completed", 
                       request_id=request_id,
                       status=final_state["status"],
                       total_time=total_time)
            
            return final_state
            
        except Exception as e:
            logger.error("Content generation failed", 
                        request_id=request_id, 
                        error=str(e))
            
            # Return error state
            error_state = initial_state.copy()
            error_state["status"] = "failed"
            error_state["errors"].append(f"Generation failed: {str(e)}")
            error_state["completed_at"] = datetime.now().isoformat()
            
            return error_state

def create_enhanced_graph(llm=None):
    """Factory function to create an enhanced content graph"""
    if llm is None:
        try:
            from .enhanced_model_registry import get_model
            llm = get_model("writer")
        except:
            llm = None
    
    return EnhancedContentGraph(llm)