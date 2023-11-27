""" CLI for the transformer module. """

import os
import typer
from tqdm import tqdm
from typing_extensions import Annotated
from visarchpy.dino.transformer import transform_to_dinov2, save_csv_dinov2, save_pickle_dinov2

app = typer.Typer(help="Transforms images into visual features using DinoV2.",
    context_settings={"help_option_names": ["-h", "--help"]},
                   add_completion=False)

@app.command(help="Extract features from a sigle image file.")
def from_file(
    file: str = typer.Argument(help="Path to image file"),
    output: Annotated[str, typer.Argument(help="Path to output directory")] = './dinov2',
    model: Annotated[str, typer.Argument(help="pretrained model to be used")] = 'facebook/dinov2-small',
    pickle: Annotated[bool, typer.Option(help="Save all model features as pickle file", is_flag=True)] = True
        ) -> None:
    
    os.makedirs(output, exist_ok=True)
    filename = os.path.basename(file).split('.')[0]

    # extract features
    results = transform_to_dinov2(file, model)
    save_csv_dinov2(os.path.join(output, filename + '.csv'), results['tensor'])
    
    # save pickle file
    if pickle:
        save_pickle_dinov2(os.path.join(output, filename + '.pickle'), results['object'])

    return None

@app.command(help="Extract features from all image files in a directory.")
def from_dir(
    directory: str = typer.Argument(help="Path to directory containing image files"),
    output: Annotated[str, typer.Argument(help="Path to parent output directory.")] = './dinov2',
    model: Annotated[str, typer.Argument(help="pretrained model to be used")] = 'facebook/dinov2-small',
    pickle: Annotated[bool, typer.Option(help="Save all model features as pickle file", is_flag=True)] = True
        ) -> None:
    
    # results will be saved in a subdirectory named after the input directory
    # and with the output directory as parent directory

    output_dir = os.path.join(output, os.path.basename(directory.rstrip('/')))
    os.makedirs(output_dir, exist_ok=True)
    files = os.listdir(directory)

    for file in tqdm(files, desc="Extracting features", unit="images"):
        filename = os.path.basename(file).split('.')[0]

        # extract features
        try:
            results = transform_to_dinov2(os.path.join(directory, file), model)
        except IOError:
            print(f"WARNING: Directory contain file(s) that are not images: {file}. Skipping...")
            continue
            # TODO: improve error handling for CLI
        else:
            save_csv_dinov2(os.path.join(output_dir, filename + '.csv'), results['tensor'])
        
            # save pickle file
            if pickle:
                save_pickle_dinov2(os.path.join(output_dir, filename + '.pickle'), results['object'])
    
    return None

if __name__ == "__main__":
    app()
