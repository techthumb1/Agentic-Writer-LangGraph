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
    
    def __init__(self):
        self.profiles_cache: Dict[str, Dict[str, Any]] = {}
        self.profiles_path: Optional[Path] = None
        self._find_and_load_profiles()
    
    def _find_and_load_profiles(self):
        """Find the style profiles directory and load all profiles"""
        
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
                    profile_data = yaml.safe_load(f)
                
                if profile_data is None:
                    logger.warning(f"Empty YAML file: {yaml_file.name}")
                    continue
                
                # Use filename without extension as profile key
                profile_name = yaml_file.stem
                self.profiles_cache[profile_name] = profile_data
                loaded_count += 1
                
                logger.debug(f"✅ Loaded profile: {profile_name}")
                
            except Exception as e:
                logger.error(f"❌ Error loading {yaml_file.name}: {e}")
        
        logger.info(f"Successfully loaded {loaded_count} style profiles")
        logger.info(f"Available profiles: {sorted(self.profiles_cache.keys())}")
    
    def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific style profile by name"""
        
        if profile_name not in self.profiles_cache:
            logger.warning(f"Profile '{profile_name}' not found")
            logger.warning(f"Available profiles: {sorted(self.profiles_cache.keys())}")
            return None
        
        return self.profiles_cache[profile_name]
    
    def list_profiles(self) -> List[str]:
        """Get list of all available profile names"""
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

# Create global instance
style_profile_loader = StyleProfileLoader()

# Function to get profile (for backward compatibility)
def get_style_profile(profile_name: str) -> Optional[Dict[str, Any]]:
    """Get a style profile by name"""
    return style_profile_loader.get_profile(profile_name)

def list_available_profiles() -> List[str]:
    """List all available profile names"""
    return style_profile_loader.list_profiles()