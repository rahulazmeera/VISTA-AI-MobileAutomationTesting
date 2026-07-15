# Contributing to VISTA

Welcome! VISTA is an open-source project, and we're excited to have you contribute.

## Code of Conduct

Be respectful, inclusive, and professional. We're building a tool for the whole community.

## Getting Started

1. **Clone the repo and install**:
   ```bash
   git clone https://github.com/yourusername/vista-mobile.git
   cd vista-mobile
   pip install -e ".[dev]"
   ```

2. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

3. **Run tests locally** (unit tests only; see below for simulator tests):
   ```bash
   pytest tests/unit -v
   ```

## Development Workflow

1. Create a branch: `git checkout -b feature/your-feature-name`
2. Make your changes, ensuring tests pass and linting is clean
3. Commit with a clear message: `git commit -m "brief description"`
4. Push and open a PR against `develop`

## Testing

VISTA uses a three-tier testing strategy:

- **Unit tests** (`pytest -m "not simulator"`) — no device needed, run on every PR
  - Mock the Driver entirely; use golden JSON fixtures for OCR/icon outputs
  - Test DSL parsing, matcher logic, executor step handlers, coordinate math
  - Located in `tests/unit/`
  
- **Vision provider tests** (`pytest -m "vision"`) — real OCR/icon models, no device needed
  - Run against committed fixture screenshots in `tests/fixtures/screens/`
  - Slower but deterministic, run on every PR
  - Verify PaddleOCR/EasyOCR accuracy and icon detection thresholds

- **Simulator integration tests** (`pytest -m "simulator"`) — requires booted iOS Simulator
  - Only run on merge-to-main / nightly given simulator boot cost
  - Drive the bundled demo app end-to-end
  - Verify the full capture→perceive→resolve→act pipeline

Add new tests in the appropriate tier. Use markers:
```python
@pytest.mark.unit
def test_text_matcher_handles_ocr_noise(): ...

@pytest.mark.vision
def test_paddle_ocr_on_login_screen(): ...

@pytest.mark.simulator
def test_login_flow_end_to_end(): ...
```

## CRITICAL RULE: No Accessibility Locators in Non-Driver Code

**This is the core constraint that makes VISTA work.** The entire point is to move away from brittle ID/XPath-based selectors. Therefore:

### Rules:
1. **Only `vista/driver/ios_appium.py` (and later `vista/driver/android_appium.py`) may directly import `appium`**.
2. **Only expose from the Driver ABC**:
   - `screenshot() -> Image`
   - `tap(x, y)`, `type_text(text)`, `swipe(start, end, duration_ms)`
   - `press_key(key)`, `screen_size()`, `scale_factor()`
3. **NEVER** call `driver.find_element()`, `find_element_by_*()`, or any accessibility-tree query outside the driver module.
4. Any code that needs to interact with the device must go through the `Driver` ABC's coordinate-based interface.

### Why This Matters:
If you slip and start using `find_element()` in the matcher, runner, or executor, we're back to the original problem: brittle tests that break with every UI change. The CI pre-commit hook will catch this (grep-based rule), but please think about it before you code — the boundary is **driver modules only**.

### Example of What NOT to Do:
```python
# WRONG — don't do this in matcher.py or runner.py
from appium.webdriver.common.by import By
element = driver.find_element(By.ACCESSIBILITY_ID, "loginButton")
```

### Example of What TO Do:
```python
# CORRECT — use Driver ABC methods
screen = driver.screenshot()
text_elements = ocr_provider.detect_text(screen)
button = matcher.resolve("Login", ScreenState(...), kind="text")
driver.tap(button.bbox.center_x, button.bbox.center_y)
```

## Architecture Overview

See [the plan document](/.claude/plans/whimsical-sniffing-walrus.md) for a detailed architecture. Quick summary:

```
capture (screenshot) 
  → perceive (OCR + icon detection) 
  → resolve (fuzzy match against ScreenState) 
  → act (tap/type/swipe via coordinates) 
  → report (HTML with annotated screenshots)
```

Each stage is pluggable via ABCs:
- `Driver` — device control (screenshot + coordinate actions)
- `OCRProvider` — text detection (PaddleOCR default, EasyOCR pluggable)
- `IconDetector` — icon detection (template matching default)
- `ElementMatcher` — resolve instruction targets to elements
- `ActionExecutor` — execute a step against the driver

## Submitting a PR

1. **Ensure tests pass**: `pytest tests/unit -v` (at minimum)
2. **Pass linting**: `black vista tests` and `ruff check vista tests`
3. **Update docs** if you're adding a new feature (especially new step types or config options)
4. **Reference the issue** if applicable: `Closes #123`
5. **Describe what you changed and why** — PRs are easier to review when the intent is clear

## Reporting Bugs

Use GitHub Issues. Include:
- A minimal reproduction script (as a `.yaml` test file if possible)
- The OS, Python version, iOS version / Android version
- Relevant logs (run with `VISTA_DEBUG=1` for verbose logging)

## Questions?

Open a discussion or ping the maintainers. We're here to help.

---

Thanks for contributing to VISTA! You're helping build the future of vision-based mobile testing. 🚀
