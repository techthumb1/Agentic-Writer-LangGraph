# File: langgraph_app/core/enriched_content_state.py

"""
Enhanced content state management for WriterzRoom agents.
Contains all dataclasses and state schemas for agent coordination.
"""

from dataclasses import dataclass, field
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

class ContentType(Enum):
    """Content type enumeration"""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    TECHNICAL_DOC = "technical_doc"
    BUSINESS_PROPOSAL = "business_proposal"
    RESEARCH_PAPER = "research_paper"
    EMAIL_NEWSLETTER = "email_newsletter"
    SOCIAL_MEDIA = "social_media"
    PRESS_RELEASE = "press_release"

class GenerationStatus(Enum):
    """Generation status tracking"""
    PENDING = "pending"
    PLANNING = "planning"
    RESEARCHING = "researching"
    WRITING = "writing"
    EDITING = "editing"
    FORMATTING = "formatting"
    OPTIMIZING = "optimizing"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentType(Enum):
    """Agent type enumeration for the content generation pipeline"""
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

class ContentPhase(Enum):
    """Content generation phase tracking"""
    INITIALIZATION = "initialization"
    PLANNING = "planning"
    RESEARCH = "research"
    DRAFTING = "drafting"
    WRITING = "writing"
    EDITING = "editing"
    FORMATTING = "formatting"
    OPTIMIZATION = "optimization"
    FINALIZATION = "finalization"
    PUBLISHING = "publishing"
    COMPLETED = "completed"

@dataclass
class ContentSpec:
    """Content specification for generation"""
    content_type: ContentType = ContentType.ARTICLE
    topic: str = ""
    target_audience: str = "general"
    audience: str = "general"  # Alias for editor agent compatibility
    tone: str = "professional"
    length: int = 1000
    template_id: str = "default"
    template_type: str = "article"
    style_profile: str = "default"
    complexity_level: int = 5
    requirements: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)
    platform: str = "general"  # For template compatibility

@dataclass
class ResearchFindings:
    """Research findings from the researcher agent - FIXED with correct field names"""
    # Core research data
    primary_insights: List[Dict[str, Any]] = field(default_factory=list)
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    industry_context: Dict[str, Any] = field(default_factory=dict)
    competitive_landscape: Dict[str, Any] = field(default_factory=dict)
    trending_topics: List[str] = field(default_factory=list)
    expert_quotes: List[Dict[str, Any]] = field(default_factory=list)
    statistical_evidence: List[Dict[str, Any]] = field(default_factory=list)
    research_gaps: List[str] = field(default_factory=list)
    credibility_sources: List[str] = field(default_factory=list)
    research_confidence: float = 0.0
    
    # Legacy field compatibility
    sources: List[Dict[str, Any]] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    research_quality_score: float = 0.0
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_insights": self.primary_insights,
            "supporting_data": self.supporting_data,
            "industry_context": self.industry_context,
            "competitive_landscape": self.competitive_landscape,
            "trending_topics": self.trending_topics,
            "expert_quotes": self.expert_quotes,
            "statistical_evidence": self.statistical_evidence,
            "research_gaps": self.research_gaps,
            "credibility_sources": self.credibility_sources,
            "research_confidence": self.research_confidence,
            "sources": self.sources,
            "key_insights": self.key_insights,
            "citations": self.citations,
            "research_quality_score": self.research_quality_score,
            "timestamp": self.timestamp
        }

@dataclass
class EditingGuidance:
    """Editing guidance and feedback from the editor agent - Exact agent compatibility"""
    # Core editing fields (original)
    structural_feedback: List[str] = field(default_factory=list)
    content_improvements: List[str] = field(default_factory=list)
    style_adjustments: List[str] = field(default_factory=list)
    fact_checking_notes: List[str] = field(default_factory=list)
    readability_score: float = 0.0
    grammar_issues: List[str] = field(default_factory=list)
    revision_priority: str = "medium"
    
    # Exact fields the editor agent actually uses
    structural_improvements: List[str] = field(default_factory=list)
    clarity_enhancements: List[str] = field(default_factory=list)
    audience_alignment_issues: List[str] = field(default_factory=list)
    flow_optimizations: List[str] = field(default_factory=list)
    fact_checking_requirements: List[str] = field(default_factory=list)
    style_consistency_notes: List[str] = field(default_factory=list)
    engagement_opportunities: List[str] = field(default_factory=list)
    editing_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "structural_feedback": self.structural_feedback,
            "content_improvements": self.content_improvements,
            "style_adjustments": self.style_adjustments,
            "fact_checking_notes": self.fact_checking_notes,
            "readability_score": self.readability_score,
            "grammar_issues": self.grammar_issues,
            "revision_priority": self.revision_priority
        }

@dataclass
class FormattingRequirements:
    """Formatting requirements and specifications"""
    output_format: str = "markdown"
    structure_rules: Dict[str, Any] = field(default_factory=dict)
    styling_preferences: Dict[str, Any] = field(default_factory=dict)
    citation_format: str = "apa"
    header_hierarchy: List[str] = field(default_factory=list)
    special_formatting: Dict[str, Any] = field(default_factory=dict)
    platform_specifications: Dict[str, Any] = field(default_factory=dict)
    visual_hierarchy: Dict[str, Any] = field(default_factory=dict)
    formatting_elements: Dict[str, Any] = field(default_factory=dict)  # Added for formatter compatibility
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "output_format": self.output_format,
            "structure_rules": self.structure_rules,
            "styling_preferences": self.styling_preferences,
            "citation_format": self.citation_format,
            "header_hierarchy": self.header_hierarchy,
            "special_formatting": self.special_formatting
        }

@dataclass
class SEOOptimizationContext:
    """SEO optimization context and recommendations"""
    target_keywords: List[str] = field(default_factory=list)
    meta_description: str = ""
    title_recommendations: List[str] = field(default_factory=list)
    header_optimization: Dict[str, Any] = field(default_factory=dict)
    internal_links: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    readability_improvements: List[str] = field(default_factory=list)
    seo_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_keywords": self.target_keywords,
            "meta_description": self.meta_description,
            "title_recommendations": self.title_recommendations,
            "header_optimization": self.header_optimization,
            "internal_links": self.internal_links,
            "external_links": self.external_links,
            "readability_improvements": self.readability_improvements,
            "seo_score": self.seo_score
        }

@dataclass
class PublishingContext:
    """Publishing context and platform specifications"""
    target_platforms: List[str] = field(default_factory=list)
    publishing_schedule: Optional[str] = None
    platform_specific_formats: Dict[str, Any] = field(default_factory=dict)
    distribution_channels: List[str] = field(default_factory=list)
    social_media_posts: Dict[str, str] = field(default_factory=dict)
    publication_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_platforms": self.target_platforms,
            "publishing_schedule": self.publishing_schedule,
            "platform_specific_formats": self.platform_specific_formats,
            "distribution_channels": self.distribution_channels,
            "social_media_posts": self.social_media_posts,
            "publication_metadata": self.publication_metadata
        }


@dataclass
class CodeGenerationContext:
    """Code generation context for technical content with all expected fields"""
    # Core fields from original definition
    programming_languages: List[str] = field(default_factory=list)
    code_examples: List[Dict[str, Any]] = field(default_factory=list)
    documentation_style: str = "technical"
    api_references: List[str] = field(default_factory=list)
    testing_requirements: Dict[str, Any] = field(default_factory=dict)
    deployment_notes: List[str] = field(default_factory=list)
    
    # Missing fields that the code agent expects
    code_requirements: List[str] = field(default_factory=list)
    complexity_level: int = 5
    integration_requirements: List[str] = field(default_factory=list)
    documentation_needs: List[str] = field(default_factory=list)
    code_examples_needed: List[Dict[str, Any]] = field(default_factory=list)
    performance_considerations: List[str] = field(default_factory=list)
    generation_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "programming_languages": self.programming_languages,
            "code_examples": self.code_examples,
            "documentation_style": self.documentation_style,
            "api_references": self.api_references,
            "testing_requirements": self.testing_requirements,
            "deployment_notes": self.deployment_notes,
            "code_requirements": self.code_requirements,
            "complexity_level": self.complexity_level,
            "integration_requirements": self.integration_requirements,
            "documentation_needs": self.documentation_needs,
            "code_examples_needed": self.code_examples_needed,
            "performance_considerations": self.performance_considerations,
            "generation_confidence": self.generation_confidence
        }
@dataclass
class EnrichedContentState:
    """Main state object for content generation pipeline"""

    # Core content specification - now optional with default
    content_spec: Optional[ContentSpec] = field(default_factory=ContentSpec)

    # Tracking / IDs
    request_id: Optional[str] = None

    # Configs must be non-empty dicts in enterprise mode (validated upstream)
    template_config: Dict[str, Any] = field(default_factory=dict)
    style_config: Dict[str, Any] = field(default_factory=dict)

    # Content and generation tracking
    content: str = ""
    title: str = ""
    status: GenerationStatus = GenerationStatus.PENDING
    current_agent: str = "start"

    # Agent-specific contexts
    research_findings: Optional[ResearchFindings] = None
    editing_guidance: Optional[EditingGuidance] = None
    formatting_requirements: Optional[FormattingRequirements] = None
    seo_optimization: Optional[SEOOptimizationContext] = None
    publishing_context: Optional[PublishingContext] = None
    code_generation: Optional[CodeGenerationContext] = None
    planning_output: Optional[Dict[str, Any]] = None
    research_output: Optional[Dict[str, Any]] = None
    writing_output: Optional[Dict[str, Any]] = None
    editing_output: Optional[Dict[str, Any]] = None

    # Generation metadata
    generation_settings: Dict[str, Any] = field(default_factory=dict)
    template_data: Dict[str, Any] = field(default_factory=dict)
    style_profile_data: Dict[str, Any] = field(default_factory=dict)
    agent_type: Optional[str] = None
    workflow_state: Optional[str] = None

    # Research plan for compatibility
    research_plan: Optional[Any] = None

    # Call-writer compatibility fields
    draft_content: str = ""
    writing_context: Optional[Dict[str, Any]] = None
    generated_code: Optional[str] = None

    # Quality and performance tracking
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

    # Error handling and debugging
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    debug_info: Dict[str, Any] = field(default_factory=dict)

    # Timestamps and tracking
    created_at: str = ""
    updated_at: str = ""
    completion_time: Optional[str] = None

    def __post_init__(self):
        """Initialize timestamps and validate enterprise requirements"""
        from datetime import datetime
        
        # Initialize timestamps
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
        
        # CRITICAL FIX: Handle LangGraph internal state creation
        # LangGraph calls EnrichedContentState() with no args for internal operations
        
        # Check if this is a LangGraph internal state (empty configs with default markers)
        is_langgraph_internal = (
            isinstance(self.template_config, dict) and 
            self.template_config.get("_langgraph_default") == True
        )
        
        if is_langgraph_internal:
            # This is LangGraph internal state management - provide minimal valid state
            self.template_config = {"_internal_state": True, "template_type": "internal"}
            self.style_config = {"_internal_state": True, "style_profile": "internal"}
            
            # Ensure content_spec has minimal valid data for internal operations
            if not self.content_spec or not getattr(self.content_spec, 'topic', None):
                from . import ContentSpec
                self.content_spec = ContentSpec(
                    topic="Internal LangGraph State",
                    template_type="internal",
                    target_audience="system",
                    platform="internal"
                )
            
            # Silent handling for internal states
            return
        
        # ENTERPRISE VALIDATION for actual application states
        if self.template_config is None:
            self.template_config = {}
        if self.style_config is None:
            self.style_config = {}
        
        # ENTERPRISE VALIDATION: Ensure configs are dicts
        if not isinstance(self.template_config, dict):
            raise TypeError(f"template_config must be dict, got {type(self.template_config)}")
        if not isinstance(self.style_config, dict):
            raise TypeError(f"style_config must be dict, got {type(self.style_config)}")
        
        # Check for empty enterprise configs (non-internal states)
        if (not self.template_config or not self.style_config) and self.request_id:
            print(f"WARNING: Enterprise state {self.request_id} has empty configs:")
            print(f"  template_config: {bool(self.template_config)}")
            print(f"  style_config: {bool(self.style_config)}")
            print(f"  content_spec.topic: '{getattr(self.content_spec, 'topic', 'MISSING') if self.content_spec else 'NO_SPEC'}'")
    
    def update_phase(self, phase: ContentPhase) -> None:
        """Update current phase and timestamp"""
        from datetime import datetime
        self.workflow_state = phase.value
        self.updated_at = datetime.now().isoformat()

    def get_agent_instructions(self, agent_type: str) -> Dict[str, Any]:
        """Get agent-specific instructions from template config"""
        if not isinstance(self.template_config, dict) or not self.template_config:
            return {}
        agent_instructions = self.template_config.get("agent_instructions", {})
        value = agent_instructions.get(agent_type, {})
        # Always return a dict
        return value if isinstance(value, dict) else {}

    def log_agent_execution(self, agent_type: str, execution_data: Dict[str, Any]) -> None:
        """Log agent execution details to debug info"""
        from datetime import datetime
        if "agent_executions" not in self.debug_info:
            self.debug_info["agent_executions"] = []
        execution_log = {
            "agent_type": agent_type,
            "timestamp": datetime.now().isoformat(),
            **execution_data
        }
        self.debug_info["agent_executions"].append(execution_log)
        self.updated_at = datetime.now().isoformat()

    # ENTERPRISE VALIDATION METHODS
    def validate_enterprise_configs(self) -> None:
        """Validate that enterprise configs are properly populated"""
        if not isinstance(self.template_config, dict) or not self.template_config:
            raise ValueError("ENTERPRISE: template_config must be a non-empty dict")
        if not isinstance(self.style_config, dict) or not self.style_config:
            raise ValueError("ENTERPRISE: style_config must be a non-empty dict")

    def ensure_enterprise_ready(self) -> None:
        """Ensure state is ready for enterprise processing"""
        self.validate_enterprise_configs()
        
        # Ensure content_spec exists
        if not self.content_spec:
            raise ValueError("ENTERPRISE: content_spec is required")
        
        # Ensure content_spec has required fields
        if not getattr(self.content_spec, 'topic', '').strip():
            raise ValueError("ENTERPRISE: content_spec.topic is required and cannot be empty")


    # Dict-like helpers (backward compatibility with dict-style access)
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)

    def keys(self):
        return self.__dataclass_fields__.keys()

    def items(self):
        for name in self.__dataclass_fields__.keys():
            yield name, getattr(self, name)

    def values(self):
        for name in self.__dataclass_fields__.keys():
            yield getattr(self, name)

    def update(self, other: Dict[str, Any]) -> None:
        for key, value in other.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # --- Enterprise validation helpers -------------------------------------

    def _is_nonempty_dict(self, value: Any) -> bool:
        return isinstance(value, dict) and bool(value)

    def ensure_style_from_profile_data(self) -> None:
        """
        If style_config is empty but style_profile_data exists and is a dict,
        copy it into style_config. This is NOT a silent fallback; it only
        normalizes already-provided profile data.
        """
        if not self._is_nonempty_dict(self.style_config) and self._is_nonempty_dict(self.style_profile_data):
            # Normalize shallowly; let explicit style_config override
            merged = dict(self.style_profile_data)
            merged.update(self.style_config or {})
            self.style_config = merged
        # --- Enterprise validation helpers -------------------------------------
    def _is_nonempty_dict(self, v):
        return isinstance(v, dict) and bool(v)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def ensure_style_from_profile_data(self) -> None:
        """
        Normalize only if a parsed style profile dict was already loaded.
        No invented defaults; explicit style_config wins on key conflicts.
        """
        if (not self._is_nonempty_dict(self.style_config)
                and self._is_nonempty_dict(self.style_profile_data)):
            merged = dict(self.style_profile_data)
            merged.update(self.style_config or {})
            self.style_config = merged

    def require_template_for(self, stage: str) -> None:
        if not self._is_nonempty_dict(self.template_config):
            raise RuntimeError(f"{stage} blocked: template_config missing or empty.")

    def require_style_for(self, stage: str) -> None:
        if not self._is_nonempty_dict(self.style_config):
            raise RuntimeError(f"{stage} blocked: style_config missing or empty.")

    def validate_for_writer(self) -> None:
        # Writer must have both configs; normalize first from style_profile_data.
        self.ensure_style_from_profile_data()
        self.require_template_for("Writer")
        self.require_style_for("Writer")

    def validate_for_editor(self) -> None:
        # Editor has identical requirements.
        self.ensure_style_from_profile_data()
        self.require_template_for("Editor")
        self.require_style_for("Editor")

@dataclass
class PlanningOutput:
    """Planning output from planner agent"""
    content_strategy: str = ""
    structure_approach: str = ""
    key_messages: List[str] = None
    research_priorities: List[str] = None
    audience_insights: Dict[str, Any] = None
    competitive_positioning: str = ""
    success_metrics: Dict[str, Any] = None
    estimated_sections: List[Dict[str, Any]] = None
    planning_confidence: float = 0.85
    
    def __post_init__(self):
        if self.key_messages is None:
            self.key_messages = []
        if self.research_priorities is None:
            self.research_priorities = []
        if self.audience_insights is None:
            self.audience_insights = {}
        if self.success_metrics is None:
            self.success_metrics = {}
        if self.estimated_sections is None:
            self.estimated_sections = []

# File: langgraph_app/core/enriched_content_state.py
# Replace the FormattingRequirements dataclass with this complete version

@dataclass
class FormattingRequirements:
    """Complete formatting requirements with all agent-expected fields"""
    # Core formatting specifications (existing)
    output_format: str = "markdown"
    structure_rules: Dict[str, Any] = field(default_factory=dict)
    styling_preferences: Dict[str, Any] = field(default_factory=dict)
    citation_format: str = "apa"
    header_hierarchy: List[str] = field(default_factory=list)
    special_formatting: Dict[str, Any] = field(default_factory=dict)
    platform_specifications: Dict[str, Any] = field(default_factory=dict)
    visual_hierarchy: Dict[str, Any] = field(default_factory=dict)
    formatting_elements: Dict[str, Any] = field(default_factory=dict)
    
    # Missing fields that the formatter agent expects
    accessibility_requirements: Dict[str, Any] = field(default_factory=dict)
    seo_considerations: List[str] = field(default_factory=list)  # Back to List - matches formatter agent return type
    publication_metadata: Dict[str, Any] = field(default_factory=dict)
    formatting_confidence: float = 0.0
    
    def __post_init__(self):
        """Ensure all dict fields are properly initialized"""
        dict_fields = [
            'structure_rules', 'styling_preferences', 'special_formatting',
            'platform_specifications', 'visual_hierarchy', 'formatting_elements',
            'accessibility_requirements', 'publication_metadata'
        ]
        
        for field_name in dict_fields:
            if not getattr(self, field_name):
                setattr(self, field_name, {})
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "output_format": self.output_format,
            "structure_rules": self.structure_rules,
            "styling_preferences": self.styling_preferences,
            "citation_format": self.citation_format,
            "header_hierarchy": self.header_hierarchy,
            "special_formatting": self.special_formatting,
            "platform_specifications": self.platform_specifications,
            "visual_hierarchy": self.visual_hierarchy,
            "formatting_elements": self.formatting_elements,
            "accessibility_requirements": self.accessibility_requirements,
            "seo_considerations": self.seo_considerations,
            "publication_metadata": self.publication_metadata,
            "formatting_confidence": self.formatting_confidence
        }

def create_initial_state(
    topic: str = "General Content",
    content_type: ContentType = ContentType.ARTICLE,
    template_id: str = "default",
    style_profile: str = "default",
    **kwargs
) -> EnrichedContentState:
    """Create initial state for content generation"""
    
    content_spec = ContentSpec(
        content_type=content_type,
        topic=topic,
        target_audience=kwargs.get("target_audience", "general"),
        tone=kwargs.get("tone", "professional"),
        length=kwargs.get("length", 1000),
        template_id=template_id,
        style_profile=style_profile,
        template_type=kwargs.get("template_type", "article"),
        complexity_level=kwargs.get("complexity_level", 5),
    )
    
    return EnrichedContentState(
        content_spec=content_spec,
        generation_settings=kwargs.get("generation_settings", {}),
    )

__all__ = [
    "EnrichedContentState", 
    "ContentSpec", 
    "AgentType", 
    "ContentPhase",
    "PlanningOutput"
]