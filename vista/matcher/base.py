"""Element matcher abstract base class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Optional

from vista.matcher.disambiguation import Disambiguator
from vista.vision.elements import UIElement
from vista.vision.screen import ScreenState


class ElementNotFoundError(Exception):
    """Raised when a target element cannot be found on the screen."""

    pass


class AmbiguousMatchError(Exception):
    """Raised when multiple elements match the target and disambiguation fails."""

    pass


class ElementMatcher(ABC):
    """
    Abstract base class for element matching.

    Resolves instruction targets (e.g., "Login", "back_button") against
    the current ScreenState to find the actual bounding box coordinates.
    """

    @abstractmethod
    def resolve(
        self,
        target: str,
        screen: ScreenState,
        kind: Literal["text", "icon"] = "text",
        disambiguator: Optional[Disambiguator] = None,
    ) -> UIElement:
        """
        Resolve a target to a UI element on the current screen.

        Args:
            target: The target string (e.g., "Login", "back_arrow").
            screen: The current ScreenState with detected elements.
            kind: Whether to search for text or icon elements.
            disambiguator: Optional strategy for resolving multiple matches.

        Returns:
            The matched UIElement with its bounding box.

        Raises:
            ElementNotFoundError: If no matching element is found.
            AmbiguousMatchError: If multiple elements match and cannot be disambiguated.
        """
        pass
