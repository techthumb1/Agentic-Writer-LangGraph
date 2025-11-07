# langgraph_app/agents/enhanced_image_agent_integrated.py
# FIXED: Conditional execution and deterministic markdown placeholder generation.

import logging
import re
from langgraph_app.core.state import EnrichedContentState, AgentType

logger = logging.getLogger(__name__)

class EnhancedImageAgent:
    """
    Enterprise Image Agent that conditionally adds image placeholders to content.
    """

    def __init__(self):
        self.agent_type = AgentType.IMAGE

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Executes image placeholder generation if required by the template."""
        template_config = state.template_config
        
        # This agent is conditional.
        image_config = template_config.get("image_generation_config")
        if not image_config or not image_config.get("enabled", False):
            logger.info("Image agent skipped: not enabled in template.")
            state.log_agent_execution(self.agent_type, {"status": "skipped"})
            return state

        logger.info("Executing Image Agent...")
        state.log_agent_execution(self.agent_type, {"status": "started"})

        content = state.draft_content
        if not content:
            logger.warning("Image agent has no content to enhance.")
            state.log_agent_execution(self.agent_type, {"status": "skipped_no_content"})
            return state

        # Add image placeholders to the content
        enhanced_content = self._add_image_placeholders(content, image_config, state.content_spec.topic)
        
        state.content = enhanced_content
        state.draft_content = enhanced_content

        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "placeholders_added": enhanced_content.count("![")
        })
        logger.info(f"Image Agent finished, added {enhanced_content.count('![')} placeholders.")
        return state

    def _add_image_placeholders(self, content: str, image_config: dict, topic: str) -> str:
        """
        Injects markdown image placeholders with descriptive alt text for generation.
        """
        placements = image_config.get("placements", [])
        if not placements:
            return content

        for placement in placements:
            anchor_text = placement.get("after_section")
            prompt = placement.get("prompt").format(topic=topic) # Allows dynamic prompts like "A diagram of {topic}"
            style = image_config.get("style", "professional")

            if not anchor_text or not prompt:
                continue
                
            # Create the descriptive alt text for the image generation service
            alt_text = f"Image generation prompt: {prompt}, style: {style}"
            
            # Create the markdown placeholder
            image_placeholder = f"![{alt_text}]({style}-image-placeholder.jpg)"

            # Insert the placeholder after the specified section header
            # Using regex to find the header and insert after it.
            # This looks for a header line and inserts the placeholder before the next header or end of content.
            pattern = re.compile(rf"(#+\s*{re.escape(anchor_text)}\s*\n)(.*?)(?=\n#+|$)", re.DOTALL)
            
            # The replacement function inserts the image placeholder after the found section
            def repl(match):
                header = match.group(1)
                section_content = match.group(2)
                return f"{header}{section_content}\n\n{image_placeholder}\n\n"

            content, count = re.subn(pattern, repl, content)
            if count == 0:
                logger.warning(f"Could not find anchor section '{anchor_text}' to insert image.")

        return content