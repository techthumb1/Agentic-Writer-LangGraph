# langgraph_app/enhanced_generate_endpoint.py
"""
Enhanced content generation endpoint that integrates Universal Template System
This replaces or enhances your existing content generation logic
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# FastAPI imports (assuming you're using FastAPI)
from fastapi import HTTPException
from pydantic import BaseModel
from .mcp_server_extension import enhanced_mcp_manager

# Your existing imports
try:
    from .enhanced_model_registry import get_optimal_model_for_style
    from .style_profile_loader import load_style_profiles
    # Add other existing imports as needed
except ImportError:
    print("⚠️ Some existing modules not found - using fallbacks")
    def get_optimal_model_for_style(*args): return "claude-3-sonnet-20240229"
    def load_style_profiles(): return {}

# Universal system imports
from .universal_system.universal_dynamic_generator import UniversalTemplateGenerator
from .universal_system.universal_integration import LangGraphUniversalIntegration

@dataclass
class ContentGenerationRequest:
    """Enhanced request model for universal content generation"""
    user_request: str
    template_id: Optional[str] = None
    style_profile: Optional[str] = None
    custom_parameters: Optional[Dict[str, Any]] = None
    user_context: Optional[Dict[str, Any]] = None
    length_preference: Optional[str] = None  
    audience_level: Optional[str] = None     
    generation_settings: Optional[Dict[str, Any]] = None  
    generation_mode: Optional[str] = None                 

class ContentGenerationResponse(BaseModel):
    """Response model for generated content"""
    request_id: str
    status: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    generated_template: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class EnhancedContentGenerator:
    """Enhanced content generator with universal template support"""
    
    def __init__(self):
        self.universal_generator = UniversalTemplateGenerator()
        self.universal_integration = LangGraphUniversalIntegration()
        self.style_profiles = load_style_profiles()
        
    async def generate_content(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """
        Main content generation method with universal template support
        """
        request_id = str(uuid.uuid4())
        
        try:
            # Step 1: Determine if we need dynamic template generation
            use_dynamic = await self._should_use_dynamic_generation(request)
            
            if use_dynamic:
                # Use universal dynamic generation
                result = await self.universal_integration.process_content_request(
                    user_request=request.user_request,
                    user_context=request.user_context or {},
                    style_preference=request.style_profile,
                    length_preference=request.length_preference,
                    audience_level=request.audience_level
                )
                
                return ContentGenerationResponse(
                    request_id=request_id,
                    status="completed",
                    content=result["content"],
                    metadata={
                        "generation_method": "universal_dynamic",
                        "template_analysis": result.get("template_analysis"),
                        "intelligent_parameters": result.get("parameters"),
                        "generation_time": result.get("generation_time"),
                        "word_count": len(result["content"].split()) if result.get("content") else 0
                    },
                    generated_template=result.get("generated_template")
                )
            
            else:
                # Use existing template system (backward compatibility)
                result = await self._generate_with_existing_system(request)
                
                return ContentGenerationResponse(
                    request_id=request_id,
                    status="completed",
                    content=result["content"],
                    metadata={
                        "generation_method": "traditional_template",
                        "template_id": request.template_id,
                        "style_profile": request.style_profile,
                        "word_count": len(result["content"].split()) if result.get("content") else 0
                    }
                )
                
        except Exception as e:
            print(f"❌ Content generation error: {str(e)}")
            return ContentGenerationResponse(
                request_id=request_id,
                status="error",
                error=str(e)
            )
    
    async def _should_use_dynamic_generation(self, request: ContentGenerationRequest) -> bool:
        """
        Determine whether to use dynamic generation vs existing templates
        """
        # Use dynamic if:
        # 1. No specific template requested
        # 2. User request contains topics outside existing templates
        # 3. User explicitly wants dynamic generation
        
        if not request.template_id:
            return True
            
        # Check if the user request seems to need dynamic generation
        dynamic_indicators = [
            "write about", "create content about", "generate", "make something about",
            "gardening", "cooking", "travel", "politics", "personal", "hobby",
            "machine learning", "data science", "AI", "artificial intelligence"
        ]
        
        user_request_lower = request.user_request.lower()
        if any(indicator in user_request_lower for indicator in dynamic_indicators):
            return True
            
        return False
    
    async def _generate_with_existing_system(self, request: ContentGenerationRequest) -> Dict[str, Any]:
        """
        Generate content using your existing template system (for backward compatibility)
        """
        # Import your existing generation logic here
        # This is a placeholder - replace with your actual existing system
        
        try:
            # Your existing template loading and generation code
            from .template_loader import load_template  # Adjust import as needed
            
            template = load_template(request.template_id)
            
            # Generate content using your existing workflow
            # Replace this with your actual generation logic
            content = f"Content generated using existing system for template: {request.template_id}"
            
            return {
                "content": content,
                "template_id": request.template_id,
                "generation_method": "existing"
            }
            
        except Exception as e:
            print(f"⚠️ Existing system fallback failed: {str(e)}")
            # Fallback to dynamic generation
            result = await self.universal_integration.process_content_request(
                user_request=request.user_request,
                user_context=request.user_context or {}
            )
            return result

# FastAPI endpoint functions
async def enhanced_generate_content(request_data: Dict[str, Any]) -> ContentGenerationResponse:
    """
    Enhanced FastAPI endpoint for content generation
    This replaces or enhances your existing /generate endpoint
    """
    generator = EnhancedContentGenerator()
    
    # Convert request data to our enhanced request model
    request = ContentGenerationRequest(
        user_request=request_data.get("user_request", ""),
        template_id=request_data.get("template_id"),
        style_profile=request_data.get("style_profile"),
        custom_parameters=request_data.get("custom_parameters"),
        user_context=request_data.get("user_context", {}),
        length_preference=request_data.get("length_preference"),
        audience_level=request_data.get("audience_level")
    )
    
    return await generator.generate_content(request)

# Integration with your existing server
def integrate_with_existing_server(app):
    """
    Function to integrate enhanced generation with your existing FastAPI app
    """
    
    @app.post("/api/universal-generate")
    async def universal_generate_endpoint(request_data: Dict[str, Any]):
        """Pure universal generation endpoint (always uses dynamic templates)"""
        generator = EnhancedContentGenerator()
        
        request = ContentGenerationRequest(
            user_request=request_data.get("user_request", ""),
            template_id=request_data.get("template_id"),
            style_profile=request_data.get("style_profile"),
            custom_parameters=request_data.get("custom_parameters"),
            user_context=request_data.get("user_context", {}),
            length_preference=request_data.get("length_preference"),
            audience_level=request_data.get("audience_level"),
            generation_settings=request_data.get("generation_settings"),  
            generation_mode=request_data.get("generation_mode")           
        )

        
        # Force dynamic generation
        result = await generator.universal_integration.process_content_request(
            user_request=request.user_request,
            user_context=request.user_context
        )
        
        return ContentGenerationResponse(
            request_id=str(uuid.uuid4()),
            status="completed",
            content=result["content"],
            metadata={
                "generation_method": "universal_dynamic",
                "template_analysis": result.get("template_analysis"),
                "word_count": len(result["content"].split()) if result.get("content") else 0
            },
            generated_template=result.get("generated_template")
        )

# Utility functions for your existing system
def get_content_suggestions(user_input: str) -> List[Dict[str, Any]]:
    """
    Get intelligent content suggestions based on user input
    """
    generator = UniversalTemplateGenerator()
    return asyncio.run(generator.get_content_suggestions(user_input))

def analyze_content_requirements(user_request: str) -> Dict[str, Any]:
    """
    Analyze user request to understand content requirements
    """
    integration = LangGraphUniversalIntegration()
    return asyncio.run(integration.analyze_content_requirements(user_request))

## Example usage and testing
#if __name__ == "__main__":
#    async def test_enhanced_generation():
#        """Test the enhanced generation system"""
#        
#        # Test 1: AI/ML content (your specialty)
#        request = ContentGenerationRequest(
#            user_request="Write a comprehensive guide about implementing gradient descent optimization for neural networks, including mathematical foundations and practical code examples",
#            length_preference="long",
#            audience_level="intermediate"
#        )
#        
#        generator = EnhancedContentGenerator()
#        result = await generator.generate_content(request)
#        
#        print("🤖 AI/ML Content Generation Test:")
#        print(f"Status: {result.status}")
#        print(f"Method: {result.metadata.get('generation_method')}")
#        print(f"Word Count: {result.metadata.get('word_count')}")
#        print(f"Content Preview: {result.content[:200] if result.content else 'None'}...")
#        print("\n" + "="*50 + "\n")
#        
#        # Test 2: Gardening content (non-technical)
#        request2 = ContentGenerationRequest(
#            user_request="How to grow heirloom tomatoes in containers for beginners",
#            length_preference="medium",
#            audience_level="beginner"
#        )
#        
#        result2 = await generator.generate_content(request2)
#        
#        print("🌱 Gardening Content Generation Test:")
#        print(f"Status: {result2.status}")
#        print(f"Method: {result2.metadata.get('generation_method')}")
#        print(f"Word Count: {result2.metadata.get('word_count')}")
#        print(f"Content Preview: {result2.content[:200] if result2.content else 'None'}...")
#        
#    # Run test
#    asyncio.run(test_enhanced_generation())