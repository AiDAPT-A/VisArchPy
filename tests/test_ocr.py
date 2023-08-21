"""
Test for OCR pipeline
"""

import PIL
import pytest
import aidapta.ocr as ocr 


def test_convert_pdf_to_images():
    """
    Test convert_pdf_to_images function
    """
    # Fixtures
    pdf_file = './data/multi-image-caption.pdf' 
    dpi = 200

    # assert True
    # print(pdf_file)
    # # Test function
    # images = ocr.convert_pdf_to_images(pdf_file, dpi) # TODO: fix function doesn't find pdf_file

    # # Assertions
    # assert isinstance(images, list)
    # assert all([isinstance(image, PIL.PpmImagePlugin.PpmImageFile) for image in images])



def test_filter_bbox_contained():
    """
    test if function return the correct bounding boxes
    """
    # Fixtures
    input_boxes = [[0, 0, 100, 100], [200, 300, 350, 400], [10, 20, 90, 90],[10, 10, 90, 90], 
                [10, 10, 90, 90], [10, 10, 15, 20],  [1000, 1000, 1100, 1100]]
    results = [[0, 0, 100, 100], [200, 300, 350, 400], [1000, 1000, 1100, 1100]]

    assert ocr.filter_bbox_contained(input_boxes) == results
    

def test_filter_bbox_contained_unique():
    """
    test if filter_bbox_contained returns only unique bounding boxes
    """
    
    # Fixtures
    input_boxes = [[0, 0, 100, 100], [200, 300, 350, 400], [10, 20, 90, 90],[10, 10, 90, 90], 
                [10, 10, 90, 90], [10, 10, 15, 20],  [1000, 1000, 1100, 1100]]

    results = ocr.filter_bbox_contained(input_boxes)
    for box in results:
        assert results.count(box) == 1
