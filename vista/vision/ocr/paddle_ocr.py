"""PaddleOCR provider — default OCR backend for VISTA."""

import logging
from typing import List

from PIL.Image import Image

from vista.vision.elements import BBox, TextElement
from vista.vision.ocr.base import OCRProvider

logger = logging.getLogger(__name__)


class PaddleOCRProvider(OCRProvider):
    """
    OCR provider using PaddleOCR.

    Best accuracy on small/varied UI text (compared to EasyOCR/Tesseract).
    Default backend for VISTA.
    """

    def __init__(self, use_gpu: bool = False, lang: str = "en"):
        """
        Initialize PaddleOCR.

        Args:
            use_gpu: Whether to use GPU (if available).
            lang: Language(s) to recognize (default: English).
                  Can be a list like ['en', 'ch'] for multi-lingual.
        """
        try:
            from paddleocr import PaddleOCR
        except ImportError as e:
            raise ImportError(
                "paddleocr is required. Install with: pip install paddleocr"
            ) from e

        logger.info(f"Initializing PaddleOCR (gpu={use_gpu}, lang={lang})")
        self._ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=use_gpu)
        logger.info("PaddleOCR initialized successfully")

    def detect_text(self, image: Image) -> List[TextElement]:
        """
        Detect all text in an image using PaddleOCR.

        Args:
            image: A PIL Image to analyze (RGB or RGBA mode).

        Returns:
            A list of TextElement objects with bounding boxes and confidence scores.
            Bounding boxes are in screenshot pixel coordinates.
        """
        logger.debug(f"Running PaddleOCR on image {image.size}")

        # Convert PIL Image to numpy array for PaddleOCR
        import numpy as np

        image_array = np.array(image)

        # Run OCR
        # PaddleOCR returns: [[[x1,y1], [x2,y1], [x2,y2], [x1,y2]], ('text', confidence)], ...]
        results = self._ocr.ocr(image_array, cls=True)

        text_elements = []

        # Process results
        if results and results[0]:
            for line in results[0]:
                # Extract coordinates and text
                coords = line[0]  # [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                text, confidence = line[1]

                # Convert to bounding box (store as LTRB: left, top, right, bottom)
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
