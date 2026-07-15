"""
Coordinate conversion utilities.

Handles pixel↔point conversion for devices with different scale factors (Retina, 2x, 3x, etc.).
This is a high-risk area for bugs — bounding boxes are stored in raw screenshot-pixel space,
then converted to points only at the final driver.tap() call site to prevent double-conversion.
"""

from typing import Tuple

from PIL.Image import Image


class CoordinateConverter:
    """Converts between screenshot pixels and device points."""

    def __init__(self, screenshot_size: Tuple[int, int], scale_factor: float):
        """
        Initialize the converter.

        Args:
            screenshot_size: Size of the screenshot in pixels (width, height).
            scale_factor: Device scale factor (pixels per point). E.g., 2.0 for Retina.
        """
        self.screenshot_width_px = screenshot_size[0]
        self.screenshot_height_px = screenshot_size[1]
        self.scale_factor = scale_factor

    @property
    def screen_size_points(self) -> Tuple[int, int]:
        """Get the logical screen size in points."""
        return (
            int(self.screenshot_width_px / self.scale_factor),
            int(self.screenshot_height_px / self.scale_factor),
        )

    def pixel_to_point(self, px: int) -> int:
        """Convert a pixel coordinate to points."""
        return int(px / self.scale_factor)

    def point_to_pixel(self, pt: int) -> int:
        """Convert a point coordinate to pixels."""
        return int(pt * self.scale_factor)

    def pixel_rect_to_point_rect(
        self, x_px: int, y_px: int, w_px: int, h_px: int
    ) -> Tuple[int, int, int, int]:
        """
        Convert a bounding box from pixels to points.

        Args:
            x_px, y_px: Top-left corner in pixels.
            w_px, h_px: Width and height in pixels.

        Returns:
            A tuple of (x_pt, y_pt, w_pt, h_pt) in points.
        """
        return (
            self.pixel_to_point(x_px),
            self.pixel_to_point(y_px),
            self.pixel_to_point(w_px),
            self.pixel_to_point(h_px),
        )


def create_converter_from_image(
    image: Image, scale_factor: float
) -> CoordinateConverter:
    """
    Create a converter from a PIL Image and scale factor.

    Args:
        image: The screenshot image.
        scale_factor: Device scale factor.

    Returns:
        A CoordinateConverter instance.
    """
    return CoordinateConverter(image.size, scale_factor)
