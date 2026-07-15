"""Configuration and provider registry.

Manages which concrete implementations (drivers, OCR providers, etc.) are used.
Designed to support pluggable providers via entry-points (Stage 7+) and out-of-tree extensions.
"""

from typing import Dict, Optional, Type

from vista.driver.base import Driver
from vista.matcher.base import ElementMatcher
from vista.report.reporter_base import Reporter
from vista.runner.executor import ActionExecutor
from vista.runner.planner import InstructionPlanner
from vista.vision.icons.base import IconDetector
from vista.vision.ocr.base import OCRProvider


class ProviderRegistry:
    """
    Registry for pluggable providers.

    Holds the concrete implementations to use for:
    - OCR providers
    - Icon detectors
    - Element matchers
    - Action executors
    - Reporters
    - Instruction planners (Stage 9+)
    """

    def __init__(self):
        self._ocr_providers: Dict[str, Type[OCRProvider]] = {}
        self._icon_detectors: Dict[str, Type[IconDetector]] = {}
        self._matchers: Dict[str, Type[ElementMatcher]] = {}
        self._executors: Dict[str, Type[ActionExecutor]] = {}
        self._reporters: Dict[str, Type[Reporter]] = {}
        self._planners: Dict[str, Type[InstructionPlanner]] = {}

        # Current selections
        self._current_ocr_provider: Optional[str] = None
        self._current_icon_detector: Optional[str] = None
        self._current_matcher: Optional[str] = None
        self._current_executor: Optional[str] = None
        self._current_reporter: Optional[str] = None
        self._current_planner: Optional[str] = None

    # OCR Provider Registration
    def register_ocr_provider(self, name: str, provider_class: Type[OCRProvider]) -> None:
        """Register an OCR provider."""
        self._ocr_providers[name] = provider_class

    def get_ocr_provider(self, name: str) -> Type[OCRProvider]:
        """Get a registered OCR provider by name."""
        if name not in self._ocr_providers:
            raise ValueError(f"OCR provider '{name}' not registered")
        return self._ocr_providers[name]

    def set_ocr_provider(self, name: str) -> None:
        """Set the current OCR provider."""
        if name not in self._ocr_providers:
            raise ValueError(f"OCR provider '{name}' not registered")
        self._current_ocr_provider = name

    def current_ocr_provider(self) -> Optional[Type[OCRProvider]]:
        """Get the currently selected OCR provider."""
        if self._current_ocr_provider is None:
            return None
        return self._ocr_providers.get(self._current_ocr_provider)

    # Icon Detector Registration
    def register_icon_detector(self, name: str, detector_class: Type[IconDetector]) -> None:
        """Register an icon detector."""
        self._icon_detectors[name] = detector_class

    def get_icon_detector(self, name: str) -> Type[IconDetector]:
        """Get a registered icon detector by name."""
        if name not in self._icon_detectors:
            raise ValueError(f"Icon detector '{name}' not registered")
        return self._icon_detectors[name]

    def set_icon_detector(self, name: str) -> None:
        """Set the current icon detector."""
        if name not in self._icon_detectors:
            raise ValueError(f"Icon detector '{name}' not registered")
        self._current_icon_detector = name

    def current_icon_detector(self) -> Optional[Type[IconDetector]]:
        """Get the currently selected icon detector."""
        if self._current_icon_detector is None:
            return None
        return self._icon_detectors.get(self._current_icon_detector)

    # Element Matcher Registration
    def register_matcher(self, name: str, matcher_class: Type[ElementMatcher]) -> None:
        """Register a matcher."""
        self._matchers[name] = matcher_class

    def get_matcher(self, name: str) -> Type[ElementMatcher]:
        """Get a registered matcher by name."""
        if name not in self._matchers:
            raise ValueError(f"Matcher '{name}' not registered")
        return self._matchers[name]

    def set_matcher(self, name: str) -> None:
        """Set the current matcher."""
        if name not in self._matchers:
            raise ValueError(f"Matcher '{name}' not registered")
        self._current_matcher = name

    def current_matcher(self) -> Optional[Type[ElementMatcher]]:
        """Get the currently selected matcher."""
        if self._current_matcher is None:
            return None
        return self._matchers.get(self._current_matcher)

    # Action Executor Registration
    def register_executor(self, name: str, executor_class: Type[ActionExecutor]) -> None:
        """Register an action executor."""
        self._executors[name] = executor_class

    def get_executor(self, name: str) -> Type[ActionExecutor]:
        """Get a registered executor by name."""
        if name not in self._executors:
            raise ValueError(f"Executor '{name}' not registered")
        return self._executors[name]

    def set_executor(self, name: str) -> None:
        """Set the current executor."""
        if name not in self._executors:
            raise ValueError(f"Executor '{name}' not registered")
        self._current_executor = name

    def current_executor(self) -> Optional[Type[ActionExecutor]]:
        """Get the currently selected executor."""
        if self._current_executor is None:
            return None
        return self._executors.get(self._current_executor)

    # Reporter Registration
    def register_reporter(self, name: str, reporter_class: Type[Reporter]) -> None:
        """Register a reporter."""
        self._reporters[name] = reporter_class

    def get_reporter(self, name: str) -> Type[Reporter]:
        """Get a registered reporter by name."""
        if name not in self._reporters:
            raise ValueError(f"Reporter '{name}' not registered")
        return self._reporters[name]

    def set_reporter(self, name: str) -> None:
        """Set the current reporter."""
        if name not in self._reporters:
            raise ValueError(f"Reporter '{name}' not registered")
        self._current_reporter = name

    def current_reporter(self) -> Optional[Type[Reporter]]:
        """Get the currently selected reporter."""
        if self._current_reporter is None:
            return None
        return self._reporters.get(self._current_reporter)

    # Instruction Planner Registration (Stage 9+)
    def register_planner(self, name: str, planner_class: Type[InstructionPlanner]) -> None:
        """Register an instruction planner."""
        self._planners[name] = planner_class

    def get_planner(self, name: str) -> Type[InstructionPlanner]:
        """Get a registered planner by name."""
        if name not in self._planners:
            raise ValueError(f"Planner '{name}' not registered")
        return self._planners[name]

    def set_planner(self, name: str) -> None:
        """Set the current planner."""
        if name not in self._planners:
            raise ValueError(f"Planner '{name}' not registered")
        self._current_planner = name

    def current_planner(self) -> Optional[Type[InstructionPlanner]]:
        """Get the currently selected planner."""
        if self._current_planner is None:
            return None
        return self._planners.get(self._current_planner)


# Global registry instance
_default_registry = ProviderRegistry()


def get_registry() -> ProviderRegistry:
    """Get the global provider registry."""
    return _default_registry
