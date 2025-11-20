# langgraph_app/agents/enhanced_image_agent_integrated.py
"""
Enterprise Image Agent with LLM-driven prompt generation and DALL-E 3 integration.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from enum import Enum

from openai import OpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

from langgraph_app.core.state import EnrichedContentState, AgentType, ContentPhase
from langgraph_app.core.types import GeneratedImage
from langgraph_app.enhanced_model_registry import get_model_for_generation

logger = logging.getLogger(__name__)


class ImageStyle(Enum):
    TECHNICAL = "technical diagram"
    PROFESSIONAL = "professional business"
    CREATIVE = "creative artistic"
    MINIMAL = "minimalist design"
    PHOTOREALISTIC = "photorealistic"


@tool
def analyze_image_requirements(content: str, template_type: str) -> Dict[str, Any]:
    """Analyze content to determine image requirements.
    
    Args:
        content: Content to analyze
        template_type: Type of template
        
    Returns:
        Image requirements
    """
    requirements = {
        "needs_images": False,
        "suggested_count": 0,
        "image_types": [],
        "placement_sections": []
    }
    
    # Detect image indicators
    image_indicators = ['diagram', 'illustration', 'visual', 'figure', 'chart', 'infographic']
    content_lower = content.lower()
    
    for indicator in image_indicators:
        if indicator in content_lower:
            requirements["needs_images"] = True
            requirements["image_types"].append(indicator)
    
    # Template-based requirements
    image_heavy_templates = ['business_proposal', 'pitch', 'marketing', 'presentation']
    if any(t in template_type.lower() for t in image_heavy_templates):
        requirements["needs_images"] = True
        requirements["suggested_count"] = 2
    
    # Find sections for placement
    sections = [line for line in content.split('\n') if line.startswith('#')]
    if len(sections) > 2:
        requirements["placement_sections"] = sections[:3]
    
    return requirements


@tool
def generate_image_prompt(
    topic: str,
    style: str,
    context: str,
    platform: str = "web"
) -> str:
    """Generate optimized DALL-E 3 prompt.
    
    Args:
        topic: Main topic
        style: Visual style
        context: Additional context
        platform: Target platform
        
    Returns:
        Optimized image generation prompt
    """
    # Platform-specific optimizations
    platform_specs = {
        "linkedin": "professional, business-appropriate",
        "medium": "editorial, clean design",
        "web": "high-quality, versatile",
        "pitch": "impactful, professional"
    }
    
    platform_style = platform_specs.get(platform.lower(), "professional")
    
    prompt = f"{style} {platform_style} image depicting {topic}. {context}. High quality, clear composition, modern aesthetic."
    
    # Ensure prompt is under 4000 chars (DALL-E limit)
    return prompt[:4000]


class EnhancedImageAgent:
    """
    Enterprise Image Agent with:
    - LLM-driven prompt optimization
    - DALL-E 3 integration
    - Tool use (requirement analysis, prompt generation)
    - Smart image placement
    """
    
    def __init__(self):
        self.agent_type = AgentType.IMAGE
        self.tools = [analyze_image_requirements, generate_image_prompt]
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute image generation with LLM."""
        
        logger.info("🖼️ IMAGE: Starting generation")
        
        template_config = state.template_config or {}
        
        # Check if images needed
        if not self._requires_images(template_config, state):
            logger.info("⏭️ IMAGE: Not required")
            state.log_agent_execution(self.agent_type, {"status": "skipped"})
            return state
        
        # Get content
        content = self._get_content(state)
        
        if not content:
            logger.warning("No content for image generation")
            return state
        
        # Analyze requirements
        requirements = analyze_image_requirements.invoke({
            "content": content,
            "template_type": template_config.get('template_type', '')
        })
        
        if not requirements.get("needs_images"):
            logger.info("No images needed based on analysis")
            return state
        
        # Generate images
        generated_images = self._generate_images(
            state,
            template_config,
            requirements
        )
        
        state.generated_images = generated_images
        
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "images_generated": len(generated_images)
        })
        
        logger.info(f"✅ IMAGE: Generated {len(generated_images)} images")
        
        return state
    
    def _requires_images(self, template_config: Dict, state: EnrichedContentState) -> bool:
        """Check if images required."""
        
        # Check template config
        image_config = template_config.get('image_generation_config', {})
        if image_config.get('enabled'):
            return True
        
        # Check template type
        template_type = template_config.get('template_type', '').lower()
        image_templates = ['proposal', 'pitch', 'marketing', 'presentation']
        
        return any(t in template_type for t in image_templates)
    
    def _get_content(self, state: EnrichedContentState) -> str:
        """Extract content from state."""
        
        if state.edited_content and hasattr(state.edited_content, 'body'):
            return state.edited_content.body
        elif state.draft_content:
            return state.draft_content.body if hasattr(state.draft_content, 'body') else state.draft_content
        else:
            return state.content or ""
    
    def _generate_images(
        self,
        state: EnrichedContentState,
        template_config: Dict,
        requirements: Dict
    ) -> List[GeneratedImage]:
        """Generate images using LLM + DALL-E."""
        
        generated = []
        
        # Get context
        topic = state.content_spec.topic if state.content_spec else "content"
        platform = state.content_spec.platform if state.content_spec else "web"
        
        # Determine style
        style = self._determine_style(template_config)
        
        # Generate up to suggested count
        count = min(requirements.get("suggested_count", 1), 3)  # Max 3 images
        
        for i in range(count):
            try:
                # Generate optimized prompt
                context = f"Image {i+1} for {template_config.get('template_type', 'content')}"
                
                prompt = generate_image_prompt.invoke({
                    "topic": topic,
                    "style": style,
                    "context": context,
                    "platform": platform
                })
                
                # Call DALL-E 3
                logger.info(f"🎨 Generating image with prompt: {prompt[:100]}...")
                
                response = self.openai_client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1
                )
                
                image_url = response.data[0].url
                
                generated.append(GeneratedImage(
                    prompt=prompt,
                    url=image_url,
                    alt_text=f"{topic} - {style} illustration",
                    width=1024,
                    height=1024
                ))
                
                logger.info(f"✅ Generated image {i+1}/{count}")
                
            except Exception as e:
                logger.error(f"Failed to generate image {i+1}: {e}")
        
        return generated
    
    def _determine_style(self, template_config: Dict) -> str:
        """Determine image style from template."""
        
        template_type = template_config.get('template_type', '').lower()
        
        if 'technical' in template_type or 'documentation' in template_type:
            return ImageStyle.TECHNICAL.value
        elif 'business' in template_type or 'proposal' in template_type:
            return ImageStyle.PROFESSIONAL.value
        elif 'marketing' in template_type or 'creative' in template_type:
            return ImageStyle.CREATIVE.value
        elif 'pitch' in template_type or 'presentation' in template_type:
            return ImageStyle.PHOTOREALISTIC.value
        else:
            return ImageStyle.MINIMAL.value