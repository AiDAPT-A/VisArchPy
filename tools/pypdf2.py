"""
This script extract images from a PDF file using PyPDF2
Author: M.G. Garcia
"""

from PyPDF2 import PdfReader
import pathlib

# From https://pypdf2.readthedocs.io/en/latest/user/extract-images.html

def create_output_dir(base_path: str, name: str) -> bool:
    """
    creates a directory in the root path if it doesn't exists.

    params:
        base_path: path to destination directory
        name: name for the directory
    returns:
        path to the new created directory
    """

    full_path = base_path + name

    print(full_path)
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

    # print(len(reader.pages))
    # extract images per page


    for page_index in range(0,len(reader.pages)):
        page = reader.pages[page_index]

        # TODO: fix issue with ValueError: not enough data in PIL
        try:
            count=1
            print('page/img index', page_index, count)
       
            for image_file_object in page.images:
                with open(str(output_directory)+'/' + 'page' +str(page_index) +'-'+str(count) + image_file_object.name, "wb") as fp:
                    fp.write(image_file_object.data)
                    count += 1
        except ValueError:
            pass

    return None


if __name__ == "__main__":

    pdf_classic = "data/RethinkWaste_research_paper_LisaUbbens_4397436.pdf"
    pdf2 = "data/4563050_AmberLuesink_P5Report_TheRevivaloftheJustCity.pdf"
    img_dir = "./img/pyPDF2/"

    extract_images(pdf_classic, img_dir)
    # extract_images(pdf2, img_dir)

    
    
    

