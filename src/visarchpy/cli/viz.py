""" CLI for the analytics module. """

import os
import typer
from tqdm import tqdm
from typing_extensions import Annotated
from visarchpy.analytics import plot_bboxes, get_image_paths

app = typer.Typer(help="Utility for visualizing architectural visuals.",
    context_settings={"help_option_names": ["-h", "--help"]},
                   add_completion=False)

@app.command(help="Creates a bounding box plot for images in a directory.")
def bbox_plot(
    image_dir: str = typer.Argument(help="Path to directory containing image for the plot."),
    color_map: Annotated[str, typer.Argument(help="Matplotlib color map to be used.")] = 'cool',
    resolution: Annotated[int, typer.Argument(help="Resolution of the plot in dpi.")] = 300,
    size: Annotated[int, typer.Argument(help="Size of the plot in inches.")] = 10,
    output_file: Annotated[str, typer.Argument(help="Path to PNG file to save plot. No file is saved by default.")] = None,
    show: Annotated[bool, typer.Option(help="Show plot in interactive window.", is_flag=True)] = True,
    max_image_size: Annotated[int, typer.Option(help="Filters images larger than this (bytes).")] = 89478485,
    ) -> None:
        
    # get image from image_dir
    images = get_image_paths(image_dir)

    # create plot
    plot_bboxes(images, cmap=color_map, show=show, size=size, resolution=resolution, save_to_file=output_file, max_image_size=max_image_size)

if __name__ == "__main__":
    app()