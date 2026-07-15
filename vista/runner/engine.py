"""Runner engine — the main capture → perceive → resolve → act → report loop."""

from typing import List

from vista.dsl.steps import Step
from vista.driver.base import Driver
from vista.matcher.base import ElementMatcher
from vista.runner.executor import ActionExecutor, StepResult
from vista.vision.screen import ScreenState


class Runner:
    """
    Orchestrates the execution of a sequence of steps.

    Implements the core loop: for each step, capture the screen, perceive elements,
    resolve targets, execute the action, and record the result.
    """

    def __init__(
        self,
        driver: Driver,
        matcher: ElementMatcher,
        executor: ActionExecutor,
    ):
        """
        Initialize the runner.

        Args:
            driver: The device driver (iOS, Android, etc.).
            matcher: The element matcher for resolving targets.
            executor: The action executor for performing steps.
        """
        self.driver = driver
        self.matcher = matcher
        self.executor = executor
        self.results: List[StepResult] = []

    def run(self, steps: List[Step]) -> List[StepResult]:
        """
        Execute a sequence of steps.

        For each step:
        1. Capture a fresh screenshot
        2. Run perception (OCR, icon detection)
        3. Resolve targets against the current screen
        4. Execute the action
        5. Record the result

        Args:
            steps: The steps to execute.

        Returns:
            A list of StepResult objects, one per step.
        """
        self.results = []
        for step in steps:
            # TODO (Stage 1+): Implement capture → perceive → resolve → act loop
            # For now, this is a stub that will be filled in during Stage 1-3
            pass
        return self.results
