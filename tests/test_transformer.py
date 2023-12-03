"""
Unit tests for dinov2/transformer.py
"""

import pytest
from transformers.modeling_outputs import BaseModelOutputWithPooling 
from torch import Tensor
from visarchpy.dino.transformer import transform_to_dinov2


@pytest.fixture(scope='class')
def image_file():
    """
    Fixture for the outputs object
    """
    return 'tests/data/test_image.jpg'

@pytest.fixture(scope='class')
def dinov2_model():
    """
    Fixture for the outputs object
    """
    return 'facebook/dinov2-small'

def test_output_type(image_file, dinov2_model):
    """
    Test that the output is a dictionary containing a tensor and an python 
    object (BaseModelOutputWithPooling)
    """

    outputs = transform_to_dinov2(image_file, dinov2_model)

    assert isinstance(outputs, dict)
    assert isinstance(outputs['tensor'], Tensor)
    assert isinstance(outputs['object'], BaseModelOutputWithPooling)

def test_output_tensor_dimmensions(image_file, dinov2_model):
    """
    Test that the output is a tensor with the correct number or dimensions (2)
    """

    outputs = transform_to_dinov2(image_file, dinov2_model)

    assert outputs['tensor'].ndim == 2

