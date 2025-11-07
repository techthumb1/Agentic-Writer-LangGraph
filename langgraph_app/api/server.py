# src/langgraph_app/api/server.py
"""
WriterzRoom API — Refactored Enterprise Edition
Main FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Core imports for lifespan
from ..core.config_manager import ConfigManager, ConfigManagerError

# Import modular routers
from .routes import generation, status, configuration, content, dashboard

logger = logging.getLogger("writerzroom.server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: Load and validate configurations on startup.
    """
    logger.info("Starting WriterzRoom API — Refactored Enterprise Mode")
    try:
        # Locate the 'data' directory relative to this file's parent's parent
        # src/langgraph_app/api -> src/langgraph_app -> src -> /
        base_dir = Path(__file__).resolve().parents[3]
        
        # Initialize the ConfigManager
        # It will find data/content_templates and data/style_profiles
        app.state.config_manager = ConfigManager(base_dir=base_dir)
        
        logger.info("✅ ConfigManager initialized and all configurations validated.")
        logger.info(f"Loaded {len(app.state.config_manager.list_templates())} templates.")
        logger.info(f"Loaded {len(app.state.config_manager.list_style_profiles())} style profiles.")
        
    except ConfigManagerError as e:
        logger.error(f"❌ CRITICAL: Failed to initialize ConfigManager. {e}")
        # This will stop the application from starting
        raise RuntimeError(f"Could not start server: {e}") from e

    # Server is running
    yield
    
    # Shutdown
    logger.info("Shutting down WriterzRoom API.")


def create_app() -> FastAPI:
    """
    Factory function to create the FastAPI app.
    """
    app = FastAPI(
        title="WriterzRoom Orchestrator",
        version="2.0",
        lifespan=lifespan
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include all the modular routers
    app.include_router(generation.router, prefix="/api", tags=["Generation"])
    app.include_router(status.router, prefix="/api/generate", tags=["Status"])
    app.include_router(configuration.router, prefix="/api", tags=["Configuration"])
    
    # Include placeholder routers for future implementation
    app.include_router(content.router, prefix="/api/content", tags=["Content (Stub)"])
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard (Stub)"])
    
    logger.info("API routers included.")
    return app

app = create_app()

if __name__ == "__main__":
    # For direct running (e.g., debugging)
    uvicorn.run(app, host="0.0.0.0", port=8000)