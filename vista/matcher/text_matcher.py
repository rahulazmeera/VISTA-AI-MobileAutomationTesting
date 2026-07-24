"""Text element matcher using fuzzy string matching."""

import logging
from typing import List, Optional

from rapidfuzz import fuzz

from vista.matcher.base import AmbiguousMatchError, ElementMatcher, ElementNotFoundError
from vista.matcher.disambiguation import Disambiguator, HighestConfidenceDisambiguator
from vista.vision.elements import TextElement
from vista.vision.screen import ScreenState

logger = logging.getLogger(__name__)


class TextElementMatcher(ElementMatcher):
    """
    Matches text targets against detected text elements using fuzzy string matching.

    Uses rapidfuzz.fuzz.WRatio for robust matching that handles:
    - Case insensitivity
    - Minor OCR errors
    - Partial matches
    """

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize the text matcher.

        Args:
            similarity_threshold: Minimum similarity score (0.0-1.0) for a match.
                                 Default 0.85 tolerates minor OCR errors.
        """
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError(f"Threshold must be 0.0-1.0, got {similarity_threshold}")

        self.similarity_threshold = similarity_threshold
        logger.info(f"TextElementMatcher initialized (threshold={similarity_threshold})")

    def resolve(
        self,
        target: str,
        screen: ScreenState,
        kind: str = "text",
        disambiguator: Optional[Disambiguator] = None,
    ) -> TextElement:
        """
        Resolve a text target to a TextElement on the current screen.

        Args:
            target: The text to find (e.g., "Login", "Email").
            screen: The current ScreenState with detected elements.
            kind: Must be "text" (icon matching is separate).
            disambiguator: Optional strategy for resolving multiple matches.

        Returns:
            The matched TextElement with its bounding box.

        Raises:
            ElementNotFoundError: If no matching text is found.
            AmbiguousMatchError: If multiple matches exist and cannot be disambiguated.
        """
        if kind != "text":
            raise ValueError(f"TextElementMatcher only handles 'text' kind, got '{kind}'")

        logger.debug(f"Resolving text target: '{target}'")

        # Filter to text elements and score each one
        candidates_with_scores = []

        normalized_target = self._normalize(target)

        for elem in screen.text_elements:
            # Normalize both strings for comparison
            normalized_elem_text = self._normalize(elem.text)

            # WRatio blends in partial-ratio scoring, which gives a short
            # substring an artificially high score against a much longer
            # string (e.g. a lone "r" scores ~100 against "shared" because
            # "r" is fully contained in it). That falsely matches stray OCR
            # fragments — like a single on-screen keyboard letter — against
            # real UI labels. Reject candidates too short to plausibly be
            # the same label as the target.
            if len(normalized_elem_text) < len(normalized_target) / 2:
                continue

            # Use weighted ratio for fuzzy matching
            score = fuzz.WRatio(normalized_target, normalized_elem_text) / 100.0

            if score >= self.similarity_threshold:
                candidates_with_scores.append((elem, score))
                logger.debug(
                    f"  Candidate: '{elem.text}' (score: {score:.2f}, "
                    f"confidence: {elem.confidence:.2f})"
                )

        if not candidates_with_scores:
            logger.warning(
                f"No match found for '{target}' "
                f"(threshold: {self.similarity_threshold}, "
                f"scanned {len(screen.text_elements)} elements)"
            )
            raise ElementNotFoundError(
                f"No text matching '{target}' found on screen "
                f"(tried {len(screen.text_elements)} elements, threshold={self.similarity_threshold})"
            )

        # Sort by score (descending), then by confidence (descending)
        candidates_with_scores.sort(
            key=lambda x: (x[1], x[0].confidence), reverse=True
        )
        candidates = [elem for elem, _ in candidates_with_scores]

        # If single match, return it
        if len(candidates) == 1:
            logger.info(
                f"Resolved '{target}' to '{candidates[0].text}' "
                f"@ ({candidates[0].bbox.x}, {candidates[0].bbox.y})"
            )
            return candidates[0]

        # Multiple matches — use disambiguator if provided, otherwise use highest score
        if disambiguator is None:
            disambiguator = HighestConfidenceDisambiguator()

        try:
            chosen = disambiguator.choose(candidates)
            logger.info(
                f"Resolved '{target}' to '{chosen.text}' "
                f"(from {len(candidates)} candidates) "
                f"@ ({chosen.bbox.x}, {chosen.bbox.y})"
            )
            return chosen
        except ValueError as e:
            raise AmbiguousMatchError(
                f"Multiple matches for '{target}': {[e.text for e in candidates]}, "
                f"and disambiguation failed: {e}"
            ) from e

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize text for fuzzy matching.

        Removes extra whitespace, converts to lowercase, removes punctuation edge cases.

        Args:
            text: Text to normalize.

        Returns:
            Normalized text.
        """
        # Strip whitespace and lowercase
        normalized = text.strip().lower()
        # Collapse multiple spaces
        normalized = " ".join(normalized.split())
        return normalized
