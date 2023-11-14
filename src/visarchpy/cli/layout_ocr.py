""" CLI for the layout_ocr pipeline."""

import typer

app = typer.Typer(help="Extract visuals from PDF files using layout and OCR analysis.",
    context_settings={"help_option_names": ["-h", "--help"]},
                   add_completion=False)


@app.command(help="Extract visuals from a single PDF file.")
def from_file(
    ) -> None:

    # TODO: implement extraction of visuals from a single PDF file.
    pass
    

@app.command(help="Extract visuals from all PDF files in a directory.")
def from_dir(
    directory: str = typer.Argument(help="Path to directory containing PDF files"),
    output: str = typer.Argument(help="Path to output directory"),
    ) -> None:
    # TODO: implement extraction of visuals from all PDF files in a directory.
    return None


@app.command(help="batch processing for TU Delft's dataset")
def batch(
    directory: str = typer.Argument(help="Path to directory containing PDF files"),
    output: str = typer.Argument(help="Path to output directory"),
    ) -> None:
    # TODO: implement batch processing for TU Delft's dataset.
    return None


if __name__ == "__main__":
    app()