"""JUnit XML reporter for CI/CD integration."""

import logging
from pathlib import Path
from xml.etree import ElementTree as ET

from vista.report.models import RunResult
from vista.report.reporter_base import Reporter

logger = logging.getLogger(__name__)


class JUnitReporter(Reporter):
    """Generate JUnit XML reports for CI/CD systems."""

    def report(self, result: RunResult, output_path: str) -> None:
        """
        Generate a JUnit XML report for a test run.

        Args:
            result: The complete run result.
            output_path: Path to write the XML report.
        """
        logger.info(f"Generating JUnit XML report: {output_path}")

        # Create root element
        test_suite = ET.Element("testsuite")
        test_suite.set("name", Path(result.script_path).stem)
        test_suite.set("tests", str(result.total_steps))
        test_suite.set("failures", str(result.failed_steps))
        test_suite.set("skipped", str(result.skipped_steps))
        test_suite.set("time", f"{result.total_duration_seconds:.2f}")

        # Add test cases
        for i, step_result in enumerate(result.step_results, 1):
            test_case = ET.SubElement(test_suite, "testcase")
            test_case.set("name", step_result.step.describe())
            test_case.set("classname", f"{Path(result.script_path).stem}.step_{i}")
            test_case.set("time", f"{step_result.duration_ms / 1000:.3f}")

            # Add failure element if step failed
            if not step_result.success and step_result.error_message:
                failure = ET.SubElement(test_case, "failure")
                failure.set("message", step_result.error_message)
                failure.text = step_result.error_message

        # Write XML file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Pretty print XML
        self._indent_xml(test_suite)
        tree = ET.ElementTree(test_suite)
        tree.write(
            output_file,
            encoding="utf-8",
            xml_declaration=True,
        )

        logger.info(f"JUnit report saved: {output_path}")

    @staticmethod
    def _indent_xml(elem, level=0):
        """Add pretty-print indentation to XML elements."""
        indent = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                JUnitReporter._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent
