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
    mode: WritingMode
    structure_pattern: str
    tone_adaptation: Dict[str, float]
    experimental_techniques: List[str]
    confidence_threshold: float = 0.7

def safe_config_access(config):
    if isinstance(config, str):
        try:
            return json.loads(config)
        except:
            return {}
    elif isinstance(config, dict):
        return config
    elif hasattr(config, '__dict__'):
        return vars(config)
    else:
        return {}

class TemplateAwareWriterAgent(RealTimeSearchMixin):
    """Template-aware writer that respects template-specific formatting without interference"""

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable required")
        
        self.client = OpenAI(api_key=api_key)
        self.researcher_agent = None  # Will be set by MCP graph
        self.web_search_tool = None   # Will be set by MCP graph
        self.max_real_time_age_hours = 72

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
        forbidden = style_config.get('forbidden_patterns', [])
        for pattern in forbidden:
            if pattern in content.lower():
                content = content.replace(pattern, "[professional alternative needed]")
        required_openings = style_config.get('required_opening_patterns', [])
        if required_openings and not any(pattern in content for pattern in required_openings):
            content = f"{required_openings[0]}:\n\n{content}"
        return content

    def validate_enterprise_config(self, template_config, style_config):
        if not template_config or not isinstance(template_config, dict):
            raise RuntimeError("ENTERPRISE: template_config required - no fallbacks")
        if not style_config or not isinstance(style_config, dict):
            raise RuntimeError("ENTERPRISE: style_config required - no fallbacks")

    def build_from_template_schema(self, template_config: Dict, context: Dict) -> str:
        prompt_schema = template_config.get('prompt_schema')
        system_preamble = prompt_schema.get('system_preamble')
        content_template = prompt_schema.get('content_template')
        dynamic_params = template_config.get('dynamic_parameters', {})
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
        for key, value in full_context.items():
            final_prompt = final_prompt.replace(f"{{{{{key}}}}}", str(value))
        return final_prompt

    def _load_template_prompt_file(self, template_id: str, template_config: Dict) -> str:
        template_type = template_config.get('template_type', template_id)
        template_slug = template_config.get('slug', template_id)

        print(f"🔍 Debug prompt loading:")
        print(f"  template_id='{template_id}'")
        print(f"  template_type='{template_type}'")
        print(f"  template_slug='{template_slug}'")

        prompt_file_mapping = {
            'blog_article_generator': 'blog_article_writer.txt',
            'blog_article': 'blog_article_writer.txt',
            'social_media_campaign': 'social_media_campaign_writer.txt',
            'email_newsletter': 'email_newsletter_writer.txt',
            'business_proposal': 'business_proposal_writer.txt',
            'api_documentation_template': 'api_documentation_template_writer.txt',
            'api_documentation': 'api_documentation_template_writer.txt',
            'data_driven_template': 'data_driven_template_writer.txt',
            'data_driven_report': 'data_driven_template_writer.txt',
            'market_analysis_template': 'market_analysis_writer.txt',
            'market_analysis': 'market_analysis_template_writer.txt',
            'strategic_brief_template': 'strategic_brief_writer.txt',
            'technical_documentation': 'technical_documentation_writer.txt',
            'press_release': 'press_release_writer.txt',
            'research_paper_template': 'grad_level_writer.txt',
            'research_paper': 'grad_level_writer.txt',
        }

        prompt_filename = None
        for identifier in [template_slug, template_id, template_type]:
            pf = prompt_file_mapping.get(identifier)
            if pf:
                print(f"📄 Mapped '{identifier}' to filename: {pf}")
                prompt_filename = pf
                break
            
        if not prompt_filename:
            print(f"❌ No mapping found for any identifier")
            return None

        for prompt_path in self.prompt_paths:
            file_path = Path(prompt_path) / prompt_filename
            print(f"🔍 Checking path: {file_path}")
            print(f"   Exists: {file_path.exists()}")

            if file_path.exists():
                print(f"✅ Found prompt file: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    print(f"📖 Loaded {len(content)} characters from prompt file")
                    return content
                except Exception as e:
                    print(f"❌ Error loading prompt file {file_path}: {e}")
                    continue
                
        print(f"❌ Prompt file '{prompt_filename}' not found in any path")
        return None

    def get_template_specific_prompt(self, template_config: Dict[str, Any], template_id: str, state: Dict = None) -> str:
        print(f"🎯 Getting template prompt for ID: '{template_id}'")
        prompt_content = self._load_template_prompt_file(template_id, template_config)
        if prompt_content:
            print(f"✅ Using template-specific prompt file for {template_id}")
            return prompt_content
        if template_config and template_config.get('prompt_schema'):
            print("📋 Using template prompt_schema")
            context = self.extract_context_values(state) if state else {}
            return self.build_from_template_schema(template_config, context)
        raise RuntimeError(f"ENTERPRISE: No template prompt found for {template_id}")

    def extract_context_values(self, state: Dict) -> Dict:
        context = {
            "topic": state.get("topic", ""),
            "audience": state.get("audience", ""),
            "content_type": "content"
        }
        return context
    
    def analyze_context(self, state: Dict) -> WritingContext:
        params = state.get("dynamic_parameters", {})
        raw_template_config = state.get('template_config', {})
        template_config = safe_config_access(raw_template_config)

        content_spec = state.get('content_spec')
        topic = None

        if content_spec and hasattr(content_spec, 'topic'):
            topic = content_spec.topic
        elif content_spec and isinstance(content_spec, dict) and 'topic' in content_spec:
            topic = content_spec['topic']

        if not topic and isinstance(template_config, dict) and 'dynamic_overrides' in template_config:
            outer_overrides = template_config['dynamic_overrides']
            if isinstance(outer_overrides, dict) and 'dynamic_overrides' in outer_overrides:
                topic = outer_overrides['dynamic_overrides'].get("topic")
            elif isinstance(outer_overrides, dict):
                topic = outer_overrides.get("topic")

        if not topic:
            dynamic_overrides = params.get("dynamic_overrides", {})
            topic = dynamic_overrides.get("topic") if dynamic_overrides else None

        if not topic:
            raise ValueError("ENTERPRISE: Missing topic")

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
        research_data = {
            'academic_sources': [],
            'technical_findings': [],
            'industry_insights': [],
            'code_examples': [],
            'api_documentation': [],
            'validation_results': [],
            'raw_findings': {}
        }

        if state.get('research_findings'):
            research_data['raw_findings'].update(state['research_findings'])

        if state.get('mcp_results'):
            mcp_results = state['mcp_results']
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

        if state.get('tools_executed'):
            research_data['tools_used'] = state['tools_executed']

        print(f"📊 Extracted MCP research: {len(research_data['raw_findings'])} findings from {len(research_data.get('tools_used', []))} tools")
        return research_data

    def calculate_required_tokens(self, template_config: Dict, dynamic_overrides: Dict) -> int:
        requirements = template_config.get('requirements', {})
        if not requirements:
            raise ValueError("ENTERPRISE: Template missing requirements section")

        min_words = requirements.get('min_words')
        if not min_words:
            raise ValueError("ENTERPRISE: Template missing min_words requirement")

        if isinstance(min_words, dict) and 'priority' in min_words:
            for source in min_words['priority']:
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
        if not prompt:
            print("WARN: Empty prompt provided to sanitization")
            return "Generate comprehensive content."
        
        if not isinstance(prompt, str):
            prompt = str(prompt)
        
        original_length = len(prompt)
        prompt = prompt.replace('\x00', '')
        prompt = prompt.replace('\r\n', '\n')
        prompt = prompt.replace('\r', '\n')
        prompt = ' '.join(prompt.split())
        final_length = len(prompt)
        
        if final_length != original_length:
            print(f"DEBUG: Prompt sanitized: {original_length} -> {final_length} chars")
        
        if not prompt.strip():
            print("WARN: Prompt empty after sanitization")
            return "Generate comprehensive content."
        
        return prompt.strip()
    
    async def _fetch_recent_events(self, topic: str, timeframe: str, min_sources: int, parameters: Dict) -> Dict[str, Any]:
        try:
            if self.web_search_tool:
                results = await self.web_search_tool.search(f"{topic} recent developments {timeframe}")
                return {
                    'events': results.get('results', [])[:5],
                    'sources': [r.get('source', 'Unknown') for r in results.get('results', [])]
                }
            else:
                return {'events': [], 'sources': []}
        except Exception as e:
            print(f"Real-time fetch failed: {e}")
            return {'events': [], 'sources': []}

    def _summarize_events(self, events: List[Dict]) -> str:
        if not events:
            return "No recent events found."
        summary_parts = []
        for event in events[:3]:
            title = event.get('title', 'Recent development')
            summary_parts.append(f"- {title}")
        return "\n".join(summary_parts)

    def extract_all_parameters(self, state: Dict) -> Dict[str, Any]:
        extracted_params = {}

        for key in ['client_name', 'clientName', 'project_type', 'projectType', 'topic', 'api_name', 'newsletter_type', 'company_name', 'audience', 'tone', 'voice', 'target_platform', 'seo_focus', 'min_words', 'target_keywords', 'headline_style', 'cta_type', 'brand_voice', 'content_angle', 'competition_level']:
            if key in state:
                extracted_params[key] = state[key]

        content_spec = state.get('content_spec')
        if content_spec:
            if hasattr(content_spec, 'topic'):
                extracted_params['topic'] = content_spec.topic
            elif isinstance(content_spec, dict):
                extracted_params.update(content_spec)

        dynamic_params = state.get("dynamic_parameters", {})
        if isinstance(dynamic_params, dict):
            template_specific_keys = [
                'campaign_goal', 'target_platforms', 'brand_voice', 'post_count', 'content_types', 'campaign_duration',
                'market_sector', 'analysis_timeframe', 'key_metrics', 'geographic_scope', 'analysis_depth', 'data_sources', 'competitor_focus', 'regulatory_factors',
                'newsletter_type', 'subject_lines', 'opening_section', 'main_content', 'cta_section', 'closing_footer',
                'api_name', 'api_domain', 'auth_type', 'programming_languages', 'base_url', 'version_number',
                'include_sdks', 'include_postman', 'complexity_level', 'min_endpoints', 'code_examples_per_endpoint',
                'include_webhooks', 'rate_limiting', 'preferred_length', 'creativity_level', 'content_quality'
            ]

            for key in template_specific_keys:
                if key in dynamic_params:
                    value = dynamic_params[key]
                    if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    extracted_params[key] = value

            if 'dynamic_overrides' in dynamic_params:
                overrides = dynamic_params['dynamic_overrides']
                if isinstance(overrides, dict):
                    extracted_params.update(overrides)

        template_config = state.get('template_config', {})
        if isinstance(template_config, dict) and 'dynamic_overrides' in template_config:
            template_overrides = template_config['dynamic_overrides']
            if isinstance(template_overrides, dict):
                if 'dynamic_overrides' in template_overrides:
                    nested_overrides = template_overrides['dynamic_overrides']
                    if isinstance(nested_overrides, dict):
                        extracted_params.update(nested_overrides)
                else:
                    extracted_params.update(template_overrides)

        if isinstance(template_config, dict) and 'user_inputs' in template_config:
            user_inputs = template_config['user_inputs']
            if isinstance(user_inputs, dict):
                extracted_params.update(user_inputs)

        if isinstance(template_config, dict) and 'dynamic_parameters' in template_config:
            template_dynamic = template_config['dynamic_parameters']
            if isinstance(template_dynamic, dict):
                for key, value in template_dynamic.items():
                    if key != 'dynamic_overrides':
                        if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        extracted_params[key] = value

        template_params = [k for k in extracted_params.keys() if k in [
            'campaign_goal', 'target_platforms', 'brand_voice', 'post_count', 'content_types', 'campaign_duration',
            'market_sector', 'analysis_timeframe', 'key_metrics', 'geographic_scope'
        ]]

        logger.info(f"EXTRACTED PARAMETERS: {list(extracted_params.keys())}")
        logger.info(f"TEMPLATE-SPECIFIC FOUND: {template_params}")

        return extracted_params

    def _build_user_content_with_realtime(
        self, 
        context, 
        state: Dict[str, Any], 
        real_time_context: Dict[str, Any]
    ) -> str:
        extracted_params = self.extract_all_parameters(state)

        user_content_parts = [
            f"TOPIC: {context.topic}",
            f"AUDIENCE: {context.audience}",
            f"PLATFORM: {context.platform}",
            f"INTENT: {context.intent}",
            f"COMPLEXITY: {context.complexity_level}"
        ]

        if extracted_params:
            user_content_parts.append("")
            user_content_parts.append("PARAMETERS:")
            for key, value in extracted_params.items():
                if value and str(value).strip():
                    user_content_parts.append(f"{key}: {value}")

        planning_output = getattr(state, "planning_output", None) or state.get("planning_output")
        if planning_output:
            user_content_parts.append(f"\nPLANNING CONTEXT: {str(planning_output)}")

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
    
    async def _generate_adaptive_content(self, state: Dict[str, Any]) -> str:
        template_config = state.get("template_config", {})
        style_config = state.get("style_config", {})

        self.validate_enterprise_config(template_config, style_config)

        try:
            template_id = state.get("template", "")
            context = self.analyze_context(state)

            params = state.get("dynamic_parameters", {})
            dynamic_overrides = params.get("dynamic_overrides", {})
            if isinstance(template_config, dict) and 'dynamic_overrides' in template_config:
                outer_overrides = template_config['dynamic_overrides']
                if isinstance(outer_overrides, dict) and 'dynamic_overrides' in outer_overrides:
                    dynamic_overrides = outer_overrides['dynamic_overrides']

            real_time_context = await self._handle_real_time_requirements(
                template_config, context, dynamic_overrides
            )

            template_specific_prompt = self.get_template_specific_prompt(template_config, template_id, state)
            if not template_specific_prompt or len(template_specific_prompt.strip()) < 10:
                raise RuntimeError("ENTERPRISE: Template prompt invalid or empty")

            user_content = self._build_user_content_with_realtime(
                context, state, real_time_context
            )

            requires_code = template_config.get("code_agent", False)
            if not requires_code:
                user_content = user_content.replace("code examples", "practical examples")
                template_specific_prompt = template_specific_prompt.replace("code blocks", "content blocks")

            if len(user_content.strip()) < 10:
                raise RuntimeError("ENTERPRISE: User prompt invalid or empty")

            generation_settings = self._get_user_generation_settings(state)

            model_obj = get_model("writer", generation_settings)
            model_name = model_obj.model_name

            system_content = self._sanitize_prompt(template_specific_prompt)
            user_content = self._sanitize_prompt(user_content)
            combined_input = f"{system_content}\n\n{user_content}"

            if len(system_content + user_content) < 20:
                raise RuntimeError("ENTERPRISE: Combined prompt too short")

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
        try:
            print("DEBUG: Starting content extraction...")
            print(f"DEBUG: Response type: {type(response)}")
            print(f"DEBUG: Response has output_text: {hasattr(response, 'output_text')}")

            if hasattr(response, 'output_text'):
                content = response.output_text
            elif hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
            else:
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
        gen: Dict[str, Any] = {}
        
        dyn = state.get('dynamic_parameters', {}) or {}
        if isinstance(dyn, dict):
            gs = dyn.get('generation_settings')
            if isinstance(gs, dict):
                gen.update(gs)
            if 'max_tokens' in dyn and 'max_tokens' not in gen:
                gen['max_tokens'] = dyn['max_tokens']
            if 'temperature' in dyn and 'temperature' not in gen:
                gen['temperature'] = dyn['temperature']
            dov = dyn.get('dynamic_overrides', {})
            if isinstance(dov, dict):
                if 'max_tokens' in dov and 'max_tokens' not in gen:
                    gen['max_tokens'] = dov['max_tokens']
                if 'temperature' in dov and 'temperature' not in gen:
                    gen['temperature'] = dov['temperature']

        tc = state.get('template_config', {}) or {}
        if isinstance(tc, dict):
            tdp = tc.get('dynamic_parameters', {})
            if isinstance(tdp, dict):
                tdp_gs = tdp.get('generation_settings', {})
                if isinstance(tdp_gs, dict):
                    if 'max_tokens' in tdp_gs and 'max_tokens' not in gen:
                        gen['max_tokens'] = tdp_gs['max_tokens']
                    if 'temperature' in tdp_gs and 'temperature' not in gen:
                        gen['temperature'] = tdp_gs['temperature']
                tdp_dov = tdp.get('dynamic_overrides', {})
                if isinstance(tdp_dov, dict):
                    if 'max_tokens' in tdp_dov and 'max_tokens' not in gen:
                        gen['max_tokens'] = tdp_dov['max_tokens']
                    if 'temperature' in tdp_dov and 'temperature' not in gen:
                        gen['temperature'] = tdp_dov['temperature']

            tov = tc.get('dynamic_overrides', {})
            if isinstance(tov, dict) and 'dynamic_overrides' in tov and isinstance(tov['dynamic_overrides'], dict):
                tov = tov['dynamic_overrides']
            if isinstance(tov, dict):
                if 'max_tokens' in tov and 'max_tokens' not in gen:
                    gen['max_tokens'] = tov['max_tokens']
                if 'temperature' in tov and 'temperature' not in gen:
                    gen['temperature'] = tov['temperature']

        fallback_sources = [
            state.get('generation_settings', {}),
            state.get('user_settings', {}),
            getattr(state.get('content_spec', {}), 'generation_settings', {}),
            dyn.get('generation_settings', {})
        ]
        for s in fallback_sources:
            if isinstance(s, dict):
                if 'max_tokens' in s and 'max_tokens' not in gen:
                    gen['max_tokens'] = s['max_tokens']
                if 'temperature' in s and 'temperature' not in gen:
                    gen['temperature'] = s['temperature']

        if 'max_tokens' not in gen or 'temperature' not in gen:
            raise ValueError("ENTERPRISE: generation_settings with max_tokens and temperature required")

        gen['max_tokens'] = int(gen['max_tokens'])
        gen['temperature'] = float(gen['temperature'])
        logger.info(f"✅ Using settings: max_tokens={gen['max_tokens']}, temperature={gen['temperature']}")
        return gen
    
    async def _handle_real_time_requirements(
        self, 
        template_config: Dict[str, Any], 
        context, 
        dynamic_overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        real_time_support = template_config.get('real_time_support', {})

        if real_time_support.get('enabled'):
            logger.info(f"Real-time data REQUIRED for template: {template_config.get('name')}")
            if not (self.researcher_agent or self.web_search_tool):
                raise RuntimeError("ENTERPRISE: Real-time data required but no search capability configured")

            search_timeframe = real_time_support.get('max_age_hours', 24)
            required_sources = real_time_support.get('verification_sources', 1)

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
            return {
                'real_time_enabled': False,
                'knowledge_cutoff_warning': True,
                'cutoff_date': '2025-01-31'
            }

    def user_provided_code(self, state: Dict) -> str:
        params = state.get("dynamic_parameters", {})
        dynamic_overrides = params.get("dynamic_overrides", {}) if params else {}
        return dynamic_overrides.get("code_input", "") if dynamic_overrides else ""

    def _sanitize_and_enforce(self, raw: str, template_config: Dict = None, state: Dict = None) -> str:
        text = raw or ""

        if not template_config:
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            return text

        template_type = template_config.get('template_type', '')
        template_id = template_config.get('id', template_config.get('slug', ''))

        if template_type == 'blog_article' or 'blog' in template_id.lower():
            return self._enforce_blog_narrative_style(text)
        elif template_type == 'social_media_campaign':
            return self._preserve_social_structure(text)
        else:
            return self._basic_code_removal(text)

    def _enforce_blog_narrative_style(self, text: str) -> str:
        text = re.sub(r"```[\s\S]*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`\n]*`", "", text)

        sections = text.split('\n\n')
        processed_sections = []

        for section in sections:
            section = section.strip()
            if not section:
                continue

            if any(keyword in section.upper() for keyword in ['SEO TITLE', 'META DESCRIPTION', 'TITLE:', 'META TITLE']):
                processed_sections.append(section)
                continue

            if self._is_bullet_list(section):
                narrative = self._convert_bullets_to_narrative(section)
                processed_sections.append(narrative)
            else:
                processed_sections.append(section)

        return '\n\n'.join(processed_sections)

    def _is_bullet_list(self, text: str) -> bool:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        bullet_lines = [line for line in lines if line.startswith(('- ', '• ', '* '))]
        return len(bullet_lines) > len(lines) * 0.5

    def _convert_bullets_to_narrative(self, bullet_text: str) -> str:
        lines = [line.strip() for line in bullet_text.split('\n') if line.strip()]

        header = ""
        content_lines = []

        for line in lines:
            if not line.startswith(('- ', '• ', '* ')) and not content_lines:
                header = line
            elif line.startswith(('- ', '• ', '* ')):
                content_lines.append(line[2:].strip())

        if not content_lines:
            return bullet_text

        if len(content_lines) <= 3:
            if len(content_lines) == 1:
                narrative = content_lines[0]
            else:
                narrative = f"{', '.join(content_lines[:-1])}, and {content_lines[-1]}."
        else:
            first_part = content_lines[:3]
            remaining = content_lines[3:]
            narrative = f"{', '.join(first_part[:-1])}, and {first_part[-1]}."
            if remaining:
                if len(remaining) == 1:
                    narrative += f" Additionally, {remaining[0]}."
                else:
                    narrative += f" {', '.join(remaining[:-1])}, and {remaining[-1]} are also important considerations."

        if header:
            return f"{header}\n\n{narrative}"
        else:
            return narrative

    def _preserve_social_structure(self, text: str) -> str:
        text = re.sub(r"```[\s\S]*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`\n]*`", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text

    def _basic_code_removal(self, text: str) -> str:
        text = re.sub(r"```[\s\S]*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`\n]*`", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        template_config = getattr(state, 'template_config', None)
        style_config = getattr(state, 'style_config', None)

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

        self.validate_enterprise_config(template_config, style_config)

        template_id = (
            getattr(state, 'template_id', '') or 
            template_config.get('slug', '') or 
            template_config.get('id', '') or
            'unknown'
        )

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

            final_content = self._sanitize_and_enforce(
                generated_content.strip(), 
                template_config=template_config,
                state=state_dict
            )

            if not final_content:
                raise RuntimeError("ENTERPRISE: Generated content is empty after strip()")

            if len(final_content) < 50:
                raise RuntimeError(f"ENTERPRISE: Generated content too short ({len(final_content)} chars)")

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
        prompt_schema = template_config.get('prompt_schema', {})
        if prompt_schema.get('system_preamble'):
            return prompt_schema['system_preamble']
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
        if not events:
            return "No recent events found."
        
        summary_parts = []
        for event in events[:3]:
            title = event.get('title', 'Untitled Event')
            date = event.get('date', 'Recent')
            source = event.get('source', 'Unknown')
            summary_parts.append(f"- {title} ({date}, {source})")
        
        return "\n".join(summary_parts)

    def _build_research_integrated_prompt(self, template_config: Dict, template_id: str, state: Dict) -> str:
        research_data = self.extract_mcp_research_data(state)
        base_prompt = self._generate_prompt_from_config(template_config, template_id)
        if research_data['raw_findings']:
            research_context = "\n".join([f"Research: {k}: {v}" for k, v in research_data['raw_findings'].items()])
            return f"{base_prompt}\n\nResearch Context:\n{research_context}"
        return base_prompt

    # Optional shim so legacy wrapper works
    def generate_adaptive_content(self, state: Dict[str, Any]) -> str:
        return asyncio.run(self._generate_adaptive_content(state))

# Export the universal template-aware agent
template_aware_writer_agent = TemplateAwareWriterAgent()

# Legacy compatibility wrapper
def _legacy_writer_fn(state: dict) -> dict:
    return template_aware_writer_agent.generate_adaptive_content(state)

# Exports
WriterAgent = TemplateAwareWriterAgent
writer = RunnableLambda(_legacy_writer_fn)
