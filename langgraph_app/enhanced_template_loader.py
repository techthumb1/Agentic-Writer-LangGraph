# langgraph_app/enhanced_template_loader.py
"""
Enhanced Template Loader that combines your existing YAML templates with universal generation
This replaces your current template_loader.py with backward compatibility
"""

import os
import yaml
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass

# Import universal system
from .universal_system import TrulyDynamicContentSystem, LangGraphUniversalIntegration

@dataclass
class EnhancedTemplate:
    """Enhanced template that can be static or dynamically generated"""
    id: str
    name: str
    content: Dict[str, Any]
    source: str  # "static_yaml" or "dynamic_generated"
    category: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]

class EnhancedTemplateLoader:
    """
    Enhanced template loader that maintains compatibility with your existing system
    while adding universal dynamic generation capabilities
    """
    
    def __init__(self, templates_dir: str = "data/content_templates"):
        self.templates_dir = Path(templates_dir)
        self.static_templates = {}
        self.dynamic_system = TrulyDynamicContentSystem()
        self.universal_integration = LangGraphUniversalIntegration()
        
        # Load existing static templates
        self._load_static_templates()
        
        print(f"📚 Enhanced Template Loader initialized")
        print(f"   📁 Static templates: {len(self.static_templates)}")
        print(f"   🤖 Dynamic generation: Enabled")
    
    def _load_static_templates(self):
        """Load existing static YAML templates"""
        
        if not self.templates_dir.exists():
            print(f"⚠️  Templates directory not found: {self.templates_dir}")
            return
        
        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                
                if template_data and isinstance(template_data, dict):
                    template_id = template_data.get('id', template_file.stem)
                    
                    enhanced_template = EnhancedTemplate(
                        id=template_id,
                        name=template_data.get('name', template_file.stem),
                        content=template_data,
                        source="static_yaml",
                        category=template_data.get('category', 'general'),
                        parameters=template_data.get('parameters', {}),
                        metadata=template_data.get('metadata', {})
                    )
                    
                    self.static_templates[template_id] = enhanced_template
                    print(f"✅ Loaded static template: {template_id}")
                    
            except Exception as e:
                print(f"❌ Error loading template {template_file}: {e}")
    
    async def get_template(
        self, 
        template_id: Optional[str] = None,
        user_request: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> EnhancedTemplate:
        """
        Get template - either existing static or dynamically generated
        
        Priority:
        1. If template_id specified and exists -> return static template
        2. If user_request provided -> generate dynamic template
        3. Otherwise -> return default universal template
        """
        
        # Try to get static template first
        if template_id and template_id in self.static_templates:
            print(f"📋 Using static template: {template_id}")
            return self.static_templates[template_id]
        
        # Generate dynamic template
        if user_request:
            print(f"🤖 Generating dynamic template for: {user_request[:50]}...")
            return await self._generate_dynamic_template(user_request, user_context)
        
        # Fallback to universal template
        print("🔧 Using fallback universal template")
        return self._get_fallback_template()
    
    async def _generate_dynamic_template(
        self, 
        user_request: str, 
        user_context: Optional[Dict[str, Any]]
    ) -> EnhancedTemplate:
        """Generate dynamic template for user request"""
        
        try:
            # Use universal system to generate approach
            content_approach = await self.dynamic_system.generate_content_approach(user_request)
            
            # Extract generated content
            analysis = content_approach["content_analysis"]
            template_yaml = content_approach["generated_template"]
            
            # Parse the generated template
            template_data = yaml.safe_load(template_yaml)
            
            # Create enhanced template
            template_id = f"dynamic_{analysis['topic_domain']}_{hash(user_request) % 10000}"
            
            enhanced_template = EnhancedTemplate(
                id=template_id,
                name=f"Dynamic {analysis['content_type'].replace('_', ' ').title()}",
                content=template_data,
                source="dynamic_generated",
                category=analysis.get('topic_domain', 'general'),
                parameters=self._extract_parameters_from_template(template_data),
                metadata={
                    "user_request": user_request,
                    "analysis": analysis,
                    "generated_at": "runtime",
                    "topic_domain": analysis.get('topic_domain'),
                    "content_type": analysis.get('content_type'),
                    "optimal_length": analysis.get('optimal_length')
                }
            )
            
            print(f"✨ Generated dynamic template: {template_id}")
            return enhanced_template
            
        except Exception as e:
            print(f"❌ Error generating dynamic template: {e}")
            return self._get_fallback_template()
    
    def _extract_parameters_from_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        # Handle V2 inputs format
        if 'inputs' in template_data:
            inputs = template_data['inputs']
            param_dict = {}

            for key, spec in inputs.items():
                param_dict[key] = {
                    'name': key,
                    'label': key.replace('_', ' ').title(),
                    'type': self._infer_input_type(spec),
                    'required': spec.get('required', False),
                    'default': spec.get('default', ''),
                    'commonly_used': key in ['topic', 'audience', 'tone', 'content_type']
                }
            return param_dict

        # Handle legacy parameters
        parameters = template_data.get('parameters', [])
        if isinstance(parameters, list):
            param_dict = {}
            for param in parameters:
                if isinstance(param, dict) and 'name' in param:
                    param_dict[param['name']] = param
            return param_dict

        return parameters if isinstance(parameters, dict) else {}
    
   
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available static templates"""
        
        templates = []
        for template_id, template in self.static_templates.items():
            templates.append({
                "id": template.id,
                "name": template.name,
                "category": template.category,
                "source": template.source,
                "description": template.content.get("description", ""),
                "parameters_count": len(template.parameters)
            })
        
        return templates
    
    def get_template_by_category(self, category: str) -> List[EnhancedTemplate]:
        """Get templates by category"""
        
        return [
            template for template in self.static_templates.values()
            if template.category == category
        ]
    
    async def get_optimal_template_for_request(
        self, 
        user_request: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get the optimal template and configuration for a user request
        This is the main method that replaces your current template selection logic
        """
        
        # Check if any existing templates are suitable
        suitable_static = self._find_suitable_static_template(user_request)
        
        if suitable_static and self._is_static_template_adequate(suitable_static, user_request):
            # Use existing static template
            template = suitable_static
            approach = "static_template"
        else:
            # Generate dynamic template
            template = await self._generate_dynamic_template(user_request, user_context)
            approach = "dynamic_generation"
        
        # Get optimal style and model
        optimal_style = self._get_optimal_style_for_template(template, user_request)
        optimal_model = self._get_optimal_model_for_template(template, optimal_style)
        
        return {
            "template": template,
            "approach": approach,
            "style_profile": optimal_style,
            "model": optimal_model,
            "parameters": self._generate_intelligent_parameters(template, user_request),
            "metadata": {
                "user_request": user_request,
                "template_source": template.source,
                "confidence": 0.9 if approach == "dynamic_generation" else 0.7
            }
        }
    
    def _find_suitable_static_template(self, user_request: str) -> Optional[EnhancedTemplate]:
        """Find suitable static template for user request"""
        
        request_lower = user_request.lower()
        
        # Simple keyword matching for now
        topic_keywords = {
            "blog": ["blog", "article", "post"],
            "technical": ["technical", "implementation", "code", "programming"],
            "academic": ["research", "analysis", "study", "academic"],
            "tutorial": ["tutorial", "guide", "how to", "step by step"]
        }
        
        for template in self.static_templates.values():
            template_category = template.category.lower()
            template_name = template.name.lower()
            
            # Check if template matches request keywords
            for topic, keywords in topic_keywords.items():
                if topic in template_category or topic in template_name:
                    if any(keyword in request_lower for keyword in keywords):
                        return template
        
        return None
    
    def _is_static_template_adequate(self, template: EnhancedTemplate, user_request: str) -> bool:
        """Check if static template is adequate for the request"""
        
        # Check if template supports substantial content generation
        instructions = template.content.get("instructions", "")
        system_prompt = template.content.get("system_prompt", "")
        
        # Simple heuristics for adequacy
        has_substantial_instructions = len(instructions) > 200
        has_good_system_prompt = len(system_prompt) > 100
        has_parameters = len(template.parameters) > 0
        
        return has_substantial_instructions and has_good_system_prompt
    
    def _get_optimal_style_for_template(self, template: EnhancedTemplate, user_request: str) -> str:
        """Get optimal style profile for template and request"""
        
        # Extract topic domain from template or request
        category = template.category.lower()
        request_lower = user_request.lower()
        
        # Style mapping based on content domain
        if any(term in category or term in request_lower for term in ['technical', 'programming', 'code']):
            return "technical_dive"
        elif any(term in category or term in request_lower for term in ['academic', 'research', 'analysis']):
            return "phd_academic"
        elif any(term in category or term in request_lower for term in ['business', 'startup', 'entrepreneur']):
            return "startup_storytelling"
        elif any(term in category or term in request_lower for term in ['beginner', 'tutorial', 'guide']):
            return "beginner_friendly"
        else:
            return "educational_expert"  # Default
    
    def _get_optimal_model_for_template(self, template: EnhancedTemplate, style_profile: str) -> str:
        """Get optimal model for template and style"""
        
        # Use your existing model selection logic
        try:
            from .enhanced_model_registry import get_optimal_model_for_style
            return get_optimal_model_for_style(style_profile, "writer")
        except ImportError:
            # Fallback model selection
            if "technical" in style_profile or "academic" in style_profile:
                return "claude-3-5-sonnet-20241022"
            else:
                return "gpt-4o"
    
    def _generate_intelligent_parameters(self, template: EnhancedTemplate, user_request: str) -> Dict[str, Any]:
        """Generate intelligent parameters based on template and request"""
        
        # Extract parameters from template
        base_parameters = template.parameters.copy()
        
        # Add intelligent defaults based on request analysis
        request_lower = user_request.lower()
        
        # Analyze request for implicit parameters
        if "beginner" in request_lower or "introduction" in request_lower:
            base_parameters["audience_level"] = "beginner"
        elif "advanced" in request_lower or "expert" in request_lower:
            base_parameters["audience_level"] = "advanced"
        else:
            base_parameters["audience_level"] = "intermediate"
        
        # Detect content focus
        if "how to" in request_lower:
            base_parameters["content_approach"] = "tutorial"
        elif "why" in request_lower or "analysis" in request_lower:
            base_parameters["content_approach"] = "analytical"
        elif "comparison" in request_lower or "vs" in request_lower:
            base_parameters["content_approach"] = "comparative"
        else:
            base_parameters["content_approach"] = "informative"
        
        # Detect length requirements
        if "comprehensive" in request_lower or "detailed" in request_lower:
            base_parameters["content_length"] = "comprehensive"
        elif "brief" in request_lower or "quick" in request_lower:
            base_parameters["content_length"] = "concise"
        else:
            base_parameters["content_length"] = "standard"
        
        return base_parameters

# Backward compatibility functions for your existing system
class BackwardCompatibleTemplateLoader:
    """
    Wrapper that provides backward compatibility with your existing template loading code
    """
    
    def __init__(self):
        self.enhanced_loader = EnhancedTemplateLoader()
    
    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Load template by ID (backward compatible)"""
        
        if template_id in self.enhanced_loader.static_templates:
            template = self.enhanced_loader.static_templates[template_id]
            return template.content
        return None
    
    def load_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load all templates (backward compatible)"""
        
        templates = {}
        for template_id, enhanced_template in self.enhanced_loader.static_templates.items():
            templates[template_id] = enhanced_template.content
        return templates
    
    async def get_template_for_generation(
        self, 
        user_request: str,
        template_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get template optimized for content generation (new enhanced method)"""
        
        return await self.enhanced_loader.get_optimal_template_for_request(
            user_request, user_context
        )

# Integration helper for your existing workflow
async def integrate_with_existing_system(
    user_request: str,
    template_id: Optional[str] = None,
    style_profile: Optional[str] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main integration function that replaces your current template selection logic
    
    This function can be called from your existing mcp_server_extension.py or wherever
    you currently handle template loading and content generation setup.
    """
    
    # Initialize the enhanced loader
    loader = EnhancedTemplateLoader()
    
    # Get optimal template and configuration
    if template_id:
        # User explicitly selected a template
        template = await loader.get_template(template_id=template_id, user_request=user_request)
        approach = "explicit_selection"
    else:
        # Use intelligent template selection
        result = await loader.get_optimal_template_for_request(user_request, user_context)
        template = result["template"]
        approach = result["approach"]
        style_profile = style_profile or result["style_profile"]
    
    # Extract content generation components
    system_prompt = template.content.get("system_prompt", "")
    instructions = template.content.get("instructions", "")
    parameters = template.parameters
    
    # Get optimal model if not specified
    if not style_profile:
        style_profile = loader._get_optimal_style_for_template(template, user_request)
    
    model = loader._get_optimal_model_for_template(template, style_profile)
    
    return {
        "template": {
            "id": template.id,
            "name": template.name,
            "content": template.content,
            "source": template.source
        },
        "generation_config": {
            "system_prompt": system_prompt,
            "instructions": instructions,
            "parameters": parameters,
            "style_profile": style_profile,
            "model": model
        },
        "metadata": {
            "approach": approach,
            "user_request": user_request,
            "template_source": template.source,
            "category": template.category
        }
    }

# Test function to verify integration
async def test_enhanced_loader():
    """Test the enhanced loader with various requests"""
    
    loader = EnhancedTemplateLoader()
    
    test_requests = [
        "I want to write about implementing neural networks in PyTorch",
        "How to grow herbs in a small apartment garden",
        "Analysis of ranked choice voting systems",
        "Building a FastAPI web application tutorial"
    ]
    
    print("🧪 Testing Enhanced Template Loader")
    print("=" * 60)
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n🔍 Test {i}: {request}")
        
        result = await integrate_with_existing_system(request)
        
        template = result["template"]
        config = result["generation_config"]
        metadata = result["metadata"]
        
        print(f"📋 Template: {template['name']} ({template['source']})")
        print(f"🎨 Style: {config['style_profile']}")
        print(f"🤖 Model: {config['model']}")
        print(f"🎯 Approach: {metadata['approach']}")
        print(f"📏 Parameters: {len(config['parameters'])}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_loader())