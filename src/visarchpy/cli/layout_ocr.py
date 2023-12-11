"""CLI for the layout_ocr pipeline."""

import os
import typer
from typing_extensions import Annotated
from visarchpy.pipelines import LayoutOCR
import json
from visarchpy.utils import create_output_dir
import shutil
import visarchpy.cli.settings as settings

app = typer.Typer(help="Extract images from PDF files using layout and \
OCR analysis.",
                  context_settings={"help_option_names": ["-h", "--help"]},
                  add_completion=False)


@app.command(help="Extract images from a single PDF file.")
def from_file(
    pdf_file: str = typer.Argument(help="Path to directory containing PDF files."),
    output_directory: str = typer.Argument(help="Path to directory where results will be saved."),
    settings: Annotated[str, typer.Option(help="Path to pipeline JSON setting file. If None default settings will be used. Use: [COMMAND] settings, to see current settings.")] = None,
    mods: Annotated[str, typer.Option(help="Path to MODS file. If None, metadata extraction will be skiped.")] = None
    ) -> None:

    if settings is None:
        settings = settings.init()
    else:
        with open(settings, "r") as f:
            settings = json.load(f)
            print('loaded settings from file: ', settings)

    # Create a temporary directory where the input PDF
    # is copied to be able to use the pipeline class
    # This could be improve.
    file_dir = os.path.dirname(pdf_file)
    temp_directory = create_output_dir(file_dir, './.visarchpy')
    data_directory = str(temp_directory) + '/'  # TODO: avoid this patching. Manage paths with os.path
    shutil.copy2(pdf_file, data_directory)

    pipeline = LayoutOCR(data_directory, output_directory,
                             settings=settings, metadata_file=mods,
                             ignore_id=True)

    pipeline.run()

    # clean up
    if temp_directory.exists():
        shutil.rmtree(temp_directory)


@app.command(help="Extract images from all PDF files in a directory.")
def from_dir(
    data_directory: str = typer.Argument(help="Path to directory containing PDF files."),
    output_directory: str = typer.Argument(help="Path to directory where results will be saved."),
    settings: Annotated[str, typer.Option(help="Path to pipeline JSON setting file. If None default settings will be used. Use: [COMMAND] settings, to see current settings.")] = None,
    mods: Annotated[str, typer.Option(help="Path to MODS file. If None, metadata extraction will be skiped.")] = None,
    tmp: Annotated[str, typer.Option(help="If provided, PDF files in the data directory will be copied to this directory.")
    ] = None) -> None:
    
    if settings is None:
        settings = settings.init()
    else:
        with open(settings, "r") as f:
            settings = json.load(f)
            print('loaded settings from file: ', settings)

    pipeline = LayoutOCR(data_directory, output_directory,
                             settings=settings, metadata_file=mods,
                             temp_directory=tmp, ignore_id=True)

    pipeline.run()


@app.command(help="Show default settings for the pipeline.")
def settings() -> None:
    """Show default settings for the pipeline."""
    typer.echo(default_settings)


@app.command(help="batch processing for TU Delft's dataset.")
def batch(entry_range: str = typer.Argument(help="Range of entries to process, e.g.: 1-10."),
          data_directory: str = typer.Argument(help="path to directory containing MODS and PDF files."),
          output_directory: str = typer.Argument(help="path to directory where results will be saved."),
          settings: Annotated[str, typer.Option(help="path to pipeline JSON setting file. If None default settings will be used. Use: [COMMAND] settings, to see current settings.")] = None,
          tmp: Annotated[str, typer.Option(help="If provided, PDF files in the data directory will be copied to this directory.")
            ] = None) -> None:
    """Extracts metadata from MODS files and images from PDF files
      using layout and OCR pipeline"""

    if settings is None:
        settings = default_settings
    else:
        with open(settings, "r") as f:
            settings = json.load(f)

    start_id = int(entry_range.split("-")[0])
    end_id = int(entry_range.split("-")[1])

    for id in range(start_id, end_id+1):
        str_id = str(id).zfill(5)

        MODS_FILE = os.path.join(data_directory, str_id + "_mods.xml")

        pipeline = LayoutOCR(data_directory, output_directory,
                             settings=settings, metadata_file=MODS_FILE,
                             temp_directory=tmp)

        pipeline.run()


if __name__ == "__main__":
    app()

    # CLI examples:

    # visarch batch 1-2 ./tests/data/00001/ ./tests/data/layout/  ./tests/data/tmp/ 

    # from-dir ./tests/data/00001/ ./tests/data/layout/  --tmp ./tests/data/tmp/

    # from-file ./tests/data/00001/00002_sample.pdf ./tests/data/layout/ --mods ./tests/data/00001/00002_mods.xml

