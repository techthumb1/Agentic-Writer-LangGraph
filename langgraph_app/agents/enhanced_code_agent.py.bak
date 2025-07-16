# File: langgraph_app/agents/enhanced_code_agent.py
import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

class IntelligentCodeAgent:
    """
    Advanced code generation agent that creates contextually appropriate code examples
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.code_templates = {
            "tutorial": "Step-by-step implementation with detailed comments",
            "example": "Clean, production-ready example with best practices",
            "demo": "Simple demonstration focusing on core concepts",
            "advanced": "Complex implementation showing advanced patterns",
            "comparative": "Multiple approaches showing different solutions"
        }
    
    def determine_code_style(self, context: Dict) -> str:
        """Determine appropriate code style based on context"""
        
        content_plan = context.get("content_plan", {})
        intent = content_plan.get("intent", "inform")
        complexity = content_plan.get("complexity_level", 5)
        audience = content_plan.get("audience", "").lower()
        
        if intent == "teach" or "beginner" in audience:
            return "tutorial"
        elif complexity >= 8 or "expert" in audience:
            return "advanced"
        elif "comparison" in str(context.get("topic", "")).lower():
            return "comparative"
        elif intent == "demonstrate":
            return "demo"
        else:
            return "example"
    
    def generate_intelligent_code(self, state: Dict) -> Dict:
        """Generate contextually appropriate code examples"""
        
        # Check if code is needed
        agent_requirements = state.get("agent_requirements", {})
        if not agent_requirements.get("code_needed", False):
            return {"code_block": ""}
        
        content_plan = state.get("content_plan", {})
        topic = content_plan.get("topic", state.get("topic", ""))
        audience = content_plan.get("audience", state.get("audience", ""))
        complexity = content_plan.get("complexity_level", 5)
        
        # Determine code style and language
        code_style = self.determine_code_style(state)
        language = self._detect_programming_language(topic, state)
        
        # Create enhanced code prompt
        code_prompt = self._create_code_prompt(topic, audience, complexity, code_style, language)
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self._get_code_system_prompt(code_style, language)},
                {"role": "user", "content": code_prompt}
            ],
            temperature=0.2,  # Low temperature for consistent code
        )
        
        code_content = response.choices[0].message.content.strip()
        
        return {
            "code_block": code_content,
            "code_metadata": {
                "language": language,
                "style": code_style,
                "complexity_level": complexity,
                "lines_of_code": len([line for line in code_content.split('\n') if line.strip()]),
                "includes_comments": "comment" in code_style.lower()
            }
        }
    
    def _detect_programming_language(self, topic: str, state: Dict) -> str:
        """Intelligently detect appropriate programming language"""
        
        topic_lower = topic.lower()
        params = state.get("dynamic_parameters", {})
        
        # Explicit language specification
        if params.get("language"):
            return params["language"]
        
        # Language detection from topic
        if any(word in topic_lower for word in ["python", "django", "flask", "pandas", "numpy"]):
            return "python"
        elif any(word in topic_lower for word in ["javascript", "js", "node", "react", "vue"]):
            return "javascript"
        elif any(word in topic_lower for word in ["java", "spring", "android"]):
            return "java"
        elif any(word in topic_lower for word in ["c++", "cpp", "c programming"]):
            return "cpp"
        elif any(word in topic_lower for word in ["rust", "cargo"]):
            return "rust"
        elif any(word in topic_lower for word in ["go", "golang"]):
            return "go"
        elif any(word in topic_lower for word in ["typescript", "ts"]):
            return "typescript"
        else:
            return "python"  # Default to Python
    
    def _create_code_prompt(self, topic: str, audience: str, complexity: int, style: str, language: str) -> str:
        """Create detailed code generation prompt"""
        
        style_instruction = self.code_templates.get(style, "Clean, readable code example")
        
        return f"""
Topic: {topic}
Audience: {audience}
Complexity Level: {complexity}/10
Programming Language: {language}
Code Style: {style_instruction}

Create a {language} code example that:
1. Directly relates to and supports the topic
2. Is appropriate for the target audience skill level
3. Follows {language} best practices and conventions
4. Includes helpful comments explaining key concepts
5. Is complete and runnable (when possible)
6. Demonstrates the main concepts clearly

Additional requirements based on complexity level:
{self._get_complexity_requirements(complexity)}
"""
    
    def _get_complexity_requirements(self, complexity: int) -> str:
        """Get additional requirements based on complexity"""
        if complexity <= 3:
            return "- Keep it simple with basic concepts only\n- Use clear variable names\n- Include extensive comments"
        elif complexity >= 7:
            return "- Show advanced patterns and optimizations\n- Include error handling\n- Demonstrate best practices\n- Consider performance implications"
        else:
            return "- Balance simplicity with real-world applicability\n- Include moderate error handling\n- Show common patterns"
    
    def _get_code_system_prompt(self, style: str, language: str) -> str:
        """Get system prompt for code generation"""
        return f"""You are an expert {language} developer and educator. Your code examples are:
- Clean, readable, and well-structured
- Following {language} best practices and conventions
- Appropriately commented to aid understanding
- Practical and applicable to real-world scenarios
- Focused on teaching concepts effectively

Style focus: {style}
Always include brief explanations of key concepts used in the code."""


# File: langgraph_app/agents/enhanced_editor.py
import os
from typing import Dict, List
from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

class IntelligentEditorAgent:
    """
    Advanced editor that adapts editing strategy based on content type and quality requirements
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.editing_strategies = {
            "technical_precision": "Focus on technical accuracy, clarity of complex concepts, and logical flow",
            "creative_enhancement": "Enhance storytelling, emotional connection, and narrative flow",
            "professional_polish": "Ensure professional tone, formal structure, and business-appropriate language",
            "educational_clarity": "Optimize for learning, clear explanations, and progressive difficulty",
            "conversational_warmth": "Maintain casual tone while improving clarity and engagement"
        }
    
    def determine_editing_strategy(self, state: Dict) -> str:
        """Determine editing strategy based on content characteristics"""
        
        content_plan = state.get("content_plan", {})
        intent = content_plan.get("intent", "inform")
        complexity = content_plan.get("complexity_level", 5)
        platform = content_plan.get("platform", "blog")
        tone_adaptations = content_plan.get("tone_adaptations", {})
        
        # Strategy selection logic
        if complexity >= 7:
            return "technical_precision"
        elif intent == "teach":
            return "educational_clarity"
        elif intent in ["inspire", "entertain"]:
            return "creative_enhancement"
        elif platform in ["linkedin", "medium"] or tone_adaptations.get("professional", 0) > 0.5:
            return "professional_polish"
        else:
            return "conversational_warmth"
    
    def create_editing_prompt(self, draft: str, strategy: str, state: Dict) -> str:
        """Create comprehensive editing prompt"""
        
        content_plan = state.get("content_plan", {})
        success_criteria = content_plan.get("success_criteria", [])
        
        strategy_instruction = self.editing_strategies.get(strategy, "General editing for clarity and flow")
        
        return f"""
DRAFT TO EDIT:
{draft}

EDITING STRATEGY: {strategy_instruction}

CONTENT CONTEXT:
- Target Audience: {content_plan.get('audience', 'General')}
- Platform: {content_plan.get('platform', 'blog')}
- Intent: {content_plan.get('intent', 'inform')}
- Complexity Level: {content_plan.get('complexity_level', 5)}/10

SUCCESS CRITERIA TO OPTIMIZE FOR:
{chr(10).join(f"- {criterion.replace('_', ' ').title()}" for criterion in success_criteria)}

EDITING TASKS:
1. Improve clarity and readability without losing meaning
2. Enhance flow and logical progression
3. Optimize for the target audience and platform
4. Ensure consistency in tone and style
5. Fix any grammatical or structural issues
6. Maintain the original innovative elements and insights

Please provide the edited version that maximizes impact while preserving the author's voice and innovative insights.
"""
    
    def intelligent_edit(self, state: Dict) -> Dict:
        """Main editing function with adaptive strategy"""
        
        draft = state.get("draft", "")
        if not draft:
            return {"edited_draft": "No draft provided for editing."}
        
        # Determine editing strategy
        strategy = self.determine_editing_strategy(state)
        
        # Create editing prompt
        editing_prompt = self.create_editing_prompt(draft, strategy, state)
        
        # Get system prompt
        system_prompt = self._get_editing_system_prompt(strategy, state)
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": editing_prompt},
            ],
            temperature=0.3,  # Lower temperature for consistent editing
        )
        
        edited_content = response.choices[0].message.content.strip()
        
        return {
            "edited_draft": edited_content,
            "editing_metadata": {
                "strategy_used": strategy,
                "original_length": len(draft.split()),
                "edited_length": len(edited_content.split()),
                "length_change_percent": round(((len(edited_content.split()) - len(draft.split())) / len(draft.split())) * 100, 1) if draft else 0,
                "editing_focus": strategy.replace('_', ' ').title()
            }
        }
    
    def _get_editing_system_prompt(self, strategy: str, state: Dict) -> str:
        """Get specialized system prompt based on editing strategy"""
        
        base_prompt = "You are an expert editor who improves content while preserving the author's voice and key insights."
        
        strategy_prompts = {
            "technical_precision": base_prompt + " Focus on technical accuracy, clear explanations of complex concepts, and logical flow. Ensure terminology is used correctly and consistently.",
            "creative_enhancement": base_prompt + " Enhance storytelling elements, emotional resonance, and narrative flow. Improve metaphors, analogies, and creative expressions while maintaining authenticity.",
            "professional_polish": base_prompt + " Ensure professional tone, formal structure, and business-appropriate language. Optimize for executive readability and professional impact.",
            "educational_clarity": base_prompt + " Optimize for learning outcomes. Ensure concepts build logically, use clear examples, and maintain appropriate difficulty progression.",
            "conversational_warmth": base_prompt + " Maintain casual, approachable tone while improving clarity. Keep the human connection while enhancing readability."
        }
        
        return strategy_prompts.get(strategy, base_prompt)

# enhanced_code_agent.py - Add to the very end:
from langchain_core.runnables import RunnableLambda

async def _enhanced_code_agent_fn(state: dict) -> dict:
    """Enhanced code agent function for LangGraph workflow"""
    code_agent = IntelligentCodeAgent()  # Adjust class name as needed
    return await code_agent.intelligent_code_generation(state)  # Adjust method name as needed

# Export the function
code_agent = RunnableLambda(_enhanced_code_agent_fn)
