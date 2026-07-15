"""Step definitions — the stable contract between YAML-based and AI-generated instructions.

Each Step subclass can come from either:
1. YAML parsing (human-authored)
2. An LLM/VLM planner (Stage 9+, AI-generated)

This symmetry is critical — downstream code (matcher, executor, runner, reporter)
only consumes Step objects and must not care about origin.
"""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class Step(BaseModel):
    """Base class for all instruction steps."""

    class Config:
        # Allow validation to be flexible; downstream code may add fields
        extra = "allow"

    def describe(self) -> str:
        """Return a human-readable description of this step."""
        return f"{self.__class__.__name__}"


class TapStep(Step):
    """Tap a target element (identified by text or icon)."""

    target: str = Field(
        description="The text or icon name to tap (resolved via ElementMatcher)"
    )
    occurrence: Optional[int] = Field(
        default=None,
        description="If multiple matches exist, tap the Nth occurrence (1-indexed)",
    )
    near: Optional[str] = Field(
        default=None,
        description="If multiple matches exist, disambiguate by choosing the match nearest to this target",
    )

    def describe(self) -> str:
        s = f"Tap '{self.target}'"
        if self.occurrence:
            s += f" (occurrence {self.occurrence})"
        if self.near:
            s += f" (nearest to '{self.near}')"
        return s


class TypeStep(Step):
    """Type text into a field."""

    text: str = Field(description="Text to type")
    into: str = Field(description="Target field identifier (text on the label or field itself)")

    def describe(self) -> str:
        return f"Type '{self.text}' into '{self.into}'"


class TapIconStep(Step):
    """Tap an icon (non-text control)."""

    icon: str = Field(description="Icon identifier from the icon catalog")
    occurrence: Optional[int] = Field(
        default=None, description="If multiple matches, tap the Nth occurrence (1-indexed)"
    )

    def describe(self) -> str:
        s = f"Tap icon '{self.icon}'"
        if self.occurrence:
            s += f" (occurrence {self.occurrence})"
        return s


class SwipeStep(Step):
    """Perform a swipe gesture."""

    direction: Literal["up", "down", "left", "right"] = Field(
        description="Direction of the swipe"
    )
    amount: float = Field(
        default=0.6,
        description="Swipe distance as a fraction of the screen dimension (0.0-1.0)",
    )

    def describe(self) -> str:
        return f"Swipe {self.direction} ({self.amount * 100}% of screen)"


class AssertVisibleStep(Step):
    """Assert that a target element is visible on the screen."""

    target: str = Field(description="The element to assert visibility of")
    kind: Literal["text", "icon"] = Field(default="text", description="Element type")

    def describe(self) -> str:
        return f"Assert '{self.target}' is visible"


class AssertNotVisibleStep(Step):
    """Assert that a target element is NOT visible on the screen."""

    target: str = Field(description="The element to assert invisibility of")
    kind: Literal["text", "icon"] = Field(default="text", description="Element type")

    def describe(self) -> str:
        return f"Assert '{self.target}' is NOT visible"


class WaitStep(Step):
    """Wait for a condition before proceeding."""

    seconds: Optional[float] = Field(
        default=None, description="Wait for a fixed number of seconds"
    )
    until_visible: Optional[str] = Field(
        default=None, description="Wait until this element becomes visible (with timeout)"
    )
    kind: Literal["text", "icon"] = Field(default="text", description="Element type for until_visible")

    def describe(self) -> str:
        if self.seconds:
            return f"Wait {self.seconds}s"
        elif self.until_visible:
            return f"Wait until '{self.until_visible}' is visible"
        return "Wait"


class ScrollUntilVisibleStep(Step):
    """Scroll until a target element becomes visible."""

    direction: Literal["up", "down", "left", "right"] = Field(
        description="Direction to scroll"
    )
    target: str = Field(description="Element to scroll until visible")
    kind: Literal["text", "icon"] = Field(default="text", description="Element type")
    max_scrolls: int = Field(
        default=5, description="Maximum number of scroll attempts before giving up"
    )

    def describe(self) -> str:
        return f"Scroll {self.direction} until '{self.target}' is visible"


class PressKeyStep(Step):
    """Press a key or key combination."""

    key: str = Field(description="Key name (e.g., 'return', 'backspace', 'home')")

    def describe(self) -> str:
        return f"Press key '{self.key}'"


class CommentStep(Step):
    """A comment or documentation line (not an action)."""

    text: str = Field(description="Comment text")

    def describe(self) -> str:
        return f"# {self.text}"
