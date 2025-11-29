# src/langgraph_app/graph/workflow.py
"""
Workflow initialization and execution utilities.
Provides a singleton instance of the compiled graph.
"""

import logging
from typing import Optional

from .builder import build_content_generation_graph

logger = logging.getLogger("writerzroom.graph.workflow")

# Singleton compiled graph instance
_compiled_graph: Optional[object] = None


def get_compiled_graph():
    """
    Returns the singleton compiled LangGraph instance.
    Builds it on first call, then caches for subsequent calls.
    """
    global _compiled_graph
    
    if _compiled_graph is None:
        logger.info("Initializing content generation graph (first call)...")
        _compiled_graph = build_content_generation_graph()
        logger.info("✅ Graph compiled and cached")
    
    return _compiled_graph


# For backward compatibility with existing imports
main_graph = get_compiled_graph()