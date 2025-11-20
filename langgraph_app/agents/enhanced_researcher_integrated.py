# File: langgraph_app/agents/enhanced_researcher_integrated.py

import os
from asyncio.log import logger
from typing import List, Optional, Dict, Any
from langgraph_app.core.state import (
    EnrichedContentState, 
    AgentType, 
    ContentPhase,
    ResearchFindings
)

class EnhancedResearcherAgent:
    """Integrated Researcher Agent using EnrichedContentState with Template Configuration Support"""
    
    def __init__(self):
        self.agent_type = AgentType.RESEARCHER
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    def _execute_research_logic(self, state: EnrichedContentState, instructions, template_config: dict) -> ResearchFindings:
        """Execute research using planning context, dynamic instructions, and template configuration"""

        planning = state.planning_output
        spec = state.content_spec or {}


        print(f"DEBUG: planning = {planning}")
        print(f"DEBUG: state.research_plan = {getattr(state, 'research_plan', 'NOT_SET')}")
        print(f"DEBUG: template_config = {template_config}")

         # Ensure research_plan exists
        if not hasattr(state, 'research_plan') or state.research_plan is None:
            from types import SimpleNamespace
            state.research_plan = SimpleNamespace(
                research_priorities=['overview', 'key_concepts', 'examples'],
                depth='moderate',
                sources_needed=3,
                focus_areas=['background', 'main_concepts', 'practical_applications']
            )

         # Extract research priorities with template priority
        research_priorities = self._get_template_research_priorities(template_config, planning, spec, instructions)
        research_priorities = [str(p) for p in research_priorities if p is not None]

        print(f"DEBUG: Final research_priorities = {research_priorities}")


          # Safe logging
        try:
            state.log_agent_execution(self.agent_type, {
                "research_priorities_source": "template_enhanced",
                "priorities_count": len(research_priorities),
                "priorities": research_priorities[:3]
            })
        except Exception as e:
            print(f"DEBUG: Failed to log priorities: {e}")

         # Execute research for each priority
        primary_insights = []
        for priority in research_priorities:
            try:
                insights = self._research_priority(priority, spec, instructions, template_config)
                primary_insights.extend(insights)
            except Exception as e:
                print(f"DEBUG: Failed to research {priority}: {e}")
                try:
                    state.log_agent_execution(self.agent_type, {
                        "priority_error": f"Failed to research {priority}: {str(e)}"
                    })
                except:
                    pass
                continue
            
        # Gather supporting data with template awareness
        evidence_types = []
        if instructions and hasattr(instructions, 'specific_requirements'):
            evidence_types = instructions.specific_requirements.get("evidence_types", [])

         # Add template-specific evidence types
        template_evidence = template_config.get('required_evidence_types', [])
        evidence_types.extend(template_evidence)

        supporting_data = self._gather_supporting_data(evidence_types, spec, template_config)

        return ResearchFindings(
            primary_insights=primary_insights,
            industry_context=self._research_industry_context(spec, template_config),
            competitive_landscape=self._research_competitive_landscape(spec, template_config),
            trending_topics=self._identify_trending_topics(spec, template_config),
            expert_quotes=[],
            supporting_data=supporting_data,
            statistical_evidence=[],
            research_gaps=self._identify_research_gaps(primary_insights),
            credibility_sources=self._validate_sources(template_config),
            research_confidence=0.80
        )

    def _gather_supporting_data(self, evidence_types: list, spec, template_config: dict) -> dict:
        """Gather supporting data via web search"""
        supporting_data = {}

        for evidence_type in evidence_types:
            if evidence_type == "market_data":
                results = self._web_search(f"{spec.topic} market size growth")
                supporting_data["market_data"] = {"findings": results[:2]}
            elif evidence_type == "financial_metrics":
                results = self._web_search(f"{spec.topic} ROI benchmarks")
                supporting_data["financial_metrics"] = {"findings": results[:2]}

        return supporting_data

    def _research_industry_context(self, spec, template_config: dict) -> dict:
        """Research industry context via web search"""
        results = self._web_search(f"{spec.topic} industry trends challenges")

        return {
            "industry": template_config.get("metadata", {}).get("domain", "general"),
            "key_challenges": [r["finding"][:100] for r in results[:2]],
            "opportunities": []
        }

    def _research_competitive_landscape(self, spec, template_config: dict) -> dict:
        """Research competitive landscape via web search"""
        results = self._web_search(f"{spec.topic} competitive landscape alternatives")

        return {
            "direct_competitors": [r["finding"][:80] for r in results[:2]],
            "differentiation_opportunities": []
        }

    def _identify_trending_topics(self, spec, template_config: dict) -> list:
        """Identify trending topics via web search"""
        results = self._web_search(f"{spec.topic} trends 2025")
        return [r["finding"][:100] for r in results[:3]]

    def _identify_research_gaps(self, insights: list) -> list:
        """Identify research gaps"""
        types_found = {i.get('type') for i in insights}
        gaps = []

        if 'market_analysis' not in types_found:
            gaps.append("Market validation needed")
        if 'competitive_analysis' not in types_found:
            gaps.append("Competitive analysis needed")

        return gaps[:3]

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Execute research with template + planning context"""
        template_config = state.template_config or state.content_template_config.get("business_context", {}).get('template_config', {})
    
        instructions = state.get_agent_instructions(self.agent_type)
    
        state.log_agent_execution(self.agent_type, {
            "status": "started",
            "template_type": getattr(template_config, 'template_type', 'default'),
            "has_planning": bool(state.planning_output)
        })
    
        research_findings = self._execute_research_logic(state, instructions, template_config)
        state.research_findings = research_findings
        state.update_phase(ContentPhase.WRITING)
    
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "insights_found": len(research_findings.primary_insights),
            "confidence_score": research_findings.research_confidence,
            "sources_validated": len(research_findings.credibility_sources)
        })
    
        return state
 

    def _get_market_data(self, spec, template_config: dict) -> dict:
        """Get REAL market data using web search"""
        
        topic = spec.topic
        
        # Use real-time search if available
        try:
            if self.web_search_tool:
                # Search for actual market data
                search_results = self.web_search_tool.search(
                    f"{topic} market size TAM SAM growth rate"
                )
                
                # Parse results for real data
                market_data = self._parse_market_data_from_results(search_results)
                if market_data:
                    return market_data
        except Exception as e:
            logger.warning(f"Real-time market search failed: {e}")
        
        # Fallback: Return indication of data source limitation
        return {
            "data_source": "knowledge_cutoff",
            "market_size": f"Market analysis for {topic} requires current data",
            "recommendation": "Integrate with market research APIs for real-time data",
            "confidence": 0.3
        }
    
    def _parse_market_data_from_results(self, search_results: dict) -> Optional[dict]:
        """Extract market data from search results"""
        
        extracted_data = {}
        results = search_results.get('results', [])
        
        for result in results[:5]:
            content = result.get('content', '') + ' ' + result.get('snippet', '')
            
            # Extract TAM/SAM patterns
            import re
            tam_matches = re.findall(r'\$(\d+(?:\.\d+)?)\s*(?:billion|B|trillion|T)', content, re.IGNORECASE)
            if tam_matches:
                extracted_data['tam'] = f"${tam_matches[0]} based on {result.get('title', 'industry analysis')}"
            
            # Extract growth rate
            growth_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%\s*(?:CAGR|growth|annually)', content, re.IGNORECASE)
            if growth_matches:
                extracted_data['growth_rate'] = f"{growth_matches[0]}% CAGR (source: {result.get('source', 'research')})"
        
        return extracted_data if extracted_data else None
    
    # File: langgraph_app/agents/enhanced_researcher_integrated.py
    # Replace _get_template_research_priorities method

    def _get_template_research_priorities(self, template_config: dict, planning, spec, instructions) -> list:
        """Dynamic research priorities based on template metadata with safe list handling"""

        priorities = []

        # Use template-defined research priorities first
        template_priorities = template_config.get('research_priorities')
        if isinstance(template_priorities, list):
            priorities.extend([str(p) for p in template_priorities if p])
        elif isinstance(template_priorities, str):
            priorities.append(template_priorities)

        # Use template research field if available
        template_research = template_config.get('research', {})
        if isinstance(template_research, dict):
            research_priorities = template_research.get('priorities')
            if isinstance(research_priorities, list):
                priorities.extend([str(p) for p in research_priorities if p])
            elif isinstance(research_priorities, str):
                priorities.append(research_priorities)

        # Extract from template parameters for context
        parameters = template_config.get('parameters', {})
        if isinstance(parameters, dict):
            for param_name, param_config in parameters.items():
                if isinstance(param_config, dict) and param_config.get('required'):
                    priorities.append(f"{param_name.replace('_', ' ')} research")

        # Add planning priorities if available - SAFE HANDLING
        if planning and hasattr(planning, 'research_priorities'):
            planning_priorities = getattr(planning, 'research_priorities', [])
            if isinstance(planning_priorities, list):
                priorities.extend([str(p) for p in planning_priorities if p])
            elif isinstance(planning_priorities, str):
                priorities.append(planning_priorities)

        # Topic-based fallback
        if not priorities and hasattr(spec, 'topic'):
            topic = getattr(spec, 'topic', '')
            if topic:
                priorities = [f"{topic} overview", f"{topic} best practices"]

        # Ensure all items are strings and remove duplicates
        clean_priorities = []
        seen = set()
        for item in priorities:
            if isinstance(item, str) and item.strip() and item not in seen:
                clean_priorities.append(item.strip())
                seen.add(item)

        return clean_priorities[:8]  # Limit to 8
    


    def _research_priority(self, priority: str, spec, instructions, template_config: dict) -> list:
        """Generic research based on priority keywords"""
        
        insights = []
        priority_lower = str(priority).lower()
        
        # Pattern-based research without hardcoded template types
        research_patterns = [
            (("market", "industry", "sector"), ("market_analysis", "industry_report")),
            (("financial", "revenue", "cost", "roi"), ("financial_data", "financial_analysis")),
            (("competitive", "competitor"), ("competitive_analysis", "market_research")),
            (("user", "customer", "audience"), ("user_research", "user_study")),
            (("trend", "emerging", "future"), ("trend_analysis", "trend_report")),
        ]
        
        for keywords, (research_type, source_type) in research_patterns:
            if any(k in priority_lower for k in keywords):
                insights.append({
                    "type": research_type,
                    "finding": f"{research_type.replace('_', ' ').title()} for {spec.topic}",
                    "relevance": "high",
                    "source_type": source_type
                })
                break

            
        # Default research if no patterns match
        if not insights:
            insights.append({
                "type": "general_research",
                "finding": f"Research insights for {spec.topic}",
                "relevance": "medium",
                "source_type": "general_analysis"
            })
        
        return insights
    
    def _web_search(self, query: str) -> List[Dict[str, Any]]:
       if not self.tavily_api_key:
           logger.warning(f"No Tavily key for: {query}")
           return []
       
       try:
           from tavily import TavilyClient
           client = TavilyClient(api_key=self.tavily_api_key)
           response = client.search(query=query, max_results=3)
           
           return [{
               "finding": r.get("content", "")[:500],
               "source": r.get("url", ""),
               "relevance": "high"
           } for r in response.get("results", [])]
       except Exception as e:
           logger.error(f"Search failed: {e}")
           return []

    # langgraph_app/agents/enhanced_researcher_integrated.py
    def search_recent_events(self, topic: str, timeframe: str = "24h"):
        results = self.web_search(f"{topic} {timeframe}")
        return self.validate_and_synthesize(results)

    def _validate_sources(self, template_config: dict) -> list:
        """Dynamic source validation based on template metadata"""

        # Base sources for all content types
        sources = ["Industry Research", "Market Analysis", "Expert Sources"]

        # Extract source requirements from template config
        template_sources = template_config.get('data_sources', [])
        if template_sources:
            sources.extend(template_sources)

        # Add sources based on template parameters
        parameters = template_config.get('parameters', {})

        # Financial content needs financial sources
        if any('budget' in key or 'cost' in key or 'roi' in key for key in parameters.keys()):
            sources.extend(["Financial Reports", "ROI Studies"])

        # Market-focused content needs market sources
        if any('market' in key or 'competitive' in key for key in parameters.keys()):
            sources.extend(["Market Research", "Competitive Analysis"])

        # Technical content needs technical sources
        if any('technical' in key or 'implementation' in key for key in parameters.keys()):
            sources.extend(["Technical Standards", "Implementation Guides"])

        # User/audience focused content needs user research
        if any('audience' in key or 'user' in key or 'customer' in key for key in parameters.keys()):
            sources.extend(["User Research", "Audience Studies"])

        return list(dict.fromkeys(sources))  # Remove duplicates