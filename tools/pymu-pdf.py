import fitz
import io
from PIL import Image
import pathlib
import fitz 


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
    pdf_doc = fitz.open(pdf_file) 

    # prepare output directory
    pdf_file_name = pathlib.Path(pdf_file).stem
    output_directory = create_output_dir(output_dir, pdf_file_name)
    print(output_directory)

    for page in range(len(pdf_doc)):
        # Check if page contains images
        this_page = pdf_doc[page]
        images = this_page.get_images()
        # print(images)

        if images:
            print(f'found {len(images)} images on page {page}')
        else:
            print('found no images on page', page)
        
        # Extract images
        for image_index, img in enumerate(images, start=1):
            xref = img[0] # the count

            ext_image = pdf_doc.extract_image(xref) # returns dictionary
            # keys: ['ext', 'smask', 'width', 'height', 'colorspace', 'bpc', 'xres', 'yres', 'cs-name', 'image']
            # print(type(ext_image))
            image_bytes = ext_image["image"]
            image_extension = ext_image["ext"]

            # Save images using PIL
            image_out = Image.open(io.BytesIO(image_bytes))
            image_out.save(open(f"{output_directory}/image{ page }-{image_index}.{image_extension}", "wb"))


if __name__ == "__main__":

    pdf_classic = "data/RethinkWaste_research_paper_LisaUbbens_4397436.pdf"
    pdf2 = "data/4563050_AmberLuesink_P5Report_TheRevivaloftheJustCity.pdf"
    img_dir = "./img/pymuPDF/"


    # extract_images(pdf_classic, img_dir)
    extract_images(pdf2, img_dir)






        
    

    


# for i in range(len(doc)): 
#     for img in doc.getPageImageList(i): 
#         xref = img[0] 
#         pix = fitz.Pixmap(doc, xref) 
#         if pix.n < 5:       # this is GRAY or RGB 

#             pix.writePNG("p%s-%s.png" % (i, xref)) 
#         else:               # CMYK: convert to RGB first 
#             pix1 = fitz.Pixmap(fitz.csRGB, pix) 
#             pix1.writePNG("p%s-%s.png" % (i, xref)) 
#             pix1 = None 

#         pix = None 