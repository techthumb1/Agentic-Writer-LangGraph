# langgraph_app/agents/enhanced_code_agent_integrated.py
# FIXED: Deterministic execution and proper markdown code block formatting.

import logging
import re
from typing import List
from langgraph_app.core.state import (
    EnrichedContentState,
    AgentType,
    CodeGenerationContext
)

logger = logging.getLogger(__name__)

class EnhancedCodeAgent:
    """
    Enterprise Code Agent for conditionally adding and formatting code examples.
    """

    def __init__(self):
        self.agent_type = AgentType.CODE

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Executes code generation and formatting if required by the template."""
        template_config = state.template_config
        
        # This agent is conditional and only runs if the template explicitly requires it.
        if not template_config.get("requirements", {}).get("requires_code", False):
            logger.info("Code agent skipped: template does not require code.")
            state.log_agent_execution(self.agent_type, {"status": "skipped"})
            return state

        logger.info("Executing Code Agent...")
        state.log_agent_execution(self.agent_type, {"status": "started"})
        
        content = state.draft_content
        if not content:
            logger.warning("Code agent has no content to enhance.")
            state.log_agent_execution(self.agent_type, {"status": "skipped_no_content"})
            return state

        context = self._create_code_context(template_config)
        state.code_generation = context

        # Enhance the content with formatted code blocks
        enhanced_content = self._add_formatted_code_blocks(content, context)

        state.content = enhanced_content
        state.draft_content = enhanced_content
        state.generated_code = self._extract_code_from_content(enhanced_content)

        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "code_blocks_added": len(state.generated_code),
        })
        logger.info(f"Code Agent finished, added {len(state.generated_code)} code blocks.")
        return state

    def _create_code_context(self, template_config: dict) -> CodeGenerationContext:
        """Creates code generation context directly from template config."""
        code_cfg = template_config.get("code_generation_config")
        if not code_cfg or not isinstance(code_cfg, dict):
            raise RuntimeError(f"ENTERPRISE: Template '{template_config.get('id')}' requires code but is missing 'code_generation_config'.")
            
        return CodeGenerationContext(
            programming_languages=code_cfg.get("languages", ["python"]),
            documentation_style=code_cfg.get("style", "technical"),
            code_examples_needed=code_cfg.get("examples", []),
            generation_confidence=0.95
        )

    def _add_formatted_code_blocks(self, content: str, context: CodeGenerationContext) -> str:
        """Finds placeholders and replaces them with formatted code blocks."""
        for example_spec in context.code_examples_needed:
            placeholder = example_spec.get("placeholder")
            code_type = example_spec.get("type")
            lang = context.programming_languages[0] # Use the primary language

            if not placeholder:
                continue

            # Generate a representative code snippet
            code_snippet = self._generate_code_snippet(code_type, lang)

            # Build the fully formatted markdown block
            formatted_block = f"```{lang}\n{code_snippet}\n```"

            # Replace the placeholder in the content
            if placeholder in content:
                content = content.replace(placeholder, formatted_block)
        
        return content

    def _generate_code_snippet(self, code_type: str, lang: str) -> str:
        """Generates a placeholder code snippet based on type."""
        # This is a deterministic placeholder. A real implementation would use an LLM
        # or a library of pre-defined snippets.
        snippets = {
            "installation": {
                "python": "pip install your-package-name",
                "javascript": "npm install your-package-name",
                "bash": "curl -sSL https://install.example.com | bash"
            },
            "initialization": {
                "python": "from your_package import Client\n\nclient = Client(api_key=\"YOUR_API_KEY\")",
                "javascript": "const { Client } = require('your-package-name');\n\nconst client = new Client({ apiKey: 'YOUR_API_KEY' });"
            },
            "function_call": {
                "python": "result = client.feature.get(item_id=\"12345\")\nprint(result)",
                "javascript": "client.feature.get({ itemId: '12345' })\n  .then(result => console.log(result));"
            }
        }
        return snippets.get(code_type, {}).get(lang, f"# Code for '{code_type}' in '{lang}' goes here.")

    def _extract_code_from_content(self, content: str) -> List[str]:
        """Extracts all markdown code blocks from the final content."""
        return re.findall(r"```(?:\w+)?\n(.*?)\n```", content, re.DOTALL)