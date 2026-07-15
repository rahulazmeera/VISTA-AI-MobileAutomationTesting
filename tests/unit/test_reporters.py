"""Tests for report generation."""

import pytest
from pathlib import Path
from xml.etree import ElementTree as ET

from vista.report.html_reporter import HTMLReporter
from vista.report.junit_reporter import JUnitReporter
from vista.report.models import RunResult, StepResult
from vista.dsl.steps import TapStep


@pytest.mark.unit
class TestHTMLReporter:
    """Test HTML report generation."""

    @pytest.fixture
    def run_result(self):
        """Create a sample run result."""
        return RunResult(
            script_path="test_login.yaml",
            total_steps=3,
            passed_steps=2,
            failed_steps=1,
            skipped_steps=0,
            total_duration_seconds=5.2,
            step_results=[
                StepResult(
                    step=TapStep(target="Email"),
                    success=True,
                    duration_ms=125.0,
                ),
                StepResult(
                    step=TapStep(target="Login"),
                    success=False,
                    duration_ms=75.0,
                    error_message="Element 'Login' not found on screen",
                ),
                StepResult(
                    step=TapStep(target="Home"),
                    success=True,
                    duration_ms=95.0,
                ),
            ],
        )

    def test_html_reporter_renders(self, run_result, tmp_path):
        """Test that HTML report is generated."""
        output_file = tmp_path / "report.html"

        reporter = HTMLReporter()
        reporter.report(run_result, str(output_file))

        # Verify file exists
        assert output_file.exists()

        # Verify content
        content = output_file.read_text()
        assert "VISTA Test Report" in content
        assert "test_login.yaml" in content
        assert "3" in content  # Total steps
        assert "2" in content  # Passed
        assert "1" in content  # Failed

    def test_html_report_includes_errors(self, run_result, tmp_path):
        """Test that error messages are included in HTML."""
        output_file = tmp_path / "report.html"

        reporter = HTMLReporter()
        reporter.report(run_result, str(output_file))

        content = output_file.read_text()
        assert "Element 'Login' not found on screen" in content

    def test_html_report_summary_correct(self, run_result, tmp_path):
        """Test that summary statistics are correct."""
        output_file = tmp_path / "report.html"

        reporter = HTMLReporter()
        reporter.report(run_result, str(output_file))

        content = output_file.read_text()
        # Pass rate should be 66.67%
        assert "66" in content  # Approximate percentage


@pytest.mark.unit
class TestJUnitReporter:
    """Test JUnit XML report generation."""

    @pytest.fixture
    def run_result(self):
        """Create a sample run result."""
        return RunResult(
            script_path="test_login.yaml",
            total_steps=3,
            passed_steps=2,
            failed_steps=1,
            skipped_steps=0,
            total_duration_seconds=5.2,
            step_results=[
                StepResult(
                    step=TapStep(target="Email"),
                    success=True,
                    duration_ms=125.0,
                ),
                StepResult(
                    step=TapStep(target="Login"),
                    success=False,
                    duration_ms=75.0,
                    error_message="Element 'Login' not found",
                ),
                StepResult(
                    step=TapStep(target="Home"),
                    success=True,
                    duration_ms=95.0,
                ),
            ],
        )

    def test_junit_reporter_creates_xml(self, run_result, tmp_path):
        """Test that JUnit XML is generated."""
        output_file = tmp_path / "report.xml"

        reporter = JUnitReporter()
        reporter.report(run_result, str(output_file))

        # Verify file exists
        assert output_file.exists()

        # Parse XML
        tree = ET.parse(output_file)
        root = tree.getroot()
        assert root.tag == "testsuite"

    def test_junit_report_attributes(self, run_result, tmp_path):
        """Test that JUnit XML has correct attributes."""
        output_file = tmp_path / "report.xml"

        reporter = JUnitReporter()
        reporter.report(run_result, str(output_file))

        tree = ET.parse(output_file)
        root = tree.getroot()

        assert root.get("tests") == "3"
        assert root.get("failures") == "1"
        assert root.get("skipped") == "0"

    def test_junit_report_test_cases(self, run_result, tmp_path):
        """Test that test cases are included."""
        output_file = tmp_path / "report.xml"

        reporter = JUnitReporter()
        reporter.report(run_result, str(output_file))

        tree = ET.parse(output_file)
        root = tree.getroot()

        test_cases = root.findall("testcase")
        assert len(test_cases) == 3

    def test_junit_report_failure_element(self, run_result, tmp_path):
        """Test that failures are captured in XML."""
        output_file = tmp_path / "report.xml"

        reporter = JUnitReporter()
        reporter.report(run_result, str(output_file))

        tree = ET.parse(output_file)
        root = tree.getroot()

        failures = root.findall(".//failure")
        assert len(failures) == 1
        assert "Element 'Login' not found" in failures[0].get("message")

    def test_junit_report_timing(self, run_result, tmp_path):
        """Test that timings are included."""
        output_file = tmp_path / "report.xml"

        reporter = JUnitReporter()
        reporter.report(run_result, str(output_file))

        tree = ET.parse(output_file)
        root = tree.getroot()

        # Check suite time
        assert root.get("time") == "5.20"

        # Check step times
        test_cases = root.findall("testcase")
        assert test_cases[0].get("time") == "0.125"  # 125ms


@pytest.mark.unit
class TestRunResult:
    """Test RunResult model."""

    def test_run_result_success_property(self):
        """Test that success property works correctly."""
        result_pass = RunResult(
            script_path="test.yaml",
            total_steps=1,
            passed_steps=1,
            failed_steps=0,
            skipped_steps=0,
            total_duration_seconds=1.0,
            step_results=[],
        )

        result_fail = RunResult(
            script_path="test.yaml",
            total_steps=1,
            passed_steps=0,
            failed_steps=1,
            skipped_steps=0,
            total_duration_seconds=1.0,
            step_results=[],
        )

        assert result_pass.success is True
        assert result_fail.success is False

    def test_run_result_pass_rate(self):
        """Test pass rate calculation."""
        result = RunResult(
            script_path="test.yaml",
            total_steps=3,
            passed_steps=2,
            failed_steps=1,
            skipped_steps=0,
            total_duration_seconds=1.0,
            step_results=[],
        )

        assert result.pass_rate == pytest.approx(66.67, 0.1)

    def test_run_result_zero_steps(self):
        """Test pass rate with zero steps."""
        result = RunResult(
            script_path="test.yaml",
            total_steps=0,
            passed_steps=0,
            failed_steps=0,
            skipped_steps=0,
            total_duration_seconds=0.0,
            step_results=[],
        )

        assert result.pass_rate == 0.0
