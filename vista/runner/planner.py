"""Instruction planner — Stage 9+ hook for AI-generated steps.

This interface allows future LLM/VLM-based planning without rewriting the core engine.
The planner produces the same Step objects as YAML parsing, maintaining symmetry.
"""

from abc import ABC, abstractmethod
from typing import List

from vista.dsl.steps import Step
from vista.vision.screen import ScreenState


class InstructionPlanner(ABC):
    """
    Abstract base class for instruction planners.

    Converts a natural-language goal into a sequence of steps.
    This is the extension point for Stage 9+ (AI-based automation).

    Example implementations:
    - LLM-based planner: uses Claude/GPT vision to reason over the screenshot
    - VLM-based planner: uses a visual grounding model to localize targets
    """

    @abstractmethod
    def plan(self, goal: str, screen: ScreenState) -> List[Step]:
        """
        Plan a sequence of steps to achieve a goal.

        Args:
            goal: A natural-language description of the desired action(s).
                  E.g., "Log in with user@example.com and password secret123"
            screen: The current screen state with detected elements.

        Returns:
            A list of Step objects that, when executed, should achieve the goal.

        Notes:
            The returned steps must be the same Step subclasses as YAML parsing produces
            (TapStep, TypeStep, etc.), ensuring compatibility with the executor and engine.
        """
        pass
