# File: langgraph_app/unified_agent_coordination.py
# Unified coordination system for template+style awareness across all agents

from typing import Dict, Any, List, Optional
from langgraph_app.core.enriched_content_state import EnrichedContentState, AgentType
import logging

logger = logging.getLogger(__name__)

class UnifiedAgentCoordination:
    """Unified coordination system ensuring all agents use template+style context"""
    
    def __init__(self):
        self.coordination_cache = {}
    
    def get_coordinated_context(self, state: EnrichedContentState, agent_type: AgentType) -> Dict[str, Any]:
        """Get unified template+style context for any agent"""
        
        # Extract template and style configs
        template_config = getattr(state, 'template_config', {}) or {}
        style_config = getattr(state, 'style_config', {}) or {}
        
        # Create coordinated context
        context = {
            'template_config': template_config,
            'style_config': style_config,
            'agent_type': agent_type,
            'coordination_rules': self._get_coordination_rules(template_config, style_config),
            'cross_agent_context': self._build_cross_agent_context(state),
            'template_style_requirements': self._merge_template_style_requirements(template_config, style_config)
        }
        
        # Agent-specific coordination
        if agent_type == AgentType.RESEARCHER:
            context.update(self._get_researcher_coordination(template_config, style_config, state))
        elif agent_type == AgentType.WRITER:
            context.update(self._get_writer_coordination(template_config, style_config, state))
        elif agent_type == AgentType.EDITOR:
            context.update(self._get_editor_coordination(template_config, style_config, state))
        elif agent_type == AgentType.FORMATTER:
            context.update(self._get_formatter_coordination(template_config, style_config, state))
        elif agent_type == AgentType.CODE:
            context.update(self._get_code_coordination(template_config, style_config, state))
        elif agent_type == AgentType.IMAGE:
            context.update(self._get_image_coordination(template_config, style_config, state))
        elif agent_type == AgentType.SEO:
            context.update(self._get_seo_coordination(template_config, style_config, state))
        elif agent_type == AgentType.PLANNER:
            context.update({'planning_coordination': self._get_planner_coordination(template_config, style_config, state)})
        elif agent_type == AgentType.PUBLISHER:
            context.update(self._get_publisher_coordination(template_config, style_config, state))
        
        return context
    
    def _get_coordination_rules(self, template_config: Dict, style_config: Dict) -> Dict[str, Any]:
        """Extract coordination rules from template and style configurations"""
        
        rules = {
            'template_priority': True,  # Template takes precedence over style when conflicting
            'style_enforcement': style_config.get('enforcement_level', 'medium'),
            'template_compliance': template_config.get('compliance_level', 'strict'),
            'cross_agent_consistency': True
        }
        
        # Template-specific coordination rules
        template_type = template_config.get('template_type')
        if template_type == 'venture_capital_pitch':
            rules.update({
                'financial_emphasis': True,
                'traction_focus': True,
                'investor_language': True,
                'metric_prominence': True
            })
        elif template_type == 'business_proposal':
            rules.update({
                'roi_emphasis': True,
                'executive_focus': True,
                'implementation_detail': True,
                'risk_assessment': True
            })
        elif template_type == 'technical_documentation':
            rules.update({
                'code_examples': True,
                'implementation_focus': True,
                'technical_accuracy': True,
                'developer_friendly': True
            })
        elif template_type == 'api_documentation_template':
            rules.update({
                'endpoint_detail': True,
                'code_samples': True,
                'integration_examples': True,
                'troubleshooting': True
            })
        
        # Style-specific coordination rules
        style_tone = style_config.get('tone', 'professional')
        if style_tone == 'formal' or style_tone == 'academic':
            rules.update({
                'formal_language': True,
                'citation_requirements': True,
                'structured_approach': True
            })
        elif style_tone == 'casual' or style_tone == 'conversational':
            rules.update({
                'accessible_language': True,
                'engaging_examples': True,
                'reader_friendly': True
            })
        
        return rules
    
    def _build_cross_agent_context(self, state: EnrichedContentState) -> Dict[str, Any]:
        """Build context from previous agent outputs for coordination"""
        
        context = {}
        
        # Planning context
        if state.planning_output:
            planning = state.planning_output
            context['planning'] = {
                'content_strategy': getattr(planning, 'content_strategy', ''),
                'key_messages': getattr(planning, 'key_messages', []),
                'structure_approach': getattr(planning, 'structure_approach', ''),
                'research_priorities': getattr(planning, 'research_priorities', [])
            }
        
        # Research context
        if state.research_findings:
            research = state.research_findings
            context['research'] = {
                'primary_insights': getattr(research, 'primary_insights', []),
                'industry_context': getattr(research, 'industry_context', {}),
                'competitive_landscape': getattr(research, 'competitive_landscape', {}),
                'statistical_evidence': getattr(research, 'statistical_evidence', [])
            }
        
        # Content context
        if hasattr(state, 'draft_content') and state.draft_content:
            context['content'] = {
                'current_draft': state.draft_content,
                'word_count': len(state.draft_content.split()),
                'section_count': state.draft_content.count('#'),
                'has_examples': 'example' in state.draft_content.lower(),
                'has_data': any(char in state.draft_content for char in ['%', '$'])
            }
        
        return context
    
    def _merge_template_style_requirements(self, template_config: Dict, style_config: Dict) -> Dict[str, Any]:
        """Merge template and style requirements with conflict resolution"""
        
        requirements = {}
        
        # Template requirements (take precedence)
        if template_config.get('section_order'):
            requirements['section_order'] = template_config['section_order']
        
        if template_config.get('min_word_count'):
            requirements['min_word_count'] = template_config['min_word_count']
        
        if template_config.get('required_elements'):
            requirements['required_elements'] = template_config['required_elements']
        
        # Style requirements (unless conflicting)
        style_tone = style_config.get('tone', {})
        if isinstance(style_tone, dict):
            requirements['tone_requirements'] = style_tone
        
        style_writing = style_config.get('writing_style', {})
        if isinstance(style_writing, dict):
            requirements['writing_style'] = style_writing
        
        style_forbidden = style_config.get('forbidden_patterns', [])
        if style_forbidden:
            requirements['forbidden_patterns'] = style_forbidden
        
        # Merge conflicts resolution
        requirements['conflict_resolution'] = {
            'template_overrides_style': True,
            'style_enhances_template': True,
            'coordination_priority': 'template_first'
        }
        
        return requirements
    
    def _get_researcher_coordination(self, template_config: Dict, style_config: Dict, state: EnrichedContentState) -> Dict[str, Any]:
        """Researcher-specific coordination context"""
        
        coordination = {
            'research_depth': template_config.get('research_depth', 'comprehensive'),
            'source_requirements': template_config.get('source_requirements', []),
            'evidence_types': template_config.get('required_evidence_types', []),
            'industry_focus': template_config.get('industry_context', {}),
            'audience_research_needs': self._get_audience_research_needs(template_config, style_config)
        }
        
        # Template-specific research priorities
        template_type = template_config.get('template_type')
        if template_type == 'venture_capital_pitch':
            coordination['vc_research_priorities'] = [
                'market_size_validation',
                'traction_benchmarks',
                'competitive_analysis',
                'exit_strategy_data',
                'funding_landscape'
            ]
        elif template_type == 'business_proposal':
            coordination['business_research_priorities'] = [
                'roi_benchmarks',
                'implementation_case_studies',
                'cost_benefit_analysis',
                'risk_assessment_data',
                'market_validation'
            ]
        elif template_type == 'technical_documentation':
            coordination['technical_research_priorities'] = [
                'implementation_examples',
                'best_practices',
                'performance_benchmarks',
                'security_requirements',
                'troubleshooting_patterns'
            ]
        
        return coordination
    
    def _get_writer_coordination(self, template_config: Dict, style_config: Dict, state: EnrichedContentState) -> Dict[str, Any]:
        """Writer-specific coordination context"""
        
        coordination = {
            'structure_requirements': template_config.get('section_order', []),
            'tone_guidance': self._merge_tone_requirements(template_config, style_config),
            'content_depth': template_config.get('content_depth', 'substantial'),
            'audience_adaptation': self._get_audience_writing_needs(template_config, style_config),
            'template_voice': template_config.get('writing_voice', {}),
            'style_voice': style_config.get('voice_characteristics', [])
        }
        
        # Integration with previous agents
        if state.research_findings:
            coordination['research_integration'] = {
                'use_primary_insights': True,
                'cite_evidence': True,
                'integrate_statistics': True,
                'reference_industry_context': True
            }
        
        return coordination
    
    def _get_editor_coordination(self, template_config: Dict, style_config: Dict, state: EnrichedContentState) -> Dict[str, Any]:
        """Editor-specific coordination context"""
        
        coordination = {
            'editing_priorities': self._determine_editing_priorities(template_config, style_config),
            'quality_standards': template_config.get('quality_requirements', {}),
            'style_enforcement': style_config.get('style_enforcement', {}),
            'template_compliance_checks': self._get_template_compliance_checks(template_config),
            'consistency_requirements': self._get_consistency_requirements(template_config, style_config)
        }
        
        return coordination
    
    def _get_formatter_coordination(self, template_config: Dict, style_config: Dict, state: EnrichedContentState) -> Dict[str, Any]:
        """Formatter-specific coordination context"""
        
        coordination = {
            'formatting_rules': template_config.get('formatting_requirements', {}),
            'platform_optimization': template_config.get('platform_specifications', {}),
            'visual_hierarchy': template_config.get('visual_hierarchy', []),
            'style_formatting': style_config.get('formatting_preferences', {}),
            'template_structure': template_config.get('structure_requirements', {})
        }
        
        return coordination
    
    def _get_code_coordination(self, template_config: Dict, style_config: Dict, state: EnrichedContentState) -> Dict[str, Any]:
        """Code agent coordination context"""
        
        coordination = {
            'code_requirements': template_config.get('code_requirements', {}),
            'programming_languages': template_config.get('programming_languages', []),
            'code_style': style_config.get('code_style', {}),
            'implementation_depth': template_config.get('implementation_depth', 'examples'),
            'technical_audience': self._determine_technical_audience(template_config, style_config)
        }
        
        return coordination
    
    def _get_image_coordination(self, template_config: Dict, style_config: Dict, state: EnrichedContentState) -> Dict[str, Any]:
        """Image agent coordination context"""
        
        coordination = {
            'image_requirements': template_config.get('image_requirements', {}),
            'visual_style': style_config.get('visual_style', {}),
            'brand_alignment': template_config.get('brand_requirements', {}),
            'content_visualization': self._determine_visualization_needs(template_config, style_config),
            'platform_image_specs': template_config.get('platform_image_specs', {})
        }
        
        return coordination
    
    def _get_seo_coordination(self, template_config: Dict, style_config: Dict, state: EnrichedContentState) -> Dict[str, Any]:
        """SEO agent coordination context"""
        
        coordination = {
            'seo_keywords': template_config.get('seo_keywords', []),
            'content_optimization': template_config.get('seo_requirements', {}),
            'platform_seo': template_config.get('platform_seo', {}),
            'audience_search_intent': self._determine_search_intent(template_config, style_config),
            'content_structure_seo': self._get_seo_structure_requirements(template_config)
        }
        
        return coordination
    
    def _get_publisher_coordination(self, template_config: Dict, style_config: Dict, state: EnrichedContentState) -> Dict[str, Any]:
        """Publisher agent coordination context"""
        
        coordination = {
            'publication_requirements': template_config.get('publication_specifications', {}),
            'distribution_strategy': template_config.get('distribution_strategy', {}),
            'quality_assurance': self._get_qa_requirements(template_config, style_config),
            'metadata_requirements': template_config.get('metadata_requirements', {}),
            'final_validation': self._get_final_validation_criteria(template_config, style_config)
        }
        
        return coordination
    
    def _get_planner_coordination(self, template_config: Dict, style_config: Dict, state: EnrichedContentState) -> Dict[str, Any]:
        """Planner-specific coordination context"""
        
        coordination = {
            'planning_guidelines': template_config.get('planning_guidelines', {}),
            'audience_analysis': style_config.get('audience_analysis', {}),
            'content_strategy': template_config.get('content_strategy', {}),
            'key_messages': template_config.get('key_messages', []),
            'structure_approach': template_config.get('structure_approach', {}),
            'research_priorities': template_config.get('research_priorities', [])
        }
        
        return coordination
    
    # Helper methods for coordination context building
    
    def _get_audience_research_needs(self, template_config: Dict, style_config: Dict) -> Dict[str, Any]:
        """Determine audience-specific research needs"""
        
        audience = template_config.get('target_audience', style_config.get('audience', 'general'))
        
        if 'executive' in audience.lower():
            return {
                'focus_areas': ['strategic_implications', 'roi_data', 'market_impact'],
                'evidence_types': ['financial_metrics', 'industry_benchmarks', 'competitive_analysis'],
                'depth': 'executive_summary_plus_detail'
            }
        elif 'technical' in audience.lower():
            return {
                'focus_areas': ['implementation_details', 'technical_specifications', 'best_practices'],
                'evidence_types': ['technical_documentation', 'code_examples', 'performance_data'],
                'depth': 'comprehensive_technical'
            }
        elif 'investor' in audience.lower():
            return {
                'focus_areas': ['market_opportunity', 'financial_projections', 'competitive_advantage'],
                'evidence_types': ['market_data', 'traction_metrics', 'exit_strategies'],
                'depth': 'investment_focused'
            }
        else:
            return {
                'focus_areas': ['practical_applications', 'key_concepts', 'real_world_examples'],
                'evidence_types': ['case_studies', 'expert_insights', 'trend_analysis'],
                'depth': 'balanced_comprehensive'
            }
    
    def _merge_tone_requirements(self, template_config: Dict, style_config: Dict) -> Dict[str, Any]:
        """Merge tone requirements from template and style"""
        
        tone_guidance = {}
        
        # Template tone (takes precedence)
        template_tone = template_config.get('tone', {})
        if template_tone:
            tone_guidance.update(template_tone)
        
        # Style tone (enhances template)
        style_tone = style_config.get('tone')
        if style_tone:
            tone_guidance['style_tone'] = style_tone
        
        # Style writing characteristics
        writing_style = style_config.get('writing_style', {})
        if writing_style:
            tone_guidance['writing_characteristics'] = writing_style
        
        return tone_guidance
    
    def _get_audience_writing_needs(self, template_config: Dict, style_config: Dict) -> Dict[str, Any]:
        """Determine audience-specific writing adaptations"""
        
        audience = template_config.get('target_audience', style_config.get('audience', 'general'))
        complexity = template_config.get('complexity_level', 5)
        
        adaptations = {
            'vocabulary_level': 'professional' if complexity > 6 else 'accessible',
            'explanation_depth': 'detailed' if complexity > 7 else 'moderate',
            'example_types': 'technical' if 'technical' in audience.lower() else 'practical'
        }
        
        if 'executive' in audience.lower():
            adaptations.update({
                'focus': 'strategic_implications',
                'structure': 'executive_summary_first',
                'language': 'business_formal',
                'emphasis': 'decision_making_support'
            })
        elif 'developer' in audience.lower() or 'technical' in audience.lower():
            adaptations.update({
                'focus': 'implementation_details',
                'structure': 'problem_solution_code',
                'language': 'technical_precise',
                'emphasis': 'practical_implementation'
            })
        
        return adaptations
    
#    def _determine_editing_priorities(self, template_config: Dict, style_config: Dict) -> List[str]:
#        """Determine editing priorities based on template and style"""
#        
#        priorities = ['template_compliance', 'style_consistency', 'content_quality']
#        
#        template_type = template_config.get('template_type')
#        if template_type == 'venture_capital_pitch':
#            priorities.extend(['financial_accuracy', 'investor_language', 'metric_validation'])
#        elif template_type == 'business_proposal':
#            priorities.extend(['roi_clarity', 'implementation_feasibility', 'executive_appeal'])
#        elif template_type == 'technical_documentation':
#            priorities.extend(['technical_accuracy', 'code_validation', 'implementation_clarity'])
#        
#        style_tone = style_config.get('tone')
#        if style_tone == 'formal':
#            priorities.append('formality_enforcement')
#        elif style_tone == 'academic':
#            priorities.append('academic_rigor')
#        
#        return priorities
#    
    def _get_template_compliance_checks(self, template_config: Dict) -> List[str]:
        """Get template compliance checks"""
        
        checks = []
        
        if template_config.get('section_order'):
            checks.append('section_order_compliance')
        
        if template_config.get('min_word_count'):
            checks.append('word_count_compliance')
        
        if template_config.get('required_elements'):
            checks.append('required_elements_present')
        
        if template_config.get('formatting_requirements'):
            checks.append('formatting_compliance')
        
        return checks
    
    def _get_consistency_requirements(self, template_config: Dict, style_config: Dict) -> Dict[str, Any]:
        """Get consistency requirements across template and style"""
        
        return {
            'tone_consistency': True,
            'terminology_consistency': True,
            'formatting_consistency': True,
            'voice_consistency': True,
            'template_structure_consistency': True,
            'style_pattern_consistency': True
        }
    
    def _determine_technical_audience(self, template_config: Dict, style_config: Dict) -> str:
        """Determine technical audience level"""
        
        audience = template_config.get('target_audience', '')
        complexity = template_config.get('complexity_level', 5)
        
        if 'developer' in audience.lower() or complexity > 7:
            return 'professional_developer'
        elif 'technical' in audience.lower():
            return 'technical_professional'
        elif complexity > 5:
            return 'technical_literate'
        else:
            return 'general_with_examples'
    
    def _determine_visualization_needs(self, template_config: Dict, style_config: Dict) -> Dict[str, Any]:
        """Determine visualization needs"""
        
        template_type = template_config.get('template_type')
        
        if template_type == 'venture_capital_pitch':
            return {
                'chart_types': ['growth_charts', 'market_size', 'financial_projections'],
                'visual_style': 'professional_investor',
                'emphasis': 'data_driven'
            }
        elif template_type == 'business_proposal':
            return {
                'chart_types': ['roi_charts', 'timeline', 'process_flow'],
                'visual_style': 'executive_professional',
                'emphasis': 'strategic_clarity'
            }
        elif template_type == 'technical_documentation':
            return {
                'chart_types': ['architecture_diagrams', 'flow_charts', 'code_examples'],
                'visual_style': 'technical_clear',
                'emphasis': 'implementation_support'
            }
        else:
            return {
                'chart_types': ['concept_diagrams', 'process_flow'],
                'visual_style': 'professional_clear',
                'emphasis': 'comprehension_support'
            }
    
#    def _determine_search_intent(self, template_config: Dict, style_config: Dict) -> str:
#        """Determine primary search intent"""
#        
#        template_type = template_config.get('template_type')
#        
#        if template_type == 'venture_capital_pitch':
#            return 'commercial_funding'
#        elif template_type == 'business_proposal':
#            return 'commercial_solution'
#        elif template_type == 'technical_documentation':
#            return 'informational_implementation'
#        else:
#            return 'informational_educational'
    
    def _get_seo_structure_requirements(self, template_config: Dict) -> Dict[str, Any]:
        """Get SEO structure requirements from template"""
        
        return {
            'header_hierarchy': template_config.get('section_order', []),
            'keyword_distribution': template_config.get('seo_keyword_strategy', {}),
            'content_structure': template_config.get('seo_structure', {}),
            'meta_requirements': template_config.get('meta_requirements', {})
        }
    
    def _get_qa_requirements(self, template_config: Dict, style_config: Dict) -> Dict[str, Any]:
        """Get quality assurance requirements"""
        
        return {
            'template_validation': template_config.get('quality_requirements', {}),
            'style_validation': style_config.get('quality_standards', {}),
            'content_standards': self._merge_content_standards(template_config, style_config),
            'compliance_checks': self._get_compliance_checks(template_config, style_config)
        }
    
    def _get_final_validation_criteria(self, template_config: Dict, style_config: Dict) -> Dict[str, Any]:
        """Get final validation criteria"""
        
        return {
            'template_compliance_score_minimum': 0.85,
            'style_consistency_score_minimum': 0.80,
            'content_quality_score_minimum': 0.85,
            'cross_agent_consistency_minimum': 0.80,
            'publication_readiness_criteria': self._get_publication_criteria(template_config, style_config)
        }
    
    def _merge_content_standards(self, template_config: Dict, style_config: Dict) -> Dict[str, Any]:
        """Merge content standards from template and style"""
        
        standards = {}
        
        # Template standards
        template_standards = template_config.get('content_standards', {})
        standards.update(template_standards)
        
        # Style standards
        style_standards = style_config.get('content_standards', {})
        standards.update(style_standards)
        
        return standards
    
#    def _get_compliance_checks(self, template_config: Dict, style_config: Dict) -> List[str]:
#        """Get compliance checks list"""
#        
#        checks = [
#            'template_structure_compliance',
#            'style_pattern_compliance',
#            'content_quality_compliance',
#            'audience_appropriateness',
#            'technical_accuracy'
#        ]
#        
#        template_type = template_config.get('template_type')
#        if template_type == 'venture_capital_pitch':
#            checks.extend(['financial_accuracy', 'investor_standards'])
#        elif template_type == 'business_proposal':
#            checks.extend(['business_accuracy', 'executive_standards'])
#        
#        return checks
    
    def _get_publication_criteria(self, template_config: Dict, style_config: Dict) -> Dict[str, Any]:
        """Get publication readiness criteria"""
        
        return {
            'minimum_word_count': template_config.get('min_word_count', 1000),
            'required_sections_present': True,
            'template_compliance_achieved': True,
            'style_consistency_maintained': True,
            'quality_standards_met': True,
            'audience_appropriateness_validated': True
        }


# Global coordination instance
_coordination_instance = None

def get_unified_coordination() -> UnifiedAgentCoordination:
    """Get global coordination instance"""
    global _coordination_instance
    if _coordination_instance is None:
        _coordination_instance = UnifiedAgentCoordination()
    return _coordination_instance

def get_coordinated_context(state: EnrichedContentState, agent_type: AgentType) -> Dict[str, Any]:
    """Get coordinated context for an agent"""
    coordination = get_unified_coordination()
    return coordination.get_coordinated_context(state, agent_type)

# Legacy compatibility
def get_coordinated_prompt_for_agent(state: EnrichedContentState, agent_name: str) -> str:
    """Legacy compatibility - get coordinated prompt"""
    agent_type_map = {
        'researcher': AgentType.RESEARCHER,
        'writer': AgentType.WRITER,
        'editor': AgentType.EDITOR,
        'formatter': AgentType.FORMATTER,
        'code': AgentType.CODE,
        'image': AgentType.IMAGE,
        'seo': AgentType.SEO,
        'publisher': AgentType.PUBLISHER
    }
    
    agent_type = agent_type_map.get(agent_name.lower())
    if not agent_type:
        return f"Generate content for {agent_name} agent"
    
    context = get_coordinated_context(state, agent_type)
    
    # Build coordinated prompt
    prompt_parts = [
        f"You are operating as the {agent_name} agent in a coordinated multi-agent system.",
        f"Template Type: {context['template_config'].get('template_type', 'default')}",
        f"Style Profile: {context['style_config'].get('id', 'default')}",
        f"Coordination Rules: {context['coordination_rules']}"
    ]
    
    return "\n".join(prompt_parts)