# File: langgraph_app/agents/writer.py
import os
import yaml
import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from langgraph_app.enhanced_model_registry import get_model

load_dotenv()

class WritingMode(Enum):
    CREATIVE = "creative"
    ANALYTICAL = "analytical" 
    TECHNICAL = "technical"
    NARRATIVE = "narrative"
    PERSUASIVE = "persuasive"
    EXPERIMENTAL = "experimental"

class AdaptiveLevel(Enum):
    CONSERVATIVE = "conservative"  # Stick to proven patterns
    BALANCED = "balanced"         # Mix proven with experimental
    INNOVATIVE = "innovative"     # Push boundaries
    EXPERIMENTAL = "experimental" # Maximum creativity

@dataclass
class WritingContext:
    """Rich context for adaptive writing decisions"""
    topic: str
    audience: str
    platform: str
    intent: str  # inform, persuade, entertain, teach, inspire
    complexity_level: int = 5  # 1-10 scale
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

class InnovativeWriterAgent:
    """
    Next-generation writer agent that adapts, learns, and innovates
    
    Features:
    - Multi-modal writing strategies
    - Real-time adaptation based on feedback
    - Experimental technique injection
    - Pattern learning from successes/failures
    - Context-aware creativity scaling
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.memory_path = Path("storage/agent_memory")
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Load accumulated knowledge
        self.success_patterns = self._load_memory("success_patterns.json")
        self.failure_patterns = self._load_memory("failure_patterns.json") 
        self.innovation_experiments = self._load_memory("experiments.json")
        
        # Experimental techniques to inject creativity
        self.experimental_techniques = {
            "contrarian_perspective": "Challenge conventional wisdom in the topic",
            "analogy_bridging": "Create unexpected analogies between disparate fields",
            "temporal_shifting": "Examine the topic from past/future perspectives",
            "stakeholder_rotation": "Tell the story from multiple viewpoints",
            "constraint_inversion": "What if the opposite constraint was true?",
            "emergence_patterns": "Look for unexpected connections and patterns",
            "question_layering": "Ask questions about your questions",
            "assumption_archaeology": "Dig up and examine hidden assumptions"
        }
        
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
    
    def analyze_context(self, state: Dict) -> WritingContext:
        """Extract and enrich context from state"""
        params = state.get("dynamic_parameters", {})

        # Determine intent from various clues
        intent = "inform"  # default
        if any(word in str(params).lower() for word in ["persuade", "convince", "argue"]):
            intent = "persuade"
        elif any(word in str(params).lower() for word in ["story", "narrative", "journey"]):
            intent = "entertain"
        elif any(word in str(params).lower() for word in ["learn", "teach", "guide", "tutorial"]):
            intent = "teach"
        elif any(word in str(params).lower() for word in ["inspire", "motivate", "vision"]):
            intent = "inspire"
            
        # Assess complexity
        complexity = 5
        if "technical" in str(state).lower() or "advanced" in str(state).lower():
            complexity = 8
        elif "beginner" in str(state).lower() or "simple" in str(state).lower():
            complexity = 3
            
        return WritingContext(
            topic=params.get("topic", state.get("topic", "Untitled")),
            audience=params.get("audience", state.get("audience", "General")),
            platform=state.get("platform", "substack"),
            intent=intent,
            complexity_level=complexity,
            innovation_preference=AdaptiveLevel(
                state.get("innovation_level", "balanced")
            )
        )
    
    def select_writing_strategy(self, context: WritingContext) -> WritingStrategy:
        """Adaptively select writing strategy based on context and learned patterns"""
        
        # Base strategy selection
        if context.intent == "teach":
            mode = WritingMode.ANALYTICAL
            base_structure = "problem → solution → examples → practice"
        elif context.intent == "inspire":
            mode = WritingMode.NARRATIVE
            base_structure = "vision → challenge → transformation → call_to_action"
        elif context.intent == "persuade":
            mode = WritingMode.PERSUASIVE
            base_structure = "problem → consequences → solution → benefits"
        elif context.complexity_level > 7:
            mode = WritingMode.TECHNICAL
            base_structure = "overview → deep_dive → implementation → implications"
        else:
            mode = WritingMode.CREATIVE
            base_structure = "hook → exploration → insight → application"
            
        # Adaptive modifications based on innovation preference
        experimental_techniques = []
        if context.innovation_preference in [AdaptiveLevel.INNOVATIVE, AdaptiveLevel.EXPERIMENTAL]:
            # Select experimental techniques based on context
            if context.complexity_level > 6:
                experimental_techniques.extend(["assumption_archaeology", "emergence_patterns"])
            if "startup" in context.topic.lower():
                experimental_techniques.extend(["contrarian_perspective", "temporal_shifting"])
            if context.intent == "inspire":
                experimental_techniques.extend(["analogy_bridging", "stakeholder_rotation"])
                
        # Learn from past successes/failures
        similar_contexts = self._find_similar_contexts(context)
        if similar_contexts:
            # Adapt based on what worked before
            successful_patterns = [p for p in similar_contexts if p.get("success_score", 0) > 0.7]
            if successful_patterns:
                # Extract successful structure patterns
                successful_structures = [p.get("structure") for p in successful_patterns]
                if successful_structures:
                    base_structure = max(set(successful_structures), key=successful_structures.count)
        
        return WritingStrategy(
            mode=mode,
            structure_pattern=base_structure,
            tone_adaptation=self._calculate_tone_adaptation(context),
            experimental_techniques=experimental_techniques
        )
    
    def _find_similar_contexts(self, context: WritingContext) -> List[Dict]:
        """Find similar past contexts to learn from"""
        similar = []
        for pattern in self.success_patterns + self.failure_patterns:
            # Simple similarity scoring
            similarity = 0
            if pattern.get("topic_category") == self._categorize_topic(context.topic):
                similarity += 0.3
            if pattern.get("audience") == context.audience:
                similarity += 0.2
            if pattern.get("intent") == context.intent:
                similarity += 0.3
            if abs(pattern.get("complexity", 5) - context.complexity_level) <= 2:
                similarity += 0.2
                
            if similarity > 0.5:
                pattern["similarity"] = similarity
                similar.append(pattern)
                
        return sorted(similar, key=lambda x: x["similarity"], reverse=True)[:5]
    
    def _categorize_topic(self, topic: str) -> str:
        """Categorize topic for pattern matching"""
        topic_lower = topic.lower()
        if any(word in topic_lower for word in ["ai", "ml", "tech", "software", "code"]):
            return "technology"
        elif any(word in topic_lower for word in ["startup", "business", "company", "market"]):
            return "business"
        elif any(word in topic_lower for word in ["learn", "skill", "education", "guide"]):
            return "education"
        else:
            return "general"
    
    def _calculate_tone_adaptation(self, context: WritingContext) -> Dict[str, float]:
        """Calculate tone adaptations based on context"""
        base_tones = {
            "formal": 0.3,
            "conversational": 0.5,
            "technical": 0.2,
            "inspiring": 0.3,
            "provocative": 0.1
        }
        
        # Adapt based on context
        if context.platform == "linkedin":
            base_tones["professional"] = 0.6
            base_tones["conversational"] = 0.4
        elif context.platform == "twitter":
            base_tones["provocative"] = 0.4
            base_tones["conversational"] = 0.6
        elif context.complexity_level > 7:
            base_tones["technical"] = 0.7
            base_tones["formal"] = 0.5
            
        if context.intent == "inspire":
            base_tones["inspiring"] = 0.8
            
        return base_tones
    
    def inject_experimental_techniques(self, prompt: str, techniques: List[str]) -> str:
        """Inject experimental writing techniques into the prompt"""
        if not techniques:
            return prompt
            
        technique_instructions = []
        for technique in techniques:
            if technique in self.experimental_techniques:
                technique_instructions.append(
                    f"🧪 EXPERIMENTAL TECHNIQUE - {technique.replace('_', ' ').title()}: "
                    f"{self.experimental_techniques[technique]}"
                )
        
        if technique_instructions:
            experimental_section = "\n\nEXPERIMENTAL WRITING DIRECTIVES:\n" + "\n".join(technique_instructions)
            experimental_section += "\n\nIntegrate these experimental approaches naturally into your writing."
            return prompt + experimental_section
            
        return prompt

    def load_style_profile(self, name: str) -> Dict:
        """Load style profile with FIXED YAML content handling"""
        
        # Validate style profile name
        if not name or len(name) > 50 or '/' in name or '\\' in name:
            print(f"Warning: Invalid style profile name '{name}', using default")
            name = "jason"

        try:
            # Try multiple possible paths for style profiles
            style_paths = [
                f"data/style_profiles/{name}.yaml",
                f"style_profile/{name}.yaml",  # Your actual location!
                f"langgraph_app/data/style_profiles/{name}.yaml"
            ]
            
            for style_path in style_paths:
                if os.path.exists(style_path):
                    with open(style_path, "r", encoding="utf-8") as f:
                        profile = yaml.safe_load(f)
                        print(f"✅ Successfully loaded style profile: {style_path}")
                        
                        # CRITICAL FIX: Ensure system_prompt is treated as content, not filename
                        if 'system_prompt' in profile:
                            system_prompt = profile['system_prompt']
                            
                            # ✅ Keep system_prompt as-is - it's YAML content, not a filename!
                            if isinstance(system_prompt, str) and system_prompt.strip():
                                print(f"✅ Using system_prompt content from YAML ({len(system_prompt)} chars)")
                            else:
                                # Fallback if system_prompt is empty or invalid
                                profile['system_prompt'] = self._get_default_system_prompt_for_profile(name)
                                print(f"⚠️ Empty system_prompt in {name}, using default")
                        else:
                            # Add default system_prompt if missing
                            profile['system_prompt'] = self._get_default_system_prompt_for_profile(name)
                            print(f"⚠️ No system_prompt in {name}, added default")

                        return profile
            
            # If no profile found, create adaptive default
            print(f"⚠️ Style profile not found: {name}, creating adaptive default")
            return self._create_adaptive_default_profile(name)

        except Exception as e:
            print(f"❌ Error loading style profile '{name}': {e}")
            return self._create_adaptive_default_profile(name)

    def load_system_prompt(self, prompt_source: str) -> str:
        """FIXED: Load system prompt - handles both YAML content AND file references"""
        
        # CRITICAL FIX: Check if this is already content (from YAML) vs filename
        if self._is_yaml_content(prompt_source):
            print(f"✅ Using YAML system_prompt content ({len(prompt_source)} chars)")
            return prompt_source.strip()
        
        # Otherwise, treat as filename and try to load from prompts directory
        if not prompt_source.endswith('.txt'):
            prompt_source += '.txt'

        prompt_path = os.path.join("prompts", "writer", prompt_source)

        try:
            if os.path.exists(prompt_path):
                with open(prompt_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    print(f"✅ Loaded system prompt from file: {prompt_path}")
                    return content
            else:
                print(f"⚠️ Prompt file not found: {prompt_path}, using default")
                return self._get_fallback_system_prompt()

        except Exception as e:
            print(f"❌ Error loading system prompt file '{prompt_source}': {e}")
            return self._get_fallback_system_prompt()

    def _is_yaml_content(self, text: str) -> bool:
        """Determine if text is YAML content vs filename"""
        if not isinstance(text, str):
            return False
        
        # If it's multi-line, it's content
        if '\n' in text:
            return True
        
        # If it's very long, it's likely content
        if len(text) > 100:
            return True
        
        # If it contains style-specific words, it's content
        style_indicators = [
            'you are', 'write', 'create', 'structure', 'tone', 'format',
            'business proposal', 'academic', 'technical', 'startup'
        ]
        
        text_lower = text.lower()
        if any(indicator in text_lower for indicator in style_indicators):
            return True
        
        # If it looks like a filename
        if text.endswith('.txt') or ('/' not in text and '\\' not in text and len(text) < 50):
            return False
        
        # Default to treating as content
        return True

    def _get_default_system_prompt_for_profile(self, profile_name: str) -> str:
        """Generate appropriate default system prompt based on profile name"""
        
        profile_lower = profile_name.lower()
        
        if 'business' in profile_lower or 'startup' in profile_lower or 'venture' in profile_lower:
            return """You are a business content specialist. Create professional business content with:
- Clear value propositions
- Strategic insights
- Actionable recommendations
- Professional business language
- Structured sections with headers
Avoid casual greetings. Start with authoritative statements."""
        
        elif 'academic' in profile_lower or 'phd' in profile_lower:
            return """You are an academic writing specialist. Create scholarly content with:
- Clear thesis statements
- Evidence-based arguments
- Rigorous analysis
- Formal academic tone
- Proper citation methodology
- Logical structure and flow
Avoid casual language. Use formal academic discourse."""
        
        elif 'technical' in profile_lower:
            return """You are a technical writing specialist. Create precise technical content with:
- Clear technical explanations
- Step-by-step procedures
- Accurate technical terminology
- Implementation details
- Best practices and standards
- Structured documentation format
Focus on clarity and technical accuracy."""
        
        elif 'storytelling' in profile_lower or 'founder' in profile_lower:
            return """You are a narrative content specialist. Create compelling stories with:
- Engaging narrative structure
- Character development
- Emotional connection
- Vivid imagery and examples
- Clear story arc
- Relatable insights
Build authentic connections through storytelling."""
        
        else:
            return """You are an expert content writer. Create engaging, well-structured content that:
- Serves the reader's needs
- Maintains appropriate tone and style
- Uses clear, compelling language
- Follows logical structure
- Provides valuable insights
- Matches the specified format and requirements
Write with authority and clarity."""

    def _create_adaptive_default_profile(self, profile_name: str) -> Dict:
        """Create intelligent default profile when none exists"""
        
        return {
            "id": profile_name,
            "name": profile_name.replace('_', ' ').title(),
            "description": f"Adaptive profile for {profile_name}",
            "system_prompt": self._get_default_system_prompt_for_profile(profile_name),
            "structure": "discovery → insight → application → impact",
            "voice": "professional and authoritative", 
            "tone": "engaging and informative",
            "settings": {
                "use_analogies": True,
                "avoid_jargon": False,
                "include_examples": True,
                "conversational_tone": False
            },
            "enhanced_version": True,
            "fallback": True,
            "created_dynamically": True
        }

    def _get_fallback_system_prompt(self) -> str:
        """Fallback system prompt when all else fails"""
        return """You are an innovative AI writing assistant that adapts to context and pushes creative boundaries.
Your goal is to create compelling, valuable content that serves the reader while exploring fresh perspectives.
Write with clarity, insight, and engagement while maintaining high quality standards."""

    def _get_template_structure_requirements(self, state: Dict) -> str:
        """Extract template structure requirements - THIS IS THE KEY METHOD FOR TEMPLATE ENFORCEMENT"""
        
        template_config = state.get("template_config", {})
        template_id = state.get("template", "")
        
        print(f"🔍 Checking template structure for: {template_id}")
        
        # Check for specific template structure requirements
        if "business_proposal" in template_id.lower():
            print("✅ Applying BUSINESS PROPOSAL structure")
            return """MANDATORY STRUCTURE - Business Proposal Format:
1. Executive Summary (150-200 words)
   - Problem statement
   - Solution overview  
   - Key benefits
   - Financial summary

2. Problem Statement & Market Opportunity (300-400 words)
   - Current market pain points
   - Market size and opportunity
   - Target audience definition
   - Competitive landscape

3. Proposed Solution & Value Proposition (400-500 words)
   - Detailed solution description
   - Unique value proposition
   - Key features and benefits
   - Competitive advantages

4. Financial Projections & ROI Analysis (300-400 words)
   - Revenue projections
   - Cost structure
   - Break-even analysis
   - Return on investment

5. Implementation Timeline & Next Steps (200-300 words)
   - Project phases
   - Key milestones
   - Resource requirements
   - Immediate action items

CRITICAL: Use professional business language throughout. Include specific metrics, financial data, and quantifiable benefits. Start with authoritative statements, not casual greetings."""
        
        elif "technical_documentation" in template_id.lower():
            print("✅ Applying TECHNICAL DOCUMENTATION structure")
            return """MANDATORY STRUCTURE - Technical Documentation Format:
1. Overview & Prerequisites (200 words)
   - System overview
   - Technical requirements
   - Prerequisites

2. Technical Specifications (400-600 words)
   - Architecture details
   - System components
   - Technical requirements

3. Implementation Guide (600-800 words)
   - Step-by-step procedures
   - Configuration details
   - Code examples

4. Code Examples & Best Practices (400-600 words)
   - Working code samples
   - Best practices
   - Common patterns

5. Troubleshooting & Support (200-400 words)
   - Common issues
   - Solutions
   - Support resources

Use precise technical language. Include code examples and implementation details."""
        
        elif "research_paper" in template_id.lower():
            print("✅ Applying RESEARCH PAPER structure")
            return """MANDATORY STRUCTURE - Research Paper Format:
1. Abstract (150-200 words)
   - Research problem
   - Methodology
   - Key findings
   - Conclusions

2. Introduction & Literature Review (400-500 words)
   - Problem definition
   - Current research landscape
   - Research gap
   - Research questions

3. Methodology (300-400 words)
   - Research approach
   - Data collection methods
   - Analysis techniques
   - Limitations

4. Results & Analysis (500-600 words)
   - Key findings
   - Data analysis
   - Statistical results
   - Interpretation

5. Discussion & Conclusions (300-400 words)
   - Implications
   - Future research
   - Limitations
   - Conclusions

Use formal academic language with proper citations and evidence-based arguments."""
        
        elif template_config.get("suggested_sections"):
            # Use template-defined sections
            sections = template_config["suggested_sections"]
            structure_parts = []
            for i, section in enumerate(sections, 1):
                section_name = section.get("name", f"Section {i}").replace("_", " ").title()
                description = section.get("description", "")
                structure_parts.append(f"{i}. {section_name}" + (f" - {description}" if description else ""))
            
            return "MANDATORY STRUCTURE:\n" + "\n".join(structure_parts)
        
        print("⚠️ No specific template structure found, using default")
        return ""

    def _get_style_enforcement_requirements(self, style: Dict, context: WritingContext) -> str:
        """Extract style enforcement requirements"""
        
        requirements = []
        
        # Voice and tone requirements
        voice = style.get('voice', '')
        tone = style.get('tone', '')
        
        if voice:
            requirements.append(f"Voice: {voice}")
        if tone:
            requirements.append(f"Tone: {tone}")
        
        # Style-specific requirements
        style_id = style.get('id', '').lower()
        
        if 'business' in style_id or 'startup' in style_id or 'venture' in style_id:
            requirements.extend([
                "Use professional business language",
                "Include specific metrics and ROI data where relevant", 
                "Start with authoritative statements, not casual greetings",
                "Focus on strategic insights and actionable recommendations"
            ])
        
        elif 'academic' in style_id or 'phd' in style_id:
            requirements.extend([
                "Use formal academic discourse",
                "Start with clear thesis statements",
                "Support arguments with evidence",
                "Avoid casual language and colloquialisms",
                "Maintain scholarly objectivity"
            ])
        
        elif 'technical' in style_id:
            requirements.extend([
                "Use precise technical terminology", 
                "Include implementation details and code examples",
                "Focus on practical applications and best practices",
                "Structure information logically for technical audiences"
            ])
        
        # Forbidden patterns (if any)
        forbidden = style.get('forbidden_patterns', [])
        if forbidden:
            requirements.append(f"FORBIDDEN PHRASES: Never use: {', '.join(forbidden)}")
        
        return "\n".join([f"- {req}" for req in requirements]) if requirements else ""

    def _create_base_prompt(self, context: WritingContext, strategy: WritingStrategy, 
                          style: Dict, state: Dict) -> str:
        """ENHANCED: Create base writing prompt with template structure enforcement"""
        
        # Platform-specific length instructions
        platform = context.platform
        if platform == "medium":
            length_instruction = "Write a comprehensive long-form article between 1600-2200 words, optimized for an 8-12 minute read."
        elif platform == "twitter":
            length_instruction = "Write a compelling Twitter thread with 5-8 tweets, each under 280 characters."
        elif platform == "linkedin":
            length_instruction = "Write a professional LinkedIn post between 800-1200 words that sparks meaningful discussion."
        else:
            length_instruction = "Write an engaging document between 800-1200 words."
        
        # Extract research context
        research = state.get("research", "")
        research_instruction = f"\n\nRELEVANT RESEARCH TO INCORPORATE:\n{research}" if research else ""
        
        # ✅ CRITICAL: Get template structure requirements
        template_structure = self._get_template_structure_requirements(state)
        template_instruction = ""
        if template_structure:
            template_instruction = f"\n\n{template_structure}"
        
        # ✅ Get style enforcement requirements  
        style_requirements = self._get_style_enforcement_requirements(style, context)
        style_instruction = ""
        if style_requirements:
            style_instruction = f"\n\nSTYLE REQUIREMENTS:\n{style_requirements}"
        
        # Build enhanced prompt
        prompt = f"""
{length_instruction}

WRITING CONTEXT:
- Topic: {context.topic}
- Target Audience: {context.audience} 
- Intent: {context.intent}
- Complexity Level: {context.complexity_level}/10
- Platform: {context.platform}

ADAPTIVE STRATEGY:
- Writing Mode: {strategy.mode.value}
- Structure Pattern: {strategy.structure_pattern}
- Innovation Level: {context.innovation_preference.value}

STYLE REQUIREMENTS:
- Voice: {style.get('voice', 'conversational')}
- Tone: {style.get('tone', 'engaging')}
- Structure Flow: {style.get('structure', strategy.structure_pattern)}

{template_instruction}
{style_instruction}
{research_instruction}

INNOVATION CHALLENGE:
Find a fresh angle or unexpected insight that adds genuine value to the reader's understanding.

CRITICAL INSTRUCTION:
You MUST follow the specified template structure exactly. Do not deviate from the required sections and format. Each section must contain the specified word count and content type.
"""
        
        return prompt
    
    def generate_adaptive_content(self, state: Dict) -> Dict:
        """Main content generation with adaptive intelligence"""
        
        # Analyze context and select strategy
        context = self.analyze_context(state)
        strategy = self.select_writing_strategy(context)
        
        # Load style profile
        style_profile_input = state.get("style_profile", "jason")
        if isinstance(style_profile_input, str):
            style = self.load_style_profile(style_profile_input)
        else:
            style = style_profile_input
            
        # Generate base prompt
        base_prompt = self._create_base_prompt(context, strategy, style, state)
        
        # Inject experimental techniques
        enhanced_prompt = self.inject_experimental_techniques(
            base_prompt, 
            strategy.experimental_techniques
        )
        
        # Get system prompt - handle both inline content and filenames
        system_prompt_source = style.get("system_prompt", "You are an expert content writer. Create engaging, well-structured content that matches the specified style and audience.")
        system_prompt = self.load_system_prompt(system_prompt_source)
        
        # Add innovation instructions to system prompt
        if context.innovation_preference in [AdaptiveLevel.INNOVATIVE, AdaptiveLevel.EXPERIMENTAL]:
            innovation_instruction = """
You are an innovative writer who pushes creative boundaries while maintaining quality.
Take calculated creative risks. Challenge conventional wisdom. Find unexpected angles.
Be bold in your approach while serving the reader's needs.
"""
            system_prompt = innovation_instruction + "\n\n" + system_prompt
        
        # CRITICAL: Add template enforcement to system prompt
        template_id = state.get("template", "")
        if template_id:
            template_enforcement = f"""
CRITICAL TEMPLATE ENFORCEMENT:
You are generating content for template: {template_id}
You MUST follow the exact structure and format specified in the user prompt.
Do not deviate from the required sections, word counts, or formatting.
This is not a blog post - follow the specific template requirements exactly.
"""
            system_prompt = template_enforcement + "\n\n" + system_prompt
        
        # Generate content
        model = get_model("writer")
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": enhanced_prompt}
            ],
            temperature=self._calculate_temperature(context.innovation_preference),
        )
        
        generated_content = response.choices[0].message.content.strip()
        
        # Create rich metadata
        metadata = {
            "topic": context.topic,
            "audience": context.audience,
            "platform": context.platform,
            "intent": context.intent,
            "complexity_level": context.complexity_level,
            "innovation_level": context.innovation_preference.value,
            "writing_mode": strategy.mode.value,
            "structure_pattern": strategy.structure_pattern,
            "experimental_techniques": strategy.experimental_techniques,
            "tone_adaptations": strategy.tone_adaptation,
            "generation_timestamp": datetime.now().isoformat(),
            "word_count": len(generated_content.split()),
            "model_used": model,
            "template_used": state.get("template", "none")
        }
        
        # Store for future learning (async)
        self._record_generation_attempt(context, strategy, metadata)
        
        return {**state, 
            "draft": generated_content,
            "metadata": metadata,
            "innovation_report": {
                "techniques_used": strategy.experimental_techniques,
                "innovation_level": context.innovation_preference.value,
                "creative_risk_score": len(strategy.experimental_techniques) * 0.2
            }
        }
    
    def _calculate_temperature(self, innovation_level: AdaptiveLevel) -> float:
        """Calculate model temperature based on innovation preference"""
        temp_map = {
            AdaptiveLevel.CONSERVATIVE: 0.3,
            AdaptiveLevel.BALANCED: 0.5,
            AdaptiveLevel.INNOVATIVE: 0.7,
            AdaptiveLevel.EXPERIMENTAL: 0.9
        }
        return temp_map.get(innovation_level, 0.5)
    
    def _record_generation_attempt(self, context: WritingContext, strategy: WritingStrategy, metadata: Dict):
        """Record generation attempt for future learning"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "context": {
                "topic_category": self._categorize_topic(context.topic),
                "audience": context.audience,
                "intent": context.intent,
                "complexity": context.complexity_level,
                "platform": context.platform
            },
            "strategy": {
                "mode": strategy.mode.value,
                "structure": strategy.structure_pattern,
                "techniques": strategy.experimental_techniques
            },
            "metadata": metadata
        }
        
        # Add to experiments log
        self.innovation_experiments.append(record)
        
        # Keep only recent experiments (last 1000)
        if len(self.innovation_experiments) > 1000:
            self.innovation_experiments = self.innovation_experiments[-1000:]
            
        # Save asynchronously
        try:
            self._save_memory(self.innovation_experiments, "experiments.json")
        except Exception as e:
            print(f"Warning: Could not save experiment data: {e}")
    
    def provide_feedback(self, generation_id: str, success_score: float, feedback: str = ""):
        """Learn from feedback to improve future generations"""
        # Find the generation in experiments
        for exp in self.innovation_experiments:
            if exp.get("metadata", {}).get("generation_id") == generation_id:
                exp["success_score"] = success_score
                exp["feedback"] = feedback
                
                # Move to success or failure patterns
                if success_score >= 0.7:
                    self.success_patterns.append(exp)
                    self._save_memory(self.success_patterns, "success_patterns.json")
                elif success_score <= 0.3:
                    self.failure_patterns.append(exp)
                    self._save_memory(self.failure_patterns, "failure_patterns.json")
                break


# Export both the class and the legacy function for compatibility
innovative_writer_agent = InnovativeWriterAgent()

# Legacy compatibility - wrapped in the new system
def _legacy_writer_fn(state: dict) -> dict:
    """Legacy wrapper for backward compatibility"""
    return innovative_writer_agent.generate_adaptive_content(state)

# Exports
WriterAgent = InnovativeWriterAgent  # Class export
writer = RunnableLambda(_legacy_writer_fn)  # Function export