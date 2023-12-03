"""
Units tests for utils.py
Pytest will automatically run all functions that start with test_ in this file.
"""

import warnings
from visarchpy import utils
import pytest


def test_convert_mm_to_point():
    """Test convert_mm_to_point function"""
    assert utils.convert_mm_to_point(1) == pytest.approx(2.8346456693)
    assert utils.convert_mm_to_point(2) == pytest.approx(5.6692913386)
    assert utils.convert_mm_to_point(3) == pytest.approx(8.5039370079)
    assert utils.convert_mm_to_point(4) == pytest.approx(11.3385826772)
    assert utils.convert_mm_to_point(5) == pytest.approx(14.1732283465)
    assert utils.convert_mm_to_point(6) == pytest.approx(17.0078740158)
    assert utils.convert_mm_to_point(7) == pytest.approx(19.842519685)
    assert utils.convert_mm_to_point(8) == pytest.approx(22.6771653543)
    assert utils.convert_mm_to_point(9) == pytest.approx(25.5118110236)
    assert utils.convert_mm_to_point(10) == pytest.approx(28.3464566929)


def test_convert_dpi_to_point():
    """Test convert_dpi_to_point function"""

    assert utils.convert_dpi_to_point(1, 1) == pytest.approx(72)
    assert utils.convert_dpi_to_point(1, 2) == pytest.approx(36)
    assert utils.convert_dpi_to_point(1, 3) == pytest.approx(24)
    assert utils.convert_dpi_to_point(1, 4) == pytest.approx(18)
    assert utils.convert_dpi_to_point(1, 5) == pytest.approx(14.4)


