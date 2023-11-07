"""
Convenience functions for analysing data produced byt the pipelines
Author: M.G. Garcia
"""

import os
from PIL import Image
from typing import List
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




def plot_bounding_boxes(image_paths: List[str], transparency: float =0.25) -> None:
    """
    Plots the bounding boxes of a list of images overlapping on the same plot.

    Parameters
    ----------
    image_paths: List[str]
        A list of image file paths.
    transparency: float
        The transparency of drawing lines. A value between 0 and 1. Default is 0.25.

    Returns
    -------
    None

    :param image_paths: A list of image file paths.
    """


    images = [] # list of PIL.Image objects
    image_widths = []
    image_heights = []
    for image_path in image_paths:
        # Open the image file using Pillow
        image = Image.open(image_path)
        image_widths.append(image.width)
        image_heights.append(image.height)
        images.append(image)

    # Create a figure and axis object
    fig, ax = plt.subplots()
    
    # Set the figure size to the maximum image dimensions
    fig.set_figwidth(max(image_widths))
    fig.set_figheight(max(image_heights))

    # Plot a dummy point to set the axis limits
    ax.plot([1, 1])

    # Loop through the image paths and bounding boxes
    for image in images:
        # Get the bounding box for the current image
        bbox = image.getbbox() 
        width = image.width
        height = image.height
        center = (image.width/2, image.height/2)

        # Create a rectangle patch for the bounding box
        # Origin is set to drwaing concentric rectangles 
        rect = patches.Rectangle((bbox[0] - 0.5*width, bbox[1] - 0.5*height), width, height, 
                                 linewidth=2, edgecolor=(1, 0, 0, transparency), 
                                 facecolor='none')

        # Plot the bounding box
        ax.add_patch(rect)
    # Show the plot
    plt.show()




def plot_boxes(images: List, kmeans, transparency: float =0.25) -> None:
    """
    Plots the bounding boxes of a list of images overlapping on the same plot.

    Parameters
    ----------
    image_paths: List[str]
        A list of image file paths.
    transparency: float
        The transparency of drawing lines. A value between 0 and 1. Default is 0.25.

    Returns
    -------
    None

    :param image_paths: A list of image file paths.
    """


    # images = [] # list of PIL.Image objects
    image_widths = []
    image_heights = []
    for image_ in images:
        # Open the image file using Pillow
        # image = Image.open(image_path)
        image_widths.append(image_.width)
        image_heights.append(image_.height)
        

    # Create a figure and axis object
    fig, ax = plt.subplots()
    
    # Set the figure size to the maximum image dimensions
    fig.set_figwidth(max(image_widths))
    fig.set_figheight(max(image_heights))

    # Plot a dummy point to set the axis limits
    ax.plot([1, 1])

    import matplotlib 
    cmap = matplotlib.cm.get_cmap('copper')

    # Loop through the image paths and bounding boxes
    for image in images:
        # Get the bounding box for the current image
        bbox = image.getbbox() 
        width = image.width
        height = image.height
        center = (image.width/2, image.height/2)

        # TODO: check if color ramp is normalized correctly. small boxes are same color as big boxes
        prediction = kmeans.predict([[width, height]])
        norm_prediction = prediction[0]/(9-0) # notmalize to 0-1
        rgba = cmap(norm_prediction)

        # print("prediction:", prediction, norm_prediction)

        # Create a rectangle patch for the bounding box
        # Origin is set to drwaing concentric rectangles 
        rect = patches.Rectangle((bbox[0] - 0.5*width, bbox[1] - 0.5*height), width, height, 
                                 linewidth=2, edgecolor=rgba, 
                                 facecolor='none')

        # Plot the bounding box
        ax.add_patch(rect)
    # Show the plot
    plt.show()
    
    # TODO: continue test with data from data pipeline

    


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

    kmeans = KMeans(n_clusters=10, random_state=0, n_init='auto').fit(X)
  

    plot_boxes(images, kmeans, transparency=0.25)




