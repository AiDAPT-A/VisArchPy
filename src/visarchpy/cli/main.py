"""
Main CLI entry point for VisArchPy.
"""

import typer
import visarchpy.cli.layout_ocr as layout_ocr
import visarchpy.cli.layout as layout
import visarchpy.cli.ocr as ocr
import visarchpy.cli.dino as dino
import visarchpy.cli.viz as viz

app = typer.Typer(
    help="VisArchPy: Data pipelines for extraction, transformation and visualization of architectural visuals in Python.",
    context_settings={
        "help_option_names": ["-h", "--help"]
        },
    add_completion=False)

# Each of this subcommands are defined in their own file in the cli directory
app.add_typer(layout.app, name="layout")
app.add_typer(ocr.app, name="ocr")
app.add_typer(layout_ocr.app, name="layoutocr")
app.add_typer(dino.app, name="dino")
app.add_typer(viz.app, name="viz")


if __name__ == "__main__":
    app()
