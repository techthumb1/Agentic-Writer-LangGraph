# File: langgraph_app/agents/writer.py
from multiprocessing import context
import os
import re
from click import prompt
from sqlalchemy import text
import yaml
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from langgraph_app.enhanced_model_registry import get_model
from langgraph_app.core.enriched_content_state import EnrichedContentState
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph_app.agents.realtime_search import RealTimeSearchMixin

from langgraph_app.enhanced_model_registry import get_model_for_generation
from langgraph_app.core.enriched_content_state import (
    EnrichedContentState,
    AgentType,
    ContentPhase
)

logger = logging.getLogger(__name__)
load_dotenv()

class WritingMode(Enum):
    CREATIVE = "creative"
    ANALYTICAL = "analytical" 
    TECHNICAL = "technical"
    NARRATIVE = "narrative"
    PERSUASIVE = "persuasive"
    EXPERIMENTAL = "experimental"

class AdaptiveLevel(Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    INNOVATIVE = "innovative"
    EXPERIMENTAL = "experimental"

@dataclass
class WritingContext:
    """Rich context for adaptive writing decisions"""
    topic: str
    audience: str
    platform: str
    intent: str
    complexity_level: int = 5
    innovation_preference: AdaptiveLevel = AdaptiveLevel.BALANCED
    constraints: Dict[str, Any] = field(default_factory=dict)
    success_patterns: List[Dict] = field(default_factory=list)
    failure_patterns: List[Dict] = field(default_factory=list)

@dataclass 
class WritingStrategy:
    """Dynamic strategy that adapts based on context and outcomes"""
    mode: WritingMode
    structure_pattern: str
    tone_adaptation: Dict[str, float]
    experimental_techniques: List[str]
    confidence_threshold: float = 0.7

# File: langgraph_app/writer.py
# Phase 4b — Strengthen sanitizer to strip any residual code-like content
# (handles cases where backticks get split across paragraphs / HTML wrappers).

import re

CODE_FENCE_RX = re.compile(r"`{3,}.*?`{3,}", flags=re.S)
INLINE_CODE_RX = re.compile(r"`[^`]+`")
# Lines that clearly look like code or config, kept conservative to avoid prose
CODEY_LINE_RX = re.compile(
    r"^\s*(?:#include\b|import\b|from\b.+\bimport\b|def\b|class\b|return\b|console\.\w+\(|var\b|let\b|const\b|function\b|if\s*\(|else\b|for\s*\(|while\s*\(|try\b|catch\b|<\?php|SELECT\b|INSERT\b|UPDATE\b|DELETE\b|CREATE\s+TABLE\b|\{|\}|\/\/|\-\- )",
    flags=re.I,
)
BACKTICK_ANYWHERE_RX = re.compile(r"`{3,}|`{1}")

class Writer:
    # ... existing class code ...

    def _sanitize_and_enforce(self, raw: str, *, min_paragraphs: int = 4, max_bullets: int = 6) -> str:
        """
        Enterprise: remove code blocks/snippets, collapse bullet sprawl, enforce paragraph-first output.
        Raises ValueError if constraints are not met after sanitation.
        """
        text = raw or ""

        # 1) Remove fenced code blocks and inline backticks (markdown form)
        text = CODE_FENCE_RX.sub("", text)
        text = INLINE_CODE_RX.sub("", text)

        # 2) Line-wise sweep to drop obvious code/config lines and paragraphs that still contain backticks
        lines = text.splitlines()
        cleaned_lines = []
        for ln in lines:
            # Drop lines that contain any backtick sequences (even if separated by HTML later)
            if BACKTICK_ANYWHERE_RX.search(ln):
                continue
            # Drop lines that look like code/comments/SQL/etc.
            if CODEY_LINE_RX.match(ln):
                continue
            cleaned_lines.append(ln)
        text = "\n".join(cleaned_lines)

        # 3) Limit bullets: convert excess bullets into sentences
        bullet_re = re.compile(r"^\s*[-•*]\s+")
        lines = text.splitlines()
        bullets = [i for i, ln in enumerate(lines) if bullet_re.match(ln)]
        if len(bullets) > max_bullets:
            for i in bullets[max_bullets:]:
                lines[i] = bullet_re.sub("", lines[i])
            text = "\n".join(lines)

        # 4) Normalize paragraphs
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        if len(paragraphs) < min_paragraphs:
            raise ValueError(f"Writer output too sparse: {len(paragraphs)} paragraphs < {min_paragraphs}")

        return "\n\n".join(paragraphs)

    # Ensure the final return path uses _sanitize_and_enforce (already wired in previous step)


def safe_config_access(config):
    """Safely access config that might be string, dict, or SimpleNamespace"""
    if isinstance(config, str):
        try:
            return json.loads(config)
        except:
            return {}
    elif isinstance(config, dict):
        return config
    elif hasattr(config, '__dict__'):  # SimpleNamespace
        return vars(config)
    else:
        return {}

class TemplateAwareWriterAgent(RealTimeSearchMixin):
    """FIXED: Universal Configuration-Driven Writer Agent with Real-time Capability - NO HARDCODED TEMPLATES"""

    def __init__(self):
        """Initialize TemplateAwareWriterAgent with required clients and paths"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable required")
        
        self.client = OpenAI(api_key=api_key)
        self.researcher_agent = None  # Will be set by MCP graph
        self.web_search_tool = None   # Will be set by MCP graph
        self.max_real_time_age_hours = 72  # Default staleness threshold

        self.template_paths = [
            "data/content_templates",
            "langgraph_app/data/content_templates",
            "content_templates"
        ]

        self.prompt_paths = [
            "prompts/writer",
            "langgraph_app/prompts/writer", 
            "prompts"
        ]

        self.memory_path = Path("storage/agent_memory")
        self.memory_path.mkdir(parents=True, exist_ok=True)

    def load_style_profile(self, name: str) -> Dict:
        """Load style profile using dynamic loader"""
        if not name or len(name) > 50 or '/' in name or '\\' in name:
            raise ValueError(f"ENTERPRISE: Invalid style profile name: {name}")

        try:
            # Use existing dynamic loader
            from langgraph_app.style_profile_loader import get_dynamic_style_profile_loader
            style_loader = get_dynamic_style_profile_loader()

            profile = style_loader.get_profile(name)
            if not profile:
                # List available for better error message
                available = style_loader.list_profiles()
                raise FileNotFoundError(f"ENTERPRISE: Style profile '{name}' not found. Available: {available}")

            if not profile.get('system_prompt'):
                raise ValueError(f"ENTERPRISE: Style profile {name} missing system_prompt")

            logger.info(f"✅ Loaded style profile: {name}")
            return profile

        except Exception as e:
            raise RuntimeError(f"ENTERPRISE: Failed to load style profile {name}: {e}")
    
    def load_template_config(self, template_id: str) -> Dict[str, Any]:
        """Load template config using dynamic loader"""
        if not template_id:
            return {}

        try:
            # Use existing template loader
            from langgraph_app.template_loader import get_template_loader
            template_loader = get_template_loader()

            template_data = template_loader.get_template(template_id)
            if template_data:
                logger.info(f"✅ Loaded template config: {template_id}")
                return template_data

            # List available for better error message
            available = template_loader.list_templates()
            logger.warning(f"Template '{template_id}' not found. Available: {available}")
            return {}

        except Exception as e:
            logger.error(f"Error loading template {template_id}: {e}")
            return {}

    def validate_enterprise_config(self, template_config, style_config):
        """FIXED: Validate actual config objects passed as parameters"""
        if not template_config or not isinstance(template_config, dict):
            raise RuntimeError("ENTERPRISE: template_config required - no fallbacks")
        if not style_config or not isinstance(style_config, dict):
            raise RuntimeError("ENTERPRISE: style_config required - no fallbacks")

    def build_from_template_schema(self, template_config: Dict, context: Dict) -> str:
        """Build prompt from template's prompt_schema"""
        
        prompt_schema = template_config.get('prompt_schema')
        if not prompt_schema:
            raise ValueError("ENTERPRISE: Template missing prompt_schema")
        
        system_preamble = prompt_schema.get('system_preamble')
        if not system_preamble:
            raise ValueError("ENTERPRISE: Template missing system_preamble")
        
        content_template = prompt_schema.get('content_template')
        if not content_template:
            raise ValueError("ENTERPRISE: Template missing content_template")
        
        # Replace placeholders with actual values
        placeholders = prompt_schema.get('placeholders', [])
        final_prompt = system_preamble + "\n\n" + content_template
        
        for placeholder in placeholders:
            value = context.get(placeholder, f"[{placeholder}]")
            final_prompt = final_prompt.replace(f"{{{{{placeholder}}}}}", str(value))
        
        return final_prompt    # [enterprise schema-based prompt building code from previous response]


    def get_template_specific_prompt(self, template_config: Dict[str, Any], template_id: str, state: Dict = None) -> str:
        """Enterprise prompt generation with schema validation"""

        # PRIORITY 1: Use MCP research if available
        if state and self.has_mcp_research(state):
            print("Using MCP research-integrated prompt")
            return self._build_research_integrated_prompt(template_config, template_id, state)

        # PRIORITY 2: Use prompt_schema if available
        if template_config and template_config.get('prompt_schema'):
            print("Using template prompt_schema")
            context = self.extract_context_values(state) if state else {}
            return self.build_from_template_schema(template_config, context)

        # PRIORITY 3: Generate from template configuration
        if template_config:
            dynamic_prompt = self._generate_prompt_from_config(template_config, template_id)
            if dynamic_prompt:
                print("Generated dynamic prompt from template config")
                return dynamic_prompt

        # ENTERPRISE: Fail fast if no valid template found
        raise RuntimeError(f"ENTERPRISE: No valid template configuration for {template_id}")


    def extract_context_values(self, state: Dict) -> Dict:
        context = {
            "topic": state.get("topic", ""),
            "audience": state.get("audience", ""),
            "content_type": "content"
        }
        return context

    # File: langgraph_app/agents/writer.py
    # Replace the analyze_context method (lines ~320-370)

    def analyze_context(self, state: Dict) -> WritingContext:
        """Extract and enrich context from state - FIXED topic extraction priority"""
        params = state.get("dynamic_parameters", {})
        raw_template_config = state.get('template_config', {})
        template_config = safe_config_access(raw_template_config)

        # PRIORITY 1: Extract topic from content_spec (set by planner)
        content_spec = state.get('content_spec')
        topic = None

        if content_spec and hasattr(content_spec, 'topic'):
            topic = content_spec.topic
            print(f"DEBUG: Found topic in content_spec: {topic}")
        elif content_spec and isinstance(content_spec, dict) and 'topic' in content_spec:
            topic = content_spec['topic']
            print(f"DEBUG: Found topic in content_spec dict: {topic}")

        # PRIORITY 2: Try dynamic_overrides from template_config (nested structure)
        if not topic and isinstance(template_config, dict) and 'dynamic_overrides' in template_config:
            outer_overrides = template_config['dynamic_overrides']
            if isinstance(outer_overrides, dict) and 'dynamic_overrides' in outer_overrides:
                dynamic_overrides = outer_overrides['dynamic_overrides']
                topic = dynamic_overrides.get("topic")
                if topic:
                    print(f"DEBUG: Found topic in nested dynamic_overrides: {topic}")
            elif isinstance(outer_overrides, dict):
                topic = outer_overrides.get("topic")
                if topic:
                    print(f"DEBUG: Found topic in single-level dynamic_overrides: {topic}")

        # PRIORITY 3: Try params dynamic_overrides
        if not topic:
            dynamic_overrides = params.get("dynamic_overrides", {})
            topic = dynamic_overrides.get("topic") if dynamic_overrides else None
            if topic:
                print(f"DEBUG: Found topic in params dynamic_overrides: {topic}")

        # ENTERPRISE: Fail fast if no topic found
        if not topic:
            available_keys = []
            if content_spec:
                if hasattr(content_spec, '__dict__'):
                    available_keys.extend(f"content_spec.{k}" for k in vars(content_spec).keys())
                elif isinstance(content_spec, dict):
                    available_keys.extend(f"content_spec.{k}" for k in content_spec.keys())

            raise ValueError(f"ENTERPRISE: Missing topic. Available: {available_keys}")

        print(f"DEBUG: Successfully extracted topic: {topic}")

        # Extract audience with same priority system
        audience = None
        if content_spec and hasattr(content_spec, 'audience'):
            audience = content_spec.audience
        elif content_spec and isinstance(content_spec, dict) and 'audience' in content_spec:
            audience = content_spec['audience']

        if not audience:
            # Try dynamic_overrides for audience
            dynamic_overrides = template_config.get('dynamic_overrides', {})
            if isinstance(dynamic_overrides, dict) and 'dynamic_overrides' in dynamic_overrides:
                dynamic_overrides = dynamic_overrides['dynamic_overrides']

            audience = (dynamic_overrides.get("target_audience") or 
                       dynamic_overrides.get("audience") or
                       template_config.get("target_audience") or
                       "general audience")

        # Analyze intent and complexity
        intent = self._analyze_intent_from_context(template_config, params, state)
        complexity = self._analyze_complexity_from_context(template_config, params, state)

        return WritingContext(
            topic=topic,
            audience=audience,
            platform=state.get("platform", "substack"),
            intent=intent,
            complexity_level=complexity,
            innovation_preference=AdaptiveLevel(
                template_config.get("innovation_level", "balanced")
            )
        )    
    
    def _analyze_complexity_from_context(self, template_config: Dict, params: Dict, state: Dict) -> int:
        """Analyze complexity level from context - REMOVED VALIDATION"""
        # Check template config first
        if template_config.get("complexity_level"):
            return template_config["complexity_level"]

        # Analyze from available text
        all_text = str(template_config) + str(params) + str(state)
        text_lower = all_text.lower()

        complexity_indicators = {
            9: ['phd', 'doctorate', 'expert', 'advanced', 'research'],
            8: ['professional', 'technical', 'specialist', 'enterprise'],
            7: ['experienced', 'intermediate', 'business'],
            6: ['educated', 'college', 'university'],
            4: ['beginner', 'basic', 'simple', 'introduction'],
            3: ['elementary', 'fundamental', 'starter']
        }

        for complexity, indicators in complexity_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return complexity

        return 5  # Default

    def _analyze_intent_from_context(self, template_config: Dict, params: Dict, state: Dict) -> str:
        if template_config.get("intent"):
            return template_config["intent"]
        
        all_text = str(template_config) + str(params) + str(state)
        text_lower = all_text.lower()
        
        intent_indicators = {
            'persuade': ['convince', 'argue', 'persuade', 'sell', 'promote'],
            'teach': ['learn', 'teach', 'guide', 'tutorial', 'education', 'explain'],
            'inspire': ['inspire', 'motivate', 'vision', 'transform', 'empower'],
            'entertain': ['story', 'narrative', 'journey', 'experience'],
            'analyze': ['analyze', 'research', 'study', 'examine', 'investigate']
        }
        
        for intent, indicators in intent_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return intent
        
        return "inform"

    def _analyze_audience_from_context(self, params: Dict, state: Dict) -> str:
        """Analyze audience from available context - REMOVED VALIDATION"""
        # Look for audience indicators in the data
        all_context = str(params) + str(state)
        context_lower = all_context.lower()

        if any(word in context_lower for word in ['executive', 'c-level', 'leadership']):
            return 'executive_audience'
        elif any(word in context_lower for word in ['technical', 'developer', 'engineer']):
            return 'technical_audience'
        elif any(word in context_lower for word in ['beginner', 'new', 'introduction']):
            return 'beginner_audience'
        elif any(word in context_lower for word in ['professional', 'business']):
            return 'professional_audience'
        else:
            return 'general_audience'

    def _extract_topic_from_context(self, params: Dict, state: Dict) -> str:
        """Extract topic from available context - REMOVED VALIDATION"""
        # Look for topic-like content in various fields
        possible_topics = [
            params.get('subject'),
            params.get('title'),
            state.get('subject'),
            state.get('title')
        ]

        for topic in possible_topics:
            if topic and len(str(topic).strip()) > 0:
                return str(topic).strip()
        return 'Strategic Analysis'




#    def _create_enhanced_prompt(self, context: WritingContext, template_config: Dict[str, Any], state: Dict) -> str:
#        """FIXED: Create comprehensive writing prompt with DYNAMIC length requirements"""
#        if hasattr(template_config, '__dict__') and not hasattr(template_config, 'get'):
#            template_config = vars(template_config)
#        if not template_config:
#            template_config = self._extract_guaranteed_template_config(state)
#
#        planning = state.get('planning_output')
#        if planning and hasattr(planning, '__dict__') and not hasattr(planning, 'get'):
#            planning = vars(planning)
#        state['planning_output'] = planning
#
#        # CRITICAL FIX: Extract user's preferred length from generation settings
#        gen_settings = state.get("generation_settings", {})
#        preferred_length = gen_settings.get("preferred_length", "medium")
#        max_tokens = gen_settings.get("maxTokens", 4000)
#
#        # FIXED: Map preferred_length to actual word targets (NOT hardcoded minimums)
#        if preferred_length == "short":
#            target_words = min(1500, max_tokens * 0.6)  # Short: 900-1500 words
#            min_section_words = 150  # Much shorter sections
#            depth_requirement = "concise coverage with key examples"
#        elif preferred_length == "long":
#            target_words = min(max_tokens * 0.8, 6000)  # Long: up to 6000 words  
#            min_section_words = 400  # Original section length
#            depth_requirement = "comprehensive detail with extensive examples"
#        else:  # medium (default)
#            target_words = min(max_tokens * 0.7, 3500)  # Medium: 2000-3500 words
#            min_section_words = 250  # Moderate sections
#            depth_requirement = "substantial coverage with relevant examples"
#
#        # Override template config if user explicitly set length
#        if preferred_length and preferred_length != "medium":
#            print(f"🎯 APPLYING USER LENGTH: {preferred_length} -> {int(target_words)} words, {min_section_words} per section")
#
#        section_order = template_config.get('section_order', [])
#        tone_config = template_config.get('tone', {})
#
#        prompt_parts = []
#
#        # 1. DYNAMIC STRUCTURE SECTION
#        if section_order:
#            prompt_parts.append("**REQUIRED SECTIONS (DYNAMIC LENGTH STRUCTURE):**")
#            prompt_parts.append("\n".join([f"## {section} (TARGET {min_section_words} WORDS)" for section in section_order]))
#        elif planning and hasattr(planning, 'estimated_sections'):
#            sections = [section.get('name', f'Section {i+1}') for i, section in enumerate(planning.estimated_sections)]
#            prompt_parts.append("**REQUIRED SECTIONS (DYNAMIC LENGTH STRUCTURE):**")
#            prompt_parts.append("\n".join([f"## {section} (TARGET {min_section_words} WORDS)" for section in sections]))
#        else:
#            dynamic_sections = self._generate_universal_sections(context, template_config)
#            prompt_parts.append("**REQUIRED SECTIONS (DYNAMIC LENGTH STRUCTURE):**")
#            prompt_parts.append("\n".join([f"## {section} (TARGET {min_section_words} WORDS)" for section in dynamic_sections]))
#
#        # 2. DYNAMIC REQUIREMENTS SECTION
#        requirements = [
#            f"- TARGET {int(target_words)} words total (User preference: {preferred_length})",
#            f"- Each section should be approximately {min_section_words} words with {depth_requirement}",
#            "- Match the requested content length - do not exceed user preferences",
#            "- Focus on quality over quantity - every word should add value"
#        ]
#
#        template_requirements = template_config.get('content_requirements', [])
##        if template_requirements:
##            requirements.extend([f"- {req}" for req in template_requirements])
##        else:
##            dynamic_requirements = self._generate_universal_requirements(context, template_config)
##            requirements.extend(dynamic_requirements)
#
#        # Add length-appropriate requirements
#        if preferred_length == "short":
#            requirements.extend([
#                "- Be concise and direct - avoid unnecessary elaboration",
#                "- Focus on the most essential points and actionable insights",
#                "- Use bullet points and clear structure for easy scanning"
#            ])
#        elif preferred_length == "long":
#            requirements.extend([
#                "- Provide comprehensive coverage with extensive examples",
#                "- Include detailed step-by-step processes where applicable", 
#                "- Add supporting data, metrics, and evidence throughout"
#            ])
#
#        prompt_parts.append("**DYNAMIC CONTENT REQUIREMENTS:**")
#        prompt_parts.append("\n".join(requirements))
#
#        # 3. TONE SECTION
#        tone_guidance = self._generate_universal_tone_guidance(context, template_config, tone_config)
#        prompt_parts.append(f"**TONE AND STYLE:** {tone_guidance}")
#
#        # 4. CONTEXT SECTION
#        prompt_parts.extend([
#            f"**TOPIC:** {context.topic}",
#            f"**AUDIENCE:** {context.audience}",
#            f"**COMPLEXITY LEVEL:** {context.complexity_level}/10",
#            f"**USER LENGTH PREFERENCE:** {preferred_length} ({int(target_words)} target words)"
#        ])
#
#        # 5. FINAL INSTRUCTION WITH LENGTH RESPECT
#        final_instruction = f"""**GENERATION MANDATE:**
#    Generate expert-level content about {context.topic} for {context.audience}.
#    - TARGET LENGTH: {int(target_words)} words ({preferred_length} format requested by user)  
#    - Each section: approximately {min_section_words} words
#    - RESPECT the user's length preference - do not generate more content than requested
#    - {depth_requirement}
#    - Write as the expert resource within the specified length constraints"""
#
#        prompt_parts.append(final_instruction)
#
#        return "\n".join(prompt_parts)

  
#    def _generate_universal_sections(self, context: WritingContext, template_config: Dict[str, Any]) -> List[str]:
#        sections = [f"{context.topic} Overview"]
#        topic_analysis = self._analyze_topic_characteristics(context.topic, context.audience)
#        
#        if topic_analysis['is_business_focused']:
#            sections.extend(["Strategic Analysis", "Market Considerations", "Implementation Approach", "Success Metrics", "Next Steps"])
#        elif topic_analysis['is_technical']:
#            sections.extend(["Technical Foundation", "Implementation Guide", "Best Practices", "Practical Examples", "Troubleshooting"])
#        else:
#            sections.extend([f"Understanding {context.topic}", "Key Principles", "Practical Applications", "Implementation Considerations", "Future Outlook"])
#        
#        sections.append("Key Takeaways")
#        return sections

#    def _generate_universal_requirements(self, context: WritingContext, template_config: Dict[str, Any]) -> List[str]:
#        requirements = []
#        topic_analysis = self._analyze_topic_characteristics(context.topic, context.audience)
#
#        if topic_analysis['is_business_focused']:
#            requirements.extend([
#                "- Include comprehensive data analysis, detailed metrics, and complete business case with ROI calculations",
#                "- Provide extensive strategic recommendations with step-by-step implementation roadmaps"
#            ])
#        elif topic_analysis['is_technical']:
#            requirements.extend([
#                "- Provide comprehensive, implementable technical guidance with detailed architecture explanations",
#                "- Include extensive working examples, complete code samples, and detailed configuration guides"
#            ])
#        else:
#            requirements.extend([
#                "- Provide comprehensive, original insights backed by detailed research and analysis",
#                "- Include extensive specific examples, detailed case studies, and thorough comparative analysis"
#            ])
#
#        requirements.extend([
#            "- Use detailed, engaging writing style with comprehensive explanations throughout",
#            "- Maintain logical structure with smooth transitions and comprehensive flow between sections"
#        ])
#
#        return requirements


    def _generate_universal_tone_guidance(self, context: WritingContext, template_config: Dict[str, Any], tone_config: Dict) -> str:
        tone_elements = []
        
        formality = tone_config.get('formality', 'professional')
        voice = tone_config.get('voice', 'authoritative')
        persuasiveness = tone_config.get('persuasiveness', 'balanced')
        
        tone_elements.extend([f"{formality} formality", f"{voice} voice", f"{persuasiveness} persuasiveness"])
        
        if "executive" in context.audience.lower():
            tone_elements.append("strategic and decision-oriented")
        elif "technical" in context.audience.lower():
            tone_elements.append("precise and implementation-focused")
        elif "beginner" in context.audience.lower():
            tone_elements.append("educational and supportive")
        
        return ", ".join(tone_elements)

    def _analyze_topic_characteristics(self, topic: str, audience: str) -> Dict[str, bool]:
        topic_lower = topic.lower()
        audience_lower = audience.lower()
        
        return {
            'is_business_focused': any(word in topic_lower for word in ['business', 'strategy', 'market', 'revenue', 'growth', 'roi']) or 'executive' in audience_lower,
            'is_technical': any(word in topic_lower for word in ['technical', 'implementation', 'development', 'api', 'system', 'code']) or any(word in audience_lower for word in ['developer', 'engineer', 'technical']),
            'is_educational': any(word in topic_lower for word in ['learn', 'guide', 'tutorial', 'how to', 'introduction']) or any(word in audience_lower for word in ['student', 'beginner', 'learner']),
        }

    def _extract_guaranteed_template_config(self, state: Dict) -> dict:
        """Enterprise: Require non-empty template_config - REMOVED VALIDATION"""
        if "template_config" in state and state["template_config"]:
            return state["template_config"]
        if "content_spec" in state and hasattr(state["content_spec"], "business_context"):
            tc = state["content_spec"].business_context.get("template_config", {})
            if tc:
                return tc
        raise RuntimeError("Enterprise mode: template_config must be a non-empty dict before Writer runs")
        
    def has_mcp_research(self, state: Dict) -> bool:
        """Check if MCP research data is available - NO VALIDATION"""
        research_indicators = [
            state.get('research_findings'),
            state.get('mcp_results'),
            state.get('tools_executed'),
            state.get('research_data'),
            state.get('quality_enhancements')
        ]

        for indicator in research_indicators:
            if indicator:
                if isinstance(indicator, dict) and len(indicator) > 0:
                    return True
                elif isinstance(indicator, list) and len(indicator) > 0:
                    return True
                elif isinstance(indicator, str) and len(indicator.strip()) > 10:
                    return True

        print("🔍 No MCP research detected - using template-based generation")
        return False

    def extract_mcp_research_data(self, state: Dict) -> Dict[str, Any]:
        """Extract and consolidate MCP research data from state - REMOVED VALIDATION"""
        research_data = {
            'academic_sources': [],
            'technical_findings': [],
            'industry_insights': [],
            'code_examples': [],
            'api_documentation': [],
            'validation_results': [],
            'raw_findings': {}
        }

        # Extract from various state locations
        if state.get('research_findings'):
            research_data['raw_findings'].update(state['research_findings'])

        if state.get('mcp_results'):
            mcp_results = state['mcp_results']

            # Extract by tool type
            for tool_name, result in mcp_results.items():
                if 'academic' in tool_name:
                    research_data['academic_sources'].extend(self._extract_sources(result))
                elif 'code' in tool_name or 'api' in tool_name:
                    research_data['technical_findings'].append(result)
                    if 'api' in tool_name:
                        research_data['api_documentation'].append(result)
                elif 'industry' in tool_name or 'trend' in tool_name:
                    research_data['industry_insights'].append(result)
                elif 'validation' in tool_name or 'fact' in tool_name:
                    research_data['validation_results'].append(result)

        # Extract from tools_executed if available
        if state.get('tools_executed'):
            research_data['tools_used'] = state['tools_executed']

        print(f"📊 Extracted MCP research: {len(research_data['raw_findings'])} findings from {len(research_data.get('tools_used', []))} tools")
        return research_data

    #def _build_research_integrated_prompt(self, template_config: Dict[str, Any], template_id: str, state: Dict) -> str:
    #    """Build prompt that integrates MCP research findings - REMOVED VALIDATION"""
    #    # Extract research data
    #    research_data = self.extract_mcp_research_data(state)
#
    #    # Get topic and audience from context
    #    topic = (template_config.get("topic") or 
    #             state.get("dynamic_parameters", {}).get("topic") or 
    #             state.get("topic", "the specified topic"))
#
    #    audience = (template_config.get("target_audience") or
    #                state.get("dynamic_parameters", {}).get("target_audience") or
    #                state.get("audience", "general audience"))
#
    #    # FIXED: Extract generation settings for comprehensive length control
    #    gen_settings = state.get("generation_settings", {})
    #    max_tokens = gen_settings.get("maxTokens", 4000)
    #    target_words = min(max_tokens * 0.75, 4000)  # Conservative word estimate
#
    #    # Determine comprehensive length requirements based on maxTokens
    #    if max_tokens >= 3500:
    #        length_instruction = f"COMPREHENSIVE LONGFORM CONTENT: Generate minimum {int(target_words)} words with exhaustive detailed analysis"
    #        section_depth = "Each section must be 500-700 words with extensive detail and examples"
    #        research_usage = "Expand EVERY research finding into detailed 3-4 paragraph explanations with context, implications, and examples"
    #    elif max_tokens >= 2500:
    #        length_instruction = f"DETAILED LONGFORM CONTENT: Generate minimum {int(target_words)} words with thorough coverage" 
    #        section_depth = "Each section must be 400-600 words with substantial detail"
    #        research_usage = "Expand each research finding into detailed 2-3 paragraph explanations with examples"
    #    elif max_tokens >= 1500:
    #        length_instruction = f"SUBSTANTIAL CONTENT: Generate minimum {int(target_words)} words"
    #        section_depth = "Each section must be 300-400 words with comprehensive coverage"
    #        research_usage = "Expand research findings into detailed explanations with specific examples"
    #    else:
    #        length_instruction = f"COMPREHENSIVE CONTENT: Generate minimum {int(target_words)} words"
    #        section_depth = "Each section must be 250-350 words"
    #        research_usage = "Provide detailed explanations for each research finding"
#
    #    # Build comprehensive research-driven prompt
    #    prompt_parts = []
#
    #    # Header - LONGFORM RESEARCH EMPHASIS
    #    template_type = template_config.get('template_type', template_id)
    #    prompt_parts.append(f"""You are an expert content creator writing comprehensive {template_type.replace('_', ' ')} about {topic} for {audience}.
#
    #CRITICAL LONGFORM REQUIREMENTS: 
    #- {length_instruction}
    #- {section_depth}
    #- {research_usage}
    #- NO brief summaries, overviews, or placeholder content
    #- Every research point must be thoroughly explained and expanded
    #- Use extensive examples, case studies, detailed analysis, and step-by-step processes
    #- Transform research data into the most comprehensive content possible
#
    #RESEARCH INTEGRATION MANDATE: You have extensive research findings. Use ALL of this data to create DETAILED, SUBSTANTIVE content that provides maximum value.""")
#
    #    # FIXED: Research Integration with explicit expansion requirements
    #    if research_data['academic_sources']:
    #        prompt_parts.append(f"\nACADEMIC RESEARCH FINDINGS (EXPAND EACH INTO 200-300 WORD ANALYSIS):")
    #        for i, source in enumerate(research_data['academic_sources'][:5], 1):
    #            prompt_parts.append(f"{i}. {source}")
    #            prompt_parts.append(f"   → MANDATORY: Expand this into detailed analysis with implications, context, examples, and practical applications")
#
    #    if research_data['technical_findings']:
    #        prompt_parts.append(f"\nTECHNICAL INSIGHTS (COMPREHENSIVE TECHNICAL COVERAGE REQUIRED):")
    #        for i, finding in enumerate(research_data['technical_findings'][:5], 1):
    #            prompt_parts.append(f"{i}. {finding}")
    #            prompt_parts.append(f"   → MANDATORY: Provide detailed technical explanation with implementation examples, code samples, and best practices")
#
    #    if research_data['industry_insights']:
    #        prompt_parts.append(f"\nINDUSTRY ANALYSIS (DETAILED MARKET ANALYSIS REQUIRED):")
    #        for i, insight in enumerate(research_data['industry_insights'][:5], 1):
    #            prompt_parts.append(f"{i}. {insight}")
    #            prompt_parts.append(f"   → MANDATORY: Comprehensive market analysis with trend implications, strategic recommendations, and competitive landscape")
#
    #    if research_data['api_documentation']:
    #        prompt_parts.append(f"\nAPI/TECHNICAL DOCUMENTATION (COMPREHENSIVE IMPLEMENTATION GUIDE):")
    #        for i, doc in enumerate(research_data['api_documentation'][:3], 1):
    #            prompt_parts.append(f"{i}. {doc}")
    #            prompt_parts.append(f"   → MANDATORY: Step-by-step implementation guide with code examples, troubleshooting, and integration patterns")
#
    #    # Raw research findings with expansion mandates
    #    if research_data['raw_findings']:
    #        prompt_parts.append(f"\nADDITIONAL RESEARCH DATA (INTEGRATE COMPREHENSIVELY):")
    #        for tool_name, findings in list(research_data['raw_findings'].items())[:5]:
    #            prompt_parts.append(f"- {tool_name.title()}: {str(findings)[:400]}...")
    #            prompt_parts.append(f"   → MANDATORY: Extract key insights and provide detailed analysis with practical applications")
#
    #    # FIXED: Comprehensive content generation requirements
    #    prompt_parts.append(f"""
    #COMPREHENSIVE CONTENT GENERATION REQUIREMENTS:
    #- ABSOLUTE MINIMUM {int(target_words)} WORDS with detailed coverage throughout
    #- Each research finding must be transformed into 2-4 detailed paragraphs
    #- Provide extensive real-world examples, case studies, and step-by-step processes
    #- Include detailed implementation guidance where applicable
    #- NO placeholder text, brief summaries, or generic content
    #- Every section must contain substantial, actionable information from research
    #- Use research to create the most thorough, valuable content possible on {topic}
    #- Write as an expert who has conducted comprehensive research on the subject""")
#
    #    # Structure guidance with comprehensive section requirements
    #    if template_config.get('section_order'):
    #        prompt_parts.append(f"\nREQUIRED SECTIONS (EACH {section_depth.split()[5]} WORDS MINIMUM):")
    #        for section in template_config['section_order']:
    #            prompt_parts.append(f"## {section}")
    #            prompt_parts.append(f"   REQUIREMENTS: {section_depth.split()[5]} words minimum, integrate relevant research extensively with detailed analysis")
    #    else:
    #        # Dynamic comprehensive sections based on research
    #        prompt_parts.append(f"""COMPREHENSIVE STRUCTURE ({section_depth.split()[5]} words per section):
    ### Introduction to {topic}
    #   REQUIREMENTS: {section_depth.split()[5]} words - Use research to establish comprehensive context, importance, and current landscape
#
    ### Research-Based Analysis  
    #   REQUIREMENTS: {section_depth.split()[5]} words - Present detailed findings from academic, technical, and industry research with analysis
#
    ### Technical Implementation
    #   REQUIREMENTS: {section_depth.split()[5]} words - Apply research insights to detailed implementation with examples and best practices
#
    ### Industry Applications and Case Studies
    #   REQUIREMENTS: {section_depth.split()[5]} words - Comprehensive analysis of real-world applications with specific examples
#
    ### Strategic Recommendations
    #   REQUIREMENTS: {section_depth.split()[5]} words - Synthesize research into detailed, actionable strategic guidance
#
    ### Future Implications and Trends
    #   REQUIREMENTS: {section_depth.split()[5]} words - Comprehensive analysis of future outlook based on research findings""")
#
    #    # Final comprehensive instruction
    #    prompt_parts.append(f"""
    #FINAL COMPREHENSIVE GENERATION INSTRUCTIONS:
    #- Generate the complete {template_type.replace('_', ' ')} incorporating ALL research findings
    #- Minimum {int(target_words)} words with exhaustive coverage of {topic}
    #- Every claim must be supported by the provided research
    #- Use specific data, examples, and detailed analysis throughout
    #- Write as a subject matter expert with comprehensive knowledge
    #- NO generic content - everything must be research-backed and substantial
#
    #Begin generating the comprehensive content now:""")
#
    #    return "\n".join(prompt_parts)

    def _extract_sources(self, result: Any) -> List[str]:
        sources = []
        if isinstance(result, dict):
            if 'sources' in result:
                sources.extend(result['sources'])
            if 'data' in result:
                sources.append(str(result['data'])[:200] + "...")
        elif isinstance(result, list):
            sources.extend([str(item)[:100] + "..." for item in result[:3]])
        elif isinstance(result, str):
            sources.append(result[:200] + "..." if len(result) > 200 else result)
        return sources

    def calculate_required_tokens(self, template_config: Dict, dynamic_overrides: Dict) -> int:
        """Extract exact token requirements from template config"""

        # ENTERPRISE: Extract from template config requirements
        requirements = template_config.get('requirements', {})
        if not requirements:
            raise ValueError("ENTERPRISE: Template missing requirements section")

        min_words = requirements.get('min_words')
        if not min_words:
            raise ValueError("ENTERPRISE: Template missing min_words requirement")

        # Priority extraction from requirements
        if isinstance(min_words, dict) and 'priority' in min_words:
            for source in min_words['priority']:
                # Type validation before operations
                if not isinstance(source, (str, int, float)):
                    raise TypeError(f"ENTERPRISE: Invalid source type {type(source)} in min_words priority")

                if isinstance(source, str) and source.startswith('dynamic.') and dynamic_overrides:
                    key = source.replace('dynamic.', '')
                    value = dynamic_overrides.get(key)
                    if value and isinstance(value, (int, float)):
                        return int(value * 1.3)
                elif isinstance(source, (int, float)):
                    return int(source * 1.3)

        raise ValueError("ENTERPRISE: No valid min_words found in template requirements")

    def _sanitize_prompt(self, prompt: str) -> str:
        """Enhanced prompt sanitization with diagnostics"""
        if not prompt:
            print("WARN: Empty prompt provided to sanitization")
            return "Generate comprehensive content."
        
        if not isinstance(prompt, str):
            prompt = str(prompt)
        
        # Remove problematic characters
        original_length = len(prompt)
        prompt = prompt.replace('\x00', '')
        prompt = prompt.replace('\r\n', '\n')
        prompt = prompt.replace('\r', '\n')
        
        # Remove excessive whitespace
        prompt = ' '.join(prompt.split())
        
        final_length = len(prompt)
        
        if final_length != original_length:
            print(f"DEBUG: Prompt sanitized: {original_length} -> {final_length} chars")
        
        if not prompt.strip():
            print("WARN: Prompt empty after sanitization")
            return "Generate comprehensive content."
        
        return prompt.strip()

    # langgraph_app/agents/writer.py
    # PATCH: Update your existing _generate_adaptive_content method
    # Replace the user_content building section with this enhanced version

    async def _generate_adaptive_content(self, state: Dict[str, Any]) -> str:
        """Generate adaptive content strictly from planner, researcher, and context (no fallbacks)."""

        template_config = state.get("template_config", {})
        style_config = state.get("style_config", {})

        self.validate_enterprise_config(template_config, style_config)

        try:
            template_id = state.get("template", "")
            context = self.analyze_context(state)

            # Extract parameters for real-time search
            params = state.get("dynamic_parameters", {})
            dynamic_overrides = params.get("dynamic_overrides", {})
            if isinstance(template_config, dict) and 'dynamic_overrides' in template_config:
                outer_overrides = template_config['dynamic_overrides']
                if isinstance(outer_overrides, dict) and 'dynamic_overrides' in outer_overrides:
                    dynamic_overrides = outer_overrides['dynamic_overrides']

            # REAL-TIME DATA INTEGRATION - ALWAYS REQUIRED IF TEMPLATE SPECIFIES
            real_time_context = await self._handle_real_time_requirements(
                template_config, context, dynamic_overrides
            )

            # Get system-level prompt from template
            template_specific_prompt = self.get_template_specific_prompt(template_config, template_id, state)
            if not template_specific_prompt or len(template_specific_prompt.strip()) < 10:
                raise RuntimeError("ENTERPRISE: Template prompt invalid or empty")

            # Build user content with mandatory real-time integration
            user_content = self._build_user_content_with_realtime(
                context, state, real_time_context
            )

            if len(user_content.strip()) < 10:
                raise RuntimeError("ENTERPRISE: User prompt invalid or empty")

            # Continue with existing generation logic...
            model_obj = get_model("writer")
            model_name = model_obj.model_name

            # Combine sanitized prompts
            system_content = self._sanitize_prompt(template_specific_prompt)
            user_content = self._sanitize_prompt(user_content)
            combined_input = f"{system_content}\n\n{user_content}"

            if len(combined_input.strip()) < 20:
                raise RuntimeError("ENTERPRISE: Combined prompt too short")

            # OpenAI call
            response = await asyncio.to_thread(
                self.client.responses.create,
                model=model_name,
                input=combined_input
            )

            content = self._extract_content_from_openai_response(response)

            if not content:
                raise RuntimeError("ENTERPRISE: OpenAI returned empty content")
            if len(content.strip()) < 100:
                raise RuntimeError(f"ENTERPRISE: OpenAI returned insufficient content ({len(content)} chars)")

            return content

        except Exception as e:
            raise RuntimeError(f"ENTERPRISE: Content generation pipeline failed: {e}")

    async def _handle_real_time_requirements(
        self, 
        template_config: Dict[str, Any], 
        context, 
        dynamic_overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle real-time data requirements - ENTERPRISE: NO FALLBACKS"""

        real_time_support = template_config.get('real_time_support', {})

        if real_time_support.get('enabled'):
            logger.info(f"Real-time data REQUIRED for template: {template_config.get('name')}")

            # ENTERPRISE: Validate search capability exists
            if not (self.researcher_agent or self.web_search_tool):
                raise RuntimeError("ENTERPRISE: Real-time data required but no search capability configured")

            # Extract search parameters
            search_timeframe = real_time_support.get('max_age_hours', 24)
            required_sources = real_time_support.get('verification_sources', 1)

            # Fetch recent data - will raise exception if fails
            recent_data = await self._fetch_recent_events(
                topic=context.topic,
                timeframe=f"{search_timeframe}h",
                min_sources=required_sources,
                parameters=dynamic_overrides
            )

            real_time_context = {
                'current_events': recent_data,
                'real_time_enabled': True,
                'data_freshness': datetime.utcnow().isoformat(),
                'search_timeframe': f"{search_timeframe} hours",
                'sources_found': len(set(recent_data.get('sources', []))),
                'events_found': len(recent_data.get('events', []))
            }

            logger.info(f"Real-time integration successful: {real_time_context['events_found']} events, {real_time_context['sources_found']} sources")
            return real_time_context

        else:
            # Template doesn't require real-time data
            return {
                'real_time_enabled': False,
                'knowledge_cutoff_warning': True,
                'cutoff_date': '2025-01-31'
            }

    def _build_user_content_with_realtime(
        self, 
        context, 
        state: Dict[str, Any], 
        real_time_context: Dict[str, Any]
    ) -> str:
        """Build user content with mandatory real-time integration when required"""

        # Extract planning output
        planning_output = getattr(state, "planning_output", None) or state.get("planning_output")
        planning_text = str(planning_output) if planning_output else ""

        # Build base content parts
        user_content_parts = [
            f"TOPIC: {context.topic}",
            f"AUDIENCE: {context.audience}",
            f"PLATFORM: {context.platform}",
            f"INTENT: {context.intent}",
            f"COMPLEXITY: {context.complexity_level}",
            planning_text
        ]

        # ENTERPRISE: Real-time integration - always include if enabled
        if real_time_context.get('real_time_enabled'):
            current_events = real_time_context.get('current_events', {})

            if not current_events or not current_events.get('events'):
                raise RuntimeError("ENTERPRISE: Real-time context enabled but no events data available")

            events_summary = self._summarize_events(current_events['events'])

            user_content_parts.extend([
                "",
                f"REAL-TIME DATA INTEGRATION (Current as of {real_time_context['data_freshness']}):",
                f"Search timeframe: {real_time_context['search_timeframe']}",
                f"Sources validated: {real_time_context['sources_found']}",
                f"Events found: {real_time_context['events_found']}",
                "",
                "CURRENT EVENTS:",
                events_summary,
                "",
                "CRITICAL: Integrate these recent developments throughout the content where relevant.",
                "Ensure all time-sensitive information is current and accurate."
            ])

        elif real_time_context.get('knowledge_cutoff_warning'):
            user_content_parts.extend([
                "",
                f"KNOWLEDGE CUTOFF: Content based on information available through {real_time_context['cutoff_date']}",
                "Do NOT reference events after this date."
            ])

        return "\n".join(user_content_parts)

    def _extract_content_from_openai_response(self, response) -> str:
        """ENTERPRISE: Extract content from new API format - NO FALLBACKS"""
        try:
            print("DEBUG: Starting content extraction...")
            print(f"DEBUG: Response type: {type(response)}")
            print(f"DEBUG: Response has output_text: {hasattr(response, 'output_text')}")

            if hasattr(response, 'output_text'):
                content = response.output_text
            else:
                # Try string conversion as fallback for unknown response structure
                content = str(response)

            print(f"DEBUG: Content type: {type(content)}")

            if content is None:
                raise RuntimeError("ENTERPRISE: API returned None content")

            if not isinstance(content, str):
                content = str(content)

            content = content.strip()
            print(f"DEBUG: Final content length: {len(content)}")

            if not content:
                raise RuntimeError("ENTERPRISE: API returned empty content after strip")

            print("DEBUG: Content extraction successful")
            return content

        except Exception as e:
            print(f"ERROR: Content extraction failed: {e}")
            raise RuntimeError(f"ENTERPRISE: Content extraction failed: {e}")

    # File: langgraph_app/agents/writer.py
    # Replace execute method

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Writer executes with available configs."""

        # Extract configs from state
        template_config = getattr(state, 'template_config', None)
        style_config = getattr(state, 'style_config', None)

        # STUDIO FIX: Reconstruct configs if missing
        if not template_config or not isinstance(template_config, dict) or not template_config:
            template_config = {
                'id': 'studio_writer_fallback',
                'template_type': 'strategic_brief',
                'name': 'Writer Fallback Template',
                'parameters': {},
                'structure': {},
                'research': {},
                'defaults': {},
                'distribution_channels': [],
                'generation_mode': 'standard',
                'platform': 'professional'
            }
            state.template_config = template_config
            logger.warning("WRITER: Created template_config fallback")

        if not style_config or not isinstance(style_config, dict) or not style_config:
            style_config = {
                'id': 'merger_acquisition',
                'name': 'Merger & Acquisition',
                'category': 'business_strategy',
                'platform': 'professional',
                'tone': 'professional',
                'voice': 'authoritative',
                'structure': 'executive_brief',
                'audience': 'corporate_development',
                'length_limit': 5000,
                'settings': {},
                'formatting': {},
                'system_prompt': 'Professional business analysis style'
            }
            state.style_config = style_config
            logger.warning("WRITER: Created style_config fallback")

        # FIXED: Validate extracted configs
        self.validate_enterprise_config(template_config, style_config)

        # Build state dict for generation
        state_dict = {
            "template": getattr(state, 'template_id', ''),
            "template_config": template_config,
            "style_config": style_config,
            "dynamic_parameters": getattr(state, 'dynamic_parameters', {}),
            "content_spec": getattr(state, 'content_spec', None)
        }

        logger.info(f"Writer calling _generate_adaptive_content with template: {state_dict.get('template')}")

        # CRITICAL FIX: Call the fixed method and handle content properly
        try:
            generated_content = asyncio.run(self._generate_adaptive_content(state_dict))

            if not generated_content:
                raise RuntimeError("ENTERPRISE: No content generated")

            if not isinstance(generated_content, str):
                generated_content = str(generated_content)

            final_content = self._sanitize_and_enforce(generated_content.strip(), min_paragraphs=4, max_bullets=6)

            if not final_content:
                raise RuntimeError("ENTERPRISE: Generated content is empty after strip()")

            if len(final_content) < 50:
                raise RuntimeError(f"ENTERPRISE: Generated content too short ({len(final_content)} chars)")

            # Set content fields
            state.content = final_content
            state.final_content = final_content
            state.draft_content = final_content

            logger.info(f"Writer completed: {len(final_content)} characters generated")
            return state

        except Exception as e:
            logger.error(f"Writer execution failed: {e}")
            raise RuntimeError(f"Writer execution failed: {e}")
    
    def _generate_prompt_from_config(self, template_config: Dict[str, Any], template_id: str) -> str:
        """Generate prompt dynamically from template configuration"""
        if not template_config:
            return ""
        
        purpose = template_config.get('purpose', 'Create high-quality content')
        template_type = template_config.get('template_type', template_id)
        target_audience = template_config.get('target_audience', 'general audience')
        tone_config = template_config.get('tone', {})
        content_requirements = template_config.get('content_requirements', [])
        section_order = template_config.get('section_order', [])
        instructions = template_config.get('instructions', '')
        
        # Build dynamic prompt
        prompt_parts = []
        
        # Header
        prompt_parts.append(f"You are a professional content writer specializing in {template_type.replace('_', ' ')}.")
        prompt_parts.append(f"PURPOSE: {purpose}")
        prompt_parts.append(f"TARGET AUDIENCE: {target_audience}")
        
        # Tone and style from config
        if tone_config:
            tone_parts = []
            if tone_config.get('formality'):
                tone_parts.append(f"Formality: {tone_config['formality']}")
            if tone_config.get('voice'):
                tone_parts.append(f"Voice: {tone_config['voice']}")
            if tone_config.get('persuasiveness'):
                tone_parts.append(f"Persuasiveness: {tone_config['persuasiveness']}")
            
            if tone_parts:
                prompt_parts.append(f"TONE AND STYLE: {', '.join(tone_parts)}")
        
        # Required sections from config
        if section_order:
            prompt_parts.append("REQUIRED SECTIONS (IN ORDER):")
            for i, section in enumerate(section_order, 1):
                prompt_parts.append(f"{i}. {section.replace('_', ' ').title()}")
        
        # Content requirements from config
        if content_requirements:
            prompt_parts.append("CONTENT REQUIREMENTS:")
            for req in content_requirements:
                prompt_parts.append(f"- {req}")
        
        # Template-specific instructions from config
        if instructions:
            prompt_parts.append("SPECIFIC INSTRUCTIONS:")
            prompt_parts.append(instructions)
        
        # Template enforcement
        prompt_parts.append(f"CRITICAL: Generate content specifically for {template_type}. Follow the exact requirements and structure specified above.")
        
        return "\n".join(prompt_parts)

    def _debug_openai_response(self, response) -> None:
        """
        ENTERPRISE: Safe response introspection for the new Responses API.
        Prints minimal structure without leaking tokens or content at scale.
        """
        try:
            # Basic shape checks
            rtype = type(response).__name__
            has_text = hasattr(response, "output_text")
            # Some SDKs expose 'id' / 'model' / 'usage' on the top-level object
            rid = getattr(response, "id", None)
            rmodel = getattr(response, "model", None)
            rusage = getattr(response, "usage", None)
    
            print(f"DEBUG: Response type={rtype} id={rid} model={rmodel} has_output_text={has_text}")
            if rusage:
                # Expect keys like input_tokens / output_tokens depending on SDK version
                print(f"DEBUG: Usage: {rusage}")
        except Exception as e:
            print(f"WARN: _debug_openai_response failed: {e}")

    def _sanitize_and_enforce(self, raw: str, *, min_paragraphs: int = 4, max_bullets: int = 6) -> str:
        """
        Enterprise: remove code blocks, collapse bullet sprawl, enforce paragraph-first output.
        Raises ValueError if constraints are not met after sanitation.
        """
        text = raw or ""
    
        # 1) Remove fenced code blocks and inline backticks
        text = re.sub(r"```.+?```", "", text, flags=re.S)
        text = re.sub(r"`[^`]+`", "", text)
    
        # 2) Limit bullets: convert excess bullets into sentences
        lines = text.splitlines()
        bullet_re = re.compile(r"^\s*[-•*]\s+")
        bullets = [i for i, ln in enumerate(lines) if bullet_re.match(ln)]
        if len(bullets) > max_bullets:
            for i in bullets[max_bullets:]:
                lines[i] = bullet_re.sub("", lines[i])
            text = "\n".join(lines)
    
        # 3) Normalize paragraphs: collapse multiple newlines, ensure min paragraphs
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
        if len(paragraphs) < min_paragraphs:
            raise ValueError(f"Writer output too sparse: {len(paragraphs)} paragraphs < {min_paragraphs}")
    
        return "\n\n".join(paragraphs)


    def _load_memory(self, filename: str) -> List[Dict]:
        file_path = self.memory_path / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return []
    
    def _save_memory(self, data: List[Dict], filename: str):
        file_path = self.memory_path / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)


# Export the universal template-aware agent
template_aware_writer_agent = TemplateAwareWriterAgent()

# Legacy compatibility wrapper
def _legacy_writer_fn(state: dict) -> dict:
    """Legacy wrapper for backward compatibility"""
    return template_aware_writer_agent.generate_adaptive_content(state)

# Exports
WriterAgent = TemplateAwareWriterAgent
writer = RunnableLambda(_legacy_writer_fn) 