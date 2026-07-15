"""Action executors for individual step types."""

import logging
import time
from typing import Dict, Type

from vista.dsl.steps import (
    AssertNotVisibleStep,
    AssertVisibleStep,
    PressKeyStep,
    Step,
    SwipeStep,
    TapIconStep,
    TapStep,
    TypeStep,
    WaitStep,
)
from vista.driver.base import Driver, Point
from vista.matcher.base import ElementMatcher, ElementNotFoundError
from vista.report.models import StepResult
from vista.runner.executor import ActionExecutor
from vista.runner.waits import wait_until
from vista.vision.screen import ScreenState

logger = logging.getLogger(__name__)


class TapStepExecutor(ActionExecutor):
    """Execute a TapStep."""

    def execute(
        self,
        step: TapStep,
        driver: Driver,
        screen: ScreenState,
        matcher: ElementMatcher,
    ) -> StepResult:
        """Execute a tap action."""
        start_time = time.time()

        try:
            # Resolve target to element
            element = matcher.resolve(step.target, screen, kind="text")

            # Tap at center of element (convert pixel to points)
            x_pt = int(element.bbox.center_x / driver.scale_factor())
            y_pt = int(element.bbox.center_y / driver.scale_factor())

            logger.info(f"Tapping '{step.target}' at ({x_pt}, {y_pt})")
            driver.tap(x_pt, y_pt)

            duration_ms = (time.time() - start_time) * 1000
            return StepResult(
                step=step,
                success=True,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Tap failed: {e}")
            return StepResult(
                step=step,
                success=False,
                duration_ms=duration_ms,
                error_message=str(e),
            )


class TapIconStepExecutor(ActionExecutor):
    """Execute a TapIconStep."""

    def execute(
        self,
        step: TapIconStep,
        driver: Driver,
        screen: ScreenState,
        matcher: ElementMatcher,
    ) -> StepResult:
        """Execute a tap icon action."""
        start_time = time.time()

        try:
            # Resolve icon target to element (need icon matcher)
            # For now, look for the icon in screen.icon_elements directly
            icon_elem = None
            for elem in screen.icon_elements:
                if elem.icon_id.lower() == step.icon.lower():
                    icon_elem = elem
                    break

            if icon_elem is None:
                raise ElementNotFoundError(
                    f"Icon '{step.icon}' not found on screen"
                )

            # Tap at center of icon (convert pixel to points)
            x_pt = int(icon_elem.bbox.center_x / driver.scale_factor())
            y_pt = int(icon_elem.bbox.center_y / driver.scale_factor())

            logger.info(f"Tapping icon '{step.icon}' at ({x_pt}, {y_pt})")
            driver.tap(x_pt, y_pt)

            duration_ms = (time.time() - start_time) * 1000
            return StepResult(
                step=step,
                success=True,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Tap icon failed: {e}")
            return StepResult(
                step=step,
                success=False,
                duration_ms=duration_ms,
                error_message=str(e),
            )


class TypeStepExecutor(ActionExecutor):
    """Execute a TypeStep."""

    def execute(
        self,
        step: TypeStep,
        driver: Driver,
        screen: ScreenState,
        matcher: ElementMatcher,
    ) -> StepResult:
        """Execute a type action."""
        start_time = time.time()

        try:
            # Resolve the field to tap into
            field = matcher.resolve(step.into, screen, kind="text")

            # Tap into the field first
            x_pt = int(field.bbox.center_x / driver.scale_factor())
            y_pt = int(field.bbox.center_y / driver.scale_factor())

            logger.info(f"Tapping field '{step.into}' at ({x_pt}, {y_pt})")
            driver.tap(x_pt, y_pt)

            # Small delay for field to focus
            time.sleep(0.2)

            # Type the text
            logger.info(f"Typing: '{step.text}'")
            driver.type_text(step.text)

            duration_ms = (time.time() - start_time) * 1000
            return StepResult(
                step=step,
                success=True,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Type failed: {e}")
            return StepResult(
                step=step,
                success=False,
                duration_ms=duration_ms,
                error_message=str(e),
            )


class SwipeStepExecutor(ActionExecutor):
    """Execute a SwipeStep."""

    def execute(
        self,
        step: SwipeStep,
        driver: Driver,
        screen: ScreenState,
        matcher: ElementMatcher,
    ) -> StepResult:
        """Execute a swipe action."""
        start_time = time.time()

        try:
            w_pt, h_pt = driver.screen_size()

            # Calculate start and end based on direction
            if step.direction == "up":
                start = Point(x=w_pt // 2, y=int(h_pt * (1 - step.amount)))
                end = Point(x=w_pt // 2, y=int(h_pt * step.amount))
            elif step.direction == "down":
                start = Point(x=w_pt // 2, y=int(h_pt * step.amount))
                end = Point(x=w_pt // 2, y=int(h_pt * (1 - step.amount)))
            elif step.direction == "left":
                start = Point(x=int(w_pt * (1 - step.amount)), y=h_pt // 2)
                end = Point(x=int(w_pt * step.amount), y=h_pt // 2)
            elif step.direction == "right":
                start = Point(x=int(w_pt * step.amount), y=h_pt // 2)
                end = Point(x=int(w_pt * (1 - step.amount)), y=h_pt // 2)
            else:
                raise ValueError(f"Invalid swipe direction: {step.direction}")

            logger.info(f"Swiping {step.direction} ({step.amount * 100}% of screen)")
            driver.swipe(start, end, duration_ms=300)

            duration_ms = (time.time() - start_time) * 1000
            return StepResult(
                step=step,
                success=True,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Swipe failed: {e}")
            return StepResult(
                step=step,
                success=False,
                duration_ms=duration_ms,
                error_message=str(e),
            )


class WaitStepExecutor(ActionExecutor):
    """Execute a WaitStep."""

    def execute(
        self,
        step: WaitStep,
        driver: Driver,
        screen: ScreenState,
        matcher: ElementMatcher,
    ) -> StepResult:
        """Execute a wait action."""
        start_time = time.time()

        try:
            if step.seconds is not None:
                logger.info(f"Waiting {step.seconds}s")
                time.sleep(step.seconds)

            elif step.until_visible is not None:
                logger.info(f"Waiting until '{step.until_visible}' is visible")

                def condition():
                    try:
                        matcher.resolve(step.until_visible, screen, kind=step.kind)
                        return True
                    except Exception:
                        return False

                wait_until(condition, timeout_seconds=10.0)

            duration_ms = (time.time() - start_time) * 1000
            return StepResult(
                step=step,
                success=True,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Wait failed: {e}")
            return StepResult(
                step=step,
                success=False,
                duration_ms=duration_ms,
                error_message=str(e),
            )


class AssertVisibleStepExecutor(ActionExecutor):
    """Execute an AssertVisibleStep."""

    def execute(
        self,
        step: AssertVisibleStep,
        driver: Driver,
        screen: ScreenState,
        matcher: ElementMatcher,
    ) -> StepResult:
        """Execute an assert visible action."""
        start_time = time.time()

        try:
            logger.info(f"Asserting '{step.target}' is visible")
            matcher.resolve(step.target, screen, kind=step.kind)

            duration_ms = (time.time() - start_time) * 1000
            return StepResult(
                step=step,
                success=True,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Assertion failed: {e}")
            return StepResult(
                step=step,
                success=False,
                duration_ms=duration_ms,
                error_message=str(e),
            )


class AssertNotVisibleStepExecutor(ActionExecutor):
    """Execute an AssertNotVisibleStep."""

    def execute(
        self,
        step: AssertNotVisibleStep,
        driver: Driver,
        screen: ScreenState,
        matcher: ElementMatcher,
    ) -> StepResult:
        """Execute an assert not visible action."""
        start_time = time.time()

        try:
            logger.info(f"Asserting '{step.target}' is NOT visible")
            try:
                matcher.resolve(step.target, screen, kind=step.kind)
                # If we get here, element was found (should not be)
                raise AssertionError(f"Element '{step.target}' should not be visible but was found")
            except Exception as e:
                if "should not be visible" in str(e):
                    raise
                # Element not found is success for this assertion
                pass

            duration_ms = (time.time() - start_time) * 1000
            return StepResult(
                step=step,
                success=True,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Assertion failed: {e}")
            return StepResult(
                step=step,
                success=False,
                duration_ms=duration_ms,
                error_message=str(e),
            )


class PressKeyStepExecutor(ActionExecutor):
    """Execute a PressKeyStep."""

    def execute(
        self,
        step: PressKeyStep,
        driver: Driver,
        screen: ScreenState,
        matcher: ElementMatcher,
    ) -> StepResult:
        """Execute a key press action."""
        start_time = time.time()

        try:
            logger.info(f"Pressing key: {step.key}")
            driver.press_key(step.key)

            duration_ms = (time.time() - start_time) * 1000
            return StepResult(
                step=step,
                success=True,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Press key failed: {e}")
            return StepResult(
                step=step,
                success=False,
                duration_ms=duration_ms,
                error_message=str(e),
            )


# Registry of step executors
EXECUTORS: Dict[Type[Step], Type[ActionExecutor]] = {
    TapStep: TapStepExecutor,
    TapIconStep: TapIconStepExecutor,
    TypeStep: TypeStepExecutor,
    SwipeStep: SwipeStepExecutor,
    WaitStep: WaitStepExecutor,
    AssertVisibleStep: AssertVisibleStepExecutor,
    AssertNotVisibleStep: AssertNotVisibleStepExecutor,
    PressKeyStep: PressKeyStepExecutor,
}


def get_executor_for_step(step: Step) -> ActionExecutor:
    """Get the appropriate executor for a step."""
    executor_class = EXECUTORS.get(type(step))
    if executor_class is None:
        raise NotImplementedError(f"No executor for step type: {type(step).__name__}")
    return executor_class()
