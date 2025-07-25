# langgraph_app/style_profile_loader.py
# ✅ FIXED VERSION - Eliminates fallback confusion and template mixing

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class StyleProfileLoader:
    """✅ FIXED: Handles loading style profiles ONLY - no template mixing"""
    
    _instance = None
    _profiles_loaded = False

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.profiles_cache: Dict[str, Dict[str, Any]] = {}
        self.profiles_path: Optional[Path] = None
    
    def _find_and_load_profiles(self):
        """Find the style profiles directory and load all profiles"""
        
        if self._profiles_loaded:
            logger.debug("Style profiles already loaded, skipping...")
            return
        
        # Get current working directory
        cwd = Path.cwd()
        logger.info(f"Current working directory: {cwd}")
        
        # ✅ FIXED: Define search paths specifically for STYLE PROFILES
        search_paths = [
            # Primary paths for style profiles
            cwd / "data" / "style_profiles",
            cwd / "style_profiles", 
            
            # If running from langgraph_app directory
            cwd / ".." / "data" / "style_profiles",
            cwd / ".." / "style_profiles",
            
            # Legacy paths (keep for backward compatibility)
            cwd / "style_profile",  # Note: singular form exists in your project
        ]
        
        # Try each path
        for path in search_paths:
            resolved_path = path.resolve()
            logger.info(f"Checking style profiles path: {resolved_path}")
            
            if resolved_path.exists() and resolved_path.is_dir():
                yaml_files = list(resolved_path.glob("*.yaml")) + list(resolved_path.glob("*.yml"))
                
                if yaml_files:
                    logger.info(f"✅ Found style profiles directory: {resolved_path}")
                    logger.info(f"Found {len(yaml_files)} YAML files")
                    
                    self.profiles_path = resolved_path
                    self._load_profiles_from_directory(resolved_path)
                    return
                else:
                    logger.warning(f"Directory exists but no YAML files found: {resolved_path}")
        
        # If no directory found, log available directories for debugging
        logger.error("❌ No style profiles directory found!")
        logger.error("Available directories from current working directory:")
        
        try:
            for item in cwd.iterdir():
                if item.is_dir():
                    logger.error(f"  📁 {item.name}")
        except Exception as e:
            logger.error(f"Could not list directories: {e}")
    
    def _load_profiles_from_directory(self, directory: Path):
        """Load all YAML profiles from the specified directory"""

        yaml_files = list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))
        loaded_count = 0

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    # Handle multiple documents in YAML files
                    documents = list(yaml.safe_load_all(f))

                    if not documents:
                        logger.warning(f"Empty YAML file: {yaml_file.name}")
                        continue
                    
                    # Use the first document if multiple exist
                    profile_data = documents[0]

                    if profile_data is None:
                        logger.warning(f"Empty YAML document in file: {yaml_file.name}")
                        continue
                    
                    # If there are multiple documents, log a warning
                    if len(documents) > 1:
                        logger.warning(f"Multiple documents found in {yaml_file.name}, using first document only")

                # ✅ FIXED: Validate that this is actually a style profile, not a template
                if self._validate_style_profile(profile_data, yaml_file.name):
                    # Use filename without extension as profile key
                    profile_name = yaml_file.stem
                    self.profiles_cache[profile_name] = profile_data
                    loaded_count += 1
                    logger.debug(f"✅ Loaded style profile: {profile_name}")
                else:
                    logger.warning(f"⚠️ Skipping {yaml_file.name} - does not appear to be a style profile")

            except yaml.YAMLError as e:
                logger.error(f"❌ YAML parsing error in {yaml_file.name}: {e}")
            except Exception as e:
                logger.error(f"❌ Error loading profile {yaml_file.name}: {e}")
                
        logger.info(f"Successfully loaded {loaded_count} style profiles")
        logger.info(f"Available style profiles: {sorted(self.profiles_cache.keys())}")
        StyleProfileLoader._profiles_loaded = True
    
    def _validate_style_profile(self, data: Dict[str, Any], filename: str) -> bool:
        """✅ NEW: Validate that loaded data is actually a style profile, not a template"""
        
        # Style profiles typically have these fields
        style_indicators = ['tone', 'voice', 'system_prompt', 'writing_style', 'category']
        
        # Templates typically have these fields  
        template_indicators = ['parameters', 'suggested_sections', 'instructions', 'estimatedLength']
        
        style_score = sum(1 for indicator in style_indicators if indicator in data)
        template_score = sum(1 for indicator in template_indicators if indicator in data)
        
        # If it looks more like a template than a style profile, reject it
        if template_score > style_score:
            logger.warning(f"File {filename} appears to be a template (template_score={template_score}, style_score={style_score})")
            return False
        
        # Must have at least one style indicator
        if style_score == 0:
            logger.warning(f"File {filename} has no style profile indicators")
            return False
        
        return True
    
    def list_profiles(self) -> List[str]:
        """Get list of all available profile names"""
        if not self._profiles_loaded:
            self._find_and_load_profiles()
        return sorted(self.profiles_cache.keys())
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about profile loading"""
        return {
            "profiles_path": str(self.profiles_path) if self.profiles_path else None,
            "current_working_directory": str(Path.cwd()),
            "available_profiles": self.list_profiles(),
            "profile_count": len(self.profiles_cache),
            "profiles_loaded": bool(self.profiles_cache)
        }
    
    def reload_profiles(self):
        """Force reload all profiles"""
        self.profiles_cache.clear()
        self.profiles_path = None
        StyleProfileLoader._profiles_loaded = False
        self._find_and_load_profiles()
    
    def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """✅ FIXED: Get a specific style profile by name with INTELLIGENT fallback support"""
        if not self._profiles_loaded:
            self._find_and_load_profiles()

        # Try to get the requested profile first
        if profile_name in self.profiles_cache:
            logger.info(f"✅ Found style profile: {profile_name}")
            return self.profiles_cache[profile_name]

        # ✅ ENHANCED: Intelligent fallback mapping for common style profiles
        intelligent_fallback_mapping = {
            # Legacy template names -> appropriate style profiles
            'analytical_authoritative': 'phd_academic',
            'week_2': 'beginner_friendly', 
            'federated_learning_101': 'technical_tutor',
            'assertive_friendly': 'beginner_friendly',
            'decision_trees': 'technical_dive',
            'introduction_to_contrastive_learning': 'educational_expert',
            'approachable_engaging': 'beginner_friendly',
            'blog_post': 'popular_sci',
            'future_of_llms': 'technical_dive',  # Map the problematic default
            
            # Common variations and aliases
            'academic': 'phd_academic',
            'technical': 'technical_dive',
            'beginner': 'beginner_friendly',
            'educational': 'educational_expert',
            'scientific': 'experimental_lab_log',
            'popular_science': 'popular_sci',
            'literature_review': 'phd_lit_review',
            
            # Template IDs that might be confused as style profiles
            'business_proposal': 'founder_storytelling',
            'technical_documentation': 'technical_tutor',
            'social_media_campaign': 'founder_storytelling',
            'blog_article_generator': 'popular_sci',
            'email_newsletter': 'market_flash',
            'press_release': 'ai_news_brief',
            
            # Default fallbacks by category
            '1': 'popular_sci',  # Default template ID fallback
            'default': 'popular_sci',
            'unknown': 'beginner_friendly'
        }

        if profile_name in intelligent_fallback_mapping:
            fallback_profile = intelligent_fallback_mapping[profile_name]
            logger.info(f"🔄 Style profile '{profile_name}' mapped to '{fallback_profile}' via intelligent fallback")

            if fallback_profile in self.profiles_cache:
                return self.profiles_cache[fallback_profile]

        # ✅ ENHANCED: Try fuzzy matching for close names
        fuzzy_match = self._find_fuzzy_match(profile_name)
        if fuzzy_match:
            logger.info(f"🔍 Style profile '{profile_name}' fuzzy-matched to '{fuzzy_match}'")
            return self.profiles_cache[fuzzy_match]

        # Still not found, use intelligent default selection
        logger.warning(f"⚠️ Style profile '{profile_name}' not found")
        logger.warning(f"Available style profiles: {sorted(self.profiles_cache.keys())}")

        # ✅ ENHANCED: Intelligent default selection based on profile name hints
        default_profile = self._select_intelligent_default(profile_name)
        
        if default_profile and default_profile in self.profiles_cache:
            logger.info(f"🎯 Using intelligent default '{default_profile}' for '{profile_name}'")
            return self.profiles_cache[default_profile]

        # Ultimate fallback - return the first available profile
        if self.profiles_cache:
            first_profile = next(iter(self.profiles_cache.keys()))
            logger.info(f"🆘 Using emergency fallback '{first_profile}' for '{profile_name}'")
            return self.profiles_cache[first_profile]

        return None
    
    def _find_fuzzy_match(self, profile_name: str) -> Optional[str]:
        """Find fuzzy matches for profile names"""
        profile_name_lower = profile_name.lower()
        
        # Check for partial matches
        for available_profile in self.profiles_cache.keys():
            available_lower = available_profile.lower()
            
            # Check if profile name is contained in available profile or vice versa
            if profile_name_lower in available_lower or available_lower in profile_name_lower:
                return available_profile
            
            # Check for word matches
            profile_words = set(profile_name_lower.replace('_', ' ').split())
            available_words = set(available_lower.replace('_', ' ').split())
            
            # If more than half the words match, consider it a fuzzy match
            if len(profile_words & available_words) > len(profile_words) / 2:
                return available_profile
        
        return None
    
    def _select_intelligent_default(self, profile_name: str) -> Optional[str]:
        """Select an intelligent default based on profile name characteristics"""
        profile_name_lower = profile_name.lower()
        
        # Academic/Research indicators
        if any(word in profile_name_lower for word in ['academic', 'phd', 'research', 'paper', 'literature']):
            if 'phd_academic' in self.profiles_cache:
                return 'phd_academic'
            elif 'phd_lit_review' in self.profiles_cache:
                return 'phd_lit_review'
        
        # Technical indicators
        if any(word in profile_name_lower for word in ['technical', 'tech', 'code', 'api', 'documentation', 'dev']):
            if 'technical_dive' in self.profiles_cache:
                return 'technical_dive'
            elif 'technical_tutor' in self.profiles_cache:
                return 'technical_tutor'
        
        # Beginner/Educational indicators
        if any(word in profile_name_lower for word in ['beginner', 'intro', 'basic', '101', 'tutorial', 'guide']):
            if 'beginner_friendly' in self.profiles_cache:
                return 'beginner_friendly'
            elif 'educational_expert' in self.profiles_cache:
                return 'educational_expert'
        
        # Business indicators
        if any(word in profile_name_lower for word in ['business', 'startup', 'founder', 'executive', 'strategy']):
            if 'founder_storytelling' in self.profiles_cache:
                return 'founder_storytelling'
            elif 'startup_trends_brief' in self.profiles_cache:
                return 'startup_trends_brief'
        
        # Scientific indicators
        if any(word in profile_name_lower for word in ['science', 'scientific', 'experiment', 'lab', 'study']):
            if 'experimental_lab_log' in self.profiles_cache:
                return 'experimental_lab_log'
            elif 'popular_sci' in self.profiles_cache:
                return 'popular_sci'
        
        # News/Brief indicators
        if any(word in profile_name_lower for word in ['news', 'brief', 'update', 'flash', 'alert']):
            if 'ai_news_brief' in self.profiles_cache:
                return 'ai_news_brief'
            elif 'market_flash' in self.profiles_cache:
                return 'market_flash'
        
        # Healthcare indicators
        if any(word in profile_name_lower for word in ['health', 'medical', 'healthcare', 'clinical']):
            if 'ai_in_healthcare' in self.profiles_cache:
                return 'ai_in_healthcare'
        
        # Default to popular_sci as the most versatile profile
        if 'popular_sci' in self.profiles_cache:
            return 'popular_sci'
        
        return None

    # ✅ REMOVED: Backward compatibility methods that were causing confusion
    # No more load_template or template mixing - this is STYLE PROFILES ONLY
    
    async def load_style_profile_async(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Async version of get_profile"""
        return self.get_profile(profile_name)

# ✅ ENHANCED: Singleton pattern with proper initialization
def get_style_profile_loader():
    """Get the singleton style profile loader instance"""
    if StyleProfileLoader._instance is None:
        StyleProfileLoader._instance = StyleProfileLoader()
        # Force loading on first access
        StyleProfileLoader._instance._find_and_load_profiles()
    return StyleProfileLoader._instance

# ✅ FIXED: Global instance and functions
style_profile_loader = get_style_profile_loader()

def get_style_profile(profile_name: str) -> Optional[Dict[str, Any]]:
    """Get a style profile by name - global function for backward compatibility"""
    return style_profile_loader.get_profile(profile_name)

def list_available_profiles() -> List[str]:
    """List all available profile names - global function"""
    return style_profile_loader.list_profiles()

def reload_style_profiles():
    """Force reload all style profiles - global function"""
    return style_profile_loader.reload_profiles()

# ✅ NEW: Validation and debugging functions
def validate_style_profile_system() -> Dict[str, Any]:
    """Validate the style profile system and return diagnostic information"""
    loader = get_style_profile_loader()
    
    validation_report = {
        "system_status": "healthy",
        "issues": [],
        "profiles_loaded": len(loader.profiles_cache),
        "profiles_path": str(loader.profiles_path) if loader.profiles_path else None,
        "available_profiles": sorted(loader.profiles_cache.keys()),
        "validation_timestamp": "2025-07-18T12:00:00Z"
    }
    
    # Check for common issues
    if len(loader.profiles_cache) == 0:
        validation_report["system_status"] = "error"
        validation_report["issues"].append("No style profiles loaded")
    
    if len(loader.profiles_cache) < 5:
        validation_report["system_status"] = "warning"
        validation_report["issues"].append(f"Only {len(loader.profiles_cache)} profiles loaded - expected more")
    
    # Check for essential profiles
    essential_profiles = ['popular_sci', 'beginner_friendly', 'technical_dive', 'phd_academic']
    missing_essential = [p for p in essential_profiles if p not in loader.profiles_cache]
    
    if missing_essential:
        validation_report["system_status"] = "warning"
        validation_report["issues"].append(f"Missing essential profiles: {missing_essential}")
    
    # Check profile structure
    invalid_profiles = []
    for profile_name, profile_data in loader.profiles_cache.items():
        if not isinstance(profile_data, dict):
            invalid_profiles.append(profile_name)
        elif not any(key in profile_data for key in ['tone', 'voice', 'system_prompt']):
            invalid_profiles.append(f"{profile_name} (missing style indicators)")
    
    if invalid_profiles:
        validation_report["system_status"] = "warning"
        validation_report["issues"].append(f"Invalid profile structures: {invalid_profiles}")
    
    return validation_report

def get_profile_recommendations(template_id: str) -> List[str]:
    """Get recommended style profiles for a given template"""
    template_to_style_recommendations = {
        'business_proposal': ['founder_storytelling', 'startup_trends_brief', 'market_flash'],
        'technical_documentation': ['technical_tutor', 'technical_dive', 'educational_expert'],
        'social_media_campaign': ['founder_storytelling', 'popular_sci', 'ai_news_brief'],
        'blog_article_generator': ['popular_sci', 'beginner_friendly', 'educational_expert'],
        'email_newsletter': ['market_flash', 'ai_news_brief', 'startup_trends_brief'],
        'press_release': ['ai_news_brief', 'market_flash', 'policy_watch']
    }
    
    recommendations = template_to_style_recommendations.get(template_id, ['popular_sci', 'beginner_friendly'])
    
    # Filter to only include available profiles
    loader = get_style_profile_loader()
    available_recommendations = [p for p in recommendations if p in loader.profiles_cache]
    
    # If no specific recommendations available, return general purpose profiles
    if not available_recommendations:
        available_recommendations = [p for p in ['popular_sci', 'beginner_friendly', 'educational_expert'] 
                                   if p in loader.profiles_cache]
    
    return available_recommendations[:3]  # Return top 3 recommendations

# ✅ ENHANCED: Debug and monitoring functions
def debug_profile_loading():
    """Debug function to test profile loading"""
    logger.info("🔍 Debug: Testing style profile loading...")
    
    loader = get_style_profile_loader()
    debug_info = loader.get_debug_info()
    
    logger.info(f"Debug info: {debug_info}")
    
    # Test loading a few profiles
    test_profiles = ['popular_sci', 'phd_academic', 'technical_dive', 'beginner_friendly']
    
    for profile_name in test_profiles:
        profile = loader.get_profile(profile_name)
        if profile:
            logger.info(f"✅ Successfully loaded {profile_name}: {profile.get('name', 'Unnamed')}")
        else:
            logger.warning(f"❌ Failed to load {profile_name}")
    
    return debug_info

# Force initialization and validation on import
try:
    _loader = get_style_profile_loader()
    logger.info(f"✅ Style profile loader initialized with {len(_loader.profiles_cache)} profiles")
except Exception as e:
    logger.error(f"❌ Failed to initialize style profile loader: {e}")