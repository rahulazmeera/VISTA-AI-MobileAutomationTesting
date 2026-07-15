"""Icon element matcher using template matching."""

import logging
from typing import List, Optional

from vista.matcher.base import AmbiguousMatchError, ElementMatcher, ElementNotFoundError
from vista.matcher.disambiguation import Disambiguator, HighestConfidenceDisambiguator
from vista.vision.elements import IconElement
from vista.vision.screen import ScreenState

logger = logging.getLogger(__name__)


class IconElementMatcher(ElementMatcher):
    """
    Matches icon targets against detected icon elements.

    Uses icon ID matching (exact string comparison).
    """

    def __init__(self):
        """Initialize the icon matcher."""
        logger.info("IconElementMatcher initialized")

    def resolve(
        self,
        target: str,
        screen: ScreenState,
        kind: str = "icon",
        disambiguator: Optional[Disambiguator] = None,
    ) -> IconElement:
        """
        Resolve an icon target to an IconElement on the current screen.

        Args:
            target: The icon ID to find (e.g., "back_arrow", "menu_icon").
            screen: The current ScreenState with detected elements.
            kind: Must be "icon" (text matching is separate).
            disambiguator: Optional strategy for resolving multiple matches.

        Returns:
            The matched IconElement with its bounding box.

        Raises:
            ElementNotFoundError: If no matching icon is found.
            AmbiguousMatchError: If multiple matches exist and cannot be disambiguated.
        """
        if kind != "icon":
            raise ValueError(f"IconElementMatcher only handles 'icon' kind, got '{kind}'")

        logger.debug(f"Resolving icon target: '{target}'")

        # Find all icons matching the target ID
        candidates = []

        for elem in screen.icon_elements:
            if elem.icon_id.lower() == target.lower():
                candidates.append(elem)
                logger.debug(
                    f"  Candidate: icon '{elem.icon_id}' "
                    f"(confidence: {elem.confidence:.2f})"
                )

        if not candidates:
            logger.warning(
                f"No icon matching '{target}' found on screen "
                f"(scanned {len(screen.icon_elements)} icons)"
            )
            raise ElementNotFoundError(
                f"No icon matching '{target}' found on screen "
                f"(tried {len(screen.icon_elements)} icons)"
            )

        # If single match, return it
        if len(candidates) == 1:
            logger.info(
                f"Resolved icon '{target}' "
                f"@ ({candidates[0].bbox.x}, {candidates[0].bbox.y})"
            )
            return candidates[0]

        # Multiple matches — use disambiguator if provided, otherwise use highest confidence
        if disambiguator is None:
            disambiguator = HighestConfidenceDisambiguator()

        try:
            # Sort by confidence first
            candidates.sort(key=lambda e: e.confidence, reverse=True)
            chosen = disambiguator.choose(candidates)
            logger.info(
                f"Resolved icon '{target}' "
                f"(from {len(candidates)} candidates) "
                f"@ ({chosen.bbox.x}, {chosen.bbox.y})"
            )
            return chosen
        except ValueError as e:
            raise AmbiguousMatchError(
                f"Multiple matches for icon '{target}': "
                f"{[e.icon_id for e in candidates]}, "
                f"and disambiguation failed: {e}"
            ) from e
