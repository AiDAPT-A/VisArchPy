"""
Test for OCR pipeline
"""


import pytest
import visarchpy.ocr as ocr 


def test_convert_pdf_to_images():
    """
    Test convert_pdf_to_images function
    """
    # Fixtures
    pdf_file = './tests/data/multi-image-caption.pdf' 
    dpi = 200

@pytest.fixture(scope="module")
def boxes_inside_boxes():
    return {'id1':[0, 0, 100, 100], 'id2': [200, 300, 350, 400], 'id3': [10, 20, 90, 90],
            'id4':[10, 10, 90, 90], 'id5': [10, 10, 90, 90], 'id6': [10, 10, 15, 20],
            'id7':  [1000, 1000, 1200, 1200], 'id8': [200, 300, 350, 400], 'id9': [200, 300, 350, 400]}

@pytest.fixture(scope="module")
def overlaping_boxes():
    return {'id1':[0, 0, 100, 210], 'id2': [50, 200, 350, 400], 'id7':  [1000, 1000, 1200, 1200]}


def test_filter_bbox_contained(boxes_inside_boxes):
    """
    test contained bounding boxes are removed but when boxes are equal, at least one is kept.
    """
    
    results = {'id1': [0, 0, 100, 100], 'id2': [200, 300, 350, 400], 'id7': [1000, 1000, 1200, 1200], 
               'id3': [10, 20, 90, 90], 'id6': [10, 10, 15, 20]}

    assert ocr.filter_bbox_contained(boxes_inside_boxes) == results
    

def test_filter_bbox_contained_unique(boxes_inside_boxes):
    """
    test if filter_bbox_contained returns only unique bounding boxes
    """

    results = ocr.filter_bbox_contained(boxes_inside_boxes)
    boxes =[ results[box] for box in results]

    for box in boxes:
        assert boxes.count(box) == 1

def test_filter_bbox_contained_overlaps(overlaping_boxes):
    """
    test if filter_bbox_contained keeps overlapping bounding boxes
    """

    assert ocr.filter_bbox_contained(overlaping_boxes) == overlaping_boxes
