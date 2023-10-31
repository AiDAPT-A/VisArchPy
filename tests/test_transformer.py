"""
Unit tests for dinov2/transformer.py
"""

import pytest

from aidapta.dinov2.transformer import save_pickle_dinov2, load_pickle_dinov2, transform_to_dinov2


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

    
def test_transfor_to_dinov2(image_file, dinov2_model):
    """
    Test that the output is a tensor with the correct number or dimensions (2)
    """

    outputs = transform_to_dinov2(image_file, dinov2_model)

    assert outputs.ndim == 2

