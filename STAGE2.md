# Stage 2: OCR + Visual Debugging

**Status**: ✅ Complete

## What Was Built

### 1. OCR Providers

#### PaddleOCR (`vista/vision/ocr/paddle_ocr.py`)
- Default OCR backend for VISTA
- Best accuracy on small/varied UI text
- Supports multi-language recognition
- GPU-optional
- Detects text and returns TextElement objects with bounding boxes

#### EasyOCR (`vista/vision/ocr/easy_ocr.py`)
- Pluggable alternative to PaddleOCR
- Easier installation (PyTorch-based, better Apple Silicon support)
- Recommended fallback if PaddleOCR has issues
- Same interface as PaddleOCR for seamless swapping

### 2. Visual Debug Overlay Tools (`vista/vision/debug.py`)

Functions to visualize detected elements on screenshots:

- **`draw_text_elements()`** — Draw green bounding boxes around detected text
- **`draw_icon_elements()`** — Draw blue bounding boxes around icons
- **`draw_all_elements()`** — Combine text and icon overlays
- **`add_grid()`** — Add coordinate grid for debugging
- Confidence score display (optional)
- Threshold filtering to hide low-confidence detections

### 3. CLI Debug Command

New command: `vista debug`

```bash
# Basic usage
vista debug screenshot.png

# Save to specific output
vista debug screenshot.png --output debug_output.png

# Use EasyOCR instead of PaddleOCR
vista debug screenshot.png --ocr easy

# Add coordinate grid
vista debug screenshot.png --grid

# Filter by confidence (show only elements >= 0.8 confidence)
vista debug screenshot.png --confidence 0.8

# Verbose logging
vista debug screenshot.png --verbose
```

### 4. Test Coverage

**46 total unit tests** (all passing):
- 9 coordinate conversion tests
- 8 iOS driver logic tests
- 12 debug overlay visualization tests
- 9 OCR provider interface tests (mocked)
- 9 Stage 0 scaffold tests

**Test categories**:
- BBox coordinate conversion (PaddleOCR and EasyOCR formats)
- Text element detection logic
- Debug overlay generation with edge cases
- Confidence threshold filtering
- Grid overlay visualization

## How to Use

### Prerequisites

Install OCR libraries (choose at least one):

```bash
# PaddleOCR (default, best accuracy)
pip install paddleocr

# OR EasyOCR (easier install, good accuracy)
pip install easyocr
```

### Basic OCR Usage

```python
from vista.vision.ocr.paddle_ocr import PaddleOCRProvider
from PIL import Image

# Initialize OCR provider
ocr = PaddleOCRProvider(use_gpu=False)

# Load screenshot
image = Image.open("screenshot.png")

# Detect text
text_elements = ocr.detect_text(image)

# Use results
for elem in text_elements:
    print(f"Text: '{elem.text}'")
    print(f"  Position: ({elem.bbox.x}, {elem.bbox.y})")
    print(f"  Size: {elem.bbox.width}x{elem.bbox.height}")
    print(f"  Confidence: {elem.confidence:.2f}")
```

### Visual Debugging

```python
from vista.vision.debug import draw_all_elements
from vista.vision.ocr.paddle_ocr import PaddleOCRProvider
from PIL import Image

# Capture or load screenshot
image = Image.open("screenshot.png")

# Run OCR
ocr = PaddleOCRProvider()
text_elements = ocr.detect_text(image)
icon_elements = []  # Stage 4: icon detection

# Draw overlays
result = draw_all_elements(image, text_elements, icon_elements)

# Save debug image
result.save("debug_output.png")
```

### CLI Workflow

```bash
# 1. Capture screenshot from device
vista screenshot --output myscreen.png

# 2. Debug OCR detection
vista debug myscreen.png --output debug.png

# 3. Inspect debug image to verify OCR accuracy
open debug.png  # macOS
# or
xdg-open debug.png  # Linux

# 4. Adjust OCR provider or confidence threshold if needed
vista debug myscreen.png --ocr easy --confidence 0.85
```

## Architecture Highlights

### Perception Pipeline

```
Screenshot (PIL Image)
    ↓
PaddleOCR / EasyOCR (OCRProvider.detect_text)
    ↓
List[TextElement] with BBox + confidence
    ↓
(Stage 3) Match against user targets
```

### Pluggable OCR Providers

```python
from vista.vision.ocr.base import OCRProvider
from PIL.Image import Image
from typing import List
from vista.vision.elements import TextElement

class CustomOCRProvider(OCRProvider):
    def detect_text(self, image: Image) -> List[TextElement]:
        # Your custom OCR implementation
        pass
```

### Debug Visualization

Green boxes = text elements (with labels showing detected text + confidence)
Blue boxes = icon elements (Stage 4, currently unused)
Grid overlay (optional) = coordinate reference for tapping

## Coordinate System

All bounding boxes are in **raw screenshot pixel coordinates** (not device points).

For Retina displays (2x):
- Screenshot: 1080×1920 pixels
- Device: 540×960 points
- OCR output: BBox in pixel space
- Tap coordinates: Convert pixels→points in driver (handled automatically)

## What's Working Now

✅ OCR text detection (PaddleOCR + EasyOCR)
✅ Bounding box extraction from OCR output
✅ Visual debug overlays with confidence scores
✅ CLI debug command for easy inspection
✅ Confidence threshold filtering
✅ Grid overlay for coordinate visualization

## What Happens in Stage 3

DSL + Action Execution:

1. Parse YAML test script (e.g., `tap: "Login"`)
2. Capture screenshot + run OCR (Stage 2 ✓)
3. **Match targets** — find "Login" in detected text elements
4. **Execute actions** — tap at the found coordinates
5. Record results + generate report

This stage will complete the core automation loop: perception → matching → action.

## Testing

Run all tests:
```bash
pytest tests/unit/ -v
```

Run only debug overlay tests:
```bash
pytest tests/unit/test_debug_overlay.py -v
```

Run only OCR tests:
```bash
pytest tests/unit/test_ocr_providers.py -v
```

## Files Added/Modified

**New files**:
- `vista/vision/ocr/paddle_ocr.py` — PaddleOCR provider
- `vista/vision/ocr/easy_ocr.py` — EasyOCR provider
- `vista/vision/debug.py` — Visual overlay tools
- `tests/unit/test_ocr_providers.py` — OCR provider tests
- `tests/unit/test_debug_overlay.py` — Debug visualization tests
- `STAGE2.md` — This file

**Modified files**:
- `vista/cli/main.py` — Added `debug` command
- Tests: All 46 unit tests passing

## Troubleshooting

### "ModuleNotFoundError: No module named 'paddleocr'"

Install PaddleOCR:
```bash
pip install paddleocr
```

### "ModuleNotFoundError: No module named 'easyocr'"

Install EasyOCR:
```bash
pip install easyocr
```

### OCR accuracy is low

Try:
1. Check screenshot brightness/contrast
2. Use `--confidence 0.8` to filter low-confidence detections
3. Try alternative OCR provider (EasyOCR vs PaddleOCR)
4. Check if text is very small (may need higher resolution)

### Debug image shows no detections

1. Verify screenshot is readable
2. Check OCR provider is initialized correctly
3. Try with `--verbose` flag for debugging
4. Test with known text screenshot

## Next Steps (Stage 3)

**DSL + Matching + Execution**:
- YAML parser for test scripts
- ElementMatcher — resolve `tap: "Login"` to actual bounding boxes
- ActionExecutor — perform tap/type/swipe
- Main run loop integrating all stages

---

**Stage 2 Status**: ✅ Complete and tested
**Test Coverage**: 46 unit tests passing (including 12 visualization tests)
