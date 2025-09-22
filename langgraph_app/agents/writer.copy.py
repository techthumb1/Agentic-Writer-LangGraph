# File: langgraph_app/agents/writer.py
from multiprocessing import context
import os
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

from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from langgraph_app.enhanced_model_registry import get_model
from langgraph_app.core.enriched_content_state import EnrichedContentState
from langchain_core.messages import SystemMessage, HumanMessage
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

class TemplateAwareWriterAgent:
    """FIXED: Universal Configuration-Driven Writer Agent - NO HARDCODED TEMPLATES"""

    def __init__(self):
        """Initialize TemplateAwareWriterAgent with required clients and paths"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable required")
        self.client = OpenAI(api_key=api_key)

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

    def extract_context_values(self, state: Dict) -> Dict:
        context = {
            "topic": state.get("topic", ""),
            "audience": state.get("audience", ""),
            "content_type": "content"
        }
        return context

    def analyze_context(self, state: Dict) -> WritingContext:
        """Extract and enrich context from state - FIXED nested topic extraction"""
        params = state.get("dynamic_parameters", {})
        raw_template_config = state.get('template_config', {})
        template_config = safe_config_access(raw_template_config)
    
        # CRITICAL FIX: Handle nested dynamic_overrides structure
        # The logs show: template_config['dynamic_overrides']['dynamic_overrides']['topic']
        dynamic_overrides = None
        
        # Try template_config.dynamic_overrides.dynamic_overrides first (nested structure)
        if isinstance(template_config, dict) and 'dynamic_overrides' in template_config:
            outer_overrides = template_config['dynamic_overrides']
            if isinstance(outer_overrides, dict) and 'dynamic_overrides' in outer_overrides:
                dynamic_overrides = outer_overrides['dynamic_overrides']
                print(f"DEBUG: Found nested dynamic_overrides with keys: {list(dynamic_overrides.keys())}")
            else:
                dynamic_overrides = outer_overrides
                print(f"DEBUG: Found single-level dynamic_overrides with keys: {list(dynamic_overrides.keys())}")
        
        # Fallback to params.dynamic_overrides
        if not dynamic_overrides:
            dynamic_overrides = params.get("dynamic_overrides", {})
            print(f"DEBUG: Using params dynamic_overrides with keys: {list(dynamic_overrides.keys())}")
        
        # Extract topic from the dynamic_overrides
        topic = dynamic_overrides.get("topic") if dynamic_overrides else None
        
        if not topic:
            raise ValueError(f"ENTERPRISE: Missing topic. Available in dynamic_overrides: {list(dynamic_overrides.keys()) if dynamic_overrides else 'None'}")
        
        print(f"DEBUG: Successfully extracted topic: {topic}")

        # Extract audience
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

    def _create_enhanced_prompt(self, context: WritingContext, template_config: Dict[str, Any], state: Dict) -> str:
        """UNIVERSAL: Create comprehensive writing prompt with LONGFORM requirements - REMOVED VALIDATION"""
        if hasattr(template_config, '__dict__') and not hasattr(template_config, 'get'):
            template_config = vars(template_config)
        if not template_config:
            template_config = self._extract_guaranteed_template_config(state)

        planning = state.get('planning_output')
        if planning and hasattr(planning, '__dict__') and not hasattr(planning, 'get'):
            planning = vars(planning)
        state['planning_output'] = planning

        # FIXED: Extract generation settings for comprehensive length control
        gen_settings = state.get("generation_settings", {})
        max_tokens = gen_settings.get("maxTokens", 4000)
        target_words = min(max_tokens * 0.75, 4000)

        # Calculate comprehensive section requirements
        if max_tokens >= 3500:
            min_section_words = 500
            total_min_words = int(target_words)
            depth_requirement = "exhaustive detail with comprehensive examples"
        elif max_tokens >= 2500:
            min_section_words = 400
            total_min_words = int(target_words)
            depth_requirement = "detailed analysis with extensive examples"
        elif max_tokens >= 1500:
            min_section_words = 300
            total_min_words = int(target_words)
            depth_requirement = "substantial coverage with specific examples"
        else:
            min_section_words = 250
            total_min_words = int(target_words)
            depth_requirement = "comprehensive coverage with examples"

        section_order = template_config.get('section_order', [])
        tone_config = template_config.get('tone', {})

        prompt_parts = []

        # 1. COMPREHENSIVE STRUCTURE SECTION
        if section_order:
            prompt_parts.append("**REQUIRED SECTIONS (COMPREHENSIVE LONGFORM STRUCTURE):**")
            prompt_parts.append("\n".join([f"## {section} (MINIMUM {min_section_words} WORDS)" for section in section_order]))
        elif planning and hasattr(planning, 'estimated_sections'):
            sections = [section.get('name', f'Section {i+1}') for i, section in enumerate(planning.estimated_sections)]
            prompt_parts.append("**REQUIRED SECTIONS (COMPREHENSIVE LONGFORM STRUCTURE):**")
            prompt_parts.append("\n".join([f"## {section} (MINIMUM {min_section_words} WORDS)" for section in sections]))
        else:
            dynamic_sections = self._generate_universal_sections(context, template_config)
            prompt_parts.append("**REQUIRED SECTIONS (COMPREHENSIVE LONGFORM STRUCTURE):**")
            prompt_parts.append("\n".join([f"## {section} (MINIMUM {min_section_words} WORDS)" for section in dynamic_sections]))

        # 2. COMPREHENSIVE REQUIREMENTS SECTION
        requirements = [
            f"- ABSOLUTE MINIMUM {total_min_words} words total across all sections",
            f"- Each section must be minimum {min_section_words} words with {depth_requirement}",
            "- NO brief summaries, overviews, or placeholder content",
            "- Every section must be fully developed with actionable insights",
            "- Use extensive examples, case studies, and detailed explanations"
        ]

        template_requirements = template_config.get('content_requirements', [])
        if template_requirements:
            requirements.extend([f"- {req}" for req in template_requirements])
        else:
            dynamic_requirements = self._generate_universal_requirements(context, template_config)
            requirements.extend(dynamic_requirements)

        # Add comprehensive-specific requirements
        requirements.extend([
            "- Provide step-by-step processes and implementation details where applicable",
            "- Include specific data, metrics, and supporting evidence throughout",
            "- Write as a subject matter expert with comprehensive knowledge",
            f"- Transform the topic into the most valuable, detailed content possible for {context.audience}"
        ])

        prompt_parts.append("**COMPREHENSIVE CONTENT REQUIREMENTS:**")
        prompt_parts.append("\n".join(requirements))

        # 3. TONE SECTION
        tone_guidance = self._generate_universal_tone_guidance(context, template_config, tone_config)
        prompt_parts.append(f"**TONE AND STYLE:** {tone_guidance}")

        # 4. CONTEXT SECTION
        prompt_parts.extend([
            f"**TOPIC:** {context.topic}",
            f"**AUDIENCE:** {context.audience}",
            f"**COMPLEXITY LEVEL:** {context.complexity_level}/10",
            f"**TARGET LENGTH:** {total_min_words}+ words ({min_section_words}+ words per section)"
        ])

        # 5. COMPREHENSIVE FINAL INSTRUCTION
        final_instruction = f"""**COMPREHENSIVE GENERATION MANDATE:**
    Generate expert-level comprehensive content about {context.topic} that provides maximum value for {context.audience}.
    - MINIMUM {total_min_words} words with detailed coverage throughout
    - Each section must be fully developed with extensive detail and examples
    - NO shortcuts, summaries, or brief treatments - provide exhaustive coverage
    - Write as the definitive expert resource on {context.topic}
    - Every paragraph must add substantial value and actionable insights"""

        prompt_parts.append(final_instruction)

        return "\n".join(prompt_parts)

    def _generate_universal_sections(self, context: WritingContext, template_config: Dict[str, Any]) -> List[str]:
        sections = [f"{context.topic} Overview"]
        topic_analysis = self._analyze_topic_characteristics(context.topic, context.audience)
        
        if topic_analysis['is_business_focused']:
            sections.extend(["Strategic Analysis", "Market Considerations", "Implementation Approach", "Success Metrics", "Next Steps"])
        elif topic_analysis['is_technical']:
            sections.extend(["Technical Foundation", "Implementation Guide", "Best Practices", "Practical Examples", "Troubleshooting"])
        else:
            sections.extend([f"Understanding {context.topic}", "Key Principles", "Practical Applications", "Implementation Considerations", "Future Outlook"])
        
        sections.append("Key Takeaways")
        return sections

    def _generate_universal_requirements(self, context: WritingContext, template_config: Dict[str, Any]) -> List[str]:
        requirements = []
        topic_analysis = self._analyze_topic_characteristics(context.topic, context.audience)

        if topic_analysis['is_business_focused']:
            requirements.extend([
                "- Include comprehensive data analysis, detailed metrics, and complete business case with ROI calculations",
                "- Provide extensive strategic recommendations with step-by-step implementation roadmaps"
            ])
        elif topic_analysis['is_technical']:
            requirements.extend([
                "- Provide comprehensive, implementable technical guidance with detailed architecture explanations",
                "- Include extensive working examples, complete code samples, and detailed configuration guides"
            ])
        else:
            requirements.extend([
                "- Provide comprehensive, original insights backed by detailed research and analysis",
                "- Include extensive specific examples, detailed case studies, and thorough comparative analysis"
            ])

        requirements.extend([
            "- Use detailed, engaging writing style with comprehensive explanations throughout",
            "- Maintain logical structure with smooth transitions and comprehensive flow between sections"
        ])

        return requirements

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

    def _generate_adaptive_content(self, state: Dict[str, Any]) -> str:
        """Generate adaptive content with enterprise fail-fast behavior."""

        # Extract configs
        template_config = state.get('template_config', {})
        style_config = state.get('style_config', {})

        print(f"DEBUG: template_config type: {type(template_config)}")
        print(f"DEBUG: template_config exists: {bool(template_config)}")
        print(f"DEBUG: style_config type: {type(style_config)}")
        print(f"DEBUG: style_config exists: {bool(style_config)}")

        # FIXED: Validate the extracted configs
        self.validate_enterprise_config(template_config, style_config)

        try:
            template_id = state.get("template", "")

            context = self.analyze_context(state)

            # DIAGNOSTIC: Check prompt generation
            try:
                template_specific_prompt = self.get_template_specific_prompt(template_config, template_id, state)
                print(f"DEBUG: System prompt length: {len(template_specific_prompt)}")
                print(f"DEBUG: System prompt preview: {template_specific_prompt[:200]}...")
            except Exception as prompt_error:
                print(f"ERROR: Template prompt generation failed: {prompt_error}")
                raise RuntimeError(f"ENTERPRISE: Template prompt generation failed: {prompt_error}")

            try:
                user_prompt = self._create_enhanced_prompt(context, template_config, state)
                print(f"DEBUG: User prompt length: {len(user_prompt)}")
                print(f"DEBUG: User prompt preview: {user_prompt[:200]}...")
            except Exception as user_prompt_error:
                print(f"ERROR: User prompt generation failed: {user_prompt_error}")
                raise RuntimeError(f"ENTERPRISE: User prompt generation failed: {user_prompt_error}")

            # Get model name
            model_obj = get_model("writer")
            model_name = model_obj.model_name
            print(f"DEBUG: Using model: {model_name}")

            # CRITICAL FIX: Ensure prompts are valid before API call
            system_content = self._sanitize_prompt(template_specific_prompt)
            user_content = self._sanitize_prompt(user_prompt)

            combined_input = f"{system_content}\n\n{user_content}"

            if not system_content or len(system_content.strip()) < 10:
                raise RuntimeError("ENTERPRISE: System prompt invalid or too short")

            if not user_content or len(user_content.strip()) < 10:
                raise RuntimeError("ENTERPRISE: User prompt invalid or too short")

            print(f"DEBUG: Final system prompt length: {len(system_content)}")
            print(f"DEBUG: Final user prompt length: {len(user_content)}")

            # ENTERPRISE: Minimal OpenAI call with fail-fast behavior
            try:
                print("DEBUG: Making OpenAI API call...")

                response = self.client.responses.create(
                    model=model_name,
                    input=combined_input 
                )

                print(f"DEBUG: OpenAI response received")
                self._debug_openai_response(response)

                # ENTERPRISE: Extract content with fail-fast
                content = self._extract_content_from_openai_response(response)

                # ENTERPRISE: Fail fast if no content - NO FALLBACKS
                if not content:
                    raise RuntimeError("ENTERPRISE: OpenAI returned empty content - template/topic mismatch likely")

                if len(content.strip()) < 100:
                    raise RuntimeError(f"ENTERPRISE: OpenAI returned insufficient content ({len(content)} chars) - check prompts")

                return content

            except Exception as openai_error:
                print(f"ERROR: OpenAI API call failed: {openai_error}")
                raise RuntimeError(f"ENTERPRISE: OpenAI generation failed: {openai_error}")

        except Exception as e:
            print(f"ERROR: Content generation pipeline failed: {e}")
            raise e


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

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Writer executes with available configs."""

        # Extract configs from state
        template_config = getattr(state, 'template_config', None)
        style_config = getattr(state, 'style_config', None)

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
            generated_content = self._generate_adaptive_content(state_dict)

            if not generated_content:
                raise RuntimeError("ENTERPRISE: No content generated")

            if not isinstance(generated_content, str):
                generated_content = str(generated_content)

            final_content = generated_content.strip()

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

    def generate_adaptive_content(self, state: Dict) -> Dict:
        """UNIVERSAL: Template-aware content generation - REMOVED VALIDATION"""
        template_id = state.get("template", "")
        print(f"🚀 Generating content for template: {template_id}")

        template_config = state.get("template_config", {})
        # After: template_config = state.get("template_config", {})
        if hasattr(template_config, '__dict__') and not hasattr(template_config, 'get'):
            template_config = vars(template_config)
            state["template_config"] = template_config  # Update state too
        template_name = ""
        if isinstance(template_config, dict):
            template_name = template_config.get('name', template_config.get('id', template_id))
        elif template_id:
            template_name = template_id

        print(f"🚀 Generating content for template: {template_name}")

        if not template_config and template_id:
            template_config = self.load_template_config(template_id)
        if not template_config:
            template_config = self._extract_guaranteed_template_config(state)
        state["template_config"] = template_config

        context = self.analyze_context(state)

        style_profile_input = state.get("style_profile", state.get("style_config", {}).get("id", "default"))
        if isinstance(style_profile_input, str):
            style = self.load_style_profile(style_profile_input)
        else:
            style = style_profile_input

        template_specific_prompt = self.get_template_specific_prompt(template_config, template_id, state)

        # FIX: Remove the extra 'style' argument - method only takes 4 params
        user_prompt = self._create_enhanced_prompt(context, template_config, state)

        template_enforcement = ""
        if template_id and template_config:
            template_type = template_config.get('template_type', template_id)
            template_enforcement = f"""
            CRITICAL TEMPLATE ENFORCEMENT:
            You are generating content for template: {template_id} (type: {template_type})
            You MUST follow the exact structure and format specified in the user prompt.
            This is content specifically for {template_type} - follow the requirements exactly.
            """

        final_system_prompt = template_enforcement + "\n\n" + template_specific_prompt

        from langgraph_app.enhanced_model_registry import get_model_for_generation

        gen_settings = state.get("generation_settings", {})
        gen_mode = state.get("generation_mode", "")
        dynamic_overrides = state.get("dynamic_parameters", {}).get("dynamic_overrides", {})
        max_tokens = self.calculate_required_tokens(template_config, dynamic_overrides)

        # Get model name string (not object)
        model_obj = get_model("writer")
        model_name = model_obj.model_name

        logger.info(f"[Writer] Using model dynamically selected: {model_name}")

        # FIXED: Extract generation settings for comprehensive length control
        max_tokens = gen_settings.get("maxTokens", 4000)
        temperature = gen_settings.get("temperature", 0.7)

        system_content = self._sanitize_prompt(final_system_prompt)
        user_content = self._sanitize_prompt(user_prompt)


        combined_input = f"{system_content}\n\n{user_content}"

        # Calculate expected word count for logging
        expected_words = min(max_tokens * 0.75, 4000)

        print(f"Using model: {model_name}")
        print(f"Template type: {template_config.get('template_type', 'universal')}")
        print(f"Generation settings: maxTokens={max_tokens}, temperature={temperature}")
        print(f"Target word count: ~{int(expected_words)} words")

        # Combine system and user prompts for the new API format

        response = self.client.responses.create(
            model=model_name,
            input=combined_input
        )

        generated_content = response.choices[0].message.content.strip()
        actual_words = len(generated_content.split())

        # Enhanced logging for length analysis
        length_ratio = actual_words / expected_words if expected_words > 0 else 0
        length_status = "✅ LONGFORM" if actual_words >= 2000 else "⚠️ SHORT" if actual_words >= 1000 else "❌ TOO SHORT"

        print(f"{length_status} Generated {actual_words} words (target: {int(expected_words)}, ratio: {length_ratio:.2f})")

        if actual_words < expected_words * 0.5:
            print(f"🚨 WARNING: Content significantly shorter than expected. Check prompt construction.")

        metadata = {
            "template_id": template_id,
            "template_type": template_config.get('template_type', 'universal'),
            "topic": context.topic,
            "audience": context.audience,
            "platform": context.platform,
            "intent": context.intent,
            "complexity_level": context.complexity_level,
            "generation_timestamp": datetime.now().isoformat(),
            "word_count": actual_words,
            "target_word_count": int(expected_words),
            "length_ratio": length_ratio,
            "max_tokens_used": max_tokens,
            "temperature_used": temperature,
            "model_used": model_name,
            "template_config_loaded": bool(template_config),
            "generation_settings_applied": bool(gen_settings)
        }

        print(f"✅ Generated {actual_words} words for {template_id}")

        # Content originality checking removed
        return {
            **state, 
            "draft": generated_content,
            "metadata": metadata,
            "template_config": template_config,
        }
    
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