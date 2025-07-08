# langgraph_app/style_profile_loader.py
# Create this new file to handle style profile loading

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class StyleProfileLoader:
    """Handles loading style profiles from multiple possible locations"""
    
    _instance = None
    _profiles_loaded = False

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.profiles_cache: Dict[str, Dict[str, Any]] = {}
        self.profiles_path: Optional[Path] = None
        #self._find_and_load_profiles()
    
    def _find_and_load_profiles(self):
        """Find the style profiles directory and load all profiles"""
        
        if self._profiles_loaded:
            logger.debug("Style profiles already loaded, skipping...")
            return
        
        # Get current working directory
        cwd = Path.cwd()
        logger.info(f"Current working directory: {cwd}")
        
        # Define search paths in order of preference
        search_paths = [
            # If running from project root
            cwd / "data" / "style_profiles",
            cwd / "style_profiles", 
            
            # If running from langgraph_app directory
            cwd / ".." / "data" / "style_profiles",
            cwd / ".." / "style_profiles",
            
            # Alternative paths
            cwd / "frontend" / "style-profiles",
            cwd / ".." / "frontend" / "style-profiles",
        ]
        
        # Try each path
        for path in search_paths:
            resolved_path = path.resolve()
            logger.info(f"Checking path: {resolved_path}")
            
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

                # Use filename without extension as profile key
                profile_name = yaml_file.stem
                self.profiles_cache[profile_name] = profile_data
                loaded_count += 1

                logger.debug(f"✅ Loaded profile: {profile_name}")

            except yaml.YAMLError as e:
                logger.error(f"❌ YAML parsing error in {yaml_file.name}: {e}")
            except Exception as e:
                logger.error(f"❌ Error loading profile {yaml_file.name}: {e}")
        logger.info(f"Successfully loaded {loaded_count} style profiles")
        logger.info(f"Available profiles: {sorted(self.profiles_cache.keys())}")
        StyleProfileLoader._profiles_loaded = True
    
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
        self._find_and_load_profiles()

    # Add this method to the StyleProfileLoader class
    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Load a content template (for backward compatibility)"""
        # For now, treat templates the same as profiles
        # In the future, you might want separate template loading
        return self.get_profile(template_id)
    
    async def load_template_async(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Async version of load_template"""
        return self.load_template(template_id)
    
    async def load_style_profile_async(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Async version of get_profile"""
        return self.get_profile(profile_name)
    
    def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific style profile by name with fallback support"""
        if not self._profiles_loaded:
            self._find_and_load_profiles()

        # Try to get the requested profile first
        if profile_name in self.profiles_cache:
            return self.profiles_cache[profile_name]

        # Profile not found, try fallback mapping
        fallback_mapping = {
            'analytical_authoritative': 'phd_academic',
            'week_2': 'beginner_friendly', 
            'federated_learning_101': 'technical_tutor',
            'assertive_friendly': 'beginner_friendly',
            'decision_trees': 'technical_dive',
            'introduction_to_contrastive_learning': 'educational_expert',
            'approachable_engaging': 'beginner_friendly',
            'blog_post': 'popular_sci'
        }

        if profile_name in fallback_mapping:
            fallback_profile = fallback_mapping[profile_name]
            logger.warning(f"Profile '{profile_name}' not found, using fallback '{fallback_profile}'")

            if fallback_profile in self.profiles_cache:
                return self.profiles_cache[fallback_profile]

        # Still not found, use default fallback
        logger.warning(f"Profile '{profile_name}' not found")
        logger.warning(f"Available profiles: {sorted(self.profiles_cache.keys())}")

        # Return beginner_friendly as ultimate fallback
        if 'beginner_friendly' in self.profiles_cache:
            logger.info(f"Using 'beginner_friendly' as ultimate fallback for '{profile_name}'")
            return self.profiles_cache['beginner_friendly']

        # If even beginner_friendly doesn't exist, return the first available profile
        if self.profiles_cache:
            first_profile = next(iter(self.profiles_cache.keys()))
            logger.info(f"Using '{first_profile}' as emergency fallback for '{profile_name}'")
            return self.profiles_cache[first_profile]

        return None

# Create global instance
style_profile_loader = StyleProfileLoader()

# Function to get profile (for backward compatibility)
def get_style_profile(profile_name: str) -> Optional[Dict[str, Any]]:
    """Get a style profile by name"""
    return style_profile_loader.get_profile(profile_name)

# Create global instance using singleton pattern
def get_style_profile_loader():
    if StyleProfileLoader._instance is None:
        StyleProfileLoader._instance = StyleProfileLoader()
    return StyleProfileLoader._instance

# Force loading on import (like before our changes)
_loader = get_style_profile_loader()
_loader._find_and_load_profiles()
style_profile_loader = get_style_profile_loader()

def list_available_profiles() -> List[str]:
    """List all available profile names"""
    loader = get_style_profile_loader()
    return style_profile_loader.list_profiles()