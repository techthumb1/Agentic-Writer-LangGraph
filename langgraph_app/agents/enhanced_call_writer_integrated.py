# File: langgraph_app/agents/enhanced_call_writer_integrated.py
from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase
)

class EnhancedCallWriterAgent:
    """Integrated Call Writer Agent - Coordinates writing process across multiple content sections"""
    
    def __init__(self):
        self.agent_type = AgentType.CALL_WRITER
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute call writer coordination with full context awareness"""
        # INJECT: Extract template_config
        template_config = getattr(state, 'template_config', {})
        if not template_config and hasattr(state, 'content_spec'):
            template_config = state.content_spec.business_context.get('template_config', {})
        
        # Get dynamic instructions
        instructions = state.get_agent_instructions(self.agent_type)
        
        # Log execution start
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "content_sections": len(self._extract_sections(state.draft_content)),
            "coordination_scope": instructions.specific_requirements.get("coordination_scope", "full_content"),
            "consistency_checks": len(instructions.specific_requirements.get("consistency_checks", []))
        })
        
        # Coordinate writing process
        coordinated_content = self._coordinate_writing_process(state, instructions)
        state.draft_content = coordinated_content
        
        # Update writing context with coordination insights
        if state.writing_context:
            state.writing_context.writing_confidence *= 1.1  # Boost confidence after coordination
        
        # Log completion
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "coordination_improvements": len(self._identify_improvements(state.draft_content)),
            "consistency_score": self._calculate_consistency_score(coordinated_content),
            "final_content_length": len(coordinated_content.split())
        })
        
        return state
    
    def _coordinate_writing_process(self, state: EnrichedContentState, instructions) -> str:
        """Coordinate the writing process for consistency and quality"""

        content = state.draft_content
        spec = state.content_spec
        planning = state.planning_output
        research = state.research_findings

        # INJECT: Extract template_config
        template_config = getattr(state, 'template_config', {})
        if not template_config:
            template_config = spec.business_context.get('template_config', {})

        # USE: Template-specific coordination
        if template_config.get('section_order'):
            content = self._enforce_template_section_order(content, template_config)

        if template_config.get('tone', {}).get('formality') == 'high':
            content = self._enforce_formal_tone(content)

        # Coordinate with code agent if needed
        content = self._coordinate_with_code_agent(content, state, template_config)

        # Coordinate with image agent if needed
        content = self._coordinate_with_image_agent(content, state, template_config)

        # Apply coordination strategies based on instructions
        coordination_scope = instructions.specific_requirements.get("coordination_scope", "full_content")

        if coordination_scope == "full_content":
            content = self._coordinate_full_content(content, state, instructions)
        elif coordination_scope == "section_level":
            content = self._coordinate_sections(content, state, instructions)

        # Apply consistency checks
        content = self._enforce_template_structure(content, template_config, state)

        return content
    
    def _coordinate_full_content(self, content: str, state: EnrichedContentState, instructions) -> str:
        """Coordinate entire content for consistency and flow"""
        
        # Ensure voice consistency throughout
        content = self._ensure_voice_consistency(content, state)
        
        # Optimize section transitions
        content = self._optimize_section_transitions(content, state)
        
        # Validate narrative coherence
        content = self._ensure_narrative_coherence(content, state)
        
        # Optimize content structure
        content = self._optimize_content_structure(content, state)
        
        return content
    
    def _coordinate_sections(self, content: str, state: EnrichedContentState, instructions) -> str:
        """Coordinate individual sections for consistency"""
        
        sections = content.split('\n# ')
        coordinated_sections = []
        
        for i, section in enumerate(sections):
            if i == 0 and not section.startswith('#'):
                # First section (title)
                coordinated_sections.append(section)
            else:
                # Process each section
                section_content = f"# {section}" if not section.startswith('#') else section
                coordinated_section = self._coordinate_individual_section(section_content, state, i)
                coordinated_sections.append(coordinated_section)
        
        return '\n\n'.join(coordinated_sections)
    
    def _enforce_template_structure(self, content: str, template_config: dict, state: EnrichedContentState) -> str:
        """Enforce template-specific structure"""

        section_order = template_config.get('section_order', [])
        if not section_order:
            return content

        # Ensure content follows section order
        sections = content.split('\n# ')
        current_sections = [s.split('\n')[0].replace('#', '').strip() for s in sections if s.strip()]

        # Reorder if needed
        missing_sections = [s for s in section_order if s not in current_sections]
        for missing in missing_sections:
            content += f"\n\n# {missing}\n\n[Section content for {missing}]"

        return content

    def _ensure_voice_consistency(self, content: str, state: EnrichedContentState) -> str:
        """Ensure consistent voice throughout content"""
        
        writing_context = state.writing_context
        if not writing_context:
            return content
        
        voice_characteristics = writing_context.voice_characteristics
        
        # Check for voice inconsistencies
        if "professional" in voice_characteristics:
            # Replace casual phrases with professional alternatives
            content = content.replace("let's", "we will")
            content = content.replace("can't", "cannot")
            content = content.replace("don't", "do not")
            content = content.replace("won't", "will not")
        
        if "authoritative" in voice_characteristics:
            # Strengthen weak language
            content = content.replace("might be", "is")
            content = content.replace("could potentially", "will")
            content = content.replace("seems to suggest", "demonstrates")
        
        if "technical" in voice_characteristics:
            # Ensure technical precision
            content = content.replace("about", "approximately")
            content = content.replace("pretty much", "essentially")
            content = content.replace("kind of", "")
        
        return content
    
    def _optimize_section_transitions(self, content: str, state: EnrichedContentState) -> str:
        """Optimize transitions between sections"""
        
        sections = content.split('\n# ')
        if len(sections) < 2:
            return content
        
        optimized_sections = [sections[0]]  # Keep first section as-is
        
        for i in range(1, len(sections)):
            current_section = f"# {sections[i]}"
            previous_section_end = optimized_sections[-1].split('\n\n')[-1]
            
            # Add transition if missing
            transition = self._generate_section_transition(
                previous_section_end, 
                current_section, 
                state
            )
            
            if transition:
                optimized_sections[-1] += f"\n\n{transition}"
            
            optimized_sections.append(current_section)
        
        return '\n\n'.join(optimized_sections)
    
    def _ensure_narrative_coherence(self, content: str, state: EnrichedContentState) -> str:
        """Ensure narrative coherence throughout content"""
        
        planning = state.planning_output
        if not planning:
            return content
        
        # Check if key messages are consistently reinforced
        key_messages = planning.key_messages
        content_strategy = planning.content_strategy
        
        # Ensure strategy is reflected throughout
        if "investor_focused" in content_strategy:
            # Add investor-relevant context where missing
            if "ROI" not in content and "return" not in content.lower():
                content = self._add_investor_context(content)
        elif "technical_deep_dive" in content_strategy:
            # Ensure technical depth is consistent
            if "implementation" not in content.lower():
                content = self._add_technical_context(content)
        
        return content
    
    def _optimize_content_structure(self, content: str, state: EnrichedContentState) -> str:
        """Optimize overall content structure"""
        
        spec = state.content_spec
        planning = state.planning_output
        
        # Ensure template-appropriate structure
        if spec.template_type == "business_proposal":
            content = self._optimize_business_proposal_structure(content, state)
        elif spec.template_type == "technical_documentation":
            content = self._optimize_technical_doc_structure(content, state)
        
        return content
    
    def _apply_consistency_checks(self, content: str, checks: list, state: EnrichedContentState) -> str:
        """Apply specific consistency checks"""
        
        for check in checks:
            if check == "voice":
                content = self._check_voice_consistency(content, state)
            elif check == "tone":
                content = self._check_tone_consistency(content, state)
            elif check == "terminology":
                content = self._check_terminology_consistency(content, state)
            elif check == "style":
                content = self._check_style_consistency(content, state)
        
        return content
    
    def _coordinate_individual_section(self, section: str, state: EnrichedContentState, section_index: int) -> str:
        """Coordinate individual section for consistency"""
        
        # Extract section title and content
        lines = section.split('\n')
        title = lines[0] if lines else ""
        section_content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
        
        # Apply section-specific coordination
        if "executive" in title.lower() or "summary" in title.lower():
            section_content = self._coordinate_executive_section(section_content, state)
        elif "problem" in title.lower() or "opportunity" in title.lower():
            section_content = self._coordinate_problem_section(section_content, state)
        elif "solution" in title.lower() or "value" in title.lower():
            section_content = self._coordinate_solution_section(section_content, state)
        elif "financial" in title.lower() or "roi" in title.lower():
            section_content = self._coordinate_financial_section(section_content, state)
        elif "implementation" in title.lower():
            section_content = self._coordinate_implementation_section(section_content, state)
        
        return f"{title}\n{section_content}"
    
    def _generate_section_transition(self, previous_end: str, current_section: str, state: EnrichedContentState) -> str:
        """Generate appropriate transition between sections"""
        
        current_title = current_section.split('\n')[0].replace('#', '').strip()
        
        if "financial" in current_title.lower():
            return "Building on this strategic foundation, the financial analysis demonstrates compelling investment potential."
        elif "implementation" in current_title.lower():
            return "With the strategic framework established, the following implementation approach ensures successful execution."
        elif "solution" in current_title.lower():
            return "Addressing these identified challenges requires a comprehensive solution approach."
        
        return f"This analysis leads directly to {current_title.lower()}."
    
    def _coordinate_executive_section(self, content: str, state: EnrichedContentState) -> str:
        """Coordinate executive summary for maximum impact"""
        
        spec = state.content_spec
        research = state.research_findings
        
        # Ensure executive summary has all key elements
        required_elements = ["opportunity", "solution", "impact", "next steps"]
        
        for element in required_elements:
            if element not in content.lower():
                content = self._add_executive_element(content, element, state)
        
        return content
    
    def _coordinate_problem_section(self, content: str, state: EnrichedContentState) -> str:
        """Coordinate problem section for clarity and impact"""
        
        # Ensure problem is quantified
        if "$" not in content and "%" not in content:
            content = self._add_quantification(content, "problem", state)
        
        return content
    
    def _coordinate_solution_section(self, content: str, state: EnrichedContentState) -> str:
        """Coordinate solution section for clarity"""
        
        # Ensure solution directly addresses stated problems
        planning = state.planning_output
        if planning and planning.key_messages:
            for message in planning.key_messages:
                if message.lower() not in content.lower():
                    content += f"\n\nAdditionally, our approach addresses {message.lower()} through systematic implementation and continuous optimization."
        
        return content
    
    def _coordinate_financial_section(self, content: str, state: EnrichedContentState) -> str:
        """Coordinate financial section for investor clarity"""
        
        # Ensure financial section has clear ROI presentation
        if "ROI" not in content and "return" not in content.lower():
            content += f"\n\n**Return on Investment:** Conservative projections indicate substantial ROI within 18-24 months of implementation."
        
        return content
    
    def _coordinate_implementation_section(self, content: str, state: EnrichedContentState) -> str:
        """Coordinate implementation section for actionability"""
        
        # Ensure implementation has clear next steps
        if "next steps" not in content.lower():
            content += f"\n\n**Immediate Next Steps:** Executive approval, team formation, and project initiation planning."
        
        return content
    
    def _check_voice_consistency(self, content: str, state: EnrichedContentState) -> str:
        """Check and fix voice consistency issues"""
        
        writing_context = state.writing_context
        if not writing_context:
            return content
        
        # Implementation of voice consistency checks
        return self._ensure_voice_consistency(content, state)
    
    def _check_tone_consistency(self, content: str, state: EnrichedContentState) -> str:
        """Check and fix tone consistency issues"""
        
        writing_context = state.writing_context
        if not writing_context:
            return content
        
        tone_adaptation = writing_context.tone_adaptation
        
        # Adjust for formal tone
        if tone_adaptation.get("formal", 0) > 0.7:
            content = content.replace("!", ".")
            content = content.replace("?", " for consideration.")
        
        return content
    
    def _check_terminology_consistency(self, content: str, state: EnrichedContentState) -> str:
        """Ensure consistent terminology throughout"""
        
        spec = state.content_spec
        
        # Create terminology map for consistency
        terminology_map = {
            "AI": "artificial intelligence",
            "ML": "machine learning", 
            "ROI": "return on investment"
        }
        
        # Apply consistent terminology based on audience
        if spec.complexity_level < 6:
            # Use full terms for less technical audiences
            for abbrev, full_term in terminology_map.items():
                if abbrev in content and full_term not in content:
                    content = content.replace(abbrev, f"{full_term} ({abbrev})", 1)
        
        return content
    
    def _check_style_consistency(self, content: str, state: EnrichedContentState) -> str:
        """Check and fix style consistency issues"""
        
        # Ensure consistent formatting
        content = content.replace("**", "**")  # Normalize bold formatting
        content = content.replace("##", "##")  # Normalize headers
        
        return content
    
    def _extract_sections(self, content: str) -> list:
        """Extract sections from content"""
        
        import re
        sections = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        return sections
    
    def _identify_improvements(self, content: str) -> list:
        """Identify coordination improvements made"""
        
        improvements = []
        
        if "**" in content:
            improvements.append("Added emphasis formatting")
        if "Building on" in content or "This leads to" in content:
            improvements.append("Enhanced section transitions")
        if len(content.split('\n# ')) > 1:
            improvements.append("Coordinated section structure")
        
        return improvements
    
    def _calculate_consistency_score(self, content: str) -> float:
        """Calculate consistency score for the content"""
        
        score = 0.8  # Base score
        
        # Check for consistent formatting
        if content.count("**") % 2 == 0:  # Even number of bold markers
            score += 0.05
        
        # Check for section transitions
        transition_words = ["building on", "this leads", "following", "next"]
        if any(word in content.lower() for word in transition_words):
            score += 0.1
        
        # Check for consistent voice
        casual_words = ["let's", "can't", "don't", "won't"]
        if not any(word in content.lower() for word in casual_words):
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _add_executive_element(self, content: str, element: str, state: EnrichedContentState) -> str:
        """Add missing executive summary element"""
        
        if element == "opportunity" and "opportunity" not in content.lower():
            content += f"\n\n**Market Opportunity:** Significant potential in the {state.content_spec.business_context.get('industry', 'technology')} sector."
        elif element == "next steps" and "next steps" not in content.lower():
            content += f"\n\n**Next Steps:** Executive review and implementation planning recommended."
        
        return content
    
    def _add_quantification(self, content: str, section_type: str, state: EnrichedContentState) -> str:
        """Add quantification to sections that need it"""
        
        if section_type == "problem":
            content += f"\n\nQuantified Impact: Current inefficiencies represent measurable opportunity for improvement and cost reduction."
        
        return content
    
    def _add_investor_context(self, content: str) -> str:
        """Add investor-relevant context"""
        
        if "investment" not in content.lower():
            content += f"\n\nInvestment Perspective: This opportunity represents compelling risk-adjusted returns with clear exit strategies."
        
        return content
    
    def _add_technical_context(self, content: str) -> str:
        """Add technical implementation context"""
        
        if "technical" not in content.lower():
            content += f"\n\nTechnical Implementation: Systematic approach ensures reliable deployment and scalable architecture."
        
        return content
    
    def _optimize_business_proposal_structure(self, content: str, state: EnrichedContentState) -> str:
        """Optimize structure for business proposals"""
        
        # Ensure business proposal has proper section order
        required_order = ["executive", "problem", "solution", "financial", "implementation"]
        
        sections = content.split('\n# ')
        current_order = []
        
        for section in sections:
            section_lower = section.lower()
            for req in required_order:
                if req in section_lower:
                    current_order.append(req)
                    break
        
        # Add note if sections are out of order
        if current_order != required_order[:len(current_order)]:
            content += f"\n\n<!-- Note: Consider reordering sections for optimal business proposal flow -->"
        
        return content
    
    def _optimize_technical_doc_structure(self, content: str, state: EnrichedContentState) -> str:
        """Optimize structure for technical documentation"""
        
        # Ensure technical docs have proper progression
        if "prerequisites" not in content.lower():
            content = f"## Prerequisites\n\nBefore implementing this solution, ensure the following requirements are met.\n\n{content}"
        
        return content
    
    def _coordinate_with_code_agent(self, content: str, state: EnrichedContentState, template_config: dict) -> str:
        """Coordinate with code agent for technical content"""

        # Check if code examples are needed
        template_type = template_config.get('template_type', state.content_spec.template_type)

        if template_type in ["technical_documentation", "api_documentation"]:
            # Ensure code sections exist
            if not state.generated_code and "implementation" in content.lower():
                content += f"\n\n## Code Examples\n\n[Code examples will be generated by the code agent]"

        # Add code placeholders where mentioned
        if "code example" in content.lower() and "```" not in content:
            content = content.replace("code example", "code example:\n\n```python\n# Code example placeholder\n```")

        return content

    def _coordinate_with_image_agent(self, content: str, state: EnrichedContentState, template_config: dict) -> str:
        """Coordinate with image agent for visual content"""
        
        # Check if images are needed based on template
        template_type = template_config.get('template_type', state.content_spec.template_type)
        platform = template_config.get('platform', state.content_spec.platform)
        
        needs_images = (
            template_type in ["business_proposal", "venture_capital_pitch"] or
            platform in ["linkedin", "medium", "instagram"]
        )
        
        if needs_images:
            # Add image placeholder if none exists
            if "[Image:" not in content and "![" not in content:
                content = f"[Image: Professional diagram illustrating {state.content_spec.topic}]\n\n" + content
        
        return content
    
    def _enforce_template_section_order(self, content: str, template_config: dict) -> str:
        """Enforce template-defined section order"""
        
        section_order = template_config.get('section_order', [])
        if not section_order:
            return content
        
        # Extract current sections
        import re
        sections = re.split(r'\n(?=# )', content)
        section_dict = {}
        
        for section in sections:
            if section.startswith('# '):
                title = section.split('\n')[0].replace('# ', '').strip()
                section_dict[title] = section
        
        # Reorder according to template
        reordered_content = []
        for required_section in section_order:
            if required_section in section_dict:
                reordered_content.append(section_dict[required_section])
            else:
                # Add missing section
                reordered_content.append(f"# {required_section}\n\n[Content for {required_section} section]")
        
        return '\n\n'.join(reordered_content)
    
    def _enforce_formal_tone(self, content: str) -> str:
        """Enforce formal tone based on template requirements"""
        
        # Replace casual language
        formal_replacements = {
            "let's": "we will",
            "can't": "cannot", 
            "don't": "do not",
            "won't": "will not",
            "it's": "it is",
            "we're": "we are"
        }
        
        for casual, formal in formal_replacements.items():
            content = content.replace(casual, formal)
        
        return content