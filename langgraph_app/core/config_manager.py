# src/langgraph_app/core/config_manager.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple

import yaml
from pydantic import ValidationError

from .schemas import Template, StyleProfile


class ConfigManagerError(RuntimeError):
    pass


class ConfigValidationError(ConfigManagerError):
    def __init__(self, errors: List[str]):
        super().__init__("Invalid YAML configuration(s):\n" + "\n".join(errors))
        self.errors = errors


class ConfigManager:
    """
    Loads and validates all YAML configs at startup and stores them in-memory.
    Fails fast (raises) if any file is invalid.
    """

    def __init__(
        self,
        base_dir: Path | None = None,
        templates_subdir: str = "data/content_templates",
        styles_subdir: str = "data/style_profiles",
    ) -> None:
        self.base_dir = Path(base_dir) if base_dir else None
        self.data_root = self._locate_data_root()
        self.templates_dir = self.data_root / templates_subdir.split("data/")[-1]
        self.styles_dir = self.data_root / styles_subdir.split("data/")[-1]

        if not self.templates_dir.exists() or not self.styles_dir.exists():
            raise ConfigManagerError(
                f"Missing required directories. "
                f"templates_dir={self.templates_dir}, styles_dir={self.styles_dir}"
            )

        # Public: dicts for fast access by id
        self.templates_by_id: Dict[str, Dict] = {}
        self.styles_by_id: Dict[str, Dict] = {}

        # Also keep pydantic objects if needed by tests
        self._template_models: Dict[str, Template] = {}
        self._style_models: Dict[str, StyleProfile] = {}

        self._load_all_or_raise()

    # --- Public API ------------------------------------------------------------------------------

    def get_template(self, template_id: str) -> Dict:
        try:
            return self.templates_by_id[template_id]
        except KeyError:
            raise ConfigManagerError(f"Template '{template_id}' not found.")

    def get_style_profile(self, style_id: str) -> Dict:
        try:
            return self.styles_by_id[style_id]
        except KeyError:
            raise ConfigManagerError(f"Style profile '{style_id}' not found.")

    def list_templates(self) -> List[str]:
        return sorted(self.templates_by_id.keys())

    def list_style_profiles(self) -> List[str]:
        return sorted(self.styles_by_id.keys())

    # --- Internals --------------------------------------------------------------------------------

    def _locate_data_root(self) -> Path:
        """
        Resolve the absolute data directory.
        Priority:
          1) WRITERZ_DATA_DIR env
          2) explicit base_dir (if given)
          3) nearest 'data/' up from this file
          4) CWD/data
        """
        env_dir = os.getenv("WRITERZ_DATA_DIR")
        if env_dir:
            candidate = Path(env_dir).expanduser().resolve()
            if candidate.exists():
                return candidate

        if self.base_dir:
            candidate = self.base_dir / "data"
            if candidate.exists():
                return candidate.resolve()

        # Walk up from this file to find a sibling 'data'
        current = Path(__file__).resolve()
        for parent in [current.parent, *current.parents]:
            candidate = parent / "data"
            if candidate.exists():
                return candidate.resolve()

        # Fallback to CWD/data
        cwd_candidate = Path.cwd() / "data"
        if cwd_candidate.exists():
            return cwd_candidate.resolve()

        raise ConfigManagerError("Could not locate 'data/' directory.")

    def _load_all_or_raise(self) -> None:
        errors: List[str] = []

        tpl_items = self._load_yaml_dir(self.templates_dir)
        stl_items = self._load_yaml_dir(self.styles_dir)

        # Validate templates
        for path, data in tpl_items:
            try:
                model = Template.model_validate(data)
            except ValidationError as ve:
                errors.append(f"[TEMPLATE] {path.name}: {ve}")
                continue

            tid = model.id
            if tid in self.templates_by_id:
                errors.append(f"[TEMPLATE] Duplicate id '{tid}' in {path.name}")
                continue

            self._template_models[tid] = model
            self.templates_by_id[tid] = model.model_dump(mode="python")

        # Validate styles
        for path, data in stl_items:
            try:
                model = StyleProfile.model_validate(data)
            except ValidationError as ve:
                errors.append(f"[STYLE] {path.name}: {ve}")
                continue

            sid = model.id
            if sid in self.styles_by_id:
                errors.append(f"[STYLE] Duplicate id '{sid}' in {path.name}")
                continue

            self._style_models[sid] = model
            self.styles_by_id[sid] = model.model_dump(mode="python")

        if errors:
            # Fail fast so the app never boots with invalid configs
            raise ConfigValidationError(errors)

    @staticmethod
    def _load_yaml_dir(directory: Path) -> List[Tuple[Path, Dict]]:
        if not directory.exists():
            return []
        items: List[Tuple[Path, Dict]] = []
        for path in sorted(directory.glob("*.y*ml")):
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                items.append((path, data))
        return items
