"""
Test for pdf.py
"""


import pytest
from pdfminer import high_level
import visarchpy.pdf as pdf


def test_extract_pages():
    """
    Test extract_pages function
    """
    pdf_file = "./tests/data/multi-image-caption.pdf"
    pages = high_level.extract_pages(pdf_file)
    print(pages)

    [results := pdf.sort_layout_elements(page) for page in pages]

    assert isinstance(results, dict)
    assert len(results) == 4
    assert "page_number" in results
    assert "texts" in results
    assert "images" in results
    assert "vectors" in results
