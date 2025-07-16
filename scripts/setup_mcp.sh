# File: setup_mcp.sh
#!/bin/bash

echo "🚀 Setting up MCP (Model Context Protocol) for Agentic Writer..."

# Create MCP directories
echo "📁 Creating MCP directories..."
mkdir -p storage/mcp_data
mkdir -p storage/drafts
mkdir -p storage/published
mkdir -p storage/templates
mkdir -p storage/analytics
mkdir -p logs/mcp

# Install MCP servers (Node.js required)
echo "📦 Installing MCP servers..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Install MCP servers globally
echo "🔧 Installing MCP servers..."
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-postgres

# Create MCP configuration
echo "⚙️ Creating MCP configuration..."
cat > mcp_config.json << EOF
{
  "servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "storage/"],
      "env": {
        "FILESYSTEM_ALLOWED_EXTENSIONS": ".md,.txt,.json,.yaml,.yml"
      }
    },
    "web_search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${DATABASE_URL}"
      }
    }
  }
}
EOF

# Create environment template
echo "📝 Creating environment template..."
cat > .env.mcp.template << EOF
# MCP Configuration
# Copy this to .env.local and fill in your API keys

# Brave Search API (for web search capabilities)
BRAVE_API_KEY=your_brave_api_key_here

# GitHub Token (for GitHub integration)
GITHUB_TOKEN=your_github_token_here

# Database URL (for PostgreSQL MCP server)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# OpenAI API Key (for content generation)
OPENAI_API_KEY=your_openai_api_key_here

# FastAPI Configuration
FASTAPI_BASE_URL=http://localhost:8000
FASTAPI_API_KEY=your_fastapi_api_key_here
EOF

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install httpx asyncio

# Create test scripts
echo "🧪 Creating test scripts..."
cat > test_mcp.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for MCP integration
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langgraph_app.mcp_integration import mcp_manager, mcp_context

async def test_mcp():
    """Test MCP functionality"""
    print("🧪 Testing MCP integration...")
    
    try:
        # Test MCP initialization
        print("1. Testing MCP initialization...")
        await mcp_manager.initialize_servers()
        print("   ✅ MCP initialized successfully")
        
        # Test server status
        print("2. Testing server status...")
        status = await mcp_manager.get_server_status()
        print(f"   📊 Status: {status}")
        
        # Test available tools
        print("3. Testing available tools...")
        tools = await mcp_manager.get_available_tools()
        print(f"   🔧 Available tools: {len(tools)}")
        for tool in tools:
            print(f"      - {tool['name']} ({tool['server']})")
        
        # Test memory operations (if available)
        if 'memory_store' in mcp_manager.tools:
            print("4. Testing memory operations...")
            
            # Store test data
            store_result = await mcp_manager.call_tool('memory_store', {
                'key': 'test_key',
                'value': 'test_value',
                'namespace': 'test'
            })
            print(f"   💾 Store result: {store_result}")
            
            # Recall test data
            recall_result = await mcp_manager.call_tool('memory_recall', {
                'key': 'test_key',
                'namespace': 'test'
            })
            print(f"   📖 Recall result: {recall_result}")
        
        # Test filesystem operations (if available)
        if 'filesystem_write' in mcp_manager.tools:
            print("5. Testing filesystem operations...")
            
            # Write test file
            write_result = await mcp_manager.call_tool('filesystem_write', {
                'path': 'test_mcp_file.txt',
                'content': 'This is a test file created by MCP!'
            })
            print(f"   📝 Write result: {write_result}")
            
            # Read test file
            if 'filesystem_read' in mcp_manager.tools:
                read_result = await mcp_manager.call_tool('filesystem_read', {
                    'path': 'test_mcp_file.txt'
                })
                print(f"   📖 Read result: {read_result}")
        
        print("✅ All MCP tests completed successfully!")
        
    except Exception as e:
        print(f"❌ MCP test failed: {e}")
        return False
    
    finally:
        # Cleanup
        await mcp_manager.cleanup()
        print("🧹 MCP cleanup completed")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mcp())
    sys.exit(0 if success else 1)
EOF

# Make test script executable
chmod +x test_mcp.py

# Create startup script
echo "🚀 Creating startup script..."
cat > start_with_mcp.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Agentic Writer with MCP support..."

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "⚠️  .env.local not found. Please copy .env.mcp.template to .env.local and configure your API keys."
    exit 1
fi

# Load environment variables
source .env.local

# Start the server
echo "🔧 Starting MCP-enhanced server..."
python -m langgraph_app.integrated_server_mcp
EOF

# Make startup script executable
chmod +x start_with_mcp.sh

# Create MCP documentation
echo "📚 Creating MCP documentation..."
cat > MCP_INTEGRATION.md << 'EOF'
# MCP Integration for Agentic Writer

## Overview

This project integrates Model Context Protocol (MCP) to enhance content generation capabilities with:

- **Filesystem Operations**: Read/write files for templates, drafts, and published content
- **Web Search**: Real-time web search for research enhancement
- **GitHub Integration**: Access to code repositories and documentation
- **Memory System**: Persistent storage for context and analytics
- **Database Integration**: PostgreSQL integration for data persistence

## Setup

1. **Install MCP servers**:
   ```bash
   ./setup_mcp.sh
   ```

2. **Configure environment**:
   ```bash
   cp .env.mcp.template .env.local
   # Edit .env.local with your API keys
   ```

3. **Test MCP integration**:
   ```bash
   python test_mcp.py
   ```

4. **Start the server**:
   ```bash
   ./start_with_mcp.sh
   ```

## API Endpoints

### MCP Status
- `GET /api/mcp/status` - Get MCP server status
- `GET /api/mcp/health` - Health check for MCP services

### MCP Tools
- `GET /api/mcp/tools` - Get available MCP tools
- `POST /api/mcp/tools/call` - Call an MCP tool

### Memory Operations
- `POST /api/mcp/memory/store` - Store data in memory
- `POST /api/mcp/memory/recall` - Recall data from memory

### File Operations
- `POST /api/mcp/files/read` - Read file via MCP
- `POST /api/mcp/files/write` - Write file via MCP

### Search Operations
- `POST /api/mcp/search` - Search via MCP (web, GitHub, etc.)

## Frontend Integration

The MCP dashboard is available at `/mcp-dashboard` and provides:

- Server status monitoring
- Tool testing interface
- Memory operations
- File management
- Search capabilities
- Analytics and reporting

## Architecture

```
Frontend (React)
    ↓
FastAPI Server
    ↓
MCP Manager
    ↓
MCP Servers (Node.js)
    ↓
External APIs (Brave, GitHub, etc.)
```

## Configuration

MCP servers are configured in `mcp_config.json`:

```json
{
  "servers": {
    "filesystem": { ... },
    "web_search": { ... },
    "github": { ... },
    "memory": { ... },
    "postgres": { ... }
  }
}
```

## Troubleshooting

1. **MCP servers not starting**: Check Node.js installation and MCP server packages
2. **API key errors**: Verify environment variables in `.env.local`
3. **Connection issues**: Check network connectivity and firewall settings
4. **Memory errors**: Ensure sufficient system resources

## Development

- MCP integration code: `langgraph_app/mcp_integration.py`
- Enhanced agents: `langgraph_app/agents/mcp_enhanced_agents.py`
- Server integration: `langgraph_app/mcp_server_integration.py`
- Frontend components: `frontend/components/mcp/`

## Security Notes

- API keys are stored in environment variables
- MCP servers run in isolated processes
- File operations are restricted to the `storage/` directory
- All API calls are authenticated and rate-limited
EOF

echo "✅ MCP setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Copy .env.mcp.template to .env.local and configure your API keys"
echo "2. Run: python test_mcp.py (to test the integration)"
echo "3. Run: ./start_with_mcp.sh (to start the server)"
echo "4. Visit: http://localhost:8000/api/mcp/status (to check MCP status)"
echo ""
echo "📚 Documentation: MCP_INTEGRATION.md"
echo "🎯 MCP Dashboard: http://localhost:8000 (after starting server)"