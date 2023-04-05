"""
This script extract images from a PDF file using PyPDF2
Author: M.G. Garcia
"""

import pathlib
import concurrent.futures
import time
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages
from pdfminer.image import ImageWriter
from pdfminer.layout import (
    LTTextContainer, 
    LTPage, 
    LTItem, 
    LTTextBox,
    LTText,
    LTContainer, 
    LTTextBoxHorizontal, 
    LTImage, 
    LTFigure
)

from aidapta.captions import find_caption_by_text, find_caption_by_bbox

# From https://pypdf2.readthedocs.io/en/latest/user/extract-images.html

def create_output_dir(base_path: str, name="") -> bool:
    """
    creates a directory in the root path if it doesn't exists.

    params:
    ----------
        base_path: path to destination directory
        name: name for the directory. If left empty, no directory will be created, 
        and the base_path will be returned 
    returns:
        path to the new created directory
    """

    full_path = base_path + name
    pathlib.Path(full_path).mkdir(parents=True, exist_ok=True)

    return pathlib.Path(full_path)


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
    sorts LTTexContainer and LTImage elements from a PDF file using PDFMiner

    params:
    ----------
        pdf_file: path to the PDF file
        img_width: minimum width of an image to be extracted
        img_height: minimum height of an image to be extracted. If
            None, img_width will be used

    returns:    
        dictionary with LTTextContainer and LTImage elements
    """
    if img_width is None:
        img_width = 0
    if img_height is None:
        img_height = img_width
    
    page_number = page.pageid  # page number on the PDF file, starts at 1
    # This is not the same as the index of the page in the list of pages

    text_elements = []
    image_elements = []

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
        elif isinstance(item, LTImage):
            x, y = item.srcsize[0], item.srcsize[1]
            if x < img_width or y < img_height:
                pass
            else:
                image_elements.append(item)

    render(page)

    return {"page_number": page_number, "texts": text_elements, "images": image_elements}




def write_image_from_page(page:LTPage, output_directory, min_x = 0, min_y = 0) -> None:
    """
    writes images from a LTPage to a directory
    """

    iw = ImageWriter(output_directory)

    element_count = 0
    for element in page:
        if isinstance(element, LTFigure):
            for fig in element:
                if isinstance(fig, LTImage):
                    print("image", fig)

                    x, y = fig.srcsize[0], fig.srcsize[1]
                    if x < min_x or y < min_y:
                        continue
                    else:
                        iw.export_image(fig)
        element_count += 1

    print(f"Processed {element_count} elements in page")

    return None


def extract_images_miner(pdf_file: str, output_dir: str, img_width: int = None, img_height: int = None) -> None:
    """
    extracts image from a PDF file using PDFMiner
    
    params:
    ----------

        - pdf_file: path to the PDF file
        - output_dir: path to directory to extract images. Outputs
            are organized in folder based on the name of the input PDF
        - img_width: minimum width of the image to be extracted
        - img_height: minimum height of the image to be extracted. If
            None, img_width will be used
    """

    # minimum resolution. Images smaller than this won't be saved
    if img_width is None:
        img_width = 0
    if img_height is None:
        img_height = img_width

    # prepare output directory
    pdf_file_name = pathlib.Path(pdf_file).stem
    output_directory = create_output_dir(output_dir, pdf_file_name)


    st = time.time()

    pdf_pages = extract_pages(pdf_file)

    page_count = 0
    for page in pdf_pages:
        write_image_from_page(page, output_directory, img_width, img_height)
        page_count += 1

        print("pages", page_count)

    et = time.time()

    print("time, milliseconds", (et-st)*1000)


    return None
                    
                    
if __name__ == "__main__":

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

    # extract_images_miner(pdf_3, out_dir, img_width=100, img_height=100)

    
