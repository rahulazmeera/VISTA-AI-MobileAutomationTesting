"""Report data models."""

from dataclasses import dataclass, field
from typing import List, Optional

from vista.dsl.steps import Step


@dataclass
class StepResult:
    """Result of executing a single step."""

    step: Step
    success: bool
    duration_ms: float = 0.0
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None  # Path to the screenshot after this step


@dataclass
class RunResult:
    """Result of running a complete test script."""

    script_path: str
    total_steps: int
    passed_steps: int
    failed_steps: int
    skipped_steps: int
    total_duration_seconds: float
    step_results: List[StepResult] = field(default_factory=list)
    error_log: Optional[str] = None

    @property
    def success(self) -> bool:
        """Whether all steps passed."""
        return self.failed_steps == 0

    @property
    def pass_rate(self) -> float:
        """Percentage of steps that passed."""
        if self.total_steps == 0:
            return 0.0
        return (self.passed_steps / self.total_steps) * 100.0
