import typer
from typing import Optional
# import aidapta.pipelines.layout as layout
# import aidapta.pipelines.ocr as ocr
import visarchpy.pipelines.layout_ocr as layout_ocr
import visarchpy.pipelines.dinov2 as dinov2

app = typer.Typer(help="VisArchPy: data pipelines for extraction and analysis of architectural visuals in Python.",
    context_settings={"help_option_names": ["-h", "--help"]},
                   add_completion=False)


# app.add_typer(layout.app, name="layout")
# app.add_typer(ocr.app, name="ocr")
app.add_typer(layout_ocr.app, name="layout-ocr")
app.add_typer(dinov2.app, name="dinov2")


if __name__ == "__main__":
    app()