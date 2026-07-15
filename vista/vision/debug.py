"""Visual debugging tools — overlay detected elements on screenshots."""

import logging
from typing import List, Optional, Tuple

from PIL import ImageDraw, ImageFont
from PIL.Image import Image

from vista.vision.elements import IconElement, TextElement

logger = logging.getLogger(__name__)

# Color scheme for overlays
COLORS = {
    "text_box": (0, 255, 0),  # Green for text bounding boxes
    "text_label": (0, 200, 0),  # Darker green for text labels
    "icon_box": (0, 0, 255),  # Blue for icon bounding boxes
    "icon_label": (0, 0, 200),  # Darker blue for icon labels
    "background": (255, 255, 255),  # White background for labels
}


def draw_text_elements(
    image: Image,
    text_elements: List[TextElement],
    confidence_threshold: float = 0.0,
    show_confidence: bool = True,
) -> Image:
    """
    Draw bounding boxes for detected text elements on the image.

    Args:
        image: The original screenshot (PIL Image).
        text_elements: List of detected TextElement objects.
        confidence_threshold: Only draw elements with confidence >= threshold.
        show_confidence: Whether to show confidence scores in labels.

    Returns:
        A new PIL Image with text bounding boxes drawn.
    """
    # Make a copy to avoid modifying the original
    result = image.copy()
    draw = ImageDraw.Draw(result)

    # Try to load a small font for labels, fall back to default if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except (IOError, OSError):
        font = ImageFont.load_default()

    for elem in text_elements:
        if elem.confidence < confidence_threshold:
            continue

        # Draw bounding box
        bbox = elem.bbox
        x1, y1 = bbox.x, bbox.y
        x2, y2 = bbox.x + bbox.width, bbox.y + bbox.height

        # Draw rectangle border
        draw.rectangle([x1, y1, x2, y2], outline=COLORS["text_box"], width=2)

        # Draw label with text and confidence
        label = elem.text
        if show_confidence:
            label += f" ({elem.confidence:.2f})"

        # Draw label background
        label_bbox = draw.textbbox((x1, max(0, y1 - 20)), label, font=font)
        draw.rectangle(label_bbox, fill=COLORS["text_label"])

        # Draw text label
        draw.text((x1, max(0, y1 - 20)), label, fill=(255, 255, 255), font=font)

    logger.info(f"Drew {len(text_elements)} text elements on image")
    return result


def draw_icon_elements(
    image: Image,
    icon_elements: List[IconElement],
    confidence_threshold: float = 0.0,
    show_confidence: bool = True,
) -> Image:
    """
    Draw bounding boxes for detected icon elements on the image.

    Args:
        image: The original screenshot (PIL Image).
        icon_elements: List of detected IconElement objects.
        confidence_threshold: Only draw elements with confidence >= threshold.
        show_confidence: Whether to show confidence scores in labels.

    Returns:
        A new PIL Image with icon bounding boxes drawn.
    """
    # Make a copy to avoid modifying the original
    result = image.copy()
    draw = ImageDraw.Draw(result)

    # Try to load a small font for labels
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    except (IOError, OSError):
        font = ImageFont.load_default()

    for elem in icon_elements:
        if elem.confidence < confidence_threshold:
            continue

        # Draw bounding box with dashed style (simulated with dots)
        bbox = elem.bbox
        x1, y1 = bbox.x, bbox.y
        x2, y2 = bbox.x + bbox.width, bbox.y + bbox.height

        # Draw rectangle border (blue for icons)
        draw.rectangle([x1, y1, x2, y2], outline=COLORS["icon_box"], width=2)

        # Draw label
        label = f"Icon: {elem.icon_id}"
        if show_confidence:
            label += f" ({elem.confidence:.2f})"

        # Draw label background
        label_bbox = draw.textbbox((x1, max(0, y1 - 20)), label, font=font)
        draw.rectangle(label_bbox, fill=COLORS["icon_label"])

        # Draw text label
        draw.text((x1, max(0, y1 - 20)), label, fill=(255, 255, 255), font=font)

    logger.info(f"Drew {len(icon_elements)} icon elements on image")
    return result


def draw_all_elements(
    image: Image,
    text_elements: List[TextElement],
    icon_elements: List[IconElement],
    confidence_threshold: float = 0.0,
    show_confidence: bool = True,
) -> Image:
    """
    Draw all detected elements (text and icons) on the image.

    Args:
        image: The original screenshot (PIL Image).
        text_elements: List of detected TextElement objects.
        icon_elements: List of detected IconElement objects.
        confidence_threshold: Only draw elements with confidence >= threshold.
        show_confidence: Whether to show confidence scores in labels.

    Returns:
        A new PIL Image with all bounding boxes drawn.
    """
    # Draw text elements first (so icons are on top)
    result = draw_text_elements(image, text_elements, confidence_threshold, show_confidence)
    result = draw_icon_elements(result, icon_elements, confidence_threshold, show_confidence)

    logger.info(
        f"Drew {len(text_elements)} text + {len(icon_elements)} icon elements"
    )
    return result


def add_grid(image: Image, grid_size: int = 50) -> Image:
    """
    Add a debug grid overlay to the image (helpful for coordinate visualization).

    Args:
        image: The original screenshot (PIL Image).
        grid_size: Size of grid cells in pixels.

    Returns:
        A new PIL Image with grid overlay.
    """
    result = image.copy()
    draw = ImageDraw.Draw(result, "RGBA")

    width, height = image.size
    grid_color = (100, 100, 100, 50)  # Semi-transparent gray

    # Draw vertical lines
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)

    # Draw horizontal lines
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    logger.info(f"Added debug grid (size={grid_size}px) to image")
    return result
