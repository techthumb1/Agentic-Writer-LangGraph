# langgraph_app/style_profile_loader.py

import os
from tomlkit import datetime
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class ContentCharacteristics:
    """Represents the characteristics of a template or style profile"""
    category: str = ""
    difficulty: str = ""
    target_audience: str = ""
    tags: List[str] = None
    tone_indicators: List[str] = None
    content_type: str = ""
    formality_level: str = ""
    technical_level: str = ""
    domain_focus: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.tone_indicators is None:
            self.tone_indicators = []

class DynamicStyleProfileLoader:
    """✅ DYNAMIC: Completely rewritten for content-driven recommendations with zero hardcoded fallbacks"""
    
    _instance = None
    _profiles_loaded = False

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.profiles_cache: Dict[str, Dict[str, Any]] = {}
        self.templates_cache: Dict[str, Dict[str, Any]] = {}
        self.profiles_path: Optional[Path] = None
        self.templates_path: Optional[Path] = None
        self.compatibility_matrix: Dict[str, Dict[str, float]] = {}
        
        # Dynamic scoring weights - can be adjusted based on system learning
        self.scoring_weights = {
            'category_match': 0.25,
            'difficulty_compatibility': 0.20,
            'audience_alignment': 0.20,
            'tag_overlap': 0.15,
            'technical_level_match': 0.10,
            'formality_match': 0.10
        }
    
    def _find_and_load_all_content(self):
        """Find and load both style profiles and content templates"""
        
        if self._profiles_loaded:
            logger.debug("Content already loaded, skipping...")
            return
        
        # Get current working directory
        cwd = Path.cwd()
        logger.info(f"Current working directory: {cwd}")
        
        # ✅ DYNAMIC: Search for both profiles and templates
        self._load_style_profiles(cwd)
        self._load_content_templates(cwd)
        
        # Build compatibility matrix after loading all content
        self._build_compatibility_matrix()
        
        DynamicStyleProfileLoader._profiles_loaded = True
    
    def _load_style_profiles(self, base_path: Path):
        """Load style profiles from multiple possible locations"""
        
        search_paths = [
            base_path / "data" / "style_profiles",
            base_path / "style_profiles", 
            base_path / ".." / "data" / "style_profiles",
            base_path / ".." / "style_profiles",
        ]
        
        for path in search_paths:
            resolved_path = path.resolve()
            logger.debug(f"Checking style profiles path: {resolved_path}")
            
            if resolved_path.exists() and resolved_path.is_dir():
                yaml_files = list(resolved_path.glob("*.yaml")) + list(resolved_path.glob("*.yml"))
                
                if yaml_files:
                    logger.info(f"✅ Found style profiles directory: {resolved_path}")
                    self.profiles_path = resolved_path
                    self._load_yaml_files_to_cache(yaml_files, self.profiles_cache, "style profile")
                    return
        
        logger.warning("❌ No style profiles directory found!")
    
    def _load_content_templates(self, base_path: Path):
        """Load content templates for analysis"""
        
        search_paths = [
            base_path / "data" / "content_templates",
            base_path / "content_templates",
            base_path / ".." / "data" / "content_templates",
            base_path / ".." / "content_templates",
        ]
        
        for path in search_paths:
            resolved_path = path.resolve()
            logger.debug(f"Checking templates path: {resolved_path}")
            
            if resolved_path.exists() and resolved_path.is_dir():
                yaml_files = list(resolved_path.glob("*.yaml")) + list(resolved_path.glob("*.yml"))
                
                if yaml_files:
                    logger.info(f"✅ Found templates directory: {resolved_path}")
                    self.templates_path = resolved_path
                    self._load_yaml_files_to_cache(yaml_files, self.templates_cache, "template")
                    return
        
        logger.warning("❌ No templates directory found!")
    
    def _load_yaml_files_to_cache(self, yaml_files: List[Path], cache: Dict[str, Dict[str, Any]], content_type: str):
        """Load YAML files into the specified cache"""
        
        loaded_count = 0
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    documents = list(yaml.safe_load_all(f))

                    if not documents:
                        logger.warning(f"Empty YAML file: {yaml_file.name}")
                        continue
                    
                    content_data = documents[0]
                    if content_data is None:
                        logger.warning(f"Empty YAML document in file: {yaml_file.name}")
                        continue
                    
                    if len(documents) > 1:
                        logger.warning(f"Multiple documents found in {yaml_file.name}, using first document only")

                # Use filename without extension as key, but prefer 'id' field if present
                content_name = content_data.get('id', yaml_file.stem)
                cache[content_name] = content_data
                loaded_count += 1
                logger.debug(f"✅ Loaded {content_type}: {content_name}")

            except yaml.YAMLError as e:
                logger.error(f"❌ YAML parsing error in {yaml_file.name}: {e}")
            except Exception as e:
                logger.error(f"❌ Error loading {content_type} {yaml_file.name}: {e}")
                
        logger.info(f"Successfully loaded {loaded_count} {content_type}s")
        logger.info(f"Available {content_type}s: {sorted(cache.keys())}")
    
    def _extract_content_characteristics(self, content: Dict[str, Any], content_type: str = "unknown") -> ContentCharacteristics:
        """✅ DYNAMIC: Extract characteristics from any content (template or profile)"""
        
        # Extract basic metadata
        category = content.get('category', '').lower()
        difficulty = content.get('difficulty', '').lower()
        target_audience = content.get('targetAudience', content.get('target_audience', '')).lower()
        tags = [tag.lower() for tag in content.get('tags', [])]
        
        # Extract tone indicators from various fields
        tone_indicators = []
        
        # Check for tone in profile-specific fields
        if 'tone' in content:
            tone_indicators.append(content['tone'].lower())
        if 'voice' in content:
            tone_indicators.append(content['voice'].lower())
        if 'writing_style' in content:
            writing_style = content['writing_style']
            if isinstance(writing_style, str):
                tone_indicators.append(writing_style.lower())
            elif isinstance(writing_style, dict):
                # Handle dict case - extract relevant fields
                if 'tone' in writing_style:
                    tone_indicators.append(str(writing_style['tone']).lower())
                elif 'style' in writing_style:
                    tone_indicators.append(str(writing_style['style']).lower())
                elif 'primary_tone' in writing_style:
                    tone_indicators.append(str(writing_style['primary_tone']).lower())
                else:
                    # Fallback: use first string value found in dict
                    for key, value in writing_style.items():
                        if isinstance(value, str) and value.strip():
                            tone_indicators.append(value.lower())
                            break
            elif isinstance(writing_style, list):
                # Handle list case
                if writing_style and isinstance(writing_style[0], str):
                    tone_indicators.append(writing_style[0].lower())
        
        # Check for tone in template-specific fields
        if 'parameters' in content:
            for param in content['parameters']:
                if 'tone' in param.get('name', '').lower() and 'options' in param:
                    tone_indicators.extend([opt.lower() for opt in param['options']])
        
        # Determine domain focus from name and content
        domain_focus = self._extract_domain_focus(content)
        
        # Determine content type and formality
        content_type_val = category or domain_focus or 'general'
        formality_level = self._determine_formality_level(content, tags, tone_indicators)
        technical_level = self._determine_technical_level(content, tags, difficulty)
        
        return ContentCharacteristics(
            category=category,
            difficulty=difficulty,
            target_audience=target_audience,
            tags=tags,
            tone_indicators=tone_indicators,
            content_type=content_type_val,
            formality_level=formality_level,
            technical_level=technical_level,
            domain_focus=domain_focus
        )
    
    def _extract_domain_focus(self, content: Dict[str, Any]) -> str:
        """Extract domain focus from content name and description"""
        
        name = content.get('name', content.get('id', '')).lower()
        description = content.get('description', '').lower()
        
        # Domain mapping based on actual profiles and templates
        domain_keywords = {
            'academic': ['academic', 'phd', 'research', 'thesis', 'dissertation', 'scholarly', 'literature_review'],
            'business': ['business', 'executive', 'corporate', 'roi', 'sales', 'market', 'investor', 'venture'],
            'technical': ['api', 'technical', 'code', 'system', 'architecture', 'deployment', 'integration'],
            'education': ['tutorial', 'course', 'learning', 'certification', 'workshop', 'training'],
            'healthcare': ['healthcare', 'medical', 'clinical'],
            'ai_ml': ['ai', 'ml', 'machine learning', 'artificial intelligence'],
            'startup': ['startup', 'founder', 'entrepreneurship'],
            'marketing': ['marketing', 'content', 'social_media', 'brand', 'campaign'],
            'science': ['science', 'research', 'experimental', 'methodology']
        }
        
        text_to_check = f"{name} {description}"
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_to_check for keyword in keywords):
                return domain
        
        return 'general'
    
    def _determine_formality_level(self, content: Dict[str, Any], tags: List[str], tone_indicators: List[str]) -> str:
        """Determine formality level from content analysis"""
        
        formal_keywords = ['formal', 'professional', 'business', 'executive', 'academic', 'official', 'board', 'scholarly']
        casual_keywords = ['casual', 'friendly', 'conversational', 'approachable', 'informal', 'beginner', 'tutorial']
        
        # Check description and instructions
        text_to_analyze = ' '.join([
            content.get('description', ''),
            content.get('instructions', ''),
            content.get('name', ''),
            ' '.join(tags),
            ' '.join(tone_indicators)
        ]).lower()
        
        formal_score = sum(1 for keyword in formal_keywords if keyword in text_to_analyze)
        casual_score = sum(1 for keyword in casual_keywords if keyword in text_to_analyze)
        
        if formal_score > casual_score:
            return 'formal'
        elif casual_score > formal_score:
            return 'casual'
        else:
            return 'neutral'
    
    def _determine_technical_level(self, content: Dict[str, Any], tags: List[str], difficulty: str) -> str:
        """Determine technical complexity level"""
        
        technical_keywords = ['technical', 'api', 'system', 'architecture', 'code', 'implementation', 'specification']
        beginner_keywords = ['beginner', 'intro', 'basic', 'simple', 'tutorial', 'getting started']
        advanced_keywords = ['advanced', 'expert', 'masterclass', 'deep', 'comprehensive', 'phd']
        
        text_to_analyze = ' '.join([
            content.get('description', ''),
            content.get('name', ''),
            ' '.join(tags),
            difficulty
        ]).lower()
        
        if any(keyword in text_to_analyze for keyword in technical_keywords):
            if any(keyword in text_to_analyze for keyword in advanced_keywords):
                return 'highly_technical'
            return 'technical'
        elif any(keyword in text_to_analyze for keyword in beginner_keywords):
            return 'beginner_friendly'
        elif any(keyword in text_to_analyze for keyword in advanced_keywords):
            return 'advanced'
        else:
            return 'intermediate'
    
    def _build_compatibility_matrix(self):
        """✅ DYNAMIC: Build compatibility matrix between all templates and profiles"""
        
        logger.info("Building dynamic compatibility matrix...")
        
        for template_id, template_data in self.templates_cache.items():
            self.compatibility_matrix[template_id] = {}
            template_chars = self._extract_content_characteristics(template_data, 'template')
            
            for profile_id, profile_data in self.profiles_cache.items():
                profile_chars = self._extract_content_characteristics(profile_data, 'profile')
                compatibility_score = self._calculate_compatibility_score(template_chars, profile_chars)
                self.compatibility_matrix[template_id][profile_id] = compatibility_score
                
                logger.debug(f"Compatibility: {template_id} -> {profile_id} = {compatibility_score:.3f}")
        
        logger.info(f"Built compatibility matrix for {len(self.templates_cache)} templates and {len(self.profiles_cache)} profiles")
    
    def _calculate_compatibility_score(self, template_chars: ContentCharacteristics, profile_chars: ContentCharacteristics) -> float:
        """Calculate compatibility score between template and profile characteristics"""
        
        score = 0.0
        
        # Category/Domain match
        if template_chars.domain_focus and profile_chars.domain_focus:
            if template_chars.domain_focus == profile_chars.domain_focus:
                score += self.scoring_weights['category_match']
            elif self._are_related_domains(template_chars.domain_focus, profile_chars.domain_focus):
                score += self.scoring_weights['category_match'] * 0.5
        
        # Difficulty compatibility
        if template_chars.difficulty and profile_chars.difficulty:
            difficulty_score = self._calculate_difficulty_compatibility(template_chars.difficulty, profile_chars.difficulty)
            score += self.scoring_weights['difficulty_compatibility'] * difficulty_score
        
        # Audience alignment
        if template_chars.target_audience and profile_chars.target_audience:
            audience_score = self._calculate_audience_alignment(template_chars.target_audience, profile_chars.target_audience)
            score += self.scoring_weights['audience_alignment'] * audience_score
        
        # Tag overlap
        if template_chars.tags and profile_chars.tags:
            tag_overlap = len(set(template_chars.tags) & set(profile_chars.tags)) / len(set(template_chars.tags) | set(profile_chars.tags))
            score += self.scoring_weights['tag_overlap'] * tag_overlap
        
        # Technical level match
        if template_chars.technical_level == profile_chars.technical_level:
            score += self.scoring_weights['technical_level_match']
        elif self._are_compatible_technical_levels(template_chars.technical_level, profile_chars.technical_level):
            score += self.scoring_weights['technical_level_match'] * 0.5
        
        # Formality match
        if template_chars.formality_level == profile_chars.formality_level:
            score += self.scoring_weights['formality_match']
        elif template_chars.formality_level == 'neutral' or profile_chars.formality_level == 'neutral':
            score += self.scoring_weights['formality_match'] * 0.5
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _are_related_domains(self, domain1: str, domain2: str) -> bool:
        """Check if two domains are related"""
        
        related_domains = {
            'academic': ['science', 'research'],
            'business': ['marketing', 'startup'],
            'technical': ['ai_ml'],
            'education': ['academic'],
            'ai_ml': ['technical', 'science']
        }
        
        return domain2 in related_domains.get(domain1, []) or domain1 in related_domains.get(domain2, [])
    
    def _calculate_difficulty_compatibility(self, template_difficulty: str, profile_difficulty: str) -> float:
        """Calculate how compatible difficulty levels are"""
        
        difficulty_hierarchy = ['beginner', 'intermediate', 'advanced', 'expert']
        
        try:
            t_idx = difficulty_hierarchy.index(template_difficulty)
            p_idx = difficulty_hierarchy.index(profile_difficulty)
            
            # Perfect match
            if t_idx == p_idx:
                return 1.0
            # Adjacent levels
            elif abs(t_idx - p_idx) == 1:
                return 0.7
            # Two levels apart
            elif abs(t_idx - p_idx) == 2:
                return 0.3
            else:
                return 0.0
        except ValueError:
            # If difficulty not in hierarchy, use fuzzy matching
            return 0.5 if template_difficulty in profile_difficulty or profile_difficulty in template_difficulty else 0.0
    
    def _calculate_audience_alignment(self, template_audience: str, profile_audience: str) -> float:
        """Calculate audience alignment score"""
        
        # Direct match
        if template_audience == profile_audience:
            return 1.0
        
        # Check for overlapping keywords
        template_words = set(template_audience.split())
        profile_words = set(profile_audience.split())
        
        if template_words & profile_words:
            return 0.7
        
        # Check for compatible audiences
        compatible_audiences = {
            'business professionals': ['executives', 'consultants', 'managers'],
            'developers': ['technical', 'engineers', 'programmers'],
            'students': ['learners', 'beginners'],
            'researchers': ['academics', 'scientists']
        }
        
        for main_audience, compatible_list in compatible_audiences.items():
            if main_audience in template_audience and any(comp in profile_audience for comp in compatible_list):
                return 0.6
            if main_audience in profile_audience and any(comp in template_audience for comp in compatible_list):
                return 0.6
        
        return 0.0
    
    def _are_compatible_technical_levels(self, level1: str, level2: str) -> bool:
        """Check if technical levels are compatible"""
        
        compatible_pairs = [
            ('beginner_friendly', 'intermediate'),
            ('intermediate', 'technical'),
            ('technical', 'highly_technical'),
            ('intermediate', 'advanced')
        ]
        
        return (level1, level2) in compatible_pairs or (level2, level1) in compatible_pairs
    
    def get_profile_recommendations(self, template_id: str, max_recommendations: int = 3) -> List[str]:
        """✅ DYNAMIC: Get style profile recommendations based on actual content analysis - NO HARDCODED FALLBACKS"""
        
        if not self._profiles_loaded:
            self._find_and_load_all_content()
        
        # Check if template exists
        if template_id not in self.compatibility_matrix:
            logger.warning(f"Template '{template_id}' not found in compatibility matrix")
            logger.warning(f"Available templates: {sorted(self.templates_cache.keys())}")
            return []  # ✅ NO FALLBACKS - return empty list
        
        # Get compatibility scores for this template
        template_scores = self.compatibility_matrix[template_id]
        
        # Sort profiles by compatibility score
        sorted_profiles = sorted(template_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Filter out profiles with zero compatibility
        compatible_profiles = [(profile, score) for profile, score in sorted_profiles if score > 0.0]
        
        if not compatible_profiles:
            logger.info(f"No compatible profiles found for template '{template_id}'")
            return []  # ✅ NO FALLBACKS - return empty list
        
        # Return top recommendations
        recommendations = [profile for profile, score in compatible_profiles[:max_recommendations]]
        
        logger.info(f"✅ Dynamic recommendations for '{template_id}': {recommendations}")
        for profile, score in compatible_profiles[:max_recommendations]:
            logger.debug(f"  {profile}: {score:.3f} compatibility")
        
        return recommendations
    
    def get_compatibility_score(self, template_id: str, profile_id: str) -> float:
        """Get the compatibility score between a specific template and profile"""
        
        if not self._profiles_loaded:
            self._find_and_load_all_content()
        
        return self.compatibility_matrix.get(template_id, {}).get(profile_id, 0.0)
    
    def get_template_analysis(self, template_id: str) -> Dict[str, Any]:
        """Get detailed analysis of a template's characteristics"""
        
        if not self._profiles_loaded:
            self._find_and_load_all_content()
        
        if template_id not in self.templates_cache:
            return {}
        
        template_data = self.templates_cache[template_id]
        characteristics = self._extract_content_characteristics(template_data, 'template')
        
        return {
            'template_id': template_id,
            'characteristics': characteristics.__dict__,
            'compatibility_scores': self.compatibility_matrix.get(template_id, {}),
            'top_recommendations': self.get_profile_recommendations(template_id)
        }
    
    def list_profiles(self) -> List[str]:
        """Get list of all available profile names"""
        if not self._profiles_loaded:
            self._find_and_load_all_content()
        return sorted(self.profiles_cache.keys())
    
    def list_templates(self) -> List[str]:
        """Get list of all available template names"""
        if not self._profiles_loaded:
            self._find_and_load_all_content()
        return sorted(self.templates_cache.keys())
    
    def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific style profile by name - returns None if not found"""
        if not self._profiles_loaded:
            self._find_and_load_all_content()

        if profile_name in self.profiles_cache:
            logger.info(f"✅ Found style profile: {profile_name}")
            return self.profiles_cache[profile_name]

        logger.warning(f"⚠️ Style profile '{profile_name}' not found")
        logger.warning(f"Available style profiles: {sorted(self.profiles_cache.keys())}")
        
        return None  # ✅ NO FALLBACKS
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by name - returns None if not found"""
        if not self._profiles_loaded:
            self._find_and_load_all_content()

        if template_name in self.templates_cache:
            logger.info(f"✅ Found template: {template_name}")
            return self.templates_cache[template_name]

        logger.warning(f"⚠️ Template '{template_name}' not found")
        logger.warning(f"Available templates: {sorted(self.templates_cache.keys())}")
        
        return None  # ✅ NO FALLBACKS
    
    def reload_all_content(self):
        """Force reload all profiles and templates"""
        self.profiles_cache.clear()
        self.templates_cache.clear()
        self.compatibility_matrix.clear()
        self.profiles_path = None
        self.templates_path = None
        DynamicStyleProfileLoader._profiles_loaded = False
        self._find_and_load_all_content()
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get comprehensive debug information"""
        return {
            "profiles_path": str(self.profiles_path) if self.profiles_path else None,
            "templates_path": str(self.templates_path) if self.templates_path else None,
            "current_working_directory": str(Path.cwd()),
            "available_profiles": self.list_profiles(),
            "available_templates": self.list_templates(),
            "profile_count": len(self.profiles_cache),
            "template_count": len(self.templates_cache),
            "compatibility_matrix_size": f"{len(self.compatibility_matrix)} x {len(self.profiles_cache) if self.profiles_cache else 0}",
            "content_loaded": bool(self.profiles_cache and self.templates_cache)
        }

# ✅ DYNAMIC: Updated singleton pattern
def get_dynamic_style_profile_loader():
    """Get the singleton dynamic style profile loader instance"""
    if DynamicStyleProfileLoader._instance is None:
        DynamicStyleProfileLoader._instance = DynamicStyleProfileLoader()
        # Force loading on first access
        DynamicStyleProfileLoader._instance._find_and_load_all_content()
    return DynamicStyleProfileLoader._instance

# ✅ DYNAMIC: Global instance and functions
dynamic_style_profile_loader = get_dynamic_style_profile_loader()

def get_profile_recommendations(template_id: str, max_recommendations: int = 3) -> List[str]:
    """✅ DYNAMIC: Get style profile recommendations - NO HARDCODED FALLBACKS"""
    return dynamic_style_profile_loader.get_profile_recommendations(template_id, max_recommendations)

def get_style_profile(profile_name: str) -> Optional[Dict[str, Any]]:
    """Get a style profile by name - global function for backward compatibility"""
    return dynamic_style_profile_loader.get_profile(profile_name)

def list_available_profiles() -> List[str]:
    """List all available profile names - global function"""
    return dynamic_style_profile_loader.list_profiles()

def list_available_templates() -> List[str]:
    """List all available template names"""
    return dynamic_style_profile_loader.list_templates()

def reload_all_content():
    """Force reload all style profiles and templates"""
    return dynamic_style_profile_loader.reload_all_content()

def get_template_compatibility_analysis(template_id: str) -> Dict[str, Any]:
    """Get detailed compatibility analysis for a template"""
    return dynamic_style_profile_loader.get_template_analysis(template_id)

# ✅ DYNAMIC: Validation and debugging functions
def validate_dynamic_recommendation_system() -> Dict[str, Any]:
    """Validate the dynamic recommendation system and return diagnostic information"""
    loader = get_dynamic_style_profile_loader()
    
    validation_report = {
        "system_status": "healthy",
        "issues": [],
        "profiles_loaded": len(loader.profiles_cache),
        "templates_loaded": len(loader.templates_cache),
        "compatibility_matrix_built": bool(loader.compatibility_matrix),
        "paths": {
            "profiles_path": str(loader.profiles_path) if loader.profiles_path else None,
            "templates_path": str(loader.templates_path) if loader.templates_path else None
        },
        "available_profiles": sorted(loader.profiles_cache.keys()),
        "available_templates": sorted(loader.templates_cache.keys()),
        "validation_timestamp": datetime.now().isoformat()
    }
    
    # Check for issues
    if len(loader.profiles_cache) == 0:
        validation_report["system_status"] = "error"
        validation_report["issues"].append("No style profiles loaded")
    
    if len(loader.templates_cache) == 0:
        validation_report["system_status"] = "error"
        validation_report["issues"].append("No templates loaded")
    
    if not loader.compatibility_matrix:
        validation_report["system_status"] = "error"
        validation_report["issues"].append("Compatibility matrix not built")
    
    # Test a few recommendations
    sample_templates = list(loader.templates_cache.keys())[:3]
    sample_results = {}
    
    for template_id in sample_templates:
        recommendations = loader.get_profile_recommendations(template_id)
        sample_results[template_id] = {
            "recommendations": recommendations,
            "recommendation_count": len(recommendations)
        }
        
        if not recommendations:
            validation_report["issues"].append(f"No recommendations found for template '{template_id}'")
    
    validation_report["sample_recommendations"] = sample_results
    
    if validation_report["issues"]:
        validation_report["system_status"] = "warning" if validation_report["system_status"] == "healthy" else "error"
    
    return validation_report