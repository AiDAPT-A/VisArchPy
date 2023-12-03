"""
Convenience functions for analysing data produced by the pipelines
Author: M.G. Garcia
"""

import os
import matplotlib
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from tqdm import tqdm
from PIL import Image, ImageFile
from typing import List, Any
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from visarchpy.models import KmeansBbox20

# This is needed to avoid errors when loading images with
# truncated data (images missing data). Use with caution.
ImageFile.LOAD_TRUNCATED_IMAGES = True


def get_image_paths(directory: str, extensions: List[str] = None) -> List[str]:
    """
    Returns a list of file paths for all image files in the given directory.

    Parameters
    ----------

    directory: str
        The directory to search for image files.
    extensions: List[str]
        List of image extensions to include in the result, e.g. ['.jpg',
        '.jpeg', '.png', '.bmp', '.gif']. If None, all file extensions
        (images or not) will be included. Default is None.

    Returns
        A list of file paths for all image files in the directory.
    """

    # If extensions is None, set it to a list of all image extensions
    image_extensions = extensions

    image_paths = []
    for filename in os.listdir(directory):

        if image_extensions is None:
            image_paths.append(os.path.join(directory, filename))
        elif extensions is not None:
            # filter by extension
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_paths.append(os.path.join(directory, filename))
    return image_paths


def plot_bboxes(images: List[str],
                cmap: str = 'cool',
                predictor: Any = None,
                show: bool = True,
                size: int = 10,
                resolution: int = 300,
                scale_factor: float = 1.0,
                max_image_size: int = 89478485,
                save_to_file: str = None) -> None:
    """
    Creates a plot of the bounding boxes organize concentrically for the given
    images.This type of plot is useful for visualizing the distribution sizes
    and shapes of the given images.

    Parameters
    ----------
    image_paths: List[str]
        A list of image file paths.
    cmap: str
        Name of the matplotlib color map to be used. Consult the matplotlib
        documentation for valid values.
    predictor: Kmeans
        A clustering Kmeans (Scikit Learn) trained model for assing a label
        and color to each image bounding box. If None, a pretained model with
        features: `width` and `height`, and 20 classes will be used.
    show: bool
        Shows plot. Default is True.
    size: int
        Size of the figure plot in inches. Default is 10. This value influences
        the quality of the plot when saving to a file.
    resolution: int
        Resolution of the plot  and figure in dots per inch (dpi).
        Default is 300.
    scale_factor: float
        Scale factor for the image size. Default is 1.0, which means that
        images will be plotted at their original size. Values larger than
        1.0 will increase the image size and values smaller than 1.0 will
        decrease the image size.
    max_image_size: int
        Maximum size of an image in pixels. Images larger than this value
        will not be plotted. Default is 89478485, which is the maximum
        size of an image in pixels that can be stored in a 32-bit system.
    save_to_file: str
        Path to a PNG file to save the plot. If None, no file is saved.

    Returns
    -------
    None

    Raises
    ------

    Warning: If an image has no bounding box in the alpha channel.
    Warning: Decompression Bomb. If an image is larger than the maximum
             size allowed for a 32-bit system.
    Killed: If system runs out of memory during plotting. Adjusting the
            `max_image_size` and `scale_factor` parameters may help.

    """

    # Plot/Figure settings and metadata
    # Create a figure and axis object
    fig, ax = plt.subplots()
    fig.set_dpi(resolution)  # set resolution
    # make plot set the axis limits
    ax.plot()
    # Set the axis labels
    ax.set_xlabel('Image Width (px)')
    ax.set_ylabel('Image Height (px)')
    ax.set_title('Bounding Box Plot')
    label_fontsize = 8
    # Set the axis tick label size
    ax.tick_params(labelsize=label_fontsize)

    # create color map
    _cmap = matplotlib.colormaps[cmap]

    # list of PIL.Image objects
    images = [Image.open(image_path) for image_path in images if
              Image.open(image_path).size != 0 and
              Image.open(image_path).size[0] *
              Image.open(image_path).size[1] <= max_image_size]

    if predictor:
        k_predictor = predictor
    else:
        model = KmeansBbox20()  # loads model
        k_predictor = model()  # gets predictor

    # collect image widths and heights to determine
    # image  maximum size
    widths = []
    heights = []
    [(widths.append(image.width * scale_factor),
      heights.append(image.height * scale_factor))
     for image in images]

    max_width = max(widths)
    max_height = max(heights)
    ratio = max_width / max_height
    # Set the figure to a size while keeping the aspect ratio
    fig.set_figwidth(size * ratio)
    fig.set_figheight(size / ratio)

    # Sort the clusters so that labels are organized in increasing order
    # This makes sure that the colors are distributed along the
    # color map in the right order
    idx = np.argsort(k_predictor.cluster_centers_.sum(axis=1))
    sorted_label = np.zeros_like(idx)
    sorted_label[idx] = np.arange(idx.shape[0])

    # Collect prediction values and images in preparation for
    # plotting. This ensures the predict function is called
    # only once.
    predictions = []
    pil_images = []
    [(predictions.append(k_predictor.predict([[image.width, image.height]])),
        pil_images.append(image))
        for image in images]

    # This is used to strech the colors
    # in the color map using the range of
    # values in the prediction
    max_sorted_label = max(sorted_label[predictions])
    min_sorted_label = min(sorted_label[predictions])

    box_tracker = {}  # keeps track of size and count of boxes already plotted
    # plot bounding boxes
    for prediction, image in tqdm(zip(predictions, pil_images),
                                  desc='Plotting...', unit='bboxes'):
        # Get the bounding box for the current image
        # This throws an TypeError if image has an alpha channel by no pixels
        # in that channel. This is the default as of Pillow 10.3.0
        # See: https://pillow.readthedocs.io/en/stable/reference/Image.html
        # #PIL.Image.Image.getbbox

        if image.size not in box_tracker:
            box_tracker[image.size] = 1  # initialize box count

            bbox = image.getbbox()  # Will return None if alpha channel
            # is empty

            # trasforms predicted label to sorted label
            prediction = sorted_label[prediction]
            # notmalize to 0-1
            norm_prediction = prediction[0]/(max_sorted_label -
                                             min_sorted_label)
            rgba = _cmap(norm_prediction)  # assignes color for rectangle

            if bbox is None:
                # Skip creating an rectangle image has no bounding
                # box (read issues with alpha channel above)
                Warning(f'Image {image.filename} has no bounding box.\
                        Skipping.')
                continue
            else:
                # Create a rectangle patch for the bounding box
                # Origin is set to center of drawing aread and
                # boxes are drawn concentrically.
                rec_width = image.width * scale_factor
                rec_height = image.height * scale_factor

                rec_x = bbox[0] * scale_factor
                rec_y = bbox[1] * scale_factor
                rect = patches.Rectangle((rec_x - 0.5 * rec_width, rec_y -
                                          0.5 * rec_height),
                                         rec_width, rec_height,
                                         linewidth=1, edgecolor=rgba,
                                         facecolor='none')

                # Plot the bounding box
                ax.add_patch(rect)
            # free some memory. It is convenient with many or large inputs
            del image

        else:
            box_tracker[image.size] = box_tracker.get(image.size) + 1

    # add plot legend
    # plots colorbar after normalizing the values of he sorted
    # prediction labels
    norm = Normalize(vmin=min_sorted_label, vmax=max_sorted_label)
    scalar_mappable = ScalarMappable(norm=norm, cmap=_cmap)
    color_bar = plt.colorbar(scalar_mappable, ax=ax)
    color_bar.set_label('Image size (w x h)', fontsize=label_fontsize)

    color_bar.ax.tick_params(labelsize=label_fontsize)
    # remove ticks and add labels
    min_size_label = str(min(box_tracker.keys()))
    max_size_label = str(max(box_tracker.keys()))
    color_bar.set_ticks(
        [min_sorted_label[0], max_sorted_label[0]],
        labels=[min_size_label, max_size_label])

    if save_to_file:
        plt.savefig(save_to_file, dpi=resolution, bbox_inches='tight')
        print(f'Plot saved to {save_to_file}')

   
    # Show the plot
    if show:
        print('Close the plot window to continue...')
        plt.show()


if __name__ == "__main__":

    # Example of how to use the plot_bboxes function
    img_plot = get_image_paths(
        directory='data/plot')

    plot_bboxes(img_plot, cmap='gist_heat_r',
                size=10, show=True, resolution=300)
