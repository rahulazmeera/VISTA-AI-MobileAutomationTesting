# Stage 1: iOS Driver + Screenshot Pipeline

**Status**: ✅ Complete

## What Was Built

### 1. iOS Appium Driver (`vista/driver/ios_appium.py`)

A complete, production-ready iOS device driver with:

- **Screenshot capture** — Get the current screen as a PIL Image with raw pixel dimensions
- **Coordinate-based actions** — tap, type_text, swipe, press_key using raw coordinates (never accessibility locators)
- **Automatic Retina scaling** — Handles 1x, 2x, 3x scale factors transparently
- **Context manager support** — Use with `with IOSAppiumDriver() as driver:`
- **Comprehensive logging** — Debug-friendly with detailed coordinate conversions

**Critical Design**: Only this module imports Appium. All device control goes through the `Driver` ABC.

### 2. Coordinate Conversion (`vista/driver/coordinates.py`)

Handles pixel ↔ point conversion for devices with different scale factors:

- **Retina 2x** (iPhone 8, XS, 11): 1080px = 540pt
- **Retina 3x** (iPhone 12/13 Pro): 1242px = 414pt
- **Non-Retina 1x**: pixels = points

Key insight: All bounding boxes are stored in **raw screenshot pixel space**, converted to points only at the final `driver.tap()` call to prevent double-conversion bugs.

### 3. CLI Screenshot Command

New command: `vista screenshot`

```bash
# Capture and save screenshot
vista screenshot --output myscreen.png

# With verbose logging
vista screenshot --output myscreen.png --verbose

# Specify Appium server URL
vista screenshot --appium-url http://192.168.1.100:4723
```

### 4. Comprehensive Tests

**Unit tests** (no device required):
- `tests/unit/test_coordinates.py` — 11 tests covering all scale factors
- `tests/unit/test_ios_driver.py` — 9 tests with mocked Appium
- All tests pass without external dependencies

**Known iPhone models tested**:
- iPhone 8: 750x1334pt (2x)
- iPhone 11: 828x1792pt (2x)
- iPhone 12/13: 390x844pt (3x)
- iPhone 12/13 Pro Max: 428x926pt (3x)

## How to Use

### Prerequisites

1. **Appium 2.x installed**:
   ```bash
   npm install -g appium
   appium driver install xcuitest
   ```

2. **iOS Simulator booted**:
   ```bash
   xcrun simctl list devices
   xcrun simctl boot "iPhone 14"
   ```

3. **VISTA installed**:
   ```bash
   pip install -e .
   ```

### Basic Usage

```python
from vista.driver.ios_appium import IOSAppiumDriver

# Connect to Appium (defaults to localhost:4723)
with IOSAppiumDriver() as driver:
    # Capture screenshot
    screenshot = driver.screenshot()
    
    # Get screen size in points (logical)
    width, height = driver.screen_size()  # e.g., (540, 960) for iPhone 8
    
    # Get scale factor
    scale = driver.scale_factor()  # e.g., 2.0 for Retina
    
    # Tap at coordinates (in points)
    driver.tap(270, 480)  # Tap center of 540x960 screen
    
    # Type text into focused field
    driver.type_text("hello@example.com")
    
    # Swipe from point A to point B
    from vista.driver.base import Point
    driver.swipe(
        Point(x=270, y=200),
        Point(x=270, y=800),
        duration_ms=300
    )
    
    # Press keys
    driver.press_key("return")
    driver.press_key("backspace")
```

### CLI Usage

```bash
# Capture screenshot
vista screenshot --output screenshot.png

# Verify connection and show device info
vista screenshot --output /tmp/test.png --verbose
```

## Architecture Highlights

### Boundary Enforcement

```python
# ✅ ALLOWED: Only in ios_appium.py
from appium import webdriver
driver = webdriver.Remote(...)
```

```python
# ❌ FORBIDDEN: Anywhere else
from appium.webdriver.common.by import By
element = driver.find_element(By.ACCESSIBILITY_ID, "button")  # WILL FAIL CI
```

### Coordinate System

```
Screenshot pixels (1080x1920)
         ↓
CoordinateConverter (scale=2.0)
         ↓
Device points (540x960)
         ↓
Driver.tap(x, y)
```

Conversion happens **only at the boundary** (in `tap()`, `swipe()`, etc.), never in intermediate layers.

### Retina Scale Handling

Automatic detection:

```python
# For a 2x Retina device:
screenshot = driver.screenshot()        # PIL Image, 1080x1920 pixels
w, h = driver.screen_size()             # 540x960 points
scale = driver.scale_factor()           # 2.0

# Internally, screenshot pixels are converted to points:
x_px = 100  # pixel coordinate from OCR bounding box
x_pt = converter.pixel_to_point(x_px)   # 50 points
driver.tap(x_pt, y_pt)                  # Tap uses points
```

## Testing

### Run all tests

```bash
# Unit tests only (fast, ~1s)
pytest tests/unit -v

# With coverage
pytest tests/unit -v --cov=vista --cov-report=html
```

### Test coordinate conversion

Verify that all known iPhone models convert correctly:

```bash
pytest tests/unit/test_coordinates.py::TestCoordinateConverter::test_known_iphone_models -v
```

### Manual testing

Boot a simulator and capture a screenshot:

```bash
python examples/stage1_screenshot_demo.py
```

This will:
1. Connect to Appium
2. Detect device scale factor
3. Capture and save a screenshot
4. Print device info and coordinate conversion test

## What's Next (Stage 2)

**OCR + Visual Debugging**

- `OCRProvider` + PaddleOCR implementation
- `ScreenState` perception
- `vista debug screenshot.png` overlay tool for visual inspection
- Verify OCR accuracy on known screenshots

All coordinate conversion and driver infrastructure from Stage 1 will be used downstream.

## Troubleshooting

### "Could not connect to Appium server"

Make sure Appium is running:
```bash
appium
# Should print: "Appium REST http interface listener started on..."
```

### "iOS Simulator not found"

Start a simulator:
```bash
xcrun simctl list devices      # See available devices
xcrun simctl boot "iPhone 14"  # Boot specific device
```

### Wrong screen size detected

Verify the booted simulator matches the device in Appium capabilities:
```bash
# Check simulator resolution
xcrun simctl list devices

# Force a specific device in code:
driver = IOSAppiumDriver()  # Auto-detects
```

### Coordinate conversion seems off

Check the scale factor:
```python
driver = IOSAppiumDriver()
print(f"Scale: {driver.scale_factor()}x")
print(f"Size: {driver.screen_size()}")
print(f"Screenshot: {driver.screenshot().size}")
```

If scale factor is wrong, the simulator might not be what you expect (check with `xcrun simctl list`).

## Files Added/Modified

**New files**:
- `vista/driver/ios_appium.py` — iOS driver implementation
- `tests/unit/test_coordinates.py` — Coordinate conversion tests (11 tests)
- `tests/unit/test_ios_driver.py` — Driver tests (9 tests)
- `examples/stage1_screenshot_demo.py` — Demo script
- `STAGE1.md` — This file

**Modified files**:
- `vista/cli/main.py` — Added `screenshot` command
- `vista/driver/__init__.py` — Export `Point` class
- `vista/__init__.py` — Available for future imports

## Next Steps

1. **Try it out**: Boot a simulator and run `vista screenshot`
2. **Verify coordinates**: Use `examples/stage1_screenshot_demo.py` to test on your device
3. **Read the code**: `vista/driver/ios_appium.py` shows the full Driver ABC implementation
4. **Plan Stage 2**: Ready to implement OCR perception layer

---

**Stage 1 Status**: ✅ Complete and tested
