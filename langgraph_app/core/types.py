# src/langgraph_app/core/types.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# === Enums ======================================================================================

class AgentType(str, Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    CALL_WRITER = "call_writer"
    WRITER = "writer"
    EDITOR = "editor"
    FORMATTER = "formatter"
    SEO = "seo"
    IMAGE = "image"
    CODE = "code"
    PUBLISHER = "publisher"


class ContentPhase(str, Enum):
    INIT = "init"
    PLANNING = "planning"
    RESEARCH = "research"
    WRITING = "writing"
    EDITING = "editing"
    IMAGE_GENERATION = "image_generation"
    FORMATTING = "formatting"
    SEO_ANALYSIS = "seo_analysis"
    OPTIMIZATION = "optimization"
    PUBLISHING = "publishing"
    COMPLETE = "complete"
    COMPLETED = "completed"


class GenerationStatus(str, Enum):
    INIT = "init"
    PLANNING = "planning"
    RESEARCHING = "researching"
    WRITING = "writing"
    EDITING = "editing"
    FORMATTING = "formatting"
    OPTIMIZING = "optimizing"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    ERROR = "error"


# === Dataclasses used across the MAS ============================================================

@dataclass
class AgentExecutionEvent:
    agent: AgentType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""  # ISO-8601 string


@dataclass
class ContentSpec:
    topic: str
    subtopics: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    platform: str = "web"  
    target_audience: str = "general"


@dataclass
class PlanningOutput:
    content_strategy: str
    structure_approach: str
    key_messages: List[str]
    research_priorities: List[str]
    estimated_sections: List[Dict[str, Any]]
    audience_insights: Dict[str, Any] = field(default_factory=dict)
    competitive_positioning: Optional[str] = None
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    planning_confidence: float = 1.0
    # Optional overrides surfaced to downstream agents (SEO/title, etc.)
    target_keywords: Optional[List[str]] = None
    search_intent: Optional[str] = None


@dataclass
class ResearchFindings:
    primary_insights: List[Dict[str, Any]]
    statistical_evidence: List[Dict[str, Any]]
    expert_quotes: List[Dict[str, Any]]
    credibility_sources: List[str]
    research_confidence: float = 1.0
    industry_context: Dict[str, Any] = field(default_factory=dict)
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    competitive_landscape: Dict[str, Any] = field(default_factory=dict)
    trending_topics: List[str] = field(default_factory=list)
    research_gaps: List[str] = field(default_factory=list)


@dataclass
class DraftContent:
    """Content in draft form from the Writer agent."""
    title: str
    body: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EditedContent:
    """Content after editing by the Editor agent."""
    title: str
    body: str
    feedback: List[str] = field(default_factory=list)
    is_approved: bool = False
    edit_summary: str = ""


@dataclass
class FormattedContent:
    """Formatted content ready for publication."""
    markdown: str
    html: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedImage:
    """Metadata for a generated image."""
    prompt: str
    url: str
    alt_text: str
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class SeoAnalysis:
    """SEO analysis results."""
    keyword_density: Dict[str, float]
    readability_score: float
    recommendations: List[str]
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


@dataclass
class FormattingRequirements:
    output_format: str
    citation_format: str = "apa"
    # Required by the Formatter; integer header levels (e.g., [1, 2, 2, 3])
    header_hierarchy: List[int] = field(default_factory=list)
    formatting_confidence: float = 1.0


@dataclass
class CodeGenerationContext:
    programming_languages: List[str] = field(default_factory=lambda: ["python"])
    documentation_style: str = "technical"
    code_examples_needed: List[Dict[str, Any]] = field(default_factory=list)
    generation_confidence: float = 1.0


@dataclass
class SEOOptimizationContext:
    target_keywords: List[str]
    meta_description: str
    title_recommendations: List[str]
    seo_score: float = 0.0