# src/langgraph_app/api/routes/configuration.py
"""
API routes for retrieving available templates and style profiles (enterprise envelope)
and exposing detail endpoints that normalize YAML inputs -> parameters for the frontend.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request, HTTPException, Query

from ...core.config_manager import ConfigManager

logger = logging.getLogger("writerzroom.api.config")
router = APIRouter()


# -------- Helpers --------

def _infer_param_type_from_default(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, list):
        # Treat list defaults as a multi/selector (UI can render select)
        return "select"
    if value and len(str(value)) > 100:
        return "textarea"
    return "string"

def _normalize_parameters(yaml_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepts a template dict (from ConfigManager) and returns a frontend-ready
    parameters map. Works with:
      - inputs: {topic: {required: true, default: ...}, ...}
      - parameters: {topic: {type: ..., default: ...}, ...}
      - legacy list format [{name: ..., type: ...}, ...] (rare)
    """
    # Prefer explicit keys if present
    params_data: Any = (
        yaml_obj.get("parameters") or
        yaml_obj.get("inputs") or
        {}
    )
    out: Dict[str, Any] = {}

    # Dict format
    if isinstance(params_data, dict):
        # Heuristic: looks like inputs if any value has required/default keys
        looks_like_inputs = any(
            isinstance(v, dict) and ("required" in v or "default" in v)
            for v in list(params_data.values())[:3]
        )
        for key, spec in params_data.items():
            if not isinstance(spec, dict):
                # simple scalar default
                out[key] = {
                    "name": key,
                    "label": key.replace("_", " ").title(),
                    "type": _infer_param_type_from_default(spec),
                    "required": False,
                    "default": spec,
                    "description": "",
                    "placeholder": "",
                    "options": None,
                }
                continue

            # inputs-like block
            if looks_like_inputs:
                inferred_type = _infer_param_type_from_default(spec.get("default"))
                if "options" in spec and isinstance(spec["options"], list):
                    inferred_type = "select"

                out[key] = {
                    "name": key,
                    "label": spec.get("label", key.replace("_", " ").title()),
                    "type": spec.get("type", inferred_type) or inferred_type,
                    "required": bool(spec.get("required", False)),
                    "default": spec.get("default"),
                    "description": spec.get("description", ""),
                    "placeholder": spec.get("placeholder", ""),
                    "options": spec.get("options", None) if spec.get("options") else None,
                    "validation": spec.get("validation", {}) or {},
                }
            else:
                # already parameters-like
                out[key] = {
                    "name": key,
                    "label": spec.get("label", key.replace("_", " ").title()),
                    "type": spec.get("type", "string"),
                    "required": bool(spec.get("required", False)),
                    "default": spec.get("default"),
                    "description": spec.get("description", ""),
                    "placeholder": spec.get("placeholder", ""),
                    "options": spec.get("options", None) if spec.get("options") else None,
                    "validation": spec.get("validation", {}) or {},
                }
        return out

    # Legacy list format
    if isinstance(params_data, list):
        for spec in params_data:
            if isinstance(spec, dict) and "name" in spec:
                key = spec["name"]
                out[key] = {
                    "name": key,
                    "label": spec.get("label", key.replace("_", " ").title()),
                    "type": spec.get("type", "string"),
                    "required": bool(spec.get("required", False)),
                    "default": spec.get("default"),
                    "description": spec.get("description", ""),
                    "placeholder": spec.get("placeholder", ""),
                    "options": spec.get("options", None) if spec.get("options") else None,
                    "validation": spec.get("validation", {}) or {},
                }
        return out

    # Fallback
    return {}


# -------- List endpoints (enterprise envelope) --------

@router.get("/templates")
async def list_templates(
    request: Request,
    page: int = 1,
    limit: int = 100
):
    """
    Returns a paginated list of available content templates (enterprise envelope).
    """
    config_manager: ConfigManager = request.app.state.config_manager
    if not config_manager:
        raise HTTPException(status_code=503, detail="Configuration Manager not available.")

    template_ids = config_manager.list_templates()
    start = (page - 1) * limit
    end = start + limit
    paginated_ids = template_ids[start:end]

    items: List[Dict[str, Any]] = []
    for tid in paginated_ids:
        try:
            t = config_manager.get_template(tid)
            items.append({
                "id": t.get("id", tid),
                "name": t.get("name", tid),
                "template_type": t.get("template_type"),
                "description": t.get("metadata", {}).get("strategy", "") or t.get("description", ""),
            })
        except Exception as ex:
            logger.warning(f"Could not read template {tid}: {ex}")

    return {"success": True, "data": {"items": items, "count": len(template_ids), "page": page, "limit": limit}}


@router.get("/style-profiles")
async def list_style_profiles(
    request: Request,
    page: int = 1,
    limit: int = 100
):
    """
    Returns a paginated list of available style profiles (enterprise envelope).
    """
    config_manager: ConfigManager = request.app.state.config_manager
    if not config_manager:
        raise HTTPException(status_code=503, detail="Configuration Manager not available.")

    profile_ids = config_manager.list_style_profiles()
    start = (page - 1) * limit
    end = start + limit
    paginated_ids = profile_ids[start:end]

    items: List[Dict[str, Any]] = []
    for pid in paginated_ids:
        try:
            p = config_manager.get_style_profile(pid)
            items.append({
                "id": p.get("id", pid),
                "name": p.get("name", pid),
                "tone": p.get("tone"),
                "voice": p.get("voice"),
                "audience": p.get("audience"),
                "platform": p.get("platform", "web"),
            })
        except Exception as ex:
            logger.warning(f"Could not read style profile {pid}: {ex}")

    return {"success": True, "data": {"items": items, "count": len(profile_ids), "page": page, "limit": limit}}


# -------- Detail endpoints (normalize inputs -> parameters) --------

@router.get("/templates/{template_id}")
async def get_template_details(template_id: str, request: Request):
    """
    Returns full template detail including normalized `parameters` map.
    """
    config_manager: ConfigManager = request.app.state.config_manager
    if not config_manager:
        raise HTTPException(status_code=503, detail="Configuration Manager not available.")

    try:
        t = config_manager.get_template(template_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    parameters = _normalize_parameters(t)

    payload = {
        "id": t.get("id", template_id),
        "name": t.get("name", template_id),
        "slug": t.get("slug", t.get("id", template_id)),
        "description": t.get("description"),
        "template_type": t.get("template_type"),
        "category": t.get("category"),
        "version": t.get("version", "1.0"),
        "parameters": parameters,
        "metadata": t.get("metadata", {}),
    }
    return {"success": True, "data": payload}


@router.get("/style-profiles/{profile_id}")
async def get_style_profile_details(profile_id: str, request: Request):
    """
    Returns full style profile detail (pass-through; no special normalization needed).
    """
    config_manager: ConfigManager = request.app.state.config_manager
    if not config_manager:
        raise HTTPException(status_code=503, detail="Configuration Manager not available.")

    try:
        p = config_manager.get_style_profile(profile_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Style profile '{profile_id}' not found")

    payload = {
        "id": p.get("id", profile_id),
        "name": p.get("name", profile_id),
        "description": p.get("description"),
        "category": p.get("category", "general"),
        "platform": p.get("platform"),
        "tone": p.get("tone"),
        "voice": p.get("voice"),
        "structure": p.get("structure"),
        "audience": p.get("audience"),
        "system_prompt": p.get("system_prompt"),
        "length_limit": p.get("length_limit", {}),
        "settings": p.get("settings", {}),
        "formatting": p.get("formatting", {}),
        "metadata": p.get("metadata", {}),
    }
    return {"success": True, "data": payload}
