# src/langgraph_app/core/state.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from .types import (
    AgentExecutionEvent,
    AgentType,
    CodeGenerationContext,
    ContentPhase,
    ContentSpec,
    DraftContent,
    EditedContent,
    FormattedContent,
    FormattingRequirements,
    GeneratedImage,
    GenerationStatus,
    PlanningOutput,
    ResearchFindings,
    SeoAnalysis,
    SEOOptimizationContext,
)


@dataclass
class EnrichedContentState:
    """
    Central, serializable state passed through the LangGraph workflow.
    Intentionally plain (dataclass) for testability and deterministic behavior.
    """
    # Validated configurations (raw dicts from schemas)
    template_config: Dict[str, Any] = field(default_factory=dict)
    style_config: Dict[str, Any] = field(default_factory=dict)

    # Dynamic inputs / overrides
    dynamic_parameters: Dict[str, Any] = field(default_factory=dict)

    # Core evolving artifacts
    content_spec: Optional[ContentSpec] = None
    planning_output: Optional[PlanningOutput] = None
    research_findings: Optional[ResearchFindings] = None
    formatting_requirements: Optional[FormattingRequirements] = None
    seo_optimization: Optional[SEOOptimizationContext] = None
    code_generation: Optional[CodeGenerationContext] = None

    # Content artifacts at different stages
    draft_content: Optional[DraftContent] = None
    edited_content: Optional[EditedContent] = None
    formatted_content: Optional[FormattedContent] = None
    seo_analysis: Optional[SeoAnalysis] = None

    # Content buffers (legacy - for backward compatibility)
    content: str = ""
    final_content: str = ""

    # Generated assets
    generated_images: List[GeneratedImage] = field(default_factory=list)
    generated_code: List[str] = field(default_factory=list)

    # Optional contexts for specific agents
    writing_context: Dict[str, Any] = field(default_factory=dict)
    publishing_context: Dict[str, Any] = field(default_factory=dict)

    # Execution bookkeeping
    status: GenerationStatus = GenerationStatus.INIT
    phase: ContentPhase = ContentPhase.INIT
    agent_execution_log: List[AgentExecutionEvent] = field(default_factory=list)

    # Legacy compatibility (kept temporarily; prefer planning_output)
    research_plan: Optional[PlanningOutput] = None

    # Current date for time-sensitive content
    current_date: str = datetime.now().isoformat()
    # --- Utility methods -----------------------------------------------------------------------

    def update_phase(self, phase: ContentPhase) -> None:
        self.phase = phase

    def log_agent_execution(self, agent: AgentType, data: Dict[str, Any]) -> None:
        event = AgentExecutionEvent(
            agent=agent,
            data=data,
            timestamp=datetime.now().isoformat()
        )
        self.agent_execution_log.append(event)

    # Useful in tests
    def to_dict(self) -> Dict[str, Any]:
        # Dataclasses inside are already dataclasses; asdict will recurse.
        return asdict(self)