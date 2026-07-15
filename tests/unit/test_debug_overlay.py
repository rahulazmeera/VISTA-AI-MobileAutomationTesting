"""Tests for debug visualization overlays."""

import pytest
from PIL import Image

from vista.vision.debug import draw_text_elements, draw_icon_elements, draw_all_elements, add_grid
from vista.vision.elements import BBox, TextElement, IconElement


@pytest.mark.unit
class TestDebugOverlay:
    """Test debug visualization functions."""

    @pytest.fixture
    def sample_image(self):
        """Create a sample image for testing."""
        return Image.new("RGB", (512, 512), color="white")

    @pytest.fixture
    def sample_text_elements(self):
        """Create sample text elements."""
        return [
            TextElement(
                text="Login",
                bbox=BBox(x=100, y=100, width=150, height=50),
                confidence=0.95,
            ),
            TextElement(
                text="Email",
                bbox=BBox(x=100, y=200, width=150, height=40),
                confidence=0.98,
            ),
        ]

    @pytest.fixture
    def sample_icon_elements(self):
        """Create sample icon elements."""
        return [
            IconElement(
                icon_id="back_button",
                bbox=BBox(x=20, y=20, width=40, height=40),
                confidence=0.92,
            ),
        ]

    def test_draw_text_elements_returns_image(self, sample_image, sample_text_elements):
        """Test that draw_text_elements returns a PIL Image."""
        result = draw_text_elements(sample_image, sample_text_elements)

        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size
        # Result should be different from original (has overlays)
        assert result is not sample_image

    def test_draw_text_elements_with_confidence_threshold(self, sample_image, sample_text_elements):
        """Test that confidence threshold filtering works."""
        # With threshold 0.96, only "Email" (0.98) should be drawn
        result = draw_text_elements(
            sample_image,
            sample_text_elements,
            confidence_threshold=0.96,
        )

        assert isinstance(result, Image.Image)

    def test_draw_text_elements_without_confidence_display(self, sample_image, sample_text_elements):
        """Test drawing text elements without confidence scores."""
        result = draw_text_elements(
            sample_image,
            sample_text_elements,
            show_confidence=False,
        )

        assert isinstance(result, Image.Image)

    def test_draw_icon_elements_returns_image(self, sample_image, sample_icon_elements):
        """Test that draw_icon_elements returns a PIL Image."""
        result = draw_icon_elements(sample_image, sample_icon_elements)

        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size
        assert result is not sample_image

    def test_draw_all_elements_combines_text_and_icons(self, sample_image, sample_text_elements, sample_icon_elements):
        """Test that draw_all_elements combines text and icon overlays."""
        result = draw_all_elements(
            sample_image,
            sample_text_elements,
            sample_icon_elements,
        )

        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size

    def test_add_grid_returns_image(self, sample_image):
        """Test that add_grid returns a PIL Image with grid overlay."""
        result = add_grid(sample_image, grid_size=50)

        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size
        assert result is not sample_image

    def test_add_grid_with_different_sizes(self, sample_image):
        """Test add_grid with different grid sizes."""
        result_25 = add_grid(sample_image, grid_size=25)
        result_100 = add_grid(sample_image, grid_size=100)

        # Both should produce valid images
        assert isinstance(result_25, Image.Image)
        assert isinstance(result_100, Image.Image)

    def test_empty_text_elements(self, sample_image):
        """Test drawing with no text elements."""
        result = draw_text_elements(sample_image, [])

        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size

    def test_empty_icon_elements(self, sample_image):
        """Test drawing with no icon elements."""
        result = draw_icon_elements(sample_image, [])

        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size

    def test_original_image_not_modified(self, sample_image, sample_text_elements):
        """Test that original image is not modified by drawing functions."""
        original_pixels = list(sample_image.getdata())

        # Draw overlays
        result = draw_text_elements(sample_image, sample_text_elements)

        # Original should be unchanged
        current_pixels = list(sample_image.getdata())
        assert original_pixels == current_pixels

    def test_overlay_with_edge_coordinates(self, sample_image):
        """Test drawing elements at image edges."""
        # Element at top-left
        edge_elements = [
            TextElement(
                text="TopLeft",
                bbox=BBox(x=0, y=0, width=50, height=30),
                confidence=0.9,
            ),
            # Element at bottom-right
            TextElement(
                text="BottomRight",
                bbox=BBox(x=462, y=482, width=50, height=30),
                confidence=0.9,
            ),
        ]

        result = draw_text_elements(sample_image, edge_elements)

        assert isinstance(result, Image.Image)

    def test_text_element_properties_preserved(self, sample_image, sample_text_elements):
        """Test that text elements retain their properties after drawing."""
        original_text = sample_text_elements[0].text
        original_bbox = sample_text_elements[0].bbox
        original_confidence = sample_text_elements[0].confidence

        draw_text_elements(sample_image, sample_text_elements)

        # Original objects should be unchanged
        assert sample_text_elements[0].text == original_text
        assert sample_text_elements[0].bbox == original_bbox
        assert sample_text_elements[0].confidence == original_confidence
