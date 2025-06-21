# Location: langgraph_app/enhanced_orchestration.py
"""
Enhanced Multi-Agent Orchestration System
Builds on existing LangGraph agents with improved coordination, state management, and reasoning
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union, TypedDict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import uuid

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """Define specialized agent roles"""
    PLANNER = "planner"
    RESEARCHER = "researcher"
    WRITER = "writer"
    EDITOR = "editor"
    FACT_CHECKER = "fact_checker"
    SEO_OPTIMIZER = "seo_optimizer"
    FORMATTER = "formatter"
    PUBLISHER = "publisher"
    QUALITY_ASSESSOR = "quality_assessor"
    COORDINATOR = "coordinator"

class TaskPriority(Enum):
    """Task execution priority"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentCapability:
    """Define agent capabilities and constraints"""
    role: AgentRole
    max_concurrent_tasks: int = 1
    required_inputs: List[str] = field(default_factory=list)
    output_format: str = "text"
    dependencies: List[AgentRole] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 3

@dataclass
class TaskContext:
    """Context passed between agents"""
    task_id: str
    content_type: str
    template_id: str
    style_profile: str
    parameters: Dict[str, Any]
    current_step: str
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class AgentState(TypedDict):
    """Enhanced state for agent workflow"""
    # Core content data
    template_id: str
    style_profile: str
    parameters: Dict[str, Any]
    content: str
    
    # Workflow management
    task_context: TaskContext
    current_agent: str
    next_agents: List[str]
    completed_agents: List[str]
    failed_agents: List[str]
    
    # Agent outputs
    research_data: Dict[str, Any]
    outline: Dict[str, Any]
    draft_content: str
    edited_content: str
    seo_metadata: Dict[str, Any]
    quality_score: Dict[str, Any]
    
    # Error handling
    errors: List[Dict[str, Any]]
    retry_count: int
    
    # Progress tracking
    overall_progress: float
    step_progress: Dict[str, float]
    
    # Metadata
    started_at: datetime
    updated_at: datetime
    workflow_config: Dict[str, Any]

class EnhancedAgent:
    """Base class for enhanced agents with reasoning capabilities"""
    
    def __init__(self, role: AgentRole, capabilities: AgentCapability, 
                 model_registry, cache_manager=None):
        self.role = role
        self.capabilities = capabilities
        self.model_registry = model_registry
        self.cache_manager = cache_manager
        self.status = AgentStatus.IDLE
        self.current_tasks: List[str] = []
        
    async def execute(self, state: AgentState) -> AgentState:
        """Execute agent task with enhanced error handling and reasoning"""
        
        self.status = AgentStatus.WORKING
        task_context = state["task_context"]
        
        try:
            logger.info(f"{self.role.value} agent starting task {task_context.task_id}")
            
            # Check prerequisites
            if not self._check_prerequisites(state):
                raise Exception(f"Prerequisites not met for {self.role.value}")
            
            # Execute agent-specific logic with reasoning
            result = await self._execute_with_reasoning(state)
            
            # Update state
            state = self._update_state(state, result)
            
            # Mark completion
            state["completed_agents"].append(self.role.value)
            self.status = AgentStatus.COMPLETED
            
            logger.info(f"{self.role.value} agent completed task {task_context.task_id}")
            return state
            
        except Exception as e:
            logger.error(f"{self.role.value} agent failed: {e}")
            state["errors"].append({
                "agent": self.role.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            state["failed_agents"].append(self.role.value)
            self.status = AgentStatus.ERROR
            raise
    
    def _check_prerequisites(self, state: AgentState) -> bool:
        """Check if all prerequisites are met"""
        for dependency in self.capabilities.dependencies:
            if dependency.value not in state["completed_agents"]:
                logger.warning(f"{self.role.value} waiting for {dependency.value}")
                return False
        return True
    
    async def _execute_with_reasoning(self, state: AgentState) -> Dict[str, Any]:
        """Execute with chain-of-thought reasoning"""
        
        # Create reasoning prompt
        reasoning_prompt = self._create_reasoning_prompt(state)
        
        # Get response from model with reasoning
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": reasoning_prompt}
        ]
        
        response = await self.model_registry.generate_with_fallback(
            messages=messages,
            preferred_model="gpt-4o",
            max_retries=self.capabilities.retry_count
        )
        
        # Parse reasoning and result
        return self._parse_response(response.content, state)
    
    def _create_reasoning_prompt(self, state: AgentState) -> str:
        """Create prompt that encourages reasoning"""
        return f"""
        Current task: {state['task_context'].content_type} content generation
        Template: {state['template_id']}
        Style: {state['style_profile']}
        
        Please analyze the current state and explain your reasoning step-by-step:
        1. What is the current situation?
        2. What needs to be accomplished?
        3. What approach will you take?
        4. What is your expected output?
        
        Then provide your work in the appropriate format.
        
        Current state: {json.dumps({k: v for k, v in state.items() if k not in ['task_context']}, default=str, indent=2)}
        """
    
    def _get_system_prompt(self) -> str:
        """Get agent-specific system prompt"""
        return f"You are a {self.role.value} agent specialized in content creation workflows."
    
    def _parse_response(self, response: str, state: AgentState) -> Dict[str, Any]:
        """Parse agent response - to be implemented by subclasses"""
        return {"output": response}
    
    def _update_state(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        """Update state with agent results - to be implemented by subclasses"""
        state["updated_at"] = datetime.now()
        return state

class EnhancedPlannerAgent(EnhancedAgent):
    """Enhanced planner with strategic thinking"""
    
    def _get_system_prompt(self) -> str:
        return """You are an expert content planning agent. Your role is to:
        1. Analyze the content requirements and create a detailed plan
        2. Determine the optimal workflow and agent sequence
        3. Set quality benchmarks and success criteria
        4. Anticipate potential challenges and create mitigation strategies
        
        Think strategically about the entire content creation process."""
    
    def _parse_response(self, response: str, state: AgentState) -> Dict[str, Any]:
        """Parse planning response"""
        # Extract structured plan from response
        try:
            # Look for JSON in response or create structured plan
            plan = {
                "content_strategy": "",
                "workflow_steps": [],
                "quality_criteria": [],
                "estimated_duration": 0,
                "resource_requirements": [],
                "risk_factors": []
            }
            
            # Parse response to extract plan elements
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if "strategy" in line.lower():
                    current_section = "strategy"
                elif "steps" in line.lower() or "workflow" in line.lower():
                    current_section = "steps"
                elif "quality" in line.lower() or "criteria" in line.lower():
                    current_section = "quality"
                elif current_section and line:
                    if current_section == "strategy":
                        plan["content_strategy"] += line + " "
                    elif current_section == "steps":
                        if line.startswith(('-', '*', '1.', '2.')):
                            plan["workflow_steps"].append(line[2:].strip())
                    elif current_section == "quality":
                        if line.startswith(('-', '*', '1.', '2.')):
                            plan["quality_criteria"].append(line[2:].strip())
            
            return {"plan": plan, "raw_response": response}
            
        except Exception as e:
            logger.warning(f"Failed to parse plan response: {e}")
            return {"plan": {"content_strategy": response}, "raw_response": response}
    
    def _update_state(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        """Update state with planning results"""
        plan = result.get("plan", {})
        
        state["outline"] = {
            "strategy": plan.get("content_strategy", ""),
            "workflow_steps": plan.get("workflow_steps", []),
            "quality_criteria": plan.get("quality_criteria", []),
            "created_by": self.role.value
        }
        
        # Set next agents based on plan
        state["next_agents"] = ["researcher", "writer"]
        
        # Update progress
        state["step_progress"]["planning"] = 100.0
        state["overall_progress"] = 15.0
        
        return super()._update_state(state, result)

class EnhancedResearcherAgent(EnhancedAgent):
    """Enhanced researcher with fact verification"""
    
    def _get_system_prompt(self) -> str:
        return """You are an expert research agent. Your role is to:
        1. Gather comprehensive, accurate information on the topic
        2. Verify facts and identify authoritative sources
        3. Organize research findings for content creation
        4. Flag any areas requiring additional investigation
        
        Focus on accuracy, relevance, and credibility of sources."""
    
    def _parse_response(self, response: str, state: AgentState) -> Dict[str, Any]:
        """Parse research response"""
        research_data = {
            "key_findings": [],
            "sources": [],
            "fact_checks": [],
            "research_gaps": [],
            "confidence_score": 0.8
        }
        
        # Parse structured research from response
        sections = response.split('\n\n')
        for section in sections:
            if "finding" in section.lower():
                research_data["key_findings"].append(section.strip())
            elif "source" in section.lower() or "http" in section:
                research_data["sources"].append(section.strip())
            elif "gap" in section.lower() or "missing" in section.lower():
                research_data["research_gaps"].append(section.strip())
        
        return {"research": research_data, "raw_response": response}
    
    def _update_state(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        """Update state with research results"""
        state["research_data"] = result.get("research", {})
        state["step_progress"]["research"] = 100.0
        state["overall_progress"] = 35.0
        state["next_agents"] = ["writer"]
        
        return super()._update_state(state, result)

class EnhancedWriterAgent(EnhancedAgent):
    """Enhanced writer with style adaptation"""
    
    def _get_system_prompt(self) -> str:
        return """You are an expert content writer. Your role is to:
        1. Create engaging, well-structured content based on research and planning
        2. Adapt writing style to match the specified style profile
        3. Incorporate research findings naturally and accurately
        4. Ensure content meets quality and engagement standards
        
        Focus on clarity, engagement, and style consistency."""
    
    def _create_reasoning_prompt(self, state: AgentState) -> str:
        """Enhanced prompt with research and planning context"""
        base_prompt = super()._create_reasoning_prompt(state)
        
        research_summary = ""
        if state.get("research_data"):
            research_summary = f"\nResearch findings: {json.dumps(state['research_data'], indent=2)}"
        
        planning_summary = ""
        if state.get("outline"):
            planning_summary = f"\nContent plan: {json.dumps(state['outline'], indent=2)}"
        
        return f"{base_prompt}{research_summary}{planning_summary}"
    
    def _parse_response(self, response: str, state: AgentState) -> Dict[str, Any]:
        """Parse writing response"""
        # Extract content from response
        content = response
        
        # Try to identify if there's structured content vs reasoning
        if "CONTENT:" in response.upper():
            parts = response.split("CONTENT:")
            if len(parts) > 1:
                content = parts[-1].strip()
        
        return {
            "content": content,
            "word_count": len(content.split()),
            "raw_response": response
        }
    
    def _update_state(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        """Update state with written content"""
        state["draft_content"] = result.get("content", "")
        state["content"] = state["draft_content"]  # Set main content field
        state["step_progress"]["writing"] = 100.0
        state["overall_progress"] = 65.0
        state["next_agents"] = ["editor", "seo_optimizer"]
        
        return super()._update_state(state, result)

class EnhancedEditorAgent(EnhancedAgent):
    """Enhanced editor with quality improvement"""
    
    def _get_system_prompt(self) -> str:
        return """You are an expert content editor. Your role is to:
        1. Review and improve content structure, flow, and clarity
        2. Ensure consistency in tone and style
        3. Correct grammar, spelling, and formatting issues
        4. Enhance readability and engagement
        
        Focus on making content polished and professional."""
    
    def _parse_response(self, response: str, state: AgentState) -> Dict[str, Any]:
        """Parse editing response"""
        edited_content = response
        
        # Look for edited content section
        if "EDITED CONTENT:" in response.upper():
            parts = response.split("EDITED CONTENT:")
            if len(parts) > 1:
                edited_content = parts[-1].strip()
        
        return {
            "edited_content": edited_content,
            "improvements": [],  # Could extract improvement notes
            "raw_response": response
        }
    
    def _update_state(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        """Update state with edited content"""
        state["edited_content"] = result.get("edited_content", "")
        state["content"] = state["edited_content"]  # Update main content
        state["step_progress"]["editing"] = 100.0
        state["overall_progress"] = 85.0
        state["next_agents"] = ["quality_assessor"]
        
        return super()._update_state(state, result)

class EnhancedQualityAssessor(EnhancedAgent):
    """Quality assessment agent"""
    
    def _get_system_prompt(self) -> str:
        return """You are a content quality assessment expert. Your role is to:
        1. Evaluate content against quality criteria
        2. Provide objective quality scores
        3. Identify areas for improvement
        4. Ensure content meets publication standards
        
        Be thorough and objective in your assessment."""
    
    def _parse_response(self, response: str, state: AgentState) -> Dict[str, Any]:
        """Parse quality assessment response"""
        quality_score = {
            "overall_score": 85,  # Default score
            "readability": 80,
            "accuracy": 90,
            "engagement": 85,
            "seo_potential": 75,
            "recommendations": []
        }
        
        # Extract scores and recommendations from response
        lines = response.split('\n')
        for line in lines:
            if "score" in line.lower() and any(char.isdigit() for char in line):
                # Try to extract numeric scores
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    score = int(numbers[0])
                    if "overall" in line.lower():
                        quality_score["overall_score"] = score
                    elif "readability" in line.lower():
                        quality_score["readability"] = score
                    elif "accuracy" in line.lower():
                        quality_score["accuracy"] = score
            elif line.strip().startswith(('-', '*', '•')):
                quality_score["recommendations"].append(line.strip()[1:].strip())