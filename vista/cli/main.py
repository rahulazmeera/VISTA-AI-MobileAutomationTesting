"""Main CLI entrypoint."""

import logging
import sys
from pathlib import Path

import typer

logger = logging.getLogger(__name__)

app = typer.Typer(
    help="VISTA — Vision-based Intelligent Screen Test Automation",
    no_args_is_help=True,
)


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@app.command()
def screenshot(
    output: str = typer.Option(
        "screenshot.png",
        "--output",
        "-o",
        help="Path to save the screenshot",
    ),
    platform: str = typer.Option(
        "ios",
        "--platform",
        "-p",
        help="Target platform (ios or android)",
    ),
    appium_url: str = typer.Option(
        "http://localhost:4723",
        "--appium-url",
        help="Appium server URL",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
):
    """Capture a screenshot from the device/simulator."""
    setup_logging(verbose)

    if platform.lower() != "ios":
        typer.echo("Error: Android not yet supported (coming in Stage 8)", err=True)
        raise typer.Exit(code=1)

    try:
        from vista.driver.ios_appium import IOSAppiumDriver

        typer.echo(f"Connecting to Appium at {appium_url}...")
        with IOSAppiumDriver(remote_url=appium_url) as driver:
            typer.echo("✓ Connected to device/simulator")

            typer.echo(f"Capturing screenshot...")
            screenshot_image = driver.screenshot()

            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            screenshot_image.save(output_path)

            w_px, h_px = screenshot_image.size
            w_pt, h_pt = driver.screen_size()
            scale = driver.scale_factor()

            typer.echo(f"✓ Screenshot saved: {output_path}")
            typer.echo(f"  Size: {w_px}x{h_px} pixels ({w_pt}x{h_pt} points)")
            typer.echo(f"  Scale factor: {scale:.1f}x")

    except ConnectionError as e:
        typer.echo(f"Error: {e}", err=True)
        typer.echo(
            "\nMake sure Appium is running:\n  appium",
            err=True,
        )
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def run(
    script: str = typer.Argument(..., help="Path to the YAML test script"),
    platform: str = typer.Option(
        "ios",
        "--platform",
        "-p",
        help="Target platform (ios or android)",
    ),
    device: str = typer.Option(
        None,
        "--device",
        "-d",
        help="Target device name or ID (optional, uses default simulator if not specified)",
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Path for output report (HTML by default)",
    ),
):
    """Run a VISTA test script."""
    # TODO (Stage 3): Implement full execution pipeline
    typer.echo(f"Running script: {script}")
    typer.echo(f"Platform: {platform}")
    if device:
        typer.echo(f"Device: {device}")
    if output:
        typer.echo(f"Output: {output}")
    typer.echo("Stage 1: iOS driver ready — full execution coming in Stage 3")


@app.command()
def debug(
    screenshot: str = typer.Argument(..., help="Path to a screenshot file"),
    ocr_provider: str = typer.Option(
        "paddle",
        "--ocr",
        help="OCR provider (paddle or easy)",
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Path for output debug image with overlays",
    ),
    confidence_threshold: float = typer.Option(
        0.0,
        "--confidence",
        "-c",
        help="Minimum confidence threshold (0.0-1.0)",
    ),
    add_grid: bool = typer.Option(
        False,
        "--grid",
        help="Add coordinate grid overlay",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
):
    """Debug a screenshot — show OCR and icon detection overlays."""
    setup_logging(verbose)

    from pathlib import Path

    screenshot_path = Path(screenshot)
    if not screenshot_path.exists():
        typer.echo(f"Error: Screenshot not found: {screenshot}", err=True)
        raise typer.Exit(code=1)

    try:
        from PIL import Image

        from vista.vision.debug import draw_all_elements, add_grid as add_grid_overlay
        from vista.vision.ocr.paddle_ocr import PaddleOCRProvider
        from vista.vision.ocr.easy_ocr import EasyOCRProvider

        typer.echo(f"Loading screenshot: {screenshot_path}")
        image = Image.open(screenshot_path).convert("RGB")
        typer.echo(f"✓ Loaded {image.size[0]}x{image.size[1]} image")

        # Select OCR provider
        if ocr_provider.lower() == "paddle":
            typer.echo("Initializing PaddleOCR...")
            ocr = PaddleOCRProvider(use_gpu=False)
        elif ocr_provider.lower() == "easy":
            typer.echo("Initializing EasyOCR...")
            ocr = EasyOCRProvider(use_gpu=False)
        else:
            typer.echo(f"Error: Unknown OCR provider: {ocr_provider}", err=True)
            raise typer.Exit(code=1)

        typer.echo("Running OCR detection...")
        text_elements = ocr.detect_text(image)
        typer.echo(f"✓ Detected {len(text_elements)} text elements")

        # For now, no icon detection (Stage 4)
        icon_elements = []

        # Draw overlays
        typer.echo("Drawing overlays...")
        result = draw_all_elements(image, text_elements, icon_elements, confidence_threshold)

        if add_grid:
            typer.echo("Adding grid overlay...")
            result = add_grid_overlay(result, grid_size=50)

        # Save output
        if output is None:
            output = screenshot_path.stem + "_debug.png"

        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.save(output_path)

        typer.echo(f"✓ Debug image saved: {output_path}")
        typer.echo(f"\nDetected elements:")
        for i, elem in enumerate(text_elements, 1):
            typer.echo(f"  {i}. '{elem.text}' @ ({elem.bbox.x}, {elem.bbox.y}) "
                      f"[{elem.bbox.width}x{elem.bbox.height}] "
                      f"(confidence: {elem.confidence:.2f})")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def doctor():
    """Check environment setup and dependencies."""
    # TODO (Stage 7): Implement environment checks
    typer.echo("Checking VISTA environment setup...")
    typer.echo("✓ Python environment OK")
    typer.echo("Stage 0 scaffold — full checks coming in Stage 7")


if __name__ == "__main__":
    app()
