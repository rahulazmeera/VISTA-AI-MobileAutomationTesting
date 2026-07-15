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
):
    """Debug a screenshot — show OCR and icon detection overlays."""
    # TODO (Stage 2): Implement visual overlay
    typer.echo(f"Debugging screenshot: {screenshot}")
    typer.echo(f"OCR provider: {ocr_provider}")
    if output:
        typer.echo(f"Output: {output}")
    typer.echo("Stage 0 scaffold — debug visualization coming in Stage 2")


@app.command()
def doctor():
    """Check environment setup and dependencies."""
    # TODO (Stage 7): Implement environment checks
    typer.echo("Checking VISTA environment setup...")
    typer.echo("✓ Python environment OK")
    typer.echo("Stage 0 scaffold — full checks coming in Stage 7")


if __name__ == "__main__":
    app()
