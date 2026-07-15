"""EasyOCR provider — pluggable alternative to PaddleOCR."""

import logging
from typing import List

from PIL.Image import Image

from vista.vision.elements import BBox, TextElement
from vista.vision.ocr.base import OCRProvider

logger = logging.getLogger(__name__)


class EasyOCRProvider(OCRProvider):
    """
    OCR provider using EasyOCR.

    Good accuracy with easier installation (pure PyTorch, better Apple Silicon support).
    Recommended alternative when PaddleOCR has installation issues.
    """

    def __init__(self, use_gpu: bool = False, lang_list: List[str] = None):
        """
        Initialize EasyOCR.

        Args:
            use_gpu: Whether to use GPU (if available).
            lang_list: Languages to recognize (default: ['en']).
                       Can include multiple languages like ['en', 'zh'].
        """
        try:
            import easyocr
        except ImportError as e:
            raise ImportError(
                "easyocr is required. Install with: pip install easyocr"
            ) from e

        if lang_list is None:
            lang_list = ["en"]

        logger.info(f"Initializing EasyOCR (gpu={use_gpu}, languages={lang_list})")
        self._reader = easyocr.Reader(lang_list, gpu=use_gpu)
        logger.info("EasyOCR initialized successfully")

    def detect_text(self, image: Image) -> List[TextElement]:
        """
        Detect all text in an image using EasyOCR.

        Args:
            image: A PIL Image to analyze (RGB or RGBA mode).

        Returns:
            A list of TextElement objects with bounding boxes and confidence scores.
            Bounding boxes are in screenshot pixel coordinates.
        """
        logger.debug(f"Running EasyOCR on image {image.size}")

        # Convert PIL Image to numpy array for EasyOCR
        import numpy as np

        image_array = np.array(image)

        # Run OCR
        # EasyOCR returns: [([x1,y1], [x2,y2], [x3,y3], [x4,y4]), 'text', confidence]
        results = self._reader.readtext(image_array, detail=1)

        text_elements = []

        # Process results
        for result in results:
            # Extract coordinates and text
            coords = result[0]  # List of 4 corner points
            text = result[1]
            confidence = result[2]

            # Convert coordinates to bounding box
            xs = [int(pt[0]) for pt in coords]
            ys = [int(pt[1]) for pt in coords]

            x_min = min(xs)
            y_min = min(ys)
            x_max = max(xs)
            y_max = max(ys)

            # Convert to BBox (x, y, width, height format)
            width = x_max - x_min
            height = y_max - y_min

            bbox = BBox(x=x_min, y=y_min, width=width, height=height)

            elem = TextElement(
                text=text.strip(),
                bbox=bbox,
                confidence=float(confidence),
            )

            text_elements.append(elem)
            logger.debug(
                f"Detected text: '{text}' at ({x_min}, {y_min}) "
                f"{width}x{height}, confidence={confidence:.2f}"
            )

        logger.info(f"Detected {len(text_elements)} text elements")
        return text_elements
