"""Tests for iOS Appium driver coordinate handling and logic."""

import pytest
from vista.driver.base import Point
from vista.driver.coordinates import CoordinateConverter


@pytest.mark.unit
class TestIOSDriverCoordinateLogic:
    """Test iOS driver coordinate conversion logic (without Appium dependency)."""

    def test_coordinate_conversion_for_tap(self):
        """Test that tap coordinates are correctly converted from points to pixels."""
        # Simulate a Retina device: 1080x1920 pixels = 540x960 points (2x scale)
        converter = CoordinateConverter((1080, 1920), scale_factor=2.0)

        # Tap at center of screen (270, 480) points on a 540x960 point screen
        # Should convert to (540, 960) pixels on the 1080x1920 pixel screenshot
        x_pt, y_pt = 270, 480
        x_px = converter.point_to_pixel(x_pt)
        y_px = converter.point_to_pixel(y_pt)

        assert x_px == 540  # 270 * 2.0
        assert y_px == 960  # 480 * 2.0

    def test_coordinate_conversion_for_swipe(self):
        """Test that swipe start/end coordinates are correctly converted."""
        # Retina device
        converter = CoordinateConverter((1080, 1920), scale_factor=2.0)

        # Swipe from (270, 200) to (270, 800) points
        start_x_pt, start_y_pt = 270, 200
        end_x_pt, end_y_pt = 270, 800

        start_x_px = converter.point_to_pixel(start_x_pt)
        start_y_px = converter.point_to_pixel(start_y_pt)
        end_x_px = converter.point_to_pixel(end_x_pt)
        end_y_px = converter.point_to_pixel(end_y_pt)

        # Verify conversion
        assert start_x_px == 540  # 270 * 2.0
        assert start_y_px == 400  # 200 * 2.0
        assert end_x_px == 540  # 270 * 2.0
        assert end_y_px == 1600  # 800 * 2.0

    def test_point_class_compatibility(self):
        """Test that Point class works for coordinate operations."""
        start = Point(x=100, y=200)
        end = Point(x=300, y=400)

        # Verify Point fields are accessible
        assert start.x == 100
        assert start.y == 200
        assert end.x == 300
        assert end.y == 400

        # Verify Point is hashable and can be used in sets/dicts
        points = {start, end}
        assert len(points) == 2

    def test_screen_size_calculation(self):
        """Test that screen size is correctly calculated from pixels and scale."""
        test_cases = [
            # (pixels, scale, expected_points)
            ((1080, 1920), 2.0, (540, 960)),
            ((1242, 2688), 3.0, (414, 896)),
            ((750, 1334), 2.0, (375, 667)),
        ]

        for pixels, scale, expected_points in test_cases:
            converter = CoordinateConverter(pixels, scale)
            assert converter.screen_size_points == expected_points

    def test_round_trip_conversion(self):
        """Test that converting pixels -> points -> pixels gives the same value."""
        converter = CoordinateConverter((1080, 1920), scale_factor=2.0)

        # Start with a pixel value
        original_px = 500

        # Convert to points and back
        pt = converter.pixel_to_point(original_px)
        back_to_px = converter.point_to_pixel(pt)

        # Should get back to original (allowing for rounding)
        assert back_to_px == original_px

    def test_multiple_devices_independence(self):
        """Test that multiple CoordinateConverter instances don't interfere."""
        converter_2x = CoordinateConverter((1080, 1920), scale_factor=2.0)
        converter_3x = CoordinateConverter((1242, 2688), scale_factor=3.0)

        # Tap at same logical location (100 points) on both devices
        x_px_2x = converter_2x.point_to_pixel(100)
        x_px_3x = converter_3x.point_to_pixel(100)

        # Should give different pixel coordinates
        assert x_px_2x == 200  # 100 * 2.0
        assert x_px_3x == 300  # 100 * 3.0
        assert x_px_2x != x_px_3x

    def test_edge_coordinates(self):
        """Test coordinate conversion at screen edges."""
        converter = CoordinateConverter((1080, 1920), scale_factor=2.0)

        # Top-left corner
        assert converter.pixel_to_point(0) == 0
        assert converter.point_to_pixel(0) == 0

        # Bottom-right corner
        assert converter.pixel_to_point(1080) == 540
        assert converter.pixel_to_point(1920) == 960

        # Verify screen size
        w_pt, h_pt = converter.screen_size_points
        assert w_pt == 540
        assert h_pt == 960

    def test_fractional_coordinate_rounding(self):
        """Test that fractional coordinates are properly rounded to integers."""
        converter = CoordinateConverter((1080, 1920), scale_factor=2.0)

        # Odd pixel values that result in fractional points
        assert converter.pixel_to_point(1) == 0  # 0.5 rounds to 0
        assert converter.pixel_to_point(3) == 1  # 1.5 rounds to 1 (banker's rounding in Python 3)
        assert converter.pixel_to_point(99) == 49  # 49.5 rounds to 49

        # Verify that close values don't map to same point
        # (to ensure we can tap on different elements)
        px_values = [99, 100, 101, 102, 103]
        pt_values = [converter.pixel_to_point(px) for px in px_values]
        # Some may map to same point due to rounding, but not all
        assert len(set(pt_values)) > 1
