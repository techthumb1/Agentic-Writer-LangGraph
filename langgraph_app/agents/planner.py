# src/langgraph_app/agents/planner.py
"""
SOTA 2026+ Agentic Planner
- Multi-provider model selection
- Tool use and composition
- Self-refinement loops
- Meta-planning capabilities
"""
from __future__ import annotations

import logging
import json
import os
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base import BaseAgent
from ..core.state import EnrichedContentState
from ..core.types import AgentType, GenerationStatus, ContentPhase, PlanningOutput
from ..core.exceptions import StateValidationError, AgentExecutionError
from ..core.model_registry import get_optimal_model, ModelInterface
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local')

import openai
import anthropic

logger = logging.getLogger(__name__)

@dataclass
class ToolCall:
    """Represents a tool the planner wants to use"""
    tool_name: str
    parameters: Dict[str, Any]
    rationale: str


@dataclass
class PlanCritique:
    """Self-critique of generated plan"""
    confidence: float
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]


class PlannerAgent(BaseAgent):
    """
    SOTA 2026+ Agentic Planner with:
    - Intelligent model routing (OpenAI/Anthropic)
    - Tool discovery and use
    - Self-refinement loops
    - Meta-planning
    """

    def __init__(self):
         super().__init__(AgentType.PLANNER)
         self.available_tools = self._register_tools()
         self.max_refinement_loops = 2
         self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
         self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute agentic planning with tool use and refinement"""
        try:
            self.log_execution_start(state)
            self.validate_state(state, ["template_config", "style_config", "content_spec"])
            
            if not state.content_spec.topic:
                raise StateValidationError("ENTERPRISE: content_spec.topic required")

            # Get optimal model for this task
            # Select model based on task complexity
            complexity = state.template_config.get("metadata", {}).get("complexity", 5)
            model_name = "gpt-4o" if complexity <= 7 else "claude-sonnet-4-20250514"
            
            logger.info(f"Planner using: {model_name}")
            # Phase 1: Tool Discovery - Let LLM decide what tools it needs
            tool_plan = self._discover_needed_tools(state, model_name)

            # Phase 2: Tool Execution - Execute tools autonomously
            tool_results = self._execute_tools(tool_plan, state)
            
            # Phase 3: Initial Planning - Generate plan with enriched context
            initial_plan = self._generate_initial_plan(state, model_name, tool_results)
            
            # Phase 4: Self-Critique - Evaluate plan quality
            critique = self._self_critique_plan(initial_plan, state, model_name)

            # Phase 5: Refinement Loop - Improve plan if needed
            final_plan = self._refine_plan_if_needed(
                initial_plan, 
                critique, 
                state, 
                model_name, 
                tool_results
            )

            # Update state
            state.planning_output = final_plan
            state.research_plan = final_plan
            state.status = GenerationStatus.PLANNING
            state.update_phase(ContentPhase.RESEARCH)

            self.log_execution_complete(state, {
                "model_name": model_name,
                "tools_used": [t.tool_name for t in tool_plan],
                "refinement_loops": 1 if critique.confidence < 0.9 else 0,
                "final_confidence": final_plan.planning_confidence
            })

            return state
            
        except Exception as e:
            logger.error(f"Agentic planner failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Planner failed: {e}") from e

    def _register_tools(self) -> Dict[str, callable]:
        """Register available tools for planner"""
        return {
            "analyze_similar_campaigns": self._tool_analyze_similar_campaigns,
            "fetch_market_data": self._tool_fetch_market_data,
            "analyze_competitor_content": self._tool_analyze_competitor_content,
            "get_trending_topics": self._tool_get_trending_topics,
            "calculate_optimal_metrics": self._tool_calculate_optimal_metrics
        }

    def _discover_needed_tools(
            self, 
            state: EnrichedContentState, 
            model_name: str
        ) -> List[ToolCall]:
            """LLM decides which tools to use"""
            system_prompt = """You are a strategic planner. Decide which tools you need.
    Available: analyze_similar_campaigns, fetch_market_data, analyze_competitor_content, get_trending_topics, calculate_optimal_metrics"""
    
            user_prompt = f"""Plan content for: {state.content_spec.topic}
    Goal: {state.template_config.get('intent', {}).get('primary_goal', 'engagement')}
    
    Output JSON array: [{{"tool_name": "name", "parameters": {{}}, "rationale": "why"}}]"""
    
            try:
                if "gpt" in model_name:
                    response = self.openai_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                        temperature=0.3,
                        max_tokens=1000
                    )
                    content = response.choices[0].message.content
                else:
                    response = self.anthropic_client.messages.create(
                        model=model_name,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_prompt}],
                        temperature=0.3,
                        max_tokens=1000
                    )
                    content = response.content[0].text
                
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if not json_match:
                    return []
                
                tool_data = json.loads(json_match.group(0))
                return [ToolCall(**t) for t in tool_data]
            except Exception as e:
                logger.warning(f"Tool discovery failed: {e}")
                return []
    def _execute_tools(
        self, 
        tool_plan: List[ToolCall], 
        state: EnrichedContentState
    ) -> Dict[str, Any]:
        """Phase 2: Execute requested tools"""
        
        results = {}
        
        for tool_call in tool_plan:
            if tool_call.tool_name in self.available_tools:
                try:
                    logger.info(f"Executing tool: {tool_call.tool_name}")
                    result = self.available_tools[tool_call.tool_name](
                        tool_call.parameters, 
                        state
                    )
                    results[tool_call.tool_name] = result
                except Exception as e:
                    logger.error(f"Tool {tool_call.tool_name} failed: {e}")
                    results[tool_call.tool_name] = {"error": str(e)}
            else:
                logger.warning(f"Tool {tool_call.tool_name} not available")
        
        return results

    def _generate_initial_plan(
        self,
        state: EnrichedContentState,
        model_name: str,
        tool_results: Dict[str, Any]
    ) -> PlanningOutput:
        """Generate initial plan with enriched context"""
        system_prompt = self._build_planning_system_prompt(state)
        user_prompt = self._build_planning_user_prompt(state, tool_results)
        
        try:
            if "gpt" in model_name:
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    temperature=0.4,
                    max_tokens=3000,
                    response_format={"type": "json_object"}
                )
                planning_data = json.loads(response.choices[0].message.content)
            else:
                response = self.anthropic_client.messages.create(
                    model=model_name,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=0.4,
                    max_tokens=3000
                )
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                planning_data = json.loads(json_match.group(0))
            
            return PlanningOutput(
                content_strategy=planning_data["content_strategy"],
                structure_approach=planning_data["structure_approach"],
                key_messages=planning_data["key_messages"],
                research_priorities=planning_data["research_priorities"],
                audience_insights=planning_data["audience_insights"],
                competitive_positioning=planning_data["competitive_positioning"],
                success_metrics=planning_data["success_metrics"],
                estimated_sections=planning_data["estimated_sections"],
                planning_confidence=planning_data.get("planning_confidence", 0.85)
            )
        except Exception as e:
            raise AgentExecutionError(f"Plan generation failed: {e}")
    
    def _self_critique_plan(
        self,
        plan: PlanningOutput,
        state: EnrichedContentState,
        model_name: str
    ) -> PlanCritique:
        """Self-critique the generated plan"""
        system_prompt = """You are an expert critic evaluating content plans.
Analyze for: strategic alignment, feasibility, audience targeting, competitive differentiation."""

        user_prompt = f"""Evaluate this plan:
TOPIC: {state.content_spec.topic}
GOAL: {state.template_config.get('intent', {}).get('primary_goal')}
STRATEGY: {plan.content_strategy}

Output JSON: {{"confidence": 0.0-1.0, "strengths": [], "weaknesses": [], "improvement_suggestions": []}}"""

        try:
            if "gpt" in model_name:
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    temperature=0.3,
                    max_tokens=1500
                )
                content = response.choices[0].message.content
            else:
                response = self.anthropic_client.messages.create(
                    model=model_name,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=0.3,
                    max_tokens=1500
                )
                content = response.content[0].text
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                critique_data = json.loads(json_match.group(0))
                return PlanCritique(**critique_data)
            
            return PlanCritique(confidence=0.85, strengths=["Plan generated"], weaknesses=[], improvement_suggestions=[])
        except Exception as e:
            logger.warning(f"Self-critique failed: {e}")
            return PlanCritique(confidence=0.85, strengths=["Plan generated"], weaknesses=[], improvement_suggestions=[])
    
    def _refine_plan_if_needed(
        self,
        initial_plan: PlanningOutput,
        critique: PlanCritique,
        state: EnrichedContentState,
        model_name: str,
        tool_results: Dict[str, Any]
    ) -> PlanningOutput:
        """Refine plan if confidence < 0.9"""
        if critique.confidence >= 0.9:
            logger.info(f"Plan confidence {critique.confidence:.2f} - accepted")
            return initial_plan
        
        logger.info(f"Plan confidence {critique.confidence:.2f} - refining...")
        
        system_prompt = self._build_planning_system_prompt(state)
        user_prompt = f"""PREVIOUS PLAN HAD ISSUES:
Weaknesses: {critique.weaknesses}
Suggestions: {critique.improvement_suggestions}

Generate IMPROVED plan addressing these issues.
{self._build_planning_user_prompt(state, tool_results)}"""

        try:
            if "gpt" in model_name:
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    temperature=0.5,
                    max_tokens=3000,
                    response_format={"type": "json_object"}
                )
                refined_data = json.loads(response.choices[0].message.content)
            else:
                response = self.anthropic_client.messages.create(
                    model=model_name,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=0.5,
                    max_tokens=3000
                )
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                refined_data = json.loads(json_match.group(0))
            
            refined_plan = PlanningOutput(
                content_strategy=refined_data["content_strategy"],
                structure_approach=refined_data["structure_approach"],
                key_messages=refined_data["key_messages"],
                research_priorities=refined_data["research_priorities"],
                audience_insights=refined_data["audience_insights"],
                competitive_positioning=refined_data["competitive_positioning"],
                success_metrics=refined_data["success_metrics"],
                estimated_sections=refined_data["estimated_sections"],
                planning_confidence=refined_data.get("planning_confidence", 0.9)
            )
            
            logger.info(f"Plan refined, new confidence: {refined_plan.planning_confidence}")
            return refined_plan
        except Exception as e:
            logger.error(f"Refinement failed: {e}, using initial plan")
            return initial_plan
            
    # Tool implementations (simulated - replace with real implementations)
    
    def _tool_analyze_similar_campaigns(self, params: Dict, state: EnrichedContentState) -> Dict:
        """Analyze similar successful campaigns"""
        # TODO: Implement real campaign database lookup
        return {
            "similar_campaigns": [
                {
                    "title": f"Similar campaign for {state.content_spec.topic}",
                    "strategy": "engagement-focused with educational value",
                    "success_rate": 0.87
                }
            ]
        }
    
    def _tool_fetch_market_data(self, params: Dict, state: EnrichedContentState) -> Dict:
        """Fetch current market statistics"""
        # TODO: Implement real market data API
        return {
            "market_size": "Growing",
            "trends": ["AI adoption", "sustainability focus"],
            "growth_rate": "15% YoY"
        }
    
    def _tool_analyze_competitor_content(self, params: Dict, state: EnrichedContentState) -> Dict:
        """Analyze competitor strategies"""
        # TODO: Implement real competitor analysis
        return {
            "competitor_strategies": ["SEO-focused", "social media heavy"],
            "gaps": ["lack of technical depth", "no video content"]
        }
    
    def _tool_get_trending_topics(self, params: Dict, state: EnrichedContentState) -> Dict:
        """Get trending topics"""
        # TODO: Implement real trend analysis
        return {
            "trending": ["AI ethics", "sustainable tech", "remote work tools"],
            "sentiment": "positive"
        }
    
    def _tool_calculate_optimal_metrics(self, params: Dict, state: EnrichedContentState) -> Dict:
        """Calculate optimal success metrics"""
        # TODO: Implement real metrics calculation
        return {
            "engagement_rate": 0.08,
            "conversion_rate": 0.03,
            "reach_target": 10000
        }

    # Helper methods
    
    def _build_planning_system_prompt(self, state: EnrichedContentState) -> str:
        """Build system prompt for planning"""
        style_config = state.style_config
        
        return f"""You are an expert content strategist and planner.

STYLE PROFILE: {style_config.get('name')}
- Tone: {style_config.get('tone')}
- Voice: {style_config.get('voice')}
- Audience: {style_config.get('audience')}

{style_config.get('system_prompt', '')}

Create optimal plans that achieve user intent through strategic reasoning."""

    def _build_planning_user_prompt(
        self, 
        state: EnrichedContentState, 
        tool_results: Dict[str, Any]
    ) -> str:
        """Build user prompt with intent and schema"""
        template_config = state.template_config
        intent = template_config.get("intent", {})
        
        tool_context = ""
        if tool_results:
            tool_context = f"\n\nCONTEXT FROM TOOLS:\n{json.dumps(tool_results, indent=2)}"
        
        return f"""Create an optimal content plan.

TOPIC: {state.content_spec.topic}
INTENT: {intent.get('primary_goal', 'Not specified')}
OUTCOME: {intent.get('desired_outcome', 'Not specified')}
{tool_context}

Output ONLY valid JSON matching this EXACT schema:
{{
  "content_strategy": "string - your strategic approach",
  "structure_approach": "string - how content will be organized",
  "key_messages": ["string", "string"] - 3-5 core messages,
  "research_priorities": ["string", "string"] - 4-6 research areas,
  "audience_insights": {{
    "primary_audience": "string",
    "complexity_level": "string",
    "platform": "string"
  }},
  "competitive_positioning": "string - unique angle",
  "success_metrics": {{"metric_name": 0.0}},
  "estimated_sections": [
    {{"name": "string", "estimated_words": 300}}
  ],
  "planning_confidence": 0.85
}}"""

    def _serialize_plan(self, plan: PlanningOutput) -> str:
        """Serialize plan for critique"""
        return f"""
Strategy: {plan.content_strategy}
Structure: {plan.structure_approach}
Key Messages: {plan.key_messages}
Research: {plan.research_priorities}
Sections: {[s['name'] for s in plan.estimated_sections]}
""" 
    
async def run_researcher(state: EnrichedContentState) -> EnrichedContentState:
    """
    Execute the Researcher agent.
    Gathers research based on the research plan.
    [PLACEHOLDER - NOT IMPLEMENTED]
    """
    logger.info("🔍 EXECUTING RESEARCHER (PLACEHOLDER)")
    state.update_phase(ContentPhase.RESEARCH)
    
    # Placeholder: Simulate research findings
    state.research_findings = state.research_plan
    state.research_findings.update(
        primary_insights=[{"type": "placeholder", "content": "Research not yet implemented"}],
        statistical_evidence=[],
        expert_quotes=[],
        credibility_sources=["placeholder.com"],
        research_confidence=0.5,
    )
    
    state.log_agent_execution(AgentType.RESEARCHER, {
        "status": "placeholder",
        "message": "Researcher agent not yet implemented"
    })
    
    logger.info("✅ Researcher placeholder completed")
    return state

