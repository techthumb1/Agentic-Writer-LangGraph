import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langgraph_app.core.enriched_content_state import (
    EnrichedContentState,
    ContentSpec,
    ResearchFindings,
    ContentPhase
)
from langgraph_app.mcp_enhanced_graph import MCPEnhancedContentGraph

# Create graph instance
graph_instance = MCPEnhancedContentGraph()
graph = graph_instance.graph