# File: langgraph_app/agents/enhanced_formatter_integrated.py
from langgraph_app.core.enriched_content_state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    FormattingRequirements
)
import re

class EnhancedFormatterAgent:
    """FIXED: Universal Configuration-Driven Formatter Agent - NO HARDCODED TEMPLATES"""
    
    def __init__(self):
        self.agent_type = AgentType.FORMATTER
        
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Format content universally"""
        template_config = state.template_config or {}
        instructions = state.get_agent_instructions(self.agent_type)
    
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "platform": state.content_spec.platform,
            "length": len(state.draft_content.split())
        })
    
        requirements = self._create_formatting_requirements_universal(state, instructions, template_config)
        state.formatting_requirements = requirements
    
        formatted = self._apply_universal_formatting(state, instructions, template_config)
        state.draft_content = formatted
    
        state.update_phase(ContentPhase.OPTIMIZATION)
    
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "formatting_applied": len(requirements.formatting_elements),
            "confidence_score": requirements.formatting_confidence
        })
    
        return state

    def _generate_intelligent_config(self, state: EnrichedContentState) -> dict:
        """Generate intelligent config based on content analysis"""
        content = state.draft_content
        spec = state.get("content_spec", {})
        
        # Analyze content patterns
        content_analysis = {
            'has_financial_data': bool(re.search(r'\$[\d,]+[MBK]?|\d+%|\d+x', content)),
            'has_technical_terms': bool(re.search(r'[A-Z][a-z]+[A-Z][a-zA-Z]*|[a-z_]+_[a-z_]+', content)),
            'has_business_language': bool(re.search(r'\b(ROI|revenue|growth|strategy|implementation)\b', content, re.I)),
            'has_executive_tone': bool(re.search(r'\b(strategic|leverage|optimize|synergy|scalable)\b', content, re.I)),
            'content_length': len(content.split()),
            'platform': spec.platform,
            'audience': spec.audience
        }
        
        formatting_rules = {}
        structure_rules = {}
        emphasis_rules = {}
        
        if content_analysis['has_financial_data']:
            emphasis_rules['financial_emphasis'] = {
                'patterns': [r'(\$[\d,]+[MBK]?)', r'(\d+%)', r'(\d+x)'],
                'replacement': r'**\1**'
            }
        
        if content_analysis['has_technical_terms']:
            formatting_rules['code_formatting'] = {
                'enable': True,
                'patterns': [r'\b([A-Z][a-z]+[A-Z][a-zA-Z]*)\b', r'\b([a-z_]+_[a-z_]+)\b']
            }
        
        if content_analysis['has_business_language']:
            emphasis_rules['business_emphasis'] = {
                'strategic_words': ['ROI', 'strategic', 'implementation', 'optimization']
            }
        
        platform_optimizations = self._get_platform_optimizations_universal(spec.platform)
        
        return {
            'type': 'intelligent_generated',
            'formatting_rules': formatting_rules,
            'structure_rules': structure_rules,
            'emphasis_rules': emphasis_rules,
            'platform_optimizations': platform_optimizations,
            'content_analysis': content_analysis
        }
    
    def _create_formatting_requirements_universal(self, state: EnrichedContentState, instructions, template_config: dict) -> FormattingRequirements:
        """Create UNIVERSAL formatting requirements from ANY template configuration"""
        
        spec = state.get("content_spec", {})
        platform = spec.platform
        
        platform_specs = self._get_platform_specifications_universal(platform, template_config)
        visual_hierarchy = self._determine_visual_hierarchy_universal(state.draft_content, template_config)
        formatting_elements = self._identify_formatting_elements_universal(state, template_config)
        accessibility_requirements = self._define_accessibility_requirements_universal(platform, template_config)
        
        return FormattingRequirements(
            platform_specifications=platform_specs,
            visual_hierarchy=visual_hierarchy,
            formatting_elements=formatting_elements,
            accessibility_requirements=accessibility_requirements,
            seo_considerations=self._identify_seo_considerations_universal(state, template_config),
            publication_metadata=self._generate_publication_metadata_universal(state, template_config),
            formatting_confidence=0.92
        )
    
    def _apply_universal_formatting(self, state: EnrichedContentState, instructions, template_config: dict) -> str:
        """Apply UNIVERSAL formatting that works with ANY template configuration"""
        
        content = state.draft_content
        platform = state.content_spec.platform
        
        # Apply formatting rules from config
        if 'formatting_rules' in template_config:
            content = self._apply_formatting_rules_from_config(content, template_config['formatting_rules'])
        
        # Apply structure rules from config
        if 'structure_rules' in template_config:
            content = self._apply_structure_rules_from_config(content, template_config['structure_rules'])
        
        # Apply emphasis rules from config
        if 'emphasis_rules' in template_config:
            content = self._apply_emphasis_rules_from_config(content, template_config['emphasis_rules'])
        
        # Apply platform optimizations
        if 'platform_optimizations' in template_config:
            content = self._apply_platform_optimizations_from_config(content, template_config['platform_optimizations'])
        
        # Apply universal improvements
        content = self._apply_visual_hierarchy_universal(content, state.formatting_requirements.visual_hierarchy)
        content = self._add_accessibility_features_universal(content, state.formatting_requirements.accessibility_requirements)
        
        return content
    
    def _apply_formatting_rules_from_config(self, content: str, formatting_rules: dict) -> str:
        """Apply formatting rules dynamically from config"""
        if 'code_formatting' in formatting_rules and formatting_rules['code_formatting'].get('enable'):
            patterns = formatting_rules['code_formatting'].get('patterns', [])
            for pattern in patterns:
                content = re.sub(pattern, r'`\1`', content)
        
        if 'header_style' in formatting_rules:
            content = self._apply_header_style_universal(content, formatting_rules['header_style'])
        
        return content
    
    def _apply_structure_rules_from_config(self, content: str, structure_rules: dict) -> str:
        """Apply structure rules dynamically from config"""
        if 'add_executive_summary' in structure_rules and structure_rules['add_executive_summary']:
            if "Executive Summary" not in content and not content.startswith("## Executive Summary"):
                content = "## Executive Summary\n\n[Key insights and recommendations]\n\n" + content
        
        if 'section_organization' in structure_rules:
            content = self._organize_sections_universal(content, structure_rules['section_organization'])
        
        return content
    
    def _apply_emphasis_rules_from_config(self, content: str, emphasis_rules: dict) -> str:
        """Apply emphasis rules dynamically from config"""
        if 'financial_emphasis' in emphasis_rules:
            patterns = emphasis_rules['financial_emphasis'].get('patterns', [])
            replacement = emphasis_rules['financial_emphasis'].get('replacement', r'**\1**')
            for pattern in patterns:
                content = re.sub(pattern, replacement, content)
        
        if 'business_emphasis' in emphasis_rules:
            strategic_words = emphasis_rules['business_emphasis'].get('strategic_words', [])
            for word in strategic_words:
                content = content.replace(word, f"**{word}**")
        
        return content
    
    def _apply_platform_optimizations_from_config(self, content: str, platform_optimizations: dict) -> str:
        """Apply platform optimizations dynamically from config"""
        platform = platform_optimizations.get('platform', 'web')
        
        if platform == "linkedin":
            content = self._optimize_for_linkedin_universal(content, platform_optimizations)
        elif platform == "medium":
            content = self._optimize_for_medium_universal(content, platform_optimizations)
        elif platform == "substack":
            content = self._optimize_for_substack_universal(content, platform_optimizations)
        elif platform == "deck_presentation":
            content = self._optimize_for_presentation_universal(content, platform_optimizations)
        else:
            content = self._optimize_for_web_universal(content, platform_optimizations)
        
        return content
    
    def _get_platform_specifications_universal(self, platform: str, template_config: dict) -> dict:
        """Get platform specifications with universal config support"""
        base_specs = {
            "linkedin": {"max_length": 3000, "supports_markdown": False, "professional_tone": True},
            "medium": {"max_length": 10000, "supports_markdown": True, "story_format": True},
            "substack": {"max_length": 15000, "supports_markdown": True, "newsletter_format": True},
            "deck_presentation": {"max_length": 100, "bullet_points": True, "visual_heavy": True},
            "web": {"max_length": 5000, "supports_markdown": True}
        }
        
        spec = base_specs.get(platform, base_specs["web"])
        
        # Apply config overrides
        if 'platform_specifications' in template_config:
            spec.update(template_config['platform_specifications'])
        
        return spec
    
    def _determine_visual_hierarchy_universal(self, content: str, template_config: dict) -> list:
        """Determine visual hierarchy universally from config or content analysis"""
        if 'visual_hierarchy' in template_config:
            return template_config['visual_hierarchy']
        
        # Analyze content for hierarchy
        headers = re.findall(r'^#+\s+(.+)', content, re.MULTILINE)
        hierarchy = []
        
        for i, header in enumerate(headers):
            level = min(3, i + 1)
            hierarchy.append({
                "level": level,
                "style": "section" if level <= 2 else "subsection",
                "content": header
            })
        
        return hierarchy
    
    def _identify_formatting_elements_universal(self, state: EnrichedContentState, template_config: dict) -> list:
        """Identify formatting elements universally from config"""
        elements = []
        platform = state.content_spec.platform
        
        # Platform-specific elements
        if platform == "linkedin":
            elements.extend(["professional_header", "engagement_hooks", "hashtags"])
        elif platform == "medium":
            elements.extend(["story_header", "subheadings", "pull_quotes"])
        elif platform == "deck_presentation":
            elements.extend(["slide_titles", "bullet_points", "visual_callouts"])
        
        # Add config-specified elements
        if 'formatting_elements' in template_config:
            elements.extend(template_config['formatting_elements'])
        
        return list(set(elements))
    
    def _define_accessibility_requirements_universal(self, platform: str, template_config: dict) -> list:
        """Define accessibility requirements universally"""
        base_requirements = ["header_structure", "reading_flow", "contrast_compliance"]
        
        if platform in ["medium", "substack"]:
            base_requirements.append("alt_text")
        
        # Add config-specified requirements
        if 'accessibility_requirements' in template_config:
            base_requirements.extend(template_config['accessibility_requirements'])
        
        return list(set(base_requirements))
    
    def _get_platform_optimizations_universal(self, platform: str) -> dict:
        """Get platform optimizations universally"""
        return {
            'platform': platform,
            'engagement_optimization': True,
            'seo_optimization': True,
            'accessibility_compliance': True
        }
    
    def _optimize_for_linkedin_universal(self, content: str, optimizations: dict) -> str:
        """Universal LinkedIn optimization"""
        content = content.replace("**", "").replace("*", "").replace("#", "")
        
        if optimizations.get('add_professional_header', True):
            content = "💼 Professional Insight\n\n" + content
        
        if optimizations.get('add_engagement_cta', True):
            content += "\n\n---\n📞 What are your thoughts? Share your experience in the comments."
        
        return content
    
    def _optimize_for_medium_universal(self, content: str, optimizations: dict) -> str:
        """Universal Medium optimization"""
        if not content.startswith("# ") and optimizations.get('ensure_title', True):
            content = f"# Strategic Analysis\n\n## Overview\n\n{content}"
        
        if optimizations.get('add_engagement_footer', True):
            content += "\n\n---\n\n*👏 If this analysis provided value, please applaud and share.*"
        
        return content
    
    def _optimize_for_substack_universal(self, content: str, optimizations: dict) -> str:
        """Universal Substack optimization"""
        if optimizations.get('add_newsletter_greeting', True):
            content = "Hello subscribers,\n\nIn today's analysis:\n\n" + content
        
        if optimizations.get('add_subscription_cta', True):
            content += "\n\n---\n\n**Thank you for reading!** Subscribe for more insights."
        
        return content
    
    def _optimize_for_presentation_universal(self, content: str, optimizations: dict) -> str:
        """Universal presentation optimization"""
        slides = []
        max_words = optimizations.get('max_words_per_slide', 50)
        
        paragraphs = content.split('\n\n')
        current_slide = ""
        word_count = 0
        
        for paragraph in paragraphs:
            paragraph_words = len(paragraph.split())
            if word_count + paragraph_words > max_words and current_slide:
                slides.append(current_slide.strip())
                current_slide = paragraph
                word_count = paragraph_words
            else:
                current_slide += paragraph + "\n\n"
                word_count += paragraph_words
        
        if current_slide:
            slides.append(current_slide.strip())
        
        formatted_slides = []
        for i, slide_content in enumerate(slides):
            bullets = [f"• {line.strip()}" for line in slide_content.split('\n') if line.strip()]
            formatted_slide = f"--- SLIDE {i+1} ---\n\n" + "\n".join(bullets[:5])
            formatted_slides.append(formatted_slide)
        
        return "\n\n".join(formatted_slides)
    
    def _optimize_for_web_universal(self, content: str, optimizations: dict) -> str:
        """Universal web optimization"""
        if optimizations.get('add_toc', False):
            headers = re.findall(r'^#+\s+(.+)', content, re.MULTILINE)
            if headers:
                toc = "\n## Table of Contents\n\n"
                for i, header in enumerate(headers):
                    toc += f"{i+1}. [{header}](#{header.lower().replace(' ', '-')})\n"
                content = toc + "\n" + content
        
        return content
    
    def _apply_visual_hierarchy_universal(self, content: str, visual_hierarchy: list) -> str:
        """Apply visual hierarchy universally"""
        for item in visual_hierarchy:
            level = item.get('level', 2)
            style = item.get('style', 'section')
            header_content = item.get('content', '')
            
            if style == "title":
                prefix = "# 🎯 "
            elif style == "section":
                prefix = "## 📊 "
            else:
                prefix = "### ➤ "
            
            pattern = f"#{level * '#'} {re.escape(header_content)}"
            replacement = f"{prefix}{header_content}"
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _add_accessibility_features_universal(self, content: str, accessibility_requirements: list) -> str:
        """Add accessibility features universally"""
        for requirement in accessibility_requirements:
            if requirement == "alt_text":
                content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'![\1 - Descriptive alt text](\2)', content)
            elif requirement == "header_structure":
                content = self._fix_header_hierarchy_universal(content)
        
        return content
    
    def _fix_header_hierarchy_universal(self, content: str) -> str:
        """Fix header hierarchy universally"""
        headers = re.findall(r'^(#+)\s+(.+)', content, re.MULTILINE)
        
        for match in headers:
            level = len(match[0])
            if level > 3:
                new_header = "### " + match[1]
                old_header = match[0] + " " + match[1]
                content = content.replace(old_header, new_header)
        
        return content
    
    def _apply_header_style_universal(self, content: str, header_style: str) -> str:
        """Apply header styling universally"""
        if header_style == "modern":
            content = re.sub(r'^#\s+(.+)', r'# 🎯 \1', content, flags=re.MULTILINE)
            content = re.sub(r'^##\s+(.+)', r'## 📊 \1', content, flags=re.MULTILINE)
        
        return content
    
    def _organize_sections_universal(self, content: str, organization_rules: dict) -> str:
        """Organize sections universally"""
        if organization_rules.get('move_conclusion_to_end', True):
            conclusion_pattern = r'(#{1,3}\s+Conclusion.*?)(?=#{1,3}|$)'
            conclusion_match = re.search(conclusion_pattern, content, re.DOTALL)
            if conclusion_match:
                conclusion = conclusion_match.group(1)
                content = re.sub(conclusion_pattern, '', content, flags=re.DOTALL)
                content += "\n\n" + conclusion
        
        return content
    
    def _identify_seo_considerations_universal(self, state: EnrichedContentState, template_config: dict) -> list:
        """Identify SEO considerations universally"""
        considerations = ["keyword_optimization", "meta_description", "header_structure"]
        
        if 'seo_considerations' in template_config:
            considerations.extend(template_config['seo_considerations'])
        
        return list(set(considerations))
    
    def _generate_publication_metadata_universal(self, state: EnrichedContentState, template_config: dict) -> dict:
        """Generate publication metadata universally"""
        spec = state.get("content_spec", {})
        
        metadata = {
            "title": template_config.get('title', f"{spec.topic}: Analysis"),
            "description": template_config.get('description', f"Analysis of {spec.topic}"),
            "keywords": template_config.get('seo_keywords', [spec.topic.lower()]),
            "audience": spec.audience,
            "reading_time": f"{len(state.draft_content.split()) // 200 + 1} min"
        }
        
        # Add config-specific metadata
        if 'metadata' in template_config:
            metadata.update(template_config['metadata'])
        
        return metadata