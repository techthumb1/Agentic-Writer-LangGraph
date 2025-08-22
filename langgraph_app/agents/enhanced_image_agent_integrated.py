# File: langgraph_app/agents/enhanced_image_agent.py
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

from langgraph_app.core.enriched_content_state import EnrichedContentState

# Import ContentPhase for phase management
from langgraph_app.core.enriched_content_state import ContentPhase

load_dotenv()

# Enhanced logging
logger = logging.getLogger(__name__)

class ImageStyle(Enum):
    TECHNICAL = "technical"
    INSPIRATIONAL = "inspirational"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    EDUCATIONAL = "educational"
    FUTURISTIC = "futuristic"
    MINIMALIST = "minimalist"
    ABSTRACT = "abstract"

class ContentIntent(Enum):
    INFORM = "inform"
    PERSUADE = "persuade"
    ENTERTAIN = "entertain"
    TEACH = "teach"
    INSPIRE = "inspire"
    ANALYZE = "analyze"

@dataclass
class ImageGenerationContext:
    """Enhanced context for Enhanced image generation"""
    topic: str
    platform: str
    intent: ContentIntent
    complexity_level: int
    innovation_level: str
    tags: List[str]
    audience: str
    content_length: str
    style_profile: Dict[str, Any]
    template_config: Dict[str, Any]

@dataclass
class ImageSpecification:
    """Detailed image specifications"""
    size: str
    style: ImageStyle
    quality: str
    aspect_ratio: str
    color_scheme: str
    composition_type: str

class EnhancedImageAgent:
    """
    Advanced image generation agent with enhanced contextual intelligence
    and proper workflow integration
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Define AgentType locally if not imported
        class AgentType(Enum):
            IMAGE = "image"
        self.agent_type = AgentType.IMAGE 
        
        # Enhanced style definitions with detailed characteristics
        self.image_styles = {
            ImageStyle.TECHNICAL: {
                "description": "Clean, minimal technical diagram or illustration",
                "colors": "Blue, gray, white, professional palette",
                "elements": "Diagrams, flowcharts, technical schematics, clean lines",
                "composition": "Structured, grid-based, informational"
            },
            ImageStyle.INSPIRATIONAL: {
                "description": "Uplifting, motivational visual with dynamic elements",
                "colors": "Warm oranges, golden yellows, inspiring blues",
                "elements": "Light rays, growth metaphors, achievement symbols",
                "composition": "Dynamic, upward movement, emotional resonance"
            },
            ImageStyle.PROFESSIONAL: {
                "description": "Corporate, clean, business-appropriate design",
                "colors": "Navy, gray, white, corporate color schemes",
                "elements": "Business graphics, clean typography, minimal design",
                "composition": "Balanced, symmetrical, trustworthy"
            },
            ImageStyle.CREATIVE: {
                "description": "Artistic, creative, visually striking composition",
                "colors": "Bold, vibrant, artistic color combinations",
                "elements": "Creative shapes, artistic interpretation, visual metaphors",
                "composition": "Asymmetrical, bold, memorable"
            },
            ImageStyle.EDUCATIONAL: {
                "description": "Clear, informative illustration that aids understanding",
                "colors": "Friendly blues, greens, educational palette",
                "elements": "Visual metaphors, explanatory diagrams, learning aids",
                "composition": "Clear hierarchy, easy to understand"
            },
            ImageStyle.FUTURISTIC: {
                "description": "Modern, tech-forward, innovative visual style",
                "colors": "Teal, purple, electric blue, neon accents",
                "elements": "Geometric shapes, tech patterns, innovation symbols",
                "composition": "Cutting-edge, forward-looking, dynamic"
            },
            ImageStyle.MINIMALIST: {
                "description": "Clean, simple, focused design with minimal elements",
                "colors": "Monochromatic, subtle, refined palette",
                "elements": "Simple shapes, negative space, essential elements only",
                "composition": "Spacious, balanced, focused"
            },
            ImageStyle.ABSTRACT: {
                "description": "Conceptual, abstract representation of ideas",
                "colors": "Varied, concept-driven color selection",
                "elements": "Abstract shapes, conceptual metaphors, symbolic representation",
                "composition": "Conceptual, thought-provoking, interpretive"
            }
        }
        
        # Enhanced platform specifications with DALL-E 3 compatible sizes
        self.platform_specs = {
            "linkedin": {
                "size": "1792x1024",  # DALL-E 3 compatible landscape
                "style": ImageStyle.PROFESSIONAL,
                "aspect_ratio": "1.75:1",
                "optimization": "Business networking, professional visibility"
            },
            "twitter": {
                "size": "1792x1024",  # DALL-E 3 compatible landscape  
                "style": ImageStyle.CREATIVE,
                "aspect_ratio": "1.75:1",
                "optimization": "Quick engagement, visual impact"
            },
            "medium": {
                "size": "1792x1024",  # DALL-E 3 compatible landscape
                "style": ImageStyle.EDUCATIONAL,
                "aspect_ratio": "1.75:1",
                "optimization": "Reading experience, article support"
            },
            "instagram": {
                "size": "1024x1024",  # DALL-E 3 compatible square
                "style": ImageStyle.CREATIVE,
                "aspect_ratio": "1:1",
                "optimization": "Visual storytelling, engagement"
            },
            "blog": {
                "size": "1792x1024",  # DALL-E 3 compatible landscape
                "style": ImageStyle.EDUCATIONAL,
                "aspect_ratio": "1.75:1",
                "optimization": "Content support, readability"
            },
            "substack": {
                "size": "1792x1024",  # DALL-E 3 compatible landscape
                "style": ImageStyle.PROFESSIONAL,
                "aspect_ratio": "1.75:1",
                "optimization": "Newsletter header, professional communication"
            },
            "youtube": {
                "size": "1792x1024",  # DALL-E 3 compatible landscape
                "style": ImageStyle.CREATIVE,
                "aspect_ratio": "1.75:1",
                "optimization": "Thumbnail impact, click-through rate"
            },
            "facebook": {
                "size": "1792x1024",  # DALL-E 3 compatible landscape
                "style": ImageStyle.INSPIRATIONAL,
                "aspect_ratio": "1.75:1",
                "optimization": "Social sharing, engagement"
            }
        }
        
        # Visual keyword mappings for enhanced context understanding
        self.visual_keyword_mappings = {
            "ai": ["neural networks", "artificial brain", "data nodes", "algorithmic patterns"],
            "machine_learning": ["learning curves", "data training", "model optimization", "pattern recognition"],
            "blockchain": ["chain links", "cryptographic blocks", "decentralized networks", "digital security"],
            "startup": ["growth rockets", "innovation lightbulbs", "entrepreneurial journey", "scaling ladders"],
            "data_science": ["data visualizations", "statistical charts", "analytical dashboards", "insight discovery"],
            "cloud": ["cloud infrastructure", "distributed computing", "scalable architecture", "digital connectivity"],
            "cybersecurity": ["digital shields", "security locks", "protection barriers", "safe networks"],
            "iot": ["connected devices", "smart sensors", "networked objects", "digital ecosystem"],
            "automation": ["robotic processes", "automated workflows", "efficiency gears", "systematic optimization"]
        }
    
    def extract_generation_context(self, state: Dict) -> ImageGenerationContext:
        """Extract and structure comprehensive context from workflow state"""
        
        # FIXED: Handle different state structures properly
        if hasattr(state, 'template_config'):
            # EnrichedContentState structure
            template_config = getattr(state, 'template_config', {})
            style_config = getattr(state, 'style_config', {})
            topic = getattr(state.content_spec, 'topic', 'Content Generation')
            platform = getattr(state.content_spec, 'platform', 'blog')
            tags = template_config.get('tags', []) if template_config else []
        else:
            # Dictionary structure fallback
            template_config = state.get('template_config', {}) if isinstance(state, dict) else {}
            style_config = state.get('style_config', {}) if isinstance(state, dict) else {}
            dynamic_params = state.get('dynamic_parameters', {}) if isinstance(state, dict) else {}
            
            topic = (template_config.get('topic') or 
                    dynamic_params.get('topic') or 
                    'Content Generation')
            
            platform = (template_config.get('platform') or 
                       dynamic_params.get('platform') or 
                       'blog')
            
            tags = (template_config.get('tags') or 
                   dynamic_params.get('tags') or 
                   [])        
        # Extract template_config
        template_config = getattr(state, "template_config", {})
        if not template_config and hasattr(state, "content_spec"):
            template_config = state.content_spec.business_context.get("template_config", {})
        # Handle different state structures (dict vs Pydantic)
        if hasattr(state, 'template_config'):
            # Pydantic AgentState structure
            template_config = state.template_config or {}
            style_config = getattr(state, 'style_config', {})
            topic = template_config.get('topic', 'Content Generation')
            platform = template_config.get('platform', 'blog')
            tags = template_config.get('tags', [])
        else:
            # Dictionary structure
            template_config = getattr(state, 'template_config', {})
            style_config = state.get('style_config', {})
            dynamic_params = state.get('dynamic_parameters', {})
            
            topic = (template_config.get('topic') or 
                    dynamic_params.get('topic') or 
                    state.get('topic', 'Content Generation'))
            
            platform = (template_config.get('platform') or 
                       dynamic_params.get('platform') or 
                       state.get('platform', 'blog'))
            
            tags = (template_config.get('tags') or 
                   dynamic_params.get('tags') or 
                   state.get('tags', []))
        
        # Determine content intent
        intent_str = (template_config.get('intent') or 
                     style_config.get('intent') or 
                     'inform')
        
        try:
            intent = ContentIntent(intent_str)
        except ValueError:
            intent = ContentIntent.INFORM
        
        # Extract additional context
        complexity_level = template_config.get('complexity_level', 5)
        innovation_level = template_config.get('innovation_level', 'balanced')
        audience = style_config.get('audience', 'general')
        content_length = template_config.get('length', 'medium')
        
        return ImageGenerationContext(
            topic=topic,
            platform=platform,
            intent=intent,
            complexity_level=complexity_level,
            innovation_level=innovation_level,
            tags=tags if isinstance(tags, list) else [],
            audience=audience,
            content_length=content_length,
            style_profile=style_config,
            template_config=template_config
        )
    
    def determine_optimal_image_style(self, context: ImageGenerationContext) -> ImageStyle:
        """Enhanced style determination based on comprehensive context analysis"""
        
        # INJECT: Check template_config for explicit image style
        template_config = context.template_config
        if template_config and template_config.get('image_style'):
            template_style = template_config['image_style']
            try:
                return ImageStyle(template_style)
            except ValueError:
                pass  # Continue with logic below
        
        # Platform-based baseline
        platform_style = self.platform_specs.get(context.platform, {}).get('style', ImageStyle.PROFESSIONAL)
        
        # Content complexity adjustments
        if context.complexity_level >= 8:
            return ImageStyle.TECHNICAL
        elif context.complexity_level <= 3:
            return ImageStyle.MINIMALIST
        
        # Intent-based prioritization
        intent_style_map = {
            ContentIntent.TEACH: ImageStyle.EDUCATIONAL,
            ContentIntent.INSPIRE: ImageStyle.INSPIRATIONAL,
            ContentIntent.ANALYZE: ImageStyle.TECHNICAL,
            ContentIntent.ENTERTAIN: ImageStyle.CREATIVE,
            ContentIntent.PERSUADE: ImageStyle.PROFESSIONAL
        }
        
        if context.intent in intent_style_map:
            return intent_style_map[context.intent]
        
        # Innovation level adjustments
        if context.innovation_level in ["innovative", "experimental"]:
            return ImageStyle.FUTURISTIC
        elif context.innovation_level == "conservative":
            return ImageStyle.PROFESSIONAL
        
        # Topic-based adjustments
        topic_lower = context.topic.lower()
        if any(tech_word in topic_lower for tech_word in ["ai", "ml", "algorithm", "tech"]):
            return ImageStyle.FUTURISTIC
        elif any(biz_word in topic_lower for biz_word in ["business", "strategy", "corporate"]):
            return ImageStyle.PROFESSIONAL
        elif any(edu_word in topic_lower for edu_word in ["tutorial", "guide", "learn"]):
            return ImageStyle.EDUCATIONAL
        
        return platform_style
    
    def extract_enhanced_visual_keywords(self, context: ImageGenerationContext) -> List[str]:
        """Advanced keyword extraction with semantic understanding"""
        
        visual_keywords = []
        topic_lower = context.topic.lower()
        
        # Map topic keywords to visual elements
        for keyword, visuals in self.visual_keyword_mappings.items():
            if keyword.replace('_', ' ') in topic_lower or keyword in topic_lower:
                visual_keywords.extend(visuals[:2])  # Take top 2 per category
        
        # Add context-specific keywords
        if context.intent == ContentIntent.INSPIRE:
            visual_keywords.extend(["upward arrows", "bright lights", "success symbols"])
        elif context.intent == ContentIntent.TEACH:
            visual_keywords.extend(["learning paths", "knowledge trees", "educational icons"])
        
        # Platform-specific visual elements
        platform_keywords = {
            "linkedin": ["professional networking", "business growth"],
            "instagram": ["visual storytelling", "aesthetic appeal"],
            "youtube": ["engaging thumbnails", "video content"],
            "medium": ["editorial design", "reading experience"]
        }
        
        if context.platform in platform_keywords:
            visual_keywords.extend(platform_keywords[context.platform])
        
        # Add relevant tags
        visual_keywords.extend([tag for tag in context.tags if len(tag) > 2])
        
        # Remove duplicates and limit
        unique_keywords = list(dict.fromkeys(visual_keywords))
        return unique_keywords[:7]  # Optimal number for prompt clarity
    
    def create_advanced_image_prompt(self, context: ImageGenerationContext, style: ImageStyle) -> str:
        """Generate sophisticated, context-aware image prompts"""
        
        style_info = self.image_styles[style]
        visual_keywords = self.extract_enhanced_visual_keywords(context)
        platform_spec = self.platform_specs.get(context.platform, {})
        
        # Base prompt construction
        base_description = f"{style_info['description']} representing '{context.topic}'"
        
        # Add visual elements
        if visual_keywords:
            element_desc = f", incorporating elements like {', '.join(visual_keywords)}"
            base_description += element_desc
        
        # Style-specific enhancements
        color_instruction = f"Color palette: {style_info['colors']}"
        composition_instruction = f"Composition: {style_info['composition']}"
        element_instruction = f"Visual elements: {style_info['elements']}"
        
        # Platform optimization
        platform_optimization = platform_spec.get('optimization', 'general appeal')
        aspect_ratio = platform_spec.get('aspect_ratio', '16:9')
        
        # Audience and complexity adjustments
        complexity_instruction = ""
        if context.complexity_level >= 7:
            complexity_instruction = "Include detailed technical elements and sophisticated visual hierarchy."
        elif context.complexity_level <= 3:
            complexity_instruction = "Keep design simple and immediately understandable."
        
        # Innovation level adjustments
        innovation_instruction = ""
        if context.innovation_level == "experimental":
            innovation_instruction = "Push creative boundaries with unique visual approaches."
        elif context.innovation_level == "innovative":
            innovation_instruction = "Include modern, cutting-edge design elements."
        
        # Construct final prompt
        final_prompt = f"""
        {base_description}. 
        
        {color_instruction}. 
        {composition_instruction}. 
        {element_instruction}. 
        
        Optimized for {context.platform} ({aspect_ratio} aspect ratio) with focus on {platform_optimization}. 
        Target audience: {context.audience}. 
        
        {complexity_instruction} 
        {innovation_instruction}
        
        High quality, detailed, visually appealing, professional execution.
        """.strip()
        
        return final_prompt
    
    def create_image_specification(self, context: ImageGenerationContext, style: ImageStyle) -> ImageSpecification:
        """Create detailed image specifications"""
        
        platform_spec = self.platform_specs.get(context.platform, self.platform_specs["blog"])
        style_info = self.image_styles[style]
        
        return ImageSpecification(
            size=platform_spec["size"],
            style=style,
            quality="hd",
            aspect_ratio=platform_spec["aspect_ratio"],
            color_scheme=style_info["colors"],
            composition_type=style_info["composition"]
        )
    
    async def generate_images(self, state: Dict) -> Dict:
        """
        Main image generation method - properly aligned with workflow expectations
        Enhanced with comprehensive context analysis and enhanced generation
        """
        
        logger.info(f"Starting enhanced image generation for topic: {state.get('topic', 'Unknown')}")
        
        try:
            # Extract comprehensive context
            context = self.extract_generation_context(state)
            
            # Determine if images are needed
            template_config = context.template_config
            style_config = context.style_profile
            
            # Check explicit image requirements
            images_needed = (
                template_config.get('images_needed', True) or
                style_config.get('include_images', True) or
                context.platform in ['instagram', 'youtube', 'linkedin']  # Visual platforms
            )
            
            if not images_needed:
                logger.info("Images not required for this content type")
                return self._create_empty_image_result("Images not required")
            
            # Determine optimal image style
            optimal_style = self.determine_optimal_image_style(context)
            
            # Create image specification
            image_spec = self.create_image_specification(context, optimal_style)
            
            # Generate enhanced prompt
            image_prompt = self.create_advanced_image_prompt(context, optimal_style)
            
            logger.info(f"Generating image with style: {optimal_style.value}, size: {image_spec.size}")
            
            # Generate image using OpenAI DALL-E
            response = await self._generate_with_openai(image_prompt, image_spec)
            
            if response and response.data:
                image_url = response.data[0].url
                
                # Create comprehensive result
                result = self._create_successful_image_result(
                    image_url, context, optimal_style, image_spec, image_prompt
                )
                
                logger.info(f"Image generation successful: {image_url}")
                return result
            else:
                logger.error("OpenAI API returned empty response")
                return self._create_error_image_result("Empty API response", context, optimal_style)
                
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return self._create_error_image_result(str(e), 
                                                 getattr(locals(), 'context', None), 
                                                 getattr(locals(), 'optimal_style', ImageStyle.PROFESSIONAL))
    
    async def _generate_with_openai(self, prompt: str, spec: ImageSpecification):
        """Generate image with OpenAI API (with proper async handling)"""
        
        # OpenAI client is sync, so we need to run it in executor
        loop = asyncio.get_event_loop()
        
        def _sync_generate():
            return self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=spec.size,
                quality=spec.quality,
                n=1
            )
        
        return await loop.run_in_executor(None, _sync_generate)
    
    def _create_successful_image_result(self, image_url: str, context: ImageGenerationContext, 
                                    style: ImageStyle, spec: ImageSpecification, prompt: str) -> Dict:
        """Create comprehensive successful result"""

        return {
            "cover_image_url": image_url,
            "image_metadata": {
                "generation_successful": True,
                "style": style.value,
                "platform_optimized": context.platform,
                "size": spec.size,
                "aspect_ratio": spec.aspect_ratio,
                "quality": spec.quality,
                "prompt_used": prompt,
                "visual_keywords": self.extract_enhanced_visual_keywords(context),
                "target_audience": context.audience,
                "complexity_level": context.complexity_level,
                "innovation_level": context.innovation_level,
                "generation_timestamp": datetime.now().isoformat(),
                "color_scheme": spec.color_scheme,
                "composition_type": spec.composition_type
            }
        }


    def _create_error_image_result(self, error_message: str, context: Optional[ImageGenerationContext], 
                                   style: Optional[ImageStyle]) -> Dict:
        """Create comprehensive error result with fallback"""
    
        fallback_url = "https://via.placeholder.com/1200x800/4A90E2/FFFFFF?text=Content+Image"
    
        return {
            "cover_image_url": fallback_url,
            "image_metadata": {
                "generation_successful": False,
                "error": error_message,
                "fallback_used": True,
                "style_attempted": style.value if style else "unknown",
                "platform": context.platform if context else "unknown",
                "generation_timestamp": datetime.now().isoformat(),
                "note": "Using placeholder image due to generation failure"
            }
        }
    
    
    def _create_empty_image_result(self, reason: str) -> Dict:
        """Create result when no image is needed"""
    
        return {
            "cover_image_url": "",
            "image_metadata": {
                "generation_successful": True,
                "image_skipped": True,
                "reason": reason,
                "generation_timestamp": datetime.now().isoformat()
            }
        }

    
    # Enhanced legacy method for backward compatibility and sync execution
    def generate_enhanced_image(self, state: Dict) -> Dict:
        """Legacy sync method - enhanced for production use"""
        
        logger.info(f"Using sync image generation for topic: {state.get('topic', 'Unknown')}")
        
        try:
            # Extract comprehensive context (same as async version)
            context = self.extract_generation_context(state)
            
            # Determine if images are needed
            template_config = context.template_config
            style_config = context.style_profile
            
            images_needed = (
                template_config.get('images_needed', True) or
                style_config.get('include_images', True) or
                context.platform in ['instagram', 'youtube', 'linkedin']
            )
            
            if not images_needed:
                logger.info("Images not required for this content type")
                return self._create_empty_image_result("Images not required")
            
            # Determine optimal image style
            optimal_style = self.determine_optimal_image_style(context)
            
            # Create image specification  
            image_spec = self.create_image_specification(context, optimal_style)
            
            # Generate enhanced prompt
            image_prompt = self.create_advanced_image_prompt(context, optimal_style)
            
            logger.info(f"Generating image with style: {optimal_style.value}, size: {image_spec.size}")
            
            # Generate image using OpenAI DALL-E (sync version)
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size=image_spec.size,
                quality=image_spec.quality,
                n=1
            )
            
            if response and response.data:
                image_url = response.data[0].url
                
                # Create comprehensive result
                result = self._create_successful_image_result(
                    image_url, context, optimal_style, image_spec, image_prompt
                )
                
                logger.info(f"Sync image generation successful: {image_url}")
                return result
            else:
                logger.error("OpenAI API returned empty response")
                return self._create_error_image_result("Empty API response", context, optimal_style)
                
        except Exception as e:
            logger.error(f"Sync image generation failed: {str(e)}")
            return self._create_error_image_result(str(e), 
                                                 getattr(locals(), 'context', None), 
                                                 getattr(locals(), 'optimal_style', ImageStyle.PROFESSIONAL))
    
    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """ENTERPRISE EXECUTE METHOD - Required for graph integration"""
        logger.info(f"Executing Enhanced Image Agent for topic: {state.content_spec.topic}")
        
        # TEMPLATE INJECTION: Extract template_config
        template_config = getattr(state, 'template_config', {})
        if not template_config and hasattr(state, 'content_spec'):
            template_config = state.content_spec.business_context.get('template_config', {})
        
        # Get dynamic instructions
        instructions = state.get_agent_instructions(self.agent_type)
        
        # Log execution start
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "template_config_found": bool(template_config),
            "instructions_received": len(instructions.primary_objectives) if instructions else 0
        })
        
        try:
            # Execute image generation using existing sync method
            image_result = self.generate_enhanced_image(state)
            
            # Update state with image results
            if image_result.get("cover_image_url"):
                state.generated_images = [image_result]
            
            # Update phase
            state.update_phase(ContentPhase.CODE_GENERATION)
            
            # Log successful completion
            state.log_agent_execution(self.agent_type, {
                "status": "completed",
                "image_generated": bool(image_result.get("cover_image_url")),
                "generation_successful": image_result.get("image_metadata", {}).get("generation_successful", False)
            })
            
            logger.info("✅ Enhanced Image Agent completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"❌ Enhanced Image Agent failed: {e}")
            state.log_agent_execution(self.agent_type, {
                "status": "failed",
                "error": str(e)
            })
            return state

# Enhanced workflow integration functions
def _enhanced_image_agent_sync_fn(state: dict) -> dict:
    """Enhanced image agent function for LangGraph workflow - sync version with proper async handling"""
    image_agent = EnhancedImageAgent()
    
    # Check if we're already in an async context

    logger.info("Running in existing event loop context")
        
    # We're in an async context, so we need to handle this carefully
    # Use the legacy sync method to avoid event loop conflicts
    return image_agent.generate_enhanced_image(state)
        
   

# Async version for when explicitly needed
async def _enhanced_image_agent_async_fn(state: dict) -> dict:
    """Enhanced image agent function for LangGraph workflow - async version"""
    image_agent = EnhancedImageAgent()
    return await image_agent.generate_images(state)

# Export sync version for LangGraph compatibility
image_agent = RunnableLambda(_enhanced_image_agent_sync_fn)

# Export async version for advanced workflows
image_agent_async = RunnableLambda(_enhanced_image_agent_async_fn)

# Backward compatibility
enhanced_image_agent = image_agent