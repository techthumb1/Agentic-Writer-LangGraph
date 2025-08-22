import os
import yaml
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass

from .universal_dynamic_generator import TrulyDynamicContentSystem

@dataclass
class ContentGenerationPayload:
    """Complete payload for content generation"""
    template_yaml: str
    parameters: Dict[str, Any]
    style_profile: str
    metadata: Dict[str, Any]
    estimated_length: str
    reading_time: str

class UniversalTemplateManager:
    """
    Replaces your current template system with universal dynamic generation
    Integrates with your existing LangGraph workflow
    """
    
    def __init__(self, templates_dir: str = "data/content_templates"):
        self.templates_dir = Path(templates_dir)
        self.dynamic_system = TrulyDynamicContentSystem()
        self.static_templates = {}
        self.generated_templates_cache = {}
        
        # Load any existing static templates as fallbacks
        self._load_existing_templates()
    
    def _load_existing_templates(self):
        """Load existing templates as fallbacks"""
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob("*.yaml"):
                try:
                    with open(template_file, 'r') as f:
                        template_data = yaml.safe_load(f)
                        if template_data and 'id' in template_data:
                            self.static_templates[template_data['id']] = template_data
                except Exception as e:
                    print(f"Error loading template {template_file}: {e}")
    
    async def get_content_generation_payload(
        self, 
        user_request: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> ContentGenerationPayload:
        """
        Main entry point: takes ANY user request and returns complete generation payload
        This replaces your current template selection logic
        """
        
        print(f"🎯 Processing request: {user_request[:100]}...")
        
        # Generate dynamic approach for this specific request
        content_approach = await self.dynamic_system.generate_content_approach(user_request)
        
        # Extract key information
        analysis = content_approach["content_analysis"]
        template_yaml = content_approach["generated_template"]
        
        # Intelligently select parameters based on the content
        parameters = self._extract_intelligent_parameters(user_request, analysis, user_preferences)
        
        # Select optimal style profile for this content type - FIXED
        style_profile = await self._select_optimal_style_llm(analysis, user_preferences)
        
        # Calculate metadata
        metadata = {
            "topic_domain": analysis["topic_domain"],
            "content_type": analysis["content_type"],
            "auto_generated": True,
            "user_request": user_request,
            "confidence_score": 0.9,
            "generation_approach": "universal_dynamic"
        }
        
        return ContentGenerationPayload(
            template_yaml=template_yaml,
            parameters=parameters,
            style_profile=style_profile,
            metadata=metadata,
            estimated_length=analysis["optimal_length"],
            reading_time=self._calculate_reading_time(analysis["optimal_length"])
        )
    
    def _extract_intelligent_parameters(
        self, 
        user_request: str, 
        analysis: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract and set intelligent parameters based on the request"""
        
        parameters = {}
        
        # Set core parameters based on analysis
        parameters["content_focus"] = self._extract_specific_focus(user_request, analysis)
        parameters["audience_level"] = analysis.get("audience_level", "intermediate")
        parameters["content_approach"] = analysis.get("content_type", "informative_guide")
        parameters["writing_style"] = analysis.get("writing_style", "conversational")
        
        # Apply user preferences if provided
        if user_preferences:
            parameters.update(user_preferences)
        
        return parameters
    
    def _extract_specific_focus(self, user_request: str, analysis: Dict[str, Any]) -> str:
        """Extract the specific focus from the user request"""
        
        # Look for specific keywords or phrases in the request
        request_lower = user_request.lower()
        
        # Extract the main topic/focus
        key_elements = analysis.get("key_elements", [])
        if key_elements:
            return key_elements[0]  # Use first key element as primary focus
        
        # Fallback to extracting from the request itself
        if "how to" in request_lower:
            return "practical_implementation"
        elif "why" in request_lower or "impact" in request_lower:
            return "analysis_and_explanation"
        elif "best" in request_lower or "guide" in request_lower:
            return "comprehensive_guide"
        elif "comparison" in request_lower or "vs" in request_lower:
            return "comparative_analysis"
        else:
            return "informative_overview"
    
    def _get_available_style_profiles(self) -> List[str]:
        """Get actual available style profiles from the system"""
        try:
            from ..integrated_server import load_style_profiles
            profiles = load_style_profiles()
            return [p.id for p in profiles]
        except:
            # Fallback to scanning data directory
            profiles_dir = Path("data/style_profiles")
            if profiles_dir.exists():
                return [f.stem for f in profiles_dir.glob("*.yaml")]
            return ["social_media_voice"]  # Safe fallback
    
    async def _select_optimal_style_llm(
        self, 
        analysis: Dict[str, Any], 
        user_preferences: Optional[Dict[str, Any]]
    ) -> str:
        """Use LLM to select optimal style from available profiles"""
        
        # If user has explicit preference, use it
        if user_preferences:
            pref = user_preferences.get("preferred_style") or user_preferences.get("style_preference")
            if pref:
                available = self._get_available_style_profiles()
                if pref in available:
                    return pref
        
        # Get available profiles
        available_profiles = self._get_available_style_profiles()
        
        if not available_profiles:
            return "social_media_voice"  # Fallback
        
        # Use LLM to select best match
        try:
            if hasattr(self.dynamic_system.generator, 'anthropic_client') and self.dynamic_system.generator.anthropic_client:
                selection_prompt = f"""
Select the most appropriate style profile for this content:

CONTENT ANALYSIS:
{json.dumps(analysis, indent=2)}

AVAILABLE STYLE PROFILES:
{', '.join(available_profiles)}

Return ONLY the style profile ID that best matches the content type, audience, and topic.
"""
                
                response = await self.dynamic_system.generator.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=50,
                    temperature=0.1,
                    messages=[{"role": "user", "content": selection_prompt}]
                )
                
                selected = response.content[0].text.strip()
                if selected in available_profiles:
                    return selected
        except Exception as e:
            print(f"LLM style selection failed: {e}")
        
        # Fallback to first available profile
        return available_profiles[0] if available_profiles else "social_media_voice"
    
    def _calculate_reading_time(self, word_range: str) -> str:
        """Calculate estimated reading time from word range"""
        
        try:
            # Extract numbers from word range (e.g., "2000-3500" -> 2750 average)
            if "-" in word_range:
                parts = word_range.split("-")
                min_words = int(''.join(filter(str.isdigit, parts[0])))
                max_words = int(''.join(filter(str.isdigit, parts[1])))
                avg_words = (min_words + max_words) // 2
            else:
                avg_words = int(''.join(filter(str.isdigit, word_range)))
            
            # Calculate reading time (average 200 words per minute)
            minutes = avg_words // 200
            
            if minutes < 5:
                return f"{minutes} min read"
            elif minutes < 60:
                return f"{minutes} min read"
            else:
                hours = minutes // 60
                remaining_min = minutes % 60
                return f"{hours}h {remaining_min}m read"
                
        except:
            return "10 min read"  # Default fallback
    
    async def save_generated_template(self, template_yaml: str, metadata: Dict[str, Any]):
        """Optionally save successful generated templates for reuse"""
        
        try:
            template_data = yaml.safe_load(template_yaml)
            template_id = template_data.get('id', 'unknown')
            
            # Save to cache
            self.generated_templates_cache[template_id] = {
                "yaml": template_yaml,
                "metadata": metadata,
                "usage_count": 1
            }
            
            # Optionally save to disk for persistence
            cache_dir = Path("generated_templates_cache")
            cache_dir.mkdir(exist_ok=True)
            
            cache_file = cache_dir / f"{template_id}.yaml"
            with open(cache_file, 'w') as f:
                f.write(template_yaml)
                
        except Exception as e:
            print(f"Error saving generated template: {e}")

# Integration with your existing LangGraph system
class LangGraphUniversalIntegration:
    """
    Integration layer between the universal template system and your LangGraph workflow
    """
    
    def __init__(self):
        self.template_manager = UniversalTemplateManager()
    
    async def process_content_request(
        self, 
        user_request: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main integration point: replaces your current template selection logic
        Returns everything needed for your LangGraph content generation workflow
        """
        
        # Get comprehensive generation payload
        payload = await self.template_manager.get_content_generation_payload(
            user_request, 
            user_context
        )
        
        # Convert to format expected by your existing system
        return {
            # For your template system
            "template": {
                "yaml_content": payload.template_yaml,
                "metadata": payload.metadata
            },
            
            # For your parameter system
            "parameters": payload.parameters,
            
            # For your style system
            "style_profile": payload.style_profile,
            
            # For your model selection (using your existing logic)
            "recommended_model": self._get_model_recommendation(payload),
            
            # Additional metadata
            "generation_info": {
                "estimated_length": payload.estimated_length,
                "reading_time": payload.reading_time,
                "approach": "universal_dynamic",
                "confidence": payload.metadata.get("confidence_score", 0.9)
            }
        }
    
    def _get_model_recommendation(self, payload: ContentGenerationPayload) -> str:
        """
        Integrate with your existing model selection logic
        """
        # Use your existing get_optimal_model_for_style function
        try:
            from ..enhanced_model_registry import get_optimal_model_for_style
            return get_optimal_model_for_style(payload.style_profile, "writer")
        except:
            # Fallback model selection
            if "technical" in payload.style_profile or "academic" in payload.style_profile:
                return "claude-3-5-sonnet-20241022"
            else:
                return "gpt-4o"