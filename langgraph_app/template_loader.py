# langgraph_app/template_loader.py
# Clean template loader with YAML-first validation, no fallback overrides
# RELEVANT FILES: mcp_enhanced_graph.py, integrated_server.py, data/content_templates/

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class TemplateValidationError(Exception):
    """Template validation failures"""

class TemplateLoader:
    """Clean template loader - respects YAML metadata, no classification overrides"""
    
    _instance = None
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.templates_cache: Dict[str, Dict[str, Any]] = {}
        self.templates_path: Optional[Path] = None
        self._find_and_load_templates()
        
        if not self.templates_cache:
            logger.error("CRITICAL: No templates loaded during initialization")
        else:
            logger.info(f"Template loader initialized with {len(self.templates_cache)} templates")
    
    def _find_and_load_templates(self):
        """Find the templates directory and load all templates"""
        cwd = Path.cwd()
        logger.info(f"Current working directory: {cwd}")
        
        search_paths = [
            cwd / "data" / "content_templates",
            cwd / "content_templates", 
            cwd / ".." / "data" / "content_templates",
            cwd / ".." / "content_templates",
        ]
        
        for path in search_paths:
            resolved_path = path.resolve()
            logger.debug(f"Checking templates path: {resolved_path}")
            
            if resolved_path.exists() and resolved_path.is_dir():
                yaml_files = list(resolved_path.glob("*.yaml")) + list(resolved_path.glob("*.yml"))
                
                if yaml_files:
                    logger.info(f"Found templates directory: {resolved_path}")
                    logger.info(f"Found {len(yaml_files)} YAML files")
                    
                    self.templates_path = resolved_path
                    self._load_templates_from_directory(resolved_path)
                    return
        
        logger.error("No templates directory found!")

    def normalize_v2_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """ENTERPRISE: Use YAML metadata directly - no fallback overrides"""
        
        # Get template_type from YAML metadata
        template_type = template_data.get('template_type')
        if not template_type:
            template_id = template_data.get('id', 'unknown')
            raise TemplateValidationError(f"ENTERPRISE: Template {template_id} must specify template_type in YAML")

        # ONLY read image_agent_enabled from YAML if present
        # Do not add any classification logic here
        if template_data.get('image_agent_enabled'):
            logger.info(f"ENABLED: Image agent for {template_data.get('id')} (YAML specified)")

        return template_data

    def _convert_inputs_to_parameters(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert V2 inputs format to parameters format"""
        inputs = template_data.get('inputs', {})
        parameters = {}
        
        for key, spec in inputs.items():
            if isinstance(spec, dict):
                param = {
                    'name': key,
                    'label': spec.get('label', key.replace('_', ' ').title()),
                    'type': self._infer_parameter_type(spec),
                    'required': spec.get('required', False),
                    'description': spec.get('description', ''),
                    'default': spec.get('default', ''),
                    'placeholder': spec.get('placeholder', ''),
                    'validation': spec.get('validation', {})
                }
                
                # Handle options for select types
                if 'options' in spec:
                    param['type'] = 'select'
                    param['options'] = spec['options']
                    
            else:
                # Simple value - create basic parameter
                param = {
                    'name': key,
                    'label': key.replace('_', ' ').title(),
                    'type': self._infer_type(spec),
                    'required': False,
                    'default': spec if spec is not None else '',
                    'description': '',
                    'validation': {}
                }
            
            parameters[key] = param
        
        # Replace inputs with parameters
        template_data['parameters'] = parameters
        del template_data['inputs']
        template_data['_converted_from_inputs'] = True
        
        logger.info(f"Converted {len(parameters)} inputs to parameters")
        return template_data

    def _infer_parameter_type(self, spec: Dict[str, Any]) -> str:
        """Infer parameter type from specification"""
        if 'type' in spec:
            return spec['type']
            
        default_value = spec.get('default')
        
        if isinstance(default_value, bool):
            return 'checkbox'
        elif isinstance(default_value, (int, float)):
            return 'number'
        elif isinstance(default_value, list):
            return 'select'
        elif 'options' in spec:
            return 'select'
        else:
            # Check length for textarea vs text
            default_str = str(default_value) if default_value else ''
            return 'textarea' if len(default_str) > 100 else 'text'

    def _infer_type(self, value):
        """Infer parameter type from default value"""
        if isinstance(value, bool): 
            return 'checkbox'
        if isinstance(value, (int, float)): 
            return 'number'
        if isinstance(value, list): 
            return 'select'
        if value and len(str(value)) > 100:
            return 'textarea'
        return 'text'

    def _load_templates_from_directory(self, directory: Path):
        """Load all YAML templates from directory with proper normalization"""
        yaml_files = list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))
        loaded_count = 0

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    documents = list(yaml.safe_load_all(f))

                if not documents or documents[0] is None:
                    logger.warning(f"Empty YAML file: {yaml_file.name}")
                    continue

                template_data = documents[0]
                
                # Set ID if missing
                if 'id' not in template_data:
                    template_data['id'] = yaml_file.stem

                # Apply normalization
                template_data = self.normalize_v2_template(template_data)

                template_name = template_data['id']
                self.templates_cache[template_name] = template_data
                loaded_count += 1

                logger.info(f"Loaded: {template_name} | Type: {template_data.get('template_type')} | Images: {template_data.get('image_agent_enabled', False)}")

            except Exception as e:
                logger.error(f"Error loading template {yaml_file.name}: {e}")
        
        logger.info(f"Successfully loaded {loaded_count} templates")

    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get template with logging for debugging"""
        if template_name not in self.templates_cache:
            logger.warning(f"Template '{template_name}' not found")
            logger.warning(f"Available: {sorted(self.templates_cache.keys())}")
            return None
        
        template = self.templates_cache[template_name]
        logger.info(f"Retrieved: {template_name} | Type: {template.get('template_type')} | Images: {template.get('image_agent_enabled', False)}")
        return template

    def list_templates(self) -> List[str]:
        """Get list of all available template names"""
        return sorted(self.templates_cache.keys())

    def get_templates_by_type(self, template_type: str) -> List[Dict[str, Any]]:
        """Get all templates of a specific type"""
        return [
            template for template in self.templates_cache.values()
            if template.get('template_type') == template_type
        ]

    def should_include_image_agent(self, template_name: str) -> bool:
        """Check if template should include image generation"""
        template = self.get_template(template_name)
        return template.get('image_agent_enabled', False) if template else False

# Singleton pattern
def get_template_loader():
    """Get the singleton template loader instance"""
    if TemplateLoader._instance is None:
        TemplateLoader._instance = TemplateLoader()
    return TemplateLoader._instance

# Create global instance
template_loader = get_template_loader()

# Global functions for backward compatibility
def get_template(template_name: str) -> Optional[Dict[str, Any]]:
    """Get a template by name"""
    return template_loader.get_template(template_name)

def should_include_image_agent(template_name: str) -> bool:
    """Check if template should include image generation"""
    return template_loader.should_include_image_agent(template_name)

def list_available_templates() -> List[str]:
    """List all available template names"""
    return template_loader.list_templates()

def reload_templates():
    """Force reload all templates"""
    global template_loader
    TemplateLoader._instance = None
    template_loader = get_template_loader()
    return template_loader