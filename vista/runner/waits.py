"""Wait strategies for screen settling and element appearance/disappearance."""

import time
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


class ScreenSettleTimeout(Exception):
    """Raised when screen doesn't settle (stop changing) within timeout."""

    pass


def wait_until(
    condition: Callable[[], bool],
    timeout_seconds: float = 10.0,
    poll_interval_seconds: float = 0.5,
    error_message: str = "Condition not met within timeout",
) -> None:
    """
    Wait until a condition becomes true.

    Args:
        condition: A callable that returns True when the condition is met.
        timeout_seconds: Maximum time to wait.
        poll_interval_seconds: How often to check the condition.
        error_message: Error message if timeout is reached.

    Raises:
        TimeoutError: If the condition is not met within timeout_seconds.
    """
    start_time = time.time()
    while True:
        if condition():
            return
        elapsed = time.time() - start_time
        if elapsed >= timeout_seconds:
            raise TimeoutError(error_message)
        time.sleep(min(poll_interval_seconds, timeout_seconds - elapsed))


def wait_for_value_change(
    get_value: Callable[[], T],
    initial_value: T,
    timeout_seconds: float = 10.0,
    poll_interval_seconds: float = 0.5,
) -> T:
    """
    Wait for a value to change from an initial value.

    Useful for waiting for a screen to change after an action.

    Args:
        get_value: A callable that returns the current value.
        initial_value: The starting value.
        timeout_seconds: Maximum time to wait.
        poll_interval_seconds: How often to check.

    Returns:
        The new value once it changes.

    Raises:
        TimeoutError: If the value doesn't change within timeout_seconds.
    """
    start_time = time.time()
    while True:
        current_value = get_value()
        if current_value != initial_value:
            return current_value
        elapsed = time.time() - start_time
        if elapsed >= timeout_seconds:
            raise TimeoutError(f"Value did not change within {timeout_seconds}s")
        time.sleep(min(poll_interval_seconds, timeout_seconds - elapsed))


def wait_for_stability(
    get_state: Callable[[], bytes],
    stable_threshold_ms: int = 500,
    poll_interval_ms: int = 100,
    timeout_seconds: float = 10.0,
) -> None:
    """
    Wait for a state to become stable (two consecutive checks are identical).

    Useful for waiting for animations to complete.

    Args:
        get_state: A callable that returns the current state (e.g., screenshot bytes).
        stable_threshold_ms: How long the state must remain unchanged to be "stable".
        poll_interval_ms: How often to check the state.
        timeout_seconds: Maximum time to wait before giving up.

    Raises:
        ScreenSettleTimeout: If the state doesn't stabilize within timeout_seconds.
    """
    start_time = time.time()
    last_state = get_state()
    last_change_time = start_time

    while True:
        time.sleep(poll_interval_ms / 1000.0)
        current_state = get_state()

        if current_state != last_state:
            last_state = current_state
            last_change_time = time.time()
        else:
            time_stable = (time.time() - last_change_time) * 1000
            if time_stable >= stable_threshold_ms:
                return

        elapsed = time.time() - start_time
        if elapsed >= timeout_seconds:
            raise ScreenSettleTimeout(
                f"Screen did not stabilize within {timeout_seconds}s"
            )
