# langgraph_app/template_loader.py
# FIXED: Correct template classification and image agent integration
# Ensures blog_article_generator maps to blog_article, press_release maps correctly
# RELEVANT FILES: mcp_enhanced_graph.py, integrated_server.py, data/content_templates/blog_article_generator.yaml

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class TemplateLoader:
    """Fixed template loader with correct classification and image agent support"""
    
    _instance = None
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.templates_cache: Dict[str, Dict[str, Any]] = {}
        self.templates_path: Optional[Path] = None
        
        # FIXED: Correct template type mapping for proper classification
        self.template_type_mapping = {
            # Blog and articles
            'blog_article_generator': 'blog_article',
            'blog_article': 'blog_article',
            
            # Marketing content
            'content_marketing': 'content_marketing',
            'social_media_campaign': 'social_media',
            'email_newsletter': 'email_campaign',
            'press_release': 'press_release',
            'product_launch': 'product_launch',
            'brand_storytelling': 'brand_storytelling',
            
            # Business documents  
            'business_proposal': 'business_document',
            'executive_summary': 'business_document',
            'roi_analysis': 'business_document',
            'strategic_planning': 'business_document',
            'investor_presentation': 'business_document',
            'venture_capital_pitch': 'business_document',
            
            # Technical content
            'technical_documentation': 'technical_documentation',
            'api_documentation_template': 'api_documentation',
            'api_documentation': 'api_documentation',
            'deployment_guide': 'technical_documentation',
            'system_architecture': 'technical_documentation',
            'code_review_standards': 'technical_documentation',
            'integration_manual': 'technical_documentation',
            'troubleshooting_manual': 'technical_documentation',
            'security_protocol': 'technical_documentation',
            'technical_specification': 'technical_documentation',
            
            # Research and academic
            'research_paper_template': 'research_paper',
            'research_paper': 'research_paper',
            'methodology_paper': 'research_paper',
            'literature_review': 'research_paper',
            'peer_review_article': 'research_paper',
            'conference_abstract': 'research_paper',
            'grant_application': 'research_paper',
            'phd_dissertation': 'research_paper',
            'phd_lit_review': 'research_paper',
            'scholarly_commentary': 'research_paper',
            'thesis_defense': 'research_paper',
            
            # Educational content
            'academic_textbook': 'educational',
            'academic_book_chapter': 'educational',
            'beginner_tutorial': 'educational',
            'advanced_masterclass': 'educational',
            'online_course': 'educational',
            'corporate_training': 'educational',
            'certification_prep': 'educational',
            'skill_assessment': 'educational',
            'learning_pathway': 'educational',
            'workshop_facilitator': 'educational',
            'knowledge_base': 'educational',
            'technical_tutor': 'educational',
        }
        
        # FIXED: Templates that should trigger image agent - expanded list
        self.image_enabled_templates = {
            # Blog and article content
            'blog_article_generator',
            'blog_article', 
            'content_marketing',
            
            # Social and visual content
            'social_media_campaign',
            'social_media',
            'social_media_voice',
            
            # Marketing materials
            'press_release',
            'product_launch',
            'brand_storytelling',
            'email_newsletter',
            'email_campaign',
            'newsletter',
            
            # Presentation content
            'investor_presentation',
            'board_presentation',
            'venture_capital_pitch',
            
            # Educational content with visuals
            'beginner_tutorial',
            'online_course',
            'workshop_facilitator',
        }
        
        self._find_and_load_templates()
    
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
        """FIXED: Normalize template with correct classification and image support"""
        
        # Extract template ID for mapping
        template_id = template_data.get('id') or template_data.get('slug') or 'unknown'
        
        # CRITICAL FIX: Apply template type mapping with priority - DEBUGGING ENABLED
        logger.info(f"TEMPLATE CLASSIFICATION: Processing {template_id}")
        logger.info(f"Available mappings: {list(self.template_type_mapping.keys())}")
        
        if template_id in self.template_type_mapping:
            correct_type = self.template_type_mapping[template_id]
            template_data['template_type'] = correct_type
            logger.info(f"SUCCESS: {template_id} -> template_type: {correct_type}")
        else:
            # FIXED: Improved fallback logic with enhanced pattern matching
            name_lower = str(template_data.get('name', '')).lower()
            desc_lower = str(template_data.get('description', '')).lower()
            slug_lower = str(template_data.get('slug', '')).lower()
            
            # Combine all text for analysis
            all_text = f"{name_lower} {desc_lower} {slug_lower}".strip()
            logger.info(f"FALLBACK ANALYSIS: '{all_text}'")
            
            # Enhanced classification with specific pattern priorities
            if 'blog' in template_id or 'article' in template_id:
                template_data['template_type'] = 'blog_article'
            elif 'press' in template_id and 'release' in template_id:
                template_data['template_type'] = 'press_release'
            elif any(word in all_text for word in ['blog', 'article', 'post']):
                template_data['template_type'] = 'blog_article'
            elif any(word in all_text for word in ['press', 'release', 'announcement']):
                template_data['template_type'] = 'press_release'
            elif any(word in all_text for word in ['social', 'campaign', 'media']):
                template_data['template_type'] = 'social_media'
            elif any(word in all_text for word in ['api', 'documentation', 'reference']) and 'api' in all_text:
                template_data['template_type'] = 'api_documentation'
            elif any(word in all_text for word in ['research', 'paper', 'study', 'methodology']):
                template_data['template_type'] = 'research_paper'
            elif any(word in all_text for word in ['email', 'newsletter']) and 'campaign' in all_text:
                template_data['template_type'] = 'email_campaign'
            elif any(word in all_text for word in ['business', 'proposal', 'plan']):
                template_data['template_type'] = 'business_document'
            elif any(word in all_text for word in ['technical', 'guide', 'manual', 'documentation']) and 'technical' in all_text:
                template_data['template_type'] = 'technical_documentation'
            elif any(word in all_text for word in ['tutorial', 'course', 'training', 'educational']):
                template_data['template_type'] = 'educational'
            else:
                template_data['template_type'] = 'article'
                
            logger.warning(f"FALLBACK: {template_id} -> template_type: {template_data['template_type']} (pattern match)")
                
        # CRITICAL FIX: Add image agent configuration based on template type
        template_type = template_data.get('template_type', '')
        if (template_id in self.image_enabled_templates or 
            template_type in ['blog_article', 'social_media', 'content_marketing', 'press_release']):
            template_data['supports_images'] = True
            template_data['image_agent_enabled'] = True
            logger.info(f"ENABLED: Image agent for {template_id} (type: {template_type})")
        else:
            template_data['supports_images'] = False
            template_data['image_agent_enabled'] = False

        # Convert inputs to parameters if needed
        if 'inputs' in template_data:
            template_data = self._convert_inputs_to_parameters(template_data)
        
        # Ensure required fields exist
        template_data.setdefault('parameters', {})
        template_data.setdefault('sections', [])
        template_data.setdefault('generation_mode', 'standard')
        
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

                # CRITICAL: Apply normalization with fixes
                template_data = self.normalize_v2_template(template_data)

                template_name = template_data['id']
                self.templates_cache[template_name] = template_data
                loaded_count += 1

                logger.info(f"Loaded: {template_name} | Type: {template_data.get('template_type')} | Images: {template_data.get('image_agent_enabled', False)}")

            except Exception as e:
                logger.error(f"Error loading template {yaml_file.name}: {e}")
        
        logger.info(f"Successfully loaded {loaded_count} templates with correct classification")

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
    """Get a template by name with correct classification"""
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