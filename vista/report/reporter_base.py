"""Reporter abstract base class."""

from abc import ABC, abstractmethod

from vista.report.models import RunResult


class Reporter(ABC):
    """
    Abstract base class for reporters.

    Pluggable implementations (HTML, JSON, JUnit XML) can be swapped
    via the provider registry in config.py.
    """

    @abstractmethod
    def report(self, result: RunResult, output_path: str) -> None:
        """
        Generate a report for a test run.

        Args:
            result: The complete run result.
            output_path: Path where the report should be written.
        """
        pass
