# langgraph_app/template_loader.py
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class TemplateLoader:
    """Handles loading content templates from template directory"""
    
    def __init__(self):
        self.templates_cache: Dict[str, Dict[str, Any]] = {}
        self.templates_path: Optional[Path] = None
        self._find_and_load_templates()
    
    def _find_and_load_templates(self):
        """Find the templates directory and load all templates"""
        
        # Get current working directory
        cwd = Path.cwd()
        logger.info(f"Current working directory: {cwd}")
        
        # Define search paths in order of preference
        search_paths = [
            # If running from project root
            cwd / "data" / "content_templates",
            cwd / "content_templates", 
            
            # If running from langgraph_app directory
            cwd / ".." / "data" / "content_templates",
            cwd / ".." / "content_templates",
            
            # Alternative paths
            cwd / "frontend" / "content-templates",
            cwd / ".." / "frontend" / "content-templates",
        ]
        
        # Try each path
        for path in search_paths:
            resolved_path = path.resolve()
            logger.info(f"Checking path: {resolved_path}")
            
            if resolved_path.exists() and resolved_path.is_dir():
                yaml_files = list(resolved_path.glob("*.yaml")) + list(resolved_path.glob("*.yml"))
                
                if yaml_files:
                    logger.info(f"✅ Found templates directory: {resolved_path}")
                    logger.info(f"Found {len(yaml_files)} YAML files")
                    
                    self.templates_path = resolved_path
                    self._load_templates_from_directory(resolved_path)
                    return
                else:
                    logger.warning(f"Directory exists but no YAML files found: {resolved_path}")
        
        logger.error("❌ No templates directory found!")
        logger.error("Available directories from current working directory:")
        
        try:
            for item in cwd.iterdir():
                if item.is_dir():
                    logger.error(f"  📁 {item.name}")
        except Exception as e:
            logger.error(f"Could not list directories: {e}")
    
    def _load_templates_from_directory(self, directory: Path):
        """Load all YAML templates from the specified directory"""

        yaml_files = list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))
        loaded_count = 0

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    documents = list(yaml.safe_load_all(f))

                    if not documents:
                        logger.warning(f"Empty YAML file: {yaml_file.name}")
                        continue
                    
                    template_data = documents[0]

                    if template_data is None:
                        logger.warning(f"Empty YAML document in file: {yaml_file.name}")
                        continue
                    
                    if len(documents) > 1:
                        logger.warning(f"Multiple documents found in {yaml_file.name}, using first document only")

                template_name = yaml_file.stem
                self.templates_cache[template_name] = template_data
                loaded_count += 1

                logger.debug(f"✅ Loaded template: {template_name}")

            except yaml.YAMLError as e:
                logger.error(f"❌ YAML parsing error in {yaml_file.name}: {e}")
            except Exception as e:
                logger.error(f"❌ Error loading template {yaml_file.name}: {e}")
        
        logger.info(f"Successfully loaded {loaded_count} templates")
        logger.info(f"Available templates: {sorted(self.templates_cache.keys())}")
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by name"""
        
        if template_name not in self.templates_cache:
            logger.warning(f"Template '{template_name}' not found")
            logger.warning(f"Available templates: {sorted(self.templates_cache.keys())}")
            return None
        
        return self.templates_cache[template_name]
    
    def list_templates(self) -> List[str]:
        """Get list of all available template names"""
        return sorted(self.templates_cache.keys())
    
    def reload_templates(self):
        """Force reload all templates"""
        self.templates_cache.clear()
        self.templates_path = None
        self._find_and_load_templates()

# Create global instance
template_loader = TemplateLoader()

# Function to get template (for backward compatibility)
def get_template(template_name: str) -> Optional[Dict[str, Any]]:
    """Get a template by name"""
    return template_loader.get_template(template_name)

def list_available_templates() -> List[str]:
    """List all available template names"""
    return template_loader.list_templates()