# langgraph_app/agents/enhanced_planner.py
# FIXED VERSION - Proper Template/Style Profile Separation

import os
import logging
import time
from typing import Dict, Any, List, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from langchain_core.runnables import RunnableLambda
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
    BUSINESS_PROPOSAL = "business_proposal"
    TECHNICAL_DOCUMENTATION = "technical_documentation"

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

class ContentAnalyzer:
    """Analyzes topics and determines optimal content approach"""
    
    def __init__(self, model_registry=None):
        self.model_registry = model_registry
    
    def analyze_topic(self, topic: str, template_config: Dict[str, Any] = None, dynamic_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze topic to determine content characteristics with template integration"""
        try:
            if not dynamic_params:
                dynamic_params = {}
            if not template_config:
                template_config = {}
            
            topic_lower = topic.lower()
            
            # ✅ FIXED: Use template configuration to determine content type
            content_type = self._determine_content_type_from_template(template_config, topic_lower, dynamic_params)
            audience = self._determine_audience(topic_lower, dynamic_params, template_config)
            complexity = self._determine_complexity(topic_lower, dynamic_params, template_config)
            approach = self._determine_approach(topic_lower, dynamic_params, template_config)
            estimated_length, read_time = self._estimate_length_and_time(content_type, complexity, template_config)
            
            return {
                "content_type": content_type,
                "target_audience": audience,
                "complexity": complexity,
                "approach": approach,
                "estimated_length": estimated_length,
                "estimated_read_time": read_time,
                "analysis_confidence": self._calculate_confidence(topic, dynamic_params, template_config)
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
    
    def _determine_content_type_from_template(self, template_config: Dict, topic: str, params: Dict) -> ContentType:
        """✅ FIXED: Determine content type primarily from template configuration"""
        
        # First priority: Use template ID mapping
        template_id = template_config.get('id', '').lower()
        template_name = template_config.get('name', '').lower()
        
        if template_id == 'business_proposal' or 'business' in template_name or 'proposal' in template_name:
            return ContentType.BUSINESS_PROPOSAL
        elif template_id == 'technical_documentation' or template_id == 'technical_documents':
            return ContentType.TECHNICAL_DOCUMENTATION
        elif template_id == 'social_media_campaign' or 'social' in template_name:
            return ContentType.SOCIAL_MEDIA
        elif template_id == 'email_newsletter' or 'newsletter' in template_name:
            return ContentType.NEWSLETTER
        elif template_id == 'press_release' or 'press' in template_name:
            return ContentType.NEWS_ANALYSIS
        elif template_id == 'blog_article_generator' or 'blog' in template_name:
            return ContentType.BLOG_POST
        
        # Second priority: Use template category
        template_category = template_config.get('category', '').lower()
        if template_category == 'business':
            return ContentType.BUSINESS_PROPOSAL
        elif template_category == 'technical writing' or template_category == 'technical':
            return ContentType.TECHNICAL_DOCUMENTATION
        elif template_category == 'social media':
            return ContentType.SOCIAL_MEDIA
        
        # Fallback to topic-based detection
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
    
    def _determine_audience(self, topic: str, params: Dict, template_config: Dict) -> Audience:
        """Determine target audience with template guidance"""
        
        # Check template configuration first
        template_audience = template_config.get('targetAudience', '').lower()
        if 'developer' in template_audience or 'technical' in template_audience:
            return Audience.TECHNICAL_PROFESSIONALS
        elif 'business' in template_audience or 'professional' in template_audience:
            return Audience.BUSINESS_LEADERS
        elif 'beginner' in template_audience:
            return Audience.BEGINNER
        
        # Check dynamic parameters
        if "target_audience" in params:
            try:
                return Audience(params["target_audience"].lower())
            except ValueError:
                pass
        
        # Topic-based fallback
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
    
    def _determine_complexity(self, topic: str, params: Dict, template_config: Dict) -> ContentComplexity:
        """Determine content complexity with template guidance"""
        
        # Check template difficulty
        template_difficulty = template_config.get('difficulty', '').lower()
        if template_difficulty == 'beginner':
            return ContentComplexity.SIMPLE
        elif template_difficulty == 'intermediate':
            return ContentComplexity.MODERATE
        elif template_difficulty == 'advanced':
            return ContentComplexity.COMPLEX
        
        # Dynamic parameters
        if "complexity" in params:
            try:
                return ContentComplexity(params["complexity"].lower())
            except ValueError:
                pass
        
        # Topic-based fallback
        if any(word in topic for word in ["simple", "basic", "easy", "beginner"]):
            return ContentComplexity.SIMPLE
        elif any(word in topic for word in ["advanced", "complex", "sophisticated"]):
            return ContentComplexity.COMPLEX
        elif any(word in topic for word in ["technical", "algorithmic", "mathematical"]):
            return ContentComplexity.HIGHLY_TECHNICAL
        else:
            return ContentComplexity.MODERATE
    
    def _determine_approach(self, topic: str, params: Dict, template_config: Dict) -> PlanningApproach:
        """Determine planning approach with template guidance"""
        
        # Check template category for approach hints
        template_category = template_config.get('category', '').lower()
        if template_category == 'business':
            return PlanningApproach.DATA_DRIVEN
        elif template_category == 'technical':
            return PlanningApproach.TUTORIAL_BASED
        
        if "approach" in params:
            try:
                return PlanningApproach(params["approach"].lower())
            except ValueError:
                pass
        
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
    
    def _estimate_length_and_time(self, content_type: ContentType, complexity: ContentComplexity, template_config: Dict) -> Tuple[int, int]:
        """Estimate content length and reading time with template guidance"""
        
        # Check template estimated length first
        template_length = template_config.get('estimatedLength', '')
        if isinstance(template_length, str):
            if '20-30' in template_length:
                base_length = 3000  # 20-30 min read
            elif '15-25' in template_length:
                base_length = 2500
            elif '10-15' in template_length:
                base_length = 1500
            else:
                base_length = self._get_default_length_for_type(content_type)
        else:
            base_length = self._get_default_length_for_type(content_type)
        
        complexity_multipliers = {
            ContentComplexity.SIMPLE: 0.8,
            ContentComplexity.MODERATE: 1.0,
            ContentComplexity.COMPLEX: 1.3,
            ContentComplexity.HIGHLY_TECHNICAL: 1.6
        }
        
        multiplier = complexity_multipliers.get(complexity, 1.0)
        estimated_length = int(base_length * multiplier)
        read_time = max(1, estimated_length // 200)  # 200 words per minute
        
        return estimated_length, read_time
    
    def _get_default_length_for_type(self, content_type: ContentType) -> int:
        """Get default length for content type"""
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
            ContentType.NEWSLETTER: 800,
            ContentType.BUSINESS_PROPOSAL: 2500,
            ContentType.TECHNICAL_DOCUMENTATION: 3000
        }
        return base_lengths.get(content_type, 1500)
    
    def _calculate_confidence(self, topic: str, params: Dict, template_config: Dict) -> float:
        """Calculate confidence score for analysis"""
        confidence = 0.7  # Base confidence
        
        if template_config:
            confidence += 0.15  # Template provides structure
        if "content_type" in params:
            confidence += 0.1
        if "target_audience" in params:
            confidence += 0.05
        
        topic_lower = topic.lower()
        if any(word in topic_lower for word in ["tutorial", "guide", "how to", "introduction"]):
            confidence += 0.05
        
        return min(1.0, confidence)

class IntelligentPlannerAgent:
    """✅ FIXED: Intelligent Planner Agent with proper template/style separation"""
    
    def __init__(self, model_registry=None):
        self.model_registry = model_registry
        self.content_analyzer = ContentAnalyzer(model_registry)
    
    async def intelligent_plan(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """✅ FIXED: Main planning function with proper template/style handling"""
        start_time = time.time()
        
        try:
            # ✅ FIXED: Robust parameter extraction with proper fallbacks
            template_id = state.get("template", "blog_article_generator")
            style_profile_id = state.get("style_profile", "popular_sci")  # Better default
            
            # Extract topic with better fallback logic - NO MORE "Future of LLMs" default!
            topic = (
                state.get("topic") or 
                state.get("dynamic_parameters", {}).get("topic") or
                state.get("template_config", {}).get("name", "").replace("_", " ").title() or
                f"Content using {template_id.replace('_', ' ').title()}"
            )
            
            dynamic_params = state.get("dynamic_parameters", {})
            
            logger.info(f"🎯 Planning content: Template='{template_id}', Style='{style_profile_id}', Topic='{topic}'")
            
            # ✅ FIXED: Load template and style profile separately
            template_config = self._load_template_config(template_id)
            style_profile = self._load_style_profile(style_profile_id)
            
            if not template_config:
                logger.warning(f"Template '{template_id}' not found, using default structure")
                template_config = self._get_default_template_config(template_id)
            
            if not style_profile:
                logger.warning(f"Style profile '{style_profile_id}' not found, using default style")
                style_profile = self._get_default_style_profile(style_profile_id)
            
            # ✅ FIXED: Analyze topic with template configuration
            analysis_result = self.content_analyzer.analyze_topic(topic, template_config, dynamic_params)
            
            # Create comprehensive content plan
            content_plan = ContentPlan(
                topic=topic,
                content_type=analysis_result["content_type"],
                target_audience=analysis_result["target_audience"],
                complexity=analysis_result["complexity"],
                approach=analysis_result["approach"],
                estimated_length=analysis_result["estimated_length"],
                estimated_read_time=analysis_result["estimated_read_time"]
            )
            
            # Generate plan components with template and style integration
            content_plan.structure = self._generate_structure(content_plan, template_config)
            content_plan.research_requirements = self._generate_research_requirements(content_plan, dynamic_params)
            content_plan.style_requirements = self._generate_style_requirements(content_plan, style_profile)
            content_plan.seo_requirements = self._generate_seo_requirements(content_plan, dynamic_params)
            content_plan.timeline = self._generate_timeline(content_plan)
            content_plan.success_metrics = self._generate_success_metrics(content_plan)
            
            # Add creation metadata
            planning_time_ms = int((time.time() - start_time) * 1000)
            content_plan.creation_metadata = {
                "planner_version": "3.0.0",  # Updated version
                "created_at": datetime.now().isoformat(),
                "planning_time_ms": planning_time_ms,
                "template_id": template_id,
                "style_profile_id": style_profile_id,
                "input_topic": topic,
                "dynamic_parameters": dynamic_params,
                "template_loaded": bool(template_config),
                "style_profile_loaded": bool(style_profile)
            }
            
            # Calculate confidence and generate guidance
            confidence_score = min(1.0, analysis_result["analysis_confidence"] + 0.2)
            recommendations = self._generate_recommendations(content_plan, template_config, style_profile)
            
            # ✅ ENHANCED: Create comprehensive response with clear separation
            response = {
                "content_plan": self._serialize_content_plan(content_plan),
                "template_metadata": {
                    "template_id": template_id,
                    "template_name": template_config.get("name", template_id),
                    "template_category": template_config.get("category", "general"),
                    "template_loaded": bool(template_config)
                },
                "style_metadata": {
                    "style_profile_id": style_profile_id,
                    "style_name": style_profile.get("name", style_profile_id),
                    "style_category": style_profile.get("category", "general"),
                    "style_loaded": bool(style_profile),
                    "tone": style_profile.get("tone", "professional"),
                    "voice": style_profile.get("voice", "authoritative")
                },
                "planning_metadata": {
                    "confidence_score": confidence_score,
                    "planning_time_ms": planning_time_ms,
                    "analysis_confidence": analysis_result["analysis_confidence"]
                },
                "planning_result": {
                    "status": "completed",
                    "reasoning": self._generate_reasoning(content_plan, analysis_result, template_config, style_profile),
                    "recommendations": recommendations
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
                }
            }
            
            logger.info(f"✅ Planning completed successfully in {planning_time_ms}ms with confidence {confidence_score:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Planning failed: {e}")
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
    
    def _load_template_config(self, template_id: str) -> Dict[str, Any]:
        """✅ FIXED: Load template configuration from template loader"""
        try:
            from langgraph_app.template_loader import template_loader
            template_config = template_loader.get_template(template_id)
            if template_config:
                logger.info(f"✅ Loaded template config for '{template_id}'")
                return template_config
            else:
                logger.warning(f"⚠️ Template '{template_id}' not found in template loader")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to load template '{template_id}': {e}")
            return {}
    
    def _load_style_profile(self, style_profile_id: str) -> Dict[str, Any]:
        """✅ FIXED: Load style profile configuration from style profile loader"""
        try:
            from langgraph_app.style_profile_loader import style_profile_loader
            style_profile = style_profile_loader.get_profile(style_profile_id)
            if style_profile:
                logger.info(f"✅ Loaded style profile for '{style_profile_id}'")
                return style_profile
            else:
                logger.warning(f"⚠️ Style profile '{style_profile_id}' not found in style profile loader")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to load style profile '{style_profile_id}': {e}")
            return {}
    
    def _get_default_template_config(self, template_id: str) -> Dict[str, Any]:
        """Provide sensible default template configuration"""
        return {
            "id": template_id,
            "name": template_id.replace("_", " ").title(),
            "category": "general",
            "difficulty": "intermediate",
            "estimatedLength": "10-15 min",
            "description": f"Content template for {template_id.replace('_', ' ')}"
        }
    
    def _get_default_style_profile(self, style_profile_id: str) -> Dict[str, Any]:
        """Provide sensible default style profile"""
        return {
            "id": style_profile_id,
            "name": style_profile_id.replace("_", " ").title(),
            "category": "general",
            "tone": "professional",
            "voice": "authoritative",
            "system_prompt": f"Write in a {style_profile_id.replace('_', ' ')} style.",
            "settings": {
                "use_analogies": True,
                "avoid_jargon": False,
                "include_examples": True,
                "conversational_tone": False
            }
        }
    
    def _generate_structure(self, content_plan: ContentPlan, template_config: Dict[str, Any]) -> ContentStructure:
        """Generate content structure with template guidance"""
        structure = ContentStructure()
        
        # Use template suggested sections if available
        suggested_sections = template_config.get("suggested_sections", [])
        if suggested_sections:
            structure.main_sections = []
            for section in suggested_sections:
                section_dict = {
                    "title": section.get("name", "Section").replace("_", " ").title(),
                    "description": section.get("description", ""),
                    "type": section.get("name", "content"),
                    "estimated_length": content_plan.estimated_length // max(len(suggested_sections), 1)
                }
                structure.main_sections.append(section_dict)
        else:
            # Use default structure generation logic
            structure = self._generate_default_structure(content_plan)
        
        structure.introduction = {
            "hook": {"type": "question" if content_plan.target_audience in [Audience.BEGINNER, Audience.GENERAL_PUBLIC] else "statement"},
            "context": {"background_info": True, "current_state": True},
            "preview": {"what_readers_will_learn": True},
            "estimated_length": min(200, content_plan.estimated_length // 10)
        }
        
        structure.conclusion = {
            "summary": {"key_points_recap": True, "main_takeaways": True},
            "call_to_action": {"next_steps": True},
            "estimated_length": min(300, content_plan.estimated_length // 8)
        }
        
        structure.metadata = {
            "total_sections": len(structure.main_sections),
            "estimated_length": content_plan.estimated_length,
            "generated_at": datetime.now().isoformat(),
            "template_guided": bool(suggested_sections)
        }
        
        return structure
    
    def _generate_default_structure(self, content_plan: ContentPlan) -> ContentStructure:
        """Generate default structure when template doesn't provide suggestions"""
        structure = ContentStructure()
        
        if content_plan.approach == PlanningApproach.TUTORIAL_BASED:
            structure.main_sections = [
                {"title": "Prerequisites and Setup", "type": "preparation", "estimated_length": content_plan.estimated_length // 8},
                {"title": "Step-by-Step Implementation", "type": "implementation", "estimated_length": content_plan.estimated_length // 2},
                {"title": "Testing and Validation", "type": "validation", "estimated_length": content_plan.estimated_length // 6}
            ]
        elif content_plan.content_type == ContentType.BUSINESS_PROPOSAL:
            structure.main_sections = [
                {"title": "Executive Summary", "type": "overview", "estimated_length": content_plan.estimated_length // 5},
                {"title": "Problem Statement", "type": "problem", "estimated_length": content_plan.estimated_length // 4},
                {"title": "Proposed Solution", "type": "solution", "estimated_length": content_plan.estimated_length // 3},
                {"title": "Timeline and Budget", "type": "logistics", "estimated_length": content_plan.estimated_length // 6}
            ]
        elif content_plan.content_type == ContentType.TECHNICAL_DOCUMENTATION:
            structure.main_sections = [
                {"title": "Getting Started", "type": "introduction", "estimated_length": content_plan.estimated_length // 6},
                {"title": "API Reference", "type": "reference", "estimated_length": content_plan.estimated_length // 2},
                {"title": "Examples and Use Cases", "type": "examples", "estimated_length": content_plan.estimated_length // 4},
                {"title": "Troubleshooting", "type": "support", "estimated_length": content_plan.estimated_length // 8}
            ]
        else:
            structure.main_sections = [
                {"title": "Understanding the Basics", "type": "fundamentals", "estimated_length": content_plan.estimated_length // 4},
                {"title": "Practical Applications", "type": "application", "estimated_length": content_plan.estimated_length // 3},
                {"title": "Best Practices", "type": "guidance", "estimated_length": content_plan.estimated_length // 3}
            ]
        
        return structure
    
    def _generate_research_requirements(self, content_plan: ContentPlan, dynamic_params: Dict[str, Any]) -> ResearchRequirements:
        """Generate research requirements"""
        primary_topics = [content_plan.topic]
        words = content_plan.topic.lower().split()
        for word in words:
            if len(word) > 4:
                primary_topics.append(word)
        
        return ResearchRequirements(
            primary_topics=primary_topics[:5],
            secondary_topics=["best practices", "examples", "case studies"],
            required_sources=["industry articles", "expert opinions"],
            source_types=["web articles", "blog posts"],
            depth_level="moderate",
            recency_requirement="within_1_year",
            credibility_threshold="moderate"
        )
    
    def _generate_style_requirements(self, content_plan: ContentPlan, style_profile: Dict[str, Any]) -> StyleRequirements:
        """✅ FIXED: Generate style requirements with proper style profile integration"""
        requirements = StyleRequirements()
        
        # Apply style profile overrides if available
        if style_profile:
            # Map style profile fields to requirements
            if "tone" in style_profile:
                requirements.tone = style_profile["tone"]
            if "voice" in style_profile:
                requirements.writing_style = style_profile["voice"]
            
            # Apply settings if available
            settings = style_profile.get("settings", {})
            if isinstance(settings, dict):
                requirements.use_examples = settings.get("include_examples", True)
                requirements.include_code_snippets = settings.get("code_blocks", "minimal") != "minimal"
                requirements.include_citations = not settings.get("avoid_jargon", False)
            
            # Apply length limits if specified
            length_limits = style_profile.get("length_limit", {})
            if isinstance(length_limits, dict):
                if "words" in length_limits:
                    # Adjust estimated length based on style profile
                    target_words = length_limits["words"]
                    if target_words != content_plan.estimated_length:
                        logger.info(f"Adjusting length from {content_plan.estimated_length} to {target_words} words based on style profile")
        
        return requirements
    
    def _generate_seo_requirements(self, content_plan: ContentPlan, dynamic_params: Dict[str, Any]) -> SEORequirements:
        """Generate SEO requirements"""
        keywords = [content_plan.topic]
        if "keywords" in dynamic_params:
            keywords.extend(dynamic_params["keywords"])
        
        return SEORequirements(
            target_keywords=keywords[:5],
            keyword_density=0.02,
            meta_description_length=160,
            title_length=60,
            header_structure=True,
            internal_linking=True,
            external_linking=True,
            image_optimization=True
        )
    
    def _generate_timeline(self, content_plan: ContentPlan) -> Dict[str, Any]:
        """Generate content creation timeline"""
        base_hours = {
            "research": max(1, content_plan.estimated_length // 300),
            "writing": max(2, content_plan.estimated_length // 200),
            "editing": max(1, content_plan.estimated_length // 500),
            "review": 1
        }
        
        total_hours = sum(base_hours.values())
        return {
            **base_hours,
            "total_estimated_hours": total_hours,
            "estimated_days": max(1, total_hours // 6)
        }
    
    def _generate_success_metrics(self, content_plan: ContentPlan) -> Dict[str, Any]:
        """Generate success metrics"""
        return {
            "length_target": {
                "minimum": int(content_plan.estimated_length * 0.9),
                "target": content_plan.estimated_length,
                "maximum": int(content_plan.estimated_length * 1.1)
            },
            "readability": {"target_reading_level": "10th grade", "sentence_length_max": 25},
            "engagement": {"estimated_read_time": content_plan.estimated_read_time, "examples_required": True}
        }
    
    def _generate_recommendations(self, content_plan: ContentPlan, template_config: Dict[str, Any], style_profile: Dict[str, Any]) -> List[str]:
        """✅ ENHANCED: Generate recommendations with template and style awareness"""
        recommendations = []
        
        # Template-specific recommendations
        template_category = template_config.get("category", "").lower()
        if template_category == "business":
            recommendations.append("Include specific metrics and ROI projections for business impact")
        elif template_category == "technical writing":
            recommendations.append("Provide code examples and clear API documentation")
        elif template_category == "social media":
            recommendations.append("Optimize for platform-specific engagement and hashtags")
        
        # Content length recommendations
        if content_plan.estimated_length > 3000:
            recommendations.append("Consider breaking into multiple sections for better readability")
        
        # Audience-specific recommendations
        if content_plan.target_audience == Audience.BEGINNER:
            recommendations.append("Include plenty of examples and avoid jargon")
        elif content_plan.target_audience == Audience.TECHNICAL_PROFESSIONALS:
            recommendations.append("Include technical details and implementation specifics")
        
        # Content type recommendations
        if content_plan.content_type == ContentType.TUTORIAL:
            recommendations.append("Include step-by-step instructions with examples")
        elif content_plan.content_type == ContentType.BUSINESS_PROPOSAL:
            recommendations.append("Focus on clear value proposition and actionable next steps")
        
        # Style profile recommendations
        if style_profile:
            tone = style_profile.get("tone", "")
            if "scientific" in tone:
                recommendations.append("Maintain objectivity and include proper citations")
            elif "educational" in tone:
                recommendations.append("Use clear explanations and learning objectives")
        
        return recommendations
    
    def _generate_reasoning(self, content_plan: ContentPlan, analysis_result: Dict[str, Any], template_config: Dict[str, Any], style_profile: Dict[str, Any]) -> str:
        """✅ ENHANCED: Generate reasoning explanation with template and style context"""
        template_name = template_config.get("name", "Unknown Template")
        style_name = style_profile.get("name", "Unknown Style")
        
        reasoning = (
            f"Based on template '{template_name}' and style profile '{style_name}', "
            f"this content is optimized as a {content_plan.content_type.value} "
            f"targeting {content_plan.target_audience.value} audience with {content_plan.complexity.value} complexity. "
            f"Estimated {content_plan.estimated_length} words for approximately {content_plan.estimated_read_time} minute read."
        )
        
        return reasoning
    
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

# Export the agent function
async def _enhanced_planner_fn(state: dict) -> dict:
    """✅ FIXED: Enhanced planner agent function for LangGraph workflow"""
    planner_agent = IntelligentPlannerAgent()
    return await planner_agent.intelligent_plan(state)

planner = RunnableLambda(_enhanced_planner_fn)