"""YAML parser for VISTA test scripts."""

import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import ValidationError

from vista.dsl.steps import (
    AssertNotVisibleStep,
    AssertVisibleStep,
    CommentStep,
    PressKeyStep,
    ScrollUntilVisibleStep,
    SwipeStep,
    TapIconStep,
    TapStep,
    TypeStep,
    WaitStep,
    Step,
)

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Raised when YAML parsing fails."""

    pass


class DSLParser:
    """Parser for VISTA YAML test scripts."""

    # Map step type identifiers to Step classes
    STEP_TYPES = {
        "tap": TapStep,
        "type": TypeStep,
        "tap_icon": TapIconStep,
        "swipe": SwipeStep,
        "assert_visible": AssertVisibleStep,
        "assert_not_visible": AssertNotVisibleStep,
        "wait": WaitStep,
        "scroll_until_visible": ScrollUntilVisibleStep,
        "press_key": PressKeyStep,
        "#": CommentStep,  # Comments
    }

    @staticmethod
    def parse_file(path: str) -> List[Step]:
        """
        Parse a YAML test script file.

        Args:
            path: Path to the YAML file.

        Returns:
            A list of Step objects.

        Raises:
            ParseError: If the file cannot be parsed.
            FileNotFoundError: If the file doesn't exist.
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Test script not found: {path}")

        logger.info(f"Parsing test script: {path}")

        try:
            with open(file_path, "r") as f:
                content = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ParseError(f"Invalid YAML: {e}") from e

        return DSLParser.parse_dict(content)

    @staticmethod
    def parse_dict(data: Any) -> List[Step]:
        """
        Parse YAML data (already loaded as a dict).

        Args:
            data: Parsed YAML data (should be a dict with 'steps' key).

        Returns:
            A list of Step objects.

        Raises:
            ParseError: If the data structure is invalid.
        """
        if not isinstance(data, dict):
            raise ParseError("YAML root must be a dict with 'steps' key")

        if "steps" not in data:
            raise ParseError("YAML must contain 'steps' key")

        steps_data = data["steps"]
        if not isinstance(steps_data, list):
            raise ParseError("'steps' must be a list")

        steps = []
        for i, step_data in enumerate(steps_data):
            try:
                step = DSLParser._parse_step(step_data)
                steps.append(step)
            except Exception as e:
                raise ParseError(f"Error parsing step {i + 1}: {e}") from e

        logger.info(f"Parsed {len(steps)} steps")
        return steps

    @staticmethod
    def _parse_step(step_data: Any) -> Step:
        """
        Parse a single step from YAML.

        Args:
            step_data: A dict representing one step.

        Returns:
            A Step object.

        Raises:
            ParseError: If the step format is invalid.
        """
        if not isinstance(step_data, dict):
            raise ParseError(f"Step must be a dict, got {type(step_data)}")

        if not step_data:
            raise ParseError("Step dict is empty")

        # Find the step type (first key)
        step_type = next(iter(step_data.keys()))

        if step_type not in DSLParser.STEP_TYPES:
            raise ParseError(
                f"Unknown step type: '{step_type}'. "
                f"Valid types: {', '.join(DSLParser.STEP_TYPES.keys())}"
            )

        step_class = DSLParser.STEP_TYPES[step_type]
        step_value = step_data[step_type]

        # Handle comments
        if step_type == "#":
            return CommentStep(text=str(step_value))

        # For other step types, value can be a string or dict
        if isinstance(step_value, (str, int, float)):
            # Simple steps like "tap: Login" or "wait: 2"
            if step_type == "tap":
                return TapStep(target=str(step_value))
            elif step_type == "type":
                raise ParseError(
                    f"'type' step requires 'into' field: type: <text>\\n  into: <field>"
                )
            elif step_type == "tap_icon":
                return TapIconStep(icon=str(step_value))
            elif step_type == "swipe":
                raise ParseError(
                    f"'swipe' step requires direction field: swipe: up|down|left|right"
                )
            elif step_type == "wait":
                return WaitStep(seconds=float(step_value))
            elif step_type == "assert_visible":
                return AssertVisibleStep(target=str(step_value))
            elif step_type == "assert_not_visible":
                return AssertNotVisibleStep(target=str(step_value))
            elif step_type == "press_key":
                return PressKeyStep(key=str(step_value))

        elif isinstance(step_value, dict):
            # Complex steps with multiple fields
            try:
                # Add the step type to the dict so Pydantic can construct it
                full_data = {"target": None, "icon": None, "text": None, "into": None, **step_value}

                if step_type == "tap":
                    return TapStep(**step_value)
                elif step_type == "type":
                    return TypeStep(**step_value)
                elif step_type == "tap_icon":
                    return TapIconStep(**step_value)
                elif step_type == "swipe":
                    return SwipeStep(**step_value)
                elif step_type == "wait":
                    return WaitStep(**step_value)
                elif step_type == "assert_visible":
                    return AssertVisibleStep(**step_value)
                elif step_type == "assert_not_visible":
                    return AssertNotVisibleStep(**step_value)
                elif step_type == "scroll_until_visible":
                    return ScrollUntilVisibleStep(**step_value)
                elif step_type == "press_key":
                    return PressKeyStep(**step_value)
            except ValidationError as e:
                raise ParseError(f"Invalid step format: {e}")

        else:
            raise ParseError(f"Step value must be string or dict, got {type(step_value)}")

        raise ParseError(f"Could not parse step: {step_data}")


def parse(path: str) -> List[Step]:
    """
    Convenience function to parse a YAML test script.

    Args:
        path: Path to the YAML file.

    Returns:
        A list of Step objects.

    Raises:
        ParseError: If parsing fails.
        FileNotFoundError: If the file doesn't exist.
    """
    return DSLParser.parse_file(path)
