# src/langgraph_app/core/schemas.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


# === Shared / Nested models ===

class Section(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=False)
    name: str = Field(..., min_length=1)
    estimated_words: int = Field(300, ge=50, le=10000)


class Structure(BaseModel):
    model_config = ConfigDict(extra="allow")
    approach: str = Field("standard", min_length=1)  # Added default
    sections: List[Union[str, Section]] = Field(default_factory=list)
    header_hierarchy: List[int] = Field(default_factory=lambda: [1, 2, 2, 3])  # Added default

    @field_validator("header_hierarchy")
    @classmethod
    def _validate_header_hierarchy(cls, v: List[int]) -> List[int]:
        if any((not isinstance(x, int) or x < 1 or x > 6) for x in v):
            raise ValueError("header_hierarchy must be a list of integers in [1..6].")
        return v


class Requirements(BaseModel):
    model_config = ConfigDict(extra="allow")
    key_messages: List[str] = Field(default_factory=list)  # Made optional
    success_metrics: Dict[str, Any] = Field(default_factory=dict)  # Made optional
    requires_code: bool = False


class ResearchConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    priorities: List[str] = Field(default_factory=list)  # Made optional


class CodeExample(BaseModel):
    model_config = ConfigDict(extra="allow")
    placeholder: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)


class CodeGenerationConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    languages: List[str] = Field(default_factory=lambda: ["python"])
    style: str = "technical"
    examples: List[CodeExample] = Field(default_factory=list)


class ImagePlacement(BaseModel):
    model_config = ConfigDict(extra="allow")
    after_section: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)


class ImageGenerationConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    enabled: bool = False
    style: str = "professional"
    placements: List[ImagePlacement] = Field(default_factory=list)


class FormattingConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    output_format: str = Field("markdown", min_length=1)  # Added default
    citation_format: str = "apa"
    emphasis_elements: List[Dict[str, Literal["bold", "italic"]]] = Field(default_factory=list)


class Metadata(BaseModel):
    model_config = ConfigDict(extra="allow")
    strategy: str = Field("general", min_length=1)  # Added default
    positioning: str = Field("standard", min_length=1)  # Added default
    complexity: int = Field(5, ge=1, le=10)
    domain: Optional[str] = None


# === Template schema ===

class Template(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field("", min_length=1)  # Will be set from slug if missing
    name: Optional[str] = None
    template_type: str = Field("general", min_length=1)  # Added default

    metadata: Metadata = Field(default_factory=Metadata)  # Made optional
    requirements: Requirements = Field(default_factory=Requirements)  # Made optional
    research: ResearchConfig = Field(default_factory=ResearchConfig)  # Made optional
    structure: Structure = Field(default_factory=Structure)  # Made optional

    distribution_channels: List[str] = Field(default_factory=lambda: ["web"])  # Made optional

    keywords: Optional[Union[str, List[str]]] = None
    code_generation_config: Optional[CodeGenerationConfig] = None
    image_generation_config: Optional[ImageGenerationConfig] = None
    instructions: Optional[str] = None
    dynamic_parameters: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("distribution_channels")
    @classmethod
    def _validate_distribution_channels(cls, v: List[str]) -> List[str]:
        if any(not isinstance(x, str) or not x.strip() for x in v):
            raise ValueError("distribution_channels must be a non-empty list of strings.")
        return [x.strip() for x in v]

    @model_validator(mode="after")
    def _enforce_code_requirements(self) -> "Template":
        if self.requirements.requires_code and not self.code_generation_config:
            raise ValueError("Template requires_code=True but code_generation_config is missing.")
        return self

    @model_validator(mode="after")
    def _normalize_keywords(self) -> "Template":
        if isinstance(self.keywords, str):
            parts = [p.strip() for p in self.keywords.split(",") if p.strip()]
            self.keywords = parts or None
        elif isinstance(self.keywords, list):
            self.keywords = [str(k).strip() for k in self.keywords if str(k).strip()]
        return self


# === Style Profile schema ===

class StyleProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    system_prompt: str = Field(..., min_length=1)
    tone: str = Field(..., min_length=1)
    voice: str = Field(..., min_length=1)
    platform: str = "web"
    audience: str = Field(..., min_length=1)
    category: Optional[str] = None
    author: Optional[str] = None

    formatting: FormattingConfig = Field(default_factory=FormattingConfig)  # Made optional with default
    forbidden_patterns: List[str] = Field(default_factory=list)

    @field_validator("forbidden_patterns")
    @classmethod
    def _validate_patterns(cls, v: List[str]) -> List[str]:
        return [p for p in v if isinstance(p, str) and p.strip()]