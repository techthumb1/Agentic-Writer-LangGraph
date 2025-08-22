# langgraph_app/config/settings.py
"""
Configuration settings for WriterzRoom API
Centralizes all environment variables and system configuration
"""

import os
import logging
from typing import Optional, Tuple, NoReturn, List

logger = logging.getLogger(__name__)

def _fatal(msg: str, *, exc: Optional[BaseException] = None) -> NoReturn:
    """Log a fatal error and terminate the process (enterprise strict)."""
    if exc:
        logger.error("%s | exception=%s: %s", msg, type(exc).__name__, exc)
    else:
        logger.error("%s", msg)
    raise SystemExit(msg)

class Settings:
    """Centralized configuration settings."""
    
    def __init__(self):
        # Environment
        self.ENVIRONMENT = os.getenv("NODE_ENV", "production")
        
        # Required environment variables
        self.REQUIRED_ENV_VARS: Tuple[str, ...] = ("LANGGRAPH_API_KEY",)
        self._validate_required_env_vars()
        
        # API Keys
        self.API_KEY = os.environ["LANGGRAPH_API_KEY"]
        self.FASTAPI_API_KEY = os.getenv("FASTAPI_API_KEY", self.API_KEY)
        
        # Server configuration
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", 8000))
        
        # Evidence collection configuration
        self.EVIDENCE_CONFIG = {
            "minimum_required": int(os.getenv("MIN_EVIDENCE_REQUIRED", "1")),
            "enable_fallback": os.getenv("ENABLE_EVIDENCE_FALLBACK", "true").lower() == "true",
            "enable_synthetic": os.getenv("ENABLE_SYNTHETIC_EVIDENCE", "true").lower() == "true",
            "debug_evidence": os.getenv("DEBUG_EVIDENCE_COLLECTION", "false").lower() == "true"
        }
        
        # Path configuration
        self.TEMPLATE_PATHS = self._get_template_paths()
        self.STYLE_PROFILE_PATHS = self._get_style_profile_paths()
        
        # Feature flags
        self.FEATURES = {
            "mcp_integration": True,
            "universal_system": True,
            "batch_generation": True,
            "analytics": True,
            "webhooks": True,
            "admin_endpoints": self.ENVIRONMENT == "development",
            "debug_endpoints": self.ENVIRONMENT == "development"
        }
        
        # CORS configuration
        self.CORS_ORIGINS = self._get_cors_origins()
        
        # Logging configuration
        self._setup_logging()
    
    def _validate_required_env_vars(self):
        """Validate that all required environment variables are set."""
        missing = [k for k in self.REQUIRED_ENV_VARS if not os.getenv(k)]
        if missing:
            _fatal(f"ENTERPRISE FAILURE: Missing required environment variables: {missing}")
    
    def _get_template_paths(self) -> List[str]:
        """Get ordered list of template directory paths - ENTERPRISE: Must exist."""
        paths = [
            "data/content_templates",
            "../data/content_templates",
            "frontend/content-templates",
            "../frontend/content-templates",
            "content-templates"
        ]
        existing_paths = [path for path in paths if os.path.exists(path)]
        
        if not existing_paths:
            raise SystemExit("ENTERPRISE MODE: No template directories found. Required paths: " + ", ".join(paths))
        
        logger.info(f"Template paths found: {existing_paths}")
        return existing_paths
    
    def _get_style_profile_paths(self) -> List[str]:
        """Get ordered list of style profile directory paths - ENTERPRISE: Must exist."""
        paths = [
            "data/style_profiles",
            "../data/style_profiles",
            "frontend/style-profiles",
            "../frontend/style-profiles",
            "style-profiles"
        ]
        existing_paths = [path for path in paths if os.path.exists(path)]
        
        if not existing_paths:
            raise SystemExit("ENTERPRISE MODE: No style profile directories found. Required paths: " + ", ".join(paths))
        
        logger.info(f"Style profile paths found: {existing_paths}")
        return existing_paths
    
    def _get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.ENVIRONMENT == "production":
            return ["https://yourdomain.com"]
        else:
            return [
                "http://localhost:3000", 
                "http://frontend:3000", 
                "https://*.vercel.app"
            ]
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    
    def get_server_config(self) -> dict:
        """Get server configuration for uvicorn."""
        return {
            "host": self.HOST,
            "port": self.PORT,
            "reload": self.ENVIRONMENT == "development",
            "log_level": "info",
            "access_log": True
        }
    
    def validate_enterprise_requirements(self) -> dict:
        """Validate all enterprise requirements are met."""
        validations = []
        
        # Environment variables
        validations.append({
            "name": "environment_variables",
            "status": all(os.getenv(var) for var in self.REQUIRED_ENV_VARS),
            "details": f"Required vars: {self.REQUIRED_ENV_VARS}"
        })
        
        # Paths
        validations.append({
            "name": "file_paths",
            "status": bool(self.TEMPLATE_PATHS and self.STYLE_PROFILE_PATHS),
            "details": f"Template paths: {len(self.TEMPLATE_PATHS)}, Profile paths: {len(self.STYLE_PROFILE_PATHS)}"
        })
        
        # API Keys
        validations.append({
            "name": "api_keys",
            "status": bool(self.API_KEY and self.FASTAPI_API_KEY),
            "details": "API keys configured"
        })
        
        failed_validations = [v for v in validations if not v["status"]]
        if failed_validations:
            logger.error(f"Enterprise validation failed: {failed_validations}")
        
        return {
            "validations": validations,
            "all_passed": len(failed_validations) == 0,
            "failed_count": len(failed_validations)
        }

# Global settings instance
settings = Settings()