"""
Stage 1 Demo: Capture a screenshot from an iOS simulator/device.

Prerequisites:
1. Appium server running: `appium`
2. iOS Simulator booted: `xcrun simctl boot "iPhone 14"`
3. VISTA installed: `pip install -e .`

Usage:
    python examples/stage1_screenshot_demo.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vista.driver.ios_appium import IOSAppiumDriver


def main():
    """Demonstrate Stage 1 iOS driver capabilities."""
    print("=" * 60)
    print("VISTA Stage 1: iOS Driver + Screenshot Pipeline")
    print("=" * 60)

    appium_url = "http://localhost:4723"
    output_path = Path("demo_screenshot.png")

    print(f"\nConnecting to Appium at {appium_url}...")
    try:
        with IOSAppiumDriver(remote_url=appium_url) as driver:
            print("✓ Connected to device/simulator\n")

            # Get device info
            w_pt, h_pt = driver.screen_size()
            scale = driver.scale_factor()

            print(f"Device Screen Size: {w_pt}x{h_pt} points (logical)")
            print(f"Pixel Scale Factor: {scale:.1f}x Retina\n")

            # Capture screenshot
            print("Capturing screenshot...")
            screenshot = driver.screenshot()

            # Get pixel size
            w_px, h_px = screenshot.size
            print(f"Screenshot Size: {w_px}x{h_px} pixels (raw)")
            print(f"Color Mode: {screenshot.mode}\n")

            # Save screenshot
            print(f"Saving to {output_path}...")
            screenshot.save(output_path)
            print(f"✓ Screenshot saved!\n")

            # Verify coordinate conversion
            print("Coordinate Conversion Test:")
            print(f"  100 pixels = {driver._converter.pixel_to_point(100)} points")
            print(f"  50 points = {driver._converter.point_to_pixel(50)} pixels")
            print(f"  Center point: ({w_pt//2}, {h_pt//2})")

    except ConnectionError as e:
        print(f"✗ Connection Error: {e}\n")
        print("Make sure:")
        print("  1. Appium is running: `appium`")
        print("  2. iOS Simulator is booted: `xcrun simctl boot 'iPhone 14'`")
        print("  3. Appium can connect to simulator")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("✓ Stage 1 Demo Complete!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
