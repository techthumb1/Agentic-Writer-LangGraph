# File: langgraph_app/agents/formatter.py
import re
from typing import Dict, List
from langchain_core.runnables import RunnableLambda

class IntelligentFormatterAgent:
    """
    Advanced formatter that creates platform-optimized output formats
    """
    
    def __init__(self):
        self.platform_formatters = {
            "medium": self._format_for_medium,
            "linkedin": self._format_for_linkedin,
            "twitter": self._format_for_twitter,
            "substack": self._format_for_substack,
            "blog": self._format_for_blog,
            "html": self._format_for_html
        }
    
    def intelligent_format(self, state: Dict) -> Dict:
        """Main formatting function with platform awareness"""
        
        content_plan = state.get("content_plan", {})
        platform = content_plan.get("platform", "blog")
        
        # Get the final content (edited draft or original draft)
        content = state.get("edited_draft", state.get("draft", "No content available"))
        
        # Get additional elements
        code_block = state.get("code_block", "")
        image_url = state.get("cover_image_url", "")
        research = state.get("research", "")
        
        # Apply platform-specific formatting
        formatter = self.platform_formatters.get(platform, self._format_for_blog)
        formatted_content = formatter(content, code_block, image_url, state)
        
        # Add metadata
        formatting_metadata = {
            "platform": platform,
            "includes_code": bool(code_block),
            "includes_image": bool(image_url),
            "includes_research": bool(research),
            "word_count": len(content.split()),
            "estimated_read_time": self._estimate_read_time(content)
        }
        
        return {
            "formatted_article": formatted_content,
            "formatting_metadata": formatting_metadata
        }
    
    def _format_for_medium(self, content: str, code: str, image: str, state: Dict) -> str:
        """Format for Medium publication"""
        
        # Medium-style formatting with proper headers and spacing
        formatted = content
        
        # Add cover image if available
        if image:
            formatted = f"![Cover Image]({image})\n\n{formatted}"
        
        # Add code block if available
        if code:
            formatted += f"\n\n## Code Example\n\n{code}"
        
        # Add publication footer
        content_plan = state.get("content_plan", {})
        tags = state.get("tags", [])
        
        if tags:
            formatted += f"\n\n---\n\n*Tags: {', '.join(tags)}*"
        
        return formatted
    
    def _format_for_linkedin(self, content: str, code: str, image: str, state: Dict) -> str:
        """Format for LinkedIn post"""
        
        # LinkedIn prefers shorter paragraphs and professional tone
        paragraphs = content.split('\n\n')
        
        # Shorten paragraphs for LinkedIn
        linkedin_paragraphs = []
        for para in paragraphs:
            if len(para.split()) > 50:  # Break long paragraphs
                sentences = para.split('. ')
                mid_point = len(sentences) // 2
                linkedin_paragraphs.append('. '.join(sentences[:mid_point]) + '.')
                linkedin_paragraphs.append('. '.join(sentences[mid_point:]))
            else:
                linkedin_paragraphs.append(para)
        
        formatted = '\n\n'.join(linkedin_paragraphs)
        
        # Add professional engagement hooks
        formatted += "\n\n💭 What's your experience with this? Share your thoughts in the comments!"
        
        # Add hashtags
        tags = state.get("tags", [])
        if tags:
            hashtags = [f"#{tag.replace(' ', '').replace('-', '')}" for tag in tags[:5]]
            formatted += f"\n\n{' '.join(hashtags)}"
        
        return formatted
    
    def _format_for_twitter(self, content: str, code: str, image: str, state: Dict) -> str:
        """Format for Twitter thread"""
        
        # Break content into tweet-sized chunks
        sentences = re.split(r'(?<=[.!?])\s+', content)
        tweets = []
        current_tweet = "🧵 Thread: "
        
        for sentence in sentences:
            if len(current_tweet + sentence) > 250:  # Leave room for thread numbering
                tweets.append(current_tweet.strip())
                current_tweet = sentence + " "
            else:
                current_tweet += sentence + " "
        
        if current_tweet.strip():
            tweets.append(current_tweet.strip())
        
        # Number the tweets
        numbered_tweets = []
        for i, tweet in enumerate(tweets):
            if i == 0:
                numbered_tweets.append(tweet)
            else:
                numbered_tweets.append(f"{i+1}/{len(tweets)} {tweet}")
        
        return '\n\n---TWEET BREAK---\n\n'.join(numbered_tweets)
    
    def _format_for_substack(self, content: str, code: str, image: str, state: Dict) -> str:
        """Format for Substack newsletter"""
        
        formatted = content
        
        # Add newsletter-style introduction
        content_plan = state.get("content_plan", {})
        topic = content_plan.get("topic", "Today's Topic")
        
        intro = f"**Welcome back to our newsletter!** Today we're exploring: *{topic}*\n\n"
        formatted = intro + formatted
        
        # Add cover image
        if image:
            formatted = f"![Newsletter Header]({image})\n\n{formatted}"
        
        # Add code section
        if code:
            formatted += f"\n\n## 💻 Code Corner\n\n{code}"
        
        # Add newsletter footer
        formatted += "\n\n---\n\n**Thanks for reading!** If you found this valuable, please share it with colleagues who might benefit.\n\n*Reply to this email with your thoughts – I read every response!*"
        
        return formatted
    
    def _format_for_blog(self, content: str, code: str, image: str, state: Dict) -> str:
        """Format for general blog post"""
        
        formatted = content
        
        # Add cover image
        if image:
            formatted = f"![Article Cover]({image})\n\n{formatted}"
        
        # Add code section
        if code:
            formatted += f"\n\n## Code Example\n\n{code}"
        
        # Add metadata footer
        content_plan = state.get("content_plan", {})
        tags = state.get("tags", [])
        
        if tags:
            formatted += f"\n\n**Tags:** {', '.join(tags)}"
        
        return formatted
    
    def _format_for_html(self, content: str, code: str, image: str, state: Dict) -> str:
        """Format as HTML document"""
        
        content_plan = state.get("content_plan", {})
        topic = content_plan.get("topic", "Article")
        
        # Convert markdown-style content to HTML
        html_content = self._markdown_to_html(content)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic}</title>
    <style>
        body {{ 
            font-family: 'Georgia', serif; 
            line-height: 1.6; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
        }}
        h1, h2, h3 {{ color: #333; }}
        code {{ 
            background-color: #f4f4f4; 
            padding: 2px 4px; 
            border-radius: 3px; 
        }}
        pre {{ 
            background-color: #f4f4f4; 
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto; 
        }}
        img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    {f'<img src="{image}" alt="Cover Image" style="width: 100%; margin-bottom: 20px;">' if image else ''}
    {html_content}
    {f'<h2>Code Example</h2><pre><code>{code}</code></pre>' if code else ''}
</body>
</html>"""
        
        return html
    
    def _markdown_to_html(self, content: str) -> str:
        """Simple markdown to HTML conversion"""
        
        # Headers - Fixed regex patterns
        content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        
        # Bold and italic
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
        
        # Paragraphs
        paragraphs = content.split('\n\n')
        html_paragraphs = [f'<p>{para.strip()}</p>' for para in paragraphs if para.strip()]
        
        return '\n'.join(html_paragraphs)
    
    def _estimate_read_time(self, content: str) -> int:
        """Estimate reading time in minutes"""
        words = len(content.split())
        return max(1, round(words / 200))  # Average reading speed: 200 words/minute


# Legacy compatibility function
def _formatter_fn(state: dict) -> dict:
    """Legacy wrapper for backward compatibility"""
    formatter = IntelligentFormatterAgent()
    return formatter.intelligent_format(state)

# Original simple formatter function for compatibility
def _legacy_formatter_fn(state: dict) -> dict:
    draft = state.get("draft", "No Draft Found")
    wrapped = f"<html><body>{draft}</body></html>"
    return {"formatted_article": wrapped}

# Function to load style profile (moved from original file)
def load_style_profile(name: str) -> dict:
    try:
        import yaml
        with open(f"data/style_profiles/{name}.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Style profile not found: {name}.yaml")

# Function to load content template (moved from original file)
def load_content_template(name: str) -> dict:
    try:
        import yaml
        with open(f"data/content_templates/{name}.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Template not found: {name}.yaml")

# Exports for compatibility
formatter: RunnableLambda = RunnableLambda(_formatter_fn)

# Class export for advanced usage
FormatterAgent = IntelligentFormatterAgent

# enhanced_formatter.py - Add to the very end:
from langchain_core.runnables import RunnableLambda

async def _enhanced_formatter_fn(state: dict) -> dict:
    """Enhanced formatter agent function for LangGraph workflow"""
    formatter_agent = IntelligentFormatterAgent()  # Adjust class name as needed
    return await formatter_agent.intelligent_format(state)  # Adjust method name as needed

# Export the function
formatter = RunnableLambda(_enhanced_formatter_fn)
