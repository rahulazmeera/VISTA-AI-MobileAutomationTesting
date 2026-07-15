"""Tests for YAML DSL parser."""

import pytest
from vista.dsl.parser import DSLParser, ParseError
from vista.dsl.steps import (
    AssertVisibleStep,
    TapStep,
    TypeStep,
    WaitStep,
    PressKeyStep,
    SwipeStep,
)


@pytest.mark.unit
class TestDSLParser:
    """Test YAML DSL parsing."""

    def test_parse_simple_tap(self):
        """Test parsing a simple tap step."""
        yaml_data = {
            "steps": [
                {"tap": "Login"},
            ]
        }

        steps = DSLParser.parse_dict(yaml_data)
        assert len(steps) == 1
        assert isinstance(steps[0], TapStep)
        assert steps[0].target == "Login"

    def test_parse_type_step(self):
        """Test parsing a type step."""
        yaml_data = {
            "steps": [
                {"type": {"text": "user@example.com", "into": "Email"}},
            ]
        }

        steps = DSLParser.parse_dict(yaml_data)
        assert len(steps) == 1
        assert isinstance(steps[0], TypeStep)
        assert steps[0].text == "user@example.com"
        assert steps[0].into == "Email"

    def test_parse_swipe_step(self):
        """Test parsing a swipe step."""
        yaml_data = {
            "steps": [
                {"swipe": {"direction": "up", "amount": 0.5}},
            ]
        }

        steps = DSLParser.parse_dict(yaml_data)
        assert len(steps) == 1
        assert isinstance(steps[0], SwipeStep)
        assert steps[0].direction == "up"
        assert steps[0].amount == 0.5

    def test_parse_wait_step_seconds(self):
        """Test parsing a wait step with seconds."""
        yaml_data = {
            "steps": [
                {"wait": 2},
            ]
        }

        steps = DSLParser.parse_dict(yaml_data)
        assert len(steps) == 1
        assert isinstance(steps[0], WaitStep)
        assert steps[0].seconds == 2

    def test_parse_assert_visible_step(self):
        """Test parsing an assert visible step."""
        yaml_data = {
            "steps": [
                {"assert_visible": "Welcome"},
            ]
        }

        steps = DSLParser.parse_dict(yaml_data)
        assert len(steps) == 1
        assert isinstance(steps[0], AssertVisibleStep)
        assert steps[0].target == "Welcome"

    def test_parse_press_key_step(self):
        """Test parsing a press key step."""
        yaml_data = {
            "steps": [
                {"press_key": "return"},
            ]
        }

        steps = DSLParser.parse_dict(yaml_data)
        assert len(steps) == 1
        assert isinstance(steps[0], PressKeyStep)
        assert steps[0].key == "return"

    def test_parse_multiple_steps(self):
        """Test parsing a complete login flow."""
        yaml_data = {
            "steps": [
                {"tap": "Email"},
                {"type": {"text": "test@example.com", "into": "Email"}},
                {"tap": "Password"},
                {"type": {"text": "password123", "into": "Password"}},
                {"tap": "Login"},
                {"wait": 2},
                {"assert_visible": "Welcome"},
            ]
        }

        steps = DSLParser.parse_dict(yaml_data)
        assert len(steps) == 7
        assert isinstance(steps[0], TapStep)
        assert isinstance(steps[1], TypeStep)
        assert isinstance(steps[4], TapStep)
        assert isinstance(steps[5], WaitStep)
        assert isinstance(steps[6], AssertVisibleStep)

    def test_parse_tap_with_occurrence(self):
        """Test parsing tap with occurrence disambiguation."""
        yaml_data = {
            "steps": [
                {"tap": {"target": "OK", "occurrence": 2}},
            ]
        }

        steps = DSLParser.parse_dict(yaml_data)
        assert len(steps) == 1
        assert isinstance(steps[0], TapStep)
        assert steps[0].target == "OK"
        assert steps[0].occurrence == 2

    def test_parse_error_missing_steps(self):
        """Test that error is raised if 'steps' key is missing."""
        yaml_data = {"flow": []}

        with pytest.raises(ParseError, match="must contain 'steps' key"):
            DSLParser.parse_dict(yaml_data)

    def test_parse_error_invalid_step_type(self):
        """Test that error is raised for unknown step type."""
        yaml_data = {
            "steps": [
                {"unknown_step": "value"},
            ]
        }

        with pytest.raises(ParseError, match="Unknown step type"):
            DSLParser.parse_dict(yaml_data)

    def test_parse_error_empty_step(self):
        """Test that error is raised for empty step."""
        yaml_data = {
            "steps": [
                {},
            ]
        }

        with pytest.raises(ParseError):
            DSLParser.parse_dict(yaml_data)

    def test_parse_error_type_missing_into(self):
        """Test that error is raised when type step is missing 'into' field."""
        yaml_data = {
            "steps": [
                {"type": "test@example.com"},
            ]
        }

        with pytest.raises(ParseError, match="requires 'into' field"):
            DSLParser.parse_dict(yaml_data)

    def test_step_description(self):
        """Test that steps have readable descriptions."""
        yaml_data = {
            "steps": [
                {"tap": "Login"},
                {"type": {"text": "password", "into": "Password"}},
                {"wait": 2},
            ]
        }

        steps = DSLParser.parse_dict(yaml_data)
        assert "Login" in steps[0].describe()
        assert "password" in steps[1].describe()
        assert "2" in steps[2].describe()
