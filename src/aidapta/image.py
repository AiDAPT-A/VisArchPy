"""
This script extract images from a PDF file using PyPDF2
Author: M.G. Garcia
"""

import pathlib
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages
from pdfminer.image import ImageWriter
from pdfminer.layout import LTTextContainer, LTTextBoxHorizontal, LTImage, LTFigure

# From https://pypdf2.readthedocs.io/en/latest/user/extract-images.html

def create_output_dir(base_path: str, name="") -> bool:
    """
    creates a directory in the root path if it doesn't exists.

    params:
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


def extract_images_miner(pdf_file: str, output_dir: str) -> None:
    """
    extracts image from a PDF file using PDFMiner
    
    params:
        pdf_file: path to the PDF file
        output_dir: path to directory to extract images. Outputs
        are organized in folder based on the name of the input PDF
    """

    # prepare output directory
    pdf_file_name = pathlib.Path(pdf_file).stem
    output_directory = create_output_dir(output_dir, pdf_file_name)

    iw = ImageWriter(output_directory)

    for page_layout in extract_pages(pdf_file):

        for element in page_layout:
            if isinstance(element, LTFigure):
                for img in element:
                    if isinstance(img, LTImage):
                        print(img)
                        saved_img = iw.export_image(img)
                        print(saved_img)
    
    return None

                    

if __name__ == "__main__":

    pdf_2 ="data-pipelines/data/4563050_AmberLuesink_P5Report_TheRevivaloftheJustCity.pdf"
    out_dir = "data-pipelines/img/pdfminer/"

    extract_images_miner(pdf_2, out_dir)

    pass
