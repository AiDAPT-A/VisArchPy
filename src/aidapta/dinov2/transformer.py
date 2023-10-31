"""
Utility functions to extract image features using DINOv2 
https://github.com/facebookresearch/dinov2

"""

import torch
import pickle
import numpy as np
import pandas as pd
from torch import Tensor
from transformers import AutoImageProcessor, AutoModel
from transformers.modeling_outputs import BaseModelOutputWithPooling 
from PIL import Image


def save_pickle_dinov2(pickle_filename: str, model_outputs: BaseModelOutputWithPooling) -> None:
    """
    Save outputs of dinov2 model to a file.

    Parameters
    ----------
    pickle_filename : str
        Path to pickle file
    outputs : BaseModelOutputWithPooling
        Pickle file with outputs object of dinov2 model. File willl be saved 
        to the same directory as the image file, and with the same name as the
        image file.

    Returns
    -------
    None
    """

    if not isinstance(model_outputs, BaseModelOutputWithPooling):
        raise TypeError("outputs must be a BaseModelOutputWithPooling object generated by the transfomers package. \
                        Got {type(outputs)}")
    
    with open(pickle_filename, 'wb') as f:
        pickle.dump(model_outputs, f)

    return None


def load_pickle_dinov2(pickle_filename: str) -> BaseModelOutputWithPooling:
    """
    Load outputs of dinov2 model from a file.

    Parameters
    ----------
    pickle_filename : str
        Path to pickle file

    Returns
    -------
    outputs : BaseModelOutputWithPooling
        Outputs of dinov2 model according to the 'transformers' package data classes. 
        A Python object
    """

    with open(pickle_filename, 'rb') as f:
        content = pickle.load(f)

    return content


def save_csv_dinov2(csv_filename: str, tensor:Tensor) -> None:
    """
    Save pytorch tensor (2D) to a csv file formatted as a Pandas dataframe.

    Parameters
    ----------
    csv_filename : str
        Path to csv file
    tensor : Tensor
        2D tensor to be saved to csv file.

    Returns
    -------
    None

    Raises
    ------
    TypeError
        If tensor is not a pytorch Tensor object.
    ValueError
        If tensor is not a 2D pytorch Tensor object.
    """

    if not isinstance(tensor, Tensor):
        raise TypeError("tensor must be a pytorch Tensor object. \
                        Got {type(tensor)}")
    
    if tensor.ndim != 2:
        raise ValueError("tensor must be a 2D pytorch Tensor object. \
                        Got {tensor.ndim}")
    
    # convert tensor to pandas dataframe
    df = pd.DataFrame(tensor.detach().numpy())
    # save to csv file
    df.to_csv(csv_filename, sep=',', index=False, encoding='utf-8')

    return None


def transform_to_dinov2(image_file: str, model_name: str) -> Tensor:
    """
    Extract features from an image using DINOv2 model.

    Parameters
    ----------
    image_file : str
        Path to image file. 
    model_name : str
        pretrained DINOv2 model name (e.g. 'facebook/dinov2-small')

    Returns
    -------
    outputs : Tensor 
        Last hidden state of DINOv2 model. Dimension with size 1 are removed.
    """

    image = Image.open(image_file)

    processor = AutoImageProcessor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    inputs = processor(images=image, return_tensors="pt") 
    outputs = model(**inputs)

    output_tensor = outputs.last_hidden_state

    # remove dimensions of size 1, i.e. squeeze tensor
    squeezed_tensor = torch.squeeze(output_tensor)

    return squeezed_tensor



