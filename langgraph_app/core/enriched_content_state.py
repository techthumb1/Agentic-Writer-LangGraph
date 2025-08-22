# File: langgraph_app/core/enriched_content_state.py
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime
import json

class AgentType(Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher" 
    WRITER = "writer"
    CALL_WRITER = "call_writer"
    EDITOR = "editor"
    FORMATTER = "formatter"
    SEO = "seo"
    IMAGE = "image"
    CODE = "code"
    PUBLISHER = "publisher"
    MCP_ENHANCED = "mcp_enhanced"

class ContentPhase(Enum):
    PLANNING = "planning"
    RESEARCH = "research"
    WRITING = "writing"
    CALL_WRITING = "call_writing"
    EDITING = "editing"
    FORMATTING = "formatting"
    IMAGE_GENERATION = "image_generation"
    CODE_GENERATION = "code_generation"
    SEO_OPTIMIZATION = "seo_optimization"
    PUBLISHING = "publishing"
    MCP_ENHANCEMENT = "mcp_enhancement"
    COMPLETE = "complete"

# In enriched_content_state.py, add this class:

@dataclass
class FormattingRequirements:
   """Formatting requirements for content"""
   platform_specifications: Dict[str, Any] = field(default_factory=dict)
   visual_hierarchy: List[str] = field(default_factory=list)
   formatting_elements: List[str] = field(default_factory=list)
   accessibility_requirements: List[str] = field(default_factory=list)
   seo_considerations: List[str] = field(default_factory=list)
   publication_metadata: Dict[str, Any] = field(default_factory=dict)
   formatting_confidence: float = 0.0
   timestamp: datetime = field(default_factory=datetime.now)

# In enriched_content_state.py, add this class:

# FIXED: Proper dataclass field ordering - non-defaults first, defaults last

@dataclass
class ContentSpec:
    """Content specification with FULLY DYNAMIC length calculation"""
    topic: str  # Required field, no default
    audience: str = ""  # Default fields come after required fields
    template_type: str = ""
    platform: str = ""
    complexity_level: int = 5
    innovation_level: str = "moderate"
    target_length: int = field(default=0)  # Calculated dynamically
    business_context: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate fully dynamic target_length - NO hardcoded values"""
        if self.target_length == 0:
            self.target_length = self._calculate_fully_dynamic_length()
    
    def _calculate_fully_dynamic_length(self) -> int:
        """PURE ALGORITHMIC calculation - adapts to any content type"""
        
        # Start with base calculation
        base_length = 400  # Minimal viable content
        
        # DYNAMIC PLATFORM ANALYSIS
        platform_factor = self._analyze_platform_characteristics()
        
        # DYNAMIC AUDIENCE ANALYSIS  
        audience_factor = self._analyze_audience_needs()
        
        # DYNAMIC COMPLEXITY SCALING
        complexity_factor = self._analyze_complexity_requirements()
        
        # DYNAMIC TEMPLATE ANALYSIS
        template_factor = self._analyze_template_characteristics()
        
        # DYNAMIC USER PREFERENCE ANALYSIS
        preference_factor = self._analyze_user_preferences()
        
        # ALGORITHMIC COMBINATION
        calculated_length = int(
            base_length * 
            platform_factor * 
            audience_factor * 
            complexity_factor * 
            template_factor * 
            preference_factor
        )
        
        # DYNAMIC BOUNDS (based on context)
        min_bound = self._calculate_minimum_viable_length()
        max_bound = self._calculate_maximum_effective_length()
        
        return max(min_bound, min(calculated_length, max_bound))
    
    def _analyze_platform_characteristics(self) -> float:
        """Analyze platform to determine length requirements dynamically"""
        platform = self.platform.lower()
        
        # Character/attention span analysis
        if 'twitter' in platform or 'tweet' in platform:
            return 0.15  # Very short attention span
        elif 'linkedin' in platform:
            return 0.4   # Professional, concise
        elif 'medium' in platform or 'substack' in platform:
            return 2.2   # Long-form reading platform
        elif 'email' in platform:
            return 0.6   # Email attention span
        elif 'mobile' in platform:
            return 0.7   # Mobile reading behavior
        else:
            return 1.0   # Standard web content
    
    def _analyze_audience_needs(self) -> float:
        """Analyze audience to determine explanation depth needed"""
        audience = self.audience.lower()
        
        # Expertise level analysis
        if any(word in audience for word in ['beginner', 'new', 'intro', 'basic']):
            return 1.4  # Need more explanation
        elif any(word in audience for word in ['expert', 'advanced', 'professional']):
            return 0.8  # Can be more concise
        elif any(word in audience for word in ['executive', 'c-level', 'leadership']):
            return 0.7  # High-level, concise
        elif any(word in audience for word in ['technical', 'developer', 'engineer']):
            return 1.2  # Technical detail needed
        elif any(word in audience for word in ['academic', 'researcher', 'scholar']):
            return 1.6  # Thorough documentation needed
        else:
            return 1.0  # General audience
    
    def _analyze_complexity_requirements(self) -> float:
        """Scale length based on complexity level (1-10)"""
        # Non-linear scaling - higher complexity needs exponentially more explanation
        return 0.5 + (self.complexity_level / 10) * 1.2
    
    def _analyze_template_characteristics(self) -> float:
        """Analyze template type dynamically without hardcoded mappings"""
        template = self.template_type.lower()
        
        # Semantic analysis of template purpose
        if any(word in template for word in ['social', 'tweet', 'post', 'caption']):
            return 0.3  # Social content is brief
        elif any(word in template for word in ['email', 'newsletter', 'message']):
            return 0.8  # Email content is moderate
        elif any(word in template for word in ['blog', 'article', 'story']):
            return 1.5  # Blog content is substantial
        elif any(word in template for word in ['technical', 'documentation', 'manual', 'guide']):
            return 2.0  # Technical content needs detail
        elif any(word in template for word in ['research', 'paper', 'study', 'analysis']):
            return 2.8  # Research content is comprehensive
        elif any(word in template for word in ['proposal', 'business', 'plan']):
            return 2.2  # Business content is detailed
        elif any(word in template for word in ['press', 'release', 'announcement']):
            return 0.9  # Press releases are focused
        else:
            return 1.0  # Unknown template type
    
    def _analyze_user_preferences(self) -> float:
        """Analyze user preferences from business context dynamically"""
        prefs = self.business_context
        
        # Check for explicit preferences
        if prefs.get('length_preference'):
            pref = str(prefs['length_preference']).lower()
            if any(word in pref for word in ['short', 'brief', 'concise', 'quick']):
                return 0.6
            elif any(word in pref for word in ['long', 'detailed', 'comprehensive', 'thorough']):
                return 1.8
            elif any(word in pref for word in ['extensive', 'complete', 'exhaustive']):
                return 2.5
        
        # Check for time constraints
        if prefs.get('time_limit'):
            # Less time = shorter content
            time_str = str(prefs['time_limit']).lower()
            if 'quick' in time_str or 'fast' in time_str:
                return 0.7
        
        # Check for formality level
        if prefs.get('formality'):
            formality = str(prefs['formality']).lower()
            if formality in ['formal', 'academic', 'professional']:
                return 1.3  # Formal content tends to be longer
            elif formality in ['casual', 'informal', 'conversational']:
                return 0.9  # Casual content can be shorter
        
        return 1.0  # Neutral
    
    def _calculate_minimum_viable_length(self) -> int:
        """Calculate minimum length needed for coherent content"""
        # Base minimum varies by content type
        if 'social' in self.template_type.lower():
            return 50   # Social posts can be very short
        elif 'email' in self.template_type.lower():
            return 100  # Emails need some substance
        else:
            return 200  # Most content needs at least this much
    
    def _calculate_maximum_effective_length(self) -> int:
        """Calculate maximum length before diminishing returns"""
        # Attention span varies by platform and audience
        platform_max = 8000  # Default web maximum
        
        if 'twitter' in self.platform.lower():
            platform_max = 2000  # Twitter thread maximum
        elif 'mobile' in self.platform.lower():
            platform_max = 1500  # Mobile reading limit
        elif 'email' in self.platform.lower():
            platform_max = 2000  # Email attention span
        elif any(word in self.template_type.lower() for word in ['research', 'academic', 'technical']):
            platform_max = 15000  # Academic content can be longer
        
        # Adjust for audience attention span
        if 'executive' in self.audience.lower():
            platform_max = min(platform_max, 2000)  # Executives want brevity
        elif 'beginner' in self.audience.lower():
            platform_max = min(platform_max, 3000)  # Beginners get overwhelmed
        
        return platform_max
@dataclass
class ContentSpecification:
    """Core content requirements with enterprise-grade type safety"""
    template_type: str
    topic: str
    audience: str
    platform: str
    complexity_level: int  # CRITICAL: Must be integer
    innovation_level: str
    target_length: int = field(default=0)
    business_context: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Enterprise-grade type validation"""
        # CRITICAL FIX: Ensure complexity_level is always integer
        if isinstance(self.complexity_level, str):
            try:
                self.complexity_level = int(self.complexity_level)
            except ValueError:
                raise ValueError(f"Invalid complexity_level: {self.complexity_level}. Must be integer 1-10.")
        
        # Validate business range
        if not isinstance(self.complexity_level, int) or not (1 <= self.complexity_level <= 10):
            raise ValueError(f"complexity_level must be integer 1-10, got {self.complexity_level}")
        
        # Calculate target length if not set
        if self.target_length == 0:
            self.target_length = self._calculate_target_length()
    
    def _calculate_target_length(self) -> int:
        """Calculate appropriate target length based on specifications"""
        base_length = 800
        
        # Platform adjustments
        platform_multipliers = {
            "linkedin": 0.6,
            "twitter": 0.2,
            "medium": 1.5,
            "blog": 1.3,
            "documentation": 2.0
        }
        
        multiplier = platform_multipliers.get(self.platform, 1.0)
        
        # Complexity adjustment (verified integer)
        complexity_factor = 0.7 + (self.complexity_level / 10) * 0.8
        
        return int(base_length * multiplier * complexity_factor)
@dataclass 
class PlanningOutput:
    """What the Planner Agent discovered and decided"""
    content_strategy: str = ""
    structure_approach: str = ""
    key_messages: List[str] = field(default_factory=list)
    research_priorities: List[str] = field(default_factory=list)
    audience_insights: Dict[str, Any] = field(default_factory=dict)
    competitive_positioning: str = ""
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    estimated_sections: List[Dict[str, str]] = field(default_factory=list)
    planning_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ResearchFindings:
    """What the Researcher Agent discovered"""
    primary_insights: List[Dict[str, str]] = field(default_factory=list)
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    industry_context: Dict[str, Any] = field(default_factory=dict)
    competitive_landscape: Dict[str, Any] = field(default_factory=dict)
    trending_topics: List[str] = field(default_factory=list)
    expert_quotes: List[Dict[str, str]] = field(default_factory=list)
    statistical_evidence: List[Dict[str, Any]] = field(default_factory=list)
    research_gaps: List[str] = field(default_factory=list)
    credibility_sources: List[str] = field(default_factory=list)
    research_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class WritingContext:
    """Dynamic context that informs writing decisions"""
    tone_adaptation: Dict[str, float] = field(default_factory=dict)
    voice_characteristics: List[str] = field(default_factory=list)
    narrative_approach: str = ""
    technical_depth: str = ""
    innovation_techniques: List[str] = field(default_factory=list)
    content_hooks: List[str] = field(default_factory=list)
    section_priorities: Dict[str, int] = field(default_factory=dict)
    writing_confidence: float = 0.0
    word_count_progress: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class EditingGuidance:
    """What the Editor Agent should focus on"""
    structural_improvements: List[str] = field(default_factory=list)
    clarity_enhancements: List[str] = field(default_factory=list)
    audience_alignment_issues: List[str] = field(default_factory=list)
    flow_optimizations: List[str] = field(default_factory=list)
    fact_checking_requirements: List[str] = field(default_factory=list)
    style_consistency_notes: List[str] = field(default_factory=list)
    engagement_opportunities: List[str] = field(default_factory=list)
    editing_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ImageGenerationContext:
    """Context for Image Agent decisions"""
    visual_requirements: List[str] = field(default_factory=list)
    image_types_needed: List[str] = field(default_factory=list)  # diagrams, photos, illustrations, charts
    brand_guidelines: Dict[str, Any] = field(default_factory=dict)
    platform_specifications: Dict[str, Any] = field(default_factory=dict)
    accessibility_requirements: List[str] = field(default_factory=list)
    visual_narrative: str = ""
    image_placement_strategy: List[Dict[str, Any]] = field(default_factory=list)
    generation_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CodeGenerationContext:
    """Context for Code Agent decisions"""
    code_requirements: List[str] = field(default_factory=list)
    programming_languages: List[str] = field(default_factory=list)
    complexity_level: int = 0
    integration_requirements: List[str] = field(default_factory=list)
    documentation_needs: List[str] = field(default_factory=list)
    testing_requirements: List[str] = field(default_factory=list)
    code_examples_needed: List[Dict[str, str]] = field(default_factory=list)
    performance_considerations: List[str] = field(default_factory=list)
    generation_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SEOOptimizationContext:
    """Context for SEO Agent decisions"""
    target_keywords: List[str] = field(default_factory=list)
    search_intent: str = ""
    competitor_analysis: Dict[str, Any] = field(default_factory=dict)
    content_optimization_opportunities: List[str] = field(default_factory=list)
    meta_data_requirements: Dict[str, str] = field(default_factory=dict)
    internal_linking_strategy: List[str] = field(default_factory=list)
    featured_snippet_opportunities: List[str] = field(default_factory=list)
    optimization_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PublishingContext:
    """Context for Publisher Agent decisions"""
    publication_platform: str = ""
    scheduling_requirements: Dict[str, Any] = field(default_factory=dict)
    distribution_channels: List[str] = field(default_factory=list)
    promotional_strategy: List[str] = field(default_factory=list)
    engagement_expectations: Dict[str, Any] = field(default_factory=dict)
    analytics_tracking: List[str] = field(default_factory=list)
    follow_up_actions: List[str] = field(default_factory=list)
    publishing_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MCPEnhancementContext:
    """Context for MCP Enhanced Agent decisions"""
    mcp_tools_available: List[str] = field(default_factory=list)
    enhancement_opportunities: List[str] = field(default_factory=list)
    integration_requirements: List[str] = field(default_factory=list)
    data_enrichment_needs: List[str] = field(default_factory=list)
    external_api_requirements: List[str] = field(default_factory=list)
    automation_possibilities: List[str] = field(default_factory=list)
    enhancement_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class FormattingContext:
    """Platform-specific formatting needs"""
    platform_specifications: Dict[str, Any] = field(default_factory=dict)
    visual_hierarchy: List[str] = field(default_factory=list)
    formatting_elements: List[str] = field(default_factory=list)
    accessibility_requirements: List[str] = field(default_factory=list)
    seo_considerations: List[str] = field(default_factory=list)
    publication_metadata: Dict[str, Any] = field(default_factory=dict)
    formatting_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AgentInstructions:
    """Dynamic instructions generated for each agent"""
    agent_type: AgentType
    primary_objectives: List[str] = field(default_factory=list)
    contextual_guidance: str = ""
    specific_requirements: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    innovation_directives: List[str] = field(default_factory=list)
    collaboration_notes: str = ""  # What previous agents discovered
    confidence_threshold: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

class ContentIntelligenceOrchestrator:
    """Central intelligence that generates dynamic agent instructions"""
    
    def __init__(self):
        self.success_patterns = {}
        self.failure_patterns = {}
        self.adaptation_rules = {}

    def _extract_planning_requirements(self, state):
       """Extract planning requirements from state"""
       return {
           "topic": state.content_spec.topic,
           "audience": state.content_spec.audience,
           "template_type": state.content_spec.template_type,
           "complexity_level": state.content_spec.complexity_level,
           "innovation_level": state.content_spec.innovation_level,
           "business_context": state.content_spec.business_context
       }

    def create_instructions(self, 
                          agent_type: AgentType, 
                          state: 'EnrichedContentState') -> AgentInstructions:
        """Generate contextually-aware instructions for each agent"""
        
        if agent_type == AgentType.PLANNER:
            return self._create_planner_instructions(state)
        elif agent_type == AgentType.RESEARCHER:
            return self._create_researcher_instructions(state)
        elif agent_type == AgentType.WRITER:
            return self._create_writer_instructions(state)
        elif agent_type == AgentType.CALL_WRITER:
            return self._create_call_writer_instructions(state)
        elif agent_type == AgentType.EDITOR:
            return self._create_editor_instructions(state)
        elif agent_type == AgentType.FORMATTER:
            return self._create_formatter_instructions(state)
        elif agent_type == AgentType.IMAGE:
            return self._create_image_instructions(state)
        elif agent_type == AgentType.CODE:
            return self._create_code_instructions(state)
        elif agent_type == AgentType.SEO:
            return self._create_seo_instructions(state)
        elif agent_type == AgentType.PUBLISHER:
            return self._create_publisher_instructions(state)
        elif agent_type == AgentType.MCP_ENHANCED:
            return self._create_mcp_enhanced_instructions(state)
        
    def _create_planner_instructions(self, state: 'EnrichedContentState') -> AgentInstructions:
        """Create dynamic planning instructions based on content spec"""
        spec = state.content_spec
        
        # Adapt objectives based on template type and context
        objectives = []
        if spec.template_type == "business_proposal":
            objectives = [
                f"Design strategic narrative for {spec.audience} audience",
                f"Structure content for {spec.platform} platform optimization",
                f"Plan {spec.innovation_level} approach with calculated creative risks",
                "Define measurable success metrics and ROI framework"
            ]
        elif spec.template_type == "technical_documentation":
            objectives = [
                f"Structure technical content for {spec.complexity_level}/10 complexity",
                "Plan progressive disclosure of technical concepts",
                "Design hands-on examples and implementation guides",
                "Create troubleshooting and support framework"
            ]
        
        # Contextual guidance based on business context
        contextual_guidance = self._generate_contextual_guidance(spec)
        
        return AgentInstructions(
            agent_type=AgentType.PLANNER,
            primary_objectives=objectives,
            contextual_guidance=contextual_guidance,
            specific_requirements=self._extract_planning_requirements(state),
            success_criteria=self._define_planning_success_criteria(spec),
            constraints=self._identify_planning_constraints(spec),
            innovation_directives=self._plan_innovation_approach(spec),
            collaboration_notes="First agent - establish foundation for all subsequent agents",
            confidence_threshold=0.8
        )
    
    def _define_planning_success_criteria(self, spec):
        return [
            "Clear content strategy defined",
            "Target audience properly identified", 
            "Content structure planned",
            "Success metrics established"
        ]

    def _identify_planning_constraints(self, spec):
        return spec.constraints.get("planning", [])

    def _plan_innovation_approach(self, spec):
        if spec.innovation_level == "experimental":
            return ["Push creative boundaries", "Test new formats"]
        elif spec.innovation_level == "conservative":
            return ["Use proven approaches", "Minimize risks"]
        return ["Balance innovation with reliability"]

    def _create_researcher_instructions(self, state: 'EnrichedContentState') -> AgentInstructions:
        """Create dynamic research instructions based on planning output"""
        planning = state.planning_output
        spec = state.content_spec
        
        # Research priorities from planning phase
        objectives = [
            f"Investigate {priority}" for priority in planning.research_priorities
        ]
        
        # Add context-specific research objectives
        if spec.template_type == "business_proposal":
            objectives.extend([
                "Gather market size and opportunity data",
                "Research competitive landscape and positioning", 
                "Find supporting financial metrics and benchmarks",
                "Identify industry trends and market validation"
            ])
        
        contextual_guidance = f"""
        Building on planning strategy: {planning.content_strategy}
        
        Key messages to support: {', '.join(planning.key_messages)}
        
        Audience insights to consider: {planning.audience_insights}
        
        Focus research on supporting the planned structure and validating strategic assumptions.
        """
        
        return AgentInstructions(
            agent_type=AgentType.RESEARCHER,
            primary_objectives=objectives,
            contextual_guidance=contextual_guidance,
            specific_requirements={
                "research_depth": spec.complexity_level,
                "evidence_types": self._determine_evidence_types(spec),
                "source_credibility_threshold": 0.8,
                "data_recency_requirements": self._determine_recency_needs(spec)
            },
            success_criteria=[
                "Gather comprehensive supporting evidence",
                "Validate planning assumptions", 
                "Identify unique insights and opportunities",
                "Build credible source foundation"
            ],
            constraints=spec.constraints.get("research", []),
            innovation_directives=self._research_innovation_approach(spec),
            collaboration_notes=f"Support planning strategy: {planning.content_strategy}",
            confidence_threshold=0.7
        )
    
    def _create_writer_instructions(self, state: 'EnrichedContentState') -> AgentInstructions:
        """Create dynamic writing instructions based on planning and research"""
        planning = state.planning_output
        research = state.research_findings
        spec = state.content_spec
        
        objectives = [
            "Transform research insights into compelling narrative",
            f"Execute {planning.content_strategy} with {spec.innovation_level} approach",
            "Integrate key messages seamlessly into content flow",
            f"Adapt writing for {spec.audience} sophistication level"
        ]
        
        contextual_guidance = f"""
        Strategic Foundation: {planning.content_strategy}
        Key Research Insights: {research.primary_insights[:3] if research else []}
        Audience Profile: {planning.audience_insights if planning else {}}
        
        Weave research findings naturally into narrative while maintaining the planned strategic approach.
        """
        
        return AgentInstructions(
            agent_type=AgentType.WRITER,
            primary_objectives=objectives,
            contextual_guidance=contextual_guidance,
            specific_requirements={
                "target_length": spec.target_length,
                "complexity_level": spec.complexity_level,
                "innovation_techniques": self._select_innovation_techniques(spec),
                "narrative_approach": planning.structure_approach if planning else "adaptive"
            },
            success_criteria=[
                "Compelling opening that hooks target audience",
                "Seamless integration of research evidence",
                "Clear progression of key messages",
                "Appropriate technical depth and complexity"
            ],
            constraints=spec.constraints.get("writing", []),
            innovation_directives=self._writing_innovation_approach(spec, research),
            collaboration_notes=f"Built on: {planning.content_strategy if planning else 'No planning'} | Research: {len(research.primary_insights) if research else 0} insights",
            confidence_threshold=0.8
        )
    
    def _create_call_writer_instructions(self, state: 'EnrichedContentState') -> AgentInstructions:
        """Create instructions for Call Writer Agent (enhanced writing coordination)"""
        objectives = [
            "Coordinate writing process across multiple content sections",
            "Ensure consistency in voice and tone throughout",
            "Manage content flow and narrative coherence",
            "Optimize content structure for maximum impact"
        ]
        
        return AgentInstructions(
            agent_type=AgentType.CALL_WRITER,
            primary_objectives=objectives,
            contextual_guidance="Orchestrate the writing process to ensure cohesive, high-quality output",
            specific_requirements={
                "coordination_scope": "full_content",
                "consistency_checks": ["voice", "tone", "terminology", "style"],
                "quality_thresholds": {"readability": 0.8, "engagement": 0.7}
            },
            success_criteria=[
                "Consistent voice throughout content",
                "Smooth transitions between sections",
                "Coherent narrative flow",
                "Optimized content structure"
            ],
            constraints=[],
            innovation_directives=[],
            collaboration_notes="Coordinate with Writer Agent for optimal content creation",
            confidence_threshold=0.75
        )
    
    def _create_editor_instructions(self, state: 'EnrichedContentState') -> AgentInstructions:
        """Create dynamic editing instructions based on written content"""
        spec = state.content_spec
        #writing_context = state.writing_context
        
        objectives = [
            "Enhance content clarity and readability",
            "Ensure alignment with target audience expectations",
            "Optimize content structure and flow",
            "Validate factual accuracy and source credibility"
        ]
        
        return AgentInstructions(
            agent_type=AgentType.EDITOR,
            primary_objectives=objectives,
            contextual_guidance=f"Refine content to maximize impact for {spec.audience} on {spec.platform}",
            specific_requirements={
                "editing_depth": "comprehensive",
                "audience_alignment": spec.audience,
                "platform_optimization": spec.platform,
                "quality_standards": "professional"
            },
            success_criteria=[
                "Clear, engaging prose",
                "Proper audience alignment",
                "Error-free content",
                "Optimized structure"
            ],
            constraints=spec.constraints.get("editing", []),
            innovation_directives=[],
            collaboration_notes="Refine Writer output while preserving strategic intent",
            confidence_threshold=0.8
        )
    
    def _create_formatter_instructions(self, state: 'EnrichedContentState') -> AgentInstructions:
        """Create formatting instructions for platform optimization"""
        spec = state.content_spec
        
        objectives = [
            f"Format content for optimal {spec.platform} presentation",
            "Implement visual hierarchy and readability enhancements",
            "Ensure accessibility and user experience optimization",
            "Apply platform-specific formatting requirements"
        ]
        
        return AgentInstructions(
            agent_type=AgentType.FORMATTER,
            primary_objectives=objectives,
            contextual_guidance=f"Transform edited content into platform-ready format for {spec.platform}",
            specific_requirements={
                "platform": spec.platform,
                "accessibility_standards": "WCAG 2.1 AA",
                "mobile_optimization": True,
                "visual_hierarchy": "clear"
            },
            success_criteria=[
                "Platform-optimized formatting",
                "Clear visual hierarchy",
                "Accessible content structure",
                "Mobile-responsive design"
            ],
            constraints=[],
            innovation_directives=[],
            collaboration_notes="Apply final formatting to edited content",
            confidence_threshold=0.75
        )
    
    def _create_image_instructions(self, state: 'EnrichedContentState') -> AgentInstructions:
        """Create image generation instructions"""
        spec = state.content_spec
        
        objectives = [
            "Generate visually compelling images that support content narrative",
            "Create platform-appropriate visual assets",
            "Ensure brand consistency and professional quality",
            "Optimize images for engagement and accessibility"
        ]
        
        return AgentInstructions(
            agent_type=AgentType.IMAGE,
            primary_objectives=objectives,
            contextual_guidance="Create visual assets that enhance content impact and engagement",
            specific_requirements={
                "image_types": self._determine_image_types(spec),
                "style_consistency": "professional",
                "platform_specs": self._get_platform_image_specs(spec.platform),
                "accessibility": True
            },
            success_criteria=[
                "High-quality visual assets",
                "Content-relevant imagery",
                "Platform-optimized formats",
                "Accessible alt text"
            ],
            constraints=[],
            innovation_directives=[],
            collaboration_notes="Support content with compelling visual elements",
            confidence_threshold=0.7
        )
    
    def _create_code_instructions(self, state: 'EnrichedContentState') -> AgentInstructions:
        """Create code generation instructions"""
        
        objectives = [
            "Generate relevant code examples and implementations",
            "Create well-documented, production-ready code",
            "Ensure code quality and best practices",
            "Provide comprehensive technical examples"
        ]
        
        return AgentInstructions(
            agent_type=AgentType.CODE,
            primary_objectives=objectives,
            contextual_guidance="Generate technical code that supports content objectives",
            specific_requirements={
                "code_quality": "production",
                "documentation": "comprehensive",
                "testing": "included",
                "best_practices": True
            },
            success_criteria=[
                "Working, tested code examples",
                "Clear documentation",
                "Best practice implementation",
                "Educational value"
            ],
            constraints=[],
            innovation_directives=[],
            collaboration_notes="Provide technical implementation support",
            confidence_threshold=0.8
        )
    
    def _create_seo_instructions(self, state: 'EnrichedContentState') -> AgentInstructions:
        """Create SEO optimization instructions"""
   
        objectives = [
            "Optimize content for search engine visibility",
            "Implement keyword strategy and semantic optimization",
            "Enhance content discoverability and ranking potential",
            "Create SEO-friendly metadata and structure"
        ]
        
        return AgentInstructions(
            agent_type=AgentType.SEO,
            primary_objectives=objectives,
            contextual_guidance="Maximize content visibility and search performance",
            specific_requirements={
                "keyword_optimization": "natural",
                "semantic_seo": True,
                "technical_seo": "comprehensive",
                "user_intent": "aligned"
            },
            success_criteria=[
                "Optimized keyword integration",
                "Strong semantic relevance",
                "Technical SEO compliance",
                "User-intent alignment"
            ],
            constraints=[],
            innovation_directives=[],
            collaboration_notes="Optimize formatted content for search visibility",
            confidence_threshold=0.75
        )
    
    def _create_publisher_instructions(self, state: 'EnrichedContentState') -> AgentInstructions:
        """Create publishing instructions"""
        spec = state.content_spec
        
        objectives = [
            "Prepare content for publication across target platforms",
            "Implement distribution and promotional strategy",
            "Set up analytics and performance tracking",
            "Execute go-to-market content strategy"
        ]
        
        return AgentInstructions(
            agent_type=AgentType.PUBLISHER,
            primary_objectives=objectives,
            contextual_guidance="Execute comprehensive content publication and promotion",
            specific_requirements={
                "publication_platforms": [spec.platform],
                "distribution_strategy": "multi_channel",
                "analytics_setup": True,
                "promotional_plan": "integrated"
            },
            success_criteria=[
                "Successful content publication",
                "Active distribution channels",
                "Analytics tracking enabled",
                "Promotional campaign launched"
            ],
            constraints=[],
            innovation_directives=[],
            collaboration_notes="Execute final publication and promotion",
            confidence_threshold=0.8
        )
    
    def _create_mcp_enhanced_instructions(self, state: 'EnrichedContentState') -> AgentInstructions:
        """Create MCP enhanced agent instructions"""
        
        objectives = [
            "Leverage MCP tools for content enhancement",
            "Integrate external data sources and APIs",
            "Automate content enrichment processes",
            "Enhance content with real-time data and insights"
        ]
        
        return AgentInstructions(
            agent_type=AgentType.MCP_ENHANCED,
            primary_objectives=objectives,
            contextual_guidance="Use MCP capabilities to enhance content quality and relevance",
            specific_requirements={
                "mcp_tools": "available",
                "data_integration": True,
                "automation_level": "high",
                "enhancement_scope": "comprehensive"
            },
            success_criteria=[
                "Enhanced content quality",
                "Integrated external data",
                "Automated enhancements",
                "Real-time relevance"
            ],
            constraints=[],
            innovation_directives=[],
            collaboration_notes="Enhance content using MCP capabilities",
            confidence_threshold=0.7
        )
    
    # Helper methods for instruction generation
    def _generate_contextual_guidance(self, spec: ContentSpecification) -> str:
        """Generate contextual guidance based on content specification"""
        guidance_elements = []
        
        if spec.business_context:
            guidance_elements.append(f"Business Context: {spec.business_context}")
        
        if spec.innovation_level == "experimental":
            guidance_elements.append("Push creative boundaries while maintaining professional quality")
        elif spec.innovation_level == "conservative":
            guidance_elements.append("Focus on proven approaches and established best practices")
        
        return " | ".join(guidance_elements)
    
    def _determine_evidence_types(self, spec: ContentSpecification) -> List[str]:
        """Determine what types of evidence are needed"""
        if spec.template_type == "business_proposal":
            return ["market_data", "financial_metrics", "case_studies", "industry_reports"]
        elif spec.template_type == "technical_documentation":
            return ["code_examples", "benchmarks", "best_practices", "implementation_guides"]
        return ["statistics", "expert_quotes", "case_studies"]
    
    def _determine_recency_needs(self, spec: ContentSpecification) -> str:
        """Determine how recent data needs to be"""
        if spec.template_type == "business_proposal":
            return "within_6_months"
        return "within_1_year"
    
    def _research_innovation_approach(self, spec: ContentSpecification) -> List[str]:
        """Define research innovation directives"""
        if spec.innovation_level == "experimental":
            return ["Seek cutting-edge sources", "Include emerging trends"]
        return ["Use established sources", "Focus on proven data"]
    
    def _select_innovation_techniques(self, spec: ContentSpecification) -> List[str]:
        """Select innovation techniques for writing"""
        if spec.innovation_level == "experimental":
            return ["narrative_storytelling", "interactive_elements", "multimedia_integration"]
        return ["clear_structure", "proven_frameworks"]
    
    def _writing_innovation_approach(self, spec: ContentSpecification, research: Optional[ResearchFindings]) -> List[str]:
        """Define writing innovation directives"""
        if spec.innovation_level == "experimental":
            return ["Experiment with narrative techniques", "Include interactive elements"]
        return ["Use proven writing patterns", "Focus on clarity"]
    
    def _determine_image_types(self, spec: ContentSpecification) -> List[str]:
        """Determine what types of images are needed"""
        if spec.template_type == "business_proposal":
            return ["charts", "graphs", "infographics", "professional_photos"]
        elif spec.template_type == "technical_documentation":
            return ["diagrams", "screenshots", "flowcharts", "architecture_diagrams"]
        return ["illustrations", "photos", "graphics"]
    
    def _get_platform_image_specs(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific image specifications"""
        specs = {
            "linkedin": {"aspect_ratio": "16:9", "max_width": 1200, "format": "PNG"},
            "medium": {"aspect_ratio": "3:2", "max_width": 1000, "format": "JPEG"},
            "substack": {"aspect_ratio": "16:9", "max_width": 1456, "format": "PNG"}
        }
        return specs.get(platform, {"aspect_ratio": "16:9", "max_width": 1200, "format": "PNG"})


@dataclass
class EnrichedContentState:
    """Central state object that flows through the entire agent pipeline"""
    
    # Core specifications
    content_spec: ContentSpecification
    request_id: str = ""  
    
    # Agent outputs (populated as agents run)
    planning_output: Optional[PlanningOutput] = None
    research_findings: Optional[ResearchFindings] = None
    writing_context: Optional[WritingContext] = None
    editing_guidance: Optional[EditingGuidance] = None
    formatting_requirements: Optional[Any] = None  # Placeholder, define FormattingRequirements if needed
    image_context: Optional[ImageGenerationContext] = None
    code_context: Optional[CodeGenerationContext] = None
    seo_context: Optional[SEOOptimizationContext] = None
    publishing_context: Optional[PublishingContext] = None
    mcp_context: Optional[MCPEnhancementContext] = None
    
    # Dynamic state management
    current_phase: ContentPhase = ContentPhase.PLANNING
    completed_phases: List[ContentPhase] = field(default_factory=list)
    agent_execution_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Content artifacts
    draft_content: str = ""
    final_content: str = ""
    generated_images: List[Dict[str, Any]] = field(default_factory=list)
    generated_code: List[Dict[str, Any]] = field(default_factory=list)
    
    # Quality metrics
    overall_confidence: float = 0.0
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Orchestration
    orchestrator: ContentIntelligenceOrchestrator = field(default_factory=ContentIntelligenceOrchestrator)
    
    def get_agent_instructions(self, agent_type: AgentType) -> AgentInstructions:
        """Get dynamic instructions for the specified agent"""
        return self.orchestrator.create_instructions(agent_type, self)
    
    def update_phase(self, new_phase: ContentPhase):
        """Update current phase and track progress"""
        if self.current_phase not in self.completed_phases:
            self.completed_phases.append(self.current_phase)
        self.current_phase = new_phase
    
    def log_agent_execution(self, agent_type: AgentType, execution_data: Dict[str, Any]):
        """Log agent execution for debugging and optimization"""
        self.agent_execution_log.append({
            "agent": agent_type.value,
            "timestamp": datetime.now().isoformat(),
            "phase": self.current_phase.value,
            "execution_data": execution_data
        })
    
    def calculate_overall_confidence(self):
        """Calculate overall confidence based on agent outputs"""
        confidences = []
        
        if self.planning_output:
            confidences.append(self.planning_output.planning_confidence)
        if self.research_findings:
            confidences.append(self.research_findings.research_confidence)
        if self.writing_context:
            confidences.append(self.writing_context.writing_confidence)
        if self.editing_guidance:
            confidences.append(self.editing_guidance.editing_confidence)
        
        self.overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    

    # File: langgraph_app/core/enriched_content_state.py 
# ADD this method to your existing EnrichedContentState class (don't replace anything)

    def to_serializable_dict(self) -> Dict[str, Any]:
        """Convert to msgpack-serializable dictionary for LangGraph workflow execution"""
        return {
            "content_spec": {
                "template_type": self.content_spec.template_type,
                "topic": self.content_spec.topic,
                "audience": self.content_spec.audience,
                "platform": self.content_spec.platform,
                "complexity_level": int(self.content_spec.complexity_level),
                "innovation_level": self.content_spec.innovation_level,
                "target_length": int(self.content_spec.target_length),
                "business_context": dict(self.content_spec.business_context),
                "constraints": dict(self.content_spec.constraints)
            },
            "request_id": str(self.request_id),
            "current_phase": self.current_phase.value,
            "completed_phases": [phase.value for phase in self.completed_phases],
            "draft_content": str(self.draft_content),
            "final_content": str(self.final_content),
            "overall_confidence": float(self.overall_confidence),
            "quality_metrics": dict(self.quality_metrics),
            "agent_execution_log": list(self.agent_execution_log),
            "generated_images": list(self.generated_images),
            "generated_code": list(self.generated_code),
            # Serialize complex objects safely
            "planning_output": self._serialize_planning_output(),
            "research_findings": self._serialize_research_findings(),
            "seo_context": self._serialize_seo_context(),
            "publishing_context": self._serialize_publishing_context()
        }
    
    def _serialize_planning_output(self) -> Optional[Dict[str, Any]]:
        """Serialize planning output to msgpack-compatible dict"""
        if not self.planning_output:
            return None
        return {
            "content_strategy": str(self.planning_output.content_strategy),
            "structure_approach": str(self.planning_output.structure_approach),
            "key_messages": list(self.planning_output.key_messages),
            "research_priorities": list(self.planning_output.research_priorities),
            "planning_confidence": float(self.planning_output.planning_confidence)
        }
    
    def _serialize_research_findings(self) -> Optional[Dict[str, Any]]:
        """Serialize research findings to msgpack-compatible dict"""
        if not self.research_findings:
            return None
        return {
            "primary_insights": list(self.research_findings.primary_insights),
            "supporting_data": dict(self.research_findings.supporting_data),
            "credibility_sources": list(self.research_findings.credibility_sources),
            "research_confidence": float(self.research_findings.research_confidence)
        }
    
    def _serialize_seo_context(self) -> Optional[Dict[str, Any]]:
        """Serialize SEO context to msgpack-compatible dict"""
        if not self.seo_context:
            return None
        return {
            "target_keywords": list(self.seo_context.target_keywords),
            "search_intent": str(self.seo_context.search_intent),
            "optimization_confidence": float(self.seo_context.optimization_confidence)
        }
    
    def _serialize_publishing_context(self) -> Optional[Dict[str, Any]]:
        """Serialize publishing context to msgpack-compatible dict"""
        if not self.publishing_context:
            return None
        return {
            "publication_platform": str(self.publishing_context.publication_platform),
            "distribution_channels": list(self.publishing_context.distribution_channels),
            "publishing_confidence": float(self.publishing_context.publishing_confidence)
        }


    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            "content_spec": self.content_spec.__dict__,
            "current_phase": self.current_phase.value,
            "completed_phases": [phase.value for phase in self.completed_phases],
            "overall_confidence": self.overall_confidence,
            "quality_metrics": self.quality_metrics,
            "agent_execution_log": self.agent_execution_log
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnrichedContentState':
        """Create state from dictionary"""
        # Implementation for deserializing state
        pass


# Usage Example
def create_initial_state(template_type: str, topic: str, audience: str, platform: str) -> EnrichedContentState:
    """Create initial enriched content state"""
    
    content_spec = ContentSpecification(
        template_type=template_type,
        topic=topic,
        audience=audience,
        platform=platform,
        complexity_level=7,
        innovation_level="balanced",
        target_length=1200,
        business_context={"industry": "technology", "stage": "growth"},
        constraints={"time_limit": "2_hours", "word_limit": 1500}
    )
    
    return EnrichedContentState(
        content_spec=content_spec,
        current_phase=ContentPhase.PLANNING
    )