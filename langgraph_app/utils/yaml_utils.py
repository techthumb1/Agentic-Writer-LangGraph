# langgraph_app/utils/yaml_utils.py
"""
YAML utilities for loading, parsing, and validating YAML files
"""

import re
import yaml
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_yaml_file_safe(file_path: str) -> Dict[str, Any]:
    """Load YAML file with comprehensive error handling - ENTERPRISE: Fail on errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            if content is None:
                raise ValueError(f"Empty YAML file: {file_path}")
            if not isinstance(content, dict):
                raise ValueError(f"Invalid YAML structure in {file_path}: expected dict, got {type(content)}")
            return content
    except yaml.YAMLError as e:
        raise SystemExit(f"ENTERPRISE MODE: YAML parsing error in {file_path}: {e}")
    except FileNotFoundError:
        raise SystemExit(f"ENTERPRISE MODE: Required file not found: {file_path}")
    except PermissionError:
        raise SystemExit(f"ENTERPRISE MODE: Permission denied reading file: {file_path}")
    except Exception as e:
        raise SystemExit(f"ENTERPRISE MODE: Unexpected error loading YAML {file_path}: {e}")

def fix_yaml_formatting(yaml_content: str) -> str:
    """Fix common YAML formatting issues from AI generation"""
    if not yaml_content or not isinstance(yaml_content, str):
        return yaml_content
        
    lines = yaml_content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            fixed_lines.append(line)
            continue
            
        # Fix missing colons after keys
        # Pattern: word followed by space and non-colon content
        if re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s+([^:].*)$', line):
            match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s+(.*)$', line)
            if match:
                indent, key, value = match.groups()
                # Don't modify if it's a list item or already formatted correctly
                if not value.startswith('-') and not key.endswith(':'):
                    line = f"{indent}{key}: {value}"
        
        # Fix multiline content that breaks YAML
        if ':' in line and len(line) > 120:
            parts = line.split(':', 1)
            if len(parts) == 2:
                key_part = parts[0]
                value_part = parts[1].strip()
                # Use literal block style for very long content
                if len(value_part) > 100 and not value_part.startswith(('"', "'", '|', '>')):
                    line = f"{key_part}: |\n    {value_part}"
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def create_fallback_template() -> Dict[str, Any]:
    """Create a minimal valid template when YAML parsing fails"""
    return {
        'name': 'Dynamic Generated Template',
        'system_prompt': 'Generate high-quality content based on the user requirements. Follow best practices for structure, clarity, and engagement.',
        'instructions': 'Create comprehensive content that meets the specified requirements. Include proper formatting, clear sections, and professional tone.',
        'parameters': {},
        'metadata': {
            'generated': True,
            'fallback': True,
            'timestamp': datetime.now().isoformat()
        }
    }

def safe_yaml_load(yaml_content: str, context: str = "unknown") -> Dict[str, Any]:
    """Safely load YAML with automatic fixing of common issues"""
    if not yaml_content:
        logger.warning(f"Empty YAML content in {context}")
        return create_fallback_template()
    
    try:
        # First attempt: try loading as-is
        result = yaml.safe_load(yaml_content)
        if result is None:
            logger.warning(f"YAML loaded as None in {context}, creating fallback")
            return create_fallback_template()
        return result
    except yaml.YAMLError as e:
        logger.warning(f"Initial YAML parse failed in {context}, attempting to fix: {e}")
        
        try:
            # Second attempt: fix formatting and try again
            fixed_content = fix_yaml_formatting(yaml_content)
            result = yaml.safe_load(fixed_content)
            if result is None:
                return create_fallback_template()
            logger.info(f"Successfully fixed YAML formatting in {context}")
            return result
        except yaml.YAMLError as e2:
            logger.error(f"Failed to fix YAML content in {context}: {e2}")
            logger.debug(f"Problematic YAML content: {yaml_content[:500]}...")
            return create_fallback_template()

def validate_template_structure(template_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize template structure"""
    if not isinstance(template_data, dict):
        logger.error(f"Template data is not a dict: {type(template_data)}")
        return create_fallback_template()
    
    # Ensure required fields exist
    required_fields = ['name', 'system_prompt']
    for field in required_fields:
        if field not in template_data:
            logger.warning(f"Missing required field '{field}' in template, adding default")
            if field == 'name':
                template_data['name'] = 'Generated Template'
            elif field == 'system_prompt':
                template_data['system_prompt'] = 'Generate high-quality content based on requirements.'
    
    # Ensure metadata exists
    if 'metadata' not in template_data:
        template_data['metadata'] = {}
    
    # Ensure parameters exists
    if 'parameters' not in template_data:
        template_data['parameters'] = {}
    
    return template_data

def validate_style_profile_structure(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize style profile structure"""
    if not isinstance(profile_data, dict):
        logger.error(f"Style profile data is not a dict: {type(profile_data)}")
        return {"name": "Default Profile", "category": "general"}
    
    # Ensure required fields exist
    if 'name' not in profile_data:
        profile_data['name'] = 'Generated Profile'
    
    if 'category' not in profile_data:
        profile_data['category'] = 'general'
    
    # Ensure metadata exists
    if 'metadata' not in profile_data:
        profile_data['metadata'] = {}
    
    return profile_data

def save_yaml_file(file_path: str, data: Dict[str, Any]) -> bool:
    """Save data to YAML file with error handling"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save YAML file {file_path}: {e}")
        return False

def merge_yaml_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two YAML configurations, with override taking precedence"""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_yaml_configs(result[key], value)
        else:
            result[key] = value
    
    return result

def extract_yaml_metadata(yaml_content: str) -> Dict[str, Any]:
    """Extract metadata from YAML content without full parsing"""
    metadata = {}
    
    try:
        # Look for common metadata patterns
        lines = yaml_content.split('\n')
        in_metadata = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('metadata:'):
                in_metadata = True
                continue
            
            if in_metadata:
                if line.startswith('  ') and ':' in line:
                    key, value = line.strip().split(':', 1)
                    metadata[key.strip()] = value.strip().strip('"\'')
                elif not line.startswith('  ') and line:
                    # End of metadata section
                    break
        
        return metadata
        
    except Exception as e:
        logger.warning(f"Failed to extract YAML metadata: {e}")
        return {}

def validate_yaml_syntax(yaml_content: str) -> tuple[bool, str]:
    """Validate YAML syntax without loading the full content"""
    try:
        yaml.safe_load(yaml_content)
        return True, "Valid YAML syntax"
    except yaml.YAMLError as e:
        return False, f"YAML syntax error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"