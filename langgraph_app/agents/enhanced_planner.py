# langgraph_app/agents/enhanced_planner.py

import os
import asyncio
import logging
import json
import time
import yaml
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from pathlib import Path

from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    TECHNICAL_ARTICLE = "technical_article"
    TUTORIAL = "tutorial"
    RESEARCH_REVIEW = "research_review"
    OPINION_PIECE = "opinion_piece"
    NEWS_ANALYSIS = "news_analysis"
    CASE_STUDY = "case_study"
    WHITEPAPER = "whitepaper"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    NEWSLETTER = "newsletter"

class Audience(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    GENERAL_PUBLIC = "general_public"
    TECHNICAL_PROFESSIONALS = "technical_professionals"
    BUSINESS_LEADERS = "business_leaders"
    RESEARCHERS = "researchers"
    STUDENTS = "students"

class ContentComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    HIGHLY_TECHNICAL = "highly_technical"

class PlanningApproach(Enum):
    RESEARCH_DRIVEN = "research_driven"
    NARRATIVE_FOCUSED = "narrative_focused"
    TUTORIAL_BASED = "tutorial_based"
    ANALYSIS_HEAVY = "analysis_heavy"
    OPINION_CENTRIC = "opinion_centric"
    DATA_DRIVEN = "data_driven"

@dataclass
class ContentStructure:
    """Defines the structure of content"""
    introduction: Dict[str, Any] = field(default_factory=dict)
    main_sections: List[Dict[str, Any]] = field(default_factory=list)
    conclusion: Dict[str, Any] = field(default_factory=dict)
    appendices: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResearchRequirements:
    """Research requirements for content planning"""
    primary_topics: List[str] = field(default_factory=list)
    secondary_topics: List[str] = field(default_factory=list)
    required_sources: List[str] = field(default_factory=list)
    source_types: List[str] = field(default_factory=list)
    depth_level: str = "moderate"
    recency_requirement: str = "within_1_year"
    credibility_threshold: str = "high"

@dataclass
class StyleRequirements:
    """Style and tone requirements"""
    writing_style: str = "professional"
    tone: str = "informative"
    formality_level: str = "formal"
    technical_depth: str = "moderate"
    use_examples: bool = True
    include_code_snippets: bool = False
    include_diagrams: bool = False
    include_citations: bool = True

@dataclass
class SEORequirements:
    """SEO optimization requirements"""
    target_keywords: List[str] = field(default_factory=list)
    keyword_density: float = 0.02
    meta_description_length: int = 160
    title_length: int = 60
    header_structure: bool = True
    internal_linking: bool = True
    external_linking: bool = True
    image_optimization: bool = True

@dataclass
class ContentPlan:
    """Comprehensive content plan"""
    topic: str = ""
    content_type: ContentType = ContentType.BLOG_POST
    target_audience: Audience = Audience.GENERAL_PUBLIC
    complexity: ContentComplexity = ContentComplexity.MODERATE
    approach: PlanningApproach = PlanningApproach.RESEARCH_DRIVEN
    estimated_length: int = 1500
    estimated_read_time: int = 6
    structure: ContentStructure = field(default_factory=ContentStructure)
    research_requirements: ResearchRequirements = field(default_factory=ResearchRequirements)
    style_requirements: StyleRequirements = field(default_factory=StyleRequirements)
    seo_requirements: SEORequirements = field(default_factory=SEORequirements)
    timeline: Dict[str, Any] = field(default_factory=dict)
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    creation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlanningResult:
    """Result of content planning"""
    plan: ContentPlan
    confidence_score: float = 0.0
    planning_time_ms: int = 0
    reasoning: str = ""
    alternatives: List[ContentPlan] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class ContentAnalyzer:
    """Analyzes topics and determines optimal content approach"""
    
    def __init__(self, model_registry=None):
        self.model_registry = model_registry
    
    def analyze_topic(self, topic: str, dynamic_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze topic to determine content characteristics"""
        try:
            if not dynamic_params:
                dynamic_params = {}
            
            # Basic topic analysis
            topic_lower = topic.lower()
            word_count = len(topic.split())
            
            # Determine content type based on topic keywords
            content_type = self._determine_content_type(topic_lower, dynamic_params)
            
            # Determine target audience
            audience = self._determine_audience(topic_lower, dynamic_params)
            
            # Determine complexity
            complexity = self._determine_complexity(topic_lower, dynamic_params)
            
            # Determine approach
            approach = self._determine_approach(topic_lower, dynamic_params)
            
            # Estimate content length and read time
            estimated_length, read_time = self._estimate_length_and_time(content_type, complexity)
            
            return {
                "content_type": content_type,
                "target_audience": audience,
                "complexity": complexity,
                "approach": approach,
                "estimated_length": estimated_length,
                "estimated_read_time": read_time,
                "analysis_confidence": self._calculate_confidence(topic, dynamic_params)
            }
            
        except Exception as e:
            logger.error(f"Topic analysis failed: {e}")
            return {
                "content_type": ContentType.BLOG_POST,
                "target_audience": Audience.GENERAL_PUBLIC,
                "complexity": ContentComplexity.MODERATE,
                "approach": PlanningApproach.RESEARCH_DRIVEN,
                "estimated_length": 1500,
                "estimated_read_time": 6,
                "analysis_confidence": 0.5
            }
    
    def _determine_content_type(self, topic: str, params: Dict) -> ContentType:
        """Determine content type from topic and parameters"""
        # Check explicit parameter
        if "content_type" in params:
            try:
                return ContentType(params["content_type"].lower())
            except ValueError:
                pass
        
        # Topic-based detection
        if any(word in topic for word in ["tutorial", "how to", "guide", "step by step"]):
            return ContentType.TUTORIAL
        elif any(word in topic for word in ["review", "analysis", "evaluation"]):
            return ContentType.RESEARCH_REVIEW
        elif any(word in topic for word in ["opinion", "thoughts", "perspective"]):
            return ContentType.OPINION_PIECE
        elif any(word in topic for word in ["news", "latest", "update", "breaking"]):
            return ContentType.NEWS_ANALYSIS
        elif any(word in topic for word in ["case study", "implementation", "example"]):
            return ContentType.CASE_STUDY
        elif any(word in topic for word in ["technical", "deep dive", "architecture"]):
            return ContentType.TECHNICAL_ARTICLE
        else:
            return ContentType.BLOG_POST
    
    def _determine_audience(self, topic: str, params: Dict) -> Audience:
        """Determine target audience"""
        if "target_audience" in params:
            try:
                return Audience(params["target_audience"].lower())
            except ValueError:
                pass
        
        # Topic-based detection
        if any(word in topic for word in ["beginner", "introduction", "basics", "101"]):
            return Audience.BEGINNER
        elif any(word in topic for word in ["advanced", "expert", "professional"]):
            return Audience.ADVANCED
        elif any(word in topic for word in ["technical", "engineering", "developer"]):
            return Audience.TECHNICAL_PROFESSIONALS
        elif any(word in topic for word in ["business", "executive", "strategy"]):
            return Audience.BUSINESS_LEADERS
        elif any(word in topic for word in ["research", "academic", "study"]):
            return Audience.RESEARCHERS
        else:
            return Audience.GENERAL_PUBLIC
    
    def _determine_complexity(self, topic: str, params: Dict) -> ContentComplexity:
        """Determine content complexity"""
        if "complexity" in params:
            try:
                return ContentComplexity(params["complexity"].lower())
            except ValueError:
                pass
        
        # Topic-based detection
        if any(word in topic for word in ["simple", "basic", "easy", "beginner"]):
            return ContentComplexity.SIMPLE
        elif any(word in topic for word in ["advanced", "complex", "sophisticated"]):
            return ContentComplexity.COMPLEX
        elif any(word in topic for word in ["technical", "algorithmic", "mathematical"]):
            return ContentComplexity.HIGHLY_TECHNICAL
        else:
            return ContentComplexity.MODERATE
    
    def _determine_approach(self, topic: str, params: Dict) -> PlanningApproach:
        """Determine planning approach"""
        if "approach" in params:
            try:
                return PlanningApproach(params["approach"].lower())
            except ValueError:
                pass
        
        # Topic-based detection
        if any(word in topic for word in ["tutorial", "how to", "guide"]):
            return PlanningApproach.TUTORIAL_BASED
        elif any(word in topic for word in ["analysis", "review", "evaluation"]):
            return PlanningApproach.ANALYSIS_HEAVY
        elif any(word in topic for word in ["opinion", "thoughts", "perspective"]):
            return PlanningApproach.OPINION_CENTRIC
        elif any(word in topic for word in ["data", "statistics", "metrics"]):
            return PlanningApproach.DATA_DRIVEN
        elif any(word in topic for word in ["story", "narrative", "journey"]):
            return PlanningApproach.NARRATIVE_FOCUSED
        else:
            return PlanningApproach.RESEARCH_DRIVEN
    
    def _estimate_length_and_time(self, content_type: ContentType, complexity: ContentComplexity) -> Tuple[int, int]:
        """Estimate content length and reading time"""
        base_lengths = {
            ContentType.TECHNICAL_ARTICLE: 2500,
            ContentType.TUTORIAL: 2000,
            ContentType.RESEARCH_REVIEW: 3000,
            ContentType.OPINION_PIECE: 1200,
            ContentType.NEWS_ANALYSIS: 1000,
            ContentType.CASE_STUDY: 2200,
            ContentType.WHITEPAPER: 4000,
            ContentType.BLOG_POST: 1500,
            ContentType.SOCIAL_MEDIA: 300,
            ContentType.NEWSLETTER: 800
        }
        
        complexity_multipliers = {
            ContentComplexity.SIMPLE: 0.8,
            ContentComplexity.MODERATE: 1.0,
            ContentComplexity.COMPLEX: 1.3,
            ContentComplexity.HIGHLY_TECHNICAL: 1.6
        }
        
        base_length = base_lengths.get(content_type, 1500)
        multiplier = complexity_multipliers.get(complexity, 1.0)
        estimated_length = int(base_length * multiplier)
        
        # Calculate read time (average 200 words per minute)
        read_time = max(1, estimated_length // 200)
        
        return estimated_length, read_time
    
    def _calculate_confidence(self, topic: str, params: Dict) -> float:
        """Calculate confidence score for analysis"""
        confidence = 0.7  # Base confidence
        
        # Boost confidence for explicit parameters
        if "content_type" in params:
            confidence += 0.1
        if "target_audience" in params:
            confidence += 0.1
        if "complexity" in params:
            confidence += 0.1
        
        # Boost confidence for clear topic indicators
        topic_lower = topic.lower()
        if any(word in topic_lower for word in ["tutorial", "guide", "how to", "introduction"]):
            confidence += 0.05
        
        return min(1.0, confidence)

class StructureGenerator:
    """Generates content structure based on planning requirements"""
    
    def __init__(self, model_registry=None):
        self.model_registry = model_registry
    
    def generate_structure(self, content_plan: ContentPlan) -> ContentStructure:
        """Generate detailed content structure"""
        try:
            structure = ContentStructure()
            
            # Generate introduction
            structure.introduction = self._generate_introduction_structure(content_plan)
            
            # Generate main sections
            structure.main_sections = self._generate_main_sections(content_plan)
            
            # Generate conclusion
            structure.conclusion = self._generate_conclusion_structure(content_plan)
            
            # Generate appendices if needed
            if content_plan.complexity in [ContentComplexity.COMPLEX, ContentComplexity.HIGHLY_TECHNICAL]:
                structure.appendices = self._generate_appendices(content_plan)
            
            # Add metadata
            structure.metadata = {
                "total_sections": len(structure.main_sections),
                "estimated_length": content_plan.estimated_length,
                "structure_type": content_plan.approach.value,
                "generated_at": datetime.now().isoformat()
            }
            
            return structure
            
        except Exception as e:
            logger.error(f"Structure generation failed: {e}")
            return self._generate_default_structure(content_plan)
    
    def _generate_introduction_structure(self, plan: ContentPlan) -> Dict[str, Any]:
        """Generate introduction structure"""
        return {
            "hook": {
                "type": "question" if plan.target_audience in [Audience.BEGINNER, Audience.GENERAL_PUBLIC] else "statement",
                "content_points": [
                    "Engaging opening",
                    "Problem statement",
                    "Why this matters"
                ]
            },
            "context": {
                "background_info": True,
                "current_state": True,
                "relevance": True
            },
            "preview": {
                "what_readers_will_learn": True,
                "key_takeaways": True,
                "structure_overview": plan.estimated_length > 2000
            },
            "estimated_length": min(200, plan.estimated_length // 10)
        }
    
    def _generate_main_sections(self, plan: ContentPlan) -> List[Dict[str, Any]]:
        """Generate main content sections"""
        sections = []
        
        if plan.approach == PlanningApproach.TUTORIAL_BASED:
            sections = self._generate_tutorial_sections(plan)
        elif plan.approach == PlanningApproach.RESEARCH_DRIVEN:
            sections = self._generate_research_sections(plan)
        elif plan.approach == PlanningApproach.ANALYSIS_HEAVY:
            sections = self._generate_analysis_sections(plan)
        elif plan.approach == PlanningApproach.OPINION_CENTRIC:
            sections = self._generate_opinion_sections(plan)
        elif plan.approach == PlanningApproach.NARRATIVE_FOCUSED:
            sections = self._generate_narrative_sections(plan)
        elif plan.approach == PlanningApproach.DATA_DRIVEN:
            sections = self._generate_data_sections(plan)
        else:
            sections = self._generate_default_sections(plan)
        
        return sections
    
    def _generate_tutorial_sections(self, plan: ContentPlan) -> List[Dict[str, Any]]:
        """Generate tutorial-style sections"""
        sections = [
            {
                "title": "Prerequisites and Setup",
                "type": "preparation",
                "content_points": [
                    "Required knowledge",
                    "Tools and resources",
                    "Environment setup"
                ],
                "estimated_length": plan.estimated_length // 8,
                "include_code": plan.style_requirements.include_code_snippets
            },
            {
                "title": "Step-by-Step Implementation",
                "type": "implementation",
                "content_points": [
                    "Detailed steps",
                    "Code examples",
                    "Common pitfalls"
                ],
                "estimated_length": plan.estimated_length // 2,
                "include_code": True
            },
            {
                "title": "Testing and Validation",
                "type": "validation",
                "content_points": [
                    "How to test",
                    "Expected results",
                    "Troubleshooting"
                ],
                "estimated_length": plan.estimated_length // 6,
                "include_code": plan.style_requirements.include_code_snippets
            }
        ]
        
        if plan.complexity in [ContentComplexity.COMPLEX, ContentComplexity.HIGHLY_TECHNICAL]:
            sections.append({
                "title": "Advanced Considerations",
                "type": "advanced",
                "content_points": [
                    "Optimization techniques",
                    "Scalability concerns",
                    "Best practices"
                ],
                "estimated_length": plan.estimated_length // 8,
                "include_code": True
            })
        
        return sections
    
    def _generate_research_sections(self, plan: ContentPlan) -> List[Dict[str, Any]]:
        """Generate research-driven sections"""
        return [
            {
                "title": "Background and Context",
                "type": "background",
                "content_points": [
                    "Historical context",
                    "Current state of field",
                    "Key terminology"
                ],
                "estimated_length": plan.estimated_length // 5,
                "requires_research": True
            },
            {
                "title": "Current Research and Findings",
                "type": "research",
                "content_points": [
                    "Recent studies",
                    "Key findings",
                    "Methodologies"
                ],
                "estimated_length": plan.estimated_length // 3,
                "requires_research": True,
                "include_citations": True
            },
            {
                "title": "Analysis and Implications",
                "type": "analysis",
                "content_points": [
                    "Data interpretation",
                    "Practical implications",
                    "Future directions"
                ],
                "estimated_length": plan.estimated_length // 4,
                "requires_analysis": True
            }
        ]
    
    def _generate_analysis_sections(self, plan: ContentPlan) -> List[Dict[str, Any]]:
        """Generate analysis-heavy sections"""
        return [
            {
                "title": "Problem Definition",
                "type": "problem",
                "content_points": [
                    "Problem statement",
                    "Scope and constraints",
                    "Success criteria"
                ],
                "estimated_length": plan.estimated_length // 6
            },
            {
                "title": "Methodology and Approach",
                "type": "methodology",
                "content_points": [
                    "Analysis framework",
                    "Data sources",
                    "Evaluation criteria"
                ],
                "estimated_length": plan.estimated_length // 5
            },
            {
                "title": "Detailed Analysis",
                "type": "analysis",
                "content_points": [
                    "Core analysis",
                    "Data interpretation",
                    "Pattern identification"
                ],
                "estimated_length": plan.estimated_length // 3,
                "include_diagrams": plan.style_requirements.include_diagrams
            },
            {
                "title": "Results and Recommendations",
                "type": "results",
                "content_points": [
                    "Key findings",
                    "Actionable recommendations",
                    "Implementation guidance"
                ],
                "estimated_length": plan.estimated_length // 4
            }
        ]
    
    def _generate_opinion_sections(self, plan: ContentPlan) -> List[Dict[str, Any]]:
        """Generate opinion-centric sections"""
        return [
            {
                "title": "The Current Landscape",
                "type": "context",
                "content_points": [
                    "Current situation",
                    "Different perspectives",
                    "Why this matters"
                ],
                "estimated_length": plan.estimated_length // 4
            },
            {
                "title": "My Perspective",
                "type": "opinion",
                "content_points": [
                    "Core argument",
                    "Supporting evidence",
                    "Personal experience"
                ],
                "estimated_length": plan.estimated_length // 2
            },
            {
                "title": "Counterarguments and Response",
                "type": "debate",
                "content_points": [
                    "Alternative viewpoints",
                    "Addressing counterarguments",
                    "Finding common ground"
                ],
                "estimated_length": plan.estimated_length // 5
            }
        ]
    
    def _generate_narrative_sections(self, plan: ContentPlan) -> List[Dict[str, Any]]:
        """Generate narrative-focused sections"""
        return [
            {
                "title": "Setting the Scene",
                "type": "setup",
                "content_points": [
                    "Background story",
                    "Key characters",
                    "Initial situation"
                ],
                "estimated_length": plan.estimated_length // 5
            },
            {
                "title": "The Journey",
                "type": "narrative",
                "content_points": [
                    "Main story arc",
                    "Challenges faced",
                    "Solutions discovered"
                ],
                "estimated_length": plan.estimated_length // 2
            },
            {
                "title": "Lessons Learned",
                "type": "reflection",
                "content_points": [
                    "Key insights",
                    "Practical takeaways",
                    "How to apply"
                ],
                "estimated_length": plan.estimated_length // 4
            }
        ]
    
    def _generate_data_sections(self, plan: ContentPlan) -> List[Dict[str, Any]]:
        """Generate data-driven sections"""
        return [
            {
                "title": "Data Overview",
                "type": "data_intro",
                "content_points": [
                    "Data sources",
                    "Collection methodology",
                    "Data quality"
                ],
                "estimated_length": plan.estimated_length // 6
            },
            {
                "title": "Key Metrics and Trends",
                "type": "data_analysis",
                "content_points": [
                    "Primary metrics",
                    "Trend analysis",
                    "Statistical significance"
                ],
                "estimated_length": plan.estimated_length // 3,
                "include_diagrams": True
            },
            {
                "title": "Deep Dive Analysis",
                "type": "detailed_analysis",
                "content_points": [
                    "Correlation analysis",
                    "Causal relationships",
                    "Predictive insights"
                ],
                "estimated_length": plan.estimated_length // 3
            },
            {
                "title": "Actionable Insights",
                "type": "insights",
                "content_points": [
                    "Key takeaways",
                    "Business implications",
                    "Next steps"
                ],
                "estimated_length": plan.estimated_length // 5
            }
        ]
    
    def _generate_default_sections(self, plan: ContentPlan) -> List[Dict[str, Any]]:
        """Generate default sections for general content"""
        return [
            {
                "title": "Understanding the Basics",
                "type": "fundamentals",
                "content_points": [
                    "Core concepts",
                    "Key terminology",
                    "Why this matters"
                ],
                "estimated_length": plan.estimated_length // 4
            },
            {
                "title": "Practical Applications",
                "type": "application",
                "content_points": [
                    "Real-world examples",
                    "Use cases",
                    "Implementation tips"
                ],
                "estimated_length": plan.estimated_length // 3
            },
            {
                "title": "Best Practices and Tips",
                "type": "guidance",
                "content_points": [
                    "Expert recommendations",
                    "Common mistakes",
                    "Optimization strategies"
                ],
                "estimated_length": plan.estimated_length // 3
            }
        ]
    
    def _generate_conclusion_structure(self, plan: ContentPlan) -> Dict[str, Any]:
        """Generate conclusion structure"""
        return {
            "summary": {
                "key_points_recap": True,
                "main_takeaways": True,
                "learning_objectives_met": True
            },
            "call_to_action": {
                "next_steps": True,
                "additional_resources": plan.style_requirements.include_citations,
                "engagement_prompt": True
            },
            "future_outlook": {
                "upcoming_trends": plan.content_type in [ContentType.TECHNICAL_ARTICLE, ContentType.RESEARCH_REVIEW],
                "evolution_expectations": True,
                "continued_learning": True
            },
            "estimated_length": min(300, plan.estimated_length // 8)
        }
    
    def _generate_appendices(self, plan: ContentPlan) -> List[Dict[str, Any]]:
        """Generate appendices for complex content"""
        appendices = []
        
        if plan.style_requirements.include_citations:
            appendices.append({
                "title": "References and Further Reading",
                "type": "references",
                "content_points": [
                    "Primary sources",
                    "Additional resources",
                    "Related research"
                ]
            })
        
        if plan.style_requirements.include_code_snippets:
            appendices.append({
                "title": "Complete Code Examples",
                "type": "code",
                "content_points": [
                    "Full implementations",
                    "Configuration files",
                    "Testing code"
                ]
            })
        
        if plan.complexity == ContentComplexity.HIGHLY_TECHNICAL:
            appendices.append({
                "title": "Technical Specifications",
                "type": "specifications",
                "content_points": [
                    "Detailed specifications",
                    "API documentation",
                    "Configuration options"
                ]
            })
        
        return appendices
    
    def _generate_default_structure(self, plan: ContentPlan) -> ContentStructure:
        """Generate fallback structure"""
        return ContentStructure(
            introduction={
                "hook": {"type": "statement", "content_points": ["Opening statement"]},
                "context": {"background_info": True},
                "preview": {"what_readers_will_learn": True},
                "estimated_length": 150
            },
            main_sections=[
                {
                    "title": "Main Content",
                    "type": "content",
                    "content_points": ["Primary information", "Key details"],
                    "estimated_length": plan.estimated_length - 300
                }
            ],
            conclusion={
                "summary": {"key_points_recap": True},
                "call_to_action": {"next_steps": True},
                "estimated_length": 150
            },
            metadata={
                "total_sections": 1,
                "estimated_length": plan.estimated_length,
                "structure_type": "default"
            }
        )

class RequirementsGenerator:
    """Generates detailed requirements for content creation"""
    
    def __init__(self, model_registry=None):
        self.model_registry = model_registry
    
    def generate_research_requirements(self, content_plan: ContentPlan, 
                                     dynamic_params: Dict[str, Any] = None) -> ResearchRequirements:
        """Generate research requirements"""
        try:
            if not dynamic_params:
                dynamic_params = {}
            
            # Extract primary topics from the main topic
            primary_topics = self._extract_primary_topics(content_plan.topic)
            
            # Generate secondary topics based on content type and approach
            secondary_topics = self._generate_secondary_topics(content_plan)
            
            # Determine source requirements
            required_sources = self._determine_required_sources(content_plan)
            source_types = self._determine_source_types(content_plan)
            
            # Set depth and recency based on content characteristics
            depth_level = self._determine_depth_level(content_plan)
            recency_requirement = self._determine_recency_requirement(content_plan)
            
            return ResearchRequirements(
                primary_topics=primary_topics,
                secondary_topics=secondary_topics,
                required_sources=required_sources,
                source_types=source_types,
                depth_level=depth_level,
                recency_requirement=recency_requirement,
                credibility_threshold="high" if content_plan.complexity in [ContentComplexity.COMPLEX, ContentComplexity.HIGHLY_TECHNICAL] else "moderate"
            )
            
        except Exception as e:
            logger.error(f"Research requirements generation failed: {e}")
            return ResearchRequirements(
                primary_topics=[content_plan.topic],
                secondary_topics=[],
                required_sources=["academic", "industry"],
                source_types=["articles", "papers"],
                depth_level="moderate",
                recency_requirement="within_1_year",
                credibility_threshold="moderate"
            )
    
    def generate_style_requirements(self, content_plan: ContentPlan,
                                  style_profile: Dict[str, Any] = None) -> StyleRequirements:
        """Generate style requirements"""
        try:
            # Start with defaults based on content plan
            requirements = StyleRequirements()
            
            # Adjust based on target audience
            if content_plan.target_audience == Audience.BEGINNER:
                requirements.writing_style = "conversational"
                requirements.tone = "friendly"
                requirements.formality_level = "informal"
                requirements.technical_depth = "shallow"
                requirements.use_examples = True
            elif content_plan.target_audience == Audience.EXPERT:
                requirements.writing_style = "technical"
                requirements.tone = "authoritative"
                requirements.formality_level = "formal"
                requirements.technical_depth = "deep"
                requirements.include_citations = True
            elif content_plan.target_audience == Audience.TECHNICAL_PROFESSIONALS:
                requirements.writing_style = "professional"
                requirements.tone = "informative"
                requirements.formality_level = "formal"
                requirements.technical_depth = "moderate"
                requirements.include_code_snippets = True
                requirements.include_diagrams = True
            
            # Adjust based on content type
            if content_plan.content_type == ContentType.TUTORIAL:
                requirements.use_examples = True
                requirements.include_code_snippets = True
                requirements.writing_style = "instructional"
            elif content_plan.content_type == ContentType.RESEARCH_REVIEW:
                requirements.include_citations = True
                requirements.formality_level = "formal"
                requirements.technical_depth = "deep"
            elif content_plan.content_type == ContentType.OPINION_PIECE:
                requirements.writing_style = "persuasive"
                requirements.tone = "engaging"
                requirements.formality_level = "semi-formal"
            
            # Apply style profile overrides
            if style_profile:
                if "writing_style" in style_profile:
                    requirements.writing_style = style_profile["writing_style"]
                if "tone" in style_profile:
                    requirements.tone = style_profile["tone"]
                if "formality_level" in style_profile:
                    requirements.formality_level = style_profile["formality_level"]
                if "technical_depth" in style_profile:
                    requirements.technical_depth = style_profile["technical_depth"]
                if "use_examples" in style_profile:
                    requirements.use_examples = style_profile["use_examples"]
                if "include_code_snippets" in style_profile:
                    requirements.include_code_snippets = style_profile["include_code_snippets"]
                if "include_diagrams" in style_profile:
                    requirements.include_diagrams = style_profile["include_diagrams"]
                if "include_citations" in style_profile:
                    requirements.include_citations = style_profile["include_citations"]
            
            return requirements
            
        except Exception as e:
            logger.error(f"Style requirements generation failed: {e}")
            return StyleRequirements()
    
    def generate_seo_requirements(self, content_plan: ContentPlan,
                                dynamic_params: Dict[str, Any] = None) -> SEORequirements:
        """Generate SEO requirements"""
        try:
            if not dynamic_params:
                dynamic_params = {}
            
            # Extract target keywords from topic and parameters
            target_keywords = self._extract_keywords(content_plan.topic, dynamic_params)
            
            # Set keyword density based on content length
            keyword_density = 0.015 if content_plan.estimated_length > 2000 else 0.02
            
            # Adjust meta description length for content type
            meta_description_length = 160
            if content_plan.content_type == ContentType.SOCIAL_MEDIA:
                meta_description_length = 120
            
            return SEORequirements(
                target_keywords=target_keywords,
                keyword_density=keyword_density,
                meta_description_length=meta_description_length,
                title_length=60,
                header_structure=True,
                internal_linking=content_plan.estimated_length > 1000,
                external_linking=content_plan.style_requirements.include_citations,
                image_optimization=content_plan.style_requirements.include_diagrams
            )
            
        except Exception as e:
            logger.error(f"SEO requirements generation failed: {e}")
            return SEORequirements(
                target_keywords=[content_plan.topic],
                keyword_density=0.02,
                meta_description_length=160,
                title_length=60,
                header_structure=True,
                internal_linking=True,
                external_linking=True,
                image_optimization=True
            )
    
    def _extract_primary_topics(self, topic: str) -> List[str]:
        """Extract primary topics from main topic"""
        # Simple extraction - in production, use NLP
        words = topic.lower().split()
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Take significant terms
        primary_topics = [topic]  # Always include full topic
        
        # Add individual significant terms
        for word in filtered_words[:3]:  # Limit to top 3 terms
            if len(word) > 4:  # Only longer, more meaningful terms
                primary_topics.append(word)
        
        return list(set(primary_topics))  # Remove duplicates
    
    def _generate_secondary_topics(self, content_plan: ContentPlan) -> List[str]:
        """Generate secondary topics based on content plan"""
        secondary_topics = []
        
        # Add related topics based on content type
        if content_plan.content_type == ContentType.TECHNICAL_ARTICLE:
            secondary_topics.extend(["implementation", "best practices", "performance", "scalability"])
        elif content_plan.content_type == ContentType.TUTORIAL:
            secondary_topics.extend(["prerequisites", "setup", "troubleshooting", "next steps"])
        elif content_plan.content_type == ContentType.RESEARCH_REVIEW:
            secondary_topics.extend(["methodology", "findings", "implications", "future research"])
        elif content_plan.content_type == ContentType.CASE_STUDY:
            secondary_topics.extend(["background", "challenges", "solution", "results"])
        
        # Add topics based on complexity
        if content_plan.complexity in [ContentComplexity.COMPLEX, ContentComplexity.HIGHLY_TECHNICAL]:
            secondary_topics.extend(["advanced concepts", "technical details", "architecture"])
        
        return secondary_topics
    
    def _determine_required_sources(self, content_plan: ContentPlan) -> List[str]:
        """Determine required source types"""
        sources = ["industry articles", "expert opinions"]
        
        if content_plan.content_type == ContentType.RESEARCH_REVIEW:
            sources.extend(["academic papers", "peer-reviewed studies", "research data"])
        elif content_plan.content_type == ContentType.TECHNICAL_ARTICLE:
            sources.extend(["technical documentation", "official specs", "developer resources"])
        elif content_plan.content_type == ContentType.NEWS_ANALYSIS:
            sources.extend(["recent news", "press releases", "market reports"])
        elif content_plan.content_type == ContentType.TUTORIAL:
            sources.extend(["documentation", "examples", "best practices"])
        
        if content_plan.complexity in [ContentComplexity.COMPLEX, ContentComplexity.HIGHLY_TECHNICAL]:
            sources.extend(["authoritative sources", "primary documentation"])
        
        return sources
    
    def _determine_source_types(self, content_plan: ContentPlan) -> List[str]:
        """Determine types of sources to search for"""
        source_types = ["web articles", "blog posts"]
        
        if content_plan.style_requirements.include_citations:
            source_types.extend(["academic papers", "research studies"])
        
        if content_plan.content_type == ContentType.TECHNICAL_ARTICLE:
            source_types.extend(["documentation", "API references", "technical specs"])
        elif content_plan.content_type == ContentType.NEWS_ANALYSIS:
            source_types.extend(["news articles", "press releases", "reports"])
        
        return source_types
    
    def _determine_depth_level(self, content_plan: ContentPlan) -> str:
        """Determine research depth level"""
        if content_plan.complexity == ContentComplexity.SIMPLE:
            return "surface"
        elif content_plan.complexity == ContentComplexity.MODERATE:
            return "moderate"
        elif content_plan.complexity == ContentComplexity.COMPLEX:
            return "deep"
        elif content_plan.complexity == ContentComplexity.HIGHLY_TECHNICAL:
            return "comprehensive"
        else:
            return "moderate"
    
    def _determine_recency_requirement(self, content_plan: ContentPlan) -> str:
        """Determine how recent sources should be"""
        if content_plan.content_type == ContentType.NEWS_ANALYSIS:
            return "within_1_month"
        elif content_plan.content_type in [ContentType.TECHNICAL_ARTICLE, ContentType.TUTORIAL]:
            return "within_6_months"
        elif content_plan.content_type == ContentType.RESEARCH_REVIEW:
            return "within_2_years"
        else:
            return "within_1_year"
    
    def _extract_keywords(self, topic: str, dynamic_params: Dict[str, Any]) -> List[str]:
        """Extract SEO keywords"""
        keywords = []
        
        # Add explicit keywords from parameters
        if "keywords" in dynamic_params:
            keywords.extend(dynamic_params["keywords"])
        
        # Extract from topic
        keywords.append(topic)
        
        # Add variations
        words = topic.lower().split()
        if len(words) > 1:
            # Add individual significant words
            for word in words:
                if len(word) > 4:
                    keywords.append(word)
            
            # Add partial phrases
            if len(words) > 2:
                for i in range(len(words) - 1):
                    phrase = " ".join(words[i:i+2])
                    keywords.append(phrase)
        
        return list(set(keywords))  # Remove duplicates

class IntelligentPlannerAgent:
    """
    Intelligent Planner Agent that creates comprehensive content plans
    """
    
    def __init__(self, model_registry=None):
        self.model_registry = model_registry
        self.content_analyzer = ContentAnalyzer(model_registry)
        self.structure_generator = StructureGenerator(model_registry)
        self.requirements_generator = RequirementsGenerator(model_registry)
    
    async def intelligent_plan(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Main planning function with intelligent analysis"""
        start_time = time.time()
        
        try:
            # Extract input parameters
            topic = state.get("topic", "")
            dynamic_params = state.get("dynamic_parameters", {})
            style_profile = state.get("style_profile", {})
            
            if not topic:
                raise ValueError("Topic is required for content planning")
            
            logger.info(f"Starting intelligent planning for topic: {topic}")
            
            # Step 1: Analyze topic to determine content characteristics
            analysis_result = self.content_analyzer.analyze_topic(topic, dynamic_params)
            
            # Step 2: Create base content plan
            content_plan = ContentPlan(
                topic=topic,
                content_type=analysis_result["content_type"],
                target_audience=analysis_result["target_audience"],
                complexity=analysis_result["complexity"],
                approach=analysis_result["approach"],
                estimated_length=analysis_result["estimated_length"],
                estimated_read_time=analysis_result["estimated_read_time"]
            )
            
            # Step 3: Generate detailed structure
            content_plan.structure = self.structure_generator.generate_structure(content_plan)
            
            # Step 4: Generate requirements
            content_plan.research_requirements = self.requirements_generator.generate_research_requirements(
                content_plan, dynamic_params
            )
            content_plan.style_requirements = self.requirements_generator.generate_style_requirements(
                content_plan, style_profile
            )
            content_plan.seo_requirements = self.requirements_generator.generate_seo_requirements(
                content_plan, dynamic_params
            )
            
            # Step 5: Generate timeline and success metrics
            content_plan.timeline = self._generate_timeline(content_plan)
            content_plan.success_metrics = self._generate_success_metrics(content_plan)
            
            # Step 6: Add creation metadata
            content_plan.creation_metadata = {
                "planner_version": "1.0",
                "created_at": datetime.now().isoformat(),
                "planning_time_ms": int((time.time() - start_time) * 1000),
                "input_topic": topic,
                "dynamic_parameters": dynamic_params,
                "style_profile_applied": bool(style_profile)
            }
            
            # Step 7: Generate alternative plans if requested
            alternatives = []
            if dynamic_params.get("generate_alternatives", False):
                alternatives = await self._generate_alternative_plans(content_plan, dynamic_params)
            
            # Step 8: Generate recommendations and warnings
            recommendations = self._generate_recommendations(content_plan)
            warnings = self._generate_warnings(content_plan)
            
            # Step 9: Calculate confidence score
            confidence_score = self._calculate_planning_confidence(content_plan, analysis_result)
            
            # Create planning result
            planning_result = PlanningResult(
                plan=content_plan,
                confidence_score=confidence_score,
                planning_time_ms=int((time.time() - start_time) * 1000),
                reasoning=self._generate_reasoning(content_plan, analysis_result),
                alternatives=alternatives,
                warnings=warnings,
                recommendations=recommendations
            )
            
            # Format response for workflow
            response = {
                "content_plan": self._serialize_content_plan(content_plan),
                "planning_metadata": {
                    "confidence_score": confidence_score,
                    "planning_time_ms": planning_result.planning_time_ms,
                    "alternatives_count": len(alternatives),
                    "warnings_count": len(warnings),
                    "recommendations_count": len(recommendations),
                    "analysis_confidence": analysis_result["analysis_confidence"]
                },
                "planning_result": {
                    "status": "completed",
                    "reasoning": planning_result.reasoning,
                    "recommendations": recommendations,
                    "warnings": warnings
                },
                "research_guidance": {
                    "primary_topics": content_plan.research_requirements.primary_topics,
                    "secondary_topics": content_plan.research_requirements.secondary_topics,
                    "source_requirements": content_plan.research_requirements.required_sources,
                    "depth_level": content_plan.research_requirements.depth_level,
                    "recency_requirement": content_plan.research_requirements.recency_requirement
                },
                "structure_outline": {
                    "introduction": content_plan.structure.introduction,
                    "main_sections": content_plan.structure.main_sections,
                    "conclusion": content_plan.structure.conclusion,
                    "appendices": content_plan.structure.appendices,
                    "total_estimated_length": content_plan.estimated_length
                },
                "style_guidance": {
                    "writing_style": content_plan.style_requirements.writing_style,
                    "tone": content_plan.style_requirements.tone,
                    "formality_level": content_plan.style_requirements.formality_level,
                    "technical_depth": content_plan.style_requirements.technical_depth,
                    "include_examples": content_plan.style_requirements.use_examples,
                    "include_code": content_plan.style_requirements.include_code_snippets,
                    "include_diagrams": content_plan.style_requirements.include_diagrams,
                    "include_citations": content_plan.style_requirements.include_citations
                },
                "seo_guidance": {
                    "target_keywords": content_plan.seo_requirements.target_keywords,
                    "keyword_density": content_plan.seo_requirements.keyword_density,
                    "meta_description_length": content_plan.seo_requirements.meta_description_length,
                    "title_length": content_plan.seo_requirements.title_length,
                    "optimization_requirements": {
                        "header_structure": content_plan.seo_requirements.header_structure,
                        "internal_linking": content_plan.seo_requirements.internal_linking,
                        "external_linking": content_plan.seo_requirements.external_linking,
                        "image_optimization": content_plan.seo_requirements.image_optimization
                    }
                }
            }
            
            logger.info(f"Planning completed successfully in {planning_result.planning_time_ms}ms with confidence {confidence_score:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return {
                "content_plan": {},
                "planning_metadata": {
                    "confidence_score": 0.0,
                    "planning_time_ms": int((time.time() - start_time) * 1000),
                    "error": str(e)
                },
                "planning_result": {
                    "status": "failed",
                    "error": str(e),
                    "reasoning": f"Planning failed due to: {str(e)}"
                }
            }
    
    def _generate_timeline(self, content_plan: ContentPlan) -> Dict[str, Any]:
        """Generate content creation timeline"""
        # Base time estimates (in hours)
        base_times = {
            "research": content_plan.estimated_length // 300,  # 300 words per hour of research
            "writing": content_plan.estimated_length // 200,   # 200 words per hour of writing
            "editing": content_plan.estimated_length // 500,   # 500 words per hour of editing
            "formatting": 1,  # 1 hour for formatting
            "review": 1       # 1 hour for final review
        }
        
        # Adjust based on complexity
        complexity_multipliers = {
            ContentComplexity.SIMPLE: 0.8,
            ContentComplexity.MODERATE: 1.0,
            ContentComplexity.COMPLEX: 1.3,
            ContentComplexity.HIGHLY_TECHNICAL: 1.6
        }
        
        multiplier = complexity_multipliers.get(content_plan.complexity, 1.0)
        
        # Calculate adjusted times
        timeline = {}
        total_hours = 0
        
        for phase, hours in base_times.items():
            adjusted_hours = max(1, int(hours * multiplier))
            timeline[phase] = {
                "estimated_hours": adjusted_hours,
                "description": self._get_phase_description(phase, content_plan)
            }
            total_hours += adjusted_hours
        
        timeline["total_estimated_hours"] = total_hours
        timeline["estimated_days"] = max(1, total_hours // 6)  # Assuming 6 working hours per day
        
        return timeline
    
    def _generate_success_metrics(self, content_plan: ContentPlan) -> Dict[str, Any]:
        """Generate success metrics for content"""
        metrics = {
            "length_target": {
                "minimum": int(content_plan.estimated_length * 0.9),
                "target": content_plan.estimated_length,
                "maximum": int(content_plan.estimated_length * 1.1)
            },
            "readability": {
                "target_reading_level": self._get_target_reading_level(content_plan.target_audience),
                "sentence_length_max": 25,
                "paragraph_length_max": 150
            },
            "seo": {
                "keyword_density": content_plan.seo_requirements.keyword_density,
                "meta_description_length": content_plan.seo_requirements.meta_description_length,
                "title_length": content_plan.seo_requirements.title_length,
                "header_tags_required": True
            },
            "engagement": {
                "estimated_read_time": content_plan.estimated_read_time,
                "examples_required": content_plan.style_requirements.use_examples,
                "visual_elements": content_plan.style_requirements.include_diagrams,
                "actionable_takeaways": True
            },
            "quality": {
                "citations_required": content_plan.style_requirements.include_citations,
                "fact_checking_required": True,
                "expert_review_recommended": content_plan.complexity in [ContentComplexity.COMPLEX, ContentComplexity.HIGHLY_TECHNICAL]
            }
        }
        
        return metrics
    
    async def _generate_alternative_plans(self, base_plan: ContentPlan, 
                                        dynamic_params: Dict[str, Any]) -> List[ContentPlan]:
        """Generate alternative content plans"""
        alternatives = []
        
        try:
            # Alternative 1: Different content type
            if base_plan.content_type != ContentType.TUTORIAL:
                alt1 = self._create_alternative_plan(base_plan, content_type=ContentType.TUTORIAL)
                alternatives.append(alt1)
            
            # Alternative 2: Different target audience
            if base_plan.target_audience != Audience.BEGINNER:
                alt2 = self._create_alternative_plan(base_plan, target_audience=Audience.BEGINNER)
                alternatives.append(alt2)
            
            # Alternative 3: Different complexity
            if base_plan.complexity != ContentComplexity.SIMPLE:
                alt3 = self._create_alternative_plan(base_plan, complexity=ContentComplexity.SIMPLE)
                alternatives.append(alt3)
            
        except Exception as e:
            logger.warning(f"Failed to generate alternatives: {e}")
        
        return alternatives[:2]  # Limit to 2 alternatives
    
    def _create_alternative_plan(self, base_plan: ContentPlan, **overrides) -> ContentPlan:
        """Create alternative plan with specific overrides"""
        # Create copy of base plan
        alt_plan = ContentPlan(
            topic=base_plan.topic,
            content_type=overrides.get('content_type', base_plan.content_type),
            target_audience=overrides.get('target_audience', base_plan.target_audience),
            complexity=overrides.get('complexity', base_plan.complexity),
            approach=base_plan.approach
        )
        
        # Recalculate length and read time
        alt_plan.estimated_length, alt_plan.estimated_read_time = self.content_analyzer._estimate_length_and_time(
            alt_plan.content_type, alt_plan.complexity
        )
        
        # Regenerate structure and requirements
        alt_plan.structure = self.structure_generator.generate_structure(alt_plan)
        alt_plan.research_requirements = self.requirements_generator.generate_research_requirements(alt_plan)
        alt_plan.style_requirements = self.requirements_generator.generate_style_requirements(alt_plan)
        alt_plan.seo_requirements = self.requirements_generator.generate_seo_requirements(alt_plan)
        
        return alt_plan
    
    def _generate_recommendations(self, content_plan: ContentPlan) -> List[str]:
        """Generate recommendations for content creation"""
        recommendations = []
        
        # Length-based recommendations
        if content_plan.estimated_length > 3000:
            recommendations.append("Consider breaking this into multiple parts or sections for better readability")
        elif content_plan.estimated_length < 800:
            recommendations.append("Consider expanding with more examples or detailed explanations")
        
        # Audience-based recommendations
        if content_plan.target_audience == Audience.BEGINNER:
            recommendations.append("Include plenty of examples and avoid jargon")
            recommendations.append("Add a glossary of terms if using technical language")
        elif content_plan.target_audience == Audience.EXPERT:
            recommendations.append("Focus on advanced insights and nuanced analysis")
            recommendations.append("Include detailed technical specifications where relevant")
        
        # Content type recommendations
        if content_plan.content_type == ContentType.TUTORIAL:
            recommendations.append("Include step-by-step instructions with screenshots or code samples")
            recommendations.append("Add troubleshooting section for common issues")
        elif content_plan.content_type == ContentType.RESEARCH_REVIEW:
            recommendations.append("Ensure comprehensive literature review with recent sources")
            recommendations.append("Include methodology section explaining review approach")
        
        # Complexity recommendations
        if content_plan.complexity == ContentComplexity.HIGHLY_TECHNICAL:
            recommendations.append("Consider peer review by subject matter expert")
            recommendations.append("Include comprehensive references and citations")
        
        return recommendations
    
    def _generate_warnings(self, content_plan: ContentPlan) -> List[str]:
        """Generate warnings about potential challenges"""
        warnings = []
        
        # Length warnings
        if content_plan.estimated_length > 4000:
            warnings.append("Very long content may have lower engagement - consider breaking into series")
        
        # Complexity warnings
        if (content_plan.complexity == ContentComplexity.HIGHLY_TECHNICAL and 
            content_plan.target_audience in [Audience.BEGINNER, Audience.GENERAL_PUBLIC]):
            warnings.append("High complexity content for general audience may be difficult to understand")
        
        # Research warnings
        if (content_plan.content_type == ContentType.RESEARCH_REVIEW and 
            len(content_plan.research_requirements.primary_topics) > 5):
            warnings.append("Too many research topics may make content unfocused")
        
        # Timeline warnings
        total_hours = content_plan.timeline.get("total_estimated_hours", 0)
        if total_hours > 40:
            warnings.append("Estimated creation time is very high - consider simplifying scope")
        
        return warnings
    
    def _calculate_planning_confidence(self, content_plan: ContentPlan, 
                                     analysis_result: Dict[str, Any]) -> float:
        """Calculate confidence score for the planning result"""
        confidence = analysis_result.get("analysis_confidence", 0.7)
        
        # Boost confidence for well-defined plans
        if content_plan.structure.main_sections:
            confidence += 0.1
        
        if content_plan.research_requirements.primary_topics:
            confidence += 0.05
        
        if content_plan.estimated_length > 0:
            confidence += 0.05
        
        # Reduce confidence for overly complex plans
        if content_plan.complexity == ContentComplexity.HIGHLY_TECHNICAL:
            confidence -= 0.1
        
        if len(content_plan.research_requirements.primary_topics) > 5:
            confidence -= 0.05
        
        return min(1.0, max(0.1, confidence))
    
    def _generate_reasoning(self, content_plan: ContentPlan, 
                          analysis_result: Dict[str, Any]) -> str:
        """Generate reasoning explanation for the plan"""
        reasoning_parts = [
            f"Based on topic analysis, this content is best suited as a {content_plan.content_type.value} "
            f"targeting {content_plan.target_audience.value} audience.",
            
            f"The {content_plan.complexity.value} complexity level was chosen considering the technical depth required.",
            
            f"A {content_plan.approach.value} approach will provide the most value for this topic.",
            
            f"Estimated length of {content_plan.estimated_length} words should provide comprehensive coverage "
            f"while maintaining reader engagement (approximately {content_plan.estimated_read_time} minute read)."
        ]
        
        if content_plan.structure.main_sections:
            reasoning_parts.append(
                f"The content structure includes {len(content_plan.structure.main_sections)} main sections "
                f"to ensure logical flow and comprehensive coverage."
            )
        
        return " ".join(reasoning_parts)
    
    def _serialize_content_plan(self, content_plan: ContentPlan) -> Dict[str, Any]:
        """Serialize content plan to dictionary"""
        return {
            "topic": content_plan.topic,
            "content_type": content_plan.content_type.value,
            "target_audience": content_plan.target_audience.value,
            "complexity": content_plan.complexity.value,
            "approach": content_plan.approach.value,
            "estimated_length": content_plan.estimated_length,
            "estimated_read_time": content_plan.estimated_read_time,
            "timeline": content_plan.timeline,
            "success_metrics": content_plan.success_metrics,
            "creation_metadata": content_plan.creation_metadata
        }
    
    def _get_phase_description(self, phase: str, content_plan: ContentPlan) -> str:
        """Get description for timeline phase"""
        descriptions = {
            "research": f"Research {len(content_plan.research_requirements.primary_topics)} primary topics with {content_plan.research_requirements.depth_level} depth",
            "writing": f"Write {content_plan.estimated_length} words following {content_plan.approach.value} approach",
            "editing": f"Edit for {content_plan.style_requirements.tone} tone and {content_plan.style_requirements.formality_level} formality",
            "formatting": "Format with proper headers, links, and visual elements",
            "review": "Final review for quality, accuracy, and SEO optimization"
        }
        return descriptions.get(phase, f"Complete {phase} phase")
    
    def _get_target_reading_level(self, audience: Audience) -> str:
        """Get target reading level for audience"""
        levels = {
            Audience.BEGINNER: "8th grade",
            Audience.INTERMEDIATE: "10th grade", 
            Audience.ADVANCED: "12th grade",
            Audience.EXPERT: "College level",
            Audience.GENERAL_PUBLIC: "8th grade",
            Audience.TECHNICAL_PROFESSIONALS: "College level",
            Audience.BUSINESS_LEADERS: "12th grade",
            Audience.RESEARCHERS: "Graduate level",
            Audience.STUDENTS: "10th grade"
        }
        return levels.get(audience, "10th grade")

# Async wrapper function for workflow integration
async def _planner_fn(state: dict) -> dict:
    """Planner agent function for workflow integration"""
    planner_agent = IntelligentPlannerAgent()
    return await planner_agent.intelligent_plan(state)

# Export the agent
planner: RunnableLambda = RunnableLambda(_planner_fn)

# Class export for advanced usage
PlannerAgent = IntelligentPlannerAgent

# enhanced_planner.py - Add to the very end (if not already there):
from langchain_core.runnables import RunnableLambda

async def _enhanced_planner_fn(state: dict) -> dict:
    """Enhanced planner agent function for LangGraph workflow"""
    planner_agent = IntelligentPlannerAgent()
    return await planner_agent.intelligent_plan(state)


# FOR enhanced_planner.py - Add to the very end (if not already there):
from langchain_core.runnables import RunnableLambda

async def _enhanced_planner_fn(state: dict) -> dict:
    """Enhanced planner agent function for LangGraph workflow"""
    planner_agent = IntelligentPlannerAgent()
    return await planner_agent.intelligent_plan(state)

# Export the function
planner = RunnableLambda(_enhanced_planner_fn)
