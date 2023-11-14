"""
Units tests for analytics.py
Pytest will automatically run all functions that start with test_ in this file.
"""


from visarchpy import analytics
import pytest
import os



@pytest.fixture(scope='class')
def image_directory():
    """
    Fixture of a directory containing image files
    """
    return 'tests/data'


class TestGetImagePaths:
    """Test class for analytics.py"""

    def test_without_extensions(self, image_directory):
        """Test get_image_paths without extensions argument"""
        result = analytics.get_image_paths(image_directory)
        assert result == [os.path.join(image_directory, file) for file in os.listdir(image_directory)]


    def test_with_extensions(self, image_directory):
        """Test get_image_paths with extensions argument
        Test for .jpg extension
        """
        result = analytics.get_image_paths("tests/data", extensions =['jpg'])

        print(result)
        assert result == [os.path.join(image_directory, file) for file in os.listdir(image_directory) if file.endswith('.jpg')]


