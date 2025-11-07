# langgraph_app/agents/enhanced_publisher_integrated.py
# FIXED: Generates deterministic metadata and a final publication package.

import logging
from datetime import datetime
from typing import Dict, Any, List
from langgraph_app.core.state import (
    EnrichedContentState,
    AgentType,
    ContentPhase
)

logger = logging.getLogger(__name__)

class EnhancedPublisherAgent:
    """Enterprise publisher that creates a final, distributable content package."""

    def __init__(self):
        self.agent_type = AgentType.PUBLISHER

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Executes the final publication and packaging workflow."""
        logger.info("Starting enterprise publication process...")
        state.log_agent_execution(self.agent_type, {"status": "started"})

        if not state.content or not state.content.strip():
            raise RuntimeError("ENTERPRISE: Publisher received no content to publish.")

        # Generate comprehensive, deterministic metadata
        publication_metadata = self._generate_publication_metadata(state)

        # Prepare the final content package with YAML frontmatter
        final_publication_package = self._prepare_publication_package(
            state.content,
            publication_metadata
        )

        # Update the state with the final packaged content
        state.content = final_publication_package
        state.final_content = final_publication_package # Legacy compatibility
        state.publishing_context = {
            "published_at": datetime.now().isoformat(),
            "publication_metadata": publication_metadata,
            "distribution_channels": self._get_distribution_channels(state),
            "status": "published"
        }

        state.update_phase(ContentPhase.COMPLETED)
        state.status = "completed" # Final status for the graph
        
        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "publication_ready": True,
            "final_package_size": len(final_publication_package)
        })
        logger.info("Publisher finished. Content is packaged and ready for distribution.")
        return state

    def _get_distribution_channels(self, state: EnrichedContentState) -> List[str]:
        """Extracts distribution channels from the template configuration."""
        channels = state.template_config.get("distribution_channels")
        if not channels or not isinstance(channels, list):
            raise RuntimeError(f"ENTERPRISE: Template '{state.template_config.get('id')}' must define 'distribution_channels' as a list.")
        return channels

    def _generate_publication_metadata(self, state: EnrichedContentState) -> Dict[str, Any]:
        """Generates a rich, deterministic metadata object from the state."""
        content_spec = state.content_spec
        style_cfg = state.style_config
        planning = state.planning_output
        seo_context = state.seo_optimization
        word_count = len(state.content.split())

        if not all([content_spec, style_cfg, planning, seo_context]):
            raise RuntimeError("ENTERPRISE: Publisher requires content_spec, style_config, planning_output, and seo_optimization to generate metadata.")

        title = seo_context.title_recommendations[0] if seo_context.title_recommendations else content_spec.topic
        
        return {
            "title": title,
            "description": seo_context.meta_description,
            "author": style_cfg.get("author", "WriterzRoom Enterprise"),
            "publication_date": datetime.now().isoformat(),
            "template_type": state.template_config.get("template_type"),
            "style_profile": style_cfg.get("id"),
            "target_audience": style_cfg.get("audience"),
            "keywords": seo_context.target_keywords,
            "word_count": word_count,
            "estimated_read_time_minutes": max(1, round(word_count / 200)),
            "content_version": "1.0.0",
        }

    def _prepare_publication_package(self, content: str, metadata: Dict[str, Any]) -> str:
        """Formats the final content with a YAML frontmatter header."""
        
        # Build the YAML frontmatter string
        frontmatter_lines = ["---"]
        for key, value in metadata.items():
            if isinstance(value, list):
                frontmatter_lines.append(f"{key}:")
                for item in value:
                    frontmatter_lines.append(f"  - \"{item}\"")
            elif isinstance(value, str):
                 frontmatter_lines.append(f"{key}: \"{value}\"")
            else:
                 frontmatter_lines.append(f"{key}: {value}")
        frontmatter_lines.append("---")
        
        frontmatter = "\n".join(frontmatter_lines)

        return f"{frontmatter}\n\n{content.strip()}"