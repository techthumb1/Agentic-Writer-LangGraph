# File: langgraph_app/style_enforcement.py
# CRITICAL FIX: Enforces style profiles to eliminate generic content

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class StyleProfileEnforcer:
    """Enforces style profiles with strict validation and correction"""
    
    def __init__(self):
        self.style_cache = {}
        self.violation_patterns = {
            'casual_greeting': [
                'hey there', 'hi there', 'hello there',
                'what\'s up', 'greetings', 'howdy'
            ],
            'weak_transitions': [
                'so,', 'well,', 'now,', 'anyway,', 'moving on'
            ],
            'filler_words': [
                'um,', 'uh,', 'like,', 'you know,', 'basically'
            ]
        }
    
    def load_style_profile(self, profile_name: str) -> Dict[str, Any]:
        """Load and cache style profile"""
        if profile_name in self.style_cache:
            return self.style_cache[profile_name]
        
        try:
            # Find style profile file
            style_paths = [
                Path(f"data/style_profiles/{profile_name}.yaml"),
                Path(f"style_profile/{profile_name}.yaml"),
                Path(f"langgraph_app/data/style_profiles/{profile_name}.yaml")
            ]
            
            for path in style_paths:
                if path.exists():
                    with open(path, 'r') as f:
                        profile = yaml.safe_load(f)
                        self.style_cache[profile_name] = profile
                        return profile
            
            logger.error(f"Style profile not found: {profile_name}")
            return self._get_fallback_profile(profile_name)
            
        except Exception as e:
            logger.error(f"Error loading style profile {profile_name}: {e}")
            return self._get_fallback_profile(profile_name)
    
    def _get_fallback_profile(self, profile_name: str) -> Dict[str, Any]:
        """Provide fallback style profiles for common types"""
        fallbacks = {
            'phd_academic': {
                'writing_style': {
                    'tone': 'formal',
                    'voice': 'authoritative',
                    'formality': 'high',
                    'technical_level': 'advanced'
                },
                'content_structure': {
                    'opening_style': 'thesis_statement',
                    'paragraph_style': 'analytical',
                    'conclusion_style': 'synthesis'
                },
                'language_requirements': {
                    'vocabulary_level': 'advanced',
                    'sentence_complexity': 'complex',
                    'use_jargon': True,
                    'citation_style': 'academic'
                },
                'forbidden_patterns': [
                    'hey there', 'what\'s up', 'greetings', 'howdy',
                    'let\'s dive in', 'buckle up', 'hang tight'
                ],
                'required_elements': [
                    'clear thesis',
                    'evidence-based arguments',
                    'methodological rigor',
                    'scholarly tone'
                ]
            },
            'technical_dive': {
                'writing_style': {
                    'tone': 'analytical',
                    'voice': 'expert',
                    'formality': 'moderate',
                    'technical_level': 'expert'
                },
                'required_elements': [
                    'technical precision',
                    'code examples',
                    'implementation details',
                    'best practices'
                ]
            },
            'business_professional': {
                'writing_style': {
                    'tone': 'professional',
                    'voice': 'confident',
                    'formality': 'high',
                    'technical_level': 'moderate'
                },
                'forbidden_patterns': [
                    'hey there', 'what\'s up', 'awesome', 'cool'
                ]
            }
        }
        
        return fallbacks.get(profile_name, fallbacks['phd_academic'])
    
    def create_style_prompt(self, profile_name: str, content_type: str = "article") -> str:
        """Create a comprehensive style enforcement prompt"""
        profile = self.load_style_profile(profile_name)
        
        # Extract style requirements
        writing_style = profile.get('writing_style', {})
        structure = profile.get('content_structure', {})
        language = profile.get('language_requirements', {})
        forbidden = profile.get('forbidden_patterns', [])
        required = profile.get('required_elements', [])
        
        prompt = f"""
CRITICAL STYLE ENFORCEMENT FOR {profile_name.upper()}:

MANDATORY WRITING STYLE:
- Tone: {writing_style.get('tone', 'professional')}
- Voice: {writing_style.get('voice', 'authoritative')}
- Formality Level: {writing_style.get('formality', 'high')}
- Technical Level: {writing_style.get('technical_level', 'advanced')}

STRUCTURE REQUIREMENTS:
- Opening: {structure.get('opening_style', 'direct thesis statement')}
- Paragraphs: {structure.get('paragraph_style', 'analytical and evidence-based')}
- Transitions: {structure.get('transition_style', 'formal logical connectors')}
- Conclusion: {structure.get('conclusion_style', 'synthesis and implications')}

LANGUAGE REQUIREMENTS:
- Vocabulary: {language.get('vocabulary_level', 'advanced')}
- Sentences: {language.get('sentence_complexity', 'complex and varied')}
- Jargon: {'Use appropriate technical terminology' if language.get('use_jargon') else 'Avoid excessive jargon'}

STRICTLY FORBIDDEN - DO NOT USE:
{chr(10).join(f'- {pattern}' for pattern in forbidden)}

REQUIRED ELEMENTS:
{chr(10).join(f'- {element}' for element in required)}

VIOLATION ALERT: If you use any forbidden patterns or fail to meet style requirements, 
the content will be rejected. Ensure every sentence aligns with the {profile_name} style.
"""
        return prompt.strip()
    
    def validate_content(self, content: str, profile_name: str) -> Dict[str, Any]:
        """Validate content against style profile"""
        profile = self.load_style_profile(profile_name)
        violations = []
        suggestions = []
        
        content_lower = content.lower()
        
        # Check for forbidden patterns
        forbidden_patterns = profile.get('forbidden_patterns', [])
        for pattern in forbidden_patterns:
            if pattern.lower() in content_lower:
                violations.append(f"Forbidden pattern detected: '{pattern}'")
                suggestions.append(f"Remove or rephrase '{pattern}' to match {profile_name} style")
        
        # Check for style violations
        for category, patterns in self.violation_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    violations.append(f"Style violation ({category}): '{pattern}'")
        
        # Check opening
        opening_words = content.split()[:10]
        opening_text = ' '.join(opening_words).lower()
        
        if profile_name == 'phd_academic':
            if any(casual in opening_text for casual in ['hey', 'hi', 'hello', 'greetings']):
                violations.append("Academic content should not start with casual greetings")
                suggestions.append("Start with a clear thesis statement or research context")
        
        return {
            'is_valid': len(violations) == 0,
            'violations': violations,
            'suggestions': suggestions,
            'compliance_score': max(0, 100 - len(violations) * 10)
        }
    
    def fix_content(self, content: str, profile_name: str) -> str:
        """Auto-fix common style violations"""
        profile = self.load_style_profile(profile_name)
        fixed_content = content
        
        # Fix forbidden patterns
        forbidden_patterns = profile.get('forbidden_patterns', [])
        
        replacements = {
            'hey there': 'This analysis examines',
            'hi there': 'This study investigates',
            'greetings': 'This research explores',
            'let\'s dive in': 'We proceed to examine',
            'let\'s explore': 'This investigation considers',
            'so,': 'Therefore,',
            'well,': 'Furthermore,',
            'now,': 'Subsequently,',
        }
        
        for old, new in replacements.items():
            fixed_content = fixed_content.replace(old, new)
            fixed_content = fixed_content.replace(old.title(), new)
        
        # Fix academic openings
        if profile_name == 'phd_academic':
            lines = fixed_content.split('\n')
            if lines and any(casual in lines[0].lower() for casual in ['hey', 'hi', 'hello']):
                # Replace casual opening with academic one
                topic = "the subject matter"  # This should be extracted from context
                lines[0] = f"This analysis examines {topic} through a comprehensive framework."
                fixed_content = '\n'.join(lines)
        
        return fixed_content

# Integration with existing agents
def apply_style_enforcement(agent_function):
    """Decorator to apply style enforcement to agent functions"""
    def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
        # Extract style profile
        style_profile = state.get('style_profile', 'professional')
        
        # Create enforcer
        enforcer = StyleProfileEnforcer()
        
        # Add style prompt to state
        style_prompt = enforcer.create_style_prompt(style_profile)
        state['style_enforcement_prompt'] = style_prompt
        
        # Run original agent
        result = agent_function(state)
        
        # Validate and fix output
        if 'content' in result or 'draft' in result:
            content = result.get('content') or result.get('draft', '')
            
            if content:
                validation = enforcer.validate_content(content, style_profile)
                
                if not validation['is_valid']:
                    logger.warning(f"Style violations detected: {validation['violations']}")
                    fixed_content = enforcer.fix_content(content, style_profile)
                    
                    if 'content' in result:
                        result['content'] = fixed_content
                    if 'draft' in result:
                        result['draft'] = fixed_content
                    
                    result['style_validation'] = validation
        
        return result
    
    return wrapper

# Export for use in agents
__all__ = ['StyleProfileEnforcer', 'apply_style_enforcement']