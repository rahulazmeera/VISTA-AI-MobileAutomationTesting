"""Disambiguation strategies for resolving multiple element matches."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from vista.vision.elements import UIElement


class Disambiguator(ABC):
    """Base class for strategies that disambiguate multiple element matches."""

    @abstractmethod
    def choose(self, candidates: List[UIElement]) -> UIElement:
        """
        Choose a single element from multiple candidates.

        Args:
            candidates: List of matching elements.

        Returns:
            The chosen element.

        Raises:
            ValueError: If the strategy cannot choose (e.g., no candidates after filtering).
        """
        pass


class OccurrenceDisambiguator(Disambiguator):
    """Choose the Nth occurrence (1-indexed)."""

    def __init__(self, occurrence: int):
        if occurrence < 1:
            raise ValueError("Occurrence must be 1-indexed (>= 1)")
        self.occurrence = occurrence

    def choose(self, candidates: List[UIElement]) -> UIElement:
        if self.occurrence > len(candidates):
            raise ValueError(
                f"Requested occurrence {self.occurrence} but only {len(candidates)} candidates found"
            )
        return candidates[self.occurrence - 1]


class NearestToDisambiguator(Disambiguator):
    """Choose the candidate nearest to a reference element."""

    def __init__(self, reference: UIElement):
        self.reference = reference

    def choose(self, candidates: List[UIElement]) -> UIElement:
        if not candidates:
            raise ValueError("No candidates to choose from")
        return min(
            candidates,
            key=lambda elem: elem.bbox.distance_to(self.reference.bbox),
        )


class TopLeftDisambiguator(Disambiguator):
    """Choose the element closest to the top-left corner of the screen."""

    def choose(self, candidates: List[UIElement]) -> UIElement:
        if not candidates:
            raise ValueError("No candidates to choose from")
        return min(candidates, key=lambda elem: (elem.bbox.x, elem.bbox.y))


class LargestDisambiguator(Disambiguator):
    """Choose the largest (by area) element."""

    def choose(self, candidates: List[UIElement]) -> UIElement:
        if not candidates:
            raise ValueError("No candidates to choose from")
        return max(candidates, key=lambda elem: elem.bbox.area())


class HighestConfidenceDisambiguator(Disambiguator):
    """Choose the element with the highest confidence score."""

    def choose(self, candidates: List[UIElement]) -> UIElement:
        if not candidates:
            raise ValueError("No candidates to choose from")
        return max(candidates, key=lambda elem: elem.confidence)
