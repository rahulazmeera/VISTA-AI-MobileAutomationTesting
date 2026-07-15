"""Icon detector abstract base class."""

from abc import ABC, abstractmethod
from typing import List, Optional

from PIL.Image import Image

from vista.vision.elements import IconElement


class IconCatalog:
    """A catalog of reference images for known icons."""

    def __init__(self):
        self.icons: dict[str, Image] = {}

    def add(self, icon_id: str, image: Image) -> None:
        """Add a reference image for an icon."""
        self.icons[icon_id] = image

    def get(self, icon_id: str) -> Optional[Image]:
        """Get a reference image for an icon."""
        return self.icons.get(icon_id)

    def __contains__(self, icon_id: str) -> bool:
        """Check if an icon is in the catalog."""
        return icon_id in self.icons


class IconDetector(ABC):
    """
    Abstract base class for icon detection providers.

    Pluggable implementations (template matching, ML-based, embedding-based)
    can be swapped via the provider registry in config.py.
    """

    @abstractmethod
    def detect_icons(
        self, image: Image, catalog: Optional[IconCatalog] = None
    ) -> List[IconElement]:
        """
        Detect all icons in an image.

        Args:
            image: A PIL Image to analyze. Should be in RGB or RGBA mode.
            catalog: Optional IconCatalog with reference images for known icons.
                     If provided, the detector may use it for template matching or similarity.

        Returns:
            A list of IconElement objects with bounding boxes and confidence scores.
            Bounding boxes are in screenshot pixel coordinates.
        """
        pass
