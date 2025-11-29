# langgraph_app/agents/realtime_search.py
# Real-time search methods for writer agent - enterprise fail-fast approach
# NO FALLBACKS: If real-time data required but unavailable, fail immediately
# RELEVANT FILES: writer.py, enhanced_researcher_integrated.py, mcp_enhanced_graph.py

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class RealTimeSearchMixin:
    """Mixin class providing real-time search capabilities for writer agent"""
    
    async def _fetch_recent_events(
        self, 
        topic: str, 
        timeframe: str = "24h", 
        min_sources: int = 1,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Fetch recent events - ENTERPRISE: NO FALLBACKS
        
        Args:
            topic: Main topic for search
            timeframe: Search timeframe (e.g., "24h", "7d")
            min_sources: Minimum number of sources required
            parameters: Additional search context from template parameters
            
        Returns:
            Dictionary with recent events and metadata
            
        Raises:
            RuntimeError: If search capability unavailable
        """
        
        # ENTERPRISE: Validate search capability exists
        if not (self.researcher_agent or self.web_search_tool):
            raise RuntimeError("ENTERPRISE: Real-time search required but no search capability available")
        
        # Build search queries based on template parameters
        search_queries = self._build_search_queries(topic, parameters, timeframe)
        
        recent_data = {
            'events': [],
            'sources': [],
            'search_timestamp': datetime.utcnow().isoformat(),
            'queries_used': search_queries,
            'timeframe': timeframe
        }
        
        successful_searches = 0
        
        for query in search_queries:
            try:
                # ENTERPRISE: Use researcher agent if available, otherwise web search
                if self.researcher_agent and hasattr(self.researcher_agent, 'search_recent_events'):
                    events = await self.researcher_agent.search_recent_events(query, timeframe)
                elif self.web_search_tool:
                    events = await self._direct_web_search(query, timeframe)
                else:
                    raise RuntimeError("ENTERPRISE: No search method available")
                
                if events and events.get('results'):
                    recent_data['events'].extend(events['results'])
                    recent_data['sources'].extend(events.get('sources', []))
                    successful_searches += 1
                    
            except Exception as e:
                logger.error(f"ENTERPRISE: Search failed for query '{query}': {str(e)}")
                # Continue with other queries but log failure
        
        # ENTERPRISE: Validate minimum requirements met
        unique_sources = len(set(recent_data['sources']))
        if unique_sources < min_sources:
            raise RuntimeError(f"ENTERPRISE: Only {unique_sources} sources found, minimum {min_sources} required")
        
        if successful_searches == 0:
            raise RuntimeError("ENTERPRISE: All search queries failed")
            
        # Sort events by recency and relevance
        recent_data['events'] = self._rank_and_filter_events(recent_data['events'])
        
        logger.info(f"Successfully fetched {len(recent_data['events'])} recent events from {unique_sources} sources")
        return recent_data
    
    def _build_search_queries(self, topic: str, parameters: Dict[str, Any], timeframe: str) -> List[str]:
        """Build targeted search queries based on template parameters"""
        
        if not topic or not topic.strip():
            raise ValueError("ENTERPRISE: Topic required for search query building")
        
        base_queries = [f"{topic} {timeframe}"]
        
        # Add parameter-specific search terms
        if parameters:
            # Product launch specific
            if parameters.get('announcement_type') == 'product_launch':
                company = parameters.get('company_name', topic)
                base_queries.extend([
                    f"{topic} product launch {timeframe}",
                    f"{company} new product {timeframe}"
                ])
            
            # News/incident specific  
            if parameters.get('content_type') in ['news', 'breaking_news', 'incident_report']:
                base_queries.extend([
                    f"{topic} breaking news {timeframe}",
                    f"{topic} latest developments {timeframe}"
                ])
            
            # Market analysis specific
            if parameters.get('analysis_type') == 'market_analysis':
                base_queries.extend([
                    f"{topic} market news {timeframe}",
                    f"{topic} stock price {timeframe}"
                ])
        
        # ENTERPRISE: Ensure we have valid queries
        valid_queries = [q for q in base_queries if q and q.strip()][:3]  # Limit to 3 queries
        
        if not valid_queries:
            raise ValueError("ENTERPRISE: No valid search queries generated")
        
        return valid_queries
    
    async def _direct_web_search(self, query: str, timeframe: str) -> Dict[str, Any]:
        """Direct web search - ENTERPRISE: NO FALLBACKS"""
        
        if not self.web_search_tool:
            raise RuntimeError("ENTERPRISE: Web search tool required but unavailable")
        
        # Add time constraint to search
        time_constrained_query = f"{query} after:{self._get_after_date(timeframe)}"
        
        search_results = await self.web_search_tool.search(time_constrained_query)
        
        if not search_results:
            raise RuntimeError(f"ENTERPRISE: Web search returned no results for query: {query}")
        
        return {
            'results': search_results.get('results', []),
            'sources': [result.get('url') for result in search_results.get('results', []) if result.get('url')],
            'query': time_constrained_query
        }
    
    def _get_after_date(self, timeframe: str) -> str:
        """Convert timeframe to date string for search constraints"""
        
        hours = 24  # Default
        
        if timeframe.endswith('h'):
            try:
                hours = int(timeframe[:-1])
            except ValueError:
                raise ValueError(f"ENTERPRISE: Invalid timeframe format: {timeframe}")
        elif timeframe.endswith('d'):
            try:
                hours = int(timeframe[:-1]) * 24
            except ValueError:
                raise ValueError(f"ENTERPRISE: Invalid timeframe format: {timeframe}")
        
        after_date = datetime.utcnow() - timedelta(hours=hours)
        return after_date.strftime('%Y-%m-%d')
    
    def _rank_and_filter_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank and filter events by recency and relevance"""
        
        if not events:
            return []
        
        # Remove duplicates based on title/URL
        seen = set()
        unique_events = []
        
        for event in events:
            if not isinstance(event, dict):
                continue
                
            identifier = event.get('title', '') + event.get('url', '')
            if identifier and identifier not in seen:
                seen.add(identifier)
                unique_events.append(event)
        
        # Sort by timestamp if available
        def sort_key(event):
            timestamp = event.get('timestamp', event.get('published_date', ''))
            if timestamp:
                try:
                    # Handle various timestamp formats
                    if isinstance(timestamp, str):
                        return timestamp
                    return str(timestamp)
                except:
                    pass
            return ''
        
        try:
            unique_events.sort(key=sort_key, reverse=True)
        except Exception as e:
            logger.warning(f"Event sorting failed: {e}")
            # Keep original order if sorting fails
        
        # Return top 10 most recent/relevant
        return unique_events[:10]

    def _summarize_events(self, events: List[Dict[str, Any]]) -> str:
        """Summarize recent events for prompt context"""
        
        if not events:
            raise ValueError("ENTERPRISE: No events to summarize")
        
        summary_lines = []
        for event in events[:5]:  # Top 5 most relevant
            if not isinstance(event, dict):
                continue
                
            title = event.get('title', 'Unknown event')
            source = event.get('source', event.get('domain', 'Unknown source'))
            date = event.get('timestamp', event.get('published_date', ''))
            
            if title != 'Unknown event':
                line = f"- {title}"
                if source != 'Unknown source':
                    line += f" (Source: {source})"
                if date:
                    line += f" [{date}]"
                summary_lines.append(line)
        
        if not summary_lines:
            raise ValueError("ENTERPRISE: No valid events found for summarization")
        
        return "\n".join(summary_lines)