# File: langgraph_app/enhanced_orchestration.py
# COMPLETE FIX - Works with your existing 11-agent system + eliminates generic content

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, TypedDict
from datetime import datetime
import uuid
from pathlib import Path
import time

from .style_patch import patch_existing_orchestrator
from .enhanced_model_registry import EnhancedModelRegistry, ModelTier
from .style_profile_loader import StyleProfileLoader
from .cache_system import ContentCacheManager
from .job_queue import JobQueue, Job
from .style_enforcement import StyleProfileEnforcer, apply_style_enforcement
from .agent_coordination import AgentCoordinator, enhance_agent_with_coordination

patch_existing_orchestrator()

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """Complete state for enterprise workflow"""
    # Input data
    template_id: str
    generation_id: str
    style_profile: str
    parameters: Dict[str, Any]
    
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
    
    # Enhanced coordination
    agent_context: Any  # AgentContext object
    coordination_prompt: str
    style_enforcement_prompt: str
    
    # Results
    final_content: str
    metadata: Dict[str, Any]
    quality_score: Dict[str, Any]
    errors: List[Dict[str, Any]]

class EnhancedOrchestrator:
    """Enterprise orchestrator with FIXED agent integration and style enforcement"""

    def __init__(self):
        self.model_registry = EnhancedModelRegistry()
        self.style_loader = StyleProfileLoader()
        self.style_enforcer = StyleProfileEnforcer()
        self.coordinator = AgentCoordinator()
        self.cache_manager: Optional[ContentCacheManager] = None
        self.job_queue: Optional[JobQueue] = None 

        # Initialize workflow graph with FIXED imports
        self.workflow = self._create_workflow()

    def _create_workflow(self):
        """Create the LangGraph workflow with CORRECTED agent imports"""
        from langgraph.graph import StateGraph, END

        # Import enhanced agents using the CORRECT format
        available_agents = {}

        # Try to import each enhanced agent individually with FIXED imports
        try:
            from .agents.enhanced_planner import IntelligentPlannerAgent
            # Create wrapper function for LangGraph compatibility
            async def planner_wrapper(state: dict) -> dict:
                planner = IntelligentPlannerAgent()
                context = self.coordinator.create_agent_context(state, 'planner')
                enhanced_state = {**state, 'agent_context': context}
                return planner.intelligent_plan(enhanced_state)
            
            available_agents['planner'] = planner_wrapper
            logger.debug("✅ Enhanced planner imported and wrapped")
        except ImportError as e:
            logger.warning(f"Enhanced planner not available: {e}")

        try:
            from .agents.enhanced_researcher import IntelligentResearcherAgent
            async def researcher_wrapper(state: dict) -> dict:
                researcher = IntelligentResearcherAgent()
                context = self.coordinator.create_agent_context(state, 'researcher')
                enhanced_state = {**state, 'agent_context': context}
                return await researcher.conduct_intelligent_research(enhanced_state)
            
            available_agents['researcher'] = researcher_wrapper
            logger.debug("✅ Enhanced researcher imported and wrapped")
        except ImportError as e:
            logger.warning(f"Enhanced researcher not available: {e}")

        try:
            from .agents.writer import InnovativeWriterAgent
            async def writer_wrapper(state: dict) -> dict:
                writer = InnovativeWriterAgent()
                context = self.coordinator.create_agent_context(state, 'writer')
                
                # Apply style enforcement
                style_prompt = self.style_enforcer.create_style_prompt(
                    state.get('style_profile', 'professional')
                )
                
                enhanced_state = {
                    **state, 
                    'agent_context': context,
                    'style_enforcement_prompt': style_prompt
                }
                
                result = writer.generate_adaptive_content(enhanced_state)
                
                # Validate and fix style violations
                if 'draft' in result:
                    validation = self.style_enforcer.validate_content(
                        result['draft'], 
                        state.get('style_profile', 'professional')
                    )
                    
                    if not validation['is_valid']:
                        logger.warning(f"Style violations in writer output: {validation['violations']}")
                        result['draft'] = self.style_enforcer.fix_content(
                            result['draft'], 
                            state.get('style_profile', 'professional')
                        )
                        result['style_validation'] = validation
                
                return result
            
            available_agents['writer'] = writer_wrapper
            logger.debug("✅ Enhanced writer imported and wrapped with style enforcement")
        except ImportError as e:
            logger.warning(f"Enhanced writer not available: {e}")

        try:
            from .agents.enhanced_editor import IntelligentEditorAgent
            async def editor_wrapper(state: dict) -> dict:
                editor = IntelligentEditorAgent()
                context = self.coordinator.create_agent_context(state, 'editor')
                enhanced_state = {**state, 'agent_context': context}
                
                result = editor.intelligent_edit(enhanced_state)
                
                # Apply style enforcement to edited content
                if 'edited_draft' in result:
                    validation = self.style_enforcer.validate_content(
                        result['edited_draft'], 
                        state.get('style_profile', 'professional')
                    )
                    
                    if not validation['is_valid']:
                        result['edited_draft'] = self.style_enforcer.fix_content(
                            result['edited_draft'], 
                            state.get('style_profile', 'professional')
                        )
                
                return result
            
            available_agents['editor'] = editor_wrapper
            logger.debug("✅ Enhanced editor imported and wrapped")
        except ImportError as e:
            logger.warning(f"Enhanced editor not available: {e}")

        try:
            from .agents.enhanced_seo_agent import IntelligentSEOAgent
            async def seo_wrapper(state: dict) -> dict:
                seo_agent = IntelligentSEOAgent()
                context = self.coordinator.create_agent_context(state, 'seo_agent')
                enhanced_state = {**state, 'agent_context': context}
                return await seo_agent.optimize_content(enhanced_state)
            
            available_agents['seo_agent'] = seo_wrapper
            logger.debug("✅ Enhanced SEO agent imported and wrapped")
        except ImportError as e:
            logger.warning(f"Enhanced SEO agent not available: {e}")

        try:
            from .agents.enhanced_formatter import IntelligentFormatterAgent
            async def formatter_wrapper(state: dict) -> dict:
                formatter = IntelligentFormatterAgent()
                context = self.coordinator.create_agent_context(state, 'formatter')
                enhanced_state = {**state, 'agent_context': context}
                return formatter.intelligent_format(enhanced_state)
            
            available_agents['formatter'] = formatter_wrapper
            logger.debug("✅ Enhanced formatter imported and wrapped")
        except ImportError as e:
            logger.warning(f"Enhanced formatter not available: {e}")

        # Check if we have minimum required agents
        required_agents = ['writer']  # At minimum, we need a writer
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
            'seo_agent', 'formatter'
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

    async def initialize_with_sota_models(self):
        """Initialize with state-of-the-art model configurations"""
        
        # Configure provider settings for maximum quality
        provider_configs = {
            "openai": {
                "api_key": None,  # Will use environment variable
                "default_model": "gpt-4o",
                "fallback_model": "gpt-4o-mini"
            },
            "anthropic": {
                "api_key": None,  # Will use environment variable  
                "default_model": "claude-3-5-sonnet-20241022",
                "fallback_model": "claude-3-haiku-20240307"
            }
        }
        
        await self.model_registry.initialize_providers(provider_configs)
        logger.info("Model registry initialized with SOTA models")

    def set_cache_manager(self, cache_manager: ContentCacheManager):
        """Set cache manager for content caching"""
        self.cache_manager = cache_manager

    def set_job_queue(self, job_queue: JobQueue):
        """Set job queue for async processing"""
        self.job_queue = job_queue

    def _calculate_quality_score(self, state: AgentState) -> Dict[str, Any]:
        """Calculate enhanced content quality score"""
        base_score = 60  # Start lower to encourage improvement
        
        score = {
            "overall": base_score,
            "completeness": 70,
            "coherence": 70,
            "style_adherence": 60,
            "technical_accuracy": 70,
            "originality": 50  # Start low, increase based on validation
        }

        # Adjust based on successful agents
        if "planner" in state["completed_agents"]:
            score["coherence"] += 10
            score["completeness"] += 5
        if "researcher" in state["completed_agents"]:
            score["technical_accuracy"] += 15
            score["originality"] += 10
        if "writer" in state["completed_agents"]:
            score["originality"] += 15
            score["style_adherence"] += 10
        if "editor" in state["completed_agents"]:
            score["coherence"] += 15
            score["style_adherence"] += 20
        if "seo_agent" in state["completed_agents"]:
            score["completeness"] += 10

        # Check for style validation results
        if "style_validation" in state.get("metadata", {}):
            validation = state["metadata"]["style_validation"]
            score["style_adherence"] = validation.get("compliance_score", 60)

        # Penalize for failed agents more heavily
        score["overall"] -= len(state["failed_agents"]) * 15

        # Ensure bounds
        for key in score:
            score[key] = max(0, min(100, score[key]))

        # Calculate overall as weighted average
        weights = {
            "completeness": 0.2,
            "coherence": 0.25,
            "style_adherence": 0.25,
            "technical_accuracy": 0.15,
            "originality": 0.15
        }
        
        score["overall"] = sum(
            score[metric] * weight 
            for metric, weight in weights.items()
        )

        return score

    async def generate_content(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main content generation entry point with enhanced quality control"""
        try:
            generation_id = str(uuid.uuid4())
            logger.info(f"Starting enhanced content generation: {generation_id}")

            # Initialize models if not done
            if not self.model_registry.providers:
                await self.initialize_with_sota_models()

            # Create initial state with enhanced context
            initial_state = {
                "template_id": request_data["template"],
                "style_profile": request_data["style_profile"],
                "parameters": request_data.get("dynamic_parameters", {}),
                "content": "",
                "current_agent": "initialize",
                "completed_agents": [],
                "failed_agents": [],
                "overall_progress": 0.0,
                "step_progress": {},
                "errors": [],
                "metadata": {},
                "generation_id": generation_id,
                
                # Enhanced fields
                "topic": request_data.get("dynamic_parameters", {}).get("topic", "Untitled Content"),
                "audience": request_data.get("dynamic_parameters", {}).get("audience", "general"),
                "content_type": "article"
            }

            # Load and validate style profile
            style_profile_data = self.style_loader.get_profile(request_data["style_profile"])
            if not style_profile_data:
                logger.warning(f"Style profile not found: {request_data['style_profile']}")
                style_profile_data = self.style_enforcer._get_fallback_profile(request_data["style_profile"])
            
            initial_state["style_data"] = style_profile_data

            # Execute enhanced workflow
            logger.info(f"Executing workflow for generation: {generation_id}")
            final_state = await self.workflow.ainvoke(
                initial_state,
                config={"thread_id": generation_id}
            )

            # Extract content with priority order (SEO > edited > draft > content)
            raw_content = (
                final_state.get("seo_optimized_content") or 
                final_state.get("formatted_content") or
                final_state.get("edited_draft") or          
                final_state.get("draft") or                 
                final_state.get("content") or 
                ""
            )
            
            # Clean markdown wrapper if present
            content = self._clean_content(raw_content)

            # Final style validation
            if content and request_data["style_profile"]:
                final_validation = self.style_enforcer.validate_content(
                    content, request_data["style_profile"]
                )
                
                if not final_validation['is_valid']:
                    logger.warning(f"Final content has style violations: {final_validation['violations']}")
                    content = self.style_enforcer.fix_content(
                        content, request_data["style_profile"]
                    )
                
                final_state["metadata"]["final_style_validation"] = final_validation

            # Enhanced metadata compilation
            metadata = {
                "generation_id": generation_id,
                "template_id": request_data["template"],
                "style_profile": request_data["style_profile"],
                "completed_agents": final_state.get("completed_agents", []),
                "failed_agents": final_state.get("failed_agents", []),
                "generation_time": datetime.now().isoformat(),
                "word_count": len(content.split()) if content else 0,
                "character_count": len(content) if content else 0,
                "seo_metadata": final_state.get("seo_metadata", {}),
                "parameters": request_data.get("dynamic_parameters", {}),
                "model_usage": final_state.get("model_usage", {}),
                "style_enforcement": final_state.get("style_validation", {}),
                "agent_performance": final_state.get("agent_performance", {})
            }

            # Calculate enhanced quality score
            quality_score = self._calculate_quality_score(final_state)

            # Log generation results
            logger.info(f"Content generation completed: {generation_id}")
            logger.info(f"Quality score: {quality_score['overall']:.1f}")
            logger.info(f"Word count: {metadata['word_count']}")
            logger.info(f"Completed agents: {metadata['completed_agents']}")

            return {
                "success": True,
                "content": content,
                "metadata": metadata,
                "quality_score": quality_score,
                "generation_id": generation_id
            }

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "generation_id": request_data.get("generation_id", str(uuid.uuid4())),
                "content": "",
                "metadata": {},
                "quality_score": {}
            }

    def _clean_content(self, content: str) -> str:
        """Clean content of markdown wrappers and formatting artifacts"""
        if not isinstance(content, str):
            return ""
            
        # Remove markdown code block wrappers
        if content.startswith('```markdown\n'):
            content = content.replace('```markdown\n', '', 1).replace('\n```', '')
        elif content.startswith('```markdown'):
            content = content.replace('```markdown', '', 1).replace('```', '')
        elif content.startswith('```'):
            lines = content.split('\n')
            if len(lines) > 1 and lines[0].startswith('```'):
                content = '\n'.join(lines[1:])
                if content.endswith('\n```'):
                    content = content[:-4]
                elif content.endswith('```'):
                    content = content[:-3]
        
        return content.strip()

# Factory function for creating orchestrator
async def create_enhanced_orchestrator(
    cache_manager: Optional[ContentCacheManager] = None,
    job_queue: Optional[JobQueue] = None
) -> EnhancedOrchestrator:
    """Create enhanced orchestrator with dependencies and SOTA models"""
    
    orchestrator = EnhancedOrchestrator()
    
    # Initialize with state-of-the-art models
    await orchestrator.initialize_with_sota_models()
    
    if cache_manager:
        orchestrator.set_cache_manager(cache_manager)
    
    if job_queue:
        orchestrator.set_job_queue(job_queue)
    
    logger.info("Enhanced orchestrator created with SOTA models and style enforcement")
    return orchestrator