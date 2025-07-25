# File: langgraph_app/style_patch.py
# SIMPLE PATCH - Just add this file, no changes to existing files needed

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class StyleEnforcementPatch:
    """Simple patch that works with your existing system"""
    
    def __init__(self):
        self.style_rules = {
            # Academic profiles
            'phd_academic': {
                'forbidden': ['hey there', 'hi there', 'greetings', 'let\'s dive in', 'awesome', 'cool'],
                'required_start': ['This analysis examines', 'This study investigates', 'This research explores'],
                'tone': 'formal academic'
            },
            'phd_lit_review': {
                'forbidden': ['hey there', 'hi there', 'greetings', 'let\'s dive in', 'awesome', 'cool'],
                'required_start': ['Contemporary literature suggests', 'Recent scholarship indicates', 'The literature reveals'],
                'tone': 'scholarly review'
            },
            
            # Technical profiles
            'technical_dive': {
                'forbidden': ['hey there', 'awesome sauce', 'super cool', 'mind-blowing'],
                'required_start': ['This technical analysis', 'The implementation of', 'Technical specifications'],
                'tone': 'technical expert'
            },
            'technical_tutor': {
                'forbidden': ['hey there', 'super duper', 'mega cool'],
                'required_start': ['Understanding', 'Learning about', 'This tutorial covers'],
                'tone': 'educational technical'
            },
            
            # Business profiles
            'founder_storytelling': {
                'forbidden': ['hey there', 'what\'s up', 'totally awesome'],
                'required_start': ['Picture this', 'Imagine a world where', 'The journey began'],
                'tone': 'narrative business'
            },
            'startup_trends_brief': {
                'forbidden': ['hey there', 'awesome', 'super'],
                'required_start': ['Market analysis reveals', 'Industry trends indicate', 'The startup landscape'],
                'tone': 'professional analysis'
            },
            
            # Healthcare & Policy
            'ai_in_healthcare': {
                'forbidden': ['hey there', 'awesome', 'cool beans'],
                'required_start': ['Healthcare applications of', 'Medical AI developments', 'Clinical implementations'],
                'tone': 'medical professional'
            },
            'policy_watch': {
                'forbidden': ['hey there', 'totally', 'amazing stuff'],
                'required_start': ['Policy implications of', 'Regulatory frameworks for', 'The policy landscape'],
                'tone': 'policy analysis'
            },
            
            # Educational profiles
            'beginner_friendly': {
                'forbidden': ['super duper', 'mega awesome', 'totally cool'],
                'required_start': ['Let\'s start with', 'First, let\'s understand', 'To begin learning'],
                'tone': 'friendly educational'
            },
            'educational_expert': {
                'forbidden': ['hey there', 'awesome sauce'],
                'required_start': ['Educational research shows', 'Pedagogical approaches to', 'Learning theory suggests'],
                'tone': 'educational authority'
            }
        }
    
    def get_enhanced_prompt(self, profile_name: str, topic: str, base_prompt: str = "") -> str:
        """Create enhanced prompt for any profile"""
        
        rules = self.style_rules.get(profile_name, {
            'forbidden': ['hey there', 'hi there', 'awesome', 'cool'],
            'required_start': ['This analysis examines', 'This discussion covers'],
            'tone': 'professional'
        })
        
        enhanced_prompt = f"""
CRITICAL STYLE REQUIREMENTS FOR {profile_name.upper()}:

TOPIC: {topic}
TONE: {rules['tone']}

ABSOLUTELY FORBIDDEN - DO NOT USE:
{chr(10).join(f'- "{pattern}"' for pattern in rules['forbidden'])}

REQUIRED OPENING - MUST START WITH ONE OF:
{chr(10).join(f'- "{start}..."' for start in rules['required_start'])}

CRITICAL: If you use any forbidden pattern or don't start correctly, the content will be REJECTED.

Write high-quality, original content that matches the {profile_name} style exactly.
Avoid generic explanations and create unique insights about {topic}.

{base_prompt}
"""
        return enhanced_prompt.strip()
    
    def validate_and_fix(self, content: str, profile_name: str) -> tuple[str, list]:
        """Validate content and fix violations"""
        
        rules = self.style_rules.get(profile_name, {})
        violations = []
        fixed_content = content
        
        # Check for forbidden patterns
        content_lower = content.lower()
        for forbidden in rules.get('forbidden', []):
            if forbidden in content_lower:
                violations.append(f"Used forbidden pattern: '{forbidden}'")
                # Simple replacement
                replacements = {
                    'hey there': rules.get('required_start', ['This analysis examines'])[0],
                    'hi there': rules.get('required_start', ['This study investigates'])[0],
                    'awesome': 'significant',
                    'cool': 'notable',
                    'amazing': 'remarkable'
                }
                replacement = replacements.get(forbidden, 'important')
                fixed_content = fixed_content.replace(forbidden, replacement)
                fixed_content = fixed_content.replace(forbidden.title(), replacement.title())
        
        # Check opening
        if content and rules.get('required_start'):
            first_sentence = content.split('.')[0].lower()
            has_good_start = any(
                first_sentence.strip().startswith(start.lower())
                for start in rules['required_start']
            )
            
            if not has_good_start:
                violations.append("Doesn't start with required pattern")
                # Fix the opening
                topic = "the subject matter"  # Could extract better
                new_start = f"{rules['required_start'][0]} {topic}"
                sentences = fixed_content.split('.')
                sentences[0] = new_start
                fixed_content = '.'.join(sentences)
        
        return fixed_content, violations

# Simple function to patch your existing writer
def enhance_writer_output(writer_function):
    """Simple decorator to enhance any writer function"""
    
    def enhanced_writer(state: Dict[str, Any]) -> Dict[str, Any]:
        patch = StyleEnforcementPatch()
        
        # Get profile and topic
        profile = state.get('style_profile', 'professional')
        topic = state.get('topic', state.get('parameters', {}).get('topic', 'the topic'))
        
        # Create enhanced prompt
        enhanced_prompt = patch.get_enhanced_prompt(profile, topic)
        
        # Add to state
        original_instructions = state.get('instructions', '')
        state['enhanced_instructions'] = f"{enhanced_prompt}\n\n{original_instructions}"
        
        # Store original prompt method and override
        if hasattr(state, 'prompt'):
            state['original_prompt'] = state['prompt']
            state['prompt'] = enhanced_prompt
        
        # Run original writer
        result = writer_function(state)
        
        # Fix output if needed
        if 'draft' in result:
            fixed_content, violations = patch.validate_and_fix(result['draft'], profile)
            
            if violations:
                logger.warning(f"Fixed style violations in {profile}: {violations}")
                result['draft'] = fixed_content
                result['style_fixes'] = violations
        
        return result
    
    return enhanced_writer

# SIMPLE INTEGRATION FOR YOUR EXISTING SYSTEM
def patch_existing_orchestrator():
    """Patch your existing orchestrator with style enforcement"""
    
    try:
        # Import your existing writer
        from .agents.writer import InnovativeWriterAgent
        
        # Create enhanced version
        original_writer = InnovativeWriterAgent()
        enhanced_generate = enhance_writer_output(original_writer.generate_adaptive_content)
        
        # Replace the method
        original_writer.generate_adaptive_content = enhanced_generate
        
        logger.info("✅ Successfully patched writer with style enforcement")
        return True
        
    except Exception as e:
        logger.error(f"Failed to patch writer: {e}")
        return False

# USAGE EXAMPLE
def create_enhanced_prompt_for_profile(profile_name: str, topic: str) -> str:
    """Quick function to create enhanced prompts"""
    patch = StyleEnforcementPatch()
    return patch.get_enhanced_prompt(profile_name, topic)

# Export everything
__all__ = ['StyleEnforcementPatch', 'enhance_writer_output', 'patch_existing_orchestrator', 'create_enhanced_prompt_for_profile']