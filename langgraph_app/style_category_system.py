# File: langgraph_app/style_category_system.py
# Professional Style Profile Category System with Content Template Alignment

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class StyleProfile:
    """Enhanced style profile with category information"""
    id: str
    name: str
    description: str
    category: str
    subcategory: str
    content_templates: List[str]
    target_audience: str
    complexity_level: str
    use_cases: List[str]
    profile_data: Dict[str, Any]

@dataclass
class ContentTemplate:
    """Enhanced content template with style alignment"""
    id: str
    name: str
    description: str
    category: str
    recommended_styles: List[str]
    target_outcome: str
    typical_length: str
    template_data: Dict[str, Any]

class StyleCategory(Enum):
    """Professional style categories"""
    ACADEMIC_RESEARCH = "academic_research"
    TECHNICAL_DOCUMENTATION = "technical_documentation" 
    BUSINESS_STRATEGY = "business_strategy"
    EDUCATIONAL_CONTENT = "educational_content"
    MARKETING_COMMUNICATIONS = "marketing_communications"
    HEALTHCARE_MEDICAL = "healthcare_medical"
    POLICY_ANALYSIS = "policy_analysis"
    CREATIVE_STORYTELLING = "creative_storytelling"
    FINANCIAL_ANALYSIS = "financial_analysis"
    SCIENTIFIC_REPORTING = "scientific_reporting"

class ContentCategory(Enum):
    """Content template categories"""
    BLOG_ARTICLES = "blog_articles"
    TECHNICAL_DOCUMENTS = "technical_documents"
    BUSINESS_PROPOSALS = "business_proposals"
    EMAIL_COMMUNICATIONS = "email_communications"
    SOCIAL_MEDIA_CAMPAIGNS = "social_media_campaigns"
    PRESS_RELEASES = "press_releases"
    RESEARCH_PAPERS = "research_papers"
    EDUCATIONAL_MATERIALS = "educational_materials"
    MARKETING_CONTENT = "marketing_content"
    POLICY_DOCUMENTS = "policy_documents"

class ProfessionalStyleCategorySystem:
    """Professional system for organizing style profiles and content templates"""
    
    def __init__(self):
        self.style_profiles: Dict[str, StyleProfile] = {}
        self.content_templates: Dict[str, ContentTemplate] = {}
        self.category_mappings = self._initialize_category_mappings()
        self.recommended_combinations = self._initialize_recommendations()
    
    def _initialize_category_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive category mappings"""
        return {
            # ACADEMIC RESEARCH CATEGORY
            StyleCategory.ACADEMIC_RESEARCH.value: {
                "name": "Academic & Research",
                "description": "Scholarly writing for academic institutions, research papers, and peer-reviewed publications",
                "style_profiles": [
                    {
                        "id": "phd_dissertation",
                        "name": "PhD Dissertation",
                        "description": "Formal academic writing for doctoral dissertations",
                        "complexity": "expert",
                        "audience": "academic_committee"
                    },
                    {
                        "id": "peer_review_article", 
                        "name": "Peer Review Article",
                        "description": "Rigorous academic style for journal submissions",
                        "complexity": "expert",
                        "audience": "researchers"
                    },
                    {
                        "id": "literature_review",
                        "name": "Literature Review",
                        "description": "Comprehensive review of existing research",
                        "complexity": "advanced",
                        "audience": "academics"
                    },
                    {
                        "id": "research_proposal",
                        "name": "Research Proposal", 
                        "description": "Formal proposal for research funding",
                        "complexity": "advanced",
                        "audience": "funding_committees"
                    },
                    {
                        "id": "conference_abstract",
                        "name": "Conference Abstract",
                        "description": "Concise academic summaries for conferences",
                        "complexity": "intermediate",
                        "audience": "conference_attendees"
                    },
                    {
                        "id": "academic_book_chapter",
                        "name": "Academic Book Chapter",
                        "description": "Scholarly writing for academic publications",
                        "complexity": "expert",
                        "audience": "academic_readers"
                    },
                    {
                        "id": "thesis_defense",
                        "name": "Thesis Defense",
                        "description": "Presentation-ready academic content",
                        "complexity": "advanced",
                        "audience": "defense_committee"
                    },
                    {
                        "id": "grant_application",
                        "name": "Grant Application",
                        "description": "Persuasive academic writing for funding",
                        "complexity": "expert",
                        "audience": "grant_reviewers"
                    },
                    {
                        "id": "scholarly_commentary",
                        "name": "Scholarly Commentary",
                        "description": "Expert commentary on academic topics",
                        "complexity": "advanced",
                        "audience": "scholarly_community"
                    },
                    {
                        "id": "methodology_paper",
                        "name": "Methodology Paper",
                        "description": "Technical academic writing on research methods",
                        "complexity": "expert",
                        "audience": "methodologists"
                    }
                ],
                "content_templates": ["research_papers", "academic_articles", "dissertation_chapters"]
            },

            # TECHNICAL DOCUMENTATION CATEGORY
            StyleCategory.TECHNICAL_DOCUMENTATION.value: {
                "name": "Technical Documentation",
                "description": "Precise technical writing for developers, engineers, and technical professionals",
                "style_profiles": [
                    {
                        "id": "api_documentation",
                        "name": "API Documentation",
                        "description": "Clear technical documentation for APIs",
                        "complexity": "advanced",
                        "audience": "developers"
                    },
                    {
                        "id": "system_architecture",
                        "name": "System Architecture", 
                        "description": "Comprehensive system design documentation",
                        "complexity": "expert",
                        "audience": "architects"
                    },
                    {
                        "id": "implementation_guide",
                        "name": "Implementation Guide",
                        "description": "Step-by-step technical implementation",
                        "complexity": "intermediate",
                        "audience": "implementers"
                    },
                    {
                        "id": "troubleshooting_manual",
                        "name": "Troubleshooting Manual",
                        "description": "Problem-solving technical documentation",
                        "complexity": "advanced",
                        "audience": "support_engineers"
                    },
                    {
                        "id": "code_review_standards",
                        "name": "Code Review Standards",
                        "description": "Technical standards and best practices",
                        "complexity": "advanced",
                        "audience": "development_teams"
                    },
                    {
                        "id": "technical_specification",
                        "name": "Technical Specification",
                        "description": "Detailed technical requirements",
                        "complexity": "expert",
                        "audience": "engineers"
                    },
                    {
                        "id": "deployment_guide",
                        "name": "Deployment Guide",
                        "description": "Production deployment procedures",
                        "complexity": "advanced",
                        "audience": "devops_engineers"
                    },
                    {
                        "id": "security_protocol",
                        "name": "Security Protocol",
                        "description": "Technical security documentation",
                        "complexity": "expert",
                        "audience": "security_engineers"
                    },
                    {
                        "id": "performance_analysis",
                        "name": "Performance Analysis",
                        "description": "Technical performance evaluation",
                        "complexity": "advanced",
                        "audience": "performance_engineers"
                    },
                    {
                        "id": "integration_manual",
                        "name": "Integration Manual",
                        "description": "System integration documentation",
                        "complexity": "advanced",
                        "audience": "integration_specialists"
                    }
                ],
                "content_templates": ["technical_documents", "api_guides", "system_manuals"]
            },

            # BUSINESS STRATEGY CATEGORY
            StyleCategory.BUSINESS_STRATEGY.value: {
                "name": "Business Strategy",
                "description": "Strategic business communication for executives, stakeholders, and decision-makers",
                "style_profiles": [
                    {
                        "id": "executive_summary",
                        "name": "Executive Summary",
                        "description": "Concise strategic overview for executives",
                        "complexity": "advanced",
                        "audience": "c_suite"
                    },
                    {
                        "id": "business_case_analysis",
                        "name": "Business Case Analysis",
                        "description": "Comprehensive business justification",
                        "complexity": "advanced",
                        "audience": "decision_makers"
                    },
                    {
                        "id": "market_research_report",
                        "name": "Market Research Report",
                        "description": "Data-driven market analysis",
                        "complexity": "intermediate",
                        "audience": "business_analysts"
                    },
                    {
                        "id": "strategic_planning",
                        "name": "Strategic Planning",
                        "description": "Long-term strategic documentation",
                        "complexity": "expert",
                        "audience": "strategic_planners"
                    },
                    {
                        "id": "investor_presentation",
                        "name": "Investor Presentation",
                        "description": "Professional investor communication",
                        "complexity": "advanced",
                        "audience": "investors"
                    },
                    {
                        "id": "competitive_analysis",
                        "name": "Competitive Analysis",
                        "description": "Comprehensive competitor evaluation",
                        "complexity": "intermediate",
                        "audience": "strategy_teams"
                    },
                    {
                        "id": "roi_analysis",
                        "name": "ROI Analysis",
                        "description": "Financial return evaluation",
                        "complexity": "advanced",
                        "audience": "financial_analysts"
                    },
                    {
                        "id": "venture_capital_pitch",
                        "name": "Venture Capital Pitch",
                        "description": "Startup funding presentation",
                        "complexity": "advanced",
                        "audience": "vc_partners"
                    },
                    {
                        "id": "merger_acquisition",
                        "name": "Merger & Acquisition",
                        "description": "M&A strategic documentation",
                        "complexity": "expert",
                        "audience": "corporate_development"
                    },
                    {
                        "id": "board_presentation",
                        "name": "Board Presentation",
                        "description": "Board-level strategic communication",
                        "complexity": "expert",
                        "audience": "board_members"
                    }
                ],
                "content_templates": ["business_proposals", "strategic_plans", "investor_decks"]
            },

            # EDUCATIONAL CONTENT CATEGORY
            StyleCategory.EDUCATIONAL_CONTENT.value: {
                "name": "Educational Content",
                "description": "Instructional content for learning, training, and knowledge transfer",
                "style_profiles": [
                    {
                        "id": "beginner_tutorial",
                        "name": "Beginner Tutorial",
                        "description": "Friendly introduction for newcomers",
                        "complexity": "beginner",
                        "audience": "beginners"
                    },
                    {
                        "id": "advanced_masterclass",
                        "name": "Advanced Masterclass",
                        "description": "Expert-level educational content",
                        "complexity": "expert",
                        "audience": "advanced_learners"
                    },
                    {
                        "id": "certification_prep",
                        "name": "Certification Prep",
                        "description": "Structured certification training",
                        "complexity": "intermediate",
                        "audience": "certification_candidates"
                    },
                    {
                        "id": "workshop_facilitator",
                        "name": "Workshop Facilitator",
                        "description": "Interactive workshop content",
                        "complexity": "intermediate",
                        "audience": "workshop_participants"
                    },
                    {
                        "id": "online_course",
                        "name": "Online Course",
                        "description": "Structured online learning content",
                        "complexity": "intermediate",
                        "audience": "online_students"
                    },
                    {
                        "id": "corporate_training",
                        "name": "Corporate Training",
                        "description": "Professional development content",
                        "complexity": "intermediate",
                        "audience": "employees"
                    },
                    {
                        "id": "academic_textbook",
                        "name": "Academic Textbook",
                        "description": "Formal educational material",
                        "complexity": "advanced",
                        "audience": "students"
                    },
                    {
                        "id": "skill_assessment",
                        "name": "Skill Assessment",
                        "description": "Competency evaluation content",
                        "complexity": "intermediate",
                        "audience": "trainees"
                    },
                    {
                        "id": "knowledge_base",
                        "name": "Knowledge Base",
                        "description": "Comprehensive reference material",
                        "complexity": "intermediate",
                        "audience": "knowledge_seekers"
                    },
                    {
                        "id": "learning_pathway",
                        "name": "Learning Pathway",
                        "description": "Structured learning progression",
                        "complexity": "intermediate",
                        "audience": "guided_learners"
                    }
                ],
                "content_templates": ["educational_materials", "training_modules", "course_content"]
            },

            # MARKETING COMMUNICATIONS CATEGORY
            StyleCategory.MARKETING_COMMUNICATIONS.value: {
                "name": "Marketing Communications",
                "description": "Persuasive marketing content for brand building and customer engagement",
                "style_profiles": [
                    {
                        "id": "brand_storytelling",
                        "name": "Brand Storytelling",
                        "description": "Compelling brand narrative",
                        "complexity": "intermediate",
                        "audience": "brand_audiences"
                    },
                    {
                        "id": "product_launch",
                        "name": "Product Launch",
                        "description": "Exciting product introduction",
                        "complexity": "intermediate",
                        "audience": "potential_customers"
                    },
                    {
                        "id": "content_marketing",
                        "name": "Content Marketing",
                        "description": "Value-driven marketing content",
                        "complexity": "intermediate",
                        "audience": "target_market"
                    },
                    {
                        "id": "social_media_voice",
                        "name": "Social Media Voice",
                        "description": "Engaging social media content",
                        "complexity": "beginner",
                        "audience": "social_followers"
                    },
                    {
                        "id": "email_campaign",
                        "name": "Email Campaign",
                        "description": "Effective email marketing",
                        "complexity": "intermediate",
                        "audience": "email_subscribers"
                    },
                    {
                        "id": "sales_enablement",
                        "name": "Sales Enablement",
                        "description": "Sales-supporting content",
                        "complexity": "intermediate",
                        "audience": "sales_prospects"
                    },
                    {
                        "id": "thought_leadership",
                        "name": "Thought Leadership",
                        "description": "Industry expertise content",
                        "complexity": "advanced",
                        "audience": "industry_peers"
                    },
                    {
                        "id": "customer_success",
                        "name": "Customer Success",
                        "description": "Customer-focused content",
                        "complexity": "intermediate",
                        "audience": "existing_customers"
                    },
                    {
                        "id": "influencer_collaboration",
                        "name": "Influencer Collaboration",
                        "description": "Influencer partnership content",
                        "complexity": "intermediate",
                        "audience": "influencer_audiences"
                    },
                    {
                        "id": "conversion_optimization",
                        "name": "Conversion Optimization",
                        "description": "Performance-driven marketing",
                        "complexity": "advanced",
                        "audience": "conversion_targets"
                    }
                ],
                "content_templates": ["marketing_content", "social_media_campaigns", "email_newsletters"]
            }
        }
    
    def _initialize_recommendations(self) -> Dict[str, List[str]]:
        """Initialize recommended style-template combinations"""
        return {
            # Content Template → Recommended Style Categories
            "blog_article_generator": [
                StyleCategory.EDUCATIONAL_CONTENT.value,
                StyleCategory.MARKETING_COMMUNICATIONS.value,
                StyleCategory.TECHNICAL_DOCUMENTATION.value
            ],
            "business_proposal": [
                StyleCategory.BUSINESS_STRATEGY.value,
                StyleCategory.FINANCIAL_ANALYSIS.value
            ],
            "technical_documents": [
                StyleCategory.TECHNICAL_DOCUMENTATION.value,
                StyleCategory.ACADEMIC_RESEARCH.value
            ],
            "email_newsletter": [
                StyleCategory.MARKETING_COMMUNICATIONS.value,
                StyleCategory.EDUCATIONAL_CONTENT.value
            ],
            "social_media_campaign": [
                StyleCategory.MARKETING_COMMUNICATIONS.value,
                StyleCategory.CREATIVE_STORYTELLING.value
            ],
            "press_release": [
                StyleCategory.MARKETING_COMMUNICATIONS.value,
                StyleCategory.BUSINESS_STRATEGY.value
            ]
        }
    
    def get_styles_for_template(self, template_id: str) -> List[Dict[str, Any]]:
        """Get recommended style profiles for a content template"""
        recommended_categories = self.recommended_combinations.get(template_id, [])
        
        styles = []
        for category in recommended_categories:
            if category in self.category_mappings:
                category_data = self.category_mappings[category]
                for style in category_data["style_profiles"]:
                    styles.append({
                        **style,
                        "category": category,
                        "category_name": category_data["name"]
                    })
        
        return styles
    
    def get_all_categories(self) -> Dict[str, Any]:
        """Get all style categories with their profiles"""
        return {
            category_id: {
                "name": data["name"],
                "description": data["description"],
                "style_count": len(data["style_profiles"]),
                "profiles": data["style_profiles"]
            }
            for category_id, data in self.category_mappings.items()
        }
    
    def generate_missing_profiles(self) -> List[Dict[str, Any]]:
        """Generate YAML files for missing style profiles"""
        missing_profiles = []
        
        for category_id, category_data in self.category_mappings.items():
            for style in category_data["style_profiles"]:
                profile_yaml = self._generate_style_profile_yaml(style, category_data)
                missing_profiles.append({
                    "filename": f"{style['id']}.yaml",
                    "content": profile_yaml,
                    "category": category_id
                })
        
        return missing_profiles
    
    def _generate_style_profile_yaml(self, style: Dict[str, Any], category: Dict[str, Any]) -> str:
        """Generate YAML content for a style profile"""
        
        yaml_content = f"""# data/style_profiles/{style['id']}.yaml
id: {style['id']}
name: {style['name']}
description: {style['description']}
category: {category['name'].lower().replace(' ', '_')}
subcategory: {style['complexity']}
platform: professional
tone: {self._get_tone_for_style(style)}
voice: {self._get_voice_for_style(style)}
structure: {self._get_structure_for_style(style)}
audience: {style['audience']}

system_prompt: >
  {self._generate_system_prompt(style, category)}

writing_style:
  tone: {self._get_tone_for_style(style)}
  voice: {self._get_voice_for_style(style)}
  formality: {self._get_formality_for_style(style)}
  technical_level: {style['complexity']}
  objectivity: {self._get_objectivity_for_style(style)}

forbidden_patterns:
{self._get_forbidden_patterns_yaml(style)}

required_opening_patterns:
{self._get_required_openings_yaml(style)}

required_elements:
{self._get_required_elements_yaml(style)}

length_limit:
  words: {self._get_word_limit(style)}
  min: {int(self._get_word_limit(style) * 0.8)}
  max: {int(self._get_word_limit(style) * 1.2)}

settings:
  use_analogies: {self._use_analogies(style)}
  avoid_jargon: {self._avoid_jargon(style)}
  include_examples: true
  conversational_tone: {self._conversational_tone(style)}
  encourage_questions: {self._encourage_questions(style)}
  reading_level: "{style['complexity']}"

formatting:
  use_headers: true
  use_bullet_points: {self._use_bullets(style)}
  use_callouts: {self._use_callouts(style)}
  code_blocks: {self._code_blocks(style)}

quality_requirements:
  style_consistency: 95
  pattern_compliance: 100
  audience_alignment: 90
  complexity_match: 85

metadata:
  version: "2.0.0"
  created_by: "category_system"
  last_updated: "2025-07-18"
  use_cases: {self._get_use_cases(style)}
  target_audience: "{style['audience']}"
  complexity_level: "{style['complexity']}"
"""
        return yaml_content.strip()
    
    def _get_tone_for_style(self, style: Dict[str, Any]) -> str:
        """Determine appropriate tone for style"""
        complexity = style['complexity']
        audience = style['audience']
        
        if 'academic' in audience or 'research' in audience:
            return 'scholarly'
        elif 'executive' in audience or 'c_suite' in audience:
            return 'authoritative'
        elif 'beginner' in audience or complexity == 'beginner':
            return 'friendly'
        elif 'technical' in audience or 'engineer' in audience:
            return 'analytical'
        else:
            return 'professional'
    
    def _get_voice_for_style(self, style: Dict[str, Any]) -> str:
        """Determine appropriate voice for style"""
        if style['complexity'] == 'expert':
            return 'authoritative'
        elif style['complexity'] == 'beginner':
            return 'helpful'
        else:
            return 'confident'
    
    def _get_formality_for_style(self, style: Dict[str, Any]) -> str:
        """Determine formality level"""
        audience = style['audience']
        
        if any(formal in audience for formal in ['academic', 'executive', 'board', 'committee']):
            return 'high'
        elif 'beginner' in audience or 'social' in audience:
            return 'moderate'
        else:
            return 'high'
    
    def _get_structure_for_style(self, style: Dict[str, Any]) -> str:
        """Determine content structure"""
        style_id = style['id']
        
        if 'research' in style_id or 'academic' in style_id:
            return 'introduction → methodology → findings → discussion → conclusion'
        elif 'business' in style_id or 'strategy' in style_id:
            return 'executive_summary → analysis → recommendations → implementation'
        elif 'tutorial' in style_id or 'guide' in style_id:
            return 'overview → step_by_step → examples → practice'
        else:
            return 'introduction → main_content → conclusion'
    
    def _generate_system_prompt(self, style: Dict[str, Any], category: Dict[str, Any]) -> str:
        """Generate appropriate system prompt"""
        return f"""Write in the {style['name'].lower()} style for {style['audience'].replace('_', ' ')} audience. 
        Focus on {category['description'].lower()}. 
        Maintain {style['complexity']} complexity level throughout. 
        Ensure content aligns with professional {category['name'].lower()} standards."""
    
    def _get_forbidden_patterns_yaml(self, style: Dict[str, Any]) -> str:
        """Get forbidden patterns in YAML format"""
        patterns = self._get_forbidden_patterns(style)
        return '\n'.join(f'  - "{pattern}"' for pattern in patterns)
    
    def _get_forbidden_patterns(self, style: Dict[str, Any]) -> List[str]:
        """Get forbidden patterns for style"""
        base_patterns = ['hey there', 'hi there', 'awesome', 'cool']
        
        if 'academic' in style['audience']:
            return base_patterns + ['greetings', 'let\'s dive in', 'amazing', 'totally']
        elif 'executive' in style['audience']:
            return base_patterns + ['super', 'really really', 'what\'s up']
        elif 'technical' in style['audience']:
            return base_patterns + ['awesome sauce', 'mind-blowing', 'crazy good']
        else:
            return base_patterns
    
    def _get_required_openings_yaml(self, style: Dict[str, Any]) -> str:
        """Get required openings in YAML format"""
        openings = self._get_required_openings(style)
        return '\n'.join(f'  - "{opening}"' for opening in openings)
    
    def _get_required_openings(self, style: Dict[str, Any]) -> List[str]:
        """Get required opening patterns"""
        if 'academic' in style['audience']:
            return ['This analysis examines', 'This research investigates', 'This study explores']
        elif 'technical' in style['audience']:
            return ['This technical guide', 'The implementation of', 'Technical specifications']
        elif 'business' in style['audience']:
            return ['This strategic analysis', 'Business implications', 'Market research indicates']
        elif 'beginner' in style['audience']:
            return ['Understanding', 'Learning about', 'Getting started with']
        else:
            return ['This analysis presents', 'The following examination', 'This discussion covers']
    
    def _get_required_elements_yaml(self, style: Dict[str, Any]) -> str:
        """Get required elements in YAML format"""
        elements = self._get_required_elements(style)
        return '\n'.join(f'  - "{element}"' for element in elements)
    
    def _get_required_elements(self, style: Dict[str, Any]) -> List[str]:
        """Get required content elements"""
        if 'academic' in style['audience']:
            return ['clear thesis', 'evidence-based arguments', 'scholarly citations', 'methodological rigor']
        elif 'technical' in style['audience']:
            return ['technical precision', 'implementation details', 'code examples', 'best practices']
        elif 'business' in style['audience']:
            return ['strategic insights', 'actionable recommendations', 'market analysis', 'ROI considerations']
        else:
            return ['clear objectives', 'structured content', 'practical examples', 'actionable insights']
    
    def _get_word_limit(self, style: Dict[str, Any]) -> int:
        """Get appropriate word limit"""
        complexity = style['complexity']
        
        if complexity == 'expert':
            return 3000
        elif complexity == 'advanced':
            return 2500
        elif complexity == 'intermediate':
            return 2000
        else:
            return 1500
    
    def _use_analogies(self, style: Dict[str, Any]) -> bool:
        """Whether to use analogies"""
        return style['complexity'] in ['beginner', 'intermediate']
    
    def _avoid_jargon(self, style: Dict[str, Any]) -> bool:
        """Whether to avoid jargon"""
        return style['complexity'] == 'beginner'
    
    def _conversational_tone(self, style: Dict[str, Any]) -> bool:
        """Whether to use conversational tone"""
        return 'beginner' in style['audience'] or 'social' in style['audience']
    
    def _encourage_questions(self, style: Dict[str, Any]) -> bool:
        """Whether to encourage questions"""
        return style['complexity'] in ['beginner', 'intermediate']
    
    def _use_bullets(self, style: Dict[str, Any]) -> bool:
        """Whether to use bullet points"""
        return 'technical' in style['audience'] or 'business' in style['audience']
    
    def _use_callouts(self, style: Dict[str, Any]) -> bool:
        """Whether to use callouts"""
        return style['complexity'] in ['beginner', 'intermediate']
    
    def _code_blocks(self, style: Dict[str, Any]) -> str:
        """Code block usage level"""
        if 'technical' in style['audience']:
            return 'extensive'
        elif 'academic' in style['audience']:
            return 'moderate'
        else:
            return 'minimal'
    
    def _get_use_cases(self, style: Dict[str, Any]) -> List[str]:
        """Get use cases for style"""
        return [f"{style['name'].lower()} content", f"{style['audience'].replace('_', ' ')} communication"]
    
    def _get_objectivity_for_style(self, style: Dict[str, Any]) -> str:
        """Determine objectivity level"""
        if 'academic' in style['audience'] or 'research' in style['audience']:
            return 'high'
        elif 'marketing' in style['audience'] or 'social' in style['audience']:
            return 'moderate'
        else:
            return 'high'

# Export the system
__all__ = ['ProfessionalStyleCategorySystem', 'StyleCategory', 'ContentCategory', 'StyleProfile', 'ContentTemplate']