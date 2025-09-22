# File: langgraph_app/agents/writer.py
"""
Simplified Writer Agent - Generates content from basic inputs only
No blocking validation, no hardcoded prompts, no template dependencies
"""

import os
import logging
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv
from openai import OpenAI
from langgraph_app.core.enriched_content_state import EnrichedContentState

logger = logging.getLogger(__name__)
load_dotenv()

class WritingMode(Enum):
    CREATIVE = "creative"
    ANALYTICAL = "analytical" 
    TECHNICAL = "technical"
    NARRATIVE = "narrative"
    PERSUASIVE = "persuasive"

@dataclass
class WritingContext:
    """Simple context for content generation"""
    topic: str
    audience: str
    platform: str = "web"
    intent: str = "inform"
    complexity_level: int = 5

class TemplateAwareWriterAgent:
    """
    Streamlined Writer Agent that generates content from basic inputs:
    - Topic + Audience from content_spec
    - Style prompt from style_config  
    - Planning structure from planning_output
    - No template dependencies, no blocking validation
    """

    def __init__(self):
        """Initialize with OpenAI client only"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable required")
        self.client = OpenAI(api_key=api_key)

    def extract_context(self, state: EnrichedContentState) -> WritingContext:
        """Extract simple writing context from state"""
        
        # Get topic and audience from content_spec (required)
        if not state.content_spec or not state.content_spec.topic:
            raise ValueError("content_spec with topic is required")
            
        topic = state.content_spec.topic.strip()
        audience = getattr(state.content_spec, 'target_audience', 'general audience')
        platform = getattr(state.content_spec, 'platform', 'web')
        
        # Basic intent analysis from topic
        topic_lower = topic.lower()
        if any(word in topic_lower for word in ['how to', 'guide', 'tutorial']):
            intent = "teach"
        elif any(word in topic_lower for word in ['analyze', 'research', 'study']):
            intent = "analyze"
        elif any(word in topic_lower for word in ['strategy', 'plan', 'approach']):
            intent = "advise"
        else:
            intent = "inform"
            
        return WritingContext(
            topic=topic,
            audience=audience,
            platform=platform,
            intent=intent,
            complexity_level=5
        )

    def _generate_adaptive_content(
        self,
        state: EnrichedContentState,
        style_config: dict
    ) -> str:
        """
        ENTERPRISE: Unified content generation entrypoint
        Consumes WritingContext + PlanningOutput + style_config
        FAIL-FAST: No fallbacks, no defaults
        """
    
        # --- Fail-fast checks ---
        if not hasattr(state, "content_spec") or not state.content_spec:
            raise ValueError("ENTERPRISE: Writer requires state.content_spec")
        if not state.planning_output:
            raise ValueError("ENTERPRISE: Writer requires planning_output from Planner")
        if not style_config or not style_config.get("system_prompt"):
            raise ValueError("ENTERPRISE: Writer requires style_config.system_prompt")
    
        spec = state.content_spec
        planning = state.planning_output
        writing_context = WritingContext(
            topic=spec.topic,
            audience=spec.audience,
            platform=spec.platform,
            tone=style_config.get("tone"),
            voice=style_config.get("voice"),
            complexity_level=spec.complexity_level,
            structure=planning.structure_approach,
            key_messages=planning.key_messages
        )
    
        # --- Prompt assembly ---
        system_prompt = style_config["system_prompt"]
        composed_prompt = (
            f"{system_prompt}\n\n"
            f"Topic: {writing_context.topic}\n"
            f"Audience: {writing_context.audience}\n"
            f"Platform: {writing_context.platform}\n"
            f"Tone: {writing_context.tone}\n"
            f"Voice: {writing_context.voice}\n"
            f"Structure: {writing_context.structure}\n"
            f"Key Messages: {', '.join(writing_context.key_messages)}\n"
        )
    
        # --- Model call ---
        response = self.model.generate(
            prompt=composed_prompt,
            temperature=style_config.get("settings", {}).get("temperature", 0.7),
            max_tokens=style_config.get("length_limit", {}).get("max_tokens", 1200),
        )
    
        state.draft_content = response.output_text
        return state.draft_content


    def build_simple_prompt(self, context: WritingContext, state: EnrichedContentState) -> str:
        """Build simple prompt from context + style + planning"""
        
        # Get style prompt (if available)
        style_prompt = ""
        if state.style_config and isinstance(state.style_config, dict):
            style_prompt = state.style_config.get('system_prompt', '')
        
        # Get planning structure (if available)
        planning_structure = ""
        if hasattr(state, 'planning_output') and state.planning_output:
            if hasattr(state.planning_output, 'structure_approach'):
                planning_structure = f"\nStructure Approach: {state.planning_output.structure_approach}"
            if hasattr(state.planning_output, 'key_messages'):
                messages = getattr(state.planning_output, 'key_messages', [])
                if messages:
                    planning_structure += f"\nKey Messages: {', '.join(messages)}"
        
        # Build simple, direct prompt
        prompt_parts = [
            f"Write comprehensive content about: {context.topic}",
            f"Target Audience: {context.audience}",
            f"Intent: {context.intent}",
            f"Platform: {context.platform}"
        ]
        
        if style_prompt:
            prompt_parts.append(f"\nStyle Guidelines: {style_prompt}")
            
        if planning_structure:
            prompt_parts.append(f"\nPlanning Guidance: {planning_structure}")
            
        prompt_parts.extend([
            f"\nGenerate substantial, valuable content that serves the {context.audience}.",
            f"Focus on {context.intent}ing the audience about {context.topic}.",
            "Write engaging, well-structured content with clear value."
        ])
        
        return "\n".join(prompt_parts)

    def generate_content(self, state: EnrichedContentState) -> str:
        """Single content generation method - no fallbacks, no complex logic"""
        
        # Extract context
        context = self.extract_context(state)
        logger.info(f"Generating content for topic: {context.topic}")
        
        # Build prompt
        prompt = self.build_simple_prompt(context, state)
        
        # Get model
        from langgraph_app.enhanced_model_registry import get_model
        model_obj = get_model("writer")
        model_name = model_obj.model_name
        
        # Generate content
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a professional content writer. Create valuable, engaging content based on the requirements provided."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            if not content or len(content.strip()) < 100:
                raise RuntimeError(f"Generated content too short: {len(content)} chars")
                
            logger.info(f"Successfully generated {len(content)} characters")
            return content.strip()
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise RuntimeError(f"Content generation failed: {e}")

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute writer agent - simplified interface"""
        
        try:
            # Generate content using simple method
            content = self.generate_content(state)
            
            # Set content in state
            state.content = content
            state.final_content = content
            state.draft_content = content
            
            logger.info(f"Writer completed: {len(content)} characters")
            return state
            
        except Exception as e:
            logger.error(f"Writer execution failed: {e}")
            raise RuntimeError(f"Writer execution failed: {e}")

# Export simplified writer
template_aware_writer_agent = TemplateAwareWriterAgent()

# Legacy compatibility
TemplateAwareWriterAgent = TemplateAwareWriterAgent
template_aware_writer_agent = template_aware_writer_agent