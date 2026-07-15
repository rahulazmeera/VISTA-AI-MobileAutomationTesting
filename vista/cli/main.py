"""Main CLI entrypoint."""

import typer

app = typer.Typer(
    help="VISTA — Vision-based Intelligent Screen Test Automation",
    no_args_is_help=True,
)


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
    typer.echo("Stage 0 scaffold — full execution coming in Stage 1-3")


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
