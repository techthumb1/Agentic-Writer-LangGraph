# File: langgraph_app/agents/enhanced_researcher.py
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from openai import OpenAI, AsyncOpenAI  # ADD AsyncOpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ResearchContext:
    topic: str
    complexity_level: int
    intent: str
    audience: str
    research_depth: str = "moderate"

class IntelligentResearcherAgent:
    """
    Advanced researcher that adapts research strategy based on content needs
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.async_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # ADD THIS
        self.research_cache = {}
        self.research_strategies = {
            "factual": "Focus on verified facts, statistics, and authoritative sources",
            "trend_analysis": "Research current trends, market data, and recent developments",
            "technical_deep_dive": "Gather technical specifications, implementation details, and expert insights", 
            "comparative": "Compare different approaches, tools, or methodologies",
            "case_study": "Find real-world examples, success stories, and practical applications",
            "future_oriented": "Research emerging trends, predictions, and future implications"
        }
    
    def determine_research_strategy(self, context: ResearchContext) -> str:
        """Intelligently determine research strategy based on context"""
        
        topic_lower = context.topic.lower()
        
        # Technical content needs deep technical research
        if context.complexity_level >= 7 or any(word in topic_lower for word in 
                                               ["algorithm", "architecture", "implementation"]):
            return "technical_deep_dive"
            
        # Trend-based topics
        if any(word in topic_lower for word in ["trends", "2024", "2025", "future", "emerging"]):
            return "trend_analysis"
            
        # Comparative topics
        if any(word in topic_lower for word in ["vs", "comparison", "best", "top", "alternatives"]):
            return "comparative"
            
        # Case study topics
        if any(word in topic_lower for word in ["how", "case study", "example", "success"]):
            return "case_study"
            
        # Future-oriented
        if any(word in topic_lower for word in ["future", "prediction", "next", "coming"]):
            return "future_oriented"
            
        return "factual"
    
    def generate_research_queries(self, context: ResearchContext, strategy: str) -> List[str]:
        """Generate targeted research queries based on strategy"""
        
        base_queries = [
            f"latest research on {context.topic}",
            f"{context.topic} best practices",
            f"{context.topic} expert insights"
        ]
        
        strategy_queries = {
            "technical_deep_dive": [
                f"{context.topic} technical specifications",
                f"{context.topic} implementation challenges",
                f"{context.topic} performance benchmarks"
            ],
            "trend_analysis": [
                f"{context.topic} trends 2024 2025",
                f"{context.topic} market analysis",
                f"future of {context.topic}"
            ],
            "comparative": [
                f"{context.topic} comparison alternatives",
                f"pros and cons of {context.topic}",
                f"{context.topic} vs competitors"
            ],
            "case_study": [
                f"{context.topic} success stories",
                f"{context.topic} real world examples",
                f"companies using {context.topic}"
            ]
        }
        
        return base_queries + strategy_queries.get(strategy, [])
    
    async def conduct_intelligent_research(self, state: Dict) -> Dict:  # MAKE ASYNC
        """Main research function with adaptive intelligence"""
        
        # Extract context from enhanced state
        content_plan = state.get("content_plan", {})
        
        context = ResearchContext(
            topic=content_plan.get("topic", state.get("topic", "Unknown")),
            complexity_level=content_plan.get("complexity_level", 5),
            intent=content_plan.get("intent", "inform"),
            audience=content_plan.get("audience", state.get("audience", "General")),
            research_depth=state.get("research_depth", "moderate")
        )
        
        # Check if research is actually needed
        agent_requirements = state.get("agent_requirements", {})
        if not agent_requirements.get("research_needed", True):
            return {"research": "Research not required for this content type."}
        
        # Determine research strategy
        strategy = self.determine_research_strategy(context)
        
        # Generate research prompt
        research_prompt = self._create_research_prompt(context, strategy)
        
        # Conduct research with appropriate model temperature
        temperature = 0.3 if strategy == "technical_deep_dive" else 0.4
        
        response = await self.async_client.chat.completions.create(  # MAKE ASYNC
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self._get_research_system_prompt(strategy)},
                {"role": "user", "content": research_prompt}
            ],
            temperature=temperature,
        )
        
        research_content = response.choices[0].message.content.strip()
        
        # Enhanced research output with metadata
        return {
            "research": research_content,
            "research_metadata": {
                "strategy_used": strategy,
                "research_depth": context.research_depth,
                "complexity_level": context.complexity_level,
                "research_timestamp": datetime.now().isoformat(),
                "word_count": len(research_content.split())
            }
        }
    
    def _create_research_prompt(self, context: ResearchContext, strategy: str) -> str:
        """Create tailored research prompt"""
        
        strategy_instruction = self.research_strategies.get(strategy, "Conduct general research")
        
        depth_instructions = {
            "shallow": "Provide 3-5 key points with basic context",
            "moderate": "Provide comprehensive overview with 5-8 key insights and supporting details",
            "deep": "Provide exhaustive research with detailed analysis, multiple perspectives, and actionable insights"
        }
        
        depth_instruction = depth_instructions.get(context.research_depth, depth_instructions["moderate"])
        
        return f"""
Research Topic: {context.topic}
Target Audience: {context.audience}
Content Intent: {context.intent}
Complexity Level: {context.complexity_level}/10

Research Strategy: {strategy_instruction}
Depth Requirement: {depth_instruction}

Please provide research that includes:
1. Key facts and recent developments
2. Relevant statistics and data points
3. Expert opinions and insights
4. Practical applications and examples
5. Reputable sources and references

Focus on information that would be valuable for creating {context.intent}-focused content for {context.audience}.
"""
    
    def _get_research_system_prompt(self, strategy: str) -> str:
        """Get system prompt based on research strategy"""
        
        base_prompt = """You are an expert research analyst who gathers high-quality, accurate information for content creation."""
        
        strategy_prompts = {
            "technical_deep_dive": base_prompt + " Focus on technical accuracy, implementation details, and expert-level insights. Prioritize authoritative technical sources.",
            "trend_analysis": base_prompt + " Focus on current trends, market data, and emerging developments. Use recent data and forward-looking insights.",
            "comparative": base_prompt + " Focus on objective comparisons, pros/cons analysis, and clear differentiation between options.",
            "case_study": base_prompt + " Focus on real-world examples, success stories, and practical applications with concrete outcomes.",
            "future_oriented": base_prompt + " Focus on emerging trends, expert predictions, and potential future developments based on current trajectories."
        }
        
        return strategy_prompts.get(strategy, base_prompt)
    
    # enhanced_researcher.py - Add to the very end:
from langchain_core.runnables import RunnableLambda

async def _enhanced_researcher_fn(state: dict) -> dict:
    """Enhanced researcher agent function for LangGraph workflow"""
    researcher_agent = IntelligentResearcherAgent()
    return await researcher_agent.conduct_intelligent_research(state)

# Export the function
researcher = RunnableLambda(_enhanced_researcher_fn)

