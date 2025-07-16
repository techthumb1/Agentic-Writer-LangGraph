# File: langgraph_app/mcp_integration.py
"""
MCP (Model Context Protocol) Integration for Agentic Writer
Provides enhanced context and capabilities through MCP servers
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import httpx
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Configuration for MCP server connections"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str] = None
    enabled: bool = True
    timeout: int = 30
    max_retries: int = 3

@dataclass
class MCPTool:
    """MCP tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    server: str

@dataclass
class MCPResource:
    """MCP resource definition"""
    uri: str
    name: str
    description: str
    mimeType: str
    server: str

class MCPManager:
    """
    Enhanced MCP Manager for Agentic Writer
    Handles multiple MCP servers for different content generation needs
    """
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.active_connections: Dict[str, Any] = {}
        self.client_sessions: Dict[str, httpx.AsyncClient] = {}
        
        # Load default MCP servers for content generation
        self._load_default_servers()
    
    def _load_default_servers(self):
        """Load default MCP servers optimized for content generation"""
        
        # 1. Filesystem MCP for template and style profile management
        self.servers['filesystem'] = MCPServerConfig(
            name='filesystem',
            command='npx',
            args=['-y', '@modelcontextprotocol/server-filesystem', 'storage/'],
            env={'FILESYSTEM_ALLOWED_EXTENSIONS': '.md,.txt,.json,.yaml,.yml'},
            enabled=True
        )
        
        # 2. Web Search MCP for research enhancement
        self.servers['web_search'] = MCPServerConfig(
            name='web_search',
            command='npx',
            args=['-y', '@modelcontextprotocol/server-brave-search'],
            env={'BRAVE_API_KEY': os.getenv('BRAVE_API_KEY', '')},
            enabled=bool(os.getenv('BRAVE_API_KEY'))
        )
        
        # 3. GitHub MCP for code examples and documentation
        self.servers['github'] = MCPServerConfig(
            name='github',
            command='npx',
            args=['-y', '@modelcontextprotocol/server-github'],
            env={'GITHUB_PERSONAL_ACCESS_TOKEN': os.getenv('GITHUB_TOKEN', '')},
            enabled=bool(os.getenv('GITHUB_TOKEN'))
        )
        
        # 4. Memory MCP for conversation context
        self.servers['memory'] = MCPServerConfig(
            name='memory',
            command='npx',
            args=['-y', '@modelcontextprotocol/server-memory'],
            enabled=True
        )
        
        # 5. Postgres MCP for content analytics (if available)
        self.servers['postgres'] = MCPServerConfig(
            name='postgres',
            command='npx',
            args=['-y', '@modelcontextprotocol/server-postgres'],
            env={'POSTGRES_CONNECTION_STRING': os.getenv('DATABASE_URL', '')},
            enabled=bool(os.getenv('DATABASE_URL'))
        )

    async def initialize_servers(self):
        """Initialize all enabled MCP servers"""
        logger.info("🚀 Initializing MCP servers...")
        
        for server_name, config in self.servers.items():
            if not config.enabled:
                logger.info(f"⏭️  Skipping disabled server: {server_name}")
                continue
            
            try:
                await self._initialize_server(server_name, config)
                logger.info(f"✅ MCP server '{server_name}' initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize MCP server '{server_name}': {e}")
                config.enabled = False

    async def _initialize_server(self, server_name: str, config: MCPServerConfig):
        """Initialize a single MCP server"""
        
        # Create async HTTP client for server communication
        self.client_sessions[server_name] = httpx.AsyncClient(
            timeout=httpx.Timeout(config.timeout),
            limits=httpx.Limits(max_connections=10)
        )
        
        # Start the MCP server process (simplified - in practice would use subprocess)
        # For now, we'll simulate the connection
        self.active_connections[server_name] = {
            'status': 'connected',
            'started_at': datetime.now().isoformat(),
            'config': config
        }
        
        # Discover tools and resources from the server
        await self._discover_capabilities(server_name)

    async def _discover_capabilities(self, server_name: str):
        """Discover tools and resources from an MCP server"""
        
        # Simulate capability discovery based on server type
        if server_name == 'filesystem':
            self.tools[f'{server_name}_read'] = MCPTool(
                name='read_file',
                description='Read content from files in the storage directory',
                inputSchema={'type': 'object', 'properties': {'path': {'type': 'string'}}},
                server=server_name
            )
            
            self.tools[f'{server_name}_write'] = MCPTool(
                name='write_file',
                description='Write content to files in the storage directory',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'path': {'type': 'string'},
                        'content': {'type': 'string'}
                    }
                },
                server=server_name
            )
        
        elif server_name == 'web_search':
            self.tools[f'{server_name}_search'] = MCPTool(
                name='web_search',
                description='Search the web for current information',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'query': {'type': 'string'},
                        'count': {'type': 'integer', 'default': 5}
                    }
                },
                server=server_name
            )
        
        elif server_name == 'github':
            self.tools[f'{server_name}_search'] = MCPTool(
                name='github_search',
                description='Search GitHub repositories and code',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'query': {'type': 'string'},
                        'type': {'type': 'string', 'enum': ['repositories', 'code', 'issues']}
                    }
                },
                server=server_name
            )
        
        elif server_name == 'memory':
            self.tools[f'{server_name}_store'] = MCPTool(
                name='store_memory',
                description='Store information in memory for later retrieval',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'key': {'type': 'string'},
                        'value': {'type': 'string'},
                        'namespace': {'type': 'string', 'default': 'default'}
                    }
                },
                server=server_name
            )
            
            self.tools[f'{server_name}_recall'] = MCPTool(
                name='recall_memory',
                description='Retrieve stored information from memory',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'key': {'type': 'string'},
                        'namespace': {'type': 'string', 'default': 'default'}
                    }
                },
                server=server_name
            )

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with given arguments"""
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        server_name = tool.server
        
        if server_name not in self.active_connections:
            raise ValueError(f"Server '{server_name}' not connected")
        
        try:
            # Simulate tool execution based on tool type
            result = await self._execute_tool(tool_name, arguments)
            
            logger.info(f"🔧 MCP tool '{tool_name}' executed successfully")
            return {
                'success': True,
                'result': result,
                'tool': tool_name,
                'server': server_name
            }
            
        except Exception as e:
            logger.error(f"❌ MCP tool '{tool_name}' failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool': tool_name,
                'server': server_name
            }

    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a specific MCP tool (simplified implementation)"""
        
        # Filesystem operations
        if tool_name == 'filesystem_read':
            return await self._read_file(arguments['path'])
        elif tool_name == 'filesystem_write':
            return await self._write_file(arguments['path'], arguments['content'])
        
        # Web search
        elif tool_name == 'web_search_search':
            return await self._web_search(arguments['query'], arguments.get('count', 5))
        
        # GitHub search
        elif tool_name == 'github_search':
            return await self._github_search(arguments['query'], arguments.get('type', 'repositories'))
        
        # Memory operations
        elif tool_name == 'memory_store':
            return await self._store_memory(arguments['key'], arguments['value'], arguments.get('namespace', 'default'))
        elif tool_name == 'memory_recall':
            return await self._recall_memory(arguments['key'], arguments.get('namespace', 'default'))
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _read_file(self, path: str) -> str:
        """Read file content"""
        try:
            full_path = os.path.join('storage', path.lstrip('/'))
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Failed to read file {path}: {e}")

    async def _write_file(self, path: str, content: str) -> str:
        """Write file content"""
        try:
            full_path = os.path.join('storage', path.lstrip('/'))
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"File {path} written successfully"
        except Exception as e:
            raise ValueError(f"Failed to write file {path}: {e}")

    async def _web_search(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Perform web search (simplified)"""
        # This would integrate with actual search APIs
        return [{
            'title': f'Search result for: {query}',
            'url': f'https://example.com/search?q={query}',
            'snippet': f'Mock search result for query: {query}',
            'source': 'web_search_mcp'
        }]

    async def _github_search(self, query: str, search_type: str = 'repositories') -> List[Dict[str, Any]]:
        """Search GitHub (simplified)"""
        # This would integrate with GitHub API
        return [{
            'name': f'repo-for-{query}',
            'url': f'https://github.com/example/repo-for-{query}',
            'description': f'Repository related to {query}',
            'stars': 100,
            'language': 'Python'
        }]

    async def _store_memory(self, key: str, value: str, namespace: str = 'default') -> str:
        """Store information in memory"""
        # This would integrate with persistent storage
        memory_key = f"{namespace}:{key}"
        # Store in a simple dict for now (would be persistent in practice)
        if not hasattr(self, '_memory_store'):
            self._memory_store = {}
        self._memory_store[memory_key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        return f"Stored {key} in namespace {namespace}"

    async def _recall_memory(self, key: str, namespace: str = 'default') -> str:
        """Retrieve information from memory"""
        memory_key = f"{namespace}:{key}"
        if not hasattr(self, '_memory_store'):
            self._memory_store = {}
        
        if memory_key in self._memory_store:
            return self._memory_store[memory_key]['value']
        else:
            raise ValueError(f"No memory found for key {key} in namespace {namespace}")

    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get all available MCP tools"""
        return [
            {
                'name': tool.name,
                'description': tool.description,
                'inputSchema': tool.inputSchema,
                'server': tool.server
            }
            for tool in self.tools.values()
        ]

    async def get_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers"""
        return {
            'servers': {
                name: {
                    'enabled': config.enabled,
                    'connected': name in self.active_connections,
                    'tools_count': len([t for t in self.tools.values() if t.server == name])
                }
                for name, config in self.servers.items()
            },
            'total_tools': len(self.tools),
            'total_resources': len(self.resources)
        }

    async def cleanup(self):
        """Clean up MCP connections"""
        logger.info("🧹 Cleaning up MCP connections...")
        
        for session in self.client_sessions.values():
            await session.aclose()
        
        self.client_sessions.clear()
        self.active_connections.clear()
        
        logger.info("✅ MCP cleanup completed")

# Global MCP manager instance
mcp_manager = MCPManager()

# Context manager for MCP lifecycle
@asynccontextmanager
async def mcp_context():
    """Context manager for MCP server lifecycle"""
    try:
        await mcp_manager.initialize_servers()
        yield mcp_manager
    finally:
        await mcp_manager.cleanup()

# Helper functions for agents
async def enhance_research_with_mcp(query: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance research using MCP tools"""
    
    enhanced_research = state.get('research', '')
    
    try:
        # Use web search MCP for additional research
        if 'web_search_search' in mcp_manager.tools:
            search_result = await mcp_manager.call_tool('web_search_search', {'query': query, 'count': 3})
            if search_result['success']:
                enhanced_research += f"\n\n## Additional Web Research:\n{search_result['result']}"
        
        # Store research in memory for later use
        if 'memory_store' in mcp_manager.tools:
            await mcp_manager.call_tool('memory_store', {
                'key': f'research_{query}',
                'value': enhanced_research,
                'namespace': 'content_generation'
            })
        
        return {**state, 'research': enhanced_research, 'mcp_enhanced': True}
        
    except Exception as e:
        logger.error(f"❌ MCP research enhancement failed: {e}")
        return {**state, 'mcp_enhanced': False}

async def save_content_with_mcp(content: str, filename: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Save generated content using MCP filesystem"""
    
    try:
        if 'filesystem_write' in mcp_manager.tools:
            result = await mcp_manager.call_tool('filesystem_write', {
                'path': f'generated_content/{filename}',
                'content': content
            })
            
            if result['success']:
                logger.info(f"✅ Content saved to {filename} via MCP")
                return {**state, 'saved_file': filename, 'mcp_saved': True}
        
        return {**state, 'mcp_saved': False}
        
    except Exception as e:
        logger.error(f"❌ MCP content saving failed: {e}")
        return {**state, 'mcp_saved': False}

async def load_style_profile_with_mcp(profile_name: str) -> Dict[str, Any]:
    """Load style profile using MCP filesystem"""
    
    try:
        if 'filesystem_read' in mcp_manager.tools:
            result = await mcp_manager.call_tool('filesystem_read', {
                'path': f'style_profile/{profile_name}.yaml'
            })
            
            if result['success']:
                # Parse YAML content (simplified)
                return {'profile_content': result['result'], 'loaded_via_mcp': True}
        
        return {'loaded_via_mcp': False}
        
    except Exception as e:
        logger.error(f"❌ MCP style profile loading failed: {e}")
        return {'loaded_via_mcp': False}

# Export for use in other modules
__all__ = [
    'MCPManager',
    'mcp_manager',
    'mcp_context',
    'enhance_research_with_mcp',
    'save_content_with_mcp',
    'load_style_profile_with_mcp'
]