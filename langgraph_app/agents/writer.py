# File: langgraph_app/agents/writer.py
import os
import yaml
import json
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
#from langgraph_app.content_quality import ContentOriginalityEngine

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
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.memory_path = Path("storage/agent_memory")
        self.memory_path.mkdir(parents=True, exist_ok=True)
   
        
        # Dynamic template configuration paths
        self.template_paths = [
            "data/content_templates",
            "content_templates", 
            "templates"
        ]
        
        # Dynamic writer prompt paths
        self.prompt_paths = [
            "prompts/writer",
            "writer_prompts",
            "prompts"
        ]
        
        # Load accumulated knowledge
        self.success_patterns = self._load_memory("success_patterns.json")
        self.failure_patterns = self._load_memory("failure_patterns.json") 
        self.innovation_experiments = self._load_memory("experiments.json")
    
    
    def execute(self, state) -> Dict:
        """Execute method - safely converts state to dict"""
        print(f"DEBUG writer execute: state type = {type(state)}")

        # Handle EnrichedContentState properly
        if hasattr(state, 'template_config'):
            template_config = state.template_config
            template_id = getattr(state, 'template_id', '')

            # Create state dict for internal processing
            state_dict = {
                "template": template_id,
                "template_config": template_config,
                "style_profile": getattr(state, 'style_config', {}),
                "dynamic_parameters": {},
                "planning_output": getattr(state, 'planning_output', None),
                "research_findings": getattr(state, 'research_findings', None)
            }

            # Add content spec info if available
            if hasattr(state, 'content_spec'):
                state_dict["topic"] = state.content_spec.topic
                state_dict["audience"] = state.content_spec.audience
                state_dict["platform"] = state.content_spec.platform

            print(f"DEBUG writer template_id: {template_id}")
            print(f"DEBUG writer template_config type: {type(template_config)}")

        elif isinstance(state, dict):
            state_dict = state
            template_id = state_dict.get("template", "")
            template_config = state_dict.get("template_config", {})
        else:
            # Fallback handling
            state_dict = {"template": "", "dynamic_parameters": {}}
            template_id = ""
            template_config = {}

        return self.generate_adaptive_content(state_dict)


    def _load_memory(self, filename: str) -> List[Dict]:
        """Load agent memory from storage"""
        file_path = self.memory_path / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return []
    
    def _save_memory(self, data: List[Dict], filename: str):
        """Save agent memory to storage"""
        file_path = self.memory_path / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def load_template_config(self, template_id: str) -> Dict[str, Any]:
        """UNIVERSAL: Load template configuration from YAML files"""
        if not template_id:
            print("⚠️ No template_id provided")
            return {}
            
        print(f"🔍 Loading template config for: {template_id}")
        
        template_files = [
            f"{template_id}.yaml",
            f"{template_id}.yml", 
            f"{template_id}_template.yaml",
            f"{template_id}_template.yml"
        ]
        
        for template_path in self.template_paths:
            for template_file in template_files:
                full_path = os.path.join(template_path, template_file)
                
                if os.path.exists(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)
                            print(f"✅ Loaded template config: {full_path}")
                            return config
                    except Exception as e:
                        print(f"❌ Error loading template {full_path}: {e}")
                        continue
        
        print(f"⚠️ Template config not found for: {template_id}")
        return {}

    def get_template_specific_prompt(self, template_config: Dict[str, Any], template_id: str) -> str:
        """UNIVERSAL: Generate template-specific writer prompt from configuration"""
        
        # PRIORITY 1: Generate from template configuration
        if template_config:
            dynamic_prompt = self._generate_prompt_from_config(template_config, template_id)
            if dynamic_prompt:
                print(f"✅ Generated dynamic prompt from template config")
                return dynamic_prompt
        
        # PRIORITY 2: Try to find matching prompt file as fallback
        template_type = template_config.get('template_type', template_id)
        print(f"🔍 Looking for fallback prompt file for: {template_type}")
        
        prompt_files = [
            f"{template_type}_writer.txt",
            f"{template_id}_writer.txt",
            f"{template_type}.txt",
            f"{template_id}.txt"
        ]
        
        for prompt_file in prompt_files:
            prompt_content = self._load_prompt_file(prompt_file)
            if prompt_content:
                print(f"✅ Using fallback prompt file: {prompt_file}")
                return prompt_content
        
        # PRIORITY 3: Generate universal prompt
        print(f"⚠️ No prompt file found, generating universal prompt")
        return self._generate_universal_prompt(template_config, template_type)

    def _generate_prompt_from_config(self, template_config: Dict[str, Any], template_id: str) -> str:
        """Generate prompt dynamically from template configuration"""
        
        if not template_config:
            return ""
        
        # Extract configuration elements
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
    
    def _load_prompt_file(self, filename: str) -> Optional[str]:
        """Load prompt file from multiple possible locations"""
        for prompt_path in self.prompt_paths:
            full_path = os.path.join(prompt_path, filename)
            
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        print(f"✅ Loaded prompt file: {full_path}")
                        return content
                except Exception as e:
                    print(f"❌ Error loading prompt {full_path}: {e}")
                    continue
        
        return None

    def _generate_universal_prompt(self, template_config: Dict[str, Any], template_type: str) -> str:
        """Generate universal prompt based on template configuration"""
        purpose = template_config.get('purpose', 'Create high-quality content')
        target_audience = template_config.get('target_audience', 'general audience')
        tone = template_config.get('tone', {})
        
        prompt = f"""You are an expert content writer specializing in {template_type.replace('_', ' ')}.

PURPOSE: {purpose}

TARGET AUDIENCE: {target_audience}

WRITING STYLE:
- Tone: {tone.get('formality', 'professional')} formality
- Approach: {tone.get('persuasiveness', 'informative')} 
- Voice: {tone.get('voice', 'authoritative')}

CONTENT REQUIREMENTS:
"""
        
        # Add requirements from template config
        if 'content_requirements' in template_config:
            for req in template_config['content_requirements']:
                prompt += f"- {req}\n"
        else:
            prompt += "- Create valuable, actionable content\n- Use clear, engaging language\n- Provide specific examples\n"
        
        return prompt

    def analyze_context(self, state: Dict) -> WritingContext:
        """Extract and enrich context from state"""
        params = state.get("dynamic_parameters", {})

        # FIX: Safe template_config and style_config access
        raw_template_config = state.get('template_config', {})
        raw_style_config = state.get('style_profile', {})  # Note: it's style_profile in state

        # Ensure they are dictionaries, not strings
        template_config = safe_config_access(raw_template_config)
        if hasattr(template_config, '__dict__') and not hasattr(template_config, 'get'):
            template_config = vars(template_config)

        print(f"DEBUG analyze_context template_config: {type(template_config)} -> {template_config}")

        # Now safely use .get() on template_config and style_config
        topic = (template_config.get("topic") or 
                 params.get("topic") or 
                 params.get("primary_topic") or
                 state.get("topic", "Untitled"))

        audience = (template_config.get("target_audience") or
                   params.get("target_audience") or 
                   params.get("audience") or
                   state.get("audience", "General"))

        # Analyze intent from available data
        intent = self._analyze_intent_from_context(template_config, params, state)
        
        # Analyze complexity from context
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

    def _analyze_intent_from_context(self, template_config: Dict, params: Dict, state: Dict) -> str:
        """Analyze intent from context data"""
        # Check template config first
        if template_config.get("intent"):
            return template_config["intent"]
        
        # Analyze from available text
        all_text = str(template_config) + str(params) + str(state)
        text_lower = all_text.lower()
        
        # Intent detection based on content analysis
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
        
        return "inform"  # Default

    def _analyze_complexity_from_context(self, template_config: Dict, params: Dict, state: Dict) -> int:
        """Analyze complexity level from context"""
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

    def load_style_profile(self, name: str) -> Dict:
        """Load style profile with universal handling"""
        if not name or len(name) > 50 or '/' in name or '\\' in name:
            print(f"Warning: Invalid style profile name '{name}', using default")
            name = "jason"

        try:
            style_paths = [
                f"data/style_profiles/{name}.yaml",
                f"style_profile/{name}.yaml",
                f"langgraph_app/data/style_profiles/{name}.yaml"
            ]
            
            for style_path in style_paths:
                if os.path.exists(style_path):
                    with open(style_path, "r", encoding="utf-8") as f:
                        profile = yaml.safe_load(f)
                        print(f"✅ Successfully loaded style profile: {style_path}")
                        
                        if 'system_prompt' in profile:
                            system_prompt = profile['system_prompt']
                            
                            if isinstance(system_prompt, str) and system_prompt.strip():
                                print(f"✅ Using system_prompt content from YAML ({len(system_prompt)} chars)")
                            else:
                                profile['system_prompt'] = self._generate_universal_system_prompt(name, profile)
                                print(f"⚠️ Empty system_prompt in {name}, generated universal")
                        else:
                            profile['system_prompt'] = self._generate_universal_system_prompt(name, profile)
                            print(f"⚠️ No system_prompt in {name}, added universal")

                        return profile
            
            print(f"⚠️ Style profile not found: {name}, creating universal default")
            return self._create_universal_default_profile(name)

        except Exception as e:
            print(f"❌ Error loading style profile '{name}': {e}")
            return self._create_universal_default_profile(name)

    def _generate_universal_system_prompt(self, profile_name: str, profile_data: Dict) -> str:
        """Generate universal system prompt based on profile data"""
        # Try to load existing prompts first
        profile_lower = profile_name.lower()
        
        # Look for existing prompt files
        existing_prompts = [f"{profile_name}_system.txt", f"{profile_name}_prompt.txt"]
        for prompt_file in existing_prompts:
            prompt_content = self._load_prompt_file(prompt_file)
            if prompt_content:
                return prompt_content
        
        # Generate based on profile characteristics
        tone = profile_data.get('tone', {})
        expertise = profile_data.get('expertise_areas', [])
        writing_style = profile_data.get('writing_style', {})
        
        prompt_parts = [
            f"You are {profile_name}, an expert content writer with the following characteristics:"
        ]
        
        if expertise:
            prompt_parts.append(f"EXPERTISE AREAS: {', '.join(expertise)}")
        
        if tone:
            formality = tone.get('formality', 'professional')
            voice = tone.get('voice', 'authoritative')
            prompt_parts.append(f"TONE: {formality} formality with {voice} voice")
        
        if writing_style:
            prompt_parts.append(f"WRITING STYLE: {writing_style}")
        
        prompt_parts.extend([
            "Create high-quality, valuable content that:",
            "- Provides actionable insights and practical value",
            "- Uses clear, engaging language appropriate for the audience",
            "- Includes specific examples and real-world applications",
            "- Maintains consistent voice and expertise throughout"
        ])
        
        return "\n".join(prompt_parts)

    def _create_universal_default_profile(self, name: str) -> Dict:
        """Create universal default profile"""
        return {
            'name': name,
            'system_prompt': self._generate_universal_system_prompt(name, {}),
            'tone': {
                'formality': 'professional',
                'voice': 'authoritative',
                'persuasiveness': 'balanced'
            },
            'writing_style': {
                'approach': 'analytical',
                'structure': 'logical',
                'examples': 'practical'
            },
            'expertise_areas': ['general content creation'],
            'generated': True
        }

    def _extract_guaranteed_template_config(self, state: Dict) -> dict:
        """Extract guaranteed template configuration"""
        template_config = {}
        
        if 'template_config' in state and state['template_config']:
            template_config = state['template_config']
        elif 'content_spec' in state and hasattr(state['content_spec'], 'business_context'):
            template_config = state['content_spec'].business_context.get('template_config', {})
        
        if not template_config:
            template_config = self._create_template_config_from_state(state)
        
        return template_config

    def _create_template_config_from_state(self, state: Dict) -> Dict:
        """Create template config from available state data - FULLY DYNAMIC"""
        params = state.get("dynamic_parameters", {})

        # Dynamic template type analysis
        template = state.get('template', '')
        template_type = self._analyze_template_type_from_context(template, params, state)

        # Dynamic topic extraction
        topic = (params.get('topic') or
                 state.get('topic') or
                 self._extract_topic_from_context(params, state))

        # Dynamic audience analysis
        audience = (params.get('audience') or
                    params.get('target_audience') or
                    state.get('audience') or
                    self._analyze_audience_from_context(params, state))

        # Dynamic word count based on content type and complexity
        word_count = self._calculate_dynamic_word_count(template_type, topic, audience, params)

        # Dynamic tone analysis
        tone = self._analyze_tone_requirements(template_type, audience, params)

        return {
            'template_type': template_type,
            'topic': topic,
            'target_audience': audience,
            'min_word_count': word_count,
            'tone': tone,
            'generated_from_state': True
        }

    def _analyze_template_type_from_context(self, template: str, params: Dict, state: Dict) -> str:
        """Analyze template type from available context"""
        if template:
            return template

        # Analyze from content patterns
        all_context = str(params) + str(state)
        context_lower = all_context.lower()

        if any(word in context_lower for word in ['business', 'proposal', 'strategy']):
            return 'business_content'
        elif any(word in context_lower for word in ['technical', 'api', 'code', 'documentation']):
            return 'technical_content'
        elif any(word in context_lower for word in ['blog', 'article', 'story']):
            return 'editorial_content'
        elif any(word in context_lower for word in ['email', 'newsletter']):
            return 'email_content'
        else:
            return 'general_content'

    def _extract_topic_from_context(self, params: Dict, state: Dict) -> str:
        """Extract topic from available context"""
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

    def _analyze_audience_from_context(self, params: Dict, state: Dict) -> str:
        """Analyze audience from available context"""
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

    def _calculate_dynamic_word_count(self, template_type: str, topic: str, audience: str, params: Dict) -> int:
        """Calculate word count based on content characteristics"""
        base_count = 800  # Minimum viable content

        # Template type multiplier
        type_multipliers = {
            'business_content': 1.8,
            'technical_content': 2.2,
            'editorial_content': 1.5,
            'email_content': 0.6,
            'general_content': 1.0
        }

        # Audience complexity multiplier
        audience_multipliers = {
            'executive_audience': 1.3,
            'technical_audience': 1.6,
            'professional_audience': 1.2,
            'beginner_audience': 1.4,
            'general_audience': 1.0
        }

        # Topic complexity (length as proxy)
        topic_multiplier = min(1.0 + (len(topic.split()) * 0.1), 1.5)

        # User-specified word count takes priority
        if params.get('word_count'):
            return params['word_count']

        calculated = int(base_count *
                         type_multipliers.get(template_type, 1.0) *
                         audience_multipliers.get(audience, 1.0) *
                         topic_multiplier)
        return max(400, min(calculated, 4000))  # Bounds: 400-4000 words

    def _analyze_tone_requirements(self, template_type: str, audience: str, params: Dict) -> Dict:
        """Analyze tone requirements from context"""
        base_tone = {'formality': 'professional', 'persuasiveness': 'balanced'}

        # Template-based tone
        if template_type == 'business_content':
            base_tone.update({'formality': 'high', 'persuasiveness': 'strong'})
        elif template_type == 'technical_content':
            base_tone.update({'formality': 'high', 'persuasiveness': 'informative'})
        elif template_type == 'email_content':
            base_tone.update({'formality': 'medium', 'persuasiveness': 'conversational'})

        # Audience-based adjustments
        if 'executive' in audience:
            base_tone['formality'] = 'very_high'
        elif 'beginner' in audience:
            base_tone['formality'] = 'medium'
            base_tone['persuasiveness'] = 'supportive'
        return base_tone

    def _create_enhanced_prompt(self, context: WritingContext, template_config: Dict[str, Any],
                                 style: Dict, state: Dict) -> str:
        """UNIVERSAL: Create comprehensive writing prompt - NO HARDCODED FALLBACKS"""
        if hasattr(template_config, '__dict__') and not hasattr(template_config, 'get'):
            template_config = vars(template_config)
        if not template_config:
            template_config = self._extract_guaranteed_template_config(state)

        planning = state.get('planning_output')
        if planning and hasattr(planning, '__dict__') and not hasattr(planning, 'get'):
            planning = vars(planning)
            state['planning_output'] = planning

        template_type = template_config.get('template_type', context.platform).lower()
        section_order = template_config.get('section_order', [])
        min_words = template_config.get('min_word_count', 2500)
        tone_config = template_config.get('tone', {})

        prompt_parts = []

        # 1. STRUCTURE SECTION - Universal from config or analysis
        if section_order:
            prompt_parts.append("**REQUIRED SECTIONS (IN ORDER):**")
            prompt_parts.append("\n".join([f"## {section}" for section in section_order]))
        elif planning and hasattr(planning, 'estimated_sections'):
            sections = [section.get('name', f'Section {i+1}') for i, section in enumerate(planning.estimated_sections)]
            prompt_parts.append("**REQUIRED SECTIONS (IN ORDER):**")
            prompt_parts.append("\n".join([f"## {section}" for section in sections]))
        else:
            dynamic_sections = self._generate_universal_sections(context, template_config)
            prompt_parts.append("**REQUIRED SECTIONS (IN ORDER):**")
            prompt_parts.append("\n".join([f"## {section}" for section in dynamic_sections]))

        # 2. REQUIREMENTS SECTION - Universal from config
        requirements = [f"- Minimum {min_words} words total", "- Each section must be substantial and complete"]

        template_requirements = template_config.get('content_requirements', [])
        if template_requirements:
            requirements.extend([f"- {req}" for req in template_requirements])
        else:
            dynamic_requirements = self._generate_universal_requirements(context, template_config)
            requirements.extend(dynamic_requirements)

        prompt_parts.append("**CONTENT REQUIREMENTS:**")
        prompt_parts.append("\n".join(requirements))

        # 3. TONE SECTION - Universal from config
        tone_guidance = self._generate_universal_tone_guidance(context, template_config, tone_config)
        prompt_parts.append(f"**TONE AND STYLE:** {tone_guidance}")

        # 4. CONTEXT SECTION
        prompt_parts.extend([
            f"**TOPIC:** {context.topic}",
            f"**AUDIENCE:** {context.audience}",
            f"**COMPLEXITY LEVEL:** {context.complexity_level}/10"
        ])

        # 5. FINAL INSTRUCTION - Universal
        final_instruction = self._generate_universal_final_instruction(context, template_config)
        prompt_parts.append(final_instruction)

        return "\n".join(prompt_parts)

    def _generate_universal_sections(self, context: WritingContext, template_config: Dict[str, Any]) -> List[str]:
        """Generate universal sections based on content analysis"""
        topic_words = context.topic.lower().split()
        audience_lower = context.audience.lower()
        
        sections = [f"{context.topic} Overview"]
        
        # Analyze topic for section generation
        topic_analysis = self._analyze_topic_characteristics(context.topic, context.audience)
        
        if topic_analysis['is_business_focused']:
            sections.extend([
                "Strategic Analysis",
                "Market Considerations", 
                "Implementation Approach",
                "Success Metrics",
                "Next Steps"
            ])
        elif topic_analysis['is_technical']:
            sections.extend([
                "Technical Foundation",
                "Implementation Guide",
                "Best Practices",
                "Practical Examples",
                "Troubleshooting"
            ])
        elif topic_analysis['is_educational']:
            sections.extend([
                "Core Concepts",
                "Step-by-Step Guide",
                "Real-World Applications",
                "Common Challenges",
                "Further Learning"
            ])
        else:
            # Universal sections based on content characteristics
            sections.extend([
                f"Understanding {context.topic}",
                "Key Principles",
                "Practical Applications",
                "Implementation Considerations",
                "Future Outlook"
            ])
        
        sections.append("Key Takeaways")
        return sections

    def _analyze_topic_characteristics(self, topic: str, audience: str) -> Dict[str, bool]:
        """Analyze topic characteristics for section generation"""
        topic_lower = topic.lower()
        audience_lower = audience.lower()
        
        return {
            'is_business_focused': any(word in topic_lower for word in ['business', 'strategy', 'market', 'revenue', 'growth', 'roi']) or 'executive' in audience_lower,
            'is_technical': any(word in topic_lower for word in ['technical', 'implementation', 'development', 'api', 'system', 'code']) or any(word in audience_lower for word in ['developer', 'engineer', 'technical']),
            'is_educational': any(word in topic_lower for word in ['learn', 'guide', 'tutorial', 'how to', 'introduction']) or any(word in audience_lower for word in ['student', 'beginner', 'learner']),
            'is_analytical': any(word in topic_lower for word in ['analysis', 'research', 'study', 'data', 'insight']),
            'is_creative': any(word in topic_lower for word in ['design', 'creative', 'innovation', 'art'])
        }

    def _generate_universal_requirements(self, context: WritingContext, template_config: Dict[str, Any]) -> List[str]:
        """Generate universal content requirements"""
        requirements = []
        
        topic_analysis = self._analyze_topic_characteristics(context.topic, context.audience)
        
        if topic_analysis['is_business_focused']:
            requirements.extend([
                "- Include specific data, metrics, and business case",
                "- Provide actionable strategic recommendations",
                "- Address ROI and implementation considerations"
            ])
        elif topic_analysis['is_technical']:
            requirements.extend([
                "- Provide concrete, implementable technical guidance",
                "- Include working examples and code where appropriate",
                "- Address troubleshooting and best practices"
            ])
        elif topic_analysis['is_educational']:
            requirements.extend([
                "- Use clear explanations with progressive complexity",
                "- Include practical exercises and examples",
                "- Provide resources for further learning"
            ])
        else:
            requirements.extend([
                "- Provide original, valuable insights",
                "- Include specific examples and case studies",
                "- Offer actionable advice readers can implement"
            ])
        
        # Universal quality requirements
        requirements.extend([
            "- Use engaging, clear writing style",
            "- Maintain logical structure and flow",
            "- Include relevant data and supporting evidence"
        ])
        
        return requirements

    def _generate_universal_tone_guidance(self, context: WritingContext, template_config: Dict[str, Any], tone_config: Dict) -> str:
        """Generate universal tone guidance"""
        tone_elements = []
        
        formality = tone_config.get('formality', 'professional')
        voice = tone_config.get('voice', 'authoritative')
        persuasiveness = tone_config.get('persuasiveness', 'balanced')
        
        tone_elements.append(f"{formality} formality")
        tone_elements.append(f"{voice} voice")
        tone_elements.append(f"{persuasiveness} persuasiveness")
        
        # Context-specific adjustments
        if "executive" in context.audience.lower():
            tone_elements.append("strategic and decision-oriented")
        elif "technical" in context.audience.lower():
            tone_elements.append("precise and implementation-focused")
        elif "beginner" in context.audience.lower():
            tone_elements.append("educational and supportive")
        
        return ", ".join(tone_elements)

    def _generate_universal_final_instruction(self, context: WritingContext, template_config: Dict[str, Any]) -> str:
        """Generate universal final instruction"""
        topic_analysis = self._analyze_topic_characteristics(context.topic, context.audience)
        
        if topic_analysis['is_business_focused']:
            focus = "strategic value and actionable business insights"
        elif topic_analysis['is_technical']:
            focus = "technical accuracy and practical implementation"
        elif topic_analysis['is_educational']:
            focus = "clear learning outcomes and skill development"
        else:
            focus = "valuable insights and practical applications"
        
        return f"Generate expert-level content about {context.topic} that provides {focus} for {context.audience}."

    def generate_adaptive_content(self, state: Dict) -> Dict:
        """UNIVERSAL: Template-aware content generation with ZERO FALLBACKS"""
        
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
        
        style_profile_input = state.get("style_profile", "jason")
        if isinstance(style_profile_input, str):
            style = self.load_style_profile(style_profile_input)
        else:
            style = style_profile_input
            
        template_specific_prompt = self.get_template_specific_prompt(template_config, template_id)
        user_prompt = self._create_enhanced_prompt(context, template_config, style, state)
        
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
        
        model = get_model("writer")
        print(f"🔧 Using model: {model}")
        print(f"📝 Template type: {template_config.get('template_type', 'universal')}")
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        
        generated_content = response.choices[0].message.content.strip()
        
        metadata = {
            "template_id": template_id,
            "template_type": template_config.get('template_type', 'universal'),
            "topic": context.topic,
            "audience": context.audience,
            "platform": context.platform,
            "intent": context.intent,
            "complexity_level": context.complexity_level,
            "generation_timestamp": datetime.now().isoformat(),
            "word_count": len(generated_content.split()),
            "model_used": model,
            "template_config_loaded": bool(template_config)
        }
        
        print(f"✅ Generated {metadata['word_count']} words for {template_id}")
        # Content originality checking removed
        return {
            **state, 
            "draft": generated_content,
            "metadata": metadata,
            "template_config": template_config,
        }


# Export the universal template-aware agent
template_aware_writer_agent = TemplateAwareWriterAgent()

# Legacy compatibility wrapper
def _legacy_writer_fn(state: dict) -> dict:
    """Legacy wrapper for backward compatibility"""
    return template_aware_writer_agent.generate_adaptive_content(state)

# Exports
WriterAgent = TemplateAwareWriterAgent
writer = RunnableLambda(_legacy_writer_fn)