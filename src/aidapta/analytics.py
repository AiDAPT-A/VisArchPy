"""
Convenience functions for analysing data produced byt the pipelines
Author: M.G. Garcia
"""

import os
from PIL import Image
from typing import List, Any
import matplotlib 
import matplotlib.patches as patches
import matplotlib.pyplot as plt


def get_image_paths(directory: str, extensions: List[str] = None) -> List[str]:
    """
    Returns a list of file paths for all image files in the given directory.

    Parameters
    ---------- 
    
    directory: str
        The directory to search for image files.
    extensions: List[str]
        List of image extensions to include in the result, e.g. ['.jpg', '.jpeg', 
        '.png', '.bmp', '.gif']. If None, all file extensions (images or not) will 
        be included. Default is None.
    
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


def plot_boxes(images: List[str], cmap: str ='cool', predictor: Any = None,
               show: bool = True, save_to_file: str = None) -> None:
    """
    Plots the bounding boxes of a list of images overlapping on the same plot.

    Parameters
    ----------
    image_paths: List[str]
        A list of image file paths.
    cmap: str
        Name of the matplotlig color map to be used. Consult the matplotlib
        documentation for valid values.
    predictor: Kmeans
        A clustering Kmeans trained model for assing a label and color to
        each image bounding box. If None, a pretained model with features:
        width and height, and 20 classes will be used.
    show: bool
        Shows plot. Default is True.
    save_to_file: str
        Path to a PNG file to save the plot. If None, no file is saved.

    Returns
    -------
    None

    """

    images = [Image.open(image_path) for image_path in images] # list of PIL.Image objects

    if predictor:
        k_predictor = predictor
    
    # TODO: Train a store a model with the package.

    # collect image widths and heights to determine
    # image  maximum size
    widths = []
    heights = []
    [ (widths.append(image.width), heights.append(image.height) ) for image in images ]  
    
    # TODO: save to file fails if w or h is higher than 2^16. Restric size.
    max_width = max(widths)
    max_height = max(heights) 

    # Create a figure and axis object
    fig, ax = plt.subplots()
    
    # Set the figure size to the maximum image dimensions
    # fig.set_figwidth(max_width)
    # fig.set_figheight(max_height)

    # make plot set the axis limits
    ax.plot()

    # create color map
    cmap = matplotlib.colormaps[cmap]

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
    [ ( predictions.append( k_predictor.predict( [[ image.width, image.height ]] )),
        pil_images.append(image) ) 
        for image in images
    ]

    # This is used to strech the colors
    # in the color map using the range of
    # values in the prediction
    max_sorted_label = max(sorted_label[predictions])
    min_sorted_label = min(sorted_label[predictions])

    # plot bounding boxes
    for prediction, image in zip(predictions, pil_images):
        # Get the bounding box for the current image
        bbox = image.getbbox() 

        prediction = sorted_label[prediction] # trasforms predicted label to sorted label
        norm_prediction = prediction[0]/( max_sorted_label - min_sorted_label) # notmalize to 0-1
        rgba = cmap(norm_prediction) # assignes color for rectangle

        # Create a rectangle patch for the bounding box
        # Origin is set to center of drawing aread and
        # boxes are drawn concentrically.
        rect = patches.Rectangle((bbox[0] - 0.5 * image.width, bbox[1] - 0.5* image.height), 
                                 image.width, image.height, 
                                 linewidth=2, edgecolor=rgba, 
                                 facecolor='none'
                                 )

        # Plot the bounding box
        ax.add_patch(rect)

        # free some memory. It is convenient with many or large inputs
        del image 

    if save_to_file:
         plt.savefig(save_to_file, dpi=400, bbox_inches='tight')  

    # Show the plot
    if show:
        plt.show()


if __name__ == "__main__":
    
    from sklearn.cluster import KMeans
    import numpy as np


    dims = []
    img_paths = get_image_paths(directory = '/home/manuel/Documents/devel/data/pdf-001')
    
    images = [] # list of PIL.Image objects
    for img in img_paths:
        image = Image.open(img) 
        width = image.width
        height = image.height
        # area = width * height
        dims.append([width, height])
        images.append(image)

    X = np.array(dims)
    # X = X.reshape(-1, 1)
    # print(X)

    k = 20
    kmeans = KMeans(n_clusters=k, random_state=0, n_init='auto').fit(X)

    idx = np.argsort(kmeans.cluster_centers_.sum(axis=1))
    lut = np.zeros_like(idx)
    lut[idx] = np.arange(k)


    # print(type(kmeans))
    # print((lut[kmeans.labels_[0]]))

    plot_boxes(img_paths, predictor= kmeans, save_to_file='./cool-fig.png' )




