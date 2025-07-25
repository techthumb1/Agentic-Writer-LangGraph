# File: langgraph_app/universal_style_enhancer.py
# Universal system that enhances ALL your existing style profiles with enforcement

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)

class UniversalStyleEnhancer:
    """Enhances ANY existing style profile with strict enforcement rules"""
    
    def __init__(self):
        self.style_cache = {}
        self.enhancement_rules = self._load_enhancement_rules()
    
    def _load_enhancement_rules(self) -> Dict[str, Any]:
        """Define enhancement rules for different style categories"""
        return {
            'academic': {
                'forbidden_patterns': [
                    'hey there', 'hi there', 'hello there', 'greetings', 'what\'s up',
                    'let\'s dive in', 'let\'s explore', 'buckle up', 'hang tight',
                    'awesome', 'cool', 'neat', 'sweet', 'amazing', 'incredible',
                    'trust me', 'believe me', 'you know', 'basically', 'so,', 'well,'
                ],
                'required_openings': [
                    'This analysis examines', 'This study investigates', 'This research explores',
                    'Contemporary literature suggests', 'Recent developments in',
                    'The present investigation', 'This paper argues that'
                ],
                'required_elements': [
                    'clear thesis statement', 'evidence-based arguments', 'scholarly tone',
                    'analytical depth', 'methodological rigor'
                ],
                'writing_style': {
                    'tone': 'formal', 'voice': 'authoritative', 'formality': 'high',
                    'technical_level': 'advanced', 'objectivity': 'high'
                }
            },
            'technical': {
                'forbidden_patterns': [
                    'hey there', 'what\'s up', 'awesome sauce', 'super cool',
                    'mind-blowing', 'crazy good', 'totally', 'really really'
                ],
                'required_openings': [
                    'This technical analysis', 'The implementation of', 'Technical specifications for',
                    'The following methodology', 'System architecture for'
                ],
                'required_elements': [
                    'technical precision', 'implementation details', 'best practices',
                    'code examples', 'troubleshooting guidance'
                ],
                'writing_style': {
                    'tone': 'analytical', 'voice': 'expert', 'formality': 'moderate',
                    'technical_level': 'expert', 'precision': 'high'
                }
            },
            'business': {
                'forbidden_patterns': [
                    'hey there', 'what\'s up', 'awesome', 'super', 'totally',
                    'really really', 'amazing stuff', 'cool beans'
                ],
                'required_openings': [
                    'This strategic analysis', 'Business implications of', 'Market research indicates',
                    'The competitive landscape', 'Strategic considerations for'
                ],
                'required_elements': [
                    'strategic insights', 'actionable recommendations', 'market analysis',
                    'competitive positioning', 'ROI considerations'
                ],
                'writing_style': {
                    'tone': 'professional', 'voice': 'confident', 'formality': 'high',
                    'technical_level': 'moderate', 'authority': 'high'
                }
            },
            'storytelling': {
                'forbidden_patterns': [
                    'in conclusion', 'to summarize', 'as we can see', 'obviously',
                    'it\'s clear that', 'needless to say'
                ],
                'required_openings': [
                    'Picture this', 'Imagine a world where', 'The story begins',
                    'Consider the journey of', 'In the landscape of'
                ],
                'required_elements': [
                    'narrative arc', 'compelling characters', 'emotional connection',
                    'vivid imagery', 'relatable examples'
                ],
                'writing_style': {
                    'tone': 'engaging', 'voice': 'narrative', 'formality': 'moderate',
                    'technical_level': 'accessible', 'emotion': 'high'
                }
            },
            'educational': {
                'forbidden_patterns': [
                    'hey there', 'what\'s up', 'super duper', 'mega cool',
                    'totally awesome', 'crazy amazing'
                ],
                'required_openings': [
                    'Understanding', 'Learning about', 'The concept of', 'To grasp',
                    'This explanation covers', 'Breaking down'
                ],
                'required_elements': [
                    'clear explanations', 'step-by-step guidance', 'practical examples',
                    'learning objectives', 'knowledge checks'
                ],
                'writing_style': {
                    'tone': 'instructional', 'voice': 'helpful', 'formality': 'moderate',
                    'technical_level': 'appropriate', 'clarity': 'high'
                }
            }
        }
    
    def detect_style_category(self, profile: Dict[str, Any]) -> str:
        """Automatically detect the style category from existing profile"""
        
        # Check explicit category
        if 'category' in profile:
            category = profile['category'].lower()
            if category in self.enhancement_rules:
                return category
        
        # Check profile ID/name for keywords
        profile_id = profile.get('id', '').lower()
        profile_name = profile.get('name', '').lower()
        combined_text = f"{profile_id} {profile_name}".lower()
        
        # Academic keywords
        if any(keyword in combined_text for keyword in ['phd', 'academic', 'research', 'scholarly', 'literature']):
            return 'academic'
        
        # Technical keywords  
        elif any(keyword in combined_text for keyword in ['technical', 'code', 'implementation', 'system', 'engineering']):
            return 'technical'
        
        # Business keywords
        elif any(keyword in combined_text for keyword in ['business', 'market', 'strategy', 'executive', 'professional']):
            return 'business'
        
        # Storytelling keywords
        elif any(keyword in combined_text for keyword in ['story', 'founder', 'narrative', 'journey']):
            return 'storytelling'
        
        # Educational keywords
        elif any(keyword in combined_text for keyword in ['beginner', 'tutorial', 'educational', 'friendly', 'guide']):
            return 'educational'
        
        # Default to business for professional content
        return 'business'
    
    def enhance_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance any existing profile with enforcement rules"""
        
        # Detect category
        category = self.detect_style_category(profile)
        enhancement_rules = self.enhancement_rules[category]
        
        # Create enhanced profile (preserve original structure)
        enhanced = profile.copy()
        
        # Add enforcement elements
        enhanced.update({
            'writing_style': {
                **enhanced.get('writing_style', {}),
                **enhancement_rules['writing_style']
            },
            'forbidden_patterns': enhancement_rules['forbidden_patterns'],
            'required_opening_patterns': enhancement_rules['required_openings'],
            'required_elements': enhancement_rules['required_elements'],
            'enforcement_category': category,
            'enhanced_version': True
        })
        
        # Enhance system prompt with enforcement
        original_prompt = enhanced.get('system_prompt', '')
        enhanced_prompt = self._create_enhanced_system_prompt(original_prompt, enhancement_rules, category)
        enhanced['system_prompt'] = enhanced_prompt
        
        # Add quality requirements
        enhanced['quality_requirements'] = {
            'style_consistency': 95,
            'pattern_compliance': 100,
            'opening_compliance': 90,
            'element_inclusion': 85
        }
        
        # Update metadata
        if 'metadata' not in enhanced:
            enhanced['metadata'] = {}
        
        enhanced['metadata'].update({
            'enhanced_date': '2025-07-18',
            'enhancement_version': '2.0.0',
            'enforcement_active': True,
            'detected_category': category
        })
        
        return enhanced
    
    def _create_enhanced_system_prompt(self, original: str, rules: Dict[str, Any], category: str) -> str:
        """Create enhanced system prompt with enforcement"""
        
        enforcement_prompt = f"""
CRITICAL STYLE ENFORCEMENT ({category.upper()}):

ABSOLUTELY FORBIDDEN - NEVER USE:
{chr(10).join(f'- "{pattern}"' for pattern in rules['forbidden_patterns'])}

REQUIRED OPENING PATTERNS - MUST START WITH ONE OF:
{chr(10).join(f'- "{pattern}..."' for pattern in rules['required_openings'])}

MANDATORY ELEMENTS TO INCLUDE:
{chr(10).join(f'- {element}' for element in rules['required_elements'])}

WRITING STYLE REQUIREMENTS:
{chr(10).join(f'- {key.replace("_", " ").title()}: {value}' for key, value in rules['writing_style'].items())}

VIOLATION WARNING: Content using forbidden patterns or lacking required elements will be rejected.

{original}
"""
        return enforcement_prompt.strip()
    
    def load_enhanced_profile(self, profile_name: str) -> Dict[str, Any]:
        """Load and enhance any existing profile on-the-fly"""
        
        if profile_name in self.style_cache:
            return self.style_cache[profile_name]
        
        # Find and load original profile
        original_profile = self._load_original_profile(profile_name)
        if not original_profile:
            return self._create_fallback_profile(profile_name)
        
        # Enhance the profile
        enhanced_profile = self.enhance_profile(original_profile)
        
        # Cache for future use
        self.style_cache[profile_name] = enhanced_profile
        
        logger.info(f"Enhanced style profile '{profile_name}' (category: {enhanced_profile.get('enforcement_category')})")
        
        return enhanced_profile
    
    def _load_original_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Load original profile from your existing files"""
        
        style_paths = [
            Path(f"data/style_profiles/{profile_name}.yaml"),
            Path(f"style_profile/{profile_name}.yaml"),
            Path(f"langgraph_app/data/style_profiles/{profile_name}.yaml")
        ]
        
        for path in style_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return yaml.safe_load(f)
                except Exception as e:
                    logger.error(f"Error loading {path}: {e}")
        
        logger.warning(f"Style profile not found: {profile_name}")
        return None
    
    def _create_fallback_profile(self, profile_name: str) -> Dict[str, Any]:
        """Create fallback profile for unknown profiles"""
        
        # Detect category from name
        category = 'academic' if 'phd' in profile_name.lower() else 'business'
        rules = self.enhancement_rules[category]
        
        return {
            'id': profile_name,
            'name': profile_name.replace('_', ' ').title(),
            'description': f'Auto-generated {category} profile',
            'category': category,
            'writing_style': rules['writing_style'],
            'forbidden_patterns': rules['forbidden_patterns'],
            'required_opening_patterns': rules['required_openings'],
            'required_elements': rules['required_elements'],
            'system_prompt': self._create_enhanced_system_prompt('', rules, category),
            'enhanced_version': True,
            'fallback': True
        }
    
    def validate_content(self, content: str, profile_name: str) -> Dict[str, Any]:
        """Validate content against enhanced profile"""
        
        profile = self.load_enhanced_profile(profile_name)
        violations = []
        suggestions = []
        
        content_lower = content.lower()
        
        # Check forbidden patterns
        forbidden = profile.get('forbidden_patterns', [])
        for pattern in forbidden:
            if pattern.lower() in content_lower:
                violations.append(f"Forbidden pattern: '{pattern}'")
                suggestions.append(f"Remove or rephrase '{pattern}'")
        
        # Check opening requirements
        required_openings = profile.get('required_opening_patterns', [])
        if required_openings and content:
            opening = content.split('.')[0].lower()
            has_valid_opening = any(
                opening.strip().startswith(pattern.lower()) 
                for pattern in required_openings
            )
            
            if not has_valid_opening:
                violations.append("Does not start with required opening pattern")
                suggestions.append(f"Start with one of: {', '.join(required_openings[:3])}")
        
        return {
            'is_valid': len(violations) == 0,
            'violations': violations,
            'suggestions': suggestions,
            'compliance_score': max(0, 100 - len(violations) * 15),
            'profile_category': profile.get('enforcement_category', 'unknown')
        }
    
    def fix_content(self, content: str, profile_name: str) -> str:
        """Auto-fix content based on profile requirements"""
        
        profile = self.load_enhanced_profile(profile_name)
        fixed_content = content
        
        # Fix forbidden patterns with category-appropriate replacements
        category = profile.get('enforcement_category', 'business')
        replacements = self._get_replacement_patterns(category)
        
        for old, new in replacements.items():
            fixed_content = re.sub(
                re.escape(old), new, fixed_content, flags=re.IGNORECASE
            )
        
        # Fix opening if needed
        required_openings = profile.get('required_opening_patterns', [])
        if required_openings and fixed_content:
            first_sentence = fixed_content.split('.')[0]
            
            # Check if opening needs fixing
            if any(casual in first_sentence.lower() for casual in ['hey', 'hi', 'hello', 'greetings']):
                # Replace with appropriate opening
                topic = self._extract_topic(fixed_content)
                new_opening = f"{required_openings[0]} {topic}"
                
                sentences = fixed_content.split('.')
                sentences[0] = new_opening
                fixed_content = '.'.join(sentences)
        
        return fixed_content
    
    def _get_replacement_patterns(self, category: str) -> Dict[str, str]:
        """Get category-appropriate replacement patterns"""
        
        replacements = {
            'academic': {
                'hey there': 'This analysis examines',
                'hi there': 'This study investigates',
                'let\'s dive in': 'We proceed to examine',
                'awesome': 'significant',
                'cool': 'notable',
                'amazing': 'remarkable'
            },
            'technical': {
                'hey there': 'This technical guide covers',
                'awesome': 'effective',
                'cool': 'efficient',
                'let\'s explore': 'This analysis examines'
            },
            'business': {
                'hey there': 'This analysis presents',
                'awesome': 'excellent',
                'cool': 'effective',
                'amazing': 'outstanding'
            },
            'storytelling': {
                'hey there': 'Picture this',
                'in conclusion': 'As the story unfolds',
                'awesome': 'remarkable',
                'cool': 'fascinating'
            },
            'educational': {
                'hey there': 'Understanding',
                'awesome': 'excellent',
                'cool': 'effective',
                'amazing': 'remarkable'
            }
        }
        
        return replacements.get(category, replacements['business'])
    
    def _extract_topic(self, content: str) -> str:
        """Extract topic from content for better opening generation"""
        
        # Simple topic extraction - look for key nouns in first few sentences
        first_paragraph = content.split('\n\n')[0] if content else ""
        words = first_paragraph.split()[:50]  # First 50 words
        
        # Look for capitalized words that might be topics
        potential_topics = [word for word in words if word[0].isupper() and len(word) > 3]
        
        if potential_topics:
            return f"the role of {potential_topics[0].lower()}"
        else:
            return "the subject matter"

# Integration class for your existing system
class StyleProfileManager:
    """Drop-in replacement for your existing style profile loader"""
    
    def __init__(self):
        self.enhancer = UniversalStyleEnhancer()
    
    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """Get enhanced profile (drop-in replacement for existing method)"""
        return self.enhancer.load_enhanced_profile(profile_name)
    
    def validate_content(self, content: str, profile_name: str) -> Dict[str, Any]:
        """Validate content against profile"""
        return self.enhancer.validate_content(content, profile_name)
    
    def fix_content(self, content: str, profile_name: str) -> str:
        """Fix content violations"""
        return self.enhancer.fix_content(content, profile_name)

# Export for easy integration
__all__ = ['UniversalStyleEnhancer', 'StyleProfileManager']