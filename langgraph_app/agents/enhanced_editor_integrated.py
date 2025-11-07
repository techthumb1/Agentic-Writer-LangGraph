# langgraph_app/agents/enhanced_editor_integrated.py
# FIXED: Performs specific, deterministic edits based on style and planning configs.

import logging
import re
from langgraph_app.core.types import EditedContent
from typing import List, Dict, Any, Tuple
from langgraph_app.core.state import (
    EnrichedContentState,
    AgentType
)

logger = logging.getLogger(__name__)

class EnhancedEditorAgent:
    """Enterprise Editor Agent for deterministic, rule-based content refinement."""

    def __init__(self):
        self.agent_type = AgentType.EDITOR

    def execute(self, state: EnrichedContentState) -> EnrichedContentState:
        """Executes the editing process based on enterprise rules."""
        # Handle both DraftContent object and legacy string format
        if hasattr(state.draft_content, 'body'):
            draft_text = state.draft_content.body
            draft_title = state.draft_content.title
        else:
            draft_text = state.draft_content or state.content
            draft_title = state.content_spec.topic if state.content_spec else "Untitled"
            
        if not draft_text or not draft_text.strip():
            raise RuntimeError("ENTERPRISE: Editor received no content to process.")

        logger.info("Starting enterprise editing process...")
        state.log_agent_execution(self.agent_type, {"status": "started"})

        edited_text, issues_found = self._apply_enterprise_edits(draft_text, state)
        
        # Create proper EditedContent object
        from langgraph_app.core.types import EditedContent
        state.edited_content = EditedContent(
            title=draft_title,
            body=edited_text,
            feedback=issues_found,
            is_approved=True,
            edit_summary=f"Applied {len(issues_found)} edits"
        )
        state.content = edited_text  # Legacy field

        state.log_agent_execution(self.agent_type, {
            "status": "completed",
            "issues_found": len(issues_found),
            "summary_of_changes": issues_found
        })
        logger.info(f"Editor finished, found and addressed {len(issues_found)} issues.")
        return state

    def _apply_enterprise_edits(self, content: str, state: EnrichedContentState) -> Tuple[str, List[str]]:
        """
        Applies a series of deterministic editing passes to the content.
        Returns the edited content and a list of changes made.
        """
        issues_found = []

        # Pass 1: Enforce forbidden patterns from style guide
        content, forbidden_issues = self._enforce_forbidden_patterns(content, state.style_config)
        issues_found.extend(forbidden_issues)

        # Pass 2: Verify required key messages from plan are present
        content, message_issues = self._verify_key_messages(content, state.planning_output)
        issues_found.extend(message_issues)

        # Pass 3: Normalize formatting and remove common LLM artifacts
        content, formatting_issues = self._normalize_formatting(content)
        issues_found.extend(formatting_issues)
        
        # Pass 4: Check for generic phrases
        generic_issues = self._check_for_generic_phrases(content)
        issues_found.extend(generic_issues)

        return content, issues_found

    def _enforce_forbidden_patterns(self, content: str, style_config: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Removes or replaces forbidden words and phrases defined in the style profile."""
        forbidden = style_config.get("forbidden_patterns", [])
        if not forbidden:
            return content, []

        issues = []
        for pattern in forbidden:
            # Using regex for case-insensitive replacement
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Removed forbidden pattern: '{pattern}'")
                content = re.sub(pattern, "", content, flags=re.IGNORECASE)
        return content, issues

    def _verify_key_messages(self, content: str, planning_output: Any) -> Tuple[str, List[str]]:
        """Checks if key messages from the plan are in the text, adding them if missing."""
        key_messages = getattr(planning_output, "key_messages", [])
        if not key_messages:
            return content, []

        issues = []
        for message in key_messages:
            if message.lower() not in content.lower():
                issues.append(f"Added missing key message: '{message}'")
                # Append the missing message to the end in a "Key Takeaways" section
                if "## Key Takeaways" not in content:
                    content += "\n\n## Key Takeaways"
                content += f"\n- {message}"
        return content, issues

    def _normalize_formatting(self, content: str) -> Tuple[str, List[str]]:
        """Cleans up common formatting issues and LLM artifacts."""
        issues = []
        
        # Remove conversational openings/closings if they exist
        artifacts = [
            r"^\s*Here is the content you requested:",
            r"^\s*Certainly, here is the article:",
            r"I hope this helps! Let me know if you have any other questions\.$",
        ]
        original_len = len(content)
        for artifact in artifacts:
            content = re.sub(artifact, "", content, flags=re.IGNORECASE | re.MULTILINE).strip()

        if len(content) < original_len:
            issues.append("Removed conversational LLM artifacts.")
        
        # Standardize spacing
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content, issues

    def _check_for_generic_phrases(self, content: str) -> List[str]:
        """Identifies use of generic, unoriginal phrases."""
        generic_phrases = [
            "in conclusion", "in today's fast-paced world", "it is important to note",
            "the world of", "as mentioned earlier", "last but not least"
        ]
        issues = []
        for phrase in generic_phrases:
            if phrase in content.lower():
                issues.append(f"Detected generic phrase: '{phrase}'")
        return issues