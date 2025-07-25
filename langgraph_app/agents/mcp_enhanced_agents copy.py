# File: langgraph_app/agents/mcp_enhanced_agents.py
"""
MCP-Enhanced Agent Functions
Integrates MCP capabilities with existing agents
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import yaml

from ..mcp_integration import mcp_manager, enhance_research_with_mcp, save_content_with_mcp, load_style_profile_with_mcp

logger = logging.getLogger(__name__)

class MCPEnhancedResearcher:
    """Enhanced researcher with MCP integration"""
    
    async def conduct_mcp_research(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct research using MCP tools"""
        
        topic = state.get('topic', '')
        if not topic:
            logger.warning("No topic provided for MCP research")
            return state
        
        try:
            # 1. Basic research enhancement
            enhanced_state = await enhance_research_with_mcp(topic, state)
            
            # 2. GitHub code search if relevant
            if any(keyword in topic.lower() for keyword in ['code', 'programming', 'algorithm', 'implementation']):
                if 'github_search' in mcp_manager.tools:
                    github_result = await mcp_manager.call_tool('github_search', {
                        'query': topic,
                        'type': 'code'
                    })
                    
                    if github_result['success']:
                        enhanced_state['github_examples'] = github_result['result']
                        enhanced_state['research'] += f"\n\n## Code Examples:\n{json.dumps(github_result['result'], indent=2)}"
            
            # 3. Store research context in memory
            if 'memory_store' in mcp_manager.tools:
                await mcp_manager.call_tool('memory_store', {
                    'key': f'research_context_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'value': json.dumps({
                        'topic': topic,
                        'research_length': len(enhanced_state.get('research', '')),
                        'enhanced_with_mcp': True,
                        'timestamp': datetime.now().isoformat()
                    }),
                    'namespace': 'research_history'
                })
            
            logger.info(f"✅ MCP research completed for topic: {topic}")
            return enhanced_state
            
        except Exception as e:
            logger.error(f"❌ MCP research failed: {e}")
            return {**state, 'mcp_research_error': str(e)}

class MCPEnhancedPlanner:
    """Enhanced planner with MCP context"""
    
    async def create_mcp_plan(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create content plan using MCP memory and context"""
        
        try:
            # 1. Load previous successful plans from memory
            similar_plans = []
            if 'memory_recall' in mcp_manager.tools:
                try:
                    plans_result = await mcp_manager.call_tool('memory_recall', {
                        'key': 'successful_plans',
                        'namespace': 'planning_history'
                    })
                    if plans_result['success']:
                        similar_plans = json.loads(plans_result['result'])
                except:
                    pass  # No previous plans found
            
            # 2. Enhanced planning with MCP context
            content_plan = state.get('content_plan', {})
            
            # Add MCP-enhanced sections
            content_plan['mcp_enhanced'] = True
            content_plan['available_tools'] = list(mcp_manager.tools.keys())
            content_plan['research_sources'] = []
            
            if 'web_search_search' in mcp_manager.tools:
                content_plan['research_sources'].append('web_search')
            if 'github_search' in mcp_manager.tools:
                content_plan['research_sources'].append('github')
            
            # 3. Store plan in memory for future reference
            if 'memory_store' in mcp_manager.tools:
                await mcp_manager.call_tool('memory_store', {
                    'key': f'plan_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'value': json.dumps(content_plan),
                    'namespace': 'planning_history'
                })
            
            return {**state, 'content_plan': content_plan}
            
        except Exception as e:
            logger.error(f"❌ MCP planning failed: {e}")
            return {**state, 'mcp_planning_error': str(e)}

class MCPEnhancedWriter:
    """Enhanced writer with MCP capabilities"""
    
    async def write_with_mcp_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write content using MCP context and tools"""
        
        try:
            # 1. Recall relevant research from memory
            research_context = ""
            if 'memory_recall' in mcp_manager.tools:
                try:
                    topic = state.get('topic', '')
                    context_result = await mcp_manager.call_tool('memory_recall', {
                        'key': f'research_{topic}',
                        'namespace': 'content_generation'
                    })
                    if context_result['success']:
                        research_context = context_result['result']
                except:
                    pass  # No previous research found
            
            # 2. Enhanced content generation
            draft_content = state.get('draft_content', '')
            
            # Add MCP context to the draft
            if research_context:
                draft_content += f"\n\n<!-- MCP Research Context -->\n{research_context}"
            
            # 3. Save draft to filesystem via MCP
            if 'filesystem_write' in mcp_manager.tools:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"draft_{timestamp}.md"
                
                save_result = await mcp_manager.call_tool('filesystem_write', {
                    'path': f'drafts/{filename}',
                    'content': draft_content
                })
                
                if save_result['success']:
                    state['draft_saved'] = filename
            
            return {**state, 'draft_content': draft_content, 'mcp_enhanced': True}
            
        except Exception as e:
            logger.error(f"❌ MCP writing failed: {e}")
            return {**state, 'mcp_writing_error': str(e)}

class MCPEnhancedPublisher:
    """Enhanced publisher with MCP storage"""
    
    async def publish_with_mcp(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Publish content using MCP filesystem"""
        
        try:
            final_content = state.get('formatted_content', '') or state.get('content', '')
            
            if not final_content:
                logger.warning("No content to publish")
                return state
            
            # 1. Generate filename
            topic = state.get('topic', 'content')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{topic.replace(' ', '_').lower()}_{timestamp}.md"
            
            # 2. Save to published content directory
            if 'filesystem_write' in mcp_manager.tools:
                save_result = await mcp_manager.call_tool('filesystem_write', {
                    'path': f'published/{filename}',
                    'content': final_content
                })
                
                if save_result['success']:
                    # 3. Store publication record in memory
                    if 'memory_store' in mcp_manager.tools:
                        publication_record = {
                            'filename': filename,
                            'topic': topic,
                            'word_count': len(final_content.split()),
                            'published_at': datetime.now().isoformat(),
                            'style_profile': state.get('style_profile', 'unknown')
                        }
                        
                        await mcp_manager.call_tool('memory_store', {
                            'key': f'publication_{timestamp}',
                            'value': json.dumps(publication_record),
                            'namespace': 'publications'
                        })
                    
                    logger.info(f"✅ Content published as {filename}")
                    return {**state, 'published_file': filename, 'mcp_published': True}
            
            return {**state, 'mcp_published': False}
            
        except Exception as e:
            logger.error(f"❌ MCP publishing failed: {e}")
            return {**state, 'mcp_publishing_error': str(e)}

# MCP-Enhanced Agent Functions for LangGraph
async def mcp_enhanced_researcher_fn(state: Dict[str, Any]) -> Dict[str, Any]:
    """MCP-enhanced researcher function"""
    researcher = MCPEnhancedResearcher()
    return await researcher.conduct_mcp_research(state)

async def mcp_enhanced_planner_fn(state: Dict[str, Any]) -> Dict[str, Any]:
    """MCP-enhanced planner function"""
    planner = MCPEnhancedPlanner()
    return await planner.create_mcp_plan(state)

async def mcp_enhanced_writer_fn(state: Dict[str, Any]) -> Dict[str, Any]:
    """MCP-enhanced writer function"""
    writer = MCPEnhancedWriter()
    return await writer.write_with_mcp_context(state)

async def mcp_enhanced_publisher_fn(state: Dict[str, Any]) -> Dict[str, Any]:
    """MCP-enhanced publisher function"""
    publisher = MCPEnhancedPublisher()
    return await publisher.publish_with_mcp(state)

# Style Profile Loader with MCP
async def load_style_profile_mcp(profile_name: str) -> Dict[str, Any]:
    """Load style profile using MCP"""
    
    try:
        # First try to load from memory cache
        if 'memory_recall' in mcp_manager.tools:
            try:
                cached_result = await mcp_manager.call_tool('memory_recall', {
                    'key': f'style_profile_{profile_name}',
                    'namespace': 'style_profiles'
                })
                if cached_result['success']:
                    return json.loads(cached_result['result'])
            except:
                pass  # Cache miss, load from file
        
        # Load from filesystem
        if 'filesystem_read' in mcp_manager.tools:
            file_result = await mcp_manager.call_tool('filesystem_read', {
                'path': f'style_profile/{profile_name}.yaml'
            })
            
            if file_result['success']:
                # Parse YAML content
                try:
                    profile_data = yaml.safe_load(file_result['result'])
                    
                    # Cache in memory for future use
                    if 'memory_store' in mcp_manager.tools:
                        await mcp_manager.call_tool('memory_store', {
                            'key': f'style_profile_{profile_name}',
                            'value': json.dumps(profile_data),
                            'namespace': 'style_profiles'
                        })
                    
                    return profile_data
                    
                except yaml.YAMLError as e:
                    logger.error(f"❌ YAML parsing failed for {profile_name}: {e}")
                    return {'error': f'Invalid YAML in {profile_name}'}
        
        return {'error': f'Style profile {profile_name} not found'}
        
    except Exception as e:
        logger.error(f"❌ Style profile loading failed: {e}")
        return {'error': str(e)}

# Analytics and Reporting with MCP
async def get_mcp_analytics() -> Dict[str, Any]:
    """Get analytics from MCP memory"""
    
    try:
        analytics = {
            'publications': [],
            'research_history': [],
            'server_status': await mcp_manager.get_server_status()
        }
        
        # Get publication history
        if 'memory_recall' in mcp_manager.tools:
            # This would iterate through publication records
            # For now, return mock data
            try:
                pub_result = await mcp_manager.call_tool('memory_recall', {
                    'key': 'publication_summary',
                    'namespace': 'analytics'
                })
                if pub_result['success']:
                    analytics['publications'] = json.loads(pub_result['result'])
            except:
                analytics['publications'] = []
        
        # Get research history
        try:
            research_result = await mcp_manager.call_tool('memory_recall', {
                'key': 'research_summary',
                'namespace': 'analytics'
            })
            if research_result['success']:
                analytics['research_history'] = json.loads(research_result['result'])
        except:
            analytics['research_history'] = []
        
        return analytics
        
    except Exception as e:
        logger.error(f"❌ MCP analytics failed: {e}")
        return {'error': str(e)}

# MCP Tool Registry for Frontend
async def get_mcp_tools_for_frontend() -> Dict[str, Any]:
    """Get MCP tools formatted for frontend consumption"""
    
    try:
        tools = await mcp_manager.get_available_tools()
        server_status = await mcp_manager.get_server_status()
        
        return {
            'tools': tools,
            'servers': server_status,
            'capabilities': {
                'research': 'web_search_search' in mcp_manager.tools,
                'github': 'github_search' in mcp_manager.tools,
                'memory': 'memory_store' in mcp_manager.tools,
                'filesystem': 'filesystem_write' in mcp_manager.tools,
                'database': 'postgres' in mcp_manager.servers and mcp_manager.servers['postgres'].enabled
            }
        }
        
    except Exception as e:
        logger.error(f"❌ MCP tools for frontend failed: {e}")
        return {'error': str(e)}

# Export all functions
__all__ = [
    'MCPEnhancedResearcher',
    'MCPEnhancedPlanner', 
    'MCPEnhancedWriter',
    'MCPEnhancedPublisher',
    'mcp_enhanced_researcher_fn',
    'mcp_enhanced_planner_fn',
    'mcp_enhanced_writer_fn',
    'mcp_enhanced_publisher_fn',
    'load_style_profile_mcp',
    'get_mcp_analytics',
    'get_mcp_tools_for_frontend'
]