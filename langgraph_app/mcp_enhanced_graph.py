# File: langgraph_app/mcp_enhanced_graph.py
"""
MCP-Enhanced LangGraph Integration
Updates existing graph with MCP capabilities
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableLambda

from .mcp_integration import mcp_manager, mcp_context
from .agents.mcp_enhanced_agents import (
    mcp_enhanced_researcher_fn,
    mcp_enhanced_planner_fn,
    mcp_enhanced_writer_fn,
    mcp_enhanced_publisher_fn
)

logger = logging.getLogger(__name__)

class MCPEnhancedWorkflow:
    """Enhanced workflow with MCP integration"""
    
    def __init__(self):
        self.graph = None
        self.memory = MemorySaver()
        self.mcp_initialized = False
    
    async def initialize_mcp_graph(self):
        """Initialize MCP-enhanced graph"""
        try:
            # Initialize MCP first
            if not self.mcp_initialized:
                await mcp_manager.initialize_servers()
                self.mcp_initialized = True
            
            # Create enhanced state graph
            workflow = StateGraph(dict)
            
            # Add MCP-enhanced nodes
            workflow.add_node("mcp_planner", self._mcp_planner_node)
            workflow.add_node("mcp_researcher", self._mcp_researcher_node)
            workflow.add_node("mcp_writer", self._mcp_writer_node)
            workflow.add_node("mcp_editor", self._mcp_editor_node)
            workflow.add_node("mcp_formatter", self._mcp_formatter_node)
            workflow.add_node("mcp_publisher", self._mcp_publisher_node)
            workflow.add_node("mcp_analytics", self._mcp_analytics_node)
            
            # Define workflow edges
            workflow.set_entry_point("mcp_planner")
            workflow.add_edge("mcp_planner", "mcp_researcher")
            workflow.add_edge("mcp_researcher", "mcp_writer")
            workflow.add_edge("mcp_writer", "mcp_editor")
            workflow.add_edge("mcp_editor", "mcp_formatter")
            workflow.add_edge("mcp_formatter", "mcp_publisher")
            workflow.add_edge("mcp_publisher", "mcp_analytics")
            workflow.add_edge("mcp_analytics", END)
            
            # Compile graph
            self.graph = workflow.compile(checkpointer=self.memory)
            
            logger.info("✅ MCP-enhanced graph initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ MCP graph initialization failed: {e}")
            raise
    
    async def _mcp_planner_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """MCP-enhanced planner node"""
        try:
            # Store planning start in memory
            if 'memory_store' in mcp_manager.tools:
                await mcp_manager.call_tool('memory_store', {
                    'key': f"planning_start_{state.get('requestId', 'unknown')}",
                    'value': datetime.now().isoformat(),
                    'namespace': 'workflow_tracking'
                })
            
            # Execute MCP-enhanced planning
            result = await mcp_enhanced_planner_fn(state)
            
            # Log planning completion
            logger.info(f"✅ MCP planning completed for request {state.get('requestId', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ MCP planner node failed: {e}")
            return {**state, 'mcp_planner_error': str(e)}
    
    async def _mcp_researcher_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """MCP-enhanced researcher node"""
        try:
            # Execute MCP-enhanced research
            result = await mcp_enhanced_researcher_fn(state)
            
            # Store research summary
            if 'memory_store' in mcp_manager.tools:
                research_summary = {
                    'topic': state.get('topic', ''),
                    'research_length': len(result.get('research', '')),
                    'sources_used': result.get('research_sources', []),
                    'timestamp': datetime.now().isoformat()
                }
                
                await mcp_manager.call_tool('memory_store', {
                    'key': f"research_summary_{state.get('requestId', 'unknown')}",
                    'value': json.dumps(research_summary),
                    'namespace': 'research_tracking'
                })
            
            logger.info(f"✅ MCP research completed for request {state.get('requestId', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ MCP researcher node failed: {e}")
            return {**state, 'mcp_researcher_error': str(e)}
    
    async def _mcp_writer_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """MCP-enhanced writer node"""
        try:
            # Execute MCP-enhanced writing
            result = await mcp_enhanced_writer_fn(state)
            
            # Store writing metrics
            if 'memory_store' in mcp_manager.tools:
                writing_metrics = {
                    'word_count': len(result.get('draft_content', '').split()),
                    'characters': len(result.get('draft_content', '')),
                    'writing_time': datetime.now().isoformat(),
                    'style_profile': state.get('style_profile', 'unknown')
                }
                
                await mcp_manager.call_tool('memory_store', {
                    'key': f"writing_metrics_{state.get('requestId', 'unknown')}",
                    'value': json.dumps(writing_metrics),
                    'namespace': 'writing_tracking'
                })
            
            logger.info(f"✅ MCP writing completed for request {state.get('requestId', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ MCP writer node failed: {e}")
            return {**state, 'mcp_writer_error': str(e)}
    
    async def _mcp_editor_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """MCP-enhanced editor node"""
        try:
            # For now, use standard editing logic with MCP context
            draft_content = state.get('draft_content', '')
            
            # Enhanced editing with MCP context
            edited_content = draft_content  # Simplified for now
            
            # Save edited version
            if 'filesystem_write' in mcp_manager.tools:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                await mcp_manager.call_tool('filesystem_write', {
                    'path': f"edited/edited_{timestamp}.md",
                    'content': edited_content
                })
            
            return {**state, 'edited_content': edited_content, 'mcp_edited': True}
            
        except Exception as e:
            logger.error(f"❌ MCP editor node failed: {e}")
            return {**state, 'mcp_editor_error': str(e)}
    
    async def _mcp_formatter_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """MCP-enhanced formatter node"""
        try:
            # Format content with MCP context
            content = state.get('edited_content', state.get('draft_content', ''))
            
            # Enhanced formatting
            formatted_content = f"""# {state.get('topic', 'Generated Content')}

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Style Profile: {state.get('style_profile', 'Default')}*
*Enhanced with MCP: {state.get('mcp_enhanced', False)}*

{content}

---
*This content was generated using MCP-enhanced agents*
"""
            
            return {**state, 'formatted_content': formatted_content, 'mcp_formatted': True}
            
        except Exception as e:
            logger.error(f"❌ MCP formatter node failed: {e}")
            return {**state, 'mcp_formatter_error': str(e)}
    
    async def _mcp_publisher_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """MCP-enhanced publisher node"""
        try:
            # Execute MCP-enhanced publishing
            result = await mcp_enhanced_publisher_fn(state)
            
            logger.info(f"✅ MCP publishing completed for request {state.get('requestId', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ MCP publisher node failed: {e}")
            return {**state, 'mcp_publisher_error': str(e)}
    
    async def _mcp_analytics_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """MCP analytics and reporting node"""
        try:
            # Collect workflow analytics
            analytics = {
                'request_id': state.get('requestId', 'unknown'),
                'completion_time': datetime.now().isoformat(),
                'stages_completed': [],
                'mcp_tools_used': [],
                'final_word_count': 0,
                'errors': []
            }
            
            # Check which stages completed successfully
            if state.get('mcp_enhanced'):
                analytics['stages_completed'].append('planning')
            if state.get('research'):
                analytics['stages_completed'].append('research')
            if state.get('draft_content'):
                analytics['stages_completed'].append('writing')
            if state.get('edited_content'):
                analytics['stages_completed'].append('editing')
            if state.get('formatted_content'):
                analytics['stages_completed'].append('formatting')
                analytics['final_word_count'] = len(state.get('formatted_content', '').split())
            if state.get('mcp_published'):
                analytics['stages_completed'].append('publishing')
            
            # Collect errors
            for key, value in state.items():
                if key.endswith('_error'):
                    analytics['errors'].append({key: value})
            
            # Store analytics
            if 'memory_store' in mcp_manager.tools:
                await mcp_manager.call_tool('memory_store', {
                    'key': f"analytics_{state.get('requestId', 'unknown')}",
                    'value': json.dumps(analytics),
                    'namespace': 'workflow_analytics'
                })
            
            return {**state, 'analytics': analytics, 'workflow_complete': True}
            
        except Exception as e:
            logger.error(f"❌ MCP analytics node failed: {e}")
            return {**state, 'mcp_analytics_error': str(e)}
    
    async def execute_workflow(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the MCP-enhanced workflow"""
        try:
            if not self.graph:
                await self.initialize_mcp_graph()
            
            # Execute the workflow
            config = {"configurable": {"thread_id": initial_state.get('requestId', 'default')}}
            
            final_state = None
            async for state in self.graph.astream(initial_state, config=config):
                final_state = state
                logger.info(f"🔄 Workflow step completed: {list(state.keys())}")
            
            return final_state or initial_state
            
        except Exception as e:
            logger.error(f"❌ MCP workflow execution failed: {e}")
            return {**initial_state, 'workflow_error': str(e)}

# Global MCP workflow instance
mcp_workflow = MCPEnhancedWorkflow()

# Integration function for existing server
async def execute_mcp_enhanced_generation(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute MCP-enhanced content generation"""
    try:
        # Initialize workflow if needed
        if not mcp_workflow.graph:
            await mcp_workflow.initialize_mcp_graph()
        
        # Execute workflow
        result = await mcp_workflow.execute_workflow(request_data)
        
        # Extract final content
        final_content = (
            result.get('formatted_content') or 
            result.get('edited_content') or 
            result.get('draft_content') or 
            result.get('content', '')
        )
        
        # Return standardized response
        return {
            'success': True,
            'content': final_content,
            'generation_id': request_data.get('requestId', 'unknown'),
            'request_id': request_data.get('requestId', 'unknown'),
            'status': 'completed' if final_content else 'failed',
            'metadata': {
                'mcp_enhanced': True,
                'stages_completed': result.get('analytics', {}).get('stages_completed', []),
                'word_count': len(final_content.split()) if final_content else 0,
                'mcp_tools_used': result.get('mcp_tools_available', []),
                'workflow_complete': result.get('workflow_complete', False),
                'errors': result.get('analytics', {}).get('errors', [])
            }
        }
        
    except Exception as e:
        logger.error(f"❌ MCP generation execution failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'generation_id': request_data.get('requestId', 'unknown'),
            'request_id': request_data.get('requestId', 'unknown'),
            'status': 'failed',
            'metadata': {
                'mcp_enhanced': False,
                'error_type': 'mcp_workflow_error'
            }
        }

# Export for use in main server
__all__ = [
    'MCPEnhancedWorkflow',
    'mcp_workflow',
    'execute_mcp_enhanced_generation'
]