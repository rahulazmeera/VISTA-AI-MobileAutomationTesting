# VISTA — Vision-based Intelligent Screen Test Automation

**VISTA** is an open-source framework for robust, maintainable mobile app testing. Instead of brittle selectors (IDs, XPaths, accessibility-ids), VISTA automates apps the way a human tester does: by *looking at the screen*.

## The Problem

Traditional mobile automation (Appium, XCUITest, Espresso) relies on element locators:
- Resource IDs: `com.example.app:id/login_button`
- XPaths: `//XCUIElementTypeButton[@name="Login"]`
- Accessibility IDs: `LoginButton`

**Every time the app layout changes, tests break** — even though the screen looks identical to a human.

## The Solution

VISTA combines OCR, icon detection, and fuzzy matching to find elements *visually*:

```yaml
# test_login.yaml
steps:
  - tap: "Login"                    # Find and tap the "Login" text
  - type: "user@example.com"        # Type into the focused field
    into: "Email"
  - tap: "Password"
  - type: "secret123"
    into: "Password"
  - tap: "Sign In"
  - wait: 2                         # Wait for navigation
  - assert_visible: "Welcome"       # Verify success
```

Run it with:
```bash
vista run test_login.yaml --platform ios
```

No brittle selectors. No test maintenance when the UI changes. Tests that read like human actions.

## Features

- **OCR-based element detection** — PaddleOCR by default, EasyOCR as a fallback
- **Icon/non-text element detection** — template matching (Stage 4), ML-based later
- **Fuzzy text matching** — handles OCR noise and minor text variations
- **Raw coordinate actions** — taps/swipes work on the actual pixels, not the accessibility tree
- **Pluggable providers** — swap OCR, icon detection, and reporting backends
- **Structured YAML DSL** — human-readable test instructions designed for future AI generation
- **Simulator support** — iOS (via Appium + WebDriverAgent), Android later (via Appium + UiAutomator2)
- **Beautiful HTML reports** — annotated screenshots with detected elements and action history

## Project Status

**VISTA is in early alpha (Stage 0 scaffolding)**. The architecture is solid and designed for a 5+ year lifespan, but core functionality (Stages 1-3) is still being built.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the roadmap and development workflow.

## Getting Started

### Prerequisites

- Python 3.9+
- Appium 2.x (for device control)
- iOS Simulator or physical iOS device

### Installation

```bash
git clone https://github.com/yourusername/vista-mobile.git
cd vista-mobile
pip install -e ".[dev]"
```

### Run Tests Locally

```bash
# Unit tests (fast, no device required)
pytest tests/unit -v

# Vision provider tests (real OCR/icon detection, ~30s)
pytest tests -m vision -v

# Simulator integration tests (requires booted simulator, slow)
pytest tests -m simulator -v
```

### Write Your First Test

1. Boot an iOS Simulator:
   ```bash
   xcrun simctl boot "iPhone 14"
   ```

2. Start the Appium server:
   ```bash
   appium
   ```

3. Create `test_hello.yaml`:
   ```yaml
   steps:
     - wait_until_visible: "Home"
   ```

4. Run it (coming in Stage 1-3):
   ```bash
   vista run test_hello.yaml --platform ios
   ```

## Architecture

VISTA is built on a clean, pluggable architecture:

```
Screenshot
    ↓
Perception (OCR + icon detection)
    ↓
ScreenState (detected text + icons)
    ↓
Matcher (resolve "Login" → bounding box)
    ↓
Executor (tap, type, swipe via coordinates)
    ↓
Report (HTML with annotated screenshots)
```

Every stage is swappable:
- **OCRProvider**: PaddleOCR, EasyOCR, Google Vision, cloud services
- **IconDetector**: template matching, ML models, embedding-based
- **ElementMatcher**: fuzzy text, semantic similarity, nearest-neighbor
- **Reporter**: HTML, JSON, JUnit XML
- **InstructionPlanner** (Stage 9+): LLM/VLM-based AI automation

See the [architecture plan](/.claude/plans/whimsical-sniffing-walrus.md) for details.

## Why This Approach?

1. **Robust**: Tests work even when the UI changes (as long as the text/icons do)
2. **Maintainable**: No brittle locators to update
3. **Future-proof**: AI-generation hooks designed in from the start (Stage 9+)
4. **Community-friendly**: Pure Python, no JS/compilation, easy to extend

## Contributing

VISTA is built for the community. See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Testing requirements
- The **critical** rule about not using accessibility locators (see [CONTRIBUTING.md#critical-rule](CONTRIBUTING.md#critical-rule-no-accessibility-locators-in-non-driver-code))
- PR submission guidelines

## Roadmap

- **Stage 0** (now): Project scaffolding ✅
- **Stage 1**: iOS driver + screenshot pipeline
- **Stage 2**: OCR + visual debugging
- **Stage 3**: DSL parser + basic actions
- **Stage 4**: Icon detection
- **Stage 5**: Gestures + assertions
- **Stage 6**: Reporting
- **Stage 7**: OSS packaging + release
- **Stage 8+**: Android support
- **Stage 9+**: AI-powered automatic test generation

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.

## Support

- 📖 [Documentation](https://docs.vistaui.dev) (coming Stage 7)
- 🐛 [Report issues](https://github.com/yourusername/vista-mobile/issues)
- 💬 [Discussions](https://github.com/yourusername/vista-mobile/discussions)
- 📧 [Email us](mailto:hello@vistaui.dev) (coming later)

---

Built with ❤️ by the VISTA community. Let's make mobile testing bulletproof.
