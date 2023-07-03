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
from tqdm import tqdm


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
    for img in tqdm(images,desc="Extracting bounding boxes", unit="pages"):
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


def crop_images_to_bbox(hocr_results: dict, output_dir:str, filter_size:int=50) -> None:
    """
    Crop images based on bounding boxes. Croped images are saved to output 
    directory as JPG files.

    params:
    --------

    image: Pillow Image or list of Pillow Image objects
    bbox: bounding box as list [x, y, width, height] or list of bounding boxes
    output_dir: path to output directory for cropped images
    ids: id or list of ids for cropped images
    filter_size: minimum size (width or height) of bounding box used to crop image. Default: 50 pixels

    returs:
    --------
    None
    """

    
    for page, results in tqdm(hocr_results.items(), desc="Cropping images", unit="pages"):
        for bounding_box, id in zip(results['bboxes'], results['ids']):
            x1, y1, x2, y2 = bounding_box # coordinates from top left corner
            width = x2 - x1
            height = y2 - y1
            if min(width, height) >= filter_size:
                cropped_image = results['img'].crop((x1, y1, x2, y2))
                cropped_image.save(f'{output_dir}/{page}-id-{id}.png')

    return None


def marked_bounding_boxes(hocr_results: dict, output_dir:str, ids:list=None, filter_size:int=50) -> None:
    """
    Draw bounding boxes of on input images and save a copy to output directory.

    params:
    --------
    imges: lis of Pillow Image
    bbox: list of bounding boxes
    output_idr: path to output directory
    ids: labels for bounding boxes. Optional.
    filter_size: minimum size (width or height) of bounding box to be drawn. Default: 50 pixels
    
    returns:
    --------
    None
    """
    # if len(images) != len(bbox):
    #     raise ValueError('images and bbox must be of same length')


    for page, result  in tqdm(hocr_results.items(), desc="Drawing bounding boxes", unit="pages"):

        if len( result['bboxes']) != 0: # skip creating images for pages with no bounding boxes
            
            fig, ax = plt.subplots(1)

            plt.axis('off')
            # Display the image
            ax.imshow(result['img'])

            # Create a Rectangle patch
    
            for bounding_box, label in zip(result['bboxes'] , result['ids']):
                x1, y1, x2, y2 = bounding_box # coordinates from top left corner
                width = x2 - x1
                height = y2 - y1
                if min(width, height) >= filter_size:
                    rect = patches.Rectangle((x1, y1), width, height, linewidth=1.5, edgecolor='r', facecolor='none')
                    ax.add_patch(rect)
                    tag_text = label
                    tag_x = x1
                    tag_y = y1
                    plt.text(tag_x, tag_y, tag_text, fontsize=9, color='blue', ha='left', va='center')

            plt.savefig(f'{output_dir}/{page}.png', dpi=200, bbox_inches='tight')    
        
            plt.close()
    
    return None

if __name__ == '__main__':

    # PDF_FILE = 'data-pipelines/data/caption-tests/multi-image-caption.pdf'
    # registry 1
    # PDF_FILE='data-pipelines/data/design-data100/00001_P5_Yilin_Zhou.pdf'
    # regisry 2
    # PDF_FILE='data-pipelines/data/design-data100/00002_P5PresentatieEricdeRidder_28jun.pdf' 
    PDF_FILE= 'data-pipelines/data/design-data100/00002_RESEARCHBOOKEricdeRidder_P5Repository.pdf'
    # registry 3
    # PDF_FILE = 'data-pipelines/data/design-data100/00003/00003_Report_Giorgio_Larcher_vol.1.pdf'
    # PDF_FILE = 'data-pipelines/data/design-data100/00003/00003_Report_Giorgio_Larcher_vol.2.pdf'
    # PDF_FILE = 'data-pipelines/data/design-data100/00003/00003_Report_Giorgio_Larcher_vol.3.pdf'    
    OUTPUT_DIR = 'data-pipelines/data/ocr-test/00002/vol2-psm3-oem1'
    images = convert_pdf_to_images(PDF_FILE, dpi=200)

    results = extract_bboxes_from_horc(images, config='--psm 3 --oem 1')
 
    marked_bounding_boxes(results, OUTPUT_DIR, filter_size=100)
    crop_images_to_bbox(results, OUTPUT_DIR, filter_size=100)
