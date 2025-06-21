# langgraph_app/utils.py

import os
import yaml
from typing import Dict, Any, Optional


def load_system_prompt(prompt_name: str) -> str:
    """Load system prompt from prompts/writer/ directory"""
    prompt_path = os.path.join("prompts", "writer", prompt_name)
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: System prompt not found: {prompt_name}")
        return "You are a helpful, high-level technical writing assistant."


def load_style_profile(name: str) -> Dict[str, Any]:
    """Load style profile from data/style_profiles/"""
    try:
        with open(f"data/style_profiles/{name}.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Style profile not found: {name}.yaml, using default")
        return {
            "structure": "hook → explanation → example → summary",
            "voice": "experienced and conversational", 
            "tone": "educational",
            "system_prompt": "grad_level_writer.txt"
        }


def load_content_template(name: str) -> Dict[str, Any]:
    """Load content template from data/content_templates/"""
    try:
        with open(f"data/content_templates/{name}.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Template not found: {name}.yaml")
        return {}


def list_style_profiles() -> list:
    """List all available style profiles"""
    try:
        profiles_dir = "data/style_profiles"
        if os.path.exists(profiles_dir):
            return [f.replace('.yaml', '') for f in os.listdir(profiles_dir) if f.endswith('.yaml')]
        return []
    except Exception as e:
        print(f"Error listing style profiles: {e}")
        return []


def list_content_templates() -> list:
    """List all available content templates"""
    try:
        templates_dir = "data/content_templates"
        if os.path.exists(templates_dir):
            return [f.replace('.yaml', '') for f in os.listdir(templates_dir) if f.endswith('.yaml')]
        return []
    except Exception as e:
        print(f"Error listing templates: {e}")
        return []


def validate_file_exists(file_path: str) -> bool:
    """Check if a file exists"""
    return os.path.exists(file_path)


def get_file_path(file_type: str, name: str) -> str:
    """Get the full path for a given file type and name"""
    if file_type == "style_profile":
        return f"data/style_profiles/{name}.yaml"
    elif file_type == "content_template":
        return f"data/content_templates/{name}.yaml"
    elif file_type == "system_prompt":
        return f"prompts/writer/{name}"
    else:
        raise ValueError(f"Unknown file type: {file_type}")