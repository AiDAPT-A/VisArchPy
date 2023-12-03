"""
A library for the extraction of images from a PDF file that performs
document layout analysis using PDFMiner.
The layout analysis check the type of elements in a PDF page recursively
and returns the elements that are images, texts, and vectors (not implemented).
Author: M.G. Garcia
"""

from pdfminer.high_level import extract_pages
from pdf2image import convert_from_path
from typing import Any

from pdfminer.layout import (
    LTPage,
    LTItem,
    LTTextBox,
    LTText,
    LTContainer,
    LTImage,
    LTFigure,
    LTCurve
)


def sort_layout_elements(
        page: LTPage,
        img_width: int = None,
        img_height: int = None) -> dict:
    """
    sorts elements by type (LTTextContainer,
    LTImage, LTFigure, and LTCurve) on a
    single PDF page using PDFMiner.six

    Parameters
    ----------
    page: LTPage
        LTPage object from PDFMiner.six
    img_width: int
        minimum width of image to be extracted. If
        None,  a value of 0 will be used
    img_height: int
        minimum height of image to be extracted. If
        None, img_width will be used

    Returns
    -------
    dict
        dictionary with LTTextContainer, LTImage, and LTCurve elements
    """

    if img_width is None:
        img_width = 0
    if img_height is None:
        img_height = img_width
    page_number = page.pageid  # page number on the PDF file, starts at 1
    # This is not the same as the index in the document

    text_elements = []
    image_elements = []
    vector_elements = []

    # From pdfminer six#
    def render(item: LTItem) -> None:
        if isinstance(item, LTContainer):
            for child in item:
                render(child)
        elif isinstance(item, LTText):
            pass
        if isinstance(item, LTTextBox):
            text_elements.append(item)
        elif isinstance(item, LTFigure) or isinstance(item, LTCurve):
            vector_elements.append(item)
        elif isinstance(item, LTImage):
            x, y = item.srcsize[0], item.srcsize[1]
            if x < img_width or y < img_height:
                pass
            else:
                image_elements.append(item)

    render(page)

    return {"page_number": page_number, "texts": text_elements,
            "images": image_elements,
            "vectors": vector_elements}



def convert_pdf_to_image(pdf_file: str,
                         dpi: int = 200,
                         **kargs) -> list[Any]:
    """
    Convert PDF file to image, one page at a time.

    Parameters
    ----------
    pdf_file: str
        path to PDF file
    dpi: int
        resolution of the output image
    kargs:
        additional arguments for the convert_from_path function from pdf2image
        package. For example, first_page and last_page can be used to specify
        the range of pages to convert.

    Returns
    --------
    list of images
        List of images. Each element in the list must be a Pillow Image object.

    """

    if 'first_page' in kargs and 'last_page' in kargs:

        first_page = kargs['first_page']
        last_page = kargs['last_page']
        return convert_from_path(pdf_file, dpi=dpi, first_page=first_page,
                                 last_page=last_page)
    else:
        return convert_from_path(pdf_file, dpi=dpi)



if __name__ == "__main__":
    
    from visarchpy.captions import find_caption_by_distance
    # has 158283 figure elements
    pdf_3 = "data-pipelines/data/caption-tests/multi-image-caption.pdf"

    out_dir = "data-pipelines/img/pdfminer/"

    pages = extract_pages(pdf_3)

    for page in pages:
        elements = sort_layout_elements(page, img_width=100, img_height=100)
        # print(elements)
        for img in elements["images"]:
            for _text in elements["texts"]:
                match = find_caption_by_distance(img, _text, offset_distance=10, direction="down")
                if match:
                    print(img, _text)

    PDF_FILE = 'tests/data/multi-image-caption.pdf'
    OUTPUT_DIR = 'tests/data'
    images = convert_pdf_to_image(PDF_FILE, dpi=200)

    # print(images[0])

    region = [1000, 500, 2000, 1000]

