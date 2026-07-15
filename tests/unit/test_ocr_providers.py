"""Tests for OCR providers (unit level, no actual OCR models needed)."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PIL import Image, ImageDraw, ImageFont

from vista.vision.elements import BBox, TextElement
from vista.vision.ocr.base import OCRProvider


@pytest.mark.unit
class TestOCRProviderBase:
    """Test OCRProvider abstract base class and contract."""

    def test_ocr_provider_is_abstract(self):
        """Test that OCRProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            OCRProvider()

    def test_text_element_creation(self):
        """Test creating TextElement objects (OCR output)."""
        bbox = BBox(x=10, y=20, width=100, height=30)
        elem = TextElement(text="Login", bbox=bbox, confidence=0.95)

        assert elem.text == "Login"
        assert elem.bbox == bbox
        assert elem.confidence == 0.95

    def test_ocr_output_structure(self):
        """Test that OCR outputs are properly structured."""
        # Simulate OCR detection result
        elements = [
            TextElement(
                text="Email",
                bbox=BBox(x=50, y=100, width=150, height=40),
                confidence=0.98,
            ),
            TextElement(
                text="Password",
                bbox=BBox(x=50, y=200, width=150, height=40),
                confidence=0.97,
            ),
            TextElement(
                text="Login",
                bbox=BBox(x=150, y=300, width=100, height=40),
                confidence=0.96,
            ),
        ]

        # Verify structure
        assert len(elements) == 3
        assert all(isinstance(e, TextElement) for e in elements)
        assert all(isinstance(e.bbox, BBox) for e in elements)
        assert all(0.0 <= e.confidence <= 1.0 for e in elements)


@pytest.mark.unit
class TestTextElementDetection:
    """Test text element detection and coordinate conversion logic."""

    def test_text_element_from_paddle_format(self):
        """Test converting PaddleOCR output format to TextElement."""
        # PaddleOCR output: [[[x1,y1], [x2,y1], [x2,y2], [x1,y2]], ('text', confidence)]
        coords = [[10, 20], [110, 20], [110, 50], [10, 50]]
        text = "Email"
        confidence = 0.98

        # Convert to BBox
        xs = [int(pt[0]) for pt in coords]
        ys = [int(pt[1]) for pt in coords]
        x_min, y_min = min(xs), min(ys)
        x_max, y_max = max(xs), max(ys)
        bbox = BBox(x=x_min, y=y_min, width=x_max - x_min, height=y_max - y_min)

        elem = TextElement(text=text, bbox=bbox, confidence=confidence)

        assert elem.text == "Email"
        assert elem.bbox.x == 10
        assert elem.bbox.y == 20
        assert elem.bbox.width == 100
        assert elem.bbox.height == 30
        assert elem.confidence == 0.98

    def test_text_element_from_easy_format(self):
        """Test converting EasyOCR output format to TextElement."""
        # EasyOCR output: ([x1,y1], [x2,y2], [x3,y3], [x4,y4]), 'text', confidence
        coords = ([10, 20], [110, 20], [110, 50], [10, 50])
        text = "Password"
        confidence = 0.97

        # Convert to BBox
        xs = [int(pt[0]) for pt in coords]
        ys = [int(pt[1]) for pt in coords]
        x_min, y_min = min(xs), min(ys)
        x_max, y_max = max(xs), max(ys)
        bbox = BBox(x=x_min, y=y_min, width=x_max - x_min, height=y_max - y_min)

        elem = TextElement(text=text, bbox=bbox, confidence=confidence)

        assert elem.text == "Password"
        assert elem.bbox.x == 10
        assert elem.bbox.y == 20
        assert elem.bbox.width == 100
        assert elem.bbox.height == 30
        assert elem.confidence == 0.97

    def test_multiple_text_elements(self):
        """Test handling multiple text elements."""
        elements = [
            TextElement(
                text="Email",
                bbox=BBox(x=10, y=20, width=100, height=30),
                confidence=0.98,
            ),
            TextElement(
                text="Password",
                bbox=BBox(x=10, y=80, width=100, height=30),
                confidence=0.97,
            ),
            TextElement(
                text="Login",
                bbox=BBox(x=50, y=150, width=100, height=30),
                confidence=0.96,
            ),
        ]

        assert len(elements) == 3
        assert elements[0].text == "Email"
        assert elements[1].text == "Password"
        assert elements[2].text == "Login"

    def test_text_element_confidence_bounds(self):
        """Test that confidence values are properly bounded."""
        # Valid confidence
        elem = TextElement(
            text="Test",
            bbox=BBox(x=0, y=0, width=100, height=30),
            confidence=0.95,
        )
        assert 0.0 <= elem.confidence <= 1.0

    def test_bbox_coordinate_consistency(self):
        """Test that bbox coordinates are internally consistent."""
        bbox = BBox(x=10, y=20, width=100, height=50)

        # Verify properties
        assert bbox.x2 == 110  # x + width
        assert bbox.y2 == 70  # y + height
        assert bbox.area() == 5000  # width * height
