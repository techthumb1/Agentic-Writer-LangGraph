from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    EditingGuidance
)

class EnhancedEditorAgent:
    """Integrated Editor Agent using EnrichedContentState"""
    
    def __init__(self):
        self.agent_type = AgentType.EDITOR
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute editing with full context awareness"""
        
        # Get dynamic instructions
        instructions = state.get_agent_instructions(self.agent_type)
        
        # Log execution start
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "content_length": len(state.draft_content.split()),
            "has_writing_context": bool(state.writing_context),
            "target_audience": state.content_spec.audience
        })
        
        # Generate editing guidance
        editing_guidance = self._create_editing_guidance(state, instructions)
        state.editing_guidance = editing_guidance
        
        # Edit content based on guidance
        edited_content = self._edit_content_with_guidance(state, instructions)
        state.draft_content = edited_content  # Update draft with edits
        
        # Update phase
        state.update_phase(ContentPhase.FORMATTING)
        
        # Log completion
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "improvements_made": len(editing_guidance.structural_improvements),
            "confidence_score": editing_guidance.editing_confidence,
            "final_length": len(edited_content.split())
        })
        
        return state
    
    def _create_editing_guidance(self, state: EnrichedContentState, instructions) -> EditingGuidance:
        """Create editing guidance based on content analysis"""
        
        content = state.draft_content
        spec = state.content_spec
        planning = state.planning_output
        research = state.research_findings
        writing_context = state.writing_context
        
        # Analyze content for improvements
        structural_improvements = self._identify_structural_improvements(content, planning)
        clarity_enhancements = self._identify_clarity_enhancements(content, spec)
        audience_alignment_issues = self._check_audience_alignment(content, spec, planning)
        flow_optimizations = self._identify_flow_optimizations(content)
        fact_checking_requirements = self._identify_fact_checking_needs(content, research)
        
        return EditingGuidance(
            structural_improvements=structural_improvements,
            clarity_enhancements=clarity_enhancements,
            audience_alignment_issues=audience_alignment_issues,
            flow_optimizations=flow_optimizations,
            fact_checking_requirements=fact_checking_requirements,
            style_consistency_notes=self._check_style_consistency(content, writing_context),
            engagement_opportunities=self._identify_engagement_opportunities(content, spec),
            editing_confidence=0.82
        )
    
    def _edit_content_with_guidance(self, state: EnrichedContentState, instructions) -> str:
        """Edit content based on guidance and instructions"""
        
        content = state.draft_content
        guidance = state.editing_guidance
        spec = state.content_spec
        
        # Apply structural improvements
        content = self._apply_structural_improvements(content, guidance.structural_improvements)
        
        # Enhance clarity
        content = self._apply_clarity_enhancements(content, guidance.clarity_enhancements)
        
        # Fix audience alignment issues
        content = self._fix_audience_alignment(content, guidance.audience_alignment_issues, spec)
        
        # Optimize flow
        content = self._optimize_flow(content, guidance.flow_optimizations)
        
        # Add engagement elements
        content = self._add_engagement_elements(content, guidance.engagement_opportunities)
        
        return content
    
    def _identify_structural_improvements(self, content: str, planning) -> list:
        """Identify structural improvements needed"""
        
        improvements = []
        
        # Check for missing elements based on planning
        if planning and planning.estimated_sections:
            planned_sections = [section["name"].lower() for section in planning.estimated_sections]
            content_lower = content.lower()
            
            for section in planned_sections:
                if section not in content_lower:
                    improvements.append(f"Add missing section: {section}")
        
        # Check section balance
        sections = content.split('\n# ')
        if len(sections) > 1:
            section_lengths = [len(section.split()) for section in sections]
            avg_length = sum(section_lengths) / len(section_lengths)
            
            for i, length in enumerate(section_lengths):
                if length < avg_length * 0.5:
                    improvements.append(f"Expand section {i+1} - too brief")
                elif length > avg_length * 2:
                    improvements.append(f"Condense section {i+1} - too lengthy")
        
        # Check for logical flow
        if "# Executive Summary" not in content and "business_proposal" in content.lower():
            improvements.append("Add executive summary for business proposal")
        
        return improvements
    
    def _identify_clarity_enhancements(self, content: str, spec) -> list:
        """Identify clarity enhancements needed"""
        
        enhancements = []
        
        # Check for jargon based on audience
        if spec.complexity_level < 6:
            # Check for technical terms that might need explanation
            technical_terms = ["ROI", "KPI", "API", "SaaS", "ML", "AI"]
            for term in technical_terms:
                if term in content and f"({term}" not in content:
                    enhancements.append(f"Define or explain technical term: {term}")
        
        # Check sentence length and complexity
        sentences = content.split('. ')
        long_sentences = [i for i, s in enumerate(sentences) if len(s.split()) > 25]
        if long_sentences:
            enhancements.append(f"Break down {len(long_sentences)} overly complex sentences")
        
        # Check for unclear transitions
        paragraphs = content.split('\n\n')
        for i in range(1, len(paragraphs)):
            if not any(word in paragraphs[i][:50].lower() for word in 
                      ['however', 'therefore', 'additionally', 'furthermore', 'consequently']):
                if len(paragraphs[i]) > 100:  # Only flag substantial paragraphs
                    enhancements.append(f"Add transition to paragraph {i+1}")
        
        return enhancements
    
    def _check_audience_alignment(self, content: str, spec, planning) -> list:
        """Check for audience alignment issues"""
        
        issues = []
        
        # Check formality level
        if "investor" in spec.audience.lower() or "executive" in spec.audience.lower():
            casual_phrases = ["hey", "let's dive", "pretty cool", "awesome", "totally"]
            for phrase in casual_phrases:
                if phrase in content.lower():
                    issues.append(f"Remove casual phrase inappropriate for {spec.audience}: '{phrase}'")
        
        # Check technical depth
        if "technical" in spec.audience.lower() and spec.complexity_level > 7:
            if "implementation" not in content.lower():
                issues.append("Add technical implementation details for technical audience")
        elif "beginner" in spec.audience.lower() and spec.complexity_level < 4:
            if len([w for w in content.split() if len(w) > 12]) > 20:
                issues.append("Simplify vocabulary for beginner audience")
        
        # Check decision factors alignment
        if planning and planning.audience_insights:
            decision_factors = planning.audience_insights.get("decision_factors", [])
            content_lower = content.lower()
            missing_factors = [factor for factor in decision_factors 
                             if factor.lower() not in content_lower]
            if missing_factors:
                issues.append(f"Address missing decision factors: {', '.join(missing_factors)}")
        
        return issues
    
    def _identify_flow_optimizations(self, content: str) -> list:
        """Identify flow optimization opportunities"""
        
        optimizations = []
        
        # Check introduction effectiveness
        intro_paragraph = content.split('\n\n')[0] if '\n\n' in content else content[:200]
        if not any(word in intro_paragraph.lower() for word in 
                  ['opportunity', 'challenge', 'solution', 'impact', 'strategic']):
            optimizations.append("Strengthen introduction with compelling hook")
        
        # Check conclusion strength
        if '\n\n' in content:
            conclusion = content.split('\n\n')[-1]
            if not any(word in conclusion.lower() for word in 
                      ['next steps', 'recommendation', 'action', 'implementation']):
                optimizations.append("Add clear call-to-action in conclusion")
        
        # Check section connections
        sections = content.split('\n# ')
        if len(sections) > 2:
            for i in range(1, len(sections)-1):
                section_end = sections[i].split('\n\n')[-1]
                next_section_start = sections[i+1].split('\n\n')[0]
                
                # Simple heuristic for connection
                if len(section_end) < 50 or "next" not in section_end.lower():
                    optimizations.append(f"Improve connection between sections {i+1} and {i+2}")
        
        return optimizations
    
    def _identify_fact_checking_needs(self, content: str, research) -> list:
        """Identify fact-checking requirements"""
        
        requirements = []
        
        # Check for unsupported claims
        claim_indicators = ["studies show", "research indicates", "data reveals", "statistics prove"]
        for indicator in claim_indicators:
            if indicator in content.lower():
                requirements.append(f"Verify and cite source for claim with '{indicator}'")
        
        # Cross-reference with research findings
        if research and research.statistical_evidence:
            research_stats = [stat["statistic"] for stat in research.statistical_evidence]
            # Simple check for statistical claims
            import re
            percentages = re.findall(r'\d+%', content)
            for percentage in percentages:
                if not any(percentage in stat for stat in research_stats):
                    requirements.append(f"Verify source for statistic: {percentage}")
        
        return requirements
    
    def _check_style_consistency(self, content: str, writing_context) -> list:
        """Check style consistency throughout content"""
        
        notes = []
        
        if not writing_context:
            return notes
        
        # Check voice consistency
        voice_chars = writing_context.voice_characteristics
        if "professional" in voice_chars:
            # Check for inconsistent casual language
            casual_words = content.lower().count("we'll") + content.lower().count("don't") + content.lower().count("can't")
            if casual_words > 5:
                notes.append("Reduce contractions to maintain professional voice")
        
        # Check tone consistency
        tone_adaptation = writing_context.tone_adaptation
        if tone_adaptation.get("formal", 0) > 0.7:
            # Check for informal elements
            informal_elements = ["!", "?", "..."]
            total_informal = sum(content.count(elem) for elem in informal_elements)
            if total_informal > 10:
                notes.append("Reduce informal punctuation to maintain formal tone")
        
        return notes
    
    def _identify_engagement_opportunities(self, content: str, spec) -> list:
        """Identify opportunities to increase engagement"""
        
        opportunities = []
        
        # Check for compelling statistics
        if "%" not in content and "business" in spec.template_type:
            opportunities.append("Add compelling statistics to support key points")
        
        # Check for examples
        if "example" not in content.lower() and "for instance" not in content.lower():
            opportunities.append("Add concrete examples to illustrate key concepts")
        
        # Check for actionable insights
        if "recommend" not in content.lower() and "should" not in content.lower():
            opportunities.append("Include actionable recommendations")
        
        # Check for visual cues
        sections = content.split('\n# ')
        if len(sections) > 3 and "**" not in content:
            opportunities.append("Add bold formatting for key points and improved scannability")
        
        return opportunities
    
    def _apply_structural_improvements(self, content: str, improvements: list) -> str:
        """Apply structural improvements to content"""
        
        for improvement in improvements:
            if "Add missing section" in improvement:
                section_name = improvement.split(": ")[1]
                # Add placeholder for missing section
                content += f"\n\n# {section_name.title()}\n\n[Section content to be developed]"
            
            elif "Expand section" in improvement:
                # Add note for expansion
                content += f"\n\n<!-- Editorial note: {improvement} -->"
        
        return content
    
    def _apply_clarity_enhancements(self, content: str, enhancements: list) -> str:
        """Apply clarity enhancements to content"""
        
        for enhancement in enhancements:
            if "Define or explain technical term" in enhancement:
                term = enhancement.split(": ")[1]
                # Add definition in parentheses
                content = content.replace(term, f"{term} (definition needed)", 1)
        
        return content
    
    def _fix_audience_alignment(self, content: str, issues: list, spec) -> str:
        """Fix audience alignment issues"""
        
        for issue in issues:
            if "Remove casual phrase" in issue and "'" in issue:
                phrase = issue.split("'")[1]
                # Replace casual phrases with professional alternatives
                replacements = {
                    "hey": "Note that",
                    "let's dive": "We will examine",
                    "pretty cool": "noteworthy",
                    "awesome": "excellent",
                    "totally": "completely"
                }
                if phrase in replacements:
                    content = content.replace(phrase, replacements[phrase])
        
        return content
    
    def _optimize_flow(self, content: str, optimizations: list) -> str:
        """Apply flow optimizations"""
        
        for optimization in optimizations:
            if "Strengthen introduction" in optimization:
                # Add strategic opening if missing
                if not content.startswith("**Strategic"):
                    content = "**Strategic Overview:** " + content
            
            elif "Add clear call-to-action" in optimization:
                if not content.endswith("next steps") and not content.endswith("implementation"):
                    content += "\n\n**Next Steps:** Implementation planning and stakeholder alignment recommended to proceed with proposed recommendations."
        
        return content
    
    def _add_engagement_elements(self, content: str, opportunities: list) -> str:
        """Add engagement elements based on opportunities"""
        
        for opportunity in opportunities:
            if "Add bold formatting" in opportunity:
                # Add bold formatting to key phrases
                content = content.replace("Key benefits:", "**Key Benefits:**")
                content = content.replace("Important:", "**Important:**")
                content = content.replace("Note:", "**Note:**")
        
        return content