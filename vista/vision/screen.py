"""ScreenState — the core data contract between perception, matching, and future AI planning."""

from dataclasses import dataclass
from typing import List, Union

from PIL.Image import Image

from vista.vision.elements import IconElement, TextElement


@dataclass
class ScreenState:
    """
    The current state of the screen as perceived by the vision engine.

    Captures a screenshot and all detected elements (text and icons).
    This is the stable data contract that:
    - The perception pipeline (OCR, icon detection) produces
    - The matcher consumes to resolve instruction targets
    - A future AI planner (Stage 9+) can reason over

    All bounding boxes are stored in raw screenshot pixel space.
    Conversion to device points only happens at the final driver.tap() call.
    """

    screenshot: Image
    text_elements: List[TextElement]
    icon_elements: List[IconElement]
    timestamp: float  # Unix timestamp when this screen was captured

    @property
    def all_elements(self) -> List[Union[TextElement, IconElement]]:
        """All detected elements."""
        return self.text_elements + self.icon_elements

    def to_dict(self) -> dict:
        """Serialize to a dictionary (useful for logging, golden test fixtures)."""
        return {
            "text_elements": [
                {
                    "text": elem.text,
                    "bbox": {
                        "x": elem.bbox.x,
                        "y": elem.bbox.y,
                        "width": elem.bbox.width,
                        "height": elem.bbox.height,
                    },
                    "confidence": elem.confidence,
                }
                for elem in self.text_elements
            ],
            "icon_elements": [
                {
                    "icon_id": elem.icon_id,
                    "bbox": {
                        "x": elem.bbox.x,
                        "y": elem.bbox.y,
                        "width": elem.bbox.width,
                        "height": elem.bbox.height,
                    },
                    "confidence": elem.confidence,
                }
                for elem in self.icon_elements
            ],
            "screenshot_size": self.screenshot.size,
        }
