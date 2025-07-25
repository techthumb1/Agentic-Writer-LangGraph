# File: langgraph_app/agents/enhanced_editor.py
# Enhanced Editor Agent with Export Function Fix

import os
import asyncio
from typing import Dict, List
from openai import OpenAI, AsyncOpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

class IntelligentEditorAgent:
    """
    Advanced editor that adapts editing strategy based on content type and quality requirements
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.async_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
    
    async def intelligent_edit(self, state: Dict) -> Dict:
        """Main editing function with adaptive strategy"""
        
        draft = state.get("draft", "")
        if not draft:
            # No draft provided, return an appropriate error or message
            return {**state, "edited_draft": "No draft provided for editing."}
        
        # Determine editing strategy
        strategy = self.determine_editing_strategy(state)
        
        # Create editing prompt
        editing_prompt = self.create_editing_prompt(draft, strategy, state)
        
        # Get system prompt
        system_prompt = self._get_editing_system_prompt(strategy, state)
        
        response = await self.async_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": editing_prompt},
            ],
            temperature=0.3,  # Lower temperature for consistent editing
        )
        
        edited_content = response.choices[0].message.content.strip()
        
        return {**state, 
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

    # Synchronous wrapper for backward compatibility
    def intelligent_edit_sync(self, state: Dict) -> Dict:
        """Synchronous wrapper for intelligent editing"""
        try:
            # Run async method in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.intelligent_edit(state))
            loop.close()
            return result
        except Exception as e:
            return {**state, "edited_draft": f"Editing failed: {str(e)}"}

# LangGraph integration functions
async def _enhanced_editor_async_fn(state: dict) -> dict:
    """Enhanced editor agent function for LangGraph workflow - async version"""
    editor_agent = IntelligentEditorAgent()
    return await editor_agent.intelligent_edit(state)

def _enhanced_editor_sync_fn(state: dict) -> dict:
    """Enhanced editor agent function for LangGraph workflow - sync version"""
    editor_agent = IntelligentEditorAgent()
    return editor_agent.intelligent_edit_sync(state)

# ✅ FIXED: Export functions for orchestration
enhanced_editor_agent = RunnableLambda(_enhanced_editor_async_fn)
enhanced_editor_agent_sync = RunnableLambda(_enhanced_editor_sync_fn)

# Create instance for direct use
intelligent_editor_agent = IntelligentEditorAgent()

# Backward compatibility exports
EditorAgent = IntelligentEditorAgent
editor = RunnableLambda(_enhanced_editor_sync_fn)