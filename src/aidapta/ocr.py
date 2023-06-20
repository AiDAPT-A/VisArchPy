'''OCR pipeline with Tesseract
Author: Manuel Garcia

This pipeline extract images by performing OCR (Tesseract) on PDF files.
The pipeline is based on the following steps:
1. Convert PDF file to image, one page at a time
2. Extract OCR data as hOCR document
3. Extract bounding boxes for non-text regions from hOCR document
4. Crop images based on bounding boxes
5. Save cropped images to output directory
'''

import pytesseract
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL.Image import Image




def convert_pdf_to_images(pdf_file: str, dpi:int = 200)-> list[Image]:
    """
    Convert PDF file to image, one page at a time.
    params:
    '''''''''''
    pdf_file: path to PDF file
    dpi: resolution of the output image
    returns:
    '''''''''''
    List of images as Pillow Image
    """
    return convert_from_path(pdf_file, dpi=dpi)


def extract_bbox_from_horc(images: list[Image], config: str ='--oem 1 --psm 1') -> dict:
    """
    Extract bounding boxes for non-text regions from hOCR document.
    params:
    '''''''''''
    images: list of images as Pillow Image
    config: tesseract config options
    returns:
    '''''''''''
    Dictionary with bounding boxes and ids for non-text regions
    """
    _config = config + ' hocr'

    for img in images:
        horc_data = pytesseract.image_to_pdf_or_hocr(img, extension='hocr', config=_config)
        soup = BeautifulSoup(horc_data, 'html.parser')
        paragraphs = soup.find_all('p', class_='ocr_par')
        paragraphs_bounding_boxes = []
        paragraphs_ids = []
        # paragraph_confidence_scores = []
        # boxed_paragraphs = []
        for paragraph in paragraphs:
            title = paragraph.get('title')
            id = paragraph.get('id')
            # used to if paragraph contains text
            text_element = paragraph.find('span', {'class': 'ocrx_word'})
            text =text_element.get_text()

            if title and text.strip() == "":
                bounding_box = title.split(';')[0].split(' ')[1:]
                bounding_box = [int(value) for value in bounding_box]
                paragraphs_bounding_boxes.append(bounding_box)
                paragraphs_ids.append(id)
                
    return {'bboxes': paragraphs_bounding_boxes, 'ids': paragraphs_ids}


# Convert PDF to image
IMAGES = convert_from_path('data-pipelines/data/caption-tests/multi-image-caption.pdf', dpi=300)
OUTPUT_DIR = 'data-pipelines/data/ocr-test'

# tessaeract options
config = r'--oem 1 --psm 1 hocr' # Engine Neural nets LSTM only. Auto page segmentation with OSD

page_counter = 1
# Extract OCR data as hOCR document
print('total pages', len(IMAGES))
for img in IMAGES:
    horc_data = pytesseract.image_to_pdf_or_hocr(img, extension='hocr', config=config)
    soup = BeautifulSoup(horc_data, 'html.parser')
    paragraphs = soup.find_all('p', class_='ocr_par')
    print('working_image', page_counter)
    paragraphs_bounding_boxes = []
    paragraphs_ids = []
    # paragraph_confidence_scores = []
    # boxed_paragraphs = []
    for paragraph in paragraphs:
        title = paragraph.get('title')
        id = paragraph.get('id')
        # used to if paragraph contains text
        text_element = paragraph.find('span', {'class': 'ocrx_word'})
        text =text_element.get_text()

        if title and text.strip() == "":
            bounding_box = title.split(';')[0].split(' ')[1:]
            bounding_box = [int(value) for value in bounding_box]
            paragraphs_bounding_boxes.append(bounding_box)
            paragraphs_ids.append(id) 
        
    # for bounding_box, id in zip(paragraphs_bounding_boxes, paragraphs_ids):
    #     x, y, w, h = bounding_box
    #     cropped_image = img.crop((x, y, w, h))
        # cropped_image.save(f'data-pipelines/data/ocr-test/image-{id}.jpg')

##########################################
# Plotting bounding boxes

    fig, ax = plt.subplots(1)

    plt.axis('off')
    # Display the image
    ax.imshow(img)

    # Create a Rectangle patch
    for bounding_box, id in zip(paragraphs_bounding_boxes, paragraphs_ids):
        x, y, w, h = bounding_box
        rect = patches.Rectangle((x, y), w - x, h - y, linewidth=2, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        tag_text = id
        tag_x = x
        tag_y = y
        plt.text(tag_x, tag_y, tag_text, fontsize=10, color='blue', ha='left', va='center')

    plt.savefig(f'{OUTPUT_DIR}/page-{page_counter}.png', dpi=200, bbox_inches='tight')
    
    page_counter += 1
    plt.close()
    # plt.show()
print('finished')
