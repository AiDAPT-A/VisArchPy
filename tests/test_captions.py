"""
Units tests for captions.py
Pytest will automatically run all functions that start with test_ in this file.
"""
from visarchpy import captions
import pytest


@pytest.fixture(scope="class")
def bbox_():
    """Fixture for BoundingBox using mm units"""
    return captions.BoundingBox((1, 2, 3, 4), "mm")


@pytest.fixture(scope="class")
def bbox_dpi():
    """Fixture for BoundingBox using dpi units"""
    return captions.BoundingBox((1, 2, 3, 4), 200)


class TestBoundingBox:
    """ Test BoundingBox class"""

    def test_init(self, bbox_):
        """Test BoundingBox init"""
        assert bbox_.coords[0] == 1
        assert bbox_.coords[1] == 2
        assert bbox_.coords[2] == 3
        assert bbox_.coords[3] == 4

    def test_bbox_mm(self, bbox_):
        """ Test BoundingBox with mm units
        returns a tupple with units in points
        """
        assert bbox_.bbox() == (pytest.approx(2.8346456693),
                                pytest.approx(5.6692913386),
                                pytest.approx(8.5039370079),
                                pytest.approx(11.3385826772)
                                )

    def test_bbox_dpi(self, bbox_dpi):
        """ Test BoundingBox with dpi units
        returns a tupple with units in points
        """

        assert bbox_dpi.bbox() == (pytest.approx(0.36),
                                   pytest.approx(0.72),
                                   pytest.approx(1.08),
                                   pytest.approx(1.44)
                                   )

    def test_bbox(self, bbox_):
        """Test BoundingBox bbox method has the correct number of coordinates"""
        assert len(bbox_.bbox()) == 4
