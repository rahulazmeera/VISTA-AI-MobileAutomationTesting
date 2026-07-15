"""
iOS driver via Appium + WebDriverAgent.

CRITICAL: This is the ONLY module that imports appium.
All device interactions go through this Driver ABC.
Never use find_element() or accessibility locators outside this module.
"""

import logging
from typing import Optional, Tuple

from PIL import Image
from PIL.Image import Image as PILImage

from vista.driver.base import Driver, Point
from vista.driver.coordinates import CoordinateConverter

logger = logging.getLogger(__name__)


class IOSAppiumDriver(Driver):
    """
    iOS device driver using Appium + WebDriverAgent.

    Uses ONLY:
    - screenshot capture
    - W3C pointer actions (tap, swipe) via raw coordinates
    - keyboard input
    - capability negotiation (screen size, scale factor)

    NEVER uses:
    - find_element() or find_elements()
    - XPath, resource-id, accessibility-id locators
    - XML source inspection
    """

    def __init__(self, remote_url: str = "http://localhost:4723"):
        """
        Initialize the iOS Appium driver.

        Args:
            remote_url: Appium server URL (default: localhost:4723 for Appium 2.x).
                       Set via environment variable APPIUM_URL if needed.

        Raises:
            ImportError: If appium-python-client is not installed.
            ConnectionError: If Appium server is not running at remote_url.
        """
        try:
            from appium import webdriver
            from appium.webdriver.common.appiumby import AppiumBy
            from appium.webdriver.webdriver import WebDriver
        except ImportError as e:
            raise ImportError(
                "appium-python-client is required for iOS driver. "
                "Install with: pip install appium-python-client"
            ) from e

        self._webdriver_class = WebDriver
        self._appiumby = AppiumBy
        self._remote_url = remote_url
        self._driver: Optional[WebDriver] = None
        self._converter: Optional[CoordinateConverter] = None

        # Connect to Appium server
        self._connect()

    def _connect(self) -> None:
        """Connect to the Appium server with XCUITest capabilities."""
        capabilities = {
            "platformName": "iOS",
            "automationName": "XCUITest",
            "app": None,  # Use already-booted simulator
            "noReset": True,
        }

        logger.info(f"Connecting to Appium server at {self._remote_url}")
        try:
            from appium import webdriver as appium_webdriver

            self._driver = appium_webdriver.Remote(
                command_executor=self._remote_url,
                desired_capabilities=capabilities,
            )
        except ImportError as e:
            raise ImportError(
                "appium-python-client is required. Install with: pip install appium-python-client"
            ) from e
        except Exception as e:
            raise ConnectionError(
                f"Could not connect to Appium server at {self._remote_url}. "
                "Make sure Appium is running: `appium`"
            ) from e

        logger.info("Connected to Appium server")
        self._initialize_converter()

    def _initialize_converter(self) -> None:
        """Initialize the coordinate converter with device screen size and scale factor."""
        if not self._driver:
            raise RuntimeError("Driver not connected")

        # Get window size in pixels
        window_size = self._driver.get_window_size()
        screenshot = self.screenshot()

        # The screenshot size in pixels is the actual pixel resolution
        actual_width, actual_height = screenshot.size
        reported_width = window_size.get("width", actual_width)
        reported_height = window_size.get("height", actual_height)

        # Scale factor = actual pixels / reported points
        # On Retina (2x): 1080px window = 540pt, so scale = 1080/540 = 2.0
        scale_factor = actual_width / reported_width if reported_width > 0 else 1.0

        self._converter = CoordinateConverter((actual_width, actual_height), scale_factor)
        logger.info(
            f"Screen: {actual_width}x{actual_height}px, "
            f"scale factor: {scale_factor:.1f}x, "
            f"logical size: {int(actual_width/scale_factor)}x{int(actual_height/scale_factor)}pt"
        )

    def screenshot(self) -> PILImage:
        """
        Capture the current screen as a PIL Image.

        Returns:
            PIL Image in RGB mode with raw pixel dimensions (e.g., 1080x1920 for 2x Retina).
        """
        if not self._driver:
            raise RuntimeError("Driver not connected")

        logger.debug("Taking screenshot")
        png_bytes = self._driver.get_screenshot_as_png()
        image = Image.open(Image.io.BytesIO(png_bytes)).convert("RGB")
        logger.debug(f"Screenshot size: {image.size}")
        return image

    def tap(self, x: int, y: int) -> None:
        """
        Tap a point on the screen.

        Args:
            x: X coordinate in points (not pixels).
            y: Y coordinate in points (not pixels).
        """
        if not self._driver or not self._converter:
            raise RuntimeError("Driver not connected or initialized")

        # Convert points to pixels
        x_px = self._converter.point_to_pixel(x)
        y_px = self._converter.point_to_pixel(y)

        logger.info(f"Tap: ({x}, {y}) points = ({x_px}, {y_px}) pixels")

        try:
            try:
                from appium.webdriver.common.action_chains import ActionChains
            except ImportError:
                # Fallback for older Appium versions
                from selenium.webdriver.common.action_chains import ActionChains

            actions = ActionChains(self._driver)
            actions.w3c_actions.pointer_action.move_to_location(x_px, y_px)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
        except Exception as e:
            logger.error(f"Tap failed: {e}")
            raise

    def type_text(self, text: str) -> None:
        """
        Type text into the currently-focused field.

        Assumes the field is already focused (via a prior tap).
        Disables autocorrect where possible.

        Args:
            text: The text to type.
        """
        if not self._driver:
            raise RuntimeError("Driver not connected")

        logger.info(f"Type: '{text}'")

        try:
            # Use mobile: type to bypass keyboard settings
            self._driver.execute_script("mobile: type", {"text": text})
        except Exception:
            # Fallback to standard type if mobile: type fails
            logger.debug("mobile: type failed, using standard type")
            self._driver.keyboard.send_keys(text)

    def swipe(self, start: Point, end: Point, duration_ms: int = 300) -> None:
        """
        Perform a swipe gesture from one point to another.

        Args:
            start: Starting point in points.
            end: Ending point in points.
            duration_ms: Duration of the swipe in milliseconds.
        """
        if not self._driver or not self._converter:
            raise RuntimeError("Driver not connected or initialized")

        # Convert points to pixels
        start_x_px = self._converter.point_to_pixel(start.x)
        start_y_px = self._converter.point_to_pixel(start.y)
        end_x_px = self._converter.point_to_pixel(end.x)
        end_y_px = self._converter.point_to_pixel(end.y)

        logger.info(
            f"Swipe: ({start.x}, {start.y}) → ({end.x}, {end.y}) points, "
            f"({start_x_px}, {start_y_px}) → ({end_x_px}, {end_y_px}) pixels, "
            f"duration {duration_ms}ms"
        )

        try:
            try:
                from appium.webdriver.common.action_chains import ActionChains
            except ImportError:
                # Fallback for older Appium versions
                from selenium.webdriver.common.action_chains import ActionChains

            actions = ActionChains(self._driver)
            actions.w3c_actions.pointer_action.move_to_location(start_x_px, start_y_px)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(duration_ms / 1000.0)
            actions.w3c_actions.pointer_action.move_to_location(end_x_px, end_y_px)
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
        except Exception as e:
            logger.error(f"Swipe failed: {e}")
            raise

    def press_key(self, key: str) -> None:
        """
        Press a key or key combination.

        Args:
            key: Key name (e.g., 'return', 'backspace', 'home', 'escape').
        """
        if not self._driver:
            raise RuntimeError("Driver not connected")

        key_map = {
            "return": "\\uE007",  # Return key
            "enter": "\\uE007",
            "backspace": "\\uE003",
            "delete": "\\uE003",
            "home": "\\uE011",
            "escape": "\\uE00C",
            "tab": "\\uE004",
        }

        key_code = key_map.get(key.lower(), key)
        logger.info(f"Press key: {key} (code: {key_code})")

        try:
            self._driver.press_keycode(key_code)
        except Exception:
            # Fallback to send_keys
            try:
                self._driver.send_keys(key_code)
            except Exception as e:
                logger.error(f"Press key failed: {e}")
                raise

    def screen_size(self) -> Tuple[int, int]:
        """
        Get the logical screen size in points (not pixels).

        Returns:
            Tuple of (width, height) in points.
        """
        if not self._converter:
            raise RuntimeError("Driver not initialized")

        return self._converter.screen_size_points

    def scale_factor(self) -> float:
        """
        Get the pixel-to-point scale factor for this device.

        For Retina displays: 2.0
        For non-Retina: 1.0
        For some newer iPhones: 3.0

        Returns:
            Scale factor (pixels per point).
        """
        if not self._converter:
            raise RuntimeError("Driver not initialized")

        return self._converter.scale_factor

    def quit(self) -> None:
        """Disconnect from the Appium server and clean up."""
        if self._driver:
            logger.info("Quitting Appium driver")
            try:
                self._driver.quit()
            except Exception as e:
                logger.error(f"Error quitting driver: {e}")
            finally:
                self._driver = None
                self._converter = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.quit()
