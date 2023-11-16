"""
A library for the extraction of images from a PDF file that performs
document layout analysis using PDFMiner.
The layout analysis check the type of elements in a PDF page recursively
and returns the elements that are images, texts, and vectors (not implemented).
Author: M.G. Garcia
"""
import os
import pathlib
# from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages
from visarchpy.utils import create_output_dir
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


# TODO: test if this code can be removed. It belongs to the old version of the code
# def extract_images(pdf_file: str, output_dir: str) -> None:
#     """
#     extracts image from a PDF file
    
#     Parameters
#     ----------
#     pdf_file: str
#         path to the PDF file
#     output_dir: str 
#         path to directory to extract images. Outputs
#         are organized in folder based on the name of the input PDF
    
#     Returns
#     -------
#     None
#     """
    
#     # open PDF document
#     reader = PdfReader(pdf_file)

#     # prepare output directory
#     pdf_file_name = pathlib.Path(pdf_file).stem
#     output_directory = create_output_dir(output_dir, pdf_file_name)

#     for page_index in range(0,len(reader.pages)):
#         page = reader.pages[page_index]

#         # TODO: fix issue with ValueError: not enough data in PIL
#         try:
#             count=1
#             print('page/img index', page_index, count)
       
#             for image_file_object in page.images:
#                 print(image_file_object)
                
#                 with open(str(output_directory)+'/' + 'page' +str(page_index) +'-'+str(count) + 
#                           image_file_object.name, "wb") as fp:
#                     fp.write(image_file_object.data)
#                     count += 1
#         except ValueError:
#             print("error")

#     return None


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
    pdf_file: LTPage
        path to the PDF file
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

                    
if __name__ == "__main__":
    from visarchpy.captions import find_caption_by_text, find_caption_by_distance

    pdf_2 ="data-pipelines/data/4563050_AmberLuesink_P5Report_TheRevivaloftheJustCity.pdf"
    # has 158283 figure elements
    pdf_3 = "data-pipelines/data/caption-tests/multi-image-caption.pdf"

    out_dir = "data-pipelines/img/pdfminer/"

    pages = extract_pages(pdf_3)

    for page in pages:
        elements=sort_layout_elements(page, img_width=100, img_height=100)
        # print(elements)
        for img in elements["images"]:
            for _text in elements["texts"]:
                match = find_caption_by_distance(img, _text, offset_distance=10, direction="down")
                if match:
                    print(img, _text)
