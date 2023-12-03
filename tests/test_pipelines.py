"""
Units tests for pipelines.py
Pytest will automatically run all functions that start with test_ in this file.
"""

import os
from visarchpy.pipelines import start_logging, find_pdf_files
from logging import Logger


def test_start_logging():
    """Test start_logging function"""

    test_log = "tests/data/test.log"
    logger = start_logging(
        "TestLogger", test_log, "00000"
    )
    assert isinstance(logger, Logger)
    assert logger.name == "TestLogger"

    # Clean up
    if os.path.isfile(test_log):
        os.remove(test_log)


def test_find_pdf_files():
    """Test find_pdf_files function"""

    pdf_files = find_pdf_files("tests/data")
    assert isinstance(pdf_files, list)
    assert len(pdf_files) == 1
