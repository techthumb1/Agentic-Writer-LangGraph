# File: langgraph_app/agents/writer.py
import os
import re
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
    """Template-aware writer that respects template-specific formatting without interference"""

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
            from langgraph_app.style_profile_loader import get_dynamic_style_profile_loader
            style_loader = get_dynamic_style_profile_loader()

            profile = style_loader.get_profile(name)
            if not profile:
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
            from langgraph_app.template_loader import get_template_loader
            template_loader = get_template_loader()

            template_data = template_loader.get_template(template_id)
            if template_data:
                logger.info(f"✅ Loaded template config: {template_id}")
                return template_data

            available = template_loader.list_templates()
            logger.warning(f"Template '{template_id}' not found. Available: {available}")
            return {}

        except Exception as e:
            logger.error(f"Error loading template {template_id}: {e}")
            return {}

    def _validate_style_requirements(self, content: str, style_config: Dict) -> str:
        # Check forbidden patterns
        forbidden = style_config.get('forbidden_patterns', [])
        for pattern in forbidden:
            if pattern in content.lower():
                content = content.replace(pattern, "[professional alternative needed]")
        
        # Ensure required opening patterns
        required_openings = style_config.get('required_opening_patterns', [])
        if required_openings and not any(pattern in content for pattern in required_openings):
            content = f"{required_openings[0]}:\n\n{content}"
        
        return content

    def validate_enterprise_config(self, template_config, style_config):
        """Validate actual config objects passed as parameters"""
        if not template_config or not isinstance(template_config, dict):
            raise RuntimeError("ENTERPRISE: template_config required - no fallbacks")
        if not style_config or not isinstance(style_config, dict):
            raise RuntimeError("ENTERPRISE: style_config required - no fallbacks")

#    def build_from_template_schema(self, template_config: Dict, context: Dict) -> str:
#        """Build prompt from template's prompt_schema"""
#        
#        prompt_schema = template_config.get('prompt_schema')
#        if not prompt_schema:
#            raise ValueError("ENTERPRISE: Template missing prompt_schema")
#        
#        system_preamble = prompt_schema.get('system_preamble')
#        if not system_preamble:
#            raise ValueError("ENTERPRISE: Template missing system_preamble")
#        
#        content_template = prompt_schema.get('content_template')
#        if not content_template:
#            raise ValueError("ENTERPRISE: Template missing content_template")
#        
#        # Replace placeholders with actual values
#        placeholders = prompt_schema.get('placeholders', [])
#        final_prompt = system_preamble + "\n\n" + content_template
#        
#        for placeholder in placeholders:
#            value = context.get(placeholder, f"[{placeholder}]")
#            final_prompt = final_prompt.replace(f"{{{{{placeholder}}}}}", str(value))
#        
#        return final_prompt

    def build_from_template_schema(self, template_config: Dict, context: Dict) -> str:
        prompt_schema = template_config.get('prompt_schema')
        system_preamble = prompt_schema.get('system_preamble')
        content_template = prompt_schema.get('content_template')

        # Extract dynamic parameters for placeholders
        dynamic_params = template_config.get('dynamic_parameters', {})

        # Build context from multiple sources
        full_context = {
            'newsletter_type': dynamic_params.get('newsletter_type', 'weekly_roundup'),
            'subject_lines': 'Generate 3 subject line variants',
            'opening_section': 'Create engaging opening',
            'main_content': 'Develop core newsletter content',
            'cta_section': 'Include clear call-to-action',
            'closing_footer': 'Add professional closing',
            'performance_notes': 'Include optimization notes'
        }
        full_context.update(context)

        final_prompt = system_preamble + "\n\n" + content_template

        # Replace all placeholders
        for key, value in full_context.items():
            final_prompt = final_prompt.replace(f"{{{{{key}}}}}", str(value))

        return final_prompt

    def get_template_specific_prompt(self, template_config: Dict[str, Any], template_id: str, state: Dict = None) -> str:
        """Load template-specific prompt from prompts/writer/ directory"""
        
        # PRIORITY 1: Load from prompt files
        prompt_content = self._load_template_prompt_file(template_id, template_config)
        if prompt_content:
            print(f"Using template-specific prompt file for {template_id}")
            return prompt_content
        
        # PRIORITY 2: Use prompt_schema if available
        if template_config and template_config.get('prompt_schema'):
            print("Using template prompt_schema")
            context = self.extract_context_values(state) if state else {}
            return self.build_from_template_schema(template_config, context)
        
        # ENTERPRISE: Fail fast if no valid template found
        raise RuntimeError(f"ENTERPRISE: No template prompt found for {template_id}")
    
    def _load_template_prompt_file(self, template_id: str, template_config: Dict) -> str:
        """Load template-specific prompt from prompts/writer/ directory"""

        template_type = template_config.get('template_type', template_id)

        # Map both template_id and template_type to prompt files
        prompt_file_mapping = {
            'social_media_campaign': 'social_media_campaign_writer.txt',
            'email_newsletter': 'email_newsletter_writer.txt',
            'business_proposal': 'business_proposal_writer.txt',
            'api_documentation': 'enhanced_technical_doc_writer.txt',
            'blog_article_generator': 'blog_article_writer.txt',  # template_id
            'blog_article': 'blog_article_writer.txt',           # template_type
            'press_release': 'press_release_writer.txt',
            'technical_documentation': 'enhanced_technical_doc_writer.txt',
            'market_analysis': 'business_writer.txt',
            'strategic_brief': 'business_writer.txt',
            'data_driven_report': 'grad_level_writer.txt',
            'research_paper': 'grad_level_writer.txt',
        }

        # Try template_id first, then template_type
        prompt_filename = prompt_file_mapping.get(template_id) or prompt_file_mapping.get(template_type)
        if not prompt_filename:
            return None

        for prompt_path in self.prompt_paths:
            file_path = Path(prompt_path) / prompt_filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read().strip()
                except Exception as e:
                    print(f"Error loading prompt file {file_path}: {e}")
                    continue
                
        return None
    
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
    #    raise RuntimeError(f"ENTERPRISE: No valid template configuration for {template_id}")

    def extract_context_values(self, state: Dict) -> Dict:
        context = {
            "topic": state.get("topic", ""),
            "audience": state.get("audience", ""),
            "content_type": "content"
        }
        return context
    
    def analyze_context(self, state: Dict) -> WritingContext:
        """Extract and enrich context from state - simplified version"""
        params = state.get("dynamic_parameters", {})
        raw_template_config = state.get('template_config', {})
        template_config = safe_config_access(raw_template_config)

        # Extract topic from content_spec (set by planner)
        content_spec = state.get('content_spec')
        topic = None

        if content_spec and hasattr(content_spec, 'topic'):
            topic = content_spec.topic
        elif content_spec and isinstance(content_spec, dict) and 'topic' in content_spec:
            topic = content_spec['topic']

        # Try dynamic_overrides from template_config if no topic
        if not topic and isinstance(template_config, dict) and 'dynamic_overrides' in template_config:
            outer_overrides = template_config['dynamic_overrides']
            if isinstance(outer_overrides, dict) and 'dynamic_overrides' in outer_overrides:
                topic = outer_overrides['dynamic_overrides'].get("topic")
            elif isinstance(outer_overrides, dict):
                topic = outer_overrides.get("topic")

        # Final fallback
        if not topic:
            dynamic_overrides = params.get("dynamic_overrides", {})
            topic = dynamic_overrides.get("topic") if dynamic_overrides else None

        if not topic:
            raise ValueError("ENTERPRISE: Missing topic")

        # Extract audience
        audience = "general audience"
        if content_spec and hasattr(content_spec, 'audience'):
            audience = content_spec.audience
        elif content_spec and isinstance(content_spec, dict) and 'audience' in content_spec:
            audience = content_spec['audience']

        return WritingContext(
            topic=topic,
            audience=audience,
            platform=state.get("platform", "web"),
            intent="inform",
            complexity_level=5,
            innovation_preference=AdaptiveLevel.BALANCED
        )

    def has_mcp_research(self, state: Dict) -> bool:
        """Check if MCP research data is available"""
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
        """Extract and consolidate MCP research data from state"""
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
    
    async def _fetch_recent_events(self, topic: str, timeframe: str, min_sources: int, parameters: Dict) -> Dict[str, Any]:
        """Fetch recent events for real-time integration"""
        try:
            if self.web_search_tool:
                results = await self.web_search_tool.search(f"{topic} recent developments {timeframe}")
                return {
                    'events': results.get('results', [])[:5],
                    'sources': [r.get('source', 'Unknown') for r in results.get('results', [])]
                }
            else:
                # Return empty but valid structure
                return {'events': [], 'sources': []}
        except Exception as e:
            print(f"Real-time fetch failed: {e}")
            return {'events': [], 'sources': []}

    def _summarize_events(self, events: List[Dict]) -> str:
        """Summarize events for real-time integration"""
        if not events:
            return "No recent events found."

        summary_parts = []
        for event in events[:3]:
            title = event.get('title', 'Recent development')
            summary_parts.append(f"- {title}")

        return "\n".join(summary_parts)

    # File: langgraph_app/agents/writer.py
    # FIX: Revert to working OpenAI API pattern from writer.copy.py

    async def _generate_adaptive_content(self, state: Dict[str, Any]) -> str:
        """Generate adaptive content - FIXED: Use working OpenAI API pattern"""

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

            # Check if template requires code generation
            requires_code = template_config.get("code_agent", False)
            if not requires_code:
                # Skip code-related processing for non-code templates
                user_content = user_content.replace("code examples", "practical examples")
                template_specific_prompt = template_specific_prompt.replace("code blocks", "content blocks")

            if len(user_content.strip()) < 10:
                raise RuntimeError("ENTERPRISE: User prompt invalid or empty")

            # Get dynamic generation settings
            generation_settings = self._get_user_generation_settings(state)

            # Continue with existing generation logic...
            model_obj = get_model("writer")
            model_name = model_obj.model_name

            # Combine sanitized prompts (SAME AS WORKING VERSION)
            system_content = self._sanitize_prompt(template_specific_prompt)
            user_content = self._sanitize_prompt(user_content)
            combined_input = f"{system_content}\n\n{user_content}"

            if len(system_content + user_content) < 20:
                raise RuntimeError("ENTERPRISE: Combined prompt too short")

            # CRITICAL FIX: Use working OpenAI API pattern from writer.copy.py
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

    def _extract_content_from_openai_response(self, response) -> str:
        """Extract content from responses.create() API - same as working version"""
        try:
            print("DEBUG: Starting content extraction...")
            print(f"DEBUG: Response type: {type(response)}")
            print(f"DEBUG: Response has output_text: {hasattr(response, 'output_text')}")

            if hasattr(response, 'output_text'):
                content = response.output_text
            elif hasattr(response, 'choices') and response.choices:
                # Fallback for chat.completions format
                content = response.choices[0].message.content
            else:
                # Try string conversion as fallback
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
    
    def _get_user_generation_settings(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user's saved generation settings"""

        defaults = {'max_tokens': 4000}

        settings_sources = [
            state.get('user_settings', {}),
            state.get('generation_settings', {}),
            getattr(state.get('content_spec'), 'generation_settings', {}),
            state.get('dynamic_parameters', {}).get('generation_settings', {})
        ]

        for settings in settings_sources:
            if isinstance(settings, dict) and 'max_tokens' in settings:
                defaults['max_tokens'] = max(100, min(int(settings['max_tokens']), 8000))
                break
            
        return defaults

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


# File: langgraph_app/agents/writer.py
# FIXED: Strengthened sanitization method to properly remove code blocks

    def user_provided_code(self, state: Dict) -> str:
        """Extract user-provided code from dynamic overrides"""
        params = state.get("dynamic_parameters", {})
        dynamic_overrides = params.get("dynamic_overrides", {}) if params else {}
        return dynamic_overrides.get("code_input", "") if dynamic_overrides else ""

# File: langgraph_app/agents/writer.py
    # Enterprise template sanitization with dynamic code handling

# File: langgraph_app/agents/writer.py
# Enterprise template sanitization with dynamic code handling

    def _sanitize_and_enforce(self, raw: str, template_config: Dict = None, state: Dict = None) -> str:
        """Enterprise template sanitization with dynamic code inclusion logic"""
        text = raw or ""

        if not template_config:
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            return text

        # Extract configuration
        output_policy = template_config.get('output_policy', {})
        template_behavior = template_config.get('template_behavior', {})
        template_type = template_config.get('template_type', '')

        # Extract user preferences and code input
        dynamic_params = state.get("dynamic_parameters", {}) if state else {}
        dynamic_overrides = dynamic_params.get("dynamic_overrides", {})
        user_wants_code = dynamic_overrides.get("include_code_examples", False)
        user_provided_code = dynamic_overrides.get("code_input", "")

        # ENTERPRISE: Remove all code blocks until code agent feature is implemented
        should_remove_code = True

        if should_remove_code:
            # AGGRESSIVE: Remove all code blocks and technical artifacts

            # Remove all code fence variations
            text = re.sub(r"```[\s\S]*?```", "", text, flags=re.DOTALL)
            text = re.sub(r"```\w*[\s\S]*?```", "", text, flags=re.DOTALL)

            # Remove inline code and backticks
            text = re.sub(r"`[^`\n]*`", "", text)
            text = text.replace("`", "")

            # Remove HTML formatting artifacts
            text = re.sub(r"</?[^>]+>", "", text)

            # Remove broken code patterns that appear mid-text
            text = re.sub(r"```\w*\s*\n?", "", text)  # Opening fences
            text = re.sub(r"\n?```\s*", "", text)     # Closing fences

            # Remove standalone code lines
            text = re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE)  # JS comments
            text = re.sub(r"^\s*#.*$", "", text, flags=re.MULTILINE)   # YAML comments
            text = re.sub(r"^\s*function\s+\w+.*$", "", text, flags=re.MULTILINE)  # Function declarations
            text = re.sub(r"^\s*class\s+\w+.*$", "", text, flags=re.MULTILINE)     # Class declarations
            text = re.sub(r"^\s*\w+:.*$", "", text, flags=re.MULTILINE)           # YAML key-value pairs

            # Remove documentation artifacts
            text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
            text = re.sub(r"\n#+\s+", "\n", text)

            # Remove technical implementation patterns
            technical_patterns = [
                r"\[Technical\s+Implementation\]",
                r"\[Code\s+Example\]", 
                r"\[Configuration\]",
                r"Implementation\s+Details:",
                r"Code\s+Structure:",
                r"Setup\s+Instructions:",
                r"Installation\s+Steps:",
                r"API\s+Reference:"
            ]

            for pattern in technical_patterns:
                text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # Normalize whitespace
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        # Template-specific validation
        if template_type == 'social_media_campaign':
            return "\n\n".join(paragraphs)

        # Standard content validation
        min_paragraphs = output_policy.get('min_paragraphs', 2)
        if len(paragraphs) < min_paragraphs:
            logger.warning(f"Content has {len(paragraphs)} paragraphs, minimum {min_paragraphs} expected")

        return "\n\n".join(paragraphs)

    def _build_user_content_with_realtime(
        self, 
        context, 
        state: Dict[str, Any], 
        real_time_context: Dict[str, Any]
    ) -> str:
        """Build user content with template-specific instructions"""

        # Extract template config to customize instructions
        template_config = state.get("template_config", {})
        template_type = template_config.get('template_type', '')

        # Build base content parts
        user_content_parts = [
            f"TOPIC: {context.topic}",
            f"AUDIENCE: {context.audience}",
            f"PLATFORM: {context.platform}",
            f"INTENT: {context.intent}",
            f"COMPLEXITY: {context.complexity_level}"
        ]

        # CRITICAL: Template-specific content instructions
        if template_type == 'social_media_campaign':
            user_content_parts.extend([
                "",
                "CRITICAL SOCIAL MEDIA REQUIREMENTS:",
                "- Generate INDIVIDUAL social media posts, NOT documentation",
                "- Each post must have: Caption, Hashtags, CTA, Platform",
                "- Format: POST 1: Caption: [text] Hashtags: [tags] CTA: [action] Platform: [platform]",
                "- NO code blocks, NO technical guides, NO documentation format",
                "- Ready-to-publish content that users can copy/paste directly",
                f"- Generate {template_config.get('parameters', {}).get('post_count', {}).get('default', 8)} individual posts"
            ])

        # Add planning context if available
        planning_output = getattr(state, "planning_output", None) or state.get("planning_output")
        if planning_output:
            user_content_parts.append(f"\nPLANNING CONTEXT: {str(planning_output)}")

        # Real-time integration (your existing logic)
        if real_time_context.get('real_time_enabled'):
            current_events = real_time_context.get('current_events', {})
            if current_events and current_events.get('events'):
                events_summary = self._summarize_events(current_events['events'])
                user_content_parts.extend([
                    "",
                    f"REAL-TIME DATA (Current as of {real_time_context['data_freshness']}):",
                    events_summary,
                    "CRITICAL: Integrate these recent developments into the content where relevant."
                ])

        return "\n".join(user_content_parts)

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Writer executes with template-specific generation - no format overrides"""

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

        # Validate extracted configs
        self.validate_enterprise_config(template_config, style_config)

        # Extract template ID with fallback
        template_id = (
            getattr(state, 'template_id', '') or 
            template_config.get('slug', '') or 
            template_config.get('id', '') or
            'unknown'
        )

        # Build state dict for generation
        state_dict = {
            "template": template_id,
            "template_config": template_config,
            "style_config": style_config,
            "dynamic_parameters": getattr(state, 'dynamic_parameters', {}),
            "content_spec": getattr(state, 'content_spec', None)
        }

        logger.info(f"Writer calling _generate_adaptive_content with template: {state_dict.get('template')}")

        try:
            generated_content = asyncio.run(self._generate_adaptive_content(state_dict))

            if not generated_content:
                raise RuntimeError("ENTERPRISE: No content generated")

            if not isinstance(generated_content, str):
                generated_content = str(generated_content)

            # MINIMAL sanitization - only remove code blocks, preserve template format
            final_content = self._sanitize_and_enforce(
                generated_content.strip(), 
                template_config=template_config,
                state=state_dict
            )

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

    def _generate_prompt_from_config(self, template_config, template_id):
        # Use template's actual prompt_schema if available
        prompt_schema = template_config.get('prompt_schema', {})
        if prompt_schema.get('system_preamble'):
            return prompt_schema['system_preamble']

        # Simple fallback
        return f"Generate {template_config.get('template_type', 'content')} as specified."
        
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

    def _summarize_events(self, events: List[Dict]) -> str:
        """Summarize events for real-time integration"""
        if not events:
            return "No recent events found."
        
        summary_parts = []
        for event in events[:3]:  # Top 3 events
            title = event.get('title', 'Untitled Event')
            date = event.get('date', 'Recent')
            source = event.get('source', 'Unknown')
            summary_parts.append(f"- {title} ({date}, {source})")
        
        return "\n".join(summary_parts)

    def _build_research_integrated_prompt(self, template_config: Dict, template_id: str, state: Dict) -> str:
        """Build prompt with MCP research integration"""
        research_data = self.extract_mcp_research_data(state)
        
        base_prompt = self._generate_prompt_from_config(template_config, template_id)
        
        # Add research context
        if research_data['raw_findings']:
            research_context = "\n".join([f"Research: {k}: {v}" for k, v in research_data['raw_findings'].items()])
            return f"{base_prompt}\n\nResearch Context:\n{research_context}"
        
        return base_prompt

# Export the universal template-aware agent
template_aware_writer_agent = TemplateAwareWriterAgent()

# Legacy compatibility wrapper
def _legacy_writer_fn(state: dict) -> dict:
    """Legacy wrapper for backward compatibility"""
    return template_aware_writer_agent.generate_adaptive_content(state)

# Exports
WriterAgent = TemplateAwareWriterAgent
writer = RunnableLambda(_legacy_writer_fn)