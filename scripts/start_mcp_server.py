# File: start_mcp_server.py
"""
Startup script for MCP-enhanced Agentic Writer
Handles all dependencies and proper initialization
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'httpx',
        'langchain_core',
        'langgraph'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Missing required packages: {', '.join(missing_packages)}")
        logger.info("📦 Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def create_directories():
    """Create necessary directories for MCP operations"""
    directories = [
        'storage',
        'storage/drafts',
        'storage/published',
        'storage/templates',
        'storage/mcp_data',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Directory created/verified: {directory}")

async def test_mcp_basic():
    """Test basic MCP functionality"""
    try:
        from langgraph_app.mcp_integration import mcp_manager
        
        logger.info("🧪 Testing MCP basic functionality...")
        
        # Test initialization
        await mcp_manager.initialize_servers()
        
        # Test server status
        status = await mcp_manager.get_server_status()
        logger.info(f"📊 MCP Status: {status}")
        
        # Test cleanup
        await mcp_manager.cleanup()
        
        logger.info("✅ MCP basic test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP basic test failed: {e}")
        return False

def main():
    """Main startup function"""
    logger.info("🚀 Starting MCP-enhanced Agentic Writer...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Test MCP basic functionality
    try:
        mcp_test_result = asyncio.run(test_mcp_basic())
        if not mcp_test_result:
            logger.warning("⚠️ MCP test failed, but continuing with limited functionality")
    except Exception as e:
        logger.warning(f"⚠️ MCP test error: {e}, continuing anyway")
    
    # Start the server
    try:
        import uvicorn
        from langgraph_app.integrated_server_mcp import create_mcp_enhanced_app
        
        app = create_mcp_enhanced_app()
        
        logger.info("🌐 Starting FastAPI server with MCP support...")
        logger.info("📍 Server URL: http://localhost:8000")
        logger.info("📊 MCP Status: http://localhost:8000/api/mcp/health")
        logger.info("🔧 MCP Dashboard: http://localhost:3000 (if frontend is running)")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload to prevent issues with MCP
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("📦 Please install missing packages and try again")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()