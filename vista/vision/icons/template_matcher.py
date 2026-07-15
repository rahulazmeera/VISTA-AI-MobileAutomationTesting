"""Icon detection using OpenCV template matching."""

import logging
from typing import Dict, List, Optional

import cv2
import numpy as np
from PIL.Image import Image

from vista.vision.elements import BBox, IconElement
from vista.vision.icons.base import IconCatalog, IconDetector

logger = logging.getLogger(__name__)


class TemplateMatchingDetector(IconDetector):
    """
    Detect icons by template matching against a reference catalog.

    Uses OpenCV's `cv2.matchTemplate()` with multi-scale pyramid to handle
    different icon sizes (e.g., Retina vs non-Retina).
    """

    def __init__(self, match_threshold: float = 0.7):
        """
        Initialize the template matcher.

        Args:
            match_threshold: Minimum correlation score (0.0-1.0) for a match.
                           Default 0.7 is good for exact template matching.
        """
        if not 0.0 <= match_threshold <= 1.0:
            raise ValueError(f"Threshold must be 0.0-1.0, got {match_threshold}")

        self.match_threshold = match_threshold
        logger.info(f"TemplateMatchingDetector initialized (threshold={match_threshold})")

    def detect_icons(
        self,
        image: Image,
        catalog: Optional[IconCatalog] = None,
    ) -> List[IconElement]:
        """
        Detect all icons in an image by matching against catalog templates.

        Args:
            image: A PIL Image to analyze (RGB or RGBA mode).
            catalog: IconCatalog with reference template images for known icons.

        Returns:
            A list of IconElement objects with bounding boxes and confidence scores.
            Bounding boxes are in screenshot pixel coordinates.
        """
        if catalog is None or len(catalog.icons) == 0:
            logger.debug("No icon catalog provided, skipping icon detection")
            return []

        logger.debug(f"Running template matching with {len(catalog.icons)} templates")

        # Convert PIL Image to numpy array for OpenCV
        image_array = np.array(image.convert("RGB"))

        detected_icons = []

        # Try matching each template in the catalog
        for icon_id, template_image in catalog.icons.items():
            matches = self._match_template(
                image_array,
                np.array(template_image.convert("RGB")),
                icon_id,
            )
            detected_icons.extend(matches)

        # Remove duplicate/overlapping detections
        detected_icons = self._filter_overlapping(detected_icons)

        logger.info(f"Detected {len(detected_icons)} icons")
        return detected_icons

    def _match_template(
        self,
        image: np.ndarray,
        template: np.ndarray,
        icon_id: str,
    ) -> List[IconElement]:
        """
        Match a template against an image using multi-scale pyramid.

        Args:
            image: The screenshot as numpy array.
            template: The reference template as numpy array.
            icon_id: The icon identifier.

        Returns:
            List of IconElement matches.
        """
        matches = []

        # Try multiple scales to handle Retina/non-Retina differences
        template_height, template_width = template.shape[:2]
        image_height, image_width = image.shape[:2]

        # Scale range: 0.5x to 2.0x template size
        for scale in np.linspace(0.5, 2.0, num=8):
            scaled_template = cv2.resize(
                template,
                (int(template_width * scale), int(template_height * scale)),
                interpolation=cv2.INTER_LINEAR,
            )

            scaled_temp_h, scaled_temp_w = scaled_template.shape[:2]

            # Skip if template is larger than image
            if scaled_temp_h > image_height or scaled_temp_w > image_width:
                continue

            # Match template
            result = cv2.matchTemplate(image, scaled_template, cv2.TM_CCOEFF_NORMED)

            # Find matches above threshold
            match_locs = np.where(result >= self.match_threshold)

            for y, x in zip(match_locs[0], match_locs[1]):
                confidence = float(result[y, x])

                bbox = BBox(
                    x=x,
                    y=y,
                    width=scaled_temp_w,
                    height=scaled_temp_h,
                )

                icon_elem = IconElement(
                    icon_id=icon_id,
                    bbox=bbox,
                    confidence=confidence,
                )

                matches.append(icon_elem)
                logger.debug(
                    f"Template match: {icon_id} at ({x}, {y}) "
                    f"{scaled_temp_w}x{scaled_temp_h}, confidence={confidence:.2f}"
                )

        return matches

    @staticmethod
    def _filter_overlapping(
        elements: List[IconElement],
        iou_threshold: float = 0.3,
    ) -> List[IconElement]:
        """
        Remove overlapping detections, keeping highest confidence.

        Args:
            elements: List of detected elements.
            iou_threshold: IoU (Intersection over Union) threshold for overlap.

        Returns:
            Filtered list with non-overlapping elements.
        """
        if not elements:
            return elements

        # Sort by confidence descending
        sorted_elems = sorted(elements, key=lambda e: e.confidence, reverse=True)

        filtered = []
        for elem in sorted_elems:
            # Check if overlaps with already-selected elements
            overlaps = False
            for selected in filtered:
                iou = TemplateMatchingDetector._compute_iou(elem.bbox, selected.bbox)
                if iou > iou_threshold:
                    overlaps = True
                    break

            if not overlaps:
                filtered.append(elem)

        return filtered

    @staticmethod
    def _compute_iou(bbox1: BBox, bbox2: BBox) -> float:
        """Compute Intersection over Union of two bounding boxes."""
        # Intersection
        x_inter_min = max(bbox1.x, bbox2.x)
        y_inter_min = max(bbox1.y, bbox2.y)
        x_inter_max = min(bbox1.x + bbox1.width, bbox2.x + bbox2.width)
        y_inter_max = min(bbox1.y + bbox1.height, bbox2.y + bbox2.height)

        if x_inter_max < x_inter_min or y_inter_max < y_inter_min:
            return 0.0  # No intersection

        inter_area = (x_inter_max - x_inter_min) * (y_inter_max - y_inter_min)

        # Union
        area1 = bbox1.width * bbox1.height
        area2 = bbox2.width * bbox2.height
        union_area = area1 + area2 - inter_area

        return inter_area / union_area if union_area > 0 else 0.0
