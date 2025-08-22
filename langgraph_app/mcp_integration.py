# File: langgraph_app/mcp_integration.py
"""
Complete MCP Integration for WriterzRoom
Connects agents through MCP protocol with proper coordination
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple MCP Manager for compatibility
class MCPManager:
    """Simple MCP Manager for handling MCP operations"""
    
    def __init__(self):
        self.initialized = False
        self.capabilities = []
    
    async def initialize(self):
        """Initialize MCP capabilities"""
        try:
            self.capabilities = ["content_generation", "agent_coordination"]
            self.initialized = True
            logger.info("MCP capabilities initialized successfully")
            return True
        except Exception as e:
            logger.error(f"MCP initialization failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup MCP resources"""
        self.initialized = False
        logger.info("MCP cleanup completed")

# Global MCP manager instance
mcp_manager = MCPManager()

@dataclass
class MCPGenerationRequest:
    """MCP-specific generation request with enhanced options"""
    topic: str
    audience: str
    template_type: str
    platform: str = "web"
    complexity_level: int = 5
    innovation_level: str = "balanced"
    research_depth: str = "standard"  # basic, standard, deep
    priority: str = "normal"  # low, normal, high, urgent
    business_context: Dict[str, Any] = None
    constraints: Dict[str, Any] = None
    mcp_options: Dict[str, Any] = None

    def __post_init__(self):
        if self.business_context is None:
            self.business_context = {}
        if self.constraints is None:
            self.constraints = {}
        if self.mcp_options is None:
            self.mcp_options = {
                "enable_memory": True,
                "enable_tool_discovery": True,
                "enable_enhanced_research": True,
                "coordination_level": "full"
            }

class MCPGenerationResponse(BaseModel):
    """Standardized MCP generation response"""
    content: str
    metadata: Dict[str, Any]
    generation_stats: Dict[str, Any]
    agent_execution_log: List[Dict[str, Any]]
    mcp_enhancements: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class MCPContentOrchestrator:
    """
    Main MCP orchestrator that coordinates all agents through MCP protocol
    """
    
    def __init__(self):
        self.content_graph = None
        self.memory_store = {}
        self.tool_registry = {}
        
        # Initialize MCP capabilities
        self._initialize_mcp_capabilities()
    
    def _initialize_mcp_capabilities(self):
        """Initialize MCP server and capabilities"""
        try:
            # Import dynamically to avoid circular imports
            try:
                from .enhanced_model_registry import EnhancedModelRegistry
                self.model_registry = EnhancedModelRegistry()
            except ImportError:
                logger.warning("Enhanced model registry not available")
                self.model_registry = None
            
            # Initialize content graph
            try:
                from .mcp_server_extension import enhanced_mcp_manager
                self.content_graph = enhanced_mcp_manager
            except ImportError:
                logger.warning("MCP Enhanced Graph not available")
                self.content_graph = None
                logger.info("MCP capabilities initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize MCP capabilities: {e}")
        except Exception as e:
            logger.error(f"Error during MCP capability initialization: {e}")
    
    def _normalize_mcp_payload(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize arbitrary MCP executor output into a stable, evidence-first shape.
        Returns:
          {
            "executed_tools": [str],
            "sources": [{"title": str, "url": str, "excerpt": str}],
            "facts": [str],
            "data_summaries": [Any],   # optional
            "code_findings": [Any]     # optional
          }
        """
        def _coerce_sources(maybe_sources) -> List[Dict[str, str]]:
            out = []
            if isinstance(maybe_sources, list):
                for s in maybe_sources:
                    if isinstance(s, dict):
                        title = str(s.get("title", "") or "")
                        url = str(s.get("url", "") or "")
                        excerpt = str(s.get("excerpt", "") or s.get("summary", "") or "")
                    else:
                        # allow plain URL/string
                        title, url, excerpt = "", str(s), ""
                    if title or url:
                        out.append({"title": title, "url": url, "excerpt": excerpt})
            return out

        def _extend_list(dst: List[Any], src: Any, cast=str):
            if isinstance(src, list):
                for v in src:
                    try:
                        dst.append(cast(v) if cast else v)
                    except Exception:
                        dst.append(v)

        executed_tools: List[str] = []
        sources: List[Dict[str, str]] = []
        facts: List[str] = []
        data_summaries: List[Any] = []
        code_findings: List[Any] = []

        # 1) Mine from execution logs (most common place tools/results live)
        log = raw.get("agent_execution_log") or raw.get("execution_log") or raw.get("logs") or []
        if isinstance(log, list):
            for entry in log:
                if not isinstance(entry, dict):
                    continue
                t = entry.get("tool") or entry.get("name") or entry.get("executor")
                if t:
                    executed_tools.append(str(t))

                out = entry.get("output") or entry.get("result") or {}
                if isinstance(out, dict):
                    # sources in various keys
                    for k in ("sources", "references", "citations"):
                        _extend = _coerce_sources(out.get(k))
                        if _extend:
                            sources.extend(_extend)
                    # facts / findings
                    for k in ("facts", "key_facts", "findings"):
                        _extend_list(facts, out.get(k), cast=str)
                    # structured summaries / tables
                    for k in ("data_summaries", "tables", "stats"):
                        _extend_list(data_summaries, out.get(k), cast=None)
                    # code-related
                    for k in ("code_findings", "snippets", "notebook_outputs"):
                        _extend_list(code_findings, out.get(k), cast=None)

        # 2) Mine from top-level fields if present
        for k in ("sources", "references", "citations"):
            sources.extend(_coerce_sources(raw.get(k)))
        for k in ("facts", "key_facts", "findings"):
            _extend_list(facts, raw.get(k), cast=str)
        for k in ("data_summaries", "tables", "stats"):
            _extend_list(data_summaries, raw.get(k), cast=None)
        for k in ("code_findings", "snippets", "notebook_outputs"):
            _extend_list(code_findings, raw.get(k), cast=None)

        # 3) Deduplicate conservatively
        executed_tools = list(dict.fromkeys([t for t in executed_tools if t]))
        # dedupe sources primarily by URL, then title
        seen = set()
        dedup_sources = []
        for s in sources:
            key = (s.get("url", ""), s.get("title", ""))
            if key in seen:
                continue
            seen.add(key)
            dedup_sources.append({
                "title": s.get("title", "") or "",
                "url": s.get("url", "") or "",
                "excerpt": s.get("excerpt", "") or ""
            })

        normalized = {
            "executed_tools": executed_tools,
            "sources": dedup_sources,
            "facts": facts,
            "data_summaries": data_summaries,
            "code_findings": code_findings
        }

        logger.info(
            "MCP normalization summary | tools=%d, sources=%d, facts=%d, data_summaries=%d, code_findings=%d",
            len(normalized["executed_tools"]),
            len(normalized["sources"]),
            len(normalized["facts"]),
            len(normalized["data_summaries"]),
            len(normalized["code_findings"]),
        )
        return normalized


async def execute_mcp_enhanced_generation(
    self,
    request_id=None,
    template_config=None,
    style_config=None,
    app_state=None,
    mcp_options=None
):
    """
    Main entry point for MCP-enhanced content generation.
    This now returns a normalized evidence payload:
      executed_tools, sources[{title,url,excerpt}], facts, data_summaries?, code_findings?
    """
    logger.info("Starting MCP enhanced generation")
    try:
        if not self.content_graph:
            logger.error("MCP Enhanced Graph not initialized, cannot proceed.")
            raise RuntimeError("MCP Enhanced Graph not initialized, cannot proceed.")
        # Import state components lazily to avoid circular deps
        try:
            from .core.enriched_content_state import (
                EnrichedContentState,
                ContentSpecification,
                ContentPhase
            )
        except ImportError as e:
            logger.error(f"Could not import state components: {e}")
            raise RuntimeError("MCP integration failed due to missing state components.") from e
        # Build ContentSpecification from provided configs (robust to ints/strings)
        if template_config and style_config:
            raw_level = template_config.get('complexity_level', 5)
            level_map = {
                'very_low': 1, 'low': 2, 'basic': 3,
                'medium': 5, 'high': 7, 'advanced': 8, 'expert': 9
            }
            if isinstance(raw_level, (int,)) or (isinstance(raw_level, str) and raw_level.isdigit()):
                complexity_level = int(raw_level)
            else:
                complexity_level = level_map.get(str(raw_level).lower(), 5)
            content_spec = ContentSpecification(
                template_type=template_config.get('name', 'general'),
                topic=template_config.get('topic', template_config.get('name', 'General Content')),
                audience=style_config.get('audience', 'general'),
                platform=template_config.get('platform', 'web'),
                complexity_level=complexity_level,
                innovation_level=template_config.get('innovation_level', 'balanced'),
                business_context=template_config.get('business_context', {}),
                constraints=template_config.get('constraints', {})
            )
        else:
            content_spec = ContentSpecification(
                template_type='general',
                topic='General Content',
                audience='general',
                platform='web',
                complexity_level=5,
                innovation_level='balanced'
            )
        initial_state = EnrichedContentState(
            content_spec=content_spec,
            current_phase=ContentPhase.PLANNING
        )
        # Execute via MCP graph (may return diverse shapes)
        raw = await self.content_graph.execute_coordinated_generation(
            initial_state,
            mcp_options=mcp_options or {}
        ) or {}
        # Normalize to evidence-first payload
        normalized = self._normalize_mcp_payload(raw)
        # Return ONLY the normalized evidence payload for downstream gating
        return normalized
    except Exception as e:
        logger.error(f"MCP generation failed: {e}")
        # Return a valid normalized empty payload on failure
        return {
            "executed_tools": [],
            "sources": [],
            "facts": [],
            "data_summaries": [],
            "code_findings": [],
            "error": f"Generation failed: {str(e)}"
        }
def get_server_status(self) -> Dict[str, Any]:
    """Get current MCP server status"""
    return {
        "status": "running",
        "capabilities": {
            "model_registry": bool(getattr(self, 'model_registry', None)),
            "content_graph": bool(self.content_graph),
            "memory_store": len(self.memory_store),
            "tool_registry": len(self.tool_registry)
        },
        "uptime": datetime.now().isoformat()
    }

# Global MCP orchestrator instance
mcp_orchestrator = MCPContentOrchestrator()

# Main function for compatibility with integrated server
async def execute_mcp_enhanced_generation(
    request_id=None,
    template_config=None,
    style_config=None,
    app_state=None,
    mcp_options=None
):
    """Convenience function for executing MCP enhanced generation"""
    return await mcp_orchestrator.execute_mcp_enhanced_generation(
        request_id=request_id,
        template_config=template_config,
        style_config=style_config,
        app_state=app_state,
        mcp_options=mcp_options,
    )


# Export main components
__all__ = [
    'MCPGenerationRequest',
    'MCPGenerationResponse', 
    'MCPContentOrchestrator',
    'mcp_orchestrator',
    'mcp_manager',
    'execute_mcp_enhanced_generation'
]