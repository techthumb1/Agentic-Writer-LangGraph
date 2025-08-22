# langgraph_app/core/content_manager.py
"""
Content management for templates, style profiles, and content operations
"""

import os
import yaml
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..config.settings import settings
from ..models.api_models import ContentTemplate, StyleProfile, TemplateParameter
from ..utils.yaml_utils import load_yaml_file_safe, safe_yaml_load, validate_template_structure

logger = logging.getLogger(__name__)

class ContentManager:
    """Manages templates, style profiles, and content operations."""
    
    def __init__(self):
        self._templates_cache: Optional[List[ContentTemplate]] = None
        self._profiles_cache: Optional[List[StyleProfile]] = None
        self._cache_timestamp = None
        self.cache_ttl = 300  # 5 minutes
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._cache_timestamp is None:
            return False
        return (datetime.now() - self._cache_timestamp).seconds < self.cache_ttl
    
    def load_templates(self, force_reload: bool = False) -> List[ContentTemplate]:
        """Load and validate all content templates."""
        if not force_reload and self._is_cache_valid() and self._templates_cache:
            return self._templates_cache
        
        templates: List[ContentTemplate] = []
        templates_loaded = 0

        for template_dir in settings.TEMPLATE_PATHS:
            if not os.path.isdir(template_dir):
                continue

            try:
                for filename in sorted(os.listdir(template_dir)):
                    if not filename.lower().endswith((".yaml", ".yml")):
                        continue

                    file_path = os.path.join(template_dir, filename)
                    template_data = load_yaml_file_safe(file_path)

                    if not template_data or not isinstance(template_data, dict):
                        logger.error(f"Failed to load template: {file_path}")
                        continue

                    # Normalize V2 `inputs` -> V1 `parameters` before parsing
                    template_data = self._normalize_inputs_to_parameters(template_data)

                    try:
                        template_id = str(template_data.get("id") or os.path.splitext(filename)[0])

                        # Process parameters
                        parameters_data = template_data.get("parameters") or {}
                        processed_parameters = self._parse_template_parameters(parameters_data)

                        template = ContentTemplate(
                            id=template_id,
                            slug=template_data.get("slug") or template_id,
                            name=template_data.get("name") or template_id.replace("_", " ").title(),
                            description=template_data.get("description") or "",
                            category=template_data.get("category") or "general",
                            defaults=template_data.get("defaults") or {},
                            system_prompt=template_data.get("system_prompt"),
                            structure=template_data.get("structure") or {},
                            research=template_data.get("research") or {},
                            parameters=processed_parameters,
                            metadata=template_data.get("metadata") or {},
                            version=str(template_data.get("version") or "2.0.0"),
                            filename=filename,
                        )

                        templates.append(template)
                        templates_loaded += 1
                        logger.info(
                            f"Loaded template: {template.name} ({template.id}) "
                            f"from {filename} with {len(processed_parameters)} parameters"
                        )

                    except Exception as e:
                        logger.error(f"Invalid template format in {filename}: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error loading templates from {template_dir}: {e}")
                continue

        if templates_loaded == 0:
            raise SystemExit("ENTERPRISE MODE: No templates could be loaded - system cannot operate")

        logger.info(f"Total templates loaded: {len(templates)}")
        
        # Update cache
        self._templates_cache = templates
        self._cache_timestamp = datetime.now()
        
        return templates
    
    def load_style_profiles(self, force_reload: bool = False) -> List[StyleProfile]:
        """Load and validate all style profiles."""
        if not force_reload and self._is_cache_valid() and self._profiles_cache:
            return self._profiles_cache
        
        profiles = []
        profiles_loaded = 0

        for profile_dir in settings.STYLE_PROFILE_PATHS:
            if not os.path.exists(profile_dir):
                continue

            try:
                files = os.listdir(profile_dir)

                for filename in files:
                    if not filename.endswith('.yaml'):
                        continue

                    file_path = os.path.join(profile_dir, filename)
                    profile_data = load_yaml_file_safe(file_path)

                    if not profile_data:
                        logger.error(f"Failed to load style profile: {file_path}")
                        continue

                    try:
                        # Normalize length_limit subfields (convert numeric strings to int)
                        length = profile_data.get("length_limit", {})
                        for k in ("min", "max", "words", "target"):
                            if k in length:
                                v = length[k]
                                if isinstance(v, str) and v.isdigit():
                                    length[k] = int(v)
                        
                        profile_id = profile_data.get('id', filename.replace('.yaml', ''))

                        profile = StyleProfile(
                            id=profile_id,
                            name=profile_data.get("name", profile_id.replace('_', ' ').title()),
                            description=profile_data.get("description", ""),
                            category=profile_data.get("category", "general"),
                            platform=profile_data.get("platform"),
                            tone=profile_data.get("tone"),
                            voice=profile_data.get("voice"),
                            structure=profile_data.get("structure"),
                            audience=profile_data.get("audience"),
                            system_prompt=profile_data.get("system_prompt"),
                            length_limit=length,
                            settings=profile_data.get("settings", {}),
                            formatting=profile_data.get("formatting", {}),
                            metadata=profile_data.get("metadata", {}),
                            filename=filename
                        )
                        profiles.append(profile)
                        profiles_loaded += 1
                        logger.info(f"Loaded style profile: {profile.name} ({profile.id})")

                    except Exception as e:
                        logger.error(f"Invalid style profile format in {filename}: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error loading style profiles from {profile_dir}: {e}")
                continue

        if profiles_loaded == 0:
            raise SystemExit("ENTERPRISE MODE: No style profiles could be loaded - system cannot operate")

        logger.info(f"Total style profiles loaded: {len(profiles)}")
        
        # Update cache
        self._profiles_cache = profiles
        self._cache_timestamp = datetime.now()
        
        return profiles
    
    def get_template_by_id(self, template_id: str) -> Optional[ContentTemplate]:
        """Get a specific template by ID."""
        templates = self.load_templates()
        return next((t for t in templates if t.id == template_id), None)
    
    def get_style_profile_by_id(self, profile_id: str) -> Optional[StyleProfile]:
        """Get a specific style profile by ID."""
        profiles = self.load_style_profiles()
        return next((p for p in profiles if p.id == profile_id), None)
    
    def find_template_by_name_variations(self, template_name: str) -> Optional[ContentTemplate]:
        """Find template by trying various name variations."""
        templates = self.load_templates()
        search_terms = [
            template_name,
            template_name.replace('.yaml', ''),
            template_name.replace('-', '_'),
            template_name.replace('_', '-'),
        ]
        
        for search_term in search_terms:
            template = next((t for t in templates if t.id == search_term), None)
            if template:
                return template
        return None
    
    def find_style_profile_by_name_variations(self, profile_name: str) -> Optional[StyleProfile]:
        """Find style profile by trying various name variations."""
        profiles = self.load_style_profiles()
        search_terms = [
            profile_name,
            profile_name.replace('.yaml', ''),
            profile_name.replace('-', '_'),
            profile_name.replace('_', '-'),
        ]
        
        for search_term in search_terms:
            profile = next((p for p in profiles if p.id == search_term), None)
            if profile:
                return profile
        return None
    
    def save_template(self, template_data: Dict[str, Any]) -> bool:
        """Save a new template to disk."""
        try:
            # Validate required fields
            if 'name' not in template_data or 'system_prompt' not in template_data:
                raise ValueError("Template must have 'name' and 'system_prompt'")
            
            # Generate ID from name if not provided
            if 'id' not in template_data:
                template_data['id'] = template_data['name'].lower().replace(' ', '_').replace('-', '_')
            
            # Ensure filename
            filename = f"{template_data['id']}.yaml"
            
            # Use first available template directory
            template_dir = settings.TEMPLATE_PATHS[0]
            file_path = os.path.join(template_dir, filename)
            
            # Check if template already exists
            if os.path.exists(file_path):
                raise ValueError("Template already exists")
            
            # Add metadata
            template_data.setdefault('metadata', {})
            template_data['metadata']['created_at'] = datetime.now().isoformat()
            template_data['metadata']['version'] = '1.0.0'
            
            # Save template
            with open(file_path, 'w') as f:
                yaml.dump(template_data, f, default_flow_style=False)
            
            # Clear cache to force reload
            self._templates_cache = None
            
            logger.info(f"Template saved: {template_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False
    
    def save_style_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Save a new style profile to disk."""
        try:
            # Validate required fields
            if 'name' not in profile_data:
                raise ValueError("Style profile must have 'name'")
            
            # Generate ID from name if not provided
            if 'id' not in profile_data:
                profile_data['id'] = profile_data['name'].lower().replace(' ', '_').replace('-', '_')
            
            # Ensure filename
            filename = f"{profile_data['id']}.yaml"
            
            # Use first available profile directory
            profile_dir = settings.STYLE_PROFILE_PATHS[0]
            file_path = os.path.join(profile_dir, filename)
            
            # Check if profile already exists
            if os.path.exists(file_path):
                raise ValueError("Style profile already exists")
            
            # Add metadata
            profile_data.setdefault('metadata', {})
            profile_data['metadata']['created_at'] = datetime.now().isoformat()
            profile_data.setdefault('category', 'general')
            
            # Save profile
            with open(file_path, 'w') as f:
                yaml.dump(profile_data, f, default_flow_style=False)
            
            # Clear cache to force reload
            self._profiles_cache = None
            
            logger.info(f"Style profile saved: {profile_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save style profile: {e}")
            return False
    
    def get_content_items(self) -> List[Dict[str, Any]]:
        """Get all content items from generated_content directory."""
        try:
            base_path = Path(__file__).parent.parent.parent
            content_dir = base_path / "generated_content"
            
            content_items = []
            
            if content_dir.exists():
                for week_dir in content_dir.iterdir():
                    if not week_dir.is_dir():
                        continue
                    
                    for json_file in week_dir.glob("*.json"):
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            
                            content_id = json_file.stem
                            content_items.append({
                                "id": content_id,
                                "title": metadata.get('title', content_id.replace('_', ' ').title()),
                                "status": metadata.get('status', 'draft'),
                                "type": metadata.get('type', 'article'),
                                "date": metadata.get('createdAt', datetime.now().isoformat()),
                                "createdAt": metadata.get('createdAt', datetime.now().isoformat()),
                                "updatedAt": metadata.get('updatedAt', datetime.now().isoformat()),
                                "views": metadata.get('views', 0),
                                "week": week_dir.name
                            })
                        except Exception as e:
                            logger.warning(f"Error processing {json_file}: {e}")
                            continue
            
            # Sort by creation date (newest first)
            content_items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
            return content_items
            
        except Exception as e:
            logger.error(f"Failed to get content items: {e}")
            return []
    
    def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get specific content item by ID."""
        try:
            base_path = Path(__file__).parent.parent.parent
            content_dir = base_path / "generated_content"
            
            for week_dir in content_dir.iterdir():
                if not week_dir.is_dir():
                    continue
                
                json_file = week_dir / f"{content_id}.json"
                md_file = week_dir / f"{content_id}.md"
                
                if json_file.exists():
                    with open(json_file, 'r') as f:
                        metadata = json.load(f)
                    
                    content = metadata.get('content', '')
                    if md_file.exists():
                        with open(md_file, 'r') as f:
                            content = f.read()
                    
                    return {
                        "id": content_id,
                        "title": metadata.get('title', content_id.replace('_', ' ').title()),
                        "content": content,
                        "contentHtml": metadata.get('contentHtml'),
                        "status": metadata.get('status', 'draft'),
                        "type": metadata.get('type', 'article'),
                        "createdAt": metadata.get('createdAt'),
                        "updatedAt": metadata.get('updatedAt'),
                        "views": metadata.get('views', 0),
                        "author": metadata.get('author'),
                        "metadata": metadata.get('metadata', {}),
                        "week": week_dir.name
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get content {content_id}: {e}")
            return None
    
    def _normalize_inputs_to_parameters(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize V2 'inputs' format to V1 'parameters' format."""
        if not isinstance(template_data, dict):
            return template_data
        if "parameters" in template_data or "inputs" not in template_data:
            return template_data

        inputs = template_data.get("inputs") or {}
        if not isinstance(inputs, dict):
            return template_data

        params: Dict[str, Any] = {}
        allowed = {"string","text","textarea","number","select","boolean","array","date","email","url"}

        for key, spec in inputs.items():
            spec = spec or {}
            default_val = spec.get("default")

            if isinstance(default_val, bool):
                ptype = "boolean"
            elif isinstance(default_val, (int, float)):
                ptype = "number"
            elif isinstance(spec.get("options"), list):
                ptype = "select"
            else:
                ptype = spec.get("type") if spec.get("type") in allowed else "text"

            params[key] = {
                "name": key,
                "label": spec.get("label", key.replace("_", " ").title()),
                "type": ptype,
                "required": bool(spec.get("required", False)),
                "default": default_val,
                "options": spec.get("options"),
                "placeholder": spec.get("placeholder"),
                "description": spec.get("description"),
                "validation": spec.get("validation", {}),
            }

        template_data["parameters"] = params
        return template_data
    
    def _parse_template_parameters(self, parameters_data: Any) -> Dict[str, TemplateParameter]:
        """Parse parameters from various formats."""
        processed_parameters = {}
        
        if isinstance(parameters_data, dict):
            for key, param in parameters_data.items():
                if isinstance(param, dict):
                    processed_parameters[key] = TemplateParameter(
                        name=key,
                        label=param.get('label', key.replace('_', ' ').title()),
                        type=param.get('type', 'string'),
                        description=param.get('description'),
                        placeholder=param.get('placeholder'),
                        default=param.get('default'),
                        options=param.get('options'),
                        required=param.get('required', False)
                    )
                else:
                    processed_parameters[key] = TemplateParameter(
                        name=key,
                        label=key.replace('_', ' ').title(),
                        type='string',
                        default=param if param is not None else None,
                        required=False
                    )
        
        elif isinstance(parameters_data, list):
            for param in parameters_data:
                if isinstance(param, dict) and 'name' in param:
                    param_name = param['name']
                    processed_parameters[param_name] = TemplateParameter(
                        name=param_name,
                        label=param.get('label', param_name.replace('_', ' ').title()),
                        type=param.get('type', 'string'),
                        description=param.get('description'),
                        placeholder=param.get('placeholder'),
                        default=param.get('default'),
                        options=param.get('options'),
                        required=param.get('required', False)
                    )
                elif isinstance(param, str):
                    processed_parameters[param] = TemplateParameter(
                        name=param,
                        label=param.replace('_', ' ').title(),
                        type='string',
                        required=False
                    )
                elif isinstance(param, dict):
                    for key, value in param.items():
                        processed_parameters[key] = TemplateParameter(
                            name=key,
                            label=key.replace('_', ' ').title(),
                            type='string',
                            default=value if not isinstance(value, dict) else None,
                            required=False
                        )
                        break
        
        return processed_parameters

# Global content manager instance
content_manager = ContentManager()