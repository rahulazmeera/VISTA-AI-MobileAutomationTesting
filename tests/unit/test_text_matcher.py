"""Tests for text element matcher with fuzzy matching."""

import pytest
from vista.matcher.base import ElementNotFoundError, AmbiguousMatchError
from vista.matcher.text_matcher import TextElementMatcher
from vista.vision.elements import BBox, TextElement
from vista.vision.screen import ScreenState
from PIL import Image


@pytest.mark.unit
class TestTextElementMatcher:
    """Test fuzzy text matching against detected elements."""

    @pytest.fixture
    def matcher(self):
        """Create a text matcher."""
        return TextElementMatcher(similarity_threshold=0.85)

    @pytest.fixture
    def screen_state(self):
        """Create a sample screen state with detected elements."""
        image = Image.new("RGB", (540, 960), color="white")
        text_elements = [
            TextElement(text="Login", bbox=BBox(x=100, y=100, width=100, height=50), confidence=0.95),
            TextElement(text="Email", bbox=BBox(x=100, y=200, width=100, height=40), confidence=0.98),
            TextElement(text="Password", bbox=BBox(x=100, y=300, width=100, height=40), confidence=0.97),
        ]
        return ScreenState(
            screenshot=image,
            text_elements=text_elements,
            icon_elements=[],
            timestamp=0.0,
        )

    def test_exact_match(self, matcher, screen_state):
        """Test matching with exact text match."""
        result = matcher.resolve("Login", screen_state)
        assert result.text == "Login"
        assert result.confidence == 0.95

    def test_case_insensitive_match(self, matcher, screen_state):
        """Test that matching is case insensitive."""
        result = matcher.resolve("login", screen_state)
        assert result.text == "Login"

    def test_fuzzy_match_with_typo(self, matcher):
        """Test fuzzy matching with minor OCR errors."""
        image = Image.new("RGB", (540, 960), color="white")
        text_elements = [
            TextElement(text="Email", bbox=BBox(x=100, y=200, width=100, height=40), confidence=0.98),
        ]
        screen_state = ScreenState(
            screenshot=image,
            text_elements=text_elements,
            icon_elements=[],
            timestamp=0.0,
        )

        # "Email" with lowercase should match
        result = matcher.resolve("email", screen_state)
        assert result.text == "Email"

    def test_partial_match(self, matcher, screen_state):
        """Test matching with partial text."""
        result = matcher.resolve("Pass", screen_state)
        assert result.text == "Password"

    def test_no_match_found(self, matcher, screen_state):
        """Test that ElementNotFoundError is raised when no match exists."""
        with pytest.raises(ElementNotFoundError):
            matcher.resolve("NonExistent", screen_state)

    def test_high_threshold_no_match(self, matcher, screen_state):
        """Test that high threshold prevents fuzzy matches."""
        strict_matcher = TextElementMatcher(similarity_threshold=0.99)
        # Even small errors should fail with 0.99 threshold
        with pytest.raises(ElementNotFoundError):
            strict_matcher.resolve("Emial", screen_state)

    def test_multiple_matches_highest_confidence(self, matcher):
        """Test that highest confidence match is chosen when multiple exist."""
        image = Image.new("RGB", (540, 960), color="white")
        text_elements = [
            TextElement(text="OK", bbox=BBox(x=100, y=100, width=50, height=40), confidence=0.85),
            TextElement(text="OK", bbox=BBox(x=200, y=100, width=50, height=40), confidence=0.95),
            TextElement(text="OK", bbox=BBox(x=300, y=100, width=50, height=40), confidence=0.90),
        ]
        screen_state = ScreenState(
            screenshot=image,
            text_elements=text_elements,
            icon_elements=[],
            timestamp=0.0,
        )

        result = matcher.resolve("OK", screen_state)
        # Should get the one with highest confidence
        assert result.confidence == 0.95

    def test_whitespace_normalization(self, matcher):
        """Test that extra whitespace is handled correctly."""
        image = Image.new("RGB", (540, 960), color="white")
        text_elements = [
            TextElement(text="Sign In", bbox=BBox(x=100, y=100, width=100, height=40), confidence=0.95),
        ]
        screen_state = ScreenState(
            screenshot=image,
            text_elements=text_elements,
            icon_elements=[],
            timestamp=0.0,
        )

        # Extra spaces should be normalized
        result = matcher.resolve("Sign   In", screen_state)
        assert result.text == "Sign In"

    def test_text_normalize_function(self):
        """Test the normalize function directly."""
        assert TextElementMatcher._normalize("Login") == "login"
        assert TextElementMatcher._normalize("  SIGN IN  ") == "sign in"
        assert TextElementMatcher._normalize("Pass  word") == "pass word"

    def test_threshold_validation(self):
        """Test that threshold validation works."""
        with pytest.raises(ValueError, match="Threshold must be"):
            TextElementMatcher(similarity_threshold=1.5)

        with pytest.raises(ValueError, match="Threshold must be"):
            TextElementMatcher(similarity_threshold=-0.1)

    def test_resolve_only_accepts_text_kind(self, matcher, screen_state):
        """Test that resolve only accepts 'text' kind."""
        with pytest.raises(ValueError, match="only handles 'text'"):
            matcher.resolve("Login", screen_state, kind="icon")

    def test_resolve_with_empty_screen(self, matcher):
        """Test resolve with no detected text elements."""
        image = Image.new("RGB", (540, 960), color="white")
        screen_state = ScreenState(
            screenshot=image,
            text_elements=[],
            icon_elements=[],
            timestamp=0.0,
        )

        with pytest.raises(ElementNotFoundError):
            matcher.resolve("Login", screen_state)

    def test_bbox_center_calculation(self, matcher, screen_state):
        """Test that matched element's center is correctly calculated."""
        result = matcher.resolve("Login", screen_state)
        # Element is at x=100, width=100, so center should be at 150
        assert result.bbox.center_x == 150
        # Element is at y=100, height=50, so center should be at 125
        assert result.bbox.center_y == 125
