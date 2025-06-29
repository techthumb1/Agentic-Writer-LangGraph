import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, TypedDict
from datetime import datetime
import uuid
from pathlib import Path
import time

from .enhanced_model_registry import EnhancedModelRegistry
from .style_profile_loader import StyleProfileLoader
from .cache_system import ContentCacheManager
from .job_queue import JobQueue, Job

# Import enhanced agents
from .agents.enhanced_planner import IntelligentPlannerAgent
from .agents.enhanced_researcher import IntelligentResearcherAgent  
from .agents.enhanced_editor import IntelligentEditorAgent
from .agents.enhanced_seo_agent import IntelligentSEOAgent
from .agents.enhanced_publisher import IntelligentPublisherAgent
from .agents.writer import InnovativeWriterAgent
#from .agents.enhanced_image_agent import IntelligentImageAgent



logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """Complete state for enterprise workflow"""
    # Input data
    template_id: str
    style_profile: str
    parameters: Dict[str, Any]
    generation_id: str
    
    # Content progression
    content: str
    outline: Dict[str, Any]
    research_data: Dict[str, Any]
    draft_content: str
    edited_content: str
    seo_metadata: Dict[str, Any]
    
    # Workflow management
    current_agent: str
    completed_agents: List[str]
    failed_agents: List[str]
    overall_progress: float
    step_progress: Dict[str, float]
    
    # System data
    template_data: Dict[str, Any]
    style_data: Dict[str, Any]
    model_config: Dict[str, Any]
    
    # Results
    final_content: str
    metadata: Dict[str, Any]
    quality_score: Dict[str, Any]
    errors: List[Dict[str, Any]]

class EnhancedOrchestrator:
    """Enterprise orchestrator with real agent integration"""

    def __init__(self):
        self.model_registry = EnhancedModelRegistry()
        self.style_loader = StyleProfileLoader()
        self.cache_manager: Optional[ContentCacheManager] = None
        self.job_queue: Optional[JobQueue] = None

        # Initialize workflow graph
        self.workflow = self._create_workflow()

        # Enhanced agent instances
        self.agents = {
            "planner": IntelligentPlannerAgent(),
            "researcher": IntelligentResearcherAgent(),
            "writer": InnovativeWriterAgent(),
            "editor": IntelligentEditorAgent(),
            "seo_optimizer": IntelligentSEOAgent(),
            "publisher": IntelligentPublisherAgent()
        }

    def _create_workflow(self):
        """Create the LangGraph workflow with enhanced agents"""
        from langgraph.graph import StateGraph, END

        # Import enhanced agents only
        available_agents = {}

        # Try to import each enhanced agent individually
        try:
            from .agents.enhanced_planner import planner
            available_agents['planner'] = planner
            logger.debug("✅ Enhanced planner imported")
        except ImportError as e:
            logger.warning(f"Enhanced planner not available: {e}")

        try:
            from .agents.enhanced_researcher import researcher
            available_agents['researcher'] = researcher
            logger.debug("✅ Enhanced researcher imported")
        except ImportError as e:
            logger.warning(f"Enhanced researcher not available: {e}")

        try:
            from .agents.writer import writer  # ✅ RunnableLambda function
            available_agents['writer'] = writer
            logger.debug("✅ Enhanced writer imported")
        except ImportError as e:
            logger.warning(f"Enhanced writer not available: {e}")

        try:
            from .agents.enhanced_editor import editor
            available_agents['editor'] = editor
            logger.debug("✅ Enhanced editor imported")
        except ImportError as e:
            logger.warning(f"Enhanced editor not available: {e}")

        try:
            from .agents.enhanced_seo_agent import seo_agent
            available_agents['seo_agent'] = seo_agent
            logger.debug("✅ Enhanced SEO agent imported")
        except ImportError as e:
            logger.warning(f"Enhanced SEO agent not available: {e}")

        try:
            from .agents.enhanced_publisher import publisher
            available_agents['publisher'] = publisher
            logger.debug("✅ Enhanced publisher imported")
        except ImportError as e:
            logger.warning(f"Enhanced publisher not available: {e}")

        try:
            from .agents.enhanced_image_agent import image_agent
            available_agents['image_agent'] = image_agent
            logger.debug("✅ Enhanced image agent imported")
        except ImportError as e:
            logger.debug(f"Enhanced image agent not available: {e}")

        # Check if we have minimum required agents
        required_agents = ['planner', 'writer']
        missing_required = [agent for agent in required_agents if agent not in available_agents]

        if missing_required:
            logger.error(f"Missing required enhanced agents: {missing_required}")
            # Create minimal workflow that just returns input
            workflow = StateGraph(dict)
            workflow.add_node("minimal", lambda state: {
                **state,
                "draft": f"Error: Missing required agents: {missing_required}",
                "status": "error"
            })
            workflow.set_entry_point("minimal")
            workflow.set_finish_point("minimal")
            return workflow.compile()

        # Create the workflow graph
        workflow = StateGraph(dict)

        # Add available agents as nodes
        for agent_name, agent_func in available_agents.items():
            workflow.add_node(agent_name, agent_func)
            logger.debug(f"Added {agent_name} to workflow")

        # Build workflow path based on available agents
        workflow_path = []

        # Define optimal agent sequence
        preferred_sequence = [
            'planner', 'researcher', 'writer', 'editor', 
            'seo_agent', 'image_agent', 'publisher'
        ]

        # Build path from available agents in preferred order
        for agent_name in preferred_sequence:
            if agent_name in available_agents:
                workflow_path.append(agent_name)

        if not workflow_path:
            logger.error("No agents available for workflow")
            # Return minimal workflow
            workflow.add_node("error", lambda state: {
                **state, 
                "error": "No enhanced agents available",
                "status": "failed"
            })
            workflow.set_entry_point("error")
            workflow.set_finish_point("error")
            return workflow.compile()

        # Set entry point
        workflow.set_entry_point(workflow_path[0])

        # Add edges between consecutive agents
        for i in range(len(workflow_path) - 1):
            current_agent = workflow_path[i]
            next_agent = workflow_path[i + 1]
            workflow.add_edge(current_agent, next_agent)
            logger.debug(f"Added edge: {current_agent} -> {next_agent}")

        # End workflow after last agent
        if workflow_path:
            workflow.add_edge(workflow_path[-1], END)
            logger.debug(f"Added end edge from {workflow_path[-1]}")

        # Compile and return
        compiled_workflow = workflow.compile()
        logger.info(f"✅ Enhanced workflow created with {len(workflow_path)} agents: {' -> '.join(workflow_path)}")

        return compiled_workflow

    def _should_continue_to_agent(self, state: Dict[str, Any], agent_name: str) -> bool:
        """Determine if workflow should continue to specific agent"""

        # Check if agent is enabled in dynamic parameters
        dynamic_params = state.get("dynamic_parameters", {})

        # Agent-specific checks
        if agent_name == "image_agent":
            return dynamic_params.get("generate_images", False)
        elif agent_name == "publisher":
            return dynamic_params.get("auto_publish", False)
        elif agent_name == "seo_agent":
            return dynamic_params.get("optimize_seo", True)  # Default true

        return True  # Default to continuing

    def _create_conditional_workflow(self):
        """Create workflow with conditional routing (advanced)"""
        from langgraph.graph import StateGraph, END

        # This is for more advanced conditional routing
        # For now, use the simple linear workflow above
        return self._create_workflow()

    def _prepare_agent_state(self, state: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """Prepare state for specific agent"""

        # Add agent-specific metadata
        agent_state = state.copy()
        agent_state["current_agent"] = agent_name
        agent_state["agent_start_time"] = time.time()

        # Agent-specific state preparation
        if agent_name == "planner":
            # Planner needs topic and parameters
            agent_state["planning_request"] = {
                "topic": state.get("topic"),
                "requirements": state.get("dynamic_parameters", {})
            }

        elif agent_name == "researcher":
            # Researcher needs research guidance from planner
            agent_state["research_requirements"] = state.get("research_guidance", {})

        elif agent_name == "writer":
            # Writer needs content plan and research data
            agent_state["writing_guidance"] = {
                "plan": state.get("content_plan", {}),
                "research": state.get("research_results", {}),
                "style": state.get("style_guidance", {})
            }

        elif agent_name == "editor":
            # Editor needs draft content and editing guidelines
            agent_state["editing_input"] = {
                "draft": state.get("draft", ""),
                "guidelines": state.get("style_guidance", {})
            }

        elif agent_name == "seo_agent":
            # SEO agent needs content and optimization requirements
            agent_state["seo_input"] = {
                "content": state.get("edited_draft", state.get("draft", "")),
                "requirements": state.get("seo_guidance", {})
            }

        elif agent_name == "image_agent":
            # Image agent needs content and visual requirements
            agent_state["image_requirements"] = {
                "content": state.get("formatted_content", ""),
                "topic": state.get("topic", ""),
                "style": state.get("style_guidance", {})
            }

        elif agent_name == "publisher":
            # Publisher needs final content and publishing settings
            agent_state["publishing_content"] = {
                "content": state.get("formatted_content", ""),
                "metadata": state.get("seo_metadata", {}),
                "images": state.get("generated_images", {}),
                "settings": state.get("dynamic_parameters", {})
            }

        return agent_state

    def set_cache_manager(self, cache_manager: ContentCacheManager):
        """Set cache manager for content caching"""
        self.cache_manager = cache_manager

    def set_job_queue(self, job_queue: JobQueue):
        """Set job queue for async processing"""
        self.job_queue = job_queue

    def _calculate_quality_score(self, state: AgentState) -> Dict[str, Any]:
        """Calculate content quality score"""
        score = {
            "overall": 75,  # Base score
            "completeness": 80,
            "coherence": 75,
            "style_adherence": 70,
            "technical_accuracy": 80
        }

        # Adjust based on successful agents
        if "researcher" in state["completed_agents"]:
            score["technical_accuracy"] += 10
        if "editor" in state["completed_agents"]:
            score["coherence"] += 10
            score["completeness"] += 5
        if "seo_optimizer" in state["completed_agents"]:
            score["style_adherence"] += 10

        # Penalize for failed agents
        score["overall"] -= len(state["failed_agents"]) * 10

        # Ensure bounds
        for key in score:
            score[key] = max(0, min(100, score[key]))

        # Calculate overall as average
        score["overall"] = sum(v for k, v in score.items() if k != "overall") / (len(score) - 1)

        return score

    async def generate_content(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main content generation entry point"""

        try:
            # Create initial state
            initial_state = {
                "template_id": request_data["template"],
                "style_profile": request_data["style_profile"],
                "parameters": request_data.get("dynamic_parameters", {}),
                "generation_id": str(uuid.uuid4()),
                "content": "",
                "current_agent": "initialize",
                "completed_agents": [],
                "failed_agents": [],
                "overall_progress": 0.0,
                "step_progress": {},
                "errors": [],
                "metadata": {}
            }

            # Execute workflow
            final_state = await self.workflow.ainvoke(
                initial_state,
                config={"thread_id": initial_state["generation_id"]}
            )

            # Return result
            return {
                "success": True,
                "content": final_state.get("final_content", ""),
                "metadata": final_state.get("metadata", {}),
                "quality_score": final_state.get("quality_score", {}),
                "generation_id": final_state["generation_id"]
            }

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "generation_id": request_data.get("generation_id", "unknown")
            }

    async def _initialize_state(self, state: AgentState) -> AgentState:
        """Initialize workflow state"""
        state["step_progress"]["initialize"] = 100.0
        state["overall_progress"] = 5.0
        state["current_agent"] = "load_templates"
        return state

    async def _load_templates(self, state: AgentState) -> AgentState:
        """Load template and style profile data"""
        try:
            # Load template data
            template_data = await self.style_loader.load_template(state["template_id"])
            if not template_data:
                raise Exception(f"Template not found: {state['template_id']}")

            # Load style profile data  
            style_data = await self.style_loader.load_style_profile(state["style_profile"])
            if not style_data:
                raise Exception(f"Style profile not found: {state['style_profile']}")

            state["template_data"] = template_data
            state["style_data"] = style_data
            state["step_progress"]["load_templates"] = 100.0
            state["overall_progress"] = 10.0
            state["current_agent"] = "check_cache"

            return state

        except Exception as e:
                    logger.error(f"Template loading failed: {e}")
                    state["errors"].append({
                        "agent": "load_templates",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                    raise
        
    async def _check_cache(self, state: AgentState) -> AgentState:
        """Check for cached content"""
        try:
            cached = await self.cache_manager.get_cached_content(
                template_id=state["template_id"],
                style_profile=state["style_profile"],
                parameters=state["parameters"],
                model_name=self.model_registry.get_default_model()
            )
            state["cached_content"] = cached
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            state["cached_content"] = None

        state["step_progress"]["check_cache"] = 100.0
        state["current_agent"] = "plan" if not state["cached_content"] else "finalize"
        return state

    def _should_use_cache(self, state: AgentState) -> str:
        """Decide whether to use cached content"""
        return "use_cache" if state.get("cached_content") else "generate_new"
    async def _execute_planner(self, state: AgentState) -> AgentState:
        """Execute intelligent planning agent"""
        try:
            planner = self.agents["planner"]
            # Convert orchestrator state to planner format
            planner_state = self._create_agent_state(state, "planner")
            # Call planner's actual method
            result = planner.intelligent_plan(planner_state)
            # Extract planning results
            state["outline"] = result.get("content_plan", {})
            state["metadata"].update(result.get("metadata", {}))
            state["completed_agents"].append("planner")
            state["step_progress"]["plan"] = 100.0
            state["overall_progress"] = 25.0
            state["current_agent"] = "research"
            return state
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            state["failed_agents"].append("planner")
            state["errors"].append({
                "agent": "planner",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
        
    async def _execute_researcher(self, state: AgentState) -> AgentState:
        """Execute intelligent research agent"""
        try:
            researcher = self.agents["researcher"]
            # Convert orchestrator state to researcher format
            researcher_state = self._create_agent_state(state, "researcher")
            # Call researcher's actual method
            result = await researcher.conduct_intelligent_research(researcher_state)
            # Extract research results
            state["research_data"] = result.get("research", {})
            state["metadata"].update(result.get("research_metadata", {}))
            state["completed_agents"].append("researcher")
            state["step_progress"]["research"] = 100.0
            state["overall_progress"] = 45.0
            state["current_agent"] = "write"
            return state
        except Exception as e:
            logger.error(f"Research failed: {e}")
            state["failed_agents"].append("researcher")
            state["errors"].append({
                "agent": "researcher", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
        
    async def _execute_writer(self, state: AgentState) -> AgentState:
        """Execute innovative writer agent"""
        try:
            writer = self.agents["writer"]
            # Convert orchestrator state to writer format
            writer_state = self._create_agent_state(state, "writer")
            # Call writer's actual method
            result = writer.generate_adaptive_content(writer_state)
            # Extract writing results
            state["draft_content"] = result.get("draft", "")
            state["content"] = result.get("draft", "")
            state["metadata"].update(result.get("metadata", {}))
            # Store innovation report
            if "innovation_report" in result:
                state["metadata"]["innovation_report"] = result["innovation_report"]
            state["completed_agents"].append("writer")
            state["step_progress"]["write"] = 100.0
            state["overall_progress"] = 65.0
            state["current_agent"] = "edit"
            return state
        except Exception as e:
            logger.error(f"Writing failed: {e}")
            state["failed_agents"].append("writer")
            state["errors"].append({
                "agent": "writer",
                "error": str(e), 
                "timestamp": datetime.now().isoformat()
            })
            raise
        
    async def _execute_editor(self, state: AgentState) -> AgentState:
        """Execute intelligent editor agent"""
        try:
            editor = self.agents["editor"]
            # Convert orchestrator state to editor format
            editor_state = self._create_agent_state(state, "editor")
            # Call editor's actual method
            result = editor.intelligent_edit(editor_state)
            # Extract editing results
            state["edited_content"] = result.get("edited_draft", "")
            state["content"] = result.get("edited_draft", "")
            state["metadata"].update(result.get("editing_metadata", {}))
            state["completed_agents"].append("editor")
            state["step_progress"]["edit"] = 100.0
            state["overall_progress"] = 80.0
            state["current_agent"] = "seo_optimize"
            return state
        except Exception as e:
            logger.error(f"Editing failed: {e}")
            state["failed_agents"].append("editor")
            state["errors"].append({
                "agent": "editor",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
        
    async def _execute_seo(self, state: AgentState) -> AgentState:
        """Execute intelligent SEO optimization agent"""
        try:
            seo_agent = self.agents["seo_optimizer"]
            # Convert orchestrator state to SEO format
            seo_state = self._create_agent_state(state, "seo")
            # Call SEO agent's actual method
            result = await seo_agent.optimize_content(seo_state)
            # Extract SEO results
            if result.get("seo_optimized_content"):
                state["content"] = result["seo_optimized_content"]
            state["seo_metadata"] = result.get("seo_metadata", {})
            state["metadata"].update(result.get("seo_metadata", {}))
            state["completed_agents"].append("seo_optimizer")
            state["step_progress"]["seo_optimize"] = 100.0
            state["overall_progress"] = 95.0
            state["current_agent"] = "finalize"
            return state
        except Exception as e:
            logger.error(f"SEO optimization failed: {e}")
            state["failed_agents"].append("seo_optimizer")
            state["errors"].append({
                "agent": "seo_optimizer",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            # SEO is optional, continue workflow
            state["current_agent"] = "finalize"
            return state
    async def _finalize_content(self, state: AgentState) -> AgentState:
        """Finalize content and prepare results"""
        try:
            # Use cached content if available
            if state.get("cached_content"):
                cached = state["cached_content"]
                state["final_content"] = cached.content
                state["metadata"] = cached.metadata
                state["quality_score"] = {"overall": 90, "source": "cache"}
                state["overall_progress"] = 100.0
                logger.info(f"Using cached content for {state['generation_id']}")
            else:
                # Use generated content
                state["final_content"] = state.get("edited_content") or state.get("draft_content") or state.get("content", "")
                # Compile metadata
                state["metadata"] = {
                    "generation_id": state["generation_id"],
                    "template_id": state["template_id"],
                    "style_profile": state["style_profile"],
                    "completed_agents": state["completed_agents"],
                    "failed_agents": state["failed_agents"],
                    "generation_time": datetime.now().isoformat(),
                    "word_count": len(state["final_content"].split()),
                    "seo_metadata": state.get("seo_metadata", {}),
                    "parameters": state["parameters"]
                }
                # Calculate quality score
                state["quality_score"] = self._calculate_quality_score(state)
                state["overall_progress"] = 100.0
            state["step_progress"]["finalize"] = 100.0
            state["current_agent"] = "cache_result"
            return state
        except Exception as e:
            logger.error(f"Finalization failed: {e}")
            state["errors"].append({
                "agent": "finalize",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
        
    async def _cache_result(self, state: AgentState) -> AgentState:
        """Cache the generated content"""
        if self.cache_manager and not state.get("cached_content"):
            try:
                await self.cache_manager.cache_content(
                    template_id=state["template_id"],
                    style_profile=state["style_profile"],
                    parameters=state["parameters"],
                    model_name=self.model_registry.get_default_model(),
                    content=state["final_content"],
                    metadata=state["metadata"]
                )
                logger.info(f"Cached content for {state['generation_id']}")
            except Exception as e:
                logger.warning(f"Failed to cache content: {e}")
        state["step_progress"]["cache_result"] = 100.0
        return state
    def _create_agent_state(self, orchestrator_state: AgentState, agent_type: str) -> Dict[str, Any]:
        """Convert orchestrator state to agent-specific format"""
        # Base agent state with legacy compatibility
        agent_state = {
            # Legacy fields for compatibility
            "templateId": orchestrator_state["template_id"],
            "styleProfileId": orchestrator_state["style_profile"],
            "style_profile": orchestrator_state["style_profile"],
            "dynamic_parameters": orchestrator_state["parameters"],
            # Rich context from template and style data
            "template_data": orchestrator_state.get("template_data", {}),
            "style_data": orchestrator_state.get("style_data", {}),
            # Content progression
            "topic": (orchestrator_state["parameters"].get("topic") or 
                     orchestrator_state.get("template_data", {}).get("title", "Untitled")),
        }
        return agent_state

# Extension to style_profile_loader for template support
class EnhancedStyleProfileLoader(StyleProfileLoader):
    """Extended loader with template support"""
    
    def __init__(self):
        super().__init__()
        self.templates_cache: Dict[str, Dict[str, Any]] = {}
        self.templates_path: Optional[Path] = None
        self._find_and_load_templates()
    
    def _find_and_load_templates(self):
        """Find and load content templates"""
        from pathlib import Path
        
        cwd = Path.cwd()
        search_paths = [
            cwd / "data" / "content_templates",
            cwd / "content_templates", 
            cwd / ".." / "data" / "content_templates",
            cwd / "frontend" / "content-templates"
        ]
        
        for path in search_paths:
            resolved_path = path.resolve()
            if resolved_path.exists() and resolved_path.is_dir():
                yaml_files = list(resolved_path.glob("*.yaml")) + list(resolved_path.glob("*.yml"))
                
                if yaml_files:
                    logger.info(f"Found templates directory: {resolved_path}")
                    self.templates_path = resolved_path
                    self._load_templates_from_directory(resolved_path)
                    return
        
        logger.warning("No content templates directory found")
    
    def _load_templates_from_directory(self, directory: Path):
        """Load all template YAML files"""
        import yaml
        
        yaml_files = list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))
        loaded_count = 0
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                
                if template_data:
                    template_name = yaml_file.stem
                    self.templates_cache[template_name] = template_data
                    loaded_count += 1
                    
            except Exception as e:
                logger.error(f"Error loading template {yaml_file.name}: {e}")
        
        logger.info(f"Successfully loaded {loaded_count} content templates")
    
    async def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Load a specific content template"""
        if template_id not in self.templates_cache:
            logger.warning(f"Template '{template_id}' not found")
            return None
        return self.templates_cache[template_id]
    
    async def load_style_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Load a style profile (async version)"""
        return self.get_profile(profile_name)
    
    async def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all available templates with metadata"""
        templates = []
        for template_id, template_data in self.templates_cache.items():
            template_info = {
                "id": template_id,
                "name": template_data.get("name", template_id),
                "description": template_data.get("description", ""),
                "category": template_data.get("category", "general"),
                "sections": template_data.get("sections", []),
                "metadata": template_data.get("metadata", {}),
                "filename": f"{template_id}.yaml"
            }
            templates.append(template_info)
        return templates
    
    async def get_all_style_profiles(self) -> List[Dict[str, Any]]:
        """Get all available style profiles with metadata"""
        profiles = []
        for profile_id, profile_data in self.profiles_cache.items():
            profile_info = {
                "id": profile_id,
                "name": profile_data.get("name", profile_id),
                "description": profile_data.get("description", ""),
                "category": profile_data.get("category", "general"),
                "tone": profile_data.get("writing_style", {}).get("tone", ""),
                "voice": profile_data.get("writing_style", {}).get("voice", ""),
                "structure": profile_data.get("content_structure", {}).get("structure", ""),
                "system_prompt": profile_data.get("system_prompt", ""),
                "settings": profile_data.get("settings", {}),
                "filename": f"{profile_id}.yaml"
            }
            profiles.append(profile_info)
        return profiles

# Factory function for creating orchestrator
async def create_enhanced_orchestrator(
    cache_manager: Optional[ContentCacheManager] = None,
    job_queue: Optional[JobQueue] = None
) -> EnhancedOrchestrator:
    """Create enhanced orchestrator with dependencies"""
    
    orchestrator = EnhancedOrchestrator()
    
    if cache_manager:
        orchestrator.set_cache_manager(cache_manager)
    
    if job_queue:
        orchestrator.set_job_queue(job_queue)
    
    return orchestrator

# Integration with job queue
async def register_orchestrator_tasks(job_manager, orchestrator: EnhancedOrchestrator):
    """Register orchestrator tasks with job queue"""
    from .job_queue import task_registry
    
    @task_registry.register("enhanced_content_generation")
    async def enhanced_content_task(job: Job, progress_callback: Callable):
        """Enhanced content generation task"""
        params = job.parameters
        
        # Update progress through workflow
        def update_progress(progress: float, metadata: Dict = None):
            asyncio.create_task(progress_callback(progress, metadata))
        
        # Execute through orchestrator
        result = await orchestrator.generate_content(params)
        
        if result["success"]:
            return {
                "content": result["content"],
                "metadata": result["metadata"],
                "quality_score": result.get("quality_score", {}),
                "generation_id": result["generation_id"]
            }
        else:
            raise Exception(result.get("error", "Unknown generation error"))
    
    logger.info("Registered enhanced orchestrator tasks with job queue")