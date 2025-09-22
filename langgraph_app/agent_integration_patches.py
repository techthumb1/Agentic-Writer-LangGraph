# File: langgraph_app/agent_integration_patches.py
# Refactored integration patches for unified coordination
# Purpose: Apply coordination to all agents with minimal duplication
# RELEVANT FILES: unified_agent_coordination.py, enhanced_*_integrated.py

from langgraph_app.unified_agent_coordination import get_coordinated_context

class AgentCoordinationMixin:
    """Common coordination methods for all agents"""
    
    def get_coordination_context(self, state, agent_type):
        """Get unified coordination context"""
        return get_coordinated_context(state, agent_type)
    
    def apply_template_rules(self, content: str, coordination_context: dict) -> str:
        """Apply template-specific rules"""
        template_type = coordination_context['template_config'].get('template_type')
        coordination_rules = coordination_context.get('coordination_rules', {})
        
        if template_type == 'venture_capital_pitch':
            if coordination_rules.get('financial_emphasis'):
                content = self._emphasize_metrics(content)
            if coordination_rules.get('investor_language'):
                content = self._enhance_investor_language(content)
                
        elif template_type == 'business_proposal':
            if coordination_rules.get('roi_emphasis'):
                content = self._emphasize_roi(content)
            if coordination_rules.get('executive_focus'):
                content = self._ensure_executive_summary(content)
                
        elif template_type == 'technical_documentation':
            if coordination_rules.get('implementation_focus'):
                content = self._ensure_implementation_guide(content)
                
        return content
    
    def _emphasize_metrics(self, content: str) -> str:
        import re
        content = re.sub(r'(\$[\d,]+[MBK]?)', r'**\1**', content)
        content = re.sub(r'(\d+%)', r'**\1**', content)
        return content
    
    def _enhance_investor_language(self, content: str) -> str:
        replacements = {
            'money': 'capital', 'customers': 'market traction',
            'sales': 'revenue', 'profit': 'returns'
        }
        for old, new in replacements.items():
            content = content.replace(old, new)
        return content
    
    def _emphasize_roi(self, content: str) -> str:
        import re
        content = re.sub(r'(ROI|Return on Investment)', r'**\1**', content, flags=re.IGNORECASE)
        return content
    
    def _ensure_executive_summary(self, content: str) -> str:
        if not content.startswith('## Executive Summary'):
            content = '## Executive Summary\n\n[Executive overview]\n\n' + content
        return content
    
    def _ensure_implementation_guide(self, content: str) -> str:
        if 'implementation' not in content.lower():
            content += '\n\n## Implementation Guide\n\n[Implementation details]'
        return content

# Agent-specific patches
def patch_researcher():
    """Researcher coordination integration"""
    return '''
    # Add to execute() method after template_config extraction:
    coordination_context = self.get_coordination_context(state, self.agent_type)
    research_priorities = self._get_coordinated_research_priorities(
        coordination_context, planning, spec, instructions
    )
    '''

def patch_writer():
    """Writer coordination integration"""
    return '''
    # Add to execute() method:
    coordination_context = self.get_coordination_context(state, self.agent_type)
    content = self.apply_template_rules(content, coordination_context)
    content = self._apply_style_coordination(content, coordination_context)
    '''

def patch_editor():
    """Editor coordination integration"""
    return '''
    # Add to execute() method:
    coordination_context = self.get_coordination_context(state, self.agent_type)
    content = self._validate_template_structure(content, coordination_context)
    content = self._enforce_style_compliance(content, coordination_context)
    '''

def patch_formatter():
    """Formatter coordination integration"""
    return '''
    # Add to execute() method:
    coordination_context = self.get_coordination_context(state, self.agent_type)
    content = self.apply_template_rules(content, coordination_context)
    content = self._apply_coordinated_formatting(content, coordination_context)
    '''

def patch_seo_agent():
    """SEO agent coordination integration"""
    return '''
    # Add to execute() method:
    coordination_context = self.get_coordination_context(state, self.agent_type)
    content = self._optimize_template_keywords(content, coordination_context)
    '''

def patch_code_agent():
    """Code agent coordination integration"""
    return '''
    # Add to execute() method:
    coordination_context = self.get_coordination_context(state, self.agent_type)
    if coordination_context.get('coordination_rules', {}).get('code_examples'):
        content = self._add_template_specific_code(content, coordination_context)
    '''

def patch_image_agent():
    """Image agent coordination integration"""
    return '''
    # Add to execute() method:
    coordination_context = self.get_coordination_context(state, self.agent_type)
    image_result = self._generate_template_aligned_image(state, coordination_context)
    '''

def patch_publisher():
    """Publisher coordination integration"""
    return '''
    # Add to execute() method:
    coordination_context = self.get_coordination_context(state, self.agent_type)
    final_content = self._apply_publication_standards(content, coordination_context)
    final_content = self._validate_cross_agent_consistency(final_content, coordination_context)
    '''

# Core method additions for each agent
AGENT_CORE_METHODS = {
    'researcher': '''
    def _get_coordinated_research_priorities(self, coordination_context, planning, spec, instructions):
        priorities = []
        
        # Template-specific priorities
        if coordination_context.get('vc_research_priorities'):
            priorities.extend(coordination_context['vc_research_priorities'])
        elif coordination_context.get('business_research_priorities'):
            priorities.extend(coordination_context['business_research_priorities'])
        elif coordination_context.get('technical_research_priorities'):
            priorities.extend(coordination_context['technical_research_priorities'])
        
        # Style-driven focus
        audience_research = coordination_context.get('audience_research_needs', {})
        if audience_research:
            priorities.extend(audience_research.get('focus_areas', []))
        
        return list(dict.fromkeys(priorities))[:8]  # Remove duplicates, limit to 8
    ''',
    
    'editor': '''
    def _validate_template_structure(self, content, coordination_context):
        template_requirements = coordination_context.get('template_style_requirements', {})
        section_order = template_requirements.get('section_order', [])
        
        if section_order:
            content_lower = content.lower()
            for section in section_order:
                if section.lower() not in content_lower:
                    content += f"\\n\\n## {section}\\n\\n[{section} content needed]"
        
        return content
    
    def _enforce_style_compliance(self, content, coordination_context):
        style_config = coordination_context.get('style_config', {})
        forbidden_patterns = style_config.get('forbidden_patterns', [])
        
        for pattern in forbidden_patterns:
            if pattern in content:
                content = content.replace(pattern, self._get_replacement(pattern))
        
        return content
    
    def _get_replacement(self, pattern):
        replacements = {
            'hey there': 'Note that',
            'awesome': 'excellent',
            'cool': 'noteworthy'
        }
        return replacements.get(pattern.lower(), pattern)
    ''',
    
    'seo_agent': '''
    def _optimize_template_keywords(self, content, coordination_context):
        template_type = coordination_context['template_config'].get('template_type')
        seo_keywords = coordination_context.get('seo_keywords', [])
        
        # Template-specific keywords
        template_keywords = {
            'venture_capital_pitch': ['venture capital', 'startup funding', 'investment opportunity'],
            'business_proposal': ['business proposal', 'ROI analysis', 'strategic planning'],
            'technical_documentation': ['technical documentation', 'implementation guide']
        }
        
        keywords = template_keywords.get(template_type, []) + seo_keywords[:5]
        
        for keyword in keywords:
            if keyword not in content.lower():
                content = self._integrate_keyword_naturally(content, keyword)
        
        return content
    
    def _integrate_keyword_naturally(self, content, keyword):
        paragraphs = content.split('\\n\\n')
        if len(paragraphs) > 1:
            paragraphs[1] = f"When considering {keyword}, " + paragraphs[1].lower()
            content = '\\n\\n'.join(paragraphs)
        return content
    ''',
    
    'code_agent': '''
    def _add_template_specific_code(self, content, coordination_context):
        template_type = coordination_context['template_config'].get('template_type')
        
        if template_type == 'technical_documentation' and '```' not in content:
            content += """
\\n\\n## Code Examples

```python
# Implementation example
def process_data(input_data):
    \"\"\"Process data according to specifications\"\"\"
    try:
        result = []
        for item in input_data:
            processed = item * 2  # Example processing
            result.append(processed)
        return result
    except Exception as e:
        return f"Error: {e}"
```"""
        
        elif template_type == 'api_documentation_template':
            content += """
\\n\\n## API Usage

```javascript
// Basic API usage
const response = await fetch('/api/endpoint', {
    method: 'GET',
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN',
        'Content-Type': 'application/json'
    }
});
const data = await response.json();
```"""
        
        return content
    ''',
    
    'image_agent': '''
    def _generate_template_aligned_image(self, state, coordination_context):
        template_type = coordination_context['template_config'].get('template_type')
        topic = getattr(state.content_spec, 'topic', 'Professional Content')
        
        prompts = {
            'venture_capital_pitch': f"Professional VC pitch slide for {topic}. Corporate design with growth charts.",
            'business_proposal': f"Executive business proposal for {topic}. Professional with ROI visualizations.",
            'technical_documentation': f"Technical diagram for {topic}. Clean technical illustration."
        }
        
        prompt = prompts.get(template_type, f"Professional illustration for {topic}")
        
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                quality="hd",
                n=1
            )
            
            if response and response.data:
                return {
                    "cover_image_url": response.data[0].url,
                    "image_metadata": {"generation_successful": True, "template_aligned": True}
                }
        except Exception as e:
            pass
        
        return {
            "cover_image_url": "https://via.placeholder.com/1200x800/4A90E2/FFFFFF?text=Professional+Content",
            "image_metadata": {"generation_successful": False, "fallback_used": True}
        }
    ''',
    
    'publisher': '''
    def _apply_publication_standards(self, content, coordination_context):
        template_type = coordination_context['template_config'].get('template_type')
        
        footers = {
            'venture_capital_pitch': "\\n\\n---\\n**Investment Opportunity Summary**\\nCompelling opportunity with validated traction.",
            'business_proposal': "\\n\\n---\\n**Next Steps**\\nStrategic opportunity for measurable impact.",
            'technical_documentation': "\\n\\n---\\n**Support**\\nFor technical assistance, contact our team."
        }
        
        content += footers.get(template_type, "")
        return self.apply_template_rules(content, coordination_context)
    
    def _validate_cross_agent_consistency(self, content, coordination_context):
        cross_agent = coordination_context.get('cross_agent_context', {})
        issues = []
        
        # Check key messages
        planning = cross_agent.get('planning', {})
        if planning:
            key_messages = planning.get('key_messages', [])
            for message in key_messages:
                if message.lower() not in content.lower():
                    issues.append(f"Missing: {message}")
        
        # Check research integration
        research = cross_agent.get('research', {})
        if research and 'research' not in content.lower() and 'data' not in content.lower():
            issues.append("Research not integrated")
        
        if issues:
            content += f"\\n\\n<!-- Issues: {'; '.join(issues)} -->"
        
        return content
    '''
}

def get_agent_patches():
    """Get all agent patches"""
    return {
        'enhanced_researcher_integrated.py': patch_researcher(),
        'enhanced_writer_integrated.py': patch_writer(),
        'enhanced_editor_integrated.py': patch_editor(),
        'enhanced_formatter_integrated.py': patch_formatter(),
        'enhanced_seo_agent_integrated.py': patch_seo_agent(),
        'enhanced_code_agent_integrated.py': patch_code_agent(),
        'enhanced_image_agent_integrated.py': patch_image_agent(),
        'enhanced_publisher_integrated.py': patch_publisher()
    }

def get_agent_methods():
    """Get core methods for each agent"""
    return AGENT_CORE_METHODS

# Integration instructions
INTEGRATION_STEPS = """
1. Add AgentCoordinationMixin to each agent class
2. Apply agent-specific patches from get_agent_patches()
3. Add core methods from get_agent_methods()
4. Import: from langgraph_app.unified_agent_coordination import get_coordinated_context
5. Test coordination flow end-to-end
"""