"""Runner engine — the main capture → perceive → resolve → act → report loop."""

import logging
import time
from typing import List, Optional

from vista.dsl.steps import CommentStep, Step
from vista.driver.base import Driver
from vista.matcher.base import ElementMatcher
from vista.report.models import RunResult, StepResult
from vista.runner.actions import get_executor_for_step
from vista.vision.icons.base import IconDetector
from vista.vision.ocr.base import OCRProvider
from vista.vision.screen import ScreenState

logger = logging.getLogger(__name__)


class Runner:
    """
    Orchestrates the execution of a sequence of steps.

    Implements the core loop: for each step:
    1. Capture a fresh screenshot
    2. Run perception (OCR, icon detection)
    3. Resolve targets against the current screen
    4. Execute the action
    5. Record the result
    """

    def __init__(
        self,
        driver: Driver,
        matcher: ElementMatcher,
        ocr_provider: OCRProvider,
        icon_detector: Optional[IconDetector] = None,
    ):
        """
        Initialize the runner.

        Args:
            driver: The device driver (iOS, Android, etc.).
            matcher: The element matcher for resolving targets.
            ocr_provider: The OCR provider for text detection.
            icon_detector: Optional icon detector for non-text UI elements.
        """
        self.driver = driver
        self.matcher = matcher
        self.ocr_provider = ocr_provider
        self.icon_detector = icon_detector
        self.results: List[StepResult] = []

    def run(self, steps: List[Step], script_path: str = "unknown") -> RunResult:
        """
        Execute a sequence of steps.

        Args:
            steps: The steps to execute.
            script_path: Path to the test script (for reporting).

        Returns:
            A RunResult with all step results and summary statistics.
        """
        logger.info(f"Running {len(steps)} steps")
        self.results = []

        total_duration = time.time()

        for i, step in enumerate(steps, 1):
            # Skip comment steps
            if isinstance(step, CommentStep):
                logger.info(f"[{i}/{len(steps)}] {step.describe()}")
                continue

            logger.info(f"[{i}/{len(steps)}] {step.describe()}")

            try:
                # Step 1: Capture screenshot
                screenshot = self.driver.screenshot()
                logger.debug(f"Screenshot: {screenshot.size}")

                # Step 2: Perceive elements (OCR + icon detection)
                text_elements = self.ocr_provider.detect_text(screenshot)
                logger.debug(f"Perceived {len(text_elements)} text elements")

                # Detect icons if icon detector is available
                icon_elements = []
                if self.icon_detector is not None:
                    icon_elements = self.icon_detector.detect_icons(screenshot)
                    logger.debug(f"Perceived {len(icon_elements)} icon elements")

                # Step 3 & 4: Build ScreenState, resolve targets, execute
                screen = ScreenState(
                    screenshot=screenshot,
                    text_elements=text_elements,
                    icon_elements=icon_elements,
                    timestamp=time.time(),
                )

                # Get appropriate executor for this step type
                executor = get_executor_for_step(step)

                # Execute the step
                result = executor.execute(step, self.driver, screen, self.matcher)

                # Step 5: Record result
                self.results.append(result)

                if result.success:
                    logger.info(f"✓ Step succeeded ({result.duration_ms:.0f}ms)")
                else:
                    logger.error(f"✗ Step failed: {result.error_message}")

            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                result = StepResult(
                    step=step,
                    success=False,
                    error_message=str(e),
                    duration_ms=(time.time() - total_duration) * 1000,
                )
                self.results.append(result)

        total_duration_seconds = time.time() - total_duration

        # Build summary
        passed = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        skipped = len(steps) - len(self.results)

        run_result = RunResult(
            script_path=script_path,
            total_steps=len(steps),
            passed_steps=passed,
            failed_steps=failed,
            skipped_steps=skipped,
            total_duration_seconds=total_duration_seconds,
            step_results=self.results,
        )

        logger.info(
            f"\n{'='*60}\n"
            f"Test Summary\n"
            f"{'='*60}\n"
            f"Total:   {len(steps)} steps\n"
            f"Passed:  {passed} ✓\n"
            f"Failed:  {failed} ✗\n"
            f"Skipped: {skipped}\n"
            f"Duration: {total_duration_seconds:.1f}s\n"
            f"{'='*60}"
        )

        return run_result
