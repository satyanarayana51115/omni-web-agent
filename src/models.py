"""Data models for Omni-Web-Agent element metadata, healing candidates, and telemetry."""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    HOVER = "hover"
    NAVIGATE = "navigate"
    ASSERT = "assert"


class ElementFingerprint(BaseModel):
    """Multi-attribute fingerprint extracted from a DOM element."""

    tag_name: str = Field(..., description="HTML tag: input, button, a, etc.")
    id: Optional[str] = Field(None, description="DOM ID attribute if present")
    name: Optional[str] = Field(None, description="Name attribute if present")
    classes: List[str] = Field(default_factory=list, description="Class list")
    text_content: Optional[str] = Field(None, description="Normalized inner text")
    aria_label: Optional[str] = Field(None, description="Accessible label")
    role: Optional[str] = Field(None, description="ARIA role")
    placeholder: Optional[str] = Field(None, description="Input placeholder")
    element_type: Optional[str] = Field(None, description="Input type (e.g., submit, text)")
    data_testid: Optional[str] = Field(None, description="Test hook attribute")
    css_selector: str = Field(..., description="Original or primary CSS selector")
    xpath: Optional[str] = Field(None, description="Absolute/Relative XPath")
    bounding_box: Optional[Dict[str, float]] = Field(None, description="Visual x, y, width, height")


class HealingMatch(BaseModel):
    """Scored candidate discovered during DOM tree scanning."""

    candidate_fingerprint: ElementFingerprint
    match_score: float = Field(..., ge=0.0, le=1.0, description="Weighted similarity score")
    selector_used: str = Field(..., description="Selector that located this candidate")
    confidence_tier: str = Field(..., description="HIGH (>=0.85), MEDIUM (>=0.65), LOW (<0.65)")
    reasons: List[str] = Field(default_factory=list, description="Attribute-level match rationales")


class ActionStep(BaseModel):
    """Single step in an automated exploration or test sequence."""

    step_id: int
    action_type: ActionType
    target_selector: str
    target_fingerprint: Optional[ElementFingerprint] = None
    value: Optional[str] = Field(None, description="Value for fill, select, or URL for navigate")
    description: str = ""
    timeout_ms: int = Field(default=5000, description="Maximum wait time before initiating heal")


class StepResult(BaseModel):
    """Outcome and telemetry of an executed action step."""

    step_id: int
    success: bool
    healed: bool = False
    original_selector: str
    effective_selector: str
    match_score: Optional[float] = None
    healing_reasons: List[str] = Field(default_factory=list)
    duration_ms: float
    error_message: Optional[str] = None