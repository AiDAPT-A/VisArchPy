"""
This script extract images from a PDF file using PyPDF2
Author: M.G. Garcia
"""

import pathlib
import concurrent.futures
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages
from pdfminer.image import ImageWriter
from pdfminer.layout import LTTextContainer, LTPage, LTTextBoxHorizontal, LTImage, LTFigure

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



def generate_figure_from_page(page: LTPage) -> LTFigure:
    """
    a generator to look over LTFigure elements in a page

    Params:
    page: pdf page
    """
    for element in page:
        if isinstance(element, LTFigure):
            for fig in element:
                if isinstance(fig, LTImage):
                    yield fig







def extract_images_miner(pdf_file: str, output_dir: str, min_width: int = None, min_height: int = None) -> None:
    """
    extracts image from a PDF file using PDFMiner
    
    params:
    ----------

        - pdf_file: path to the PDF file
        - output_dir: path to directory to extract images. Outputs
            are organized in folder based on the name of the input PDF
        - min_width: minimum width of the image to be extracted
        - min_height: minimum height of the image to be extracted. If
            None, min_width will be used
    """

    # minimum resolution. Images smaller than this won't be saved
    if min_width is None:
        min_x = 0
    if min_height is None:
        min_y = min_x


    # prepare output directory
    pdf_file_name = pathlib.Path(pdf_file).stem
    output_directory = create_output_dir(output_dir, pdf_file_name)



    pdf_pages = extract_pages(pdf_file)


    def write_image_from_page(page:LTPage, outpu_directory) -> None:
        """
        writes images from a LTPage to a directory
        """

        iw = ImageWriter(output_directory)

        for element in page:
            if isinstance(element, LTFigure):
                for fig in element:
                    if isinstance(fig, LTImage):

                        x, y = fig.srcsize[0], fig.srcsize[1]
                        if x < min_x or y < min_y:
                            continue
                        else:
                            iw.export_image(fig)

    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        page_count = 0
        for page in pdf_pages:
            executor.submit(write_image_from_page, page, output_directory)
            page_count += 1
            print("page", page_count)
    return None

                    
if __name__ == "__main__":

    pdf_2 ="data-pipelines/data/4563050_AmberLuesink_P5Report_TheRevivaloftheJustCity.pdf"
    # has 158283 figure elements
    pdf_3 = "data-pipelines/data/caption-tests/multi-image-caption.pdf"

    out_dir = "data-pipelines/img/pdfminer/"

    extract_images_miner(pdf_2, out_dir)

    pass
