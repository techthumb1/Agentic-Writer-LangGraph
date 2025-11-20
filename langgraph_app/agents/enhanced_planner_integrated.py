# langgraph_app/agents/planner.py
"""
Enterprise Planner Agent - Unified
Combines LLM intelligence, tool use, YAML constraints, and self-refinement
"""
from __future__ import annotations
import time
from anthropic._exceptions import OverloadedError
import logging
import json
import os
import re
from typing import Dict, Any, List
from dataclasses import dataclass
import random

from .base import BaseAgent
from ..core.state import EnrichedContentState
from ..core.types import AgentType, GenerationStatus, ContentPhase, PlanningOutput
from ..core.exceptions import StateValidationError, AgentExecutionError
from langgraph_app.core.circuit_breaker import get_circuit_breaker

import openai
import anthropic
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    tool_name: str
    parameters: Dict[str, Any]
    rationale: str


@dataclass
class PlanCritique:
    confidence: float
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]


class EnhancedPlannerAgent(BaseAgent):
    """Unified planner: LLM + YAML constraints + tools + self-refinement"""

    def __init__(self):
        super().__init__(AgentType.PLANNER)
        self.available_tools = self._register_tools()
        self.max_refinement_loops = 2
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute planning with tools, LLM, and refinement"""
        try:
            self.log_execution_start(state)
            self.validate_state(state, ["template_config", "style_config", "content_spec"])
            
            if not state.content_spec.topic:
                raise StateValidationError("ENTERPRISE: content_spec.topic required")

            # Select model based on complexity
            complexity = state.template_config.get("metadata", {}).get("complexity", 5)
            model_name = "gpt-4o" if complexity <= 7 else "claude-sonnet-4-20250514"
            
            logger.info(f"Planner using: {model_name}")

            # Phase 1: Tool Discovery
            tool_plan = self._discover_needed_tools(state, model_name)

            # Phase 2: Tool Execution
            tool_results = self._execute_tools(tool_plan, state)
            
            # Phase 3: Initial Planning
            initial_plan = self._llm_generate_planning(state, model_name, tool_results)
            
            # Phase 4: Self-Critique
            critique = self._self_critique_plan(initial_plan, state, model_name)

            # Phase 5: Refinement if needed
            final_plan = self._refine_plan_if_needed(
                initial_plan, critique, state, model_name, tool_results
            )

            # Update state
            state.planning_output = final_plan
            state.research_plan = final_plan
            state.status = GenerationStatus.PLANNING
            state.update_phase(ContentPhase.RESEARCH)

            self.log_execution_complete(state, {
                "model": model_name,
                "tools_used": [t.tool_name for t in tool_plan],
                "refinement_loops": 1 if critique.confidence < 0.9 else 0,
                "final_confidence": final_plan.planning_confidence
            })

            return state
            
        except Exception as e:
            logger.error(f"Planner failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Planner failed: {e}") from e

    def _register_tools(self) -> Dict[str, callable]:
        return {
            "analyze_similar_campaigns": self._tool_analyze_similar_campaigns,
            "get_trending_topics": self._tool_get_trending_topics,
            "analyze_competitor_content": self._tool_analyze_competitor_content,
            "calculate_optimal_metrics": self._tool_calculate_optimal_metrics
        }

    def _discover_needed_tools(self, state: EnrichedContentState, model_name: str) -> List[ToolCall]:
        """LLM decides which tools to use"""
        system_prompt = """You are a strategic planner. Decide which tools you need.
Available: analyze_similar_campaigns, get_trending_topics, analyze_competitor_content, calculate_optimal_metrics"""

        user_prompt = f"""Plan content for: {state.content_spec.topic}
Template: {state.template_config.get('template_type')}

Output JSON array: [{{"tool_name": "name", "parameters": {{}}, "rationale": "why"}}]"""

        try:
            if "gpt" in model_name:
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
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

    def _execute_tools(self, tool_plan: List[ToolCall], state: EnrichedContentState) -> Dict[str, Any]:
        """Execute requested tools"""
        results = {}
        
        for tool_call in tool_plan:
            if tool_call.tool_name in self.available_tools:
                try:
                    logger.info(f"Executing tool: {tool_call.tool_name}")
                    result = self.available_tools[tool_call.tool_name](
                        tool_call.parameters, state
                    )
                    results[tool_call.tool_name] = result
                except Exception as e:
                    logger.error(f"Tool {tool_call.tool_name} failed: {e}")
                    results[tool_call.tool_name] = {"error": str(e)}
        
        return results

# UPDATED SECTION FOR: langgraph_app/agents/enhanced_planner_integrated.py
# Lines 180-238 (the _llm_generate_planning method)

    def _llm_generate_planning(
        self,
        state: Dict,
        model_name: str,
        tool_results: dict
    ) -> PlanningOutput:

        system_prompt = self._build_system_prompt(state)
        user_prompt = self._build_user_prompt(state, tool_results)

        max_attempts = 4  # Increased from 3
        circuit_breaker = get_circuit_breaker()
        last_exception = None
        provider = "anthropic" if "claude" in model_name.lower() else "openai"

        # Exponential backoff delays: 2s, 5s, 12s, 30s (total ~49s worst case)
        delays = [2.0, 5.0, 12.0, 30.0]

        for attempt in range(max_attempts):
            try:
                # Check circuit breaker before attempting call
                if not circuit_breaker.can_execute(provider):
                    logger.error(
                        f"Circuit breaker OPEN for {provider} - aborting planner "
                        f"(attempt {attempt + 1}/{max_attempts})"
                    )
                    raise AgentExecutionError(
                        f"Circuit breaker open for {provider} after repeated failures. "
                        f"Provider may be experiencing outage. Please try again later."
                    )

                # Attempt API call
                if "gpt" in model_name:
                    response = self.openai_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
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

                # Success - record with circuit breaker
                circuit_breaker.record_success(provider)

                # Log retry success if not first attempt
                if attempt > 0:
                    logger.info(
                        f"✅ Planner succeeded on retry {attempt + 1}/{max_attempts} "
                        f"using {model_name}"
                    )

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

            except OverloadedError as e:
                last_exception = e
                error_type = "overloaded"
                
                # Record failure with circuit breaker
                circuit_breaker.record_failure(provider, error_type)

                # Check if we should retry
                if attempt < max_attempts - 1:
                    # Calculate delay with jitter
                    base_delay = delays[attempt]
                    jitter = random.uniform(0, 1.0)  # Add 0-1s random jitter
                    total_delay = base_delay + jitter
                    
                    logger.warning(
                        f"⚠️ Anthropic API overloaded (529) - "
                        f"retry {attempt + 1}/{max_attempts} in {total_delay:.1f}s "
                        f"(base={base_delay}s + jitter={jitter:.1f}s)"
                    )
                    
                    time.sleep(total_delay)
                else:
                    # Final attempt failed
                    logger.error(
                        f"❌ Planner failed after {max_attempts} attempts. "
                        f"Anthropic API remained overloaded (529). "
                        f"Total time spent: ~{sum(delays[:attempt]):.0f}s"
                    )
                    raise AgentExecutionError(
                        f"Plan generation failed after {max_attempts} retries with exponential backoff. "
                        f"Anthropic API is experiencing high load (529 errors). "
                        f"Please try again in a few minutes. Error: {e}"
                    )

            except Exception as e:
                # Non-retryable errors (JSON parsing, network, etc.)
                error_type = type(e).__name__
                logger.error(f"❌ Planner failed with non-retryable error: {error_type} - {str(e)}")
                
                # Record failure but don't retry
                circuit_breaker.record_failure(provider, error_type)
                
                raise AgentExecutionError(f"Plan generation failed: {error_type} - {str(e)}")

        # Should never reach here, but for safety
        raise AgentExecutionError(f"Plan generation failed after {max_attempts} attempts: {last_exception}")    
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
STRATEGY: {plan.content_strategy}

Output JSON: {{"confidence": 0.0-1.0, "strengths": [], "weaknesses": [], "improvement_suggestions": []}}"""

        try:
            if "gpt" in model_name:
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
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
            
            return PlanCritique(
                confidence=0.85,
                strengths=["Plan generated"],
                weaknesses=[],
                improvement_suggestions=[]
            )
        except Exception as e:
            logger.warning(f"Self-critique failed: {e}")
            return PlanCritique(
                confidence=0.85,
                strengths=["Plan generated"],
                weaknesses=[],
                improvement_suggestions=[]
            )

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
        
        system_prompt = self._build_system_prompt(state)
        user_prompt = f"""PREVIOUS PLAN HAD ISSUES:
Weaknesses: {critique.weaknesses}
Suggestions: {critique.improvement_suggestions}

Generate IMPROVED plan addressing these issues.
{self._build_user_prompt(state, tool_results)}"""

        try:
            if "gpt" in model_name:
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
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

    # Tool implementations
    def _tool_analyze_similar_campaigns(self, params: Dict, state: EnrichedContentState) -> Dict:
        return {
            "similar_campaigns": [{
                "title": f"Similar campaign for {state.content_spec.topic}",
                "strategy": "engagement-focused",
                "success_rate": 0.87
            }]
        }

    def _tool_get_trending_topics(self, params: Dict, state: EnrichedContentState) -> Dict:
        return {
            "trending": ["AI ethics", "sustainable tech"],
            "sentiment": "positive"
        }

    def _tool_analyze_competitor_content(self, params: Dict, state: EnrichedContentState) -> Dict:
        return {
            "competitor_strategies": ["SEO-focused", "social media heavy"],
            "gaps": ["lack of technical depth"]
        }

    def _tool_calculate_optimal_metrics(self, params: Dict, state: EnrichedContentState) -> Dict:
        return {
            "engagement_rate": 0.08,
            "conversion_rate": 0.03,
            "reach_target": 10000
        }

    # Prompt builders
    def _build_system_prompt(self, state: EnrichedContentState) -> str:
        """Build system prompt with style guidance"""
        style_config = state.style_config
        
        return f"""You are an expert content strategist and planner.

STYLE PROFILE: {style_config.get('name')}
- Tone: {style_config.get('tone')}
- Voice: {style_config.get('voice')}
- Audience: {style_config.get('audience')}

{style_config.get('system_prompt', '')}

Create optimal plans that achieve user intent."""

    def _build_user_prompt(self, state: EnrichedContentState, tool_results: Dict[str, Any]) -> str:
        """Build user prompt with YAML constraints and tool context"""
        template_config = state.template_config
        content_spec = state.content_spec
        
        constraints = self._extract_constraints(template_config)
        tool_context = f"\n\nTOOL INSIGHTS:\n{json.dumps(tool_results, indent=2)}" if tool_results else ""
        
        return f"""Create an optimal content plan.

TOPIC: {content_spec.topic}
TEMPLATE: {template_config.get('template_type')}
DESCRIPTION: {template_config.get('description')}

CONSTRAINTS:
{self._format_constraints(constraints)}
{tool_context}

Output ONLY valid JSON:
{{
  "content_strategy": "string",
  "structure_approach": "string",
  "key_messages": ["string"],
  "research_priorities": ["string"],
  "audience_insights": {{
    "primary_audience": "string",
    "complexity_level": "string",
    "platform": "string"
  }},
  "competitive_positioning": "string",
  "success_metrics": {{"metric": 0.0}},
  "estimated_sections": [{{"name": "string", "estimated_words": 300}}],
  "planning_confidence": 0.85
}}"""

    def _extract_constraints(self, template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract YAML constraints"""
        return {
            "requirements": template_config.get("requirements", {}),
            "output": template_config.get("output", {}),
            "metadata": template_config.get("metadata", {})
        }

    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format constraints for prompt"""
        lines = []
        
        if constraints.get("requirements"):
            lines.append("REQUIREMENTS:")
            for key, value in constraints["requirements"].items():
                lines.append(f"  - {key}: {value}")
        
        if constraints.get("metadata"):
            meta = constraints["metadata"]
            if meta.get("complexity"):
                lines.append(f"\nCOMPLEXITY: {meta['complexity']}")
        
        return "\n".join(lines)