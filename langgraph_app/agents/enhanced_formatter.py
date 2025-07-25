# File: langgraph_app/agents/enhanced_formatter.py
# Enhanced Formatter Agent with Multi-Format Support and Template Integration

import os
import re
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import base64
import html

from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class OutputFormat(Enum):
    """Supported output formats"""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    PLAIN_TEXT = "plain_text"
    RICH_TEXT = "rich_text"
    STRUCTURED_DATA = "structured_data"
    EMAIL_HTML = "email_html"
    SOCIAL_MEDIA = "social_media"
    PDF_READY = "pdf_ready"
    DOCX_READY = "docx_ready"

class FormattingStyle(Enum):
    """Formatting style presets"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    RICH = "rich"
    ACADEMIC = "academic"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    SOCIAL = "social"

@dataclass
class FormattingRules:
    """Formatting rules and preferences"""
    format_type: OutputFormat
    style_preset: FormattingStyle
    preserve_structure: bool = True
    add_toc: bool = False
    include_metadata: bool = True
    apply_styling: bool = True
    optimize_for_platform: str = ""
    custom_css: str = ""
    custom_template: str = ""

@dataclass
class FormattingResult:
    """Result of formatting operation"""
    formatted_content: str
    format_type: OutputFormat
    metadata: Dict[str, Any]
    assets: Dict[str, str] = field(default_factory=dict)  # CSS, images, etc.
    export_ready: bool = False
    file_extensions: List[str] = field(default_factory=list)

class IntelligentFormatterAgent:
    """
    Enhanced formatter agent with multi-format support, template integration,
    and intelligent formatting based on content type and target platform.
    """
    
    def __init__(self, model_registry=None):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except ImportError:
            logger.warning("OpenAI not available, using basic formatting")
            self.client = None
            
        self.model_registry = model_registry
        
        # Formatting templates
        self.html_templates = {
            "minimal": self._get_minimal_html_template(),
            "standard": self._get_standard_html_template(),
            "rich": self._get_rich_html_template(),
            "academic": self._get_academic_html_template(),
            "professional": self._get_professional_html_template()
        }
        
        # CSS styles
        self.css_styles = {
            "minimal": self._get_minimal_css(),
            "standard": self._get_standard_css(),
            "rich": self._get_rich_css(),
            "academic": self._get_academic_css(),
            "professional": self._get_professional_css()
        }
        
        # Platform-specific formatting rules
        self.platform_rules = {
            "medium": {"max_length": 100000, "format": OutputFormat.HTML, "style": FormattingStyle.STANDARD},
            "linkedin": {"max_length": 3000, "format": OutputFormat.PLAIN_TEXT, "style": FormattingStyle.PROFESSIONAL},
            "twitter": {"max_length": 280, "format": OutputFormat.PLAIN_TEXT, "style": FormattingStyle.SOCIAL},
            "github": {"max_length": 50000, "format": OutputFormat.MARKDOWN, "style": FormattingStyle.TECHNICAL},
            "email": {"max_length": 10000, "format": OutputFormat.EMAIL_HTML, "style": FormattingStyle.PROFESSIONAL},
            "blog": {"max_length": 50000, "format": OutputFormat.HTML, "style": FormattingStyle.STANDARD},
            "documentation": {"max_length": 100000, "format": OutputFormat.MARKDOWN, "style": FormattingStyle.TECHNICAL}
        }

    async def intelligent_format(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main formatting method that applies intelligent formatting based on context
        """
        logger.info("Starting intelligent formatting")
        
        try:
            # Extract content and formatting requirements
            content = self._extract_content(state)
            if not content:
                return self._create_error_response(state, "No content provided for formatting")
            
            # Determine formatting requirements
            formatting_rules = self._determine_formatting_rules(state)
            
            # Apply intelligent formatting
            formatting_result = await self._apply_formatting(content, formatting_rules, state)
            
            # Generate additional formats if requested
            additional_formats = await self._generate_additional_formats(formatting_result, state)
            
            # Create comprehensive response
            response = {
                **state,
                "formatted_content": formatting_result.formatted_content,
                "formatting_metadata": {
                    "format_type": formatting_result.format_type.value,
                    "style_applied": formatting_rules.style_preset.value,
                    "platform_optimized": formatting_rules.optimize_for_platform,
                    "export_ready": formatting_result.export_ready,
                    "file_extensions": formatting_result.file_extensions,
                    "content_length": len(formatting_result.formatted_content),
                    "formatting_applied": True
                },
                "formatting_assets": formatting_result.assets,
                "additional_formats": additional_formats
            }
            
            logger.info(f"Formatting completed: {formatting_result.format_type.value} format with {formatting_rules.style_preset.value} style")
            return response
            
        except Exception as e:
            logger.error(f"Formatting failed: {e}")
            return self._create_error_response(state, str(e))

    def _extract_content(self, state: Dict[str, Any]) -> str:
        """Extract content from state for formatting"""
        return (
            state.get("seo_optimized_content") or
            state.get("edited_content") or
            state.get("edited_draft") or
            state.get("draft") or
            state.get("content") or
            ""
        )

    def _determine_formatting_rules(self, state: Dict[str, Any]) -> FormattingRules:
        """Determine formatting rules based on state and context"""
        
        # Extract context
        template_config = state.get("template_config", {})
        style_config = state.get("style_config", {})
        dynamic_params = state.get("dynamic_parameters", {})
        
        # Determine target platform
        platform = (
            dynamic_params.get("platform") or
            template_config.get("platform") or
            style_config.get("platform") or
            "blog"
        ).lower()
        
        # Get platform rules
        platform_rule = self.platform_rules.get(platform, self.platform_rules["blog"])
        
        # Determine output format
        requested_format = dynamic_params.get("format", "").lower()
        if requested_format in [f.value for f in OutputFormat]:
            output_format = OutputFormat(requested_format)
        else:
            output_format = platform_rule["format"]
        
        # Determine style preset
        style_profile_id = state.get("style_profile", "").lower()
        if "academic" in style_profile_id or "phd" in style_profile_id:
            style_preset = FormattingStyle.ACADEMIC
        elif "technical" in style_profile_id:
            style_preset = FormattingStyle.TECHNICAL
        elif "professional" in style_profile_id or "business" in style_profile_id:
            style_preset = FormattingStyle.PROFESSIONAL
        elif "creative" in style_profile_id or "story" in style_profile_id:
            style_preset = FormattingStyle.CREATIVE
        elif "social" in platform:
            style_preset = FormattingStyle.SOCIAL
        else:
            style_preset = platform_rule["style"]
        
        # Additional formatting options
        template_id = state.get("template", "").lower()
        add_toc = "guide" in template_id or "documentation" in template_id
        include_metadata = output_format in [OutputFormat.JSON, OutputFormat.STRUCTURED_DATA]
        
        return FormattingRules(
            format_type=output_format,
            style_preset=style_preset,
            preserve_structure=True,
            add_toc=add_toc,
            include_metadata=include_metadata,
            apply_styling=True,
            optimize_for_platform=platform,
            custom_css=style_config.get("custom_css", ""),
            custom_template=template_config.get("custom_template", "")
        )

    async def _apply_formatting(self, content: str, rules: FormattingRules, state: Dict[str, Any]) -> FormattingResult:
        """Apply formatting based on rules"""
        
        # Choose formatting method based on output format
        if rules.format_type == OutputFormat.HTML:
            return await self._format_to_html(content, rules, state)
        elif rules.format_type == OutputFormat.JSON:
            return await self._format_to_json(content, rules, state)
        elif rules.format_type == OutputFormat.MARKDOWN:
            return await self._format_to_markdown(content, rules, state)
        elif rules.format_type == OutputFormat.EMAIL_HTML:
            return await self._format_to_email_html(content, rules, state)
        elif rules.format_type == OutputFormat.SOCIAL_MEDIA:
            return await self._format_to_social_media(content, rules, state)
        elif rules.format_type == OutputFormat.PLAIN_TEXT:
            return await self._format_to_plain_text(content, rules, state)
        elif rules.format_type == OutputFormat.PDF_READY:
            return await self._format_for_pdf(content, rules, state)
        else:
            # Default to standard formatting
            return await self._format_to_markdown(content, rules, state)

    async def _format_to_html(self, content: str, rules: FormattingRules, state: Dict[str, Any]) -> FormattingResult:
        """Format content to HTML"""
        
        # Convert markdown to HTML if needed
        html_content = self._markdown_to_html(content)
        
        # Apply styling
        if rules.apply_styling:
            template = self.html_templates.get(rules.style_preset.value, self.html_templates["standard"])
            css = self.css_styles.get(rules.style_preset.value, self.css_styles["standard"])
            
            # Add custom CSS if provided
            if rules.custom_css:
                css += f"\n{rules.custom_css}"
            
            # Generate metadata
            metadata = self._extract_metadata(state)
            title = metadata.get("title", "Generated Content")
            
            # Apply template
            formatted_content = template.format(
                title=title,
                css=css,
                content=html_content,
                metadata_json=json.dumps(metadata, indent=2)
            )
        else:
            formatted_content = html_content
        
        # Add table of contents if requested
        if rules.add_toc:
            toc = self._generate_html_toc(formatted_content)
            formatted_content = formatted_content.replace("{{TOC}}", toc)
        else:
            formatted_content = formatted_content.replace("{{TOC}}", "")
        
        assets = {"css": self.css_styles.get(rules.style_preset.value, "")}
        
        return FormattingResult(
            formatted_content=formatted_content,
            format_type=OutputFormat.HTML,
            metadata=self._extract_metadata(state),
            assets=assets,
            export_ready=True,
            file_extensions=["html"]
        )

    async def _format_to_json(self, content: str, rules: FormattingRules, state: Dict[str, Any]) -> FormattingResult:
        """Format content to structured JSON"""
        
        # Extract metadata
        metadata = self._extract_metadata(state)
        
        # Structure content
        structured_content = {
            "meta": {
                "title": metadata.get("title", "Generated Content"),
                "description": metadata.get("description", ""),
                "author": metadata.get("author", ""),
                "created_at": datetime.now().isoformat(),
                "format": "json",
                "version": "1.0"
            },
            "content": {
                "raw": content,
                "structured": self._parse_content_structure(content),
                "word_count": len(content.split()),
                "reading_time": max(1, len(content.split()) // 200)
            },
            "seo": state.get("seo_metadata", {}),
            "formatting": {
                "style_preset": rules.style_preset.value,
                "platform": rules.optimize_for_platform,
                "preserves_structure": rules.preserve_structure
            }
        }
        
        formatted_content = json.dumps(structured_content, indent=2, ensure_ascii=False)
        
        return FormattingResult(
            formatted_content=formatted_content,
            format_type=OutputFormat.JSON,
            metadata=metadata,
            export_ready=True,
            file_extensions=["json"]
        )

    async def _format_to_markdown(self, content: str, rules: FormattingRules, state: Dict[str, Any]) -> FormattingResult:
        """Format content to enhanced Markdown"""
        
        # Clean and enhance markdown
        formatted_content = self._enhance_markdown(content, rules, state)
        
        # Add metadata header if requested
        if rules.include_metadata:
            metadata = self._extract_metadata(state)
            yaml_header = self._generate_yaml_frontmatter(metadata)
            formatted_content = f"{yaml_header}\n\n{formatted_content}"
        
        # Add table of contents if requested
        if rules.add_toc:
            toc = self._generate_markdown_toc(formatted_content)
            formatted_content = f"{toc}\n\n{formatted_content}"
        
        return FormattingResult(
            formatted_content=formatted_content,
            format_type=OutputFormat.MARKDOWN,
            metadata=self._extract_metadata(state),
            export_ready=True,
            file_extensions=["md", "markdown"]
        )

    async def _format_to_email_html(self, content: str, rules: FormattingRules, state: Dict[str, Any]) -> FormattingResult:
        """Format content for email (inline CSS, limited HTML)"""
        
        html_content = self._markdown_to_html(content)
        
        # Email-safe HTML template with inline CSS
        email_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            {content}
        </body>
        </html>
        """
        
        # Apply inline styles
        styled_content = self._apply_inline_styles(html_content)
        
        metadata = self._extract_metadata(state)
        formatted_content = email_template.format(
            title=metadata.get("title", "Newsletter"),
            content=styled_content
        )
        
        return FormattingResult(
            formatted_content=formatted_content,
            format_type=OutputFormat.EMAIL_HTML,
            metadata=metadata,
            export_ready=True,
            file_extensions=["html"]
        )

    async def _format_to_social_media(self, content: str, rules: FormattingRules, state: Dict[str, Any]) -> FormattingResult:
        """Format content for social media platforms"""
        
        platform = rules.optimize_for_platform
        platform_rules = self.platform_rules.get(platform, {})
        max_length = platform_rules.get("max_length", 500)
        
        # Extract key points and create social media post
        if platform == "twitter":
            formatted_content = self._create_twitter_thread(content, max_length)
        elif platform == "linkedin":
            formatted_content = self._create_linkedin_post(content, max_length)
        else:
            # Generic social media format
            formatted_content = self._create_social_post(content, max_length)
        
        return FormattingResult(
            formatted_content=formatted_content,
            format_type=OutputFormat.SOCIAL_MEDIA,
            metadata={"platform": platform, "character_count": len(formatted_content)},
            export_ready=True,
            file_extensions=["txt"]
        )

    async def _format_to_plain_text(self, content: str, rules: FormattingRules, state: Dict[str, Any]) -> FormattingResult:
        """Format content to clean plain text"""
        
        # Remove markdown formatting
        plain_text = self._markdown_to_plain_text(content)
        
        # Apply platform-specific formatting
        if rules.optimize_for_platform:
            platform_rules = self.platform_rules.get(rules.optimize_for_platform, {})
            max_length = platform_rules.get("max_length")
            
            if max_length and len(plain_text) > max_length:
                plain_text = self._truncate_content(plain_text, max_length)
        
        return FormattingResult(
            formatted_content=plain_text,
            format_type=OutputFormat.PLAIN_TEXT,
            metadata={"character_count": len(plain_text)},
            export_ready=True,
            file_extensions=["txt"]
        )

    async def _format_for_pdf(self, content: str, rules: FormattingRules, state: Dict[str, Any]) -> FormattingResult:
        """Format content ready for PDF generation"""
        
        # Use academic or professional HTML template for PDF
        html_content = self._markdown_to_html(content)
        
        # PDF-optimized template
        pdf_template = self.html_templates.get("academic", self.html_templates["professional"])
        pdf_css = self._get_pdf_optimized_css()
        
        metadata = self._extract_metadata(state)
        
        formatted_content = pdf_template.format(
            title=metadata.get("title", "Document"),
            css=pdf_css,
            content=html_content,
            metadata_json=""
        )
        
        return FormattingResult(
            formatted_content=formatted_content,
            format_type=OutputFormat.PDF_READY,
            metadata=metadata,
            assets={"css": pdf_css},
            export_ready=True,
            file_extensions=["html", "pdf"]
        )

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert Markdown to HTML"""
        
        html = markdown_text
        
        # Headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
        html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)
        
        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        
        # Code blocks
        html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code class="language-\1">\2</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        
        # Lists
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', html, flags=re.MULTILINE)
        
        # Wrap lists
        html = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        html = re.sub(r'</ul>\s*<ul>', '', html)
        
        # Paragraphs
        paragraphs = html.split('\n\n')
        html_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('<'):
                para = f'<p>{para}</p>'
            if para:
                html_paragraphs.append(para)
        
        return '\n'.join(html_paragraphs)

    def _markdown_to_plain_text(self, markdown_text: str) -> str:
        """Convert Markdown to plain text"""
        
        text = markdown_text
        
        # Remove markdown formatting
        text = re.sub(r'#{1,6}\s*', '', text)  # Headers
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
        text = re.sub(r'__(.+?)__', r'\1', text)  # Bold
        text = re.sub(r'_(.+?)_', r'\1', text)  # Italic
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # Links
        text = re.sub(r'`(.+?)`', r'\1', text)  # Inline code
        text = re.sub(r'```.*?\n(.*?)\n```', r'\1', text, flags=re.DOTALL)  # Code blocks
        text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)  # List markers
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)  # Numbered lists
        
        # Clean up extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        return text

    def _enhance_markdown(self, content: str, rules: FormattingRules, state: Dict[str, Any]) -> str:
        """Enhance markdown formatting"""
        
        enhanced = content
        
        # Ensure proper header hierarchy
        enhanced = self._fix_header_hierarchy(enhanced)
        
        # Add code syntax highlighting hints
        enhanced = self._enhance_code_blocks(enhanced)
        
        # Improve list formatting
        enhanced = self._improve_list_formatting(enhanced)
        
        return enhanced

    def _fix_header_hierarchy(self, content: str) -> str:
        """Fix header hierarchy in markdown"""
        
        lines = content.split('\n')
        fixed_lines = []
        current_level = 0
        
        for line in lines:
            if line.startswith('#'):
                # Count header level
                level = len(line) - len(line.lstrip('#'))
                
                # Ensure proper hierarchy
                if level > current_level + 1:
                    level = current_level + 1
                
                current_level = level
                header_text = line.lstrip('#').strip()
                fixed_lines.append('#' * level + ' ' + header_text)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def _enhance_code_blocks(self, content: str) -> str:
        """Enhance code blocks with language hints"""
        
        # Add language hints to code blocks if missing
        enhanced = re.sub(
            r'```\n((?:(?!```).*\n)*?)```',
            lambda m: self._detect_code_language(m.group(1)),
            content,
            flags=re.DOTALL
        )
        
        return enhanced

    def _detect_code_language(self, code: str) -> str:
        """Detect programming language in code block"""
        
        code_lower = code.lower()
        
        if any(keyword in code_lower for keyword in ['def ', 'import ', 'from ', 'print(']):
            return f'```python\n{code}```'
        elif any(keyword in code_lower for keyword in ['function', 'const ', 'let ', 'var ']):
            return f'```javascript\n{code}```'
        elif any(keyword in code_lower for keyword in ['public class', 'private ', 'system.out']):
            return f'```java\n{code}```'
        elif any(keyword in code_lower for keyword in ['<html', '<div', '<script']):
            return f'```html\n{code}```'
        elif any(keyword in code_lower for keyword in ['select ', 'from ', 'where ', 'insert ']):
            return f'```sql\n{code}```'
        else:
            return f'```\n{code}```'

    def _improve_list_formatting(self, content: str) -> str:
        """Improve list formatting in markdown"""
        
        lines = content.split('\n')
        improved_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('- ') or stripped.startswith('* ') or re.match(r'^\d+\. ', stripped):
                if not in_list and improved_lines and improved_lines[-1].strip():
                    improved_lines.append('')  # Add blank line before list
                in_list = True
                improved_lines.append(line)
            else:
                if in_list and stripped and not stripped.startswith(' '):
                    improved_lines.append('')  # Add blank line after list
                in_list = False
                improved_lines.append(line)
        
        return '\n'.join(improved_lines)

    def _parse_content_structure(self, content: str) -> Dict[str, Any]:
        """Parse content structure for JSON format"""
        
        structure = {
            "sections": [],
            "headers": {},
            "lists": [],
            "code_blocks": [],
            "links": []
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            stripped = line.strip()
            
            # Headers
            if stripped.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                header_text = stripped.lstrip('#').strip()
                
                if level not in structure["headers"]:
                    structure["headers"][f"h{level}"] = []
                structure["headers"][f"h{level}"].append(header_text)
                
                current_section = {
                    "title": header_text,
                    "level": level,
                    "content": []
                }
                structure["sections"].append(current_section)
            
            # Lists
            elif stripped.startswith(('- ', '* ')) or re.match(r'^\d+\. ', stripped):
                list_item = re.sub(r'^[-*]\s+|\d+\.\s+', '', stripped)
                structure["lists"].append(list_item)
            
            # Code blocks
            elif stripped.startswith('```'):
                if '```' in content[content.index(stripped):]:
                    code_block = content[content.index(stripped):content.index('```', content.index(stripped) + 3) + 3]
                    structure["code_blocks"].append(code_block)
            
            # Links
            elif '[' in stripped and '](' in stripped:
                links = re.findall(r'\[(.+?)\]\((.+?)\)', stripped)
                structure["links"].extend([{"text": text, "url": url} for text, url in links])
            
            # Regular content
            elif current_section and stripped:
                current_section["content"].append(stripped)
        
        return structure

    def _generate_yaml_frontmatter(self, metadata: Dict[str, Any]) -> str:
        """Generate YAML frontmatter for markdown"""
        
        frontmatter = ["---"]
        
        for key, value in metadata.items():
            if isinstance(value, str):
                frontmatter.append(f"{key}: \"{value}\"")
            elif isinstance(value, list):
                frontmatter.append(f"{key}:")
                for item in value:
                    frontmatter.append(f"  - \"{item}\"")
            else:
                frontmatter.append(f"{key}: {value}")
        
        frontmatter.append("---")
        
        return '\n'.join(frontmatter)

    def _generate_html_toc(self, html_content: str) -> str:
        """Generate HTML table of contents"""
        
        headers = re.findall(r'<h([1-6])>(.*?)</h[1-6]>', html_content)
        
        if not headers:
            return ""
        
        toc = ['<div class="table-of-contents">', '<h2>Table of Contents</h2>', '<ul>']
        
        for level, title in headers:
            level = int(level)
            anchor = re.sub(r'[^a-zA-Z0-9\s]', '', title).replace(' ', '-').lower()
            
            if level == 1:
                toc.append(f'<li><a href="#{anchor}">{title}</a></li>')
            elif level == 2:
                toc.append(f'  <li><a href="#{anchor}">{title}</a></li>')
            else:
                toc.append(f'    <li><a href="#{anchor}">{title}</a></li>')
        
        toc.extend(['</ul>', '</div>'])
        
        return '\n'.join(toc)

    def _generate_markdown_toc(self, markdown_content: str) -> str:
        """Generate Markdown table of contents"""
        
        headers = re.findall(r'^(#{1,6})\s+(.+)', markdown_content, re.MULTILINE)
        
        if not headers:
            return ""
        
        toc = ['## Table of Contents', '']
        
        for hashes, title in headers:
            level = len(hashes)
            anchor = re.sub(r'[^a-zA-Z0-9\s]', '', title).replace(' ', '-').lower()
            indent = '  ' * (level - 1)
            toc.append(f'{indent}- [{title}](#{anchor})')
        
        return '\n'.join(toc)

    def _apply_inline_styles(self, html_content: str) -> str:
        """Apply inline CSS styles for email compatibility"""
        
        # Define inline styles
        styles = {
            'h1': 'font-size: 24px; font-weight: bold; margin: 20px 0 10px 0; color: #333;',
            'h2': 'font-size: 20px; font-weight: bold; margin: 18px 0 8px 0; color: #444;',
            'h3': 'font-size: 18px; font-weight: bold; margin: 16px 0 6px 0; color: #555;',
            'p': 'margin: 10px 0; line-height: 1.6;',
            'ul': 'margin: 10px 0; padding-left: 20px;',
            'ol': 'margin: 10px 0; padding-left: 20px;',
            'li': 'margin: 5px 0;',
            'a': 'color: #007cba; text-decoration: none;',
            'strong': 'font-weight: bold;',
            'em': 'font-style: italic;',
            'code': 'background-color: #f4f4f4; padding: 2px 4px; font-family: monospace;'
        }
        
        # Apply inline styles
        for tag, style in styles.items():
            pattern = f'<{tag}>'
            replacement = f'<{tag} style="{style}">'
            html_content = html_content.replace(pattern, replacement)
        
        return html_content

    def _create_twitter_thread(self, content: str, max_length: int) -> str:
        """Create Twitter thread from content"""
        
        # Extract key points
        sentences = content.split('. ')
        tweets = []
        current_tweet = ""
        
        for sentence in sentences:
            sentence = sentence.strip() + '.'
            
            if len(current_tweet + sentence) < max_length - 10:  # Leave room for thread numbering
                current_tweet += sentence + ' '
            else:
                if current_tweet:
                    tweets.append(current_tweet.strip())
                current_tweet = sentence + ' '
        
        if current_tweet:
            tweets.append(current_tweet.strip())
        
        # Format as thread
        thread = []
        for i, tweet in enumerate(tweets[:10]):  # Limit to 10 tweets
            if i == 0:
                thread.append(f"🧵 {tweet}")
            else:
                thread.append(f"{i+1}/{len(tweets)} {tweet}")
        
        return '\n\n---\n\n'.join(thread)

    def _create_linkedin_post(self, content: str, max_length: int) -> str:
        """Create LinkedIn post from content"""
        
        # Extract first paragraph and key points
        paragraphs = content.split('\n\n')
        first_para = paragraphs[0] if paragraphs else content[:500]
        
        # Create engaging LinkedIn format
        post = f"💡 {first_para}\n\n"
        
        # Add key takeaways
        remaining_length = max_length - len(post) - 100
        if remaining_length > 0:
            post += "Key takeaways:\n"
            
            # Extract bullet points or create them
            bullets = re.findall(r'^[-*]\s+(.+)', content, re.MULTILINE)
            if not bullets:
                sentences = content.split('. ')
                bullets = sentences[1:4]  # Take 2-4 key sentences
            
            for bullet in bullets[:3]:
                bullet_text = f"• {bullet.strip()}\n"
                if len(post + bullet_text) < max_length - 50:
                    post += bullet_text
        
        post += "\n#insights #productivity #tech"
        
        return post[:max_length]

    def _create_social_post(self, content: str, max_length: int) -> str:
        """Create generic social media post"""
        
        # Extract first sentence or paragraph
        first_sentence = content.split('.')[0] + '.'
        
        if len(first_sentence) > max_length:
            return first_sentence[:max_length-3] + "..."
        
        return first_sentence

    def _truncate_content(self, content: str, max_length: int) -> str:
        """Intelligently truncate content"""
        
        if len(content) <= max_length:
            return content
        
        # Try to truncate at sentence boundary
        truncated = content[:max_length-3]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.7:  # If we can save at least 30% of content
            return truncated[:last_period+1]
        else:
            return truncated + "..."

    def _extract_metadata(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from state"""
        
        dynamic_params = state.get("dynamic_parameters", {})
        template_config = state.get("template_config", {})
        seo_metadata = state.get("seo_metadata", {})
        
        return {
            "title": (
                seo_metadata.get("title") or
                dynamic_params.get("title") or
                template_config.get("name") or
                state.get("topic", "Generated Content")
            ),
            "description": (
                seo_metadata.get("meta_description") or
                template_config.get("description") or
                ""
            ),
            "author": dynamic_params.get("author", "AI Writer"),
            "keywords": seo_metadata.get("keywords", []),
            "category": template_config.get("category", ""),
            "format": "formatted_content",
            "created_at": datetime.now().isoformat()
        }

    async def _generate_additional_formats(self, primary_result: FormattingResult, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate additional formats from primary result"""
        
        additional = {}
        
        # Always generate plain text version
        if primary_result.format_type != OutputFormat.PLAIN_TEXT:
            plain_text_rules = FormattingRules(
                format_type=OutputFormat.PLAIN_TEXT,
                style_preset=FormattingStyle.MINIMAL
            )
            plain_result = await self._format_to_plain_text(primary_result.formatted_content, plain_text_rules, state)
            additional["plain_text"] = plain_result.formatted_content
        
        # Generate JSON metadata version
        if primary_result.format_type != OutputFormat.JSON:
            json_rules = FormattingRules(
                format_type=OutputFormat.JSON,
                style_preset=FormattingStyle.STANDARD,
                include_metadata=True
            )
            json_result = await self._format_to_json(primary_result.formatted_content, json_rules, state)
            additional["json_metadata"] = json_result.formatted_content
        
        return additional

    def _get_minimal_html_template(self) -> str:
        """Get minimal HTML template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css}</style>
</head>
<body>
    {content}
</body>
</html>"""

    def _get_standard_html_template(self) -> str:
        """Get standard HTML template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css}</style>
</head>
<body>
    <header>
        <h1>{title}</h1>
    </header>
    <main>
        {{TOC}}
        <article>
            {content}
        </article>
    </main>
    <footer>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d')}</p>
    </footer>
</body>
</html>"""

    def _get_rich_html_template(self) -> str:
        """Get rich HTML template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css}</style>
</head>
<body>
    <div class="container">
        <header class="hero">
            <h1>{title}</h1>
            <p class="subtitle">Professional Content</p>
        </header>
        <nav class="toc">
            {{TOC}}
        </nav>
        <main>
            <article class="content">
                {content}
            </article>
        </main>
        <footer>
            <div class="footer-content">
                <p>Generated with AI • {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
        </footer>
    </div>
</body>
</html>"""

    def _get_academic_html_template(self) -> str:
        """Get academic HTML template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css}</style>
</head>
<body>
    <div class="document">
        <header class="document-header">
            <h1 class="document-title">{title}</h1>
            <div class="document-meta">
                <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
        </header>
        <div class="document-toc">
            {{TOC}}
        </div>
        <main class="document-content">
            {content}
        </main>
    </div>
</body>
</html>"""

    def _get_professional_html_template(self) -> str:
        """Get professional HTML template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css}</style>
</head>
<body>
    <div class="page">
        <header class="page-header">
            <div class="header-content">
                <h1 class="page-title">{title}</h1>
            </div>
        </header>
        <div class="page-body">
            <aside class="sidebar">
                {{TOC}}
            </aside>
            <main class="main-content">
                {content}
            </main>
        </div>
    </div>
</body>
</html>"""

    def _get_minimal_css(self) -> str:
        """Get minimal CSS styles"""
        return """
body { font-family: system-ui, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
h1, h2, h3 { color: #333; }
pre { background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
code { background: #f5f5f5; padding: 2px 4px; border-radius: 2px; }
"""

    def _get_standard_css(self) -> str:
        """Get standard CSS styles"""
        return """
body { font-family: system-ui, sans-serif; line-height: 1.6; color: #333; margin: 0; }
header { background: #f8f9fa; padding: 20px; text-align: center; }
main { max-width: 800px; margin: 0 auto; padding: 20px; }
h1 { color: #2c3e50; }
h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; }
h3 { color: #7f8c8d; }
pre { background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; border-left: 4px solid #007cba; }
code { background: #f8f9fa; padding: 2px 4px; border-radius: 2px; font-family: 'Courier New', monospace; }
blockquote { border-left: 4px solid #007cba; margin: 0; padding-left: 15px; font-style: italic; }
footer { text-align: center; padding: 20px; color: #7f8c8d; border-top: 1px solid #ecf0f1; margin-top: 40px; }
"""

    def _get_rich_css(self) -> str:
        """Get rich CSS styles"""
        return """
body { font-family: 'Segoe UI', system-ui, sans-serif; line-height: 1.6; color: #333; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.container { min-height: 100vh; }
.hero { background: white; padding: 40px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.hero h1 { font-size: 2.5em; margin: 0; color: #2c3e50; }
.subtitle { color: #7f8c8d; font-size: 1.2em; margin-top: 10px; }
.content { background: white; padding: 40px; margin: 20px; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
h2 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
pre { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; overflow-x: auto; }
.footer-content { background: white; padding: 20px; text-align: center; margin: 20px; border-radius: 8px; }
"""

    def _get_academic_css(self) -> str:
        """Get academic CSS styles"""
        return """
body { font-family: 'Times New Roman', serif; line-height: 1.8; color: #000; max-width: 8.5in; margin: 0 auto; padding: 1in; }
.document-header { text-align: center; margin-bottom: 2em; }
.document-title { font-size: 24pt; font-weight: bold; margin-bottom: 0.5em; }
.document-meta { font-size: 12pt; color: #666; }
h1 { font-size: 18pt; font-weight: bold; margin-top: 1.5em; margin-bottom: 0.5em; }
h2 { font-size: 16pt; font-weight: bold; margin-top: 1.2em; margin-bottom: 0.4em; }
h3 { font-size: 14pt; font-weight: bold; margin-top: 1em; margin-bottom: 0.3em; }
p { margin-bottom: 1em; text-align: justify; }
.document-toc { border: 1px solid #ccc; padding: 1em; margin-bottom: 2em; }
pre { font-family: 'Courier New', monospace; font-size: 10pt; background: #f9f9f9; padding: 1em; border: 1px solid #ddd; }
"""

    def _get_professional_css(self) -> str:
        """Get professional CSS styles"""
        return """
body { font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; }
.page { display: flex; flex-direction: column; min-height: 100vh; }
.page-header { background: #2c3e50; color: white; padding: 20px; }
.page-title { margin: 0; font-size: 1.8em; }
.page-body { display: flex; flex: 1; }
.sidebar { width: 250px; background: #ecf0f1; padding: 20px; }
.main-content { flex: 1; padding: 20px; }
h1 { color: #2c3e50; font-size: 1.8em; }
h2 { color: #34495e; font-size: 1.4em; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
pre { background: #2c3e50; color: white; padding: 15px; border-radius: 4px; }
.table-of-contents ul { list-style: none; padding: 0; }
.table-of-contents a { color: #2c3e50; text-decoration: none; }
.table-of-contents a:hover { color: #3498db; }
"""

    def _get_pdf_optimized_css(self) -> str:
        """Get PDF-optimized CSS styles"""
        return """
@media print {
    body { font-size: 12pt; line-height: 1.4; }
    h1 { page-break-before: always; }
    h1, h2, h3 { page-break-after: avoid; }
    p, li { orphans: 3; widows: 3; }
    pre { page-break-inside: avoid; }
}
body { font-family: 'Times New Roman', serif; line-height: 1.6; max-width: none; margin: 0; padding: 20mm; }
h1 { font-size: 18pt; color: #000; margin-top: 0; }
h2 { font-size: 16pt; color: #000; }
h3 { font-size: 14pt; color: #000; }
pre { background: #f5f5f5; padding: 10pt; border: 1px solid #ccc; font-size: 10pt; }
"""

    def _create_error_response(self, state: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """Create error response for formatting"""
        
        return {
            **state,
            "formatted_content": state.get("content", ""),
            "formatting_metadata": {
                "error": error_message,
                "formatting_applied": False,
                "format_type": "none"
            }
        }

    # Synchronous method for backward compatibility
    def intelligent_format_sync(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for intelligent formatting"""
        try:
            import asyncio
            # Run async method
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.intelligent_format(state))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Sync formatting failed: {e}")
            return self._create_error_response(state, str(e))

# LangGraph integration functions
async def _enhanced_formatter_agent_async_fn(state: dict) -> dict:
    """Enhanced formatter agent function for LangGraph workflow - async version"""
    formatter_agent = IntelligentFormatterAgent()
    return await formatter_agent.intelligent_format(state)

def _enhanced_formatter_agent_sync_fn(state: dict) -> dict:
    """Enhanced formatter agent function for LangGraph workflow - sync version"""
    formatter_agent = IntelligentFormatterAgent()
    return formatter_agent.intelligent_format_sync(state)

# Export functions for orchestration
enhanced_formatter_agent = RunnableLambda(_enhanced_formatter_agent_async_fn)
enhanced_formatter_agent_sync = RunnableLambda(_enhanced_formatter_agent_sync_fn)

# Create instance for direct use
intelligent_formatter_agent = IntelligentFormatterAgent()

# Backward compatibility
IntelligentFormatterAgent = IntelligentFormatterAgent