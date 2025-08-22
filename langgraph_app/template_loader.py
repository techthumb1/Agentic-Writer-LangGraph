# langgraph_app/template_loader.py

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class TemplateLoader:
    """✅ UPDATED: Template loader integrated with dynamic system - consistent with DynamicStyleProfileLoader"""
    
    _instance = None
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.templates_cache: Dict[str, Dict[str, Any]] = {}
        self.templates_path: Optional[Path] = None
        self._find_and_load_templates()
    
    def _find_and_load_templates(self):
        """Find the templates directory and load all templates"""
        
        # Get current working directory
        cwd = Path.cwd()
        logger.info(f"Current working directory: {cwd}")
        
        # ✅ CONSISTENT: Same search paths as DynamicStyleProfileLoader
        search_paths = [
            # Primary paths for content templates
            cwd / "data" / "content_templates",
            cwd / "content_templates", 
            
            # If running from langgraph_app directory
            cwd / ".." / "data" / "content_templates",
            cwd / ".." / "content_templates",
            
            # Legacy paths (keep for backward compatibility)
            cwd / "frontend" / "content-templates",
            cwd / ".." / "frontend" / "content-templates",
        ]
        
        # Try each path
        for path in search_paths:
            resolved_path = path.resolve()
            logger.debug(f"Checking templates path: {resolved_path}")
            
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
        
        # If no directory found, log available directories for debugging
        logger.error("❌ No templates directory found!")
        logger.error("Available directories from current working directory:")
        
        try:
            for item in cwd.iterdir():
                if item.is_dir():
                    logger.error(f"  📁 {item.name}")
        except Exception as e:
            logger.error(f"Could not list directories: {e}")
    def normalize_v2_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert V2 template inputs to parameter format"""
        if 'inputs' not in template_data:
            return template_data

        inputs = template_data['inputs']
        parameters = []

        for key, spec in inputs.items():
            param = {
                'name': key,
                'label': key.replace('_', ' ').title(),
                'type': self._infer_type(spec.get('default')),
                'required': spec.get('required', False),
                'default': spec.get('default', ''),
                'commonly_used': key in ['topic', 'audience', 'tone']  # Mark common ones
            }
            parameters.append(param)

        template_data['parameters'] = parameters
        return template_data

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

                    template_data = self.normalize_v2_template(documents[0])
                    if template_data is None:
                        logger.warning(f"Empty YAML document in file: {yaml_file.name}")
                        continue
                    
                    if len(documents) > 1:
                        logger.warning(f"Multiple documents found in {yaml_file.name}, using first document only")

                # ✅ CONSISTENT: Use id field first, then filename (same as DynamicStyleProfileLoader)
                template_name = template_data.get('id', yaml_file.stem)
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
        """✅ NO FALLBACKS: Get a specific template by name - returns None if not found"""
        
        if template_name not in self.templates_cache:
            logger.warning(f"⚠️ Template '{template_name}' not found")
            logger.warning(f"Available templates: {sorted(self.templates_cache.keys())}")
            return None  # ✅ NO FALLBACKS - return None instead of generic content
        
        logger.info(f"✅ Found template: {template_name}")
        return self.templates_cache[template_name]
    
    def list_templates(self) -> List[str]:
        """Get list of all available template names"""
        return sorted(self.templates_cache.keys())
    
    def get_template_by_category(self, category: str) -> List[str]:
        """Get templates filtered by category"""
        matching_templates = []
        for template_name, template_data in self.templates_cache.items():
            if template_data.get('category', '').lower() == category.lower():
                matching_templates.append(template_name)
        return sorted(matching_templates)
    
    def get_template_metadata(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get template metadata without full content"""
        template = self.get_template(template_name)
        if not template:
            return None
        
        return {
            'id': template.get('id', template_name),
            'name': template.get('name', ''),
            'description': template.get('description', ''),
            'category': template.get('category', ''),
            'difficulty': template.get('difficulty', ''),
            'targetAudience': template.get('targetAudience', ''),
            'tags': template.get('tags', []),
            'estimatedLength': template.get('estimatedLength', ''),
            'icon': template.get('icon', ''),
        }
    
    def search_templates(self, search_term: str) -> List[str]:
        """Search templates by name, description, or tags"""
        search_term = search_term.lower()
        matching_templates = []
        
        for template_name, template_data in self.templates_cache.items():
            # Search in name
            if search_term in template_data.get('name', '').lower():
                matching_templates.append(template_name)
                continue
            
            # Search in description
            if search_term in template_data.get('description', '').lower():
                matching_templates.append(template_name)
                continue
            
            # Search in tags
            tags = template_data.get('tags', [])
            if any(search_term in tag.lower() for tag in tags):
                matching_templates.append(template_name)
                continue
        
        return sorted(matching_templates)
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """Validate a template structure and return validation report"""
        template = self.get_template(template_name)
        if not template:
            return {
                'valid': False,
                'errors': [f"Template '{template_name}' not found"],
                'warnings': []
            }
        
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['id', 'name', 'description', 'category']
        for field in required_fields:
            if not template.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Check recommended fields
        recommended_fields = ['difficulty', 'targetAudience', 'tags', 'estimatedLength']
        for field in recommended_fields:
            if not template.get(field):
                warnings.append(f"Missing recommended field: {field}")
        
        # Validate parameters structure
        if 'parameters' in template:
            parameters = template['parameters']
            if not isinstance(parameters, list):
                errors.append("Parameters should be a list")
            else:
                for i, param in enumerate(parameters):
                    if not isinstance(param, dict):
                        errors.append(f"Parameter {i} should be a dictionary")
                        continue
                    
                    if not param.get('name'):
                        errors.append(f"Parameter {i} missing required 'name' field")
                    if not param.get('type'):
                        errors.append(f"Parameter {i} missing required 'type' field")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def reload_templates(self):
        """Force reload all templates"""
        self.templates_cache.clear()
        self.templates_path = None
        self._find_and_load_templates()
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about template loading"""
        return {
            "templates_path": str(self.templates_path) if self.templates_path else None,
            "current_working_directory": str(Path.cwd()),
            "available_templates": self.list_templates(),
            "template_count": len(self.templates_cache),
            "templates_loaded": bool(self.templates_cache)
        }


    def _infer_type(self, value):
        if isinstance(value, bool): return 'boolean'
        if isinstance(value, (int, float)): return 'number'
        if isinstance(value, list): return 'select'
        return 'text'

# ✅ CONSISTENT: Singleton pattern (same as DynamicStyleProfileLoader)
def get_template_loader():
    """Get the singleton template loader instance"""
    if TemplateLoader._instance is None:
        TemplateLoader._instance = TemplateLoader()
    return TemplateLoader._instance

# Create global instance
template_loader = get_template_loader()

# ✅ NO FALLBACKS: Global functions for backward compatibility
def get_template(template_name: str) -> Optional[Dict[str, Any]]:
    """Get a template by name - NO FALLBACKS"""
    return template_loader.get_template(template_name)

def list_available_templates() -> List[str]:
    """List all available template names"""
    return template_loader.list_templates()

def get_template_metadata(template_name: str) -> Optional[Dict[str, Any]]:
    """Get template metadata without full content"""
    return template_loader.get_template_metadata(template_name)

def search_templates(search_term: str) -> List[str]:
    """Search templates by name, description, or tags"""
    return template_loader.search_templates(search_term)

def validate_template(template_name: str) -> Dict[str, Any]:
    """Validate a template structure"""
    return template_loader.validate_template(template_name)

def reload_templates():
    """Force reload all templates"""
    return template_loader.reload_templates()

# ✅ INTEGRATION: Functions to work with the dynamic style profile system
def get_template_with_style_recommendations(template_name: str) -> Optional[Dict[str, Any]]:
    """Get template with style profile recommendations"""
    try:
        from style_profile_loader import get_profile_recommendations
        
        template = get_template(template_name)
        if not template:
            return None
        
        # Add dynamic style recommendations
        recommendations = get_profile_recommendations(template_name)
        template_with_recommendations = template.copy()
        template_with_recommendations['recommended_style_profiles'] = recommendations
        
        return template_with_recommendations
    
    except ImportError as e:
        logger.warning(f"Could not import style_profile_loader: {e}")
        return get_template(template_name)

def get_all_templates_with_recommendations() -> Dict[str, Dict[str, Any]]:
    """Get all templates with their style profile recommendations"""
    try:
        from style_profile_loader import get_profile_recommendations
        
        all_templates = {}
        for template_name in list_available_templates():
            template = get_template(template_name)
            if template:
                recommendations = get_profile_recommendations(template_name)
                template_with_recommendations = template.copy()
                template_with_recommendations['recommended_style_profiles'] = recommendations
                all_templates[template_name] = template_with_recommendations
        
        return all_templates
    
    except ImportError as e:
        logger.warning(f"Could not import style_profile_loader: {e}")
        return {name: get_template(name) for name in list_available_templates() if get_template(name)}

# ✅ VALIDATION: Template system validation
def validate_template_system() -> Dict[str, Any]:
    """Validate the template system and return diagnostic information"""
    loader = get_template_loader()
    
    validation_report = {
        "system_status": "healthy",
        "issues": [],
        "templates_loaded": len(loader.templates_cache),
        "templates_path": str(loader.templates_path) if loader.templates_path else None,
        "available_templates": sorted(loader.templates_cache.keys()),
        "validation_timestamp": yaml.safe_load("!!timestamp 2025-01-01T00:00:00")  # Using YAML timestamp
    }
    
    # Check for common issues
    if len(loader.templates_cache) == 0:
        validation_report["system_status"] = "error"
        validation_report["issues"].append("No templates loaded")
    
    if len(loader.templates_cache) < 5:
        validation_report["system_status"] = "warning"
        validation_report["issues"].append(f"Only {len(loader.templates_cache)} templates loaded - expected more")
    
    # Validate template structures
    invalid_templates = []
    template_categories = set()
    
    for template_name in loader.templates_cache.keys():
        validation_result = validate_template(template_name)
        if not validation_result['valid']:
            invalid_templates.append(f"{template_name}: {validation_result['errors']}")
        
        template = get_template(template_name)
        if template and template.get('category'):
            template_categories.add(template['category'])
    
    if invalid_templates:
        validation_report["system_status"] = "warning"
        validation_report["issues"].append(f"Invalid template structures: {invalid_templates}")
    
    validation_report["template_categories"] = sorted(template_categories)
    validation_report["categories_count"] = len(template_categories)
    
    return validation_report