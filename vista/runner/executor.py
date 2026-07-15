"""Action executor — performs individual steps against the driver."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from vista.dsl.steps import Step
from vista.driver.base import Driver
from vista.matcher.base import ElementMatcher
from vista.vision.screen import ScreenState


@dataclass
class StepResult:
    """Result of executing a single step."""

    step: Step
    success: bool
    error_message: Optional[str] = None
    duration_ms: float = 0.0


class ActionExecutor(ABC):
    """
    Abstract base class for executing steps.

    Concrete implementations handle each step type (Tap, Type, Swipe, etc.)
    and use the Driver, Matcher, and ScreenState to perform the action.
    """

    @abstractmethod
    def execute(
        self,
        step: Step,
        driver: Driver,
        screen: ScreenState,
        matcher: ElementMatcher,
    ) -> StepResult:
        """
        Execute a single step against the driver.

        Args:
            step: The step to execute.
            driver: The device driver.
            screen: The current screen state.
            matcher: The element matcher for resolving targets.

        Returns:
            A StepResult indicating success or failure.
        """
        pass
