# langgraph_app/agents/enhanced_editor_integrated.py
"""
Enterprise Editor Agent with LLM integration, tool use, and self-refinement loops.
Follows SOTA multi-agent patterns from enhanced_planner and enhanced_researcher.
"""

import os
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from langgraph_app.core.circuit_breaker import get_circuit_breaker
import time
import random

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

from langgraph_app.core.state import EnrichedContentState, AgentType
from langgraph_app.core.types import EditedContent
from langgraph_app.enhanced_model_registry import get_model, get_model_for_generation

logger = logging.getLogger(__name__)


# Tool definitions for Editor agent
@tool
def check_grammar(text: str) -> Dict[str, Any]:
    """Check grammar and style issues in text.
    
    Args:
        text: Content to check
        
    Returns:
        Dictionary with grammar issues and suggestions
    """
    # Placeholder - integrate LanguageTool API or similar
    issues = []
    
    # Basic checks
    if text.count('  ') > 0:
        issues.append({"type": "spacing", "message": "Double spaces detected"})
    
    if re.search(r'\b(very|really|actually|basically)\b', text, re.I):
        issues.append({"type": "weak_words", "message": "Contains weak intensifiers"})
    
    return {
        "total_issues": len(issues),
        "issues": issues,
        "suggestions": [i["message"] for i in issues]
    }


@tool
def analyze_readability(text: str) -> Dict[str, Any]:
    """Analyze content readability metrics.
    
    Args:
        text: Content to analyze
        
    Returns:
        Readability scores and recommendations
    """
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    
    avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
    avg_sentence_length = len(words) / max(len(sentences), 1)
    
    # Flesch Reading Ease approximation
    syllables = sum(len(re.findall(r'[aeiouy]+', word)) for word in words)
    avg_syllables = syllables / max(len(words), 1)
    
    score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables
    
    return {
        "flesch_score": max(0, min(100, score)),
        "avg_word_length": round(avg_word_length, 2),
        "avg_sentence_length": round(avg_sentence_length, 2),
        "recommendations": [
            "Shorten sentences" if avg_sentence_length > 25 else "Sentence length optimal",
            "Simplify vocabulary" if avg_word_length > 6 else "Vocabulary appropriate"
        ]
    }


@tool
def detect_ai_tells(text: str) -> Dict[str, Any]:
    """Detect AI-generated content markers.
    
    Args:
        text: Content to check
        
    Returns:
        List of detected AI tells and replacements
    """
    ai_tells = {
        r'\bdelve\b': 'examine',
        r'\bdelving\b': 'examining',
        r'\bshowcase\b': 'demonstrate',
        r'\bleverage\b': 'use',
        r'\bin conclusion\b': 'finally',
        r'\bin summary\b': 'overall',
        r'\bit\'s important to note\b': 'notably',
        r'\bit should be noted\b': 'note that'
    }
    
    detected = []
    for pattern, replacement in ai_tells.items():
        matches = re.findall(pattern, text, re.I)
        if matches:
            detected.append({
                "pattern": pattern,
                "found": matches[0],
                "replacement": replacement,
                "count": len(matches)
            })
    
    return {
        "total_ai_tells": len(detected),
        "detected_patterns": detected,
        "clean_score": max(0, 100 - len(detected) * 10)
    }


class EnhancedEditorAgent:
    """
    Enterprise Editor Agent with:
    - LLM-driven intelligent editing
    - Tool use (grammar, readability, AI tell detection)
    - Self-refinement loop with quality validation
    - Dynamic model selection (OpenAI GPT-4o / Anthropic Claude Sonnet 4)
    """
    
    def __init__(self):
        self.agent_type = AgentType.EDITOR
        self.tools = [check_grammar, analyze_readability, detect_ai_tells]
        
        # Quality thresholds
        self.min_readability = 60.0
        self.max_ai_tells = 3
        self.max_refinement_loops = 1
    
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute editor with LLM-driven editing and self-refinement."""
        
        logger.info("🧐 EDITOR: Starting enterprise editing")
        
        # Extract draft content
        if hasattr(state.draft_content, 'body'):
            draft_text = state.draft_content.body
            draft_title = state.draft_content.title
        else:
            draft_text = state.draft_content or state.content
            draft_title = (state.content_spec.topic if state.content_spec else "Untitled")
        
        if not draft_text or not draft_text.strip():
            raise RuntimeError("ENTERPRISE: Editor requires draft content")
        
        # Get configs
        template_config = state.template_config or {}
        style_config = state.style_config or {}
        
        # Extract context
        context = self._extract_editing_context(state)
        
        # Self-refinement loop
        edited_text = draft_text
        refinement_round = 0
        quality_acceptable = False
        
        while refinement_round < self.max_refinement_loops and not quality_acceptable:
            refinement_round += 1
            logger.info(f"📝 Refinement round {refinement_round}/{self.max_refinement_loops}")
            
            # Run LLM editing with tools
            edited_text, tool_results = self._llm_edit_with_tools(
                edited_text,
                template_config,
                style_config,
                context
            )
            
            # Validate quality
            quality_acceptable = self._validate_edit_quality(tool_results)
            
            if quality_acceptable:
                logger.info(f"✅ Quality acceptable after {refinement_round} rounds")
                break
            else:
                logger.info(f"⚠️ Quality below threshold, refining...")
        
        # Create EditedContent object
        state.edited_content = EditedContent(
            title=draft_title,
            body=edited_text,
            feedback=[f"Completed {refinement_round} refinement rounds"],
            is_approved=quality_acceptable,
            edit_summary=f"Applied LLM editing with {len(tool_results)} tool checks"
        )
        
        state.content = edited_text  # Legacy field
        
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "refinement_rounds": refinement_round,
            "quality_acceptable": quality_acceptable,
            "tools_used": len(tool_results)
        })
        
        logger.info(f"✅ EDITOR: Completed with {refinement_round} refinements")
        
        return state
    
    def _extract_editing_context(self, state: EnrichedContentState) -> Dict[str, Any]:
        """Extract relevant context for editing."""
        
        context = {}
        
        # Research insights
        if state.research_findings:
            primary_insights = getattr(state.research_findings, 'primary_insights', [])
            context['research_insights'] = [
                i.get('finding', '') for i in primary_insights[:3] if isinstance(i, dict)
            ]
        
        # Planning guidance
        if state.planning_output:
            context['key_messages'] = getattr(state.planning_output, 'key_messages', [])
            context['structure_approach'] = getattr(state.planning_output, 'structure_approach', '')
        
        # Content spec
        if state.content_spec:
            context['topic'] = state.content_spec.topic
            context['audience'] = state.content_spec.target_audience
            context['platform'] = state.content_spec.platform
        
        return context
    
    def _llm_edit_with_tools(
        self,
        content: str,
        template_config: Dict,
        style_config: Dict,
        context: Dict
    ) -> tuple[str, List[Dict]]:
        """
        Use LLM with tools to intelligently edit content.

        Improvements:
        - Circuit breaker integration
        - Exponential backoff with jitter
        - Graceful fallback to original content on failure
        - Provider detection (Anthropic vs OpenAI)
        """

        circuit_breaker = get_circuit_breaker()

        # Select model based on complexity
        task_complexity = len(content.split()) / 1000  # Words in thousands
        generation_settings = context.get('generation_settings', {'max_tokens': 4000, 'temperature': 1.0})
        model = get_model("editor", generation_settings)

        # Determine provider from model
        model_name = str(model).lower()
        provider = "anthropic" if "claude" in model_name else "openai"

        logger.info(f"Editor using model: {model_name} (provider: {provider})")

        # Check circuit breaker before attempting
        if not circuit_breaker.can_execute(provider):
            logger.warning(
                f"⚠️ Circuit breaker OPEN for {provider} - "
                f"returning content without LLM edits"
            )
            return content, [{"tool": "passthrough", "result": "circuit_breaker_open"}]

        # Bind tools to model
        model_with_tools = model.bind_tools(self.tools)

        # Build editing prompts
        system_prompt = self._build_editing_system_prompt(
            template_config,
            style_config,
            context
        )

        user_prompt = f"""Edit the following content to improve quality, clarity, and alignment with requirements.

    **Content to Edit:**
    {content}

    **Instructions:**
    1. Use check_grammar tool to identify grammar issues
    2. Use analyze_readability tool to assess readability
    3. Use detect_ai_tells tool to find AI-generated markers
    4. Apply intelligent edits based on tool results
    5. Ensure research insights and key messages are integrated
    6. Maintain template and style requirements

    Provide the edited content with improvements applied."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Retry loop with circuit breaker
        max_attempts = 3
        delays = [2.0, 5.0, 10.0]

        for attempt in range(max_attempts):
            try:
                # Invoke with tools
                logger.info(f"Editor invoking LLM (attempt {attempt + 1}/{max_attempts})...")
                response = model_with_tools.invoke(messages)

                # Success - record with circuit breaker
                circuit_breaker.record_success(provider)

                # Log retry success if not first attempt
                if attempt > 0:
                    logger.info(f"✅ Editor LLM call succeeded on retry {attempt + 1}/{max_attempts}")

                # Extract tool calls
                tool_results = []
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    for tool_call in response.tool_calls:
                        logger.info(f"🔧 Tool called: {tool_call['name']}")
                        tool_results.append({
                            "tool": tool_call['name'],
                            "result": tool_call.get('args', {})
                        })

                # Extract edited content
                edited_content = response.content if hasattr(response, 'content') else content

                return edited_content, tool_results

            except Exception as e:
                error_str = str(e).lower()
                error_type = type(e).__name__

                # Record failure with circuit breaker
                circuit_breaker.record_failure(provider, error_type)

                # Determine if error is retryable
                is_retryable = any(keyword in error_str for keyword in [
                    'timeout', 'rate_limit', 'overloaded', '429', '500', '503', '529'
                ])

                # Retry on transient errors
                if attempt < max_attempts - 1 and is_retryable:
                    delay = delays[attempt] + random.uniform(0, 1.0)  # Add jitter
                    logger.warning(
                        f"⚠️ Editor LLM call failed with {error_type} "
                        f"(attempt {attempt + 1}/{max_attempts}). "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                else:
                    # Final attempt or non-retryable error
                    logger.error(
                        f"❌ Editor LLM call failed after {max_attempts} attempts: {error_type} - {str(e)}"
                    )
                    logger.warning("Returning original content as fallback")

                    # Return original content as fallback
                    return content, [{"tool": "error_fallback", "result": str(e)}]

        # Fallback (should not reach here, but for safety)
        logger.warning("Editor retry loop exhausted - returning original content")
        return content, []

    def _build_editing_system_prompt(
        self,
        template_config: Dict,
        style_config: Dict,
        context: Dict
    ) -> str:
        """Build system prompt for editing."""
        
        template_type = template_config.get('template_type', 'content')
        style_tone = style_config.get('tone', 'professional')
        style_voice = style_config.get('voice', 'authoritative')
        
        forbidden_patterns = style_config.get('forbidden_patterns', [])
        
        prompt = f"""You are an expert content editor specializing in {template_type}.

**Editing Objectives:**
- Improve clarity, coherence, and impact
- Ensure alignment with {style_tone} tone and {style_voice} voice
- Integrate research insights naturally
- Remove AI-generated tells and generic phrases
- Enhance readability while maintaining depth
- Ensure structural integrity

**Style Requirements:**
- Tone: {style_tone}
- Voice: {style_voice}"""
        
        if forbidden_patterns:
            prompt += f"\n- Forbidden patterns: {', '.join(forbidden_patterns[:5])}"
        
        if context.get('key_messages'):
            prompt += f"\n\n**Key Messages to Preserve:**\n"
            for msg in context['key_messages'][:3]:
                prompt += f"- {msg}\n"
        
        if context.get('research_insights'):
            prompt += f"\n**Research Insights to Integrate:**\n"
            for insight in context['research_insights']:
                prompt += f"- {insight}\n"
        
        prompt += """

**Critical Instructions:**
1. Use available tools to analyze content quality
2. Apply data-driven edits based on tool feedback
3. Maintain factual accuracy - never fabricate
4. Preserve author's core arguments and evidence
5. Focus on enhancement, not rewriting from scratch"""
        
        return prompt
    
    def _validate_edit_quality(self, tool_results: List[Dict]) -> bool:
        """Validate if editing meets quality thresholds."""
        
        # Check readability
        readability_results = [r for r in tool_results if r.get('tool') == 'analyze_readability']
        if readability_results:
            score = readability_results[0].get('result', {}).get('flesch_score', 50)
            if score < self.min_readability:
                logger.warning(f"Readability too low: {score} < {self.min_readability}")
                return False
        
        # Check AI tells
        ai_tell_results = [r for r in tool_results if r.get('tool') == 'detect_ai_tells']
        if ai_tell_results:
            ai_tells = ai_tell_results[0].get('result', {}).get('total_ai_tells', 0)
            if ai_tells > self.max_ai_tells:
                logger.warning(f"Too many AI tells: {ai_tells} > {self.max_ai_tells}")
                return False
        
        # Grammar check
        grammar_results = [r for r in tool_results if r.get('tool') == 'check_grammar']
        if grammar_results:
            issues = grammar_results[0].get('result', {}).get('total_issues', 0)
            if issues > 5:
                logger.warning(f"Too many grammar issues: {issues}")
                return False
        
        return True