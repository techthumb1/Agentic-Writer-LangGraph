# langgraph_app/integrated_server_mcp.py
import os
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Import your modules
from .mcp_integration import mcp_manager, mcp_context
from .template_loader import template_loader
from .style_profile_loader import style_profile_loader
from .mcp_enhanced_graph import execute_mcp_enhanced_generation

# Configuration
API_KEY = os.getenv("LANGGRAPH_API_KEY", "prod_api_key_2025_secure_content_gen_v1")
ENVIRONMENT = os.getenv("NODE_ENV", "development")

# Security dependency that allows optional auth in development
async def get_api_key(request: Request) -> Optional[str]:
    """Extract API key from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None

async def verify_api_key(api_key: Optional[str] = Depends(get_api_key)):
    """Verify API key - optional in development, required in production"""
    if ENVIRONMENT == "production":
        if not api_key or api_key != API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key"
            )
    # In development, auth is optional
    return True

# Lifespan manager with MCP
@asynccontextmanager
async def lifespan_with_mcp(app: FastAPI):
    """Manage MCP lifecycle"""
    try:
        # Initialize MCP
        await mcp_manager.initialize_servers()
        logger.info("✅ MCP servers initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ MCP initialization failed (continuing without MCP): {e}")
    
    yield
    
    # Cleanup
    try:
        await mcp_manager.cleanup()
        logger.info("✅ MCP cleanup completed")
    except Exception as e:
        logger.error(f"MCP cleanup error: {e}")

def create_mcp_enhanced_app():
    """Create FastAPI app with MCP integration"""
    
    app = FastAPI(
        title="Agentic Writer API with MCP",
        version="2.0.0",
        lifespan=lifespan_with_mcp
    )
    
    # Configure CORS for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    
    # Health check (no auth)
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "environment": ENVIRONMENT,
            "mcp_enabled": bool(mcp_manager.active_connections)
        }
    
    # Templates endpoint with optional auth
    @app.get("/api/templates")
    async def get_templates(authenticated: bool = Depends(verify_api_key)):
        """Get templates with MCP enhancement"""
        try:
            # Load templates from file system
            template_names = template_loader.list_templates()
            templates = []
            
            for name in template_names:
                template_data = template_loader.get_template(name)
                if template_data:
                    templates.append({
                        "id": name,
                        "name": template_data.get("name", name.replace("_", " ").title()),
                        "description": template_data.get("description", ""),
                        "category": template_data.get("category", "general"),
                        "parameters": template_data.get("parameters", {})
                    })
            
            # Add MCP capabilities info
            return JSONResponse(content={
                "templates": templates,
                "count": len(templates),
                "mcp_enhanced": bool(mcp_manager.active_connections),
                "capabilities": list(mcp_manager.tools.keys()) if mcp_manager.active_connections else []
            })
            
        except Exception as e:
            logger.error(f"❌ Templates loading failed: {e}")
            # Return fallback templates
            return JSONResponse(content={
                "templates": [
                    {
                        "id": "blog_post",
                        "name": "Blog Post",
                        "description": "Standard blog post format",
                        "category": "content"
                    },
                    {
                        "id": "technical_tutorial",
                        "name": "Technical Tutorial", 
                        "description": "Step-by-step technical guide",
                        "category": "technical"
                    },
                    {
                        "id": "market_analysis",
                        "name": "Market Analysis",
                        "description": "Market research and analysis",
                        "category": "business"
                    }
                ],
                "count": 3,
                "mcp_enhanced": False,
                "capabilities": []
            })
    
    # Style profiles endpoint with optional auth
    @app.get("/api/style-profiles")
    async def get_style_profiles(authenticated: bool = Depends(verify_api_key)):
        """Get style profiles"""
        try:
            profile_names = style_profile_loader.list_profiles()
            profiles = []
            
            for name in profile_names:
                profile_data = style_profile_loader.get_profile(name)
                if profile_data:
                    profiles.append({
                        "id": name,
                        "name": profile_data.get("name", name.replace("_", " ").title()),
                        "description": profile_data.get("description", ""),
                        "tone": profile_data.get("tone", "neutral"),
                        "characteristics": profile_data.get("characteristics", [])
                    })
            
            return JSONResponse(content={
                "profiles": profiles,
                "count": len(profiles)
            })
            
        except Exception as e:
            logger.error(f"❌ Style profiles loading failed: {e}")
            # Return fallback profiles
            return JSONResponse(content={
                "profiles": [
                    {
                        "id": "professional",
                        "name": "Professional",
                        "description": "Formal business tone",
                        "tone": "formal"
                    },
                    {
                        "id": "casual",
                        "name": "Casual",
                        "description": "Friendly conversational tone",
                        "tone": "informal"
                    },
                    {
                        "id": "academic",
                        "name": "Academic",
                        "description": "Scholarly and precise",
                        "tone": "formal"
                    }
                ],
                "count": 3
            })
    
    # MCP status endpoint (public)
    @app.get("/api/mcp/status")
    async def mcp_status():
        """Get MCP server status"""
        return await mcp_manager.get_server_status()
    
    # MCP tools endpoint
    @app.get("/api/mcp/tools")
    async def mcp_tools(authenticated: bool = Depends(verify_api_key)):
        """Get available MCP tools"""
        return await mcp_manager.get_available_tools()
    
    # Content generation with MCP
    @app.post("/api/generate")
    async def generate_content(
        request: Request,
        authenticated: bool = Depends(verify_api_key)
    ):
        """Generate content using MCP-enhanced workflow"""
        try:
            data = await request.json()
            
            # Add request ID if not present
            if "requestId" not in data:
                import uuid
                data["requestId"] = str(uuid.uuid4())
            
            # Execute MCP-enhanced generation
            result = await execute_mcp_enhanced_generation(data)
            
            return JSONResponse(content=result)
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

# Create the app instance
app = create_mcp_enhanced_app()

if __name__ == "__main__":
    import uvicorn
    
    # Server configuration
    config = {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
        "log_level": "info",
        "access_log": True,
    }
    
    logger.info("🚀 Starting Agentic Writer with MCP support...")
    logger.info(f"📡 Server available at http://localhost:{config['port']}")
    logger.info("🔧 MCP Dashboard: http://localhost:8000/api/mcp/status")
    logger.info(f"🔐 Environment: {ENVIRONMENT}")
    logger.info(f"🔑 Auth required: {'Yes' if ENVIRONMENT == 'production' else 'No (dev mode)'}")
    
    # Run the server
    uvicorn.run(app, **config)