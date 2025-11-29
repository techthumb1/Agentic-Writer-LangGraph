# File: langgraph_app/agents/enhanced_call_writer_integrated.py

from langgraph_app.core.state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase
)

# File: langgraph_app/agents/enhanced_call_writer_integrated.py

from langgraph_app.core.state import EnrichedContentState, AgentType
from datetime import datetime

class EnhancedCallWriterAgent:
    """Call Writer agent that prepares writing instructions"""
    
    def __init__(self):
        self.agent_type = AgentType.CALL_WRITER
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute call writer logic with proper dataclass access"""
        
        # Update state
        state.current_agent = "call_writer"
        state.updated_at = datetime.now().isoformat()
        
        # Extract planning data using attribute access instead of getattr()
        planning_output = state.planning_output
        if planning_output:
            content_strategy = getattr(planning_output, 'content_strategy', 'balanced_approach')
            structure_approach = getattr(planning_output, 'structure_approach', 'standard_structure')
            key_messages = getattr(planning_output, 'key_messages', [])
            research_priorities = getattr(planning_output, 'research_priorities', [])
        else:
            content_strategy = 'balanced_approach'
            structure_approach = 'standard_structure'
            key_messages = []
            research_priorities = []
        
        # Create writing instructions
        writing_instructions = {
            "strategy": content_strategy,
            "structure": structure_approach,
            "key_messages": key_messages,
            "research_context": research_priorities,
            "template_type": state.content_spec.template_type,
            "target_audience": state.content_spec.target_audience,
            "topic": state.content_spec.topic
        }
        
        # Store instructions for writer
        state.writing_instructions = writing_instructions
        
        # Update debug info
        if not state.debug_info:
            state.debug_info = {}
            
        state.debug_info.update({
            "call_writer_execution": {
                "timestamp": datetime.now().isoformat(),
                "action": "writing_instructions_prepared",
                "strategy": content_strategy,
                "structure": structure_approach,
                "key_messages_count": len(key_messages)
            }
        })
        
        return state

    def _coordinate_writing_process(self, state: EnrichedContentState, instructions) -> str:
        """Coordinate the writing process for consistency and quality"""
        
        content = state.draft_content or state.content or ""
        spec = state.content_spec
        planning = state.planning_output
        research = state.research_findings
        
        # Extract template_config
        template_config = getattr(state, 'template_config', {})
        if not template_config and spec:
            template_config = spec.business_context.get('template_config', {})
        
        # Use template-specific coordination
        if template_config.get('section_order'):
            content = self._enforce_template_section_order(content, template_config)
        
        if template_config.get('tone', {}).get('formality') == 'high':
            content = self._enforce_formal_tone(content)
        
        # Coordinate with code agent if needed
        content = self._coordinate_with_code_agent(content, state, template_config)
        
        # Coordinate with image agent if needed  
        content = self._coordinate_with_image_agent(content, state, template_config)
        
        # Apply coordination strategies based on instructions
        coordination_scope = "full_content"
        if instructions and isinstance(instructions, dict):
            specific_req = instructions.get("specific_requirements", {})
            if isinstance(specific_req, dict):
                coordination_scope = specific_req.get("coordination_scope", "full_content")
        
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
                coordinated_sections.append(section)
            else:
                section_content = f"# {section}" if not section.startswith('#') else section
                coordinated_section = self._coordinate_individual_section(section_content, state, i)
                coordinated_sections.append(coordinated_section)
        
        return '\n\n'.join(coordinated_sections)
    
    def _ensure_voice_consistency(self, content: str, state: EnrichedContentState) -> str:
        """Ensure consistent voice throughout content"""
        
        writing_context = state.writing_context or {}
        voice_characteristics = writing_context.get('voice_characteristics', [])
        
        if "professional" in voice_characteristics:
            content = content.replace("let's", "we will")
            content = content.replace("can't", "cannot")
            content = content.replace("don't", "do not")
            content = content.replace("won't", "will not")
        
        if "authoritative" in voice_characteristics:
            content = content.replace("might be", "is")
            content = content.replace("could potentially", "will")
            content = content.replace("seems to suggest", "demonstrates")
        
        if "technical" in voice_characteristics:
            content = content.replace("about", "approximately")
            content = content.replace("pretty much", "essentially")
            content = content.replace("kind of", "")
        
        return content
    
    def _optimize_section_transitions(self, content: str, state: EnrichedContentState) -> str:
        """Optimize transitions between sections"""
        
        sections = content.split('\n# ')
        if len(sections) < 2:
            return content
        
        optimized_sections = [sections[0]]
        
        for i in range(1, len(sections)):
            current_section = f"# {sections[i]}"
            previous_section_end = optimized_sections[-1].split('\n\n')[-1]
            
            transition = self._generate_section_transition(previous_section_end, current_section, state)
            
            if transition:
                optimized_sections[-1] += f"\n\n{transition}"
            
            optimized_sections.append(current_section)
        
        return '\n\n'.join(optimized_sections)
    
    def _ensure_narrative_coherence(self, content: str, state: EnrichedContentState) -> str:
        """Ensure narrative coherence throughout content"""
        
        planning = state.planning_output
        key_messages = getattr(planning, 'key_messages', []) if planning else []
        content_strategy = getattr(planning, 'content_strategy', '') if planning else ''


        if "investor_focused" in content_strategy:
            if "ROI" not in content and "return" not in content.lower():
                content = self._add_investor_context(content)
        elif "technical_deep_dive" in content_strategy:
            if "implementation" not in content.lower():
                content = self._add_technical_context(content)
        
        return content
    
#    def _optimize_content_structure(self, content: str, state: EnrichedContentState) -> str:
#        """Optimize overall content structure"""
#        
#        spec = state.content_spec
#        if not spec:
#            return content
#        
#        if spec.template_type == "business_proposal":
#            content = self._optimize_business_proposal_structure(content, state)
#        elif spec.template_type == "technical_documentation":
#            content = self._optimize_technical_doc_structure(content, state)
#        
#        return content
    
    def _coordinate_individual_section(self, section: str, state: EnrichedContentState, section_index: int) -> str:
        """Coordinate individual section for consistency"""
        
        lines = section.split('\n')
        title = lines[0] if lines else ""
        section_content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
        
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
        
        required_elements = ["opportunity", "solution", "impact", "next steps"]
        
        for element in required_elements:
            if element not in content.lower():
                content = self._add_executive_element(content, element, state)
        
        return content
    
    def _coordinate_problem_section(self, content: str, state: EnrichedContentState) -> str:
        """Coordinate problem section for clarity and impact"""
        
        if "$" not in content and "%" not in content:
            content = self._add_quantification(content, "problem", state)
        
        return content
    
    def _coordinate_solution_section(self, content: str, state: EnrichedContentState) -> str:
        """Coordinate solution section for clarity"""
        
        planning = state.planning_output
        key_messages = getattr(planning, 'key_messages', []) if planning else []

        for message in key_messages:
            if message.lower() not in content.lower():
                content += f"\n\nAdditionally, our approach addresses {message.lower()} through systematic implementation and continuous optimization."
        
        return content
    
    def _coordinate_financial_section(self, content: str, state: EnrichedContentState) -> str:
        """Coordinate financial section for investor clarity"""
        
        if "ROI" not in content and "return" not in content.lower():
            content += f"\n\n**Return on Investment:** Conservative projections indicate substantial ROI within 18-24 months of implementation."
        
        return content
    
    def _coordinate_implementation_section(self, content: str, state: EnrichedContentState) -> str:
        """Coordinate implementation section for actionability"""
        
        if "next steps" not in content.lower():
            content += f"\n\n**Immediate Next Steps:** Executive approval, team formation, and project initiation planning."
        
        return content
    
    def _calculate_consistency_score(self, content: str) -> float:
        """Calculate consistency score for the content"""
        
        score = 0.8
        
        if content.count("**") % 2 == 0:
            score += 0.05
        
        transition_words = ["building on", "this leads", "following", "next"]
        if any(word in content.lower() for word in transition_words):
            score += 0.1
        
        casual_words = ["let's", "can't", "don't", "won't"]
        if not any(word in content.lower() for word in casual_words):
            score += 0.05
        
        return min(score, 1.0)
    
    def _add_executive_element(self, content: str, element: str, state: EnrichedContentState) -> str:
        """Add missing executive summary element"""
        
        if element == "opportunity" and "opportunity" not in content.lower():
            industry = "technology"
            if state.content_spec and state.content_spec.business_context:
                industry = state.content_spec.business_context.get('industry', 'technology')
            content += f"\n\n**Market Opportunity:** Significant potential in the {industry} sector."
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
        
        required_order = ["executive", "problem", "solution", "financial", "implementation"]
        
        sections = content.split('\n# ')
        current_order = []
        
        for section in sections:
            section_lower = section.lower()
            for req in required_order:
                if req in section_lower:
                    current_order.append(req)
                    break
        
        if current_order != required_order[:len(current_order)]:
            content += f"\n\n<!-- Note: Consider reordering sections for optimal business proposal flow -->"
        
        return content
    
    def _optimize_technical_doc_structure(self, content: str, state: EnrichedContentState) -> str:
        """Optimize structure for technical documentation"""
        
        if "prerequisites" not in content.lower():
            content = f"## Prerequisites\n\nBefore implementing this solution, ensure the following requirements are met.\n\n{content}"
        
        return content
    
#    def _coordinate_with_code_agent(self, content: str, state: EnrichedContentState, template_config: dict) -> str:
#        """Coordinate with code agent for technical content"""
#        
#        template_type = template_config.get('template_type')
#        if not template_type and state.content_spec:
#            template_type = state.content_spec.template_type
#        
#        if template_type in ["technical_documentation", "api_documentation"]:
#            if not state.generated_code and "implementation" in content.lower():
#                content += f"\n\n## Code Examples\n\n[Code examples will be generated by the code agent]"
#        
#        if "code example" in content.lower() and "```" not in content:
#            content = content.replace("code example", "code example:\n\n```python\n# Code example placeholder\n```")
#        
#        return content
    
    def _coordinate_with_image_agent(self, content: str, state: EnrichedContentState, template_config: dict) -> str:
        """Coordinate with image agent for visual content"""
        
        template_type = template_config.get('template_type')
        if not template_type and state.content_spec:
            template_type = state.content_spec.template_type
        
        needs_images = template_type in ["business_proposal", "venture_capital_pitch"]
        
        if needs_images:
            if "[Image:" not in content and "![" not in content:
                topic = "content"
                if state.content_spec:
                    topic = state.content_spec.topic
                content = f"[Image: Professional diagram illustrating {topic}]\n\n" + content
        
        return content
    
    def _enforce_template_section_order(self, content: str, template_config: dict) -> str:
        """Enforce template-defined section order"""
        
        section_order = template_config.get('section_order', [])
        if not section_order:
            return content
        
        import re
        sections = re.split(r'\n(?=# )', content)
        section_dict = {}
        
        for section in sections:
            if section.startswith('# '):
                title = section.split('\n')[0].replace('# ', '').strip()
                section_dict[title] = section
        
        reordered_content = []
        for required_section in section_order:
            if required_section in section_dict:
                reordered_content.append(section_dict[required_section])
            else:
                reordered_content.append(f"# {required_section}\n\n[Content for {required_section} section]")
        
        return '\n\n'.join(reordered_content)
    
    def _enforce_formal_tone(self, content: str) -> str:
        """Enforce formal tone based on template requirements"""
        
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
    
    def _enforce_template_structure(self, content: str, template_config: dict, state: EnrichedContentState) -> str:
        """Enforce template-specific structure"""
        
        section_order = template_config.get('section_order', [])
        if not section_order:
            return content
        
        sections = content.split('\n# ')
        current_sections = [s.split('\n')[0].replace('#', '').strip() for s in sections if s.strip()]
        
        missing_sections = [s for s in section_order if s not in current_sections]
        for missing in missing_sections:
            content += f"\n\n# {missing}\n\n[Section content for {missing}]"
        
        return content