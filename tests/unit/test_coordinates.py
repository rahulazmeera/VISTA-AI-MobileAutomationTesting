"""Tests for coordinate conversion and scale factor handling."""

import pytest

from vista.driver.coordinates import CoordinateConverter


@pytest.mark.unit
class TestCoordinateConverter:
    """Test pixel ↔ point coordinate conversion for various devices."""

    def test_retina_2x_scale_factor(self):
        """Test iPhone with 2x Retina display (e.g., iPhone 8, XS, 11)."""
        # iPhone 8: 750x1334 points = 1500x2668 pixels (2x)
        converter = CoordinateConverter((1500, 2668), scale_factor=2.0)

        assert converter.screen_size_points == (750, 1334)
        assert converter.scale_factor == 2.0

        # Pixel to point
        assert converter.pixel_to_point(100) == 50
        assert converter.pixel_to_point(1000) == 500

        # Point to pixel
        assert converter.point_to_pixel(50) == 100
        assert converter.point_to_pixel(500) == 1000

    def test_non_retina_1x_scale_factor(self):
        """Test hypothetical non-Retina display with 1x scale."""
        converter = CoordinateConverter((375, 667), scale_factor=1.0)

        assert converter.screen_size_points == (375, 667)
        assert converter.scale_factor == 1.0

        # Pixel to point should be identity
        assert converter.pixel_to_point(100) == 100
        assert converter.point_to_pixel(100) == 100

    def test_three_x_scale_factor(self):
        """Test newer iPhones with 3x scale factor (e.g., iPhone 11 Pro Max)."""
        # iPhone 11 Pro Max: 414x896 points = 1242x2688 pixels (3x)
        converter = CoordinateConverter((1242, 2688), scale_factor=3.0)

        assert converter.screen_size_points == (414, 896)
        assert converter.scale_factor == 3.0

        # Pixel to point
        assert converter.pixel_to_point(300) == 100
        assert converter.pixel_to_point(1242) == 414

        # Point to pixel
        assert converter.point_to_pixel(100) == 300
        assert converter.point_to_pixel(414) == 1242

    def test_rectangle_conversion_retina(self):
        """Test converting a bounding box from pixels to points (2x Retina)."""
        converter = CoordinateConverter((1080, 1920), scale_factor=2.0)

        # Bounding box at (100, 200) with size 200x100 pixels
        x_pt, y_pt, w_pt, h_pt = converter.pixel_rect_to_point_rect(100, 200, 200, 100)

        assert x_pt == 50  # 100 / 2
        assert y_pt == 100  # 200 / 2
        assert w_pt == 100  # 200 / 2
        assert h_pt == 50  # 100 / 2

    def test_rectangle_conversion_3x(self):
        """Test converting a bounding box from pixels to points (3x scale)."""
        converter = CoordinateConverter((1242, 2688), scale_factor=3.0)

        # Bounding box at (300, 600) with size 300x150 pixels
        x_pt, y_pt, w_pt, h_pt = converter.pixel_rect_to_point_rect(300, 600, 300, 150)

        assert x_pt == 100  # 300 / 3
        assert y_pt == 200  # 600 / 3
        assert w_pt == 100  # 300 / 3
        assert h_pt == 50  # 150 / 3

    def test_rounding_precision(self):
        """Test that fractional coordinates are properly rounded."""
        converter = CoordinateConverter((1080, 1920), scale_factor=2.0)

        # Odd pixel values that result in fractional points
        # 99 pixels / 2.0 = 49.5, rounded to 49
        assert converter.pixel_to_point(99) == 49

        # 101 pixels / 2.0 = 50.5, rounded to 50
        assert converter.pixel_to_point(101) == 50

        # 199 pixels / 2.0 = 99.5, rounded to 99
        assert converter.pixel_to_point(199) == 99

    def test_corner_coordinates(self):
        """Test conversion of screen corner coordinates."""
        converter = CoordinateConverter((1080, 1920), scale_factor=2.0)
        w_pt, h_pt = converter.screen_size_points

        # Top-left corner (0, 0)
        assert converter.pixel_to_point(0) == 0
        assert converter.pixel_to_point(0) == 0

        # Bottom-right corner
        assert converter.pixel_to_point(1080) == 540
        assert converter.pixel_to_point(1920) == 960

        # Verify symmetry
        assert converter.point_to_pixel(540) == 1080
        assert converter.point_to_pixel(960) == 1920

    def test_center_coordinate(self):
        """Test converting the center coordinate."""
        converter = CoordinateConverter((1080, 1920), scale_factor=2.0)

        # Screen center
        w_pt, h_pt = converter.screen_size_points
        center_x_pt = w_pt // 2
        center_y_pt = h_pt // 2

        # Convert to pixels and back
        center_x_px = converter.point_to_pixel(center_x_pt)
        center_y_px = converter.point_to_pixel(center_y_pt)

        assert converter.pixel_to_point(center_x_px) == center_x_pt
        assert converter.pixel_to_point(center_y_px) == center_y_pt

    def test_known_iphone_models(self):
        """Test coordinate conversion for known iPhone models."""
        test_cases = [
            # (screen_pixels, scale_factor, expected_points)
            ((750, 1334), 2.0, (375, 667)),  # iPhone 8
            ((1080, 1920), 2.0, (540, 960)),  # iPhone XS Max
            ((828, 1792), 2.0, (414, 896)),  # iPhone 11
            ((1170, 2532), 3.0, (390, 844)),  # iPhone 12/13
            ((1284, 2778), 3.0, (428, 926)),  # iPhone 12/13 Pro Max
        ]

        for pixels, scale, expected_points in test_cases:
            converter = CoordinateConverter(pixels, scale)
            assert converter.screen_size_points == expected_points, (
                f"Failed for {pixels}px at {scale}x scale: "
                f"expected {expected_points}, got {converter.screen_size_points}"
            )
