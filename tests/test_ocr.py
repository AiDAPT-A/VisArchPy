"""
Test for OCR pipeline
"""

import PIL

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
    images = ocr.convert_pdf_to_images(pdf_file, dpi) # TODO: fix function doesn't find pdf_file

    # # Assertions
    # assert isinstance(images, list)
    # assert all([isinstance(image, PIL.PpmImagePlugin.PpmImageFile) for image in images])

