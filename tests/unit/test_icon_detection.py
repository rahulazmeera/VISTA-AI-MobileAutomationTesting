"""Tests for icon detection and matching."""

import pytest
from PIL import Image, ImageDraw

from vista.matcher.base import ElementNotFoundError
from vista.matcher.icon_matcher import IconElementMatcher
from vista.vision.elements import BBox, IconElement
from vista.vision.icons.base import IconCatalog
from vista.vision.icons.template_matcher import TemplateMatchingDetector
from vista.vision.screen import ScreenState


@pytest.mark.unit
class TestTemplateMatchingDetector:
    """Test OpenCV template matching for icon detection."""

    @pytest.fixture
    def detector(self):
        """Create a template matching detector."""
        return TemplateMatchingDetector(match_threshold=0.7)

    def test_detector_initialization(self):
        """Test that detector initializes correctly."""
        detector = TemplateMatchingDetector(match_threshold=0.8)
        assert detector.match_threshold == 0.8

    def test_invalid_threshold(self):
        """Test that invalid threshold raises error."""
        with pytest.raises(ValueError, match="Threshold must be"):
            TemplateMatchingDetector(match_threshold=1.5)

    def test_empty_catalog(self, detector):
        """Test detection with empty catalog."""
        image = Image.new("RGB", (540, 960), color="white")
        result = detector.detect_icons(image, catalog=None)
        assert result == []

    def test_empty_catalog_object(self, detector):
        """Test detection with empty catalog object."""
        image = Image.new("RGB", (540, 960), color="white")
        catalog = IconCatalog()
        result = detector.detect_icons(image, catalog=catalog)
        assert result == []

    def test_simple_template_match(self, detector):
        """Test matching a simple template on a larger image."""
        # Create a small template (white square)
        template = Image.new("RGB", (50, 50), color="white")

        # Create a larger image with the template in the middle
        image = Image.new("RGB", (540, 960), color="black")
        image.paste(template, (245, 455))  # Paste near center

        # Create catalog with the template
        catalog = IconCatalog()
        catalog.add("test_icon", template)

        # Detect
        result = detector.detect_icons(image, catalog=catalog)

        # Should find at least one match
        assert len(result) > 0
        # Check the match is near where we pasted it
        detected = result[0]
        assert detected.icon_id == "test_icon"
        assert 240 < detected.bbox.x < 250  # Approximately at x=245
        assert 450 < detected.bbox.y < 460  # Approximately at y=455

    def test_iou_calculation(self):
        """Test IoU calculation for overlapping boxes."""
        bbox1 = BBox(x=0, y=0, width=100, height=100)
        bbox2 = BBox(x=50, y=50, width=100, height=100)

        # 50x50 intersection, 150x150 union = 2500/22500 ≈ 0.111
        iou = TemplateMatchingDetector._compute_iou(bbox1, bbox2)
        assert 0.1 < iou < 0.15

    def test_iou_no_overlap(self):
        """Test IoU with non-overlapping boxes."""
        bbox1 = BBox(x=0, y=0, width=100, height=100)
        bbox2 = BBox(x=200, y=200, width=100, height=100)

        iou = TemplateMatchingDetector._compute_iou(bbox1, bbox2)
        assert iou == 0.0

    def test_iou_complete_overlap(self):
        """Test IoU with completely overlapping boxes."""
        bbox1 = BBox(x=0, y=0, width=100, height=100)
        bbox2 = BBox(x=0, y=0, width=100, height=100)

        iou = TemplateMatchingDetector._compute_iou(bbox1, bbox2)
        assert iou == 1.0

    def test_filter_overlapping(self):
        """Test filtering of overlapping detections."""
        elem1 = IconElement(
            icon_id="icon1",
            bbox=BBox(x=0, y=0, width=50, height=50),
            confidence=0.9,
        )
        elem2 = IconElement(
            icon_id="icon1",
            bbox=BBox(x=25, y=25, width=50, height=50),
            confidence=0.85,
        )
        elem3 = IconElement(
            icon_id="icon1",
            bbox=BBox(x=200, y=200, width=50, height=50),
            confidence=0.88,
        )

        # elem1 and elem2 overlap significantly, elem3 doesn't
        filtered = TemplateMatchingDetector._filter_overlapping(
            [elem1, elem2, elem3], iou_threshold=0.3
        )

        # Should keep elem1 (highest confidence) and elem3 (no overlap)
        assert len(filtered) == 2
        assert elem1 in filtered  # Highest confidence
        assert elem3 in filtered  # Non-overlapping


@pytest.mark.unit
class TestIconElementMatcher:
    """Test icon element matching."""

    @pytest.fixture
    def matcher(self):
        """Create an icon matcher."""
        return IconElementMatcher()

    @pytest.fixture
    def screen_with_icons(self):
        """Create a screen state with icon elements."""
        image = Image.new("RGB", (540, 960), color="white")
        icon_elements = [
            IconElement(
                icon_id="back_arrow",
                bbox=BBox(x=20, y=20, width=40, height=40),
                confidence=0.95,
            ),
            IconElement(
                icon_id="menu_button",
                bbox=BBox(x=500, y=20, width=40, height=40),
                confidence=0.92,
            ),
            IconElement(
                icon_id="settings",
                bbox=BBox(x=270, y=450, width=50, height=50),
                confidence=0.88,
            ),
        ]
        return ScreenState(
            screenshot=image,
            text_elements=[],
            icon_elements=icon_elements,
            timestamp=0.0,
        )

    def test_exact_icon_match(self, matcher, screen_with_icons):
        """Test exact icon ID matching."""
        result = matcher.resolve("back_arrow", screen_with_icons)
        assert result.icon_id == "back_arrow"
        assert result.confidence == 0.95

    def test_case_insensitive_icon_match(self, matcher, screen_with_icons):
        """Test that icon matching is case insensitive."""
        result = matcher.resolve("BACK_ARROW", screen_with_icons)
        assert result.icon_id == "back_arrow"

    def test_icon_not_found(self, matcher, screen_with_icons):
        """Test error when icon is not found."""
        with pytest.raises(ElementNotFoundError):
            matcher.resolve("nonexistent_icon", screen_with_icons)

    def test_multiple_same_icons_highest_confidence(self, matcher):
        """Test that highest confidence icon is chosen when multiple exist."""
        image = Image.new("RGB", (540, 960), color="white")
        icon_elements = [
            IconElement(
                icon_id="close",
                bbox=BBox(x=100, y=100, width=40, height=40),
                confidence=0.85,
            ),
            IconElement(
                icon_id="close",
                bbox=BBox(x=200, y=100, width=40, height=40),
                confidence=0.95,
            ),
            IconElement(
                icon_id="close",
                bbox=BBox(x=300, y=100, width=40, height=40),
                confidence=0.90,
            ),
        ]
        screen = ScreenState(
            screenshot=image,
            text_elements=[],
            icon_elements=icon_elements,
            timestamp=0.0,
        )

        result = matcher.resolve("close", screen)
        # Should get the one with highest confidence
        assert result.confidence == 0.95
        assert result.bbox.x == 200

    def test_resolve_only_accepts_icon_kind(self, matcher, screen_with_icons):
        """Test that resolve only accepts 'icon' kind."""
        with pytest.raises(ValueError, match="only handles 'icon'"):
            matcher.resolve("back_arrow", screen_with_icons, kind="text")

    def test_resolve_with_empty_icons(self, matcher):
        """Test resolve with no icon elements."""
        image = Image.new("RGB", (540, 960), color="white")
        screen = ScreenState(
            screenshot=image,
            text_elements=[],
            icon_elements=[],
            timestamp=0.0,
        )

        with pytest.raises(ElementNotFoundError):
            matcher.resolve("back_arrow", screen)

    def test_icon_center_calculation(self, matcher, screen_with_icons):
        """Test that matched icon's center is correctly calculated."""
        result = matcher.resolve("back_arrow", screen_with_icons)
        # Icon is at x=20, width=40, so center should be at 40
        assert result.bbox.center_x == 40
        # Icon is at y=20, height=40, so center should be at 40
        assert result.bbox.center_y == 40


@pytest.mark.unit
class TestIconCatalog:
    """Test icon catalog functionality."""

    def test_catalog_add_and_get(self):
        """Test adding and retrieving icons from catalog."""
        catalog = IconCatalog()
        icon1 = Image.new("RGB", (40, 40), color="red")

        catalog.add("back_button", icon1)
        retrieved = catalog.get("back_button")

        assert retrieved is icon1

    def test_catalog_contains(self):
        """Test checking if icon exists in catalog."""
        catalog = IconCatalog()
        icon = Image.new("RGB", (40, 40), color="blue")
        catalog.add("menu_icon", icon)

        assert "menu_icon" in catalog
        assert "nonexistent" not in catalog

    def test_catalog_get_nonexistent(self):
        """Test getting nonexistent icon returns None."""
        catalog = IconCatalog()
        assert catalog.get("nonexistent") is None

    def test_catalog_multiple_icons(self):
        """Test catalog with multiple icons."""
        catalog = IconCatalog()
        for i in range(5):
            icon = Image.new("RGB", (40, 40), color="white")
            catalog.add(f"icon_{i}", icon)

        assert len(catalog.icons) == 5
        for i in range(5):
            assert f"icon_{i}" in catalog
