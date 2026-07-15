"""Tests to verify the basic project scaffold."""

import pytest

from vista import __version__
from vista.dsl.steps import AssertVisibleStep, TapStep, TypeStep
from vista.driver.coordinates import CoordinateConverter
from vista.matcher.disambiguation import (
    HighestConfidenceDisambiguator,
    OccurrenceDisambiguator,
    TopLeftDisambiguator,
)
from vista.vision.elements import BBox, IconElement, TextElement


@pytest.mark.unit
def test_version():
    """Test that the package version is set."""
    assert __version__ == "0.1.0"


@pytest.mark.unit
def test_step_classes_exist():
    """Test that core step classes exist and can be instantiated."""
    tap = TapStep(target="Login")
    assert tap.target == "Login"
    assert tap.describe() == "Tap 'Login'"

    tap_with_occurrence = TapStep(target="Save", occurrence=2)
    assert "occurrence 2" in tap_with_occurrence.describe()

    type_step = TypeStep(text="user@example.com", into="Email")
    assert type_step.text == "user@example.com"

    assert_visible = AssertVisibleStep(target="Welcome")
    assert assert_visible.target == "Welcome"


@pytest.mark.unit
def test_bounding_box():
    """Test BBox calculations."""
    bbox = BBox(x=10, y=20, width=100, height=50)
    assert bbox.center_x == 60
    assert bbox.center_y == 45
    assert bbox.x2 == 110
    assert bbox.y2 == 70
    assert bbox.area() == 5000


@pytest.mark.unit
def test_text_element():
    """Test TextElement creation."""
    bbox = BBox(x=10, y=20, width=100, height=30)
    elem = TextElement(text="Login", bbox=bbox, confidence=0.95)
    assert elem.text == "Login"
    assert elem.confidence == 0.95


@pytest.mark.unit
def test_icon_element():
    """Test IconElement creation."""
    bbox = BBox(x=50, y=60, width=40, height=40)
    elem = IconElement(icon_id="back_arrow", bbox=bbox, confidence=0.88)
    assert elem.icon_id == "back_arrow"
    assert elem.confidence == 0.88


@pytest.mark.unit
def test_coordinate_converter():
    """Test pixel ↔ point coordinate conversion."""
    # Simulate a Retina display (2x scale factor)
    converter = CoordinateConverter((1080, 1920), scale_factor=2.0)
    assert converter.screen_size_points == (540, 960)

    # Convert pixel to point
    assert converter.pixel_to_point(100) == 50
    assert converter.point_to_pixel(50) == 100

    # Convert rectangle
    x_pt, y_pt, w_pt, h_pt = converter.pixel_rect_to_point_rect(0, 0, 200, 200)
    assert x_pt == 0
    assert y_pt == 0
    assert w_pt == 100
    assert h_pt == 100


@pytest.mark.unit
def test_disambiguator_occurrence():
    """Test occurrence-based disambiguation."""
    elem1 = TextElement(text="OK", bbox=BBox(10, 10, 50, 50), confidence=0.9)
    elem2 = TextElement(text="OK", bbox=BBox(100, 100, 50, 50), confidence=0.9)
    elem3 = TextElement(text="OK", bbox=BBox(200, 200, 50, 50), confidence=0.9)

    disamb = OccurrenceDisambiguator(occurrence=2)
    chosen = disamb.choose([elem1, elem2, elem3])
    assert chosen == elem2

    with pytest.raises(ValueError):
        OccurrenceDisambiguator(occurrence=0)  # 0-indexed not allowed

    with pytest.raises(ValueError):
        disamb5 = OccurrenceDisambiguator(occurrence=5)
        disamb5.choose([elem1, elem2])  # Not enough elements


@pytest.mark.unit
def test_disambiguator_top_left():
    """Test top-left disambiguation."""
    elem1 = TextElement(text="B", bbox=BBox(100, 100, 50, 50), confidence=0.9)
    elem2 = TextElement(text="A", bbox=BBox(10, 10, 50, 50), confidence=0.9)
    elem3 = TextElement(text="C", bbox=BBox(200, 200, 50, 50), confidence=0.9)

    disamb = TopLeftDisambiguator()
    chosen = disamb.choose([elem1, elem2, elem3])
    assert chosen == elem2  # elem2 is at (10, 10), top-left


@pytest.mark.unit
def test_disambiguator_highest_confidence():
    """Test highest confidence disambiguation."""
    elem1 = TextElement(text="A", bbox=BBox(10, 10, 50, 50), confidence=0.8)
    elem2 = TextElement(text="B", bbox=BBox(100, 100, 50, 50), confidence=0.95)
    elem3 = TextElement(text="C", bbox=BBox(200, 200, 50, 50), confidence=0.85)

    disamb = HighestConfidenceDisambiguator()
    chosen = disamb.choose([elem1, elem2, elem3])
    assert chosen == elem2  # elem2 has highest confidence
