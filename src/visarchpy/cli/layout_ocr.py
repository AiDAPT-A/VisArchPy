"""CLI for the layout_ocr pipeline."""

import os
import typer
from typing_extensions import Annotated, Optional
from visarchpy.pipelines.layout_ocr import pipeline

app = typer.Typer(help="Extract visuals from PDF files using layout and\
                  OCR analysis.",
                  context_settings={"help_option_names": ["-h", "--help"]},
                  add_completion=False)


@app.command(help="Extract visuals from a single PDF file.")
def from_file() -> None:

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
def batch(entry_range: str = typer.Argument(help="Range of entries to process\
                                            e.g.: 1-10"),
          data_directory: str = typer.Argument(help="path to directory\
                                               containing MODS and pdf files"),
          output_directory: str = typer.Argument(help="path to directory where\
                                                 results will be saved"),
          temp_directory: Annotated[Optional[str],
                                    typer.Argument(help="temporary directory")
                                    ] = None
          ) -> None:
    """Extracts metadata from MODS files and images from PDF files
      using layout and OCR analysis."""

    start_id = int(entry_range.split("-")[0])
    end_id = int(entry_range.split("-")[1])
    DATA_DIR = data_directory

    for id in range(start_id, end_id+1):
        str_id = str(id).zfill(5)

        MODS_FILE = os.path.join(DATA_DIR, str_id + "_mods.xml")

        pipeline(data_directory,
                 output_directory,
                 metadata_file=MODS_FILE,
                 temp_directory=temp_directory)


if __name__ == "__main__":
    app()
