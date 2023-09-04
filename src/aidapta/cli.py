import typer
from typing import Optional
# import aidapta.pipelines.layout as layout
# import aidapta.pipelines.ocr as ocr
import aidapta.pipelines.layout_ocr as layout_ocr



app = typer.Typer()


# app.add_typer(layout.app, name="layout")
# app.add_typer(ocr.app, name="ocr")
app.add_typer(layout_ocr.app, name="layout-ocr")




if __name__ == "__main__":
    app()