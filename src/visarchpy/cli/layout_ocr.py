"""CLI for the layout_ocr pipeline."""

import os
import typer
from typing_extensions import Annotated, Optional
from visarchpy.pipelines import LayoutOCR
import json

app = typer.Typer(help="Extract visuals from PDF files using layout and \
OCR analysis.",
                  context_settings={"help_option_names": ["-h", "--help"]},
                  add_completion=False)

with open("../default-settings.json", "r") as f:
    default_settings = json.load(f)

    # src/visarchpy/default-settings.json

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



@app.command(help="Show default settings for the pipeline.")
def settings() -> None:
    """Show default settings for the pipeline."""
    typer.echo(default_settings)

@app.command(help="batch processing for TU Delft's dataset")
def batch(entry_range: str = typer.Argument(help="Range of entries to process\
                                            e.g.: 1-10"),
          data_directory: str = typer.Argument(help="path to directory\
                                               containing MODS and pdf files"),
          output_directory: str = typer.Argument(help="path to directory where\
                                                 results will be saved"),
          settings_file: Annotated[Optional[str],
                                   typer.Argument(help="path to pipeline JSON settings\
                                             file. If None default settings will be\
                                             used. Use: [COMMAND] setting, to see\
                                             current settings")]= None,
          temp_directory: Annotated[Optional[str],
                                    typer.Argument(help="temporary directory")
                                    ] = None,
          ) -> None:
    """Extracts metadata from MODS files and images from PDF files
      using layout and OCR pipeline"""

    if settings_file is None:
        settings = default_settings
    else:
        with open(settings_file, "r") as f:
            settings = json.load(f)

    start_id = int(entry_range.split("-")[0])
    end_id = int(entry_range.split("-")[1])

    for id in range(start_id, end_id+1):
        str_id = str(id).zfill(5)

        MODS_FILE = os.path.join(data_directory, str_id + "_mods.xml")

        LayoutOCR(data_directory, output_directory,
                  settings=settings, metadata_file=MODS_FILE,
                  temp_directory=temp_directory)

        # TODO: test batch cli

if __name__ == "__main__":
    app()
