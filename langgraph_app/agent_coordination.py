# File: langgraph_app/agent_coordination.py
# CRITICAL FIX: Proper agent coordination to eliminate generic content

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class AgentContext:
    """Rich context passed between agents"""
    topic: str
    style_profile: str
    target_audience: str
    content_type: str
    research_insights: List[str]
    writing_requirements: Dict[str, Any]
    previous_agent_outputs: Dict[str, Any]
    quality_targets: Dict[str, float]

class AgentCoordinator:
    """Coordinates agents to build on each other's work"""
    
    def __init__(self):
        self.agent_chain = [
            'planner', 'researcher', 'writer', 'editor', 'seo_agent', 'formatter'
        ]
        self.context_builders = {
            'planner': self._build_planner_context,
            'researcher': self._build_researcher_context,
            'writer': self._build_writer_context,
            'editor': self._build_editor_context,
            'seo_agent': self._build_seo_context,
            'formatter': self._build_formatter_context
        }
    
    def create_agent_context(self, state: Dict[str, Any], agent_name: str) -> AgentContext:
        """Create rich context for specific agent"""
        base_context = AgentContext(
            topic=state.get('topic', 'Untitled Content'),
            style_profile=state.get('style_profile', 'professional'),
            target_audience=state.get('audience', 'general'),
            content_type=state.get('content_type', 'article'),
            research_insights=[],
            writing_requirements={},
            previous_agent_outputs={},
            quality_targets={'originality': 0.8, 'coherence': 0.9, 'style_adherence': 0.95}
        )
        
        # Use specific context builder
        if agent_name in self.context_builders:
            return self.context_builders[agent_name](state, base_context)
        
        return base_context
    
    def _build_planner_context(self, state: Dict[str, Any], context: AgentContext) -> AgentContext:
        """Build context for planner agent"""
        context.writing_requirements = {
            'avoid_generic_openings': True,
            'require_unique_angle': True,
            'depth_level': state.get('depth_level', 'comprehensive'),
            'structure_type': self._determine_structure_type(context.style_profile),
            'innovation_factor': 0.8  # High innovation required
        }
        
        # Extract topic-specific requirements
        dynamic_params = state.get('dynamic_parameters', {})
        if 'technical_level' in dynamic_params:
            context.writing_requirements['technical_depth'] = dynamic_params['technical_level']
        
        return context
    
    def _build_researcher_context(self, state: Dict[str, Any], context: AgentContext) -> AgentContext:
        """Build context for researcher agent"""
        # Get planning output
        planning_output = state.get('content_plan', {})
        context.previous_agent_outputs['planner'] = planning_output
        
        # Extract research requirements from plan
        if planning_output:
            context.research_insights = planning_output.get('research_requirements', [])
            context.writing_requirements['focus_areas'] = planning_output.get('focus_areas', [])
            context.writing_requirements['unique_angles'] = planning_output.get('unique_angles', [])
        
        # Set research depth based on style profile
        research_depth = {
            'phd_academic': 'deep',
            'technical_dive': 'expert',
            'business_professional': 'strategic',
            'popular_science': 'accessible'
        }.get(context.style_profile, 'moderate')
        
        context.writing_requirements['research_depth'] = research_depth
        return context
    
    def _build_writer_context(self, state: Dict[str, Any], context: AgentContext) -> AgentContext:
        """Build context for writer agent"""
        # Gather all previous outputs
        context.previous_agent_outputs = {
            'planner': state.get('content_plan', {}),
            'researcher': state.get('research_data', {})
        }
        
        # Extract key insights for writing
        research_data = state.get('research_data', {})
        if research_data:
            context.research_insights = research_data.get('key_insights', [])
            
        # Build comprehensive writing requirements
        content_plan = state.get('content_plan', {})
        context.writing_requirements = {
            'style_profile': context.style_profile,
            'unique_angle': content_plan.get('unique_angle', ''),
            'key_points': content_plan.get('key_points', []),
            'research_backing': context.research_insights,
            'avoid_generic_phrases': self._get_generic_phrases(context.style_profile),
            'required_elements': self._get_required_elements(context.style_profile),
            'innovation_level': 'high',
            'originality_check': True
        }
        
        return context
    
    def _build_editor_context(self, state: Dict[str, Any], context: AgentContext) -> AgentContext:
        """Build context for editor agent"""
        context.previous_agent_outputs = {
            'planner': state.get('content_plan', {}),
            'researcher': state.get('research_data', {}),
            'writer': {'draft': state.get('draft', '')}
        }
        
        # Set editing requirements based on style profile
        editing_requirements = {
            'style_consistency': True,
            'eliminate_generic_content': True,
            'enhance_uniqueness': True,
            'improve_flow': True,
            'target_style': context.style_profile
        }
        
        # Add specific requirements for academic style
        if context.style_profile == 'phd_academic':
            editing_requirements.update({
                'ensure_thesis_clarity': True,
                'verify_evidence_support': True,
                'check_argumentation_flow': True,
                'eliminate_casual_language': True
            })
        
        context.writing_requirements = editing_requirements
        return context
    
    def _build_seo_context(self, state: Dict[str, Any], context: AgentContext) -> AgentContext:
        """Build context for SEO agent"""
        context.previous_agent_outputs = {
            'edited_content': state.get('edited_draft', ''),
            'research_keywords': state.get('research_data', {}).get('keywords', [])
        }
        
        context.writing_requirements = {
            'maintain_style_profile': context.style_profile,
            'preserve_uniqueness': True,
            'enhance_discoverability': True
        }
        
        return context
    
    def _build_formatter_context(self, state: Dict[str, Any], context: AgentContext) -> AgentContext:
        """Build context for formatter agent"""
        context.previous_agent_outputs = {
            'final_content': state.get('seo_optimized_content', state.get('edited_draft', '')),
            'seo_metadata': state.get('seo_metadata', {})
        }
        
        return context
    
    def _determine_structure_type(self, style_profile: str) -> str:
        """Determine content structure based on style profile"""
        structure_map = {
            'phd_academic': 'research_paper',
            'technical_dive': 'technical_analysis',
            'business_professional': 'executive_brief',
            'popular_science': 'narrative_explanation',
            'startup_storytelling': 'problem_solution_story'
        }
        return structure_map.get(style_profile, 'standard_article')
    
    def _get_generic_phrases(self, style_profile: str) -> List[str]:
        """Get phrases to avoid for specific style profiles"""
        generic_phrases = {
            'phd_academic': [
                'hey there', 'hi there', 'what\'s up', 'greetings',
                'let\'s dive in', 'buckle up', 'hang tight',
                'awesome', 'cool', 'neat', 'sweet',
                'trust me', 'believe me', 'take my word'
            ],
            'technical_dive': [
                'hey there', 'what\'s up', 'awesome sauce',
                'super cool', 'mind-blowing', 'crazy good'
            ],
            'business_professional': [
                'hey there', 'what\'s up', 'awesome',
                'super', 'totally', 'really really'
            ]
        }
        
        return generic_phrases.get(style_profile, generic_phrases['phd_academic'])
    
    def _get_required_elements(self, style_profile: str) -> List[str]:
        """Get required elements for specific style profiles"""
        required_elements = {
            'phd_academic': [
                'clear thesis statement',
                'evidence-based arguments',
                'logical progression',
                'scholarly tone',
                'analytical depth'
            ],
            'technical_dive': [
                'technical precision',
                'practical examples',
                'implementation details',
                'best practices',
                'troubleshooting insights'
            ],
            'business_professional': [
                'executive summary mindset',
                'strategic implications',
                'actionable insights',
                'professional tone',
                'clear recommendations'
            ]
        }
        
        return required_elements.get(style_profile, required_elements['phd_academic'])
    
    def create_enhanced_prompt(self, agent_name: str, context: AgentContext, base_prompt: str) -> str:
        """Create enhanced prompt with coordination context"""
        
        coordination_prompt = f"""
AGENT COORDINATION CONTEXT:
You are the {agent_name.upper()} agent in a sophisticated multi-agent content creation system.

TOPIC: {context.topic}
STYLE PROFILE: {context.style_profile}
TARGET AUDIENCE: {context.target_audience}

PREVIOUS AGENT OUTPUTS:
{self._format_previous_outputs(context.previous_agent_outputs)}

CRITICAL REQUIREMENTS:
{self._format_requirements(context.writing_requirements)}

QUALITY TARGETS:
- Originality: {context.quality_targets.get('originality', 0.8)*100}%
- Coherence: {context.quality_targets.get('coherence', 0.9)*100}%
- Style Adherence: {context.quality_targets.get('style_adherence', 0.95)*100}%

BUILD UPON PREVIOUS WORK: Your output should enhance and build upon what previous agents have created, not ignore or contradict it.

ELIMINATE GENERIC CONTENT: Avoid cliché openings, overused transitions, and generic phrases. Create unique, engaging content that matches the {context.style_profile} style exactly.

---

{base_prompt}
"""
        
        return coordination_prompt
    
    def _format_previous_outputs(self, outputs: Dict[str, Any]) -> str:
        """Format previous agent outputs for context"""
        formatted = []
        for agent, output in outputs.items():
            if isinstance(output, dict):
                summary = self._summarize_output(output)
                formatted.append(f"{agent.upper()}: {summary}")
            else:
                formatted.append(f"{agent.upper()}: {str(output)[:200]}...")
        
        return '\n'.join(formatted) if formatted else "No previous outputs available"
    
    def _format_requirements(self, requirements: Dict[str, Any]) -> str:
        """Format requirements for prompt"""
        formatted = []
        for key, value in requirements.items():
            if isinstance(value, list):
                formatted.append(f"- {key.replace('_', ' ').title()}: {', '.join(value)}")
            else:
                formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        return '\n'.join(formatted) if formatted else "No specific requirements"
    
    def _summarize_output(self, output: Dict[str, Any]) -> str:
        """Summarize agent output for context"""
        if 'unique_angle' in output:
            return f"Unique angle: {output['unique_angle']}"
        elif 'key_insights' in output:
            insights = output['key_insights'][:3]  # First 3 insights
            return f"Key insights: {'; '.join(insights)}"
        elif 'content_plan' in output:
            return f"Content plan: {output.get('content_plan', {}).get('summary', 'Created')}"
        else:
            return "Output processed successfully"

# Integration function for existing workflow
def enhance_agent_with_coordination(agent_function, agent_name: str):
    """Decorator to enhance agents with coordination"""
    def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
        coordinator = AgentCoordinator()
        
        # Create enhanced context
        context = coordinator.create_agent_context(state, agent_name)
        
        # Add coordination context to state
        state['agent_context'] = context
        state['coordination_prompt'] = coordinator.create_enhanced_prompt(
            agent_name, context, ""
        )
        
        # Run enhanced agent
        result = agent_function(state)
        
        # Log coordination info
        logger.info(f"{agent_name} completed with coordination context")
        
        return result
    
    return wrapper

# Export for use in orchestration
__all__ = ['AgentCoordinator', 'AgentContext', 'enhance_agent_with_coordination']