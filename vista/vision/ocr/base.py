"""OCR provider abstract base class."""

from abc import ABC, abstractmethod
from typing import List

from PIL.Image import Image

from vista.vision.elements import TextElement


class OCRProvider(ABC):
    """
    Abstract base class for OCR providers.

    Pluggable implementations (PaddleOCR, EasyOCR, cloud APIs) can be swapped
    via the provider registry in config.py.
    """

    @abstractmethod
    def detect_text(self, image: Image) -> List[TextElement]:
        """
        Detect all text in an image.

        Args:
            image: A PIL Image to analyze. Should be in RGB or RGBA mode.

        Returns:
            A list of TextElement objects with bounding boxes and confidence scores.
            Bounding boxes are in screenshot pixel coordinates.
        """
        pass
