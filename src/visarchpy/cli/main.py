"""
Main CLI entry point for VisArchPy.
"""

import typer
# import aidapta.pipelines.layout as layout
# import aidapta.pipelines.ocr as ocr
import visarchpy.pipelines.layout_ocr as layout_ocr
import visarchpy.cli.dino as dino

app = typer.Typer(
    help="VisArchPy: data pipelines for extraction and analysis of "
         "architectural visuals in Python.",
    context_settings={
        "help_option_names": ["-h", "--help"]
        },
    add_completion=False)


# Each of this subcommands are defined in their own file in the cli directory

# app.add_typer(layout.app, name="layout")
# app.add_typer(ocr.app, name="ocr"from typing import Optional)
app.add_typer(layout_ocr.app, name="layout-ocr")

app.add_typer(dino.app, name="dino")


if __name__ == "__main__":
    app()
