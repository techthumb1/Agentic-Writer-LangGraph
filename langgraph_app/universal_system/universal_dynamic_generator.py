# Universal Dynamic Content Generator
# Adapts to ANY topic: gardening, politics, AI/ML, cooking, travel, business, etc.

import asyncio
import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from anthropic import AsyncAnthropic

@dataclass
class UniversalContentRequest:
    """Request for any type of content"""
    user_request: str
    desired_length: Optional[str] = None  # "short", "medium", "long", "comprehensive"
    target_audience: Optional[str] = None  # "beginners", "intermediate", "experts", "general"
    content_style: Optional[str] = None   # "casual", "professional", "academic", "conversational"

class UniversalDynamicGenerator:
    """Generates content templates for ANY topic - no restrictions"""
    
    def __init__(self):
        # Fix: Explicit API key loading for Anthropic
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        # Get API key explicitly
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("Warning: ANTHROPIC_API_KEY not found in environment")
            # Try alternative environment variable names
            api_key = os.getenv('CLAUDE_API_KEY') or os.getenv('ANTHROPIC_KEY')
        
        if api_key:
            self.anthropic_client = AsyncAnthropic(api_key=api_key)
            print(f"✅ Anthropic client initialized with key: {api_key[:10]}...")
        else:
            print("⚠️ No Anthropic API key found - using fallback mode")
            self.anthropic_client = None
    
    async def analyze_content_request(self, request: UniversalContentRequest) -> Dict[str, Any]:
        """Analyze ANY user request and determine optimal content approach"""
        
        # Check if client is available
        if not self.anthropic_client:
            print("⚠️ Anthropic client not available, using fallback analysis")
            return self._get_fallback_analysis()
        
        analysis_prompt = f"""
Analyze this content request and determine the optimal approach for high-quality content generation.

USER REQUEST: "{request.user_request}"

Analyze and provide:
1. TOPIC DOMAIN: What is this about? (e.g., gardening, politics, AI/ML, cooking, travel, business, personal development, etc.)
2. CONTENT TYPE: What type of content would be most valuable? (guide, analysis, tutorial, opinion piece, comparison, case study, etc.)
3. AUDIENCE LEVEL: Who would benefit from this? (beginners, intermediate, experts, general public)
4. OPTIMAL LENGTH: How long should this be for maximum value? (800-1500, 2000-3500, 4000-6000, 6000+ words)
5. WRITING STYLE: What tone/approach would work best? (casual, professional, academic, conversational, storytelling)
6. KEY ELEMENTS: What specific elements should be included? (examples, data, personal experience, step-by-step instructions, etc.)
7. UNIQUE ANGLE: What would make this content stand out and be genuinely useful?

Respond in JSON format:
{{
  "topic_domain": "specific_domain",
  "content_type": "optimal_content_type",
  "audience_level": "target_audience", 
  "optimal_length": "word_range",
  "writing_style": "best_style_approach",
  "key_elements": ["element1", "element2", "element3"],
  "unique_angle": "what_makes_this_valuable",
  "suggested_structure": ["section1", "section2", "section3"],
  "expertise_required": "level_of_expertise_needed"
}}
"""
        
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.3,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            content = response.content[0].text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "{" in content:
                content = content[content.find("{"):content.rfind("}")+1]
            
            return json.loads(content.strip())
            
        except Exception as e:
            print(f"Error analyzing request: {e}")
            return self._get_fallback_analysis()
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when LLM is unavailable"""
        return {
            "topic_domain": "general",
            "content_type": "informative_guide",
            "audience_level": "intermediate",
            "optimal_length": "2000-3500",
            "writing_style": "conversational",
            "key_elements": ["examples", "practical_tips", "clear_explanations"],
            "unique_angle": "comprehensive_practical_approach",
            "suggested_structure": ["introduction", "main_content", "conclusion"],
            "expertise_required": "intermediate"
        }
    
    async def generate_dynamic_template(
        self, 
        request: UniversalContentRequest,
        analysis: Dict[str, Any]
    ) -> str:
        """Generate a custom template for ANY topic based on analysis"""
        
        # Check if client is available
        if not self.anthropic_client:
            print("⚠️ Anthropic client not available, using fallback template")
            return self._get_universal_fallback_template()
        
        template_prompt = f"""
Create a dynamic YAML template that can generate excellent content for this specific request.

REQUEST: "{request.user_request}"
ANALYSIS: {json.dumps(analysis, indent=2)}

Generate a YAML template that:
1. Adapts to the specific topic domain and audience
2. Produces content of optimal length for the subject
3. Uses appropriate writing style and tone
4. Includes relevant elements and structure
5. Can generate genuinely useful, engaging content

Template Structure:
```yaml
id: dynamic_[topic]_generator
name: [Descriptive Name for this Content Type]
description: [What this template generates]
category: [topic_domain]
content_type: [from analysis]

# Length targeting based on topic complexity
length_optimization:
  target_words: "[word_range_from_analysis]"
  reading_time: "[estimated_reading_time]"
  depth: "[appropriate_depth_level]"

# Topic-specific system prompt
system_prompt: |
  [Create a system prompt that:
   - Understands the specific topic domain
   - Knows the target audience level
   - Can generate content in the appropriate style
   - Includes relevant examples and insights
   - Produces engaging, valuable content]

# Dynamic instructions for this topic
instructions: |
  [Specific instructions for generating great content in this domain:
   - Content structure appropriate for the topic
   - Key elements to include
   - How to make it engaging and useful
   - Specific considerations for this subject area]

# Smart parameters for this content type
parameters:
  - name: specific_focus
    type: text/select
    label: [Topic-specific focus parameter]
    description: [Relevant to this domain]
    commonly_used: false
    affects_scope: true
    
  - name: audience_expertise
    type: select
    label: Audience Level
    description: [Relevant expertise levels for this topic]
    commonly_used: false
    affects_approach: true
    options: [appropriate_expertise_levels]
    
  - name: content_angle
    type: select
    label: Content Approach
    description: [Different angles relevant to this topic]
    commonly_used: false
    affects_approach: true
    options: [topic_specific_angles]

# Metadata
metadata:
  topic_domain: "{analysis['topic_domain']}"
  content_type: "{analysis['content_type']}"
  target_length: "{analysis['optimal_length']}"
  adaptable: true
```

Generate ONLY the complete YAML template. Make it specific to the topic but flexible enough to handle variations within that domain.
"""
        
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                temperature=0.2,
                messages=[{"role": "user", "content": template_prompt}]
            )
            
            content = response.content[0].text
            if "```yaml" in content:
                content = content.split("```yaml")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return content.strip()
            
        except Exception as e:
            print(f"Error generating template: {e}")
            return self._get_universal_fallback_template()
    
    def _get_universal_fallback_template(self) -> str:
        """Universal fallback template when LLM is unavailable"""
        return """
id: universal_fallback
name: Universal Content Generator
description: Adaptable template for any content type
category: general

system_prompt: |
  You are an expert content creator who can write engaging, informative content on any topic.
  Adapt your writing style, depth, and approach to match the specific request and audience.
  
instructions: |
  Create comprehensive, well-structured content that:
  - Addresses the user's specific request
  - Uses appropriate tone and complexity for the audience
  - Includes relevant examples and practical insights
  - Follows a logical structure with clear sections
  - Provides genuine value to readers

parameters:
  - name: content_focus
    type: text
    label: Main Focus
    description: Primary aspect to emphasize

metadata:
  adaptable: true
  fallback: true
"""

class TrulyDynamicContentSystem:
    """Content system that adapts to literally any topic"""
    
    def __init__(self):
        self.generator = UniversalDynamicGenerator()
        self.template_cache = {}
    
    async def generate_content_approach(self, user_request: str) -> Dict[str, Any]:
        """Take ANY user request and generate the optimal content approach"""
        
        # Create request object
        request = UniversalContentRequest(user_request=user_request)
        
        # Analyze the request
        analysis = await self.generator.analyze_content_request(request)
        
        # Generate custom template
        template_yaml = await self.generator.generate_dynamic_template(request, analysis)
        
        return {
            "user_request": user_request,
            "content_analysis": analysis,
            "generated_template": template_yaml,
            "approach_summary": {
                "topic": analysis.get("topic_domain", "general"),
                "type": analysis.get("content_type", "guide"),
                "length": analysis.get("optimal_length", "2000-3500"),
                "style": analysis.get("writing_style", "conversational"),
                "audience": analysis.get("audience_level", "general")
            }
        }

# Run the test
if __name__ == "__main__":
    asyncio.run(
        TrulyDynamicContentSystem().generate_content_approach("")
    )