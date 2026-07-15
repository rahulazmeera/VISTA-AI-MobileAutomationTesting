"""Driver ABC — the only place where device control happens (screenshot + raw coordinate actions)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

from PIL.Image import Image


@dataclass(frozen=True)
class Point:
    """A point in coordinate space."""

    x: int
    y: int


class Driver(ABC):
    """
    Abstract base class for device drivers.

    This is the ONLY interface that communicates with the actual device/simulator.
    All implementations MUST:
    - Use ONLY screenshot capture and raw coordinate-based actions (tap, type, swipe)
    - NEVER use accessibility-tree lookups (find_element, find_by_id, etc.)
    - Return coordinates and sizes in their native coordinate system (points for iOS, dp for Android)

    This boundary is critical to VISTA's design. Any use of accessibility locators
    elsewhere in the codebase defeats the purpose of vision-based automation.
    See CONTRIBUTING.md for details.
    """

    @abstractmethod
    def screenshot(self) -> Image:
        """
        Capture the current screen as an image.

        Returns:
            A PIL Image of the current screen in raw pixel dimensions (Retina etc.)
            Color mode should be RGB or RGBA.
        """
        pass

    @abstractmethod
    def tap(self, x: int, y: int) -> None:
        """
        Tap a single point on the screen.

        Args:
            x: X coordinate in points (not pixels).
            y: Y coordinate in points (not pixels).
        """
        pass

    @abstractmethod
    def type_text(self, text: str) -> None:
        """
        Type text into the currently-focused field.

        Assumes the field is already focused (via a prior tap).
        Disables autocorrect/predictive text where possible.

        Args:
            text: The text to type.
        """
        pass

    @abstractmethod
    def swipe(
        self, start: Point, end: Point, duration_ms: int = 300
    ) -> None:
        """
        Perform a swipe gesture from one point to another.

        Args:
            start: Starting point in points.
            end: Ending point in points.
            duration_ms: Duration of the swipe in milliseconds.
        """
        pass

    @abstractmethod
    def press_key(self, key: str) -> None:
        """
        Press a key or key combination.

        Args:
            key: Key name (e.g., 'return', 'backspace', 'home', 'escape').
        """
        pass

    @abstractmethod
    def screen_size(self) -> Tuple[int, int]:
        """
        Get the screen size in points (not pixels).

        Returns:
            A tuple of (width, height) in points.
        """
        pass

    @abstractmethod
    def scale_factor(self) -> float:
        """
        Get the pixel-to-point scale factor for this device.

        Returns:
            Scale factor (e.g., 2.0 for Retina, 1.0 for non-Retina).
            Used internally to convert screenshot pixels to coordinate points.
        """
        pass
