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
    --------
    pdf_file: path to PDF file
    dpi: resolution of the output image

    returns:
    --------
    List of images as Pillow Image
    """
    return convert_from_path(pdf_file, dpi=dpi)


def extract_bboxes_from_horc(images: list[Image], config: str ='--oem 1 --psm 1') -> dict:
    """
    Extract bounding boxes for non-text regions from hOCR document.

    params:
    --------
    images: list of images as Pillow Image
    config: tesseract config options. Default: --oem 1 --psm 1. Engine Neural nets LSTM only. Auto page segmentation with OSD
    
    returns:
    ----------
    Dictionary with bounding boxes and ids for non-text regions
    Example:
    {'page': {'img': None, 'bboxes': [], 'ids': []} }
    """
    _config = config + ' hocr'

    results = {}
    page_counter = 1
    for img in images:
        horc_data = pytesseract.image_to_pdf_or_hocr(img, extension='hocr', config=_config)
        soup = BeautifulSoup(horc_data, 'html.parser')
        paragraphs = soup.find_all('p', class_='ocr_par')
        non_text_bboxes = [] 
        paragraphs_ids = []
        # paragraph_confidence_scores = []
        # boxed_paragraphs = []
        for paragraph in paragraphs:
            title = paragraph.get('title')
            id = paragraph.get('id')
            # use to check if paragraph contains text
            text_element = paragraph.find('span', {'class': 'ocrx_word'})
            text =text_element.get_text()

            if title and text.strip() == "":
                bounding_box = title.split(';')[0].split(' ')[1:]
                bounding_box = [int(value) for value in bounding_box]
                non_text_bboxes.append(bounding_box)
                paragraphs_ids.append(id)

        results[f'page-{page_counter}'] = {'img': img, 'bboxes': non_text_bboxes, 'ids': paragraphs_ids}
        page_counter += 1
    return results


def crop_images_to_bbox(images:list[Image], bbox: list[list[int]], 
                       ids:list, output_dir:str ) -> None:
    """
    Crop images based on bounding boxes. Croped images are saved to output 
    directory as JPG files.

    params:
    --------

    image: Pillow Image or list of Pillow Image objects
    bbox: bounding box as list [x, y, width, height] or list of bounding boxes
    output_dir: path to output directory for cropped images
    ids: id or list of ids for cropped images

    returs:
    --------
    None
    """

    if isinstance(images, list) and isinstance(bbox, list) and isinstance(ids, list):
        if len(images) == len(bbox) == len(ids): # TODO: check if all variables must be the same length
            for img, bounding_box, id in zip(images, bbox, ids):
                x, y, w, h = bounding_box
                cropped_image = img.crop((x, y, w, h))
                cropped_image.save(f'{output_dir}/image-{id}.jpg')
        else:
            raise ValueError('images, bbox, and ids must be of same length')

    else:
        raise TypeError('images, bbox, and ids must be of type list')

    return None


def marked_bounding_boxes(images: list[Image], bbox:list[list[int]], output_dir:str, ids:list=None) -> None:
    """
    Draw bounding boxes of on input images and save a copy to output directory.

    params:
    --------
    imges: lis of Pillow Image
    bbox: list of bounding boxes
    output_idr: path to output directory
    ids: labels for bounding boxes. Optional.
    
    returns:
    --------
    None
    """
    # if len(images) != len(bbox):
    #     raise ValueError('images and bbox must be of same length')

    if ids is None:
        ids = [''] * len(bbox)

    image_counter = 1
    for img in images:

        fig, ax = plt.subplots(1)

        plt.axis('off')
        # Display the image
        ax.imshow(img)

        # Create a Rectangle patch
  
        for bounding_box, label in zip(bbox, ids):
            x, y, w, h = bounding_box
            rect = patches.Rectangle((x, y), w - x, h - y, linewidth=1.5, edgecolor='r', facecolor='none')
            ax.add_patch(rect)
            tag_text = label
            tag_x = x
            tag_y = y
            plt.text(tag_x, tag_y, tag_text, fontsize=9, color='blue', ha='left', va='center')

        plt.savefig(f'{output_dir}/page-{image_counter}.png', dpi=200, bbox_inches='tight')    
        image_counter += 1

        plt.close()
    
    return None


if __name__ == '__main__':

    # PDF_FILE = 'data-pipelines/data/caption-tests/multi-image-caption.pdf'
    PDF_FILE = 'data-pipelines/data/design-data100/00003/00003_Report_Giorgio_Larcher_vol.2.pdf'
    OUTPUT_DIR = 'data-pipelines/data/ocr-test/ocr-pipeline'
    images = convert_pdf_to_images(PDF_FILE, dpi=200)

    bboxes = extract_bboxes_from_horc(images)
    print('image_ boxes',bboxes['bboxes'])

    marked_bounding_boxes(images, bboxes['bboxes'], OUTPUT_DIR, bboxes['ids'])
