# File: langgraph_app/mcp_server_extension.py
"""
MCP Extension for Existing Integrated Server
Adds MCP capabilities to your existing server without replacing it
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import MCP components
from .mcp_integration import mcp_manager
from .mcp_server_integration import (
    MCPToolCall, MCPToolResponse, MCPMemoryStore, 
    MCPMemoryRecall, MCPFileOperation, MCPSearchRequest
)

logger = logging.getLogger(__name__)

class MCPGenerationRequest(BaseModel):
    """Extended generation request with MCP options"""
    # Keep all existing fields from your current GenerateRequest
    template: str
    style_profile: str
    dynamic_parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=5)
    timeout_seconds: int = Field(default=300, ge=60, le=1800)
    
    # Add MCP-specific fields
    enable_mcp: bool = Field(default=True, description="Enable MCP enhancement")
    research_depth: str = Field(default="moderate", description="Research depth: shallow, moderate, deep")
    memory_namespace: str = Field(default="default", description="Memory namespace to use")

def add_mcp_endpoints(app: FastAPI) -> None:
    """Add MCP endpoints to existing FastAPI app"""
    
    @app.get("/api/mcp/health")
    async def mcp_health_check():
        """Check MCP health status"""
        try:
            if not mcp_manager.active_connections:
                return JSONResponse(
                    content={
                        "status": "unavailable",
                        "message": "MCP not initialized",
                        "servers": {},
                        "capabilities": {}
                    },
                    status_code=503
                )
            
            status = await mcp_manager.get_server_status()
            
            return JSONResponse(content={
                "status": "healthy",
                "message": "MCP is operational",
                "servers": status.get('servers', {}),
                "capabilities": {
                    "research": 'web_search_search' in mcp_manager.tools,
                    "github": 'github_search' in mcp_manager.tools,
                    "memory": 'memory_store' in mcp_manager.tools,
                    "filesystem": 'filesystem_write' in mcp_manager.tools
                }
            })
            
        except Exception as e:
            logger.error(f"❌ MCP health check failed: {e}")
            return JSONResponse(
                content={
                    "status": "error",
                    "message": str(e),
                    "servers": {},
                    "capabilities": {}
                },
                status_code=500
            )
    
    @app.get("/api/mcp/status")
    async def get_mcp_status():
        """Get MCP server status"""
        try:
            if not mcp_manager.active_connections:
                return JSONResponse(
                    content={"error": "MCP not initialized"},
                    status_code=503
                )
            
            status = await mcp_manager.get_server_status()
            return JSONResponse(content=status)
            
        except Exception as e:
            logger.error(f"❌ MCP status check failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/mcp/tools")
    async def get_mcp_tools():
        """Get available MCP tools"""
        try:
            if not mcp_manager.active_connections:
                return JSONResponse(
                    content={"error": "MCP not initialized"},
                    status_code=503
                )
            
            tools = await mcp_manager.get_available_tools()
            capabilities = {
                "research": 'web_search_search' in mcp_manager.tools,
                "github": 'github_search' in mcp_manager.tools,
                "memory": 'memory_store' in mcp_manager.tools,
                "filesystem": 'filesystem_write' in mcp_manager.tools
            }
            
            return JSONResponse(content={
                "tools": tools,
                "capabilities": capabilities
            })
            
        except Exception as e:
            logger.error(f"❌ MCP tools retrieval failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/mcp/tools/call")
    async def call_mcp_tool(tool_call: MCPToolCall):
        """Call an MCP tool"""
        try:
            if not mcp_manager.active_connections:
                raise HTTPException(status_code=503, detail="MCP not initialized")
            
            start_time = datetime.now()
            
            # Execute the tool
            result = await mcp_manager.call_tool(
                tool_call.tool_name,
                tool_call.arguments
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return MCPToolResponse(
                success=result['success'],
                result=result.get('result'),
                error=result.get('error'),
                tool_name=tool_call.tool_name,
                server=result.get('server', 'unknown'),
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"❌ MCP tool call failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

async def enhance_generation_with_mcp(
    original_task_func,
    requestId: str,
    template_config: Dict[str, Any],
    style_config: Dict[str, Any],
    app_state,
    mcp_options: Optional[Dict[str, Any]] = None
):
    """Enhance existing generation with MCP capabilities"""
    
    mcp_enabled = mcp_options and mcp_options.get('enable_mcp', True)
    
    if not mcp_enabled or not mcp_manager.active_connections:
        # Fall back to original generation
        logger.info(f"🔄 Using original generation for {requestId} (MCP disabled or unavailable)")
        return await original_task_func(requestId, template_config, style_config, app_state)
    
    logger.info(f"🚀 Using MCP-enhanced generation for {requestId}")
    
    try:
        # Store generation context in MCP memory
        if 'memory_store' in mcp_manager.tools:
            context = {
                'requestId': requestId,
                'template': template_config.get('name', 'unknown'),
                'style_profile': style_config.get('name', 'unknown'),
                'started_at': datetime.now().isoformat(),
                'mcp_enhanced': True
            }
            
            await mcp_manager.call_tool('memory_store', {
                'key': f'generation_context_{requestId}',
                'value': str(context),
                'namespace': mcp_options.get('memory_namespace', 'default')
            })
        
        # Enhanced research if available
        topic = template_config.get('dynamic_parameters', {}).get('topic', 'Content Generation')
        if 'web_search_search' in mcp_manager.tools:
            logger.info(f"🔍 Enhancing research for topic: {topic}")
            
            search_result = await mcp_manager.call_tool('web_search_search', {
                'query': topic,
                'count': 3
            })
            
            if search_result.get('success'):
                # Add research to template config
                template_config.setdefault('enhanced_research', search_result.get('result', []))
        
        # Use original generation with enhanced context
        result = await original_task_func(requestId, template_config, style_config, app_state)
        
        # Save result to MCP filesystem if available
        if hasattr(result, 'content') and result.content and 'filesystem_write' in mcp_manager.tools:
            try:
                filename = f"generated_{requestId}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                await mcp_manager.call_tool('filesystem_write', {
                    'path': f'generated_content/{filename}',
                    'content': result.content
                })
                
                # Update result metadata
                if hasattr(result, 'metadata'):
                    result.metadata['mcp_saved_file'] = filename
                    result.metadata['mcp_enhanced'] = True
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to save content via MCP: {e}")
        
        logger.info(f"✅ MCP-enhanced generation completed for {requestId}")
        return result
        
    except Exception as e:
        logger.error(f"❌ MCP enhancement failed for {requestId}: {e}")
        # Fall back to original generation
        logger.info(f"🔄 Falling back to original generation for {requestId}")
        return await original_task_func(requestId, template_config, style_config, app_state)

async def initialize_mcp_for_existing_server(app: FastAPI) -> bool:
    """Initialize MCP for existing server"""
    try:
        logger.info("🔧 Initializing MCP for existing server...")
        
        # Initialize MCP manager
        await mcp_manager.initialize_servers()
        
        # Add MCP endpoints
        add_mcp_endpoints(app)
        
        # Store MCP manager in app state
        app.state.mcp_manager = mcp_manager
        app.state.mcp_available = True
        
        logger.info("✅ MCP successfully integrated with existing server")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP initialization failed: {e}")
        app.state.mcp_available = False
        return False

async def cleanup_mcp_for_existing_server(app: FastAPI):
    """Cleanup MCP for existing server"""
    try:
        if hasattr(app.state, 'mcp_manager'):
            await app.state.mcp_manager.cleanup()
            logger.info("✅ MCP cleanup completed")
    except Exception as e:
        logger.error(f"❌ MCP cleanup failed: {e}")

# Export key functions
__all__ = [
    'add_mcp_endpoints',
    'enhance_generation_with_mcp',
    'initialize_mcp_for_existing_server',
    'cleanup_mcp_for_existing_server',
    'MCPGenerationRequest'
]