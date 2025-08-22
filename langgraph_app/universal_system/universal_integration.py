# langgraph_app/universal_integration.py
"""
Integration layer between Universal Template System and existing LangGraph workflow
This file bridges your current system with the new universal dynamic generation
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import your existing components
try:
    from ..enhanced_model_registry import get_optimal_model_for_style
except ImportError:
    # Fallback if import fails
    def get_optimal_model_for_style(style_profile: str, agent_type: str = "writer") -> str:
        if "technical" in style_profile or "academic" in style_profile:
            return "claude-3-5-sonnet-20241022"
        return "gpt-4o"

try:
    from ..integrated_server import load_style_profiles
except ImportError:
    def load_style_profiles():
        return []

# Import the universal system
from .universal_template_system import LangGraphUniversalIntegration
from .universal_dynamic_generator import TrulyDynamicContentSystem

class WriterzRoomUniversalAdapter:
    """
    Adapter that integrates universal template system with your existing WriterzRoom workflow
    """
    
    def __init__(self):
        self.universal_integration = LangGraphUniversalIntegration()
        self.dynamic_system = TrulyDynamicContentSystem()
        
        print("WriterzRoom Universal Adapter initialized")
    
    async def process_user_request(
        self, 
        user_request: str,
        template_id: Optional[str] = None,
        style_profile: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point that replaces your current template selection logic
        
        This handles ANY user request and returns everything needed for content generation
        """
        
        print(f"🔍 Processing request: {user_request[:100]}...")
        
        # If user explicitly selected template/style, respect their choice
        if template_id and style_profile:
            return await self._handle_explicit_selection(
                user_request, template_id, style_profile, user_context
            )
        
        # Otherwise, use universal dynamic generation
        return await self._handle_dynamic_generation(user_request, user_context)
    
    async def _handle_dynamic_generation(
        self, 
        user_request: str, 
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle fully dynamic content generation"""
        
        # Use universal system to generate optimal approach
        result = await self.universal_integration.process_content_request(
            user_request, user_context
        )
        
        # Extract the generated template content
        template_yaml = result["template"]["yaml_content"]
        
        # Format for your existing LangGraph workflow
        return {
            "approach": "universal_dynamic",
            "template_content": template_yaml,
            "parameters": result["parameters"],
            "style_profile": result["style_profile"],
            "model": result["recommended_model"],
            "metadata": {
                "user_request": user_request,
                "estimated_length": result["generation_info"]["estimated_length"],
                "reading_time": result["generation_info"]["reading_time"],
                "confidence": result["generation_info"]["confidence"],
                "template_source": "ai_generated"
            },
            "instructions": self._extract_instructions_from_yaml(template_yaml),
            "system_prompt": self._extract_system_prompt_from_yaml(template_yaml)
        }
    
    async def _handle_explicit_selection(
        self,
        user_request: str,
        template_id: str, 
        style_profile: str,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle explicit template/style selection"""
        
        # Load the selected template (your existing logic)
        template_content = self._load_existing_template(template_id)
        
        if not template_content:
            # Fall back to dynamic generation if template not found
            return await self._handle_dynamic_generation(user_request, user_context)
        
        # Use existing template with selected style
        model = get_optimal_model_for_style(style_profile)
        
        return {
            "approach": "explicit_selection",
            "template_content": template_content,
            "parameters": {},  # Could be extracted from template
            "style_profile": style_profile,
            "model": model,
            "metadata": {
                "user_request": user_request,
                "template_id": template_id,
                "template_source": "existing_yaml"
            },
            "instructions": template_content.get("instructions", ""),
            "system_prompt": template_content.get("system_prompt", "")
        }
    
    def _load_existing_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Load existing YAML template if it exists"""
        
        template_path = Path(f"data/content_templates/{template_id}.yaml")
        if not template_path.exists():
            return None
        
        try:
            import yaml
            with open(template_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading template {template_id}: {e}")
            return None
    
    def _extract_instructions_from_yaml(self, yaml_content: str) -> str:
        """Extract instructions from generated YAML"""
        
        try:
            import yaml
            template_data = yaml.safe_load(yaml_content)
            return template_data.get("instructions", "")
        except:
            return ""
    
    def _extract_system_prompt_from_yaml(self, yaml_content: str) -> str:
        """Extract system prompt from generated YAML"""
        
        try:
            import yaml
            template_data = yaml.safe_load(yaml_content)
            return template_data.get("system_prompt", "")
        except:
            return ""

# Integration with your existing server/API endpoints
class WriterzRoomAPIIntegration:
    """
    Integration for your existing API endpoints (like frontend/app/api/generate/route.ts)
    """
    
    def __init__(self):
        self.adapter = WriterzRoomUniversalAdapter()
    
    async def handle_api_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle API requests from your frontend
        
        Expected request_data format:
        {
            "user_request": "I want to write about...",
            "template_id": "optional_template_id", 
            "style_profile": "optional_style",
            "user_context": {...}
        }
        """
        
        user_request = request_data.get("user_request", "")
        template_id = request_data.get("template_id")
        style_profile = request_data.get("style_profile") 
        user_context = request_data.get("user_context", {})
        
        if not user_request:
            return {
                "error": "user_request is required",
                "success": False
            }
        
        try:
            # Process the request
            result = await self.adapter.process_user_request(
                user_request=user_request,
                template_id=template_id,
                style_profile=style_profile,
                user_context=user_context
            )
            
            # Format response for frontend
            return {
                "success": True,
                "approach": result["approach"],
                "template": {
                    "content": result["template_content"],
                    "instructions": result["instructions"],
                    "system_prompt": result["system_prompt"]
                },
                "generation_config": {
                    "parameters": result["parameters"],
                    "style_profile": result["style_profile"], 
                    "model": result["model"]
                },
                "metadata": result["metadata"]
            }
            
        except Exception as e:
            return {
                "error": f"Processing failed: {str(e)}",
                "success": False
            }

# Example usage for your existing workflow
async def example_integration():
    """
    Example showing how to integrate with your existing system
    """
    
    adapter = WriterzRoomUniversalAdapter()
    
    # Test requests that show the universal nature
    test_requests = [
        {
            "user_request": "I want to write about implementing LSTM networks for time series prediction",
            "user_context": {"expertise_level": "intermediate", "domain": "machine_learning"}
        },
        {
            "user_request": "How to grow tomatoes in containers on a small balcony",
            "user_context": {"expertise_level": "beginner", "domain": "gardening"}
        },
        {
            "user_request": "The benefits and drawbacks of ranked choice voting",
            "user_context": {"expertise_level": "general", "domain": "politics"}
        }
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n🧪 Test {i}: {request['user_request'][:50]}...")
        
        result = await adapter.process_user_request(**request)
        
        print(f"✅ Approach: {result['approach']}")
        print(f"🎨 Style: {result['style_profile']}")
        print(f"🤖 Model: {result['model']}")
        print(f"📏 Length: {result['metadata'].get('estimated_length', 'unknown')}")
        
        # Show template preview
        if isinstance(result['template_content'], str):
            lines = result['template_content'].split('\n')[:5]
            print(f"📋 Template preview:")
            for line in lines:
                print(f"    {line}")
            print("    ...")

if __name__ == "__main__":
    asyncio.run(example_integration())