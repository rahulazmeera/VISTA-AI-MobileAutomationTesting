"""UI element data models."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BBox:
    """A bounding box in pixel coordinates (as found in the screenshot)."""

    x: int
    y: int
    width: int
    height: int

    @property
    def center_x(self) -> float:
        """Center X coordinate."""
        return self.x + self.width / 2.0

    @property
    def center_y(self) -> float:
        """Center Y coordinate."""
        return self.y + self.height / 2.0

    @property
    def x2(self) -> int:
        """Right edge X coordinate."""
        return self.x + self.width

    @property
    def y2(self) -> int:
        """Bottom edge Y coordinate."""
        return self.y + self.height

    def area(self) -> int:
        """Bounding box area in pixels."""
        return self.width * self.height

    def distance_to(self, other: "BBox") -> float:
        """Euclidean distance between the centers of two bboxes."""
        return (
            (self.center_x - other.center_x) ** 2
            + (self.center_y - other.center_y) ** 2
        ) ** 0.5


@dataclass(frozen=True)
class UIElement:
    """Base class for a detected UI element."""

    bbox: BBox
    confidence: float


@dataclass(frozen=True)
class TextElement(UIElement):
    """A detected text element."""

    text: str


@dataclass(frozen=True)
class IconElement(UIElement):
    """A detected icon/non-text UI element."""

    icon_id: str  # e.g., "back_button", "menu_icon"
