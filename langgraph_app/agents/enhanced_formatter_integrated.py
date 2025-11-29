# langgraph_app/agents/enhanced_formatter_integrated.py
"""
Enterprise Formatter Agent - PASSTHROUGH MODE FOR TESTING
"""

import os
import logging
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

from langgraph_app.core.state import EnrichedContentState, AgentType, ContentPhase
from langgraph_app.core.types import FormattedContent, FormattingRequirements
from langgraph_app.enhanced_model_registry import get_model, get_model_for_generation

logger = logging.getLogger(__name__)


# Tool definitions for Formatter agent
@tool
def remove_ai_tells(text: str) -> Dict[str, Any]:
    """Remove AI-generated content markers from text."""
    ai_tell_patterns = {
        r'\bdelve into\b': 'examine',
        r'\bdelving\b': 'examining',
        r'\bshowcase\b': 'demonstrate',
        r'\bleverage\b': 'use',
        r'\butilize\b': 'use',
        r'\bin the realm of\b': 'in',
        r'\bit\'s worth noting that\b': 'notably',
        r'\bit is important to note that\b': 'importantly',
        r'\bin conclusion\b': 'finally',
        r'\bin summary\b': 'overall',
        r'\bcrucial\b': 'important',
        r'\bparadigm shift\b': 'change',
        r'\bgame-changer\b': 'significant innovation'
    }
    
    cleaned = text
    removals = []
    
    for pattern, replacement in ai_tell_patterns.items():
        matches = re.findall(pattern, cleaned, re.I)
        if matches:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.I)
            removals.append({
                "pattern": pattern,
                "replacement": replacement,
                "count": len(matches)
            })
    
    return {
        "cleaned_text": cleaned,
        "removals": removals,
        "total_removed": len(removals)
    }


@tool
def optimize_for_platform(text: str, platform: str) -> Dict[str, Any]:
    """Optimize content formatting for specific platform."""
    optimizations = []
    optimized = text
    
    if platform.lower() == "linkedin":
        if "**" not in optimized:
            optimized = re.sub(r'^(#+\s+.+)$', r'**\1**', optimized, flags=re.M)
            optimizations.append("Added bold formatting for headers")
        
        paragraphs = optimized.split('\n\n')
        if any(len(p.split()) > 100 for p in paragraphs):
            optimizations.append("Long paragraphs detected - consider breaking up")
    
    elif platform.lower() == "medium":
        if not optimized.startswith('#'):
            optimized = f"# {optimized.split(chr(10))[0]}\n\n" + '\n'.join(optimized.split('\n')[1:])
            optimizations.append("Added H1 header")
    
    elif platform.lower() in ["web", "blog"]:
        if optimized.count('#') < 3:
            optimizations.append("Consider adding more section headers for scannability")
    
    return {
        "optimized_text": optimized,
        "platform": platform,
        "optimizations_applied": optimizations
    }


@tool
def format_citations(sources: List[Dict], style: str = "apa") -> str:
    """Format research sources as citations."""
    if style.lower() == "apa":
        citations = []
        for idx, source in enumerate(sources, 1):
            url = source.get('url', '')
            domain = urlparse(url).netloc if url else 'Unknown'
            title = source.get('title', 'Untitled')
            year = source.get('published_date', 'n.d.')[:4] if source.get('published_date') else 'n.d.'
            
            citation = f"{idx}. {title}. ({year}). {domain}. {url}"
            citations.append(citation)
        
        return "\n".join(citations)
    
    return ""


class EnhancedFormatterAgent:
    """Enterprise Formatter Agent - PASSTHROUGH MODE"""
    
    def __init__(self):
        self.agent_type = AgentType.FORMATTER
        self.tools = [remove_ai_tells, optimize_for_platform, format_citations]
        
        self.platform_configs = {
            "web": {"max_heading_levels": 6, "supports_markdown": True},
            "linkedin": {"max_heading_levels": 3, "supports_markdown": False},
            "medium": {"max_heading_levels": 6, "supports_markdown": True},
            "email": {"max_heading_levels": 2, "supports_markdown": False}
        }
    
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute formatter - PASSTHROUGH MODE."""
        
        logger.info("🎨 FORMATTER: Starting (PASSTHROUGH MODE)")
        
        # Extract content
        content = None
        
        if state.edited_content:
            if hasattr(state.edited_content, 'body'):
                content = state.edited_content.body
            elif isinstance(state.edited_content, str):
                content = state.edited_content
        
        if not content and state.draft_content:
            if hasattr(state.draft_content, 'body'):
                content = state.draft_content.body
            elif isinstance(state.draft_content, str):
                content = state.draft_content
        
        if not content:
            content = state.content
        
        if not content or not content.strip():
            logger.error(f"No content found. edited={type(state.edited_content)}, draft={type(state.draft_content)}, content={type(state.content)}")
            raise RuntimeError("ENTERPRISE: Formatter requires content")
        
        logger.info(f"📝 Formatter received: {len(content)} chars, {len(content.split())} words")
        
        template_config = state.template_config or {}
        style_config = state.style_config or {}
        
        platform = (state.content_spec.platform if state.content_spec 
                   else template_config.get('platform', 'web'))
        
        # PASSTHROUGH - no LLM
        formatted_content, metadata = self._llm_format_with_tools(
            content,
            platform,
            template_config,
            style_config,
            state
        )
        
        logger.info(f"✅ Formatter output: {len(formatted_content)} chars, {len(formatted_content.split())} words")
        
        # Set content
        state.content = formatted_content
        state.formatted_content = FormattedContent(
            markdown=formatted_content,
            html=self._convert_to_html(formatted_content) if platform in ["web", "medium"] else None,
            metadata=metadata
        )
        
        state.update_phase(ContentPhase.OPTIMIZATION)
        
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "platform": platform,
            "word_count": len(formatted_content.split()),
            "formatting_confidence": metadata.get('confidence', 0.9)
        })
        
        logger.info(f"✅ FORMATTER: Completed for platform={platform}")
        
        return state
    
    def _llm_format_with_tools(
        self,
        content: str,
        platform: str,
        template_config: Dict,
        style_config: Dict,
        state: EnrichedContentState
    ) -> tuple[str, Dict]:
        """PASSTHROUGH - Direct return without LLM."""
        
        logger.info(f"🔄 Formatter passthrough: {len(content)} chars")
        
        metadata = {
            "platform": platform,
            "confidence": 1.0,
            "chars": len(content),
            "words": len(content.split()),
            "mode": "passthrough"
        }
        
        return content, metadata
    
    def _build_formatting_system_prompt(
        self,
        platform: str,
        template_config: Dict,
        style_config: Dict
    ) -> str:
        """Build system prompt for formatting."""
        
        template_type = template_config.get('template_type', 'content')
        platform_config = self.platform_configs.get(platform, self.platform_configs['web'])
        
        prompt = f"""You are an expert content formatter specializing in {platform} platform.

**Formatting Objectives:**
- Apply platform-specific formatting optimizations
- Remove all AI-generated tells and markers
- Ensure visual hierarchy and scannability
- Maintain professional appearance
- Optimize for {platform} best practices

**Platform Constraints:**
- Max heading levels: {platform_config['max_heading_levels']}
- Markdown support: {'Yes' if platform_config['supports_markdown'] else 'No'}
- Content type: {template_type}

**Formatting Rules:**
1. Use proper markdown syntax (headers, bold, lists)
2. Add visual breaks between sections
3. Highlight key points with bold or quotes
4. Ensure consistent formatting throughout
5. Remove generic transitions and AI tells
6. Add citations if research sources provided

**Critical Instructions:**
- Use available tools to analyze and optimize
- Never sacrifice content quality for formatting
- Maintain factual accuracy - never fabricate
- Focus on readability and professional polish"""
        
        return prompt
    
    def _convert_to_html(self, markdown: str) -> str:
        """Convert markdown to HTML (basic implementation)."""
        
        html = markdown
        
        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.M)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.M)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.M)
        
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'
        
        return html