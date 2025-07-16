# File: langgraph_app/integrated_workflow.py
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

# Import your existing agents
from .agents.writer import WriterAgent
from .agents.enhanced_researcher import IntelligentResearcherAgent
from .agents.enhanced_editor import IntelligentEditorAgent
from .agents.enhanced_seo_agent import IntelligentSEOAgent
from .agents.enhanced_formatter import IntelligentFormatterAgent
from .agents.enhanced_planner import IntelligentPlannerAgent
from .agents.enhanced_publisher import IntelligentPublisherAgent
from .agents.enhanced_image_agent import IntelligentImageAgent
from .agents.enhanced_code_agent import IntelligentCodeAgent

# Import your existing infrastructure
from .enhanced_model_registry import ModelRegistry
from .cache_system import CacheSystem
from .job_queue import JobQueue
from .semantic_search import SemanticSearch
from .style_profile_loader import StyleProfileLoader
from .integration_coordinator import IntegrationCoordinator
from .utils import *

class WorkflowType(Enum):
    SIMPLE = "simple"  # Basic write -> edit -> format
    COMPREHENSIVE = "comprehensive"  # Full pipeline with research and SEO
    RESEARCH_HEAVY = "research_heavy"  # Research-focused content
    TECHNICAL = "technical"  # Code-heavy content
    VISUAL = "visual"  # Image-heavy content
    PUBLICATION_READY = "publication_ready"  # Full pipeline + publishing

@dataclass
class IntegratedGenerationState:
    """Enhanced state object that flows through your existing agent ecosystem"""
    
    # Input requirements (from the new system)
    content_requirements: Dict[str, Any]
    style_requirements: Dict[str, Any]
    structure_requirements: Dict[str, Any]
    language_requirements: Dict[str, Any]
    formatting_requirements: Dict[str, Any]
    user_parameters: Dict[str, Any]
    
    # Generation preferences
    max_tokens: int = 2000
    temperature: float = 0.7
    model: str = "gpt-4-turbo"
    workflow_type: WorkflowType = WorkflowType.COMPREHENSIVE
    
    # Your existing workflow state
    current_step: str = "initialize"
    plan: Optional[Dict] = None
    research_data: Optional[Dict] = None
    draft_content: Optional[str] = None
    edited_content: Optional[str] = None
    seo_optimized_content: Optional[str] = None
    formatted_content: Optional[str] = None
    final_content: Optional[str] = None
    
    # Media content
    images: List[Dict] = None
    code_blocks: List[Dict] = None
    
    # Publishing
    publication_config: Optional[Dict] = None
    published_urls: List[str] = None
    
    # Metadata and tracking
    generation_id: str = ""
    started_at: datetime = None
    completed_at: Optional[datetime] = None
    agent_steps: List[Dict] = None
    errors: List[str] = None
    cache_hits: int = 0
    total_tokens_used: int = 0
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now()
        if self.agent_steps is None:
            self.agent_steps = []
        if self.errors is None:
            self.errors = []
        if self.images is None:
            self.images = []
        if self.code_blocks is None:
            self.code_blocks = []
        if self.published_urls is None:
            self.published_urls = []

class IntegratedContentWorkflow:
    """
    Integration layer that connects the new business logic with your existing agents
    """
    
    def __init__(self):
        # Initialize your existing infrastructure
        self.model_registry = ModelRegistry()
        self.cache_system = CacheSystem()
        self.job_queue = JobQueue()
        self.semantic_search = SemanticSearch()
        self.style_profile_loader = StyleProfileLoader()
        self.integration_coordinator = IntegrationCoordinator()
        
        # Initialize your existing agents
        self.enhanced_planner = IntelligentPlannerAgent(self.model_registry)
        self.enhanced_researcher = IntelligentResearcherAgent(self.model_registry, self.semantic_search)
        self.writer = WriterAgent(self.model_registry, self.cache_system)
        self.enhanced_editor = IntelligentEditorAgent(self.model_registry)
        self.enhanced_seo_agent = IntelligentSEOAgent(self.model_registry)
        self.enhanced_formatter = IntelligentFormatterAgent()
        self.enhanced_image_agent = IntelligentImageAgent(self.model_registry)
        self.enhanced_code_agent = IntelligentCodeAgent(self.model_registry)
        self.enhanced_publisher = IntelligentPublisherAgent(self.model_registry)
        
        # Build workflow graphs for different types
        self.workflows = {
            WorkflowType.SIMPLE: self._build_simple_workflow(),
            WorkflowType.COMPREHENSIVE: self._build_comprehensive_workflow(),
            WorkflowType.RESEARCH_HEAVY: self._build_research_heavy_workflow(),
            WorkflowType.TECHNICAL: self._build_technical_workflow(),
            WorkflowType.VISUAL: self._build_visual_workflow(),
            WorkflowType.PUBLICATION_READY: self._build_publication_workflow(),
        }
    
    def _build_simple_workflow(self) -> StateGraph:
        """Simple workflow: Plan -> Write -> Edit -> Format"""
        workflow = StateGraph(IntegratedGenerationState)
        
        workflow.add_node("plan", self._planning_step)
        workflow.add_node("write", self._writing_step)
        workflow.add_node("edit", self._editing_step)
        workflow.add_node("format", self._formatting_step)
        workflow.add_node("finalize", self._finalization_step)
        
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "write")
        workflow.add_edge("write", "edit")
        workflow.add_edge("edit", "format")
        workflow.add_edge("format", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _build_comprehensive_workflow(self) -> StateGraph:
        """Full pipeline workflow"""
        workflow = StateGraph(IntegratedGenerationState)
        
        workflow.add_node("plan", self._planning_step)
        workflow.add_node("research", self._research_step)
        workflow.add_node("write", self._writing_step)
        workflow.add_node("edit", self._editing_step)
        workflow.add_node("seo_optimize", self._seo_step)
        workflow.add_node("format", self._formatting_step)
        workflow.add_node("finalize", self._finalization_step)
        
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "research")
        workflow.add_edge("research", "write")
        workflow.add_edge("write", "edit")
        workflow.add_edge("edit", "seo_optimize")
        workflow.add_edge("seo_optimize", "format")
        workflow.add_edge("format", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _build_technical_workflow(self) -> StateGraph:
        """Technical content workflow with code generation"""
        workflow = StateGraph(IntegratedGenerationState)
        
        workflow.add_node("plan", self._planning_step)
        workflow.add_node("research", self._research_step)
        workflow.add_node("generate_code", self._code_generation_step)
        workflow.add_node("write", self._writing_step)
        workflow.add_node("edit", self._editing_step)
        workflow.add_node("format", self._formatting_step)
        workflow.add_node("finalize", self._finalization_step)
        
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "research")
        workflow.add_edge("research", "generate_code")
        workflow.add_edge("generate_code", "write")
        workflow.add_edge("write", "edit")
        workflow.add_edge("edit", "format")
        workflow.add_edge("format", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _build_visual_workflow(self) -> StateGraph:
        """Visual content workflow with image generation"""
        workflow = StateGraph(IntegratedGenerationState)
        
        workflow.add_node("plan", self._planning_step)
        workflow.add_node("research", self._research_step)
        workflow.add_node("generate_images", self._image_generation_step)
        workflow.add_node("write", self._writing_step)
        workflow.add_node("edit", self._editing_step)
        workflow.add_node("format", self._formatting_step)
        workflow.add_node("finalize", self._finalization_step)
        
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "research")
        workflow.add_edge("research", "generate_images")
        workflow.add_edge("generate_images", "write")
        workflow.add_edge("write", "edit")
        workflow.add_edge("edit", "format")
        workflow.add_edge("format", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _build_publication_workflow(self) -> StateGraph:
        """Full workflow with publishing"""
        workflow = StateGraph(IntegratedGenerationState)
        
        workflow.add_node("plan", self._planning_step)
        workflow.add_node("research", self._research_step)
        workflow.add_node("write", self._writing_step)
        workflow.add_node("edit", self._editing_step)
        workflow.add_node("seo_optimize", self._seo_step)
        workflow.add_node("format", self._formatting_step)
        workflow.add_node("publish", self._publishing_step)
        workflow.add_node("finalize", self._finalization_step)
        
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "research")
        workflow.add_edge("research", "write")
        workflow.add_edge("write", "edit")
        workflow.add_edge("edit", "seo_optimize")
        workflow.add_edge("seo_optimize", "format")
        workflow.add_edge("format", "publish")
        workflow.add_edge("publish", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _build_research_heavy_workflow(self) -> StateGraph:
        """Research-focused workflow"""
        workflow = StateGraph(IntegratedGenerationState)
        
        workflow.add_node("plan", self._planning_step)
        workflow.add_node("deep_research", self._deep_research_step)
        workflow.add_node("semantic_analysis", self._semantic_analysis_step)
        workflow.add_node("write", self._writing_step)
        workflow.add_node("edit", self._editing_step)
        workflow.add_node("format", self._formatting_step)
        workflow.add_node("finalize", self._finalization_step)
        
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "deep_research")
        workflow.add_edge("deep_research", "semantic_analysis")
        workflow.add_edge("semantic_analysis", "write")
        workflow.add_edge("write", "edit")
        workflow.add_edge("edit", "format")
        workflow.add_edge("format", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def _planning_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """Planning step using your existing PlannerAgent"""
        try:
            state.current_step = "planning"
            self._log_agent_step(state, "planner", "creating_content_plan")
            
            # Use your existing planner
            planning_context = {
                "content_requirements": state.content_requirements,
                "style_requirements": state.style_requirements,
                "structure_requirements": state.structure_requirements,
                "user_parameters": state.user_parameters,
                "workflow_type": state.workflow_type.value
            }
            
            plan = await self.planner.create_plan(planning_context)
            state.plan = plan
            
            # Determine optimal workflow based on plan
            if not hasattr(state, 'workflow_type') or state.workflow_type == WorkflowType.COMPREHENSIVE:
                state.workflow_type = self._determine_optimal_workflow(plan, state)
            
            self._log_agent_step(state, "planner", "plan_created", 
                               f"Created {len(plan.get('sections', []))} sections")
            
            return state
            
        except Exception as e:
            self._log_error(state, "planning", str(e))
            return state
    
    async def _research_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """Enhanced research step using your existing ResearcherAgent"""
        try:
            state.current_step = "research"
            self._log_agent_step(state, "researcher", "gathering_information")
            
            # Check cache first
            cache_key = self._generate_cache_key("research", state)
            cached_research = await self.cache_system.get(cache_key)
            
            if cached_research:
                state.research_data = cached_research
                state.cache_hits += 1
                self._log_agent_step(state, "researcher", "cache_hit", "Used cached research data")
                return state
            
            # Build research query from plan and requirements
            research_query = self._build_research_query_from_plan(state)
            
            # Use your existing researcher with semantic search
            research_result = await self.researcher.research(
                query=research_query,
                content_type=state.content_requirements.get("category", "general"),
                depth=self._determine_research_depth(state),
                semantic_search=self.semantic_search,
                plan=state.plan
            )
            
            state.research_data = research_result
            
            # Cache the results
            await self.cache_system.set(cache_key, research_result, ttl=3600)
            
            self._log_agent_step(state, "researcher", "research_completed", 
                               f"Found {len(research_result.get('sources', []))} sources")
            
            return state
            
        except Exception as e:
            self._log_error(state, "research", str(e))
            return state
    
    async def _deep_research_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """Deep research for research-heavy workflow"""
        try:
            state.current_step = "deep_research"
            self._log_agent_step(state, "researcher", "deep_research")
            
            # Multi-phase research
            research_phases = [
                {"type": "background", "depth": "comprehensive"},
                {"type": "current_trends", "depth": "detailed"},
                {"type": "expert_opinions", "depth": "focused"},
                {"type": "case_studies", "depth": "specific"}
            ]
            
            comprehensive_research = {}
            for phase in research_phases:
                phase_query = self._build_phase_specific_query(state, phase)
                phase_result = await self.researcher.research(
                    query=phase_query,
                    content_type=state.content_requirements.get("category"),
                    depth=phase["depth"],
                    research_type=phase["type"]
                )
                comprehensive_research[phase["type"]] = phase_result
            
            state.research_data = comprehensive_research
            
            self._log_agent_step(state, "researcher", "deep_research_completed", 
                               f"Completed {len(research_phases)} research phases")
            
            return state
            
        except Exception as e:
            self._log_error(state, "deep_research", str(e))
            return state
    
    async def _semantic_analysis_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """Semantic analysis of research data"""
        try:
            state.current_step = "semantic_analysis"
            self._log_agent_step(state, "semantic_analyzer", "analyzing_research")
            
            if state.research_data:
                # Use your semantic search for analysis
                analysis = await self.semantic_search.analyze_research_coherence(
                    research_data=state.research_data,
                    content_requirements=state.content_requirements
                )
                
                # Enhance research data with semantic insights
                state.research_data["semantic_analysis"] = analysis
                
                self._log_agent_step(state, "semantic_analyzer", "analysis_completed", 
                                   f"Analyzed {analysis.get('coherence_score', 0):.2f} coherence")
            
            return state
            
        except Exception as e:
            self._log_error(state, "semantic_analysis", str(e))
            return state
    
    async def _writing_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """Enhanced writing step using your existing WriterAgent"""
        try:
            state.current_step = "writing"
            self._log_agent_step(state, "writer", "generating_content")
            
            # Load style profile using your existing loader
            style_profile = await self.style_profile_loader.load_profile(
                state.style_requirements
            )
            
            # Prepare comprehensive writing context
            writing_context = {
                "plan": state.plan,
                "research_data": state.research_data,
                "content_requirements": state.content_requirements,
                "style_profile": style_profile,
                "structure_requirements": state.structure_requirements,
                "language_requirements": state.language_requirements,
                "user_parameters": state.user_parameters,
                "images": state.images,  # For visual workflow
                "code_blocks": state.code_blocks,  # For technical workflow
            }
            
            # Use your existing writer
            draft = await self.writer.generate_content(
                context=writing_context,
                max_tokens=state.max_tokens,
                temperature=state.temperature,
                model=state.model,
                cache_system=self.cache_system
            )
            
            state.draft_content = draft
            word_count = len(draft.split())
            state.total_tokens_used += int(word_count * 1.3)  # Rough token estimate
            
            self._log_agent_step(state, "writer", "content_generated", 
                               f"Generated {word_count} words")
            
            return state
            
        except Exception as e:
            self._log_error(state, "writing", str(e))
            return state
    
    async def _code_generation_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """Code generation using your existing CodeAgent"""
        try:
            state.current_step = "code_generation"
            self._log_agent_step(state, "code_agent", "generating_code")
            
            # Extract code requirements from plan
            code_requirements = self._extract_code_requirements(state.plan, state.user_parameters)
            
            # Generate code blocks using your existing agent
            code_blocks = await self.code_agent.generate_code(
                requirements=code_requirements,
                context=state.research_data,
                style=state.style_requirements.get("code_style", "professional")
            )
            
            state.code_blocks = code_blocks
            
            self._log_agent_step(state, "code_agent", "code_generated", 
                               f"Generated {len(code_blocks)} code blocks")
            
            return state
            
        except Exception as e:
            self._log_error(state, "code_generation", str(e))
            return state
    
    async def _image_generation_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """Image generation using your existing ImageAgent"""
        try:
            state.current_step = "image_generation"
            self._log_agent_step(state, "image_agent", "generating_images")
            
            # Extract image requirements from plan
            image_requirements = self._extract_image_requirements(state.plan, state.user_parameters)
            
            # Generate images using your existing agent
            images = await self.image_agent.generate_images(
                requirements=image_requirements,
                content_context=state.research_data,
                style=state.style_requirements.get("visual_style", "professional")
            )
            
            state.images = images
            
            self._log_agent_step(state, "image_agent", "images_generated", 
                               f"Generated {len(images)} images")
            
            return state
            
        except Exception as e:
            self._log_error(state, "image_generation", str(e))
            return state
    
    async def _editing_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """Enhanced editing using your existing EditorAgent"""
        try:
            state.current_step = "editing"
            self._log_agent_step(state, "editor", "editing_content")
            
            content_to_edit = state.draft_content
            if not content_to_edit:
                raise ValueError("No draft content to edit")
            
            # Use your existing editor with comprehensive context
            edited_content = await self.editor.edit_content(
                content=content_to_edit,
                style_requirements=state.style_requirements,
                structure_requirements=state.structure_requirements,
                language_requirements=state.language_requirements,
                target_audience=state.content_requirements.get("target_audience"),
                content_type=state.content_requirements.get("category"),
                plan=state.plan,
                research_context=state.research_data
            )
            
            state.edited_content = edited_content
            
            # Calculate improvement metrics
            original_words = len(content_to_edit.split())
            edited_words = len(edited_content.split())
            
            self._log_agent_step(state, "editor", "editing_completed", 
                               f"Edited: {original_words} → {edited_words} words")
            
            return state
            
        except Exception as e:
            self._log_error(state, "editing", str(e))
            return state
    
    async def _seo_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """SEO optimization using your existing SEOAgent"""
        try:
            state.current_step = "seo_optimization"
            self._log_agent_step(state, "seo_agent", "optimizing_seo")
            
            content_to_optimize = state.edited_content or state.draft_content
            if not content_to_optimize:
                raise ValueError("No content to optimize")
            
            # Use your existing SEO agent
            seo_optimized = await self.seo_agent.optimize_content(
                content=content_to_optimize,
                target_keywords=state.user_parameters.get("target_keywords", []),
                content_type=state.content_requirements.get("category"),
                target_audience=state.content_requirements.get("target_audience"),
                research_context=state.research_data
            )
            
            state.seo_optimized_content = seo_optimized
            
            self._log_agent_step(state, "seo_agent", "seo_completed", "SEO optimization applied")
            
            return state
            
        except Exception as e:
            self._log_error(state, "seo_optimization", str(e))
            return state
    
    async def _formatting_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """Formatting using your existing FormatterAgent"""
        try:
            state.current_step = "formatting"
            self._log_agent_step(state, "formatter", "formatting_content")
            
            content_to_format = (
                state.seo_optimized_content or 
                state.edited_content or 
                state.draft_content
            )
            
            if not content_to_format:
                raise ValueError("No content to format")
            
            # Use your existing formatter
            formatted_content = await self.formatter.format_content(
                content=content_to_format,
                formatting_requirements=state.formatting_requirements,
                structure_requirements=state.structure_requirements,
                images=state.images,
                code_blocks=state.code_blocks,
                output_format=state.user_parameters.get("output_format", "markdown")
            )
            
            state.formatted_content = formatted_content
            
            self._log_agent_step(state, "formatter", "formatting_completed", "Content formatted")
            
            return state
            
        except Exception as e:
            self._log_error(state, "formatting", str(e))
            return state
    
    async def _publishing_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """Publishing using your existing PublisherAgent"""
        try:
            state.current_step = "publishing"
            self._log_agent_step(state, "publisher", "publishing_content")
            
            content_to_publish = state.formatted_content
            if not content_to_publish:
                raise ValueError("No content to publish")
            
            # Get publication configuration
            pub_config = state.user_parameters.get("publication_config", {})
            
            # Use your existing publisher
            publication_results = await self.publisher.publish_content(
                content=content_to_publish,
                config=pub_config,
                metadata={
                    "title": state.content_requirements.get("title"),
                    "category": state.content_requirements.get("category"),
                    "tags": state.user_parameters.get("tags", []),
                    "images": state.images,
                }
            )
            
            state.published_urls = publication_results.get("urls", [])
            state.publication_config = publication_results.get("config", {})
            
            self._log_agent_step(state, "publisher", "publishing_completed", 
                               f"Published to {len(state.published_urls)} platforms")
            
            return state
            
        except Exception as e:
            self._log_error(state, "publishing", str(e))
            return state
    
    async def _finalization_step(self, state: IntegratedGenerationState) -> IntegratedGenerationState:
        """Final step: prepare output and cleanup"""
        try:
            state.current_step = "finalization"
            self._log_agent_step(state, "coordinator", "finalizing")
            
            # Choose the best available content version
            final_content = (
                state.formatted_content or
                state.seo_optimized_content or 
                state.edited_content or 
                state.draft_content
            )
            
            if not final_content:
                raise ValueError("No content generated")
            
            state.final_content = final_content
            state.completed_at = datetime.now()
            state.current_step = "completed"
            
            # Use integration coordinator for final processing
            await self.integration_coordinator.finalize_generation(state)
            
            final_word_count = len(final_content.split())
            self._log_agent_step(state, "coordinator", "finalization_completed", 
                               f"Final content: {final_word_count} words")
            
            return state
            
        except Exception as e:
            self._log_error(state, "finalization", str(e))
            return state
    
    # Helper methods
    def _determine_optimal_workflow(self, plan: Dict, state: IntegratedGenerationState) -> WorkflowType:
        """Determine the best workflow based on plan and requirements"""
        
        # Check for technical content
        if any("code" in section.lower() or "programming" in section.lower() 
               for section in plan.get("sections", [])):
            return WorkflowType.TECHNICAL
        
        # Check for visual content
        if state.user_parameters.get("include_images") or \
           any("image" in section.lower() or "visual" in section.lower() 
               for section in plan.get("sections", [])):
            return WorkflowType.VISUAL
        
        # Check for research-heavy content
        if state.content_requirements.get("difficulty") == "advanced" or \
           len(plan.get("research_topics", [])) > 5:
            return WorkflowType.RESEARCH_HEAVY
        
        # Check for publication requirements
        if state.user_parameters.get("auto_publish") or \
           state.user_parameters.get("publication_config"):
            return WorkflowType.PUBLICATION_READY
        
        # Default to comprehensive
        return WorkflowType.COMPREHENSIVE
    
    def _build_research_query_from_plan(self, state: IntegratedGenerationState) -> str:
        """Build research query from the generated plan"""
        if not state.plan:
            return self._build_basic_research_query(state)
        
        query_parts = []
        
        # Main topic
        if "main_topic" in state.plan:
            query_parts.append(state.plan["main_topic"])
        
        # Section topics
        for section in state.plan.get("sections", [])[:3]:
            if isinstance(section, dict) and "topic" in section:
                query_parts.append(section["topic"])
            elif isinstance(section, str):
                query_parts.append(section)
        
        # Research topics from plan
        research_topics = state.plan.get("research_topics", [])
        query_parts.extend(research_topics[:3])
        
        return " ".join(query_parts)
    
    def _build_basic_research_query(self, state: IntegratedGenerationState) -> str:
        """Fallback research query building"""
        content_req = state.content_requirements
        user_params = state.user_parameters
        
        query_parts = [content_req.get("title", "")]
        
        if content_req.get("category"):
            query_parts.append(content_req["category"])
        
        # Add user-specified topics
        if "topics" in user_params:
            if isinstance(user_params["topics"], list):
                query_parts.extend(user_params["topics"])
            else:
                query_parts.append(str(user_params["topics"]))
        
        return " ".join(query_parts)
    
    def _build_phase_specific_query(self, state: IntegratedGenerationState, phase: Dict) -> str:
        """Build query for specific research phase"""
        base_query = self._build_research_query_from_plan(state)
        phase_modifier = {
            "background": f"{base_query} history overview fundamentals",
            "current_trends": f"{base_query} 2024 2025 trends recent developments",
            "expert_opinions": f"{base_query} expert analysis professional insights",
            "case_studies": f"{base_query} case study examples real-world applications"
        }
        
        return phase_modifier.get(phase["type"], base_query)
    
    def _extract_code_requirements(self, plan: Dict, user_params: Dict) -> List[Dict]:
        """Extract code generation requirements from plan"""
        if not plan:
            return []
        
        code_requirements = []
        
        # Look for code sections in plan
        for section in plan.get("sections", []):
            if isinstance(section, dict):
                section_content = section.get("description", "").lower()
                if any(keyword in section_content for keyword in ["code", "implementation", "example", "script"]):
                    code_requirements.append({
                        "type": "code_example",
                        "language": user_params.get("programming_language", "python"),
                        "description": section.get("description", ""),
                        "complexity": section.get("complexity", "intermediate")
                    })
        
        # Add explicit code requirements from user parameters
        if "code_examples" in user_params:
            for code_req in user_params["code_examples"]:
                code_requirements.append(code_req)
        
        return code_requirements
    
    def _extract_image_requirements(self, plan: Dict, user_params: Dict) -> List[Dict]:
        """Extract image generation requirements from plan"""
        if not plan:
            return []
        
        image_requirements = []
        
        # Look for visual elements in plan
        for section in plan.get("sections", []):
            if isinstance(section, dict):
                section_content = section.get("description", "").lower()
                if any(keyword in section_content for keyword in ["image", "diagram", "chart", "visual", "illustration"]):
                    image_requirements.append({
                        "type": "illustration",
                        "description": section.get("description", ""),
                        "style": user_params.get("image_style", "professional"),
                        "size": user_params.get("image_size", "1024x1024")
                    })
        
        # Add explicit image requirements from user parameters
        if "images" in user_params:
            for img_req in user_params["images"]:
                image_requirements.append(img_req)
        
        return image_requirements
    
    def _determine_research_depth(self, state: IntegratedGenerationState) -> str:
        """Determine research depth based on requirements"""
        difficulty = state.content_requirements.get("difficulty", "intermediate")
        technical_level = state.style_requirements.get("technical_level", "intermediate")
        workflow_type = state.workflow_type
        
        if workflow_type == WorkflowType.RESEARCH_HEAVY:
            return "comprehensive"
        elif difficulty == "advanced" or technical_level == "expert":
            return "deep"
        elif difficulty == "beginner" or technical_level == "basic":
            return "shallow"
        else:
            return "moderate"
    
    def _generate_cache_key(self, operation: str, state: IntegratedGenerationState) -> str:
        """Generate cache key for operation"""
        import hashlib
        
        # Create a unique key based on operation and relevant state
        key_data = {
            "operation": operation,
            "content_title": state.content_requirements.get("title", ""),
            "category": state.content_requirements.get("category", ""),
            "style_profile": state.style_requirements.get("name", ""),
            "model": state.model,
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _log_agent_step(self, state: IntegratedGenerationState, agent: str, action: str, result: str = ""):
        """Log agent step with consistent format"""
        step = {
            "agent": agent,
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
        state.agent_steps.append(step)
    
    def _log_error(self, state: IntegratedGenerationState, step: str, error: str):
        """Log error consistently"""
        state.errors.append(f"{step}: {error}")
        self._log_agent_step(state, "system", "error", f"{step} failed: {error}")
    
    async def generate_content(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point that integrates with your existing system"""
        try:
            # Create initial state from request
            prompt = request["prompt"]
            preferences = request["preferences"]
            
            # Determine workflow type from request or auto-detect
            workflow_type_str = request.get("workflow_type", "comprehensive")
            try:
                workflow_type = WorkflowType(workflow_type_str)
            except ValueError:
                workflow_type = WorkflowType.COMPREHENSIVE
            
            state = IntegratedGenerationState(
                content_requirements=prompt["content_requirements"],
                style_requirements=prompt["style_requirements"],
                structure_requirements=prompt["structure_requirements"],
                language_requirements=prompt["language_requirements"],
                formatting_requirements=prompt["formatting_requirements"],
                user_parameters=prompt["user_parameters"],
                max_tokens=preferences["maxTokens"],
                temperature=preferences["temperature"],
                model=preferences["model"],
                workflow_type=workflow_type,
                generation_id=f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(request)}"
            )
            
            # Add to job queue if using async processing
            if request.get("async", False):
                job_id = await self.job_queue.add_job(
                    job_type="content_generation",
                    job_data=asdict(state),
                    priority=request.get("priority", 0)
                )
                
                return {
                    "job_id": job_id,
                    "status": "queued",
                    "message": "Content generation job queued for processing"
                }
            
            # Get the appropriate workflow
            workflow = self.workflows.get(workflow_type, self.workflows[WorkflowType.COMPREHENSIVE])
            
            # Run the workflow
            final_state = await workflow.ainvoke(state)
            
            # Prepare comprehensive response
            if final_state.final_content:
                response = {
                    "content": final_state.final_content,
                    "metadata": {
                        "generation_id": final_state.generation_id,
                        "model_used": final_state.model,
                        "workflow_type": final_state.workflow_type.value,
                        "tokens_consumed": final_state.total_tokens_used,
                        "generation_time": (final_state.completed_at - final_state.started_at).total_seconds(),
                        "agent_steps": final_state.agent_steps,
                        "cache_hits": final_state.cache_hits,
                        "word_count": len(final_state.final_content.split()),
                        "sections": self._extract_sections_from_content(final_state.final_content),
                        "images": final_state.images,
                        "code_blocks": final_state.code_blocks,
                        "published_urls": final_state.published_urls,
                    },
                    "status": "success" if not final_state.errors else "partial",
                    "errors": final_state.errors if final_state.errors else None,
                }
                
                # Log successful generation to your analytics
                await self._log_generation_analytics(final_state)
                
                return response
            else:
                return {
                    "content": "",
                    "metadata": {
                        "generation_id": final_state.generation_id,
                        "agent_steps": final_state.agent_steps,
                        "workflow_type": final_state.workflow_type.value,
                    },
                    "status": "error",
                    "error": "Content generation failed",
                    "errors": final_state.errors,
                }
                
        except Exception as e:
            return {
                "content": "",
                "metadata": {
                    "generation_id": f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                },
                "status": "error",
                "error": f"Workflow execution failed: {str(e)}",
            }
    
    def _extract_sections_from_content(self, content: str) -> List[Dict]:
        """Extract sections from final content"""
        sections = []
        
        # Split by markdown headers
        import re
        section_pattern = r'^(#{1,6})\s+(.+?)$'
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            header_match = re.match(section_pattern, line)
            if header_match:
                # Save previous section
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_content).strip(),
                        "wordCount": len(' '.join(current_content).split())
                    })
                
                # Start new section
                current_section = header_match.group(2).strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add final section
        if current_section:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content).strip(),
                "wordCount": len(' '.join(current_content).split())
            })
        
        return sections
    
    async def _log_generation_analytics(self, state: IntegratedGenerationState):
        """Log generation analytics to your system"""
        try:
            analytics_data = {
                "generation_id": state.generation_id,
                "workflow_type": state.workflow_type.value,
                "model_used": state.model,
                "total_tokens": state.total_tokens_used,
                "generation_time": (state.completed_at - state.started_at).total_seconds(),
                "word_count": len(state.final_content.split()) if state.final_content else 0,
                "cache_hits": state.cache_hits,
                "agent_steps_count": len(state.agent_steps),
                "error_count": len(state.errors),
                "success": state.final_content is not None,
                "template_id": state.content_requirements.get("template_id"),
                "style_profile_id": state.style_requirements.get("profile_id"),
                "timestamp": state.completed_at
            }
            
            # Use your existing analytics system
            # await self.analytics_system.log_generation(analytics_data)
            
        except Exception as e:
            print(f"Failed to log analytics: {e}")
    
    async def get_workflow_status(self, generation_id: str) -> Dict[str, Any]:
        """Get status of a workflow (for async processing)"""
        try:
            # Check job queue status
            job_status = await self.job_queue.get_job_status(generation_id)
            
            if job_status:
                return {
                    "generation_id": generation_id,
                    "status": job_status["status"],
                    "progress": job_status.get("progress", 0),
                    "current_step": job_status.get("current_step", "unknown"),
                    "estimated_completion": job_status.get("estimated_completion"),
                    "result": job_status.get("result")
                }
            else:
                return {
                    "generation_id": generation_id,
                    "status": "not_found",
                    "error": "Generation ID not found"
                }
                
        except Exception as e:
            return {
                "generation_id": generation_id,
                "status": "error",
                "error": str(e)
            }
    
    async def list_available_workflows(self) -> List[Dict[str, Any]]:
        """List all available workflow types"""
        return [
            {
                "type": WorkflowType.SIMPLE.value,
                "name": "Simple Content Generation",
                "description": "Basic plan -> write -> edit -> format workflow",
                "estimated_time": "2-5 minutes",
                "best_for": ["Quick content", "Simple articles", "Basic documentation"]
            },
            {
                "type": WorkflowType.COMPREHENSIVE.value,
                "name": "Comprehensive Content Generation",
                "description": "Full pipeline with research, writing, editing, SEO, and formatting",
                "estimated_time": "5-10 minutes",
                "best_for": ["Blog posts", "Articles", "Marketing content", "Educational content"]
            },
            {
                "type": WorkflowType.RESEARCH_HEAVY.value,
                "name": "Research-Heavy Content",
                "description": "Deep research with semantic analysis and comprehensive writing",
                "estimated_time": "8-15 minutes",
                "best_for": ["Academic content", "Research reports", "In-depth analysis"]
            },
            {
                "type": WorkflowType.TECHNICAL.value,
                "name": "Technical Content Generation",
                "description": "Content generation with code examples and technical documentation",
                "estimated_time": "6-12 minutes",
                "best_for": ["Technical tutorials", "API documentation", "Programming guides"]
            },
            {
                "type": WorkflowType.VISUAL.value,
                "name": "Visual Content Generation",
                "description": "Content generation with image creation and visual elements",
                "estimated_time": "8-15 minutes",
                "best_for": ["Visual guides", "Infographic content", "Social media posts"]
            },
            {
                "type": WorkflowType.PUBLICATION_READY.value,
                "name": "Publication-Ready Content",
                "description": "Complete workflow with automatic publishing to platforms",
                "estimated_time": "10-20 minutes",
                "best_for": ["Blog publishing", "Social media campaigns", "Content distribution"]
            }
        ]

# Global integrated workflow instance
integrated_workflow = IntegratedContentWorkflow()
            