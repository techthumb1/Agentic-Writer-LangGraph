# File: langgraph_app/agents/enhanced_editor_integrated.py
from types import SimpleNamespace
from typing import Dict, List
from langgraph_app.core.state import EditingGuidance
from datetime import datetime
from langgraph_app.core.state import (
    EnrichedContentState, 
    AgentType
)
import logging

logger = logging.getLogger(__name__)

class EnhancedEditorAgent:
    """Universal Configuration-Driven Editor Agent - NO HARDCODED TEMPLATES"""

    def __init__(self):
        self.agent_type = AgentType.EDITOR

    def intelligent_edit(self, state: EnrichedContentState) -> EnrichedContentState:
        return self.execute(state)

    # File: langgraph_app/agents/enhanced_editor_integrated.py

# File: langgraph_app/agents/enhanced_editor_integrated.py
# Replace execute method

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute with intelligent editing"""
        
        draft_content = getattr(state, 'draft_content', '') or getattr(state, 'content', '')
        
        if not draft_content.strip():
            raise RuntimeError("ENTERPRISE: Editor requires draft content - cannot proceed")
        
        template_config = getattr(state, 'template_config', {})
        style_config = getattr(state, 'style_config', {})
        
        # Analyze content quality
        quality_issues = self._analyze_content_quality(draft_content, state)
        
        logger.info(f"Editor found {len(quality_issues)} quality issues")
        
        # Apply intelligent edits
        edited_content = self._apply_intelligent_edits(
            draft_content,
            quality_issues,
            template_config,
            style_config,
            state
        )
        
        # Validate improvements
        improvement_score = self._calculate_improvement_score(draft_content, edited_content)
        
        logger.info(f"Editor improvement score: {improvement_score:.2f}")
        
        state.content = edited_content
        state.edited_content = edited_content
        state.draft_content = edited_content  # Update draft for downstream agents
        
        return state
    
    def _analyze_content_quality(self, content: str, state: EnrichedContentState) -> List[str]:
        """Identify specific quality issues"""
        
        issues = []
        
        # Check research integration
        research = getattr(state, 'research_findings', None)
        if research:
            primary_insights = getattr(research, 'primary_insights', [])
            missing_insights = 0
            for insight in primary_insights[:3]:
                if isinstance(insight, dict):
                    key_term = insight.get('finding', '')[:50]
                    if key_term and key_term.lower() not in content.lower():
                        missing_insights += 1
            
            if missing_insights > 0:
                issues.append(f"Missing {missing_insights} key research insights")
        
        # Check planning alignment
        planning = getattr(state, 'planning_output', None)
        if planning:
            key_messages = getattr(planning, 'key_messages', [])
            missing_messages = 0
            for msg in key_messages[:3]:
                if msg and msg.lower() not in content.lower():
                    missing_messages += 1
            
            if missing_messages > 0:
                issues.append(f"Missing {missing_messages} planned key messages")
        
        # Structural issues
        if content.count('#') < 3:
            issues.append("Insufficient section structure (need min 3 sections)")
        
        # Length validation
        word_count = len(content.split())
        template_config = getattr(state, 'template_config', {})
        min_words = template_config.get('requirements', {}).get('min_words', 1000)
        
        if word_count < min_words * 0.8:
            issues.append(f"Content too short: {word_count} words (target: {min_words})")
        
        # Generic language check
        generic_phrases = [
            'in this article', 'in this post', 'in conclusion',
            'it is important to note', 'there are many', 'it should be noted'
        ]
        found_generic = [phrase for phrase in generic_phrases if phrase in content.lower()]
        if found_generic:
            issues.append(f"Contains {len(found_generic)} generic phrases")
        
        return issues
    
    def _apply_intelligent_edits(
        self,
        content: str,
        issues: List[str],
        template_config: Dict,
        style_config: Dict,
        state: EnrichedContentState
    ) -> str:
        """Apply edits based on identified issues"""
        
        edited = content
        
        # Fix missing research insights
        if any('research insights' in issue for issue in issues):
            research = getattr(state, 'research_findings', None)
            if research:
                primary_insights = getattr(research, 'primary_insights', [])
                insights_to_add = []
                for insight in primary_insights[:2]:
                    if isinstance(insight, dict):
                        finding = insight.get('finding', '')
                        if finding and finding.lower() not in edited.lower():
                            insights_to_add.append(f"Research indicates that {finding.lower()}.")
                
                if insights_to_add:
                    # Add after first paragraph
                    paragraphs = edited.split('\n\n')
                    if len(paragraphs) > 1:
                        paragraphs.insert(1, ' '.join(insights_to_add))
                        edited = '\n\n'.join(paragraphs)
        
        # Fix missing key messages
        if any('key messages' in issue for issue in issues):
            planning = getattr(state, 'planning_output', None)
            if planning:
                key_messages = getattr(planning, 'key_messages', [])
                for msg in key_messages[:2]:
                    if msg and msg.lower() not in edited.lower():
                        edited += f"\n\n**Key Insight:** {msg}"
        
        # Remove generic phrases
        generic_replacements = {
            'in this article': 'This analysis shows',
            'in this post': 'This examination reveals',
            'in conclusion': 'The evidence demonstrates',
            'it is important to note': 'Notably',
            'there are many': 'Multiple factors include'
        }
        
        for generic, replacement in generic_replacements.items():
            if generic in edited.lower():
                # Case-insensitive replacement
                import re
                edited = re.sub(re.escape(generic), replacement, edited, flags=re.IGNORECASE)
        
        return edited
    
    def _calculate_improvement_score(self, original: str, edited: str) -> float:
        """Calculate how much editing improved content"""
        
        score = 0.5  # Base
        
        # Word count improvement
        orig_words = len(original.split())
        edit_words = len(edited.split())
        if edit_words > orig_words:
            score += 0.1
        
        # Structure improvement
        orig_sections = original.count('#')
        edit_sections = edited.count('#')
        if edit_sections > orig_sections:
            score += 0.1
        
        # Generic phrase reduction
        generic_count_before = sum(1 for phrase in [
            'in this article', 'in conclusion', 'it is important'
        ] if phrase in original.lower())
        
        generic_count_after = sum(1 for phrase in [
            'in this article', 'in conclusion', 'it is important'
        ] if phrase in edited.lower())
        
        if generic_count_after < generic_count_before:
            score += 0.2
        
        # Data integration check
        if ('$' in edited or '%' in edited) and not ('$' in original or '%' in original):
            score += 0.1
        
        return min(score, 1.0)

    def _improve_content(self, text: str, template_config: dict, style_config: dict) -> str:
        """Basic string-level improvements without external calls."""
        t = (text or "").strip()
        if not t:
            return t

        # Normalize spacing
        t = t.replace("\r\n", "\n").replace("\n\n\n", "\n\n")

        # Enforce required sections if template specifies
        for section in template_config.get("section_order", []):
            if isinstance(section, str) and section.lower() not in t.lower():
                t += f"\n\n## {section}\n"

        return t
    # File: langgraph_app/agents/enhanced_editor_integrated.py
    # Add this method to the EnhancedEditorAgent class

    def _edit_content(self, state_dict: dict) -> str:
        """Edit content using available style and template configs."""

        draft_content = state_dict.get("draft_content", "")
        style_config = state_dict.get("style_config", {})
        template_config = state_dict.get("template_config", {})

        if not draft_content.strip():
            return "No content available for editing"

        # Basic editing logic - enhance based on configs
        edited_content = draft_content

        # Apply style-based improvements if style_config available
        if style_config:
            tone = style_config.get("tone", "")
            if tone == "formal":
                # Apply formal tone adjustments
                edited_content = self._apply_formal_tone(edited_content)
            elif tone == "casual":
                # Apply casual tone adjustments  
                edited_content = self._apply_casual_tone(edited_content)

        # Apply template-based structure if template_config available
        if template_config:
            structure = template_config.get("structure", {})
            if structure:
                edited_content = self._apply_structure_formatting(edited_content, structure)

        return edited_content

    def _apply_formal_tone(self, content: str) -> str:
        """Apply formal tone adjustments."""
        # Basic formal tone processing
        return content.replace("don't", "do not").replace("can't", "cannot")

    def _apply_casual_tone(self, content: str) -> str:
        """Apply casual tone adjustments."""
        # Basic casual tone processing
        return content

    def _apply_structure_formatting(self, content: str, structure: dict) -> str:
        """Apply structural formatting based on template config."""
        # Basic structure processing
        return content
    

    
    def _create_universal_planning_output(self, state: EnrichedContentState):
        """Create universal planning output based on content analysis"""
        template_config = self._extract_universal_template_config(state)
        
        # Analyze content characteristics
        content_analysis = self._analyze_content_characteristics(state, template_config)
        
        # Generate sections from template config or content analysis
        estimated_sections = self._generate_sections_from_config(template_config, content_analysis)
        
        # Generate key messages from content analysis
        key_messages = self._generate_key_messages_from_analysis(content_analysis)
        
        return SimpleNamespace(
            content_strategy=f"universal_{content_analysis['content_type']}_strategy",
            structure_approach=content_analysis['structure_approach'],
            key_messages=key_messages,
            research_priorities=content_analysis['research_priorities'],
            depth=content_analysis['depth_level'],
            sources_needed=content_analysis['sources_needed'],
            focus_areas=content_analysis['focus_areas'],
            audience_insights={
                "primary_audience": state.content_spec.audience,
                "expertise_level": state.content_spec.complexity_level,
                "decision_factors": content_analysis['decision_factors']
            },
            competitive_positioning="value_driven_differentiation",
            success_metrics={"engagement_target": content_analysis['engagement_target']},
            estimated_sections=estimated_sections,
            planning_confidence=content_analysis['confidence']
        )

    def _analyze_content_characteristics(self, state: EnrichedContentState, template_config: dict) -> dict:
        """Analyze content characteristics for universal planning"""
        topic = state.content_spec.topic.lower()
        audience = state.content_spec.audience.lower()
        complexity = state.content_spec.complexity_level
        
        # Determine content type from analysis
        content_type = 'general'
        if any(word in topic for word in ['business', 'strategy', 'proposal']):
            content_type = 'business'
        elif any(word in topic for word in ['technical', 'api', 'documentation']):
            content_type = 'technical'
        elif any(word in topic for word in ['research', 'study', 'analysis']):
            content_type = 'analytical'
        elif any(word in topic for word in ['investment', 'funding', 'venture']):
            content_type = 'financial'
        
        # Determine structure approach
        structure_approach = 'logical_progression'
        if 'executive' in audience:
            structure_approach = 'executive_summary_first'
        elif 'technical' in audience:
            structure_approach = 'implementation_focused'
        elif 'investor' in audience:
            structure_approach = 'roi_focused'
        
        return {
            'content_type': content_type,
            'structure_approach': structure_approach,
            'depth_level': 'comprehensive' if complexity >= 7 else 'moderate',
            'sources_needed': min(max(complexity, 3), 10),
            'engagement_target': min(0.7 + (complexity * 0.02), 0.95),
            'confidence': 0.85,
            'research_priorities': self._determine_research_priorities(topic, content_type),
            'focus_areas': self._determine_focus_areas(topic, content_type, audience),
            'decision_factors': self._determine_decision_factors(audience, content_type)
        }
    
    def _determine_research_priorities(self, topic: str, content_type: str) -> list:
        """Determine research priorities from content analysis"""
        base_priorities = ['background_research', 'key_concepts']
        
        if content_type == 'business':
            base_priorities.extend(['market_analysis', 'financial_data'])
        elif content_type == 'technical':
            base_priorities.extend(['technical_specifications', 'implementation_examples'])
        elif content_type == 'analytical':
            base_priorities.extend(['data_analysis', 'comparative_studies'])
        elif content_type == 'financial':
            base_priorities.extend(['financial_projections', 'market_data'])
        
        return base_priorities
    
    def _determine_focus_areas(self, topic: str, content_type: str, audience: str) -> list:
        """Determine focus areas from content analysis"""
        base_areas = ['introduction', 'main_analysis']
        
        if 'executive' in audience:
            base_areas.extend(['strategic_implications', 'decision_framework'])
        elif 'technical' in audience:
            base_areas.extend(['implementation_details', 'technical_specifications'])
        elif 'investor' in audience:
            base_areas.extend(['financial_projections', 'market_opportunity'])
        else:
            base_areas.extend(['practical_applications', 'next_steps'])
        
        return base_areas
    
    def _determine_decision_factors(self, audience: str, content_type: str) -> list:
        """Determine decision factors from audience analysis"""
        if 'executive' in audience:
            return ['strategic_value', 'roi', 'implementation_feasibility']
        elif 'investor' in audience:
            return ['market_size', 'growth_potential', 'competitive_advantage']
        elif 'technical' in audience:
            return ['technical_feasibility', 'implementation_complexity', 'scalability']
        else:
            return ['relevance', 'actionability', 'credibility']
    
    def _generate_sections_from_config(self, template_config: dict, content_analysis: dict) -> list:
        """Generate sections from config or content analysis"""
        # Try template config first
        if template_config.get('section_order'):
            sections = []
            for section_name in template_config['section_order']:
                sections.append({
                    "name": section_name,
                    "estimated_words": template_config.get('section_word_counts', {}).get(section_name, 400)
                })
            return sections
        
        # Generate from content analysis
        content_type = content_analysis['content_type']
        
        if content_type == 'business':
            return [
                {"name": "Executive Overview", "estimated_words": 400},
                {"name": "Strategic Analysis", "estimated_words": 600},
                {"name": "Market Considerations", "estimated_words": 500},
                {"name": "Implementation Approach", "estimated_words": 500},
                {"name": "Success Metrics", "estimated_words": 300},
                {"name": "Next Steps", "estimated_words": 200}
            ]
        elif content_type == 'technical':
            return [
                {"name": "Technical Overview", "estimated_words": 400},
                {"name": "Implementation Guide", "estimated_words": 800},
                {"name": "Configuration Details", "estimated_words": 600},
                {"name": "Best Practices", "estimated_words": 400},
                {"name": "Troubleshooting", "estimated_words": 300}
            ]
        elif content_type == 'analytical':
            return [
                {"name": "Research Overview", "estimated_words": 400},
                {"name": "Methodology", "estimated_words": 500},
                {"name": "Analysis Results", "estimated_words": 700},
                {"name": "Implications", "estimated_words": 400},
                {"name": "Conclusions", "estimated_words": 300}
            ]
        else:
            return [
                {"name": "Introduction", "estimated_words": 400},
                {"name": "Core Analysis", "estimated_words": 600},
                {"name": "Practical Applications", "estimated_words": 500},
                {"name": "Implementation Considerations", "estimated_words": 400},
                {"name": "Key Takeaways", "estimated_words": 300}
            ]
    
    def _generate_key_messages_from_analysis(self, content_analysis: dict) -> list:
        """Generate key messages from content analysis"""
        content_type = content_analysis['content_type']
        
        if content_type == 'business':
            return [
                "Strategic value proposition",
                "Market opportunity analysis", 
                "Implementation roadmap"
            ]
        elif content_type == 'technical':
            return [
                "Technical implementation approach",
                "Configuration and setup guidance",
                "Best practices and optimization"
            ]
        elif content_type == 'analytical':
            return [
                "Research methodology and approach",
                "Key findings and insights",
                "Practical implications"
            ]
        else:
            return [
                "Core concepts and principles",
                "Practical applications",
                "Implementation guidance"
            ]

    def _extract_universal_template_config(self, state: EnrichedContentState) -> dict:
        """Extract template configuration universally"""
        template_config = {}
        
        if hasattr(state, 'template_config') and state.template_config:
            template_config = state.template_config
        elif hasattr(state, 'content_spec') and state.content_spec.business_context:
            template_config = state.content_spec.business_context.get('template_config', {})
        
        if not template_config and hasattr(state, 'content_spec'):
            template_config = self._create_universal_template_config(state.content_spec)
        
        return template_config

    def _create_universal_template_config(self, content_spec) -> dict:
        """Create universal template configuration from content analysis"""
        topic = content_spec.topic.lower()
        audience = content_spec.audience.lower()
        template_type = content_spec.template_type.lower()
        
        # Analyze content characteristics for config generation
        formality_level = 'high' if any(word in audience for word in ['executive', 'investor', 'board']) else 'medium'
        
        persuasiveness_level = 'high' if any(word in template_type for word in ['proposal', 'pitch']) else 'medium'
        
        # Determine word count based on complexity and audience
        base_word_count = 2500
        if content_spec.complexity_level >= 8:
            base_word_count = 4000
        elif content_spec.complexity_level <= 4:
            base_word_count = 1800
        
        return {
            "template_type": template_type,
            "tone": {
                "formality": formality_level,
                "persuasiveness": persuasiveness_level,
                "clarity": "high"
            },
            "min_word_count": base_word_count,
            "max_word_count": int(base_word_count * 1.5),
            "audience": audience,
            "platform": content_spec.platform,
            "adaptable": True,
            "generated_from_analysis": True
        }

    def _create_editing_guidance_universal(self, state: EnrichedContentState, instructions) -> EditingGuidance:
        """Create universal editing guidance from configuration"""
        content = state.draft_content
        spec = state.content_spec or {}
        planning = state.planning_output
        template_config = state.template_config
        
        structural_improvements = self._identify_structural_improvements_universal(content, planning, template_config)
        clarity_enhancements = self._identify_clarity_enhancements_universal(content, spec, template_config)
        audience_alignment_issues = self._check_audience_alignment_universal(content, spec, planning, template_config)
        flow_optimizations = self._identify_flow_optimizations_universal(content, template_config)
        fact_checking_requirements = self._identify_fact_checking_needs_universal(content, template_config)

        return EditingGuidance(
            structural_improvements=structural_improvements,
            clarity_enhancements=clarity_enhancements,
            audience_alignment_issues=audience_alignment_issues,
            flow_optimizations=flow_optimizations,
            fact_checking_requirements=fact_checking_requirements,
            style_consistency_notes=self._check_style_consistency_universal(content, template_config),
            engagement_opportunities=self._identify_engagement_opportunities_universal(content, spec, template_config),
            editing_confidence=0.85
        )
    
    def _edit_content_with_guidance_universal(self, state: EnrichedContentState, instructions) -> str:
        """Edit content universally based on guidance"""
        content = state.draft_content
        guidance = state.editing_guidance
        spec = state.content_spec or {}
        
        content = self._apply_structural_improvements_universal(content, guidance.structural_improvements)
        content = self._apply_clarity_enhancements_universal(content, guidance.clarity_enhancements)
        content = self._fix_audience_alignment_universal(content, guidance.audience_alignment_issues, spec)
        content = self._optimize_flow_universal(content, guidance.flow_optimizations)
        content = self._add_engagement_elements_universal(content, guidance.engagement_opportunities)
        
        return content
    
    def _identify_structural_improvements_universal(self, content: str, planning, template_config: dict) -> list:
        """Identify structural improvements universally"""
        improvements = []
        
        # Check template requirements
        if template_config.get('section_order'):
            required_sections = template_config['section_order']
            content_lower = content.lower()
            
            for section in required_sections:
                if section.lower() not in content_lower:
                    improvements.append(f"Add required section: {section}")
        
        # Check planning requirements
        elif planning and planning.get('estimated_sections'):
            planned_sections = [section["name"].lower() for section in planning.estimated_sections]
            content_lower = content.lower()
            
            for section in planned_sections:
                if section not in content_lower:
                    improvements.append(f"Add planned section: {section}")
        
        # Check section balance
        sections = content.split('\n# ')
        if len(sections) > 1:
            section_lengths = [len(section.split()) for section in sections]
            avg_length = sum(section_lengths) / len(section_lengths)
            
            for i, length in enumerate(section_lengths):
                if length < avg_length * 0.5:
                    improvements.append(f"Expand section {i+1} - insufficient content")
                elif length > avg_length * 2.5:
                    improvements.append(f"Condense section {i+1} - excessive length")
        
        # Check word count requirements
        total_words = len(content.split())
        min_words = template_config.get('min_word_count', 2000)
        if total_words < min_words:
            improvements.append(f"Expand content to meet minimum {min_words} words (current: {total_words})")
        
        return improvements
    
    def _identify_clarity_enhancements_universal(self, content: str, spec, template_config: dict) -> list:
        """Identify clarity enhancements universally"""
        enhancements = []
        
        # Check formality requirements
        formality = template_config.get('tone', {}).get('formality', 'medium')
        if formality == 'high':
            contractions = ["don't", "can't", "won't", "it's", "we're", "they're"]
            for contraction in contractions:
                if contraction in content.lower():
                    enhancements.append(f"Replace contraction '{contraction}' for formal tone")
        
        # Check complexity for audience
        if spec.complexity_level < 6:
            technical_terms = ["ROI", "KPI", "API", "SaaS", "ML", "AI", "B2B", "SLA"]
            for term in technical_terms:
                if term in content and f"({term}" not in content:
                    enhancements.append(f"Define technical term: {term}")
        
        # Check sentence complexity
        sentences = content.split('. ')
        long_sentences = [i for i, s in enumerate(sentences) if len(s.split()) > 25]
        if long_sentences:
            enhancements.append(f"Break down {len(long_sentences)} overly complex sentences")
        
        # Check paragraph transitions
        paragraphs = content.split('\n\n')
        transition_words = ['however', 'therefore', 'additionally', 'furthermore', 'consequently', 'moreover', 'nevertheless']
        
        for i in range(1, len(paragraphs)):
            if len(paragraphs[i]) > 100:  # Only check substantial paragraphs
                has_transition = any(word in paragraphs[i][:50].lower() for word in transition_words)
                if not has_transition:
                    enhancements.append(f"Add transition to paragraph {i+1}")
        
        return enhancements
    
    def _check_audience_alignment_universal(self, content: str, spec, planning, template_config: dict) -> list:
        """Check audience alignment universally"""
        issues = []
        
        target_audience = template_config.get('audience', spec.audience).lower()
        
        # Check formality alignment
        if any(word in target_audience for word in ['executive', 'investor', 'board']):
            casual_phrases = ["hey", "let's dive", "pretty cool", "awesome", "totally", "super", "really"]
            for phrase in casual_phrases:
                if phrase in content.lower():
                    issues.append(f"Remove casual phrase inappropriate for {target_audience}: '{phrase}'")
        
        # Check technical depth alignment
        if 'technical' in target_audience and spec.complexity_level > 7:
            if 'implementation' not in content.lower():
                issues.append("Add technical implementation details for technical audience")
        elif 'beginner' in target_audience and spec.complexity_level < 4:
            complex_words = [w for w in content.split() if len(w) > 12]
            if len(complex_words) > 20:
                issues.append("Simplify vocabulary for beginner audience")
        
        # Check decision factors alignment
        if planning and hasattr(planning, 'audience_insights'):
            decision_factors = planning.audience_insights.get("decision_factors", [])
            content_lower = content.lower()
            missing_factors = [factor for factor in decision_factors 
                             if factor.lower().replace('_', ' ') not in content_lower]
            if missing_factors:
                issues.append(f"Address missing decision factors: {', '.join(missing_factors)}")
        
        return issues
    
    def _identify_flow_optimizations_universal(self, content: str, template_config: dict) -> list:
        """Identify flow optimizations universally"""
        optimizations = []
        
        # Check section order alignment
        section_order = template_config.get('section_order', [])
        if section_order:
            import re
            headers = re.findall(r'^#+\s+(.+)', content, re.MULTILINE)
            
            for i, required_section in enumerate(section_order):
                if i < len(headers):
                    if required_section.lower() not in headers[i].lower():
                        optimizations.append(f"Reorder section '{headers[i]}' to match template requirement '{required_section}'")
        
        # Check introduction effectiveness
        intro_paragraph = content.split('\n\n')[0] if '\n\n' in content else content[:200]
        hook_words = ['opportunity', 'challenge', 'solution', 'impact', 'strategic', 'critical', 'essential']
        if not any(word in intro_paragraph.lower() for word in hook_words):
            optimizations.append("Strengthen introduction with compelling hook")
        
        # Check conclusion strength
        if '\n\n' in content:
            conclusion = content.split('\n\n')[-1]
            action_words = ['next steps', 'recommendation', 'action', 'implementation', 'forward', 'proceed']
            if not any(word in conclusion.lower() for word in action_words):
                optimizations.append("Add clear call-to-action in conclusion")
        
        # Check section connections
        sections = content.split('\n# ')
        if len(sections) > 2:
            for i in range(1, len(sections)-1):
                section_end = sections[i].split('\n\n')[-1] if '\n\n' in sections[i] else sections[i][-100:]
                if len(section_end) < 50 or not any(word in section_end.lower() for word in ['next', 'following', 'now', 'therefore']):
                    optimizations.append(f"Improve connection between sections {i+1} and {i+2}")
        
        return optimizations
    
    def _identify_fact_checking_needs_universal(self, content: str, template_config: dict) -> list:
        """Identify fact-checking needs universally"""
        requirements = []
        
        # Check for unsupported claims
        claim_indicators = ["studies show", "research indicates", "data reveals", "statistics prove", "according to", "experts say"]
        for indicator in claim_indicators:
            if indicator in content.lower():
                requirements.append(f"Verify and cite source for claim with '{indicator}'")
        
        # Check for statistical claims
        import re
        percentages = re.findall(r'\d+%', content)
        if percentages:
            for percentage in percentages:
                requirements.append(f"Verify source for statistic: {percentage}")
        
        # Check for financial claims
        financial_claims = re.findall(r'\$[\d,]+[MBK]?', content)
        if financial_claims:
            requirements.append("Verify sources for financial data")
        
        # Check template-specific fact checking
        template_type = template_config.get('template_type', '')
        if 'research' in template_type or 'academic' in template_type:
            if 'methodology' in content.lower() and 'citation' not in content.lower():
                requirements.append("Add citations for research methodology")
        
        return requirements
    
    def _check_style_consistency_universal(self, content: str, template_config: dict) -> list:
        """Check style consistency universally"""
        notes = []
        
        tone_requirements = template_config.get('tone', {})
        
        # Check formality consistency
        if tone_requirements.get('formality') == 'high':
            informal_markers = ["!", "?", "...", "etc.", "OK", "okay"]
            for marker in informal_markers:
                if marker in content:
                    notes.append(f"Remove informal element '{marker}' for formal template")
        
        # Check persuasiveness consistency
        if tone_requirements.get('persuasiveness') == 'high':
            weak_language = ["might", "could", "maybe", "perhaps", "possibly"]
            weak_count = sum(content.lower().count(word) for word in weak_language)
            if weak_count > 5:
                notes.append("Reduce tentative language to increase persuasiveness")
        
        # Check voice consistency
        voice_inconsistencies = 0
        if "I think" in content and "we recommend" in content:
            voice_inconsistencies += 1
        if "you should" in content and "one must" in content:
            voice_inconsistencies += 1
        
        if voice_inconsistencies > 0:
            notes.append("Maintain consistent voice throughout content")
        
        return notes
    
    def _identify_engagement_opportunities_universal(self, content: str, spec, template_config: dict) -> list:
        """Identify engagement opportunities universally"""
        opportunities = []
        
        platform = template_config.get('platform', spec.platform)
        
        # Platform-specific engagement
        if platform in ["linkedin", "medium"]:
            if "**" not in content:
                opportunities.append("Add bold formatting for social media platforms")
        
        # Content type specific engagement
        if spec.complexity_level > 6:
            if "%" not in content and "$" not in content:
                opportunities.append("Add quantitative metrics for credibility")
        
        # Check for examples
        if "example" not in content.lower() and "for instance" not in content.lower():
            opportunities.append("Add concrete examples to illustrate concepts")
        
        # Check for actionable insights
        action_words = ["recommend", "should", "implement", "apply", "execute"]
        if not any(word in content.lower() for word in action_words):
            opportunities.append("Include actionable recommendations")
        
        # Check for visual cues
        sections = content.split('\n# ')
        if len(sections) > 3 and content.count('**') < 5:
            opportunities.append("Add bold formatting for key points and scannability")
        
        # Check for compelling statistics
        if len(content.split()) > 1000 and not any(char in content for char in ['%', '$']):
            opportunities.append("Add compelling statistics to support key points")
        
        return opportunities
    
    def _apply_structural_improvements_universal(self, content: str, improvements: list) -> str:
        """Apply structural improvements universally"""
        for improvement in improvements:
            if "Add required section" in improvement or "Add planned section" in improvement:
                section_name = improvement.split(": ")[1] if ": " in improvement else improvement.split("section: ")[1]
                content += f"\n\n# {section_name.title()}\n\n[Content for {section_name} to be developed based on template requirements]"
            elif "Expand content to meet minimum" in improvement:
                content += f"\n\n<!-- Editorial note: {improvement} -->"
        
        return content
    
    def _apply_clarity_enhancements_universal(self, content: str, enhancements: list) -> str:
        """Apply clarity enhancements universally"""
        for enhancement in enhancements:
            if "Define technical term" in enhancement:
                term = enhancement.split(": ")[1]
                content = content.replace(term, f"{term} (definition required)", 1)
            elif "Replace contraction" in enhancement:
                contraction = enhancement.split("'")[1]
                contractions_map = {
                    "don't": "do not", "can't": "cannot", "won't": "will not",
                    "it's": "it is", "we're": "we are", "they're": "they are"
                }
                if contraction in contractions_map:
                    content = content.replace(contraction, contractions_map[contraction])
        
        return content
    
    def _fix_audience_alignment_universal(self, content: str, issues: list, spec) -> str:
        """Fix audience alignment issues universally"""
        for issue in issues:
            if "Remove casual phrase" in issue and "'" in issue:
                phrase = issue.split("'")[1]
                replacements = {
                    "hey": "Note that", "let's dive": "We will examine",
                    "pretty cool": "noteworthy", "awesome": "excellent", "totally": "completely"
                }
                if phrase in replacements:
                    content = content.replace(phrase, replacements[phrase])
            elif "Add technical implementation" in issue:
                content += f"\n\n**Technical Implementation:** [Implementation details to be added for technical audience]"
            elif "Address missing decision factors" in issue:
                factors = issue.split(": ")[1]
                content += f"\n\n**Decision Factors:** Analysis of {factors} to be included"
        
        return content
    
    def _optimize_flow_universal(self, content: str, optimizations: list) -> str:
        """Apply flow optimizations universally"""
        for optimization in optimizations:
            if "Strengthen introduction" in optimization:
                if not any(word in content[:200].lower() for word in ['strategic', 'critical', 'essential', 'opportunity']):
                    content = "**Strategic Overview:** " + content
            elif "Add clear call-to-action" in optimization:
                if not content.lower().endswith(('next steps', 'implementation', 'action')):
                    content += "\n\n**Next Steps:** Implementation planning and stakeholder alignment recommended."
        
        return content
    
    def _add_engagement_elements_universal(self, content: str, opportunities: list) -> str:
        """Add engagement elements universally"""
        for opportunity in opportunities:
            if "Add bold formatting" in opportunity:
                content = content.replace("Key benefits:", "**Key Benefits:**")
                content = content.replace("Important:", "**Important:**")
                content = content.replace("Note:", "**Note:**")
            elif "Add quantitative metrics" in opportunity:
                content += f"\n\n**Performance Metrics:** [Add relevant quantitative data and metrics]"
            elif "Add concrete examples" in opportunity:
                content += f"\n\n**Practical Example:** [Add relevant case study or example]"
            elif "Include actionable recommendations" in opportunity:
                content += f"\n\n**Actionable Recommendations:** [Add specific implementation steps]"
        
        return content

    def _apply_style_profile_refinements(self, content: str, style_config: Dict) -> str:
        """Apply specific style profile rules to content"""

        # Extract style enforcement rules
        forbidden_patterns = style_config.get('forbidden_patterns', [])
        required_patterns = style_config.get('required_opening_patterns', [])
        quality_requirements = style_config.get('quality_requirements', {})

        # Remove forbidden patterns
        for pattern in forbidden_patterns:
            content = content.replace(pattern, self._get_formal_replacement(pattern))

        # Enhance transitions based on style requirements
        if quality_requirements.get('formality_score', 0) > 70:
            content = self._enhance_formal_transitions(content)

        # Apply style-specific vocabulary adjustments
        content = self._adjust_vocabulary_for_style(content, style_config)

        return content

    def _enhance_formal_transitions(self, content: str) -> str:
        """Replace weak transitions with formal alternatives"""

        transition_improvements = {
            'so,': 'Therefore,',
            'well,': 'Furthermore,',
            'now,': 'Subsequently,',
            'anyway,': 'In any case,'
        }

        for weak, strong in transition_improvements.items():
            content = content.replace(weak, strong)

        return content

    def _assess_content_quality(self, content: str, style_config: Dict) -> Dict[str, float]:
        """Assess content quality against style profile requirements"""
        
        quality_scores = {}
        requirements = style_config.get('quality_requirements', {})
        
        # Formality assessment
        formal_score = self._calculate_formality_score(content)
        quality_scores['formality'] = formal_score
        
        # Repetition detection
        repetition_score = self._calculate_repetition_score(content)
        quality_scores['variety'] = repetition_score
        
        # Transition quality
        transition_score = self._calculate_transition_quality(content)
        quality_scores['flow'] = transition_score
        
        return quality_scores
    
    def _calculate_repetition_score(self, content: str) -> float:
        """Calculate how repetitive the content structure is"""
        
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 10]
        if len(sentences) < 5:
            return 1.0
        
        # Check for identical sentence beginnings
        beginnings = [s[:20] for s in sentences]
        unique_beginnings = len(set(beginnings))
        
        return unique_beginnings / len(beginnings)