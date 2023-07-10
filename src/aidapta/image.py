"""
This script extract images from a PDF file using PyPDF2
Author: M.G. Garcia
"""
import os
import pathlib
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages
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

# From https://pypdf2.readthedocs.io/en/latest/user/extract-images.html

def create_output_dir(base_path: str, path="") -> bool:
    """
    creates a directory in the root path if it doesn't exists.

    params:
    ----------
        base_path: path to destination directory
        name: name  or path for the new directory, parent directories are created if they don't exists
    returns:
        relative path to the new created directory
    """

    if isinstance(base_path, pathlib.Path):
        base_path = str(base_path)
    full_path = os.path.join(base_path, path)
    pathlib.Path(full_path).mkdir(parents=True, exist_ok=True)

    return pathlib.Path(path)


def extract_images(pdf_file: str, output_dir: str) -> None:
    """
    extracts image from a PDF file
    
    params:
    ----------
        pdf_file: path to the PDF file
        output_dir: path to directory to extract images. Outputs
        are organized in folder based on the name of the input PDF
    """
    
    # open PDF document
    reader = PdfReader(pdf_file)

    # prepare output directory
    pdf_file_name = pathlib.Path(pdf_file).stem
    output_directory = create_output_dir(output_dir, pdf_file_name)

    for page_index in range(0,len(reader.pages)):
        page = reader.pages[page_index]

        # TODO: fix issue with ValueError: not enough data in PIL
        try:
            count=1
            print('page/img index', page_index, count)
       
            for image_file_object in page.images:
                print(image_file_object)
                
                with open(str(output_directory)+'/' + 'page' +str(page_index) +'-'+str(count) + image_file_object.name, "wb") as fp:
                    fp.write(image_file_object.data)
                    count += 1
        except ValueError:
            print("error")

    return None


def sort_layout_elements(page:LTPage, img_width = None, img_height = None)-> dict:
    """
    sorts LTTextContainer, LTImage, LTFigure, and LTCurve elements from a single PDF page using PDFMiner.six

    params:
    ----------
        pdf_file: path to the PDF file
        img_width: minimum width of an image to be extracted
        img_height: minimum height of an image to be extracted. If
            None, img_width will be used

    returns:    
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
            # TODO: check how using text boxes affects the results of caption extraction
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

    return {"page_number": page_number, "texts": text_elements, "images": image_elements, "vectors": vector_elements}

                    
if __name__ == "__main__":
    from aidapta.captions import find_caption_by_text, find_caption_by_bbox

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
                match = find_caption_by_bbox(img, _text, offset=10, direction="down")
                if match:
                    print(img, _text)
