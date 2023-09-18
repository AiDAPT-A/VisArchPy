"""
A library for applyin Optic Character Recognition with Tesseract
to PDF files.
Author: Manuel Garcia
"""

import itertools
import pytesseract
import copy
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from PIL.Image import Image
from tqdm import tqdm
from collections import Counter
from pytesseract import image_to_string


def region_to_string(image: Image, bbox: list[float], config: str ='--oem 1 --psm 1') -> str:
    """
    Extract text from a region of an image.

    Parameters
    ----------
    imge: Image
        image of type Pillow Image
    bbox: list
        list of coordinates for bounding box of the region to be analyzed
    config: str
        tesseract configuration options. Default: --oem 1 --psm 1. 
        Which applies: Engine Neural nets LSTM only. Auto page segmentation with OSD
    
    Returns
    -------
    str
        text extracted from the region of the image
    """

    x1, y1, x2, y2 = bbox
    region = image.crop((x1, y1, x2, y2))
    text = pytesseract.image_to_string(region, config=config)
    return text


def convert_pdf_to_image(pdf_file: str, dpi:int = 200, **kargs)-> list[Image]:
    """
    Convert PDF file to image, one page at a time.

    Parameters
    ----------
    pdf_file: str   
        path to PDF file
    dpi: int     
        resolution of the output image
    kargs: 
        additional arguments for the convert_from_path function from pdf2image package.
        For example, first_page and last_page can be used to specify the range of 
        pages to convert.

    Returns
    --------
    list of images 
        List of images. Images are of type Pillow Image

    """

    if 'first_page' in kargs and 'last_page' in kargs:

        first_page = kargs['first_page']
        last_page = kargs['last_page']
        return convert_from_path(pdf_file, dpi=dpi, first_page=first_page, last_page=last_page)
    else:
        return convert_from_path(pdf_file, dpi=dpi)


def extract_bboxes_from_horc(images: list[Image], config: str ='--oem 1 --psm 1', 
                             page_number:int =None, entry_id: str=None, resize: int = 32767) -> dict:
    """
    Extract bounding boxes for elements from hOCR document.

    Parameters
    -----------
    images: list[Image] 
        list of images of type Pillow Image
    config: str
        tesseract configuration options. Default: --oem 1 --psm 1. 
        Which applies: Engine Neural nets LSTM only. Auto page segmentation with OSD
    page_number: int
        page number for the PDF file. Optional.
    entry_id: 
        id for entry (an entry identifies a group of files somehow related). Optional.
    resize: int
        maximun with or height allowed before resizing is enforced. Optional. This avoids to send images that are
        too large to be processed by Tesseract. Default: 32767 pixels (current limite in Tessaract 5.3)
    
    Returns
    -------
    dict
        Dictionary with bounding boxes and ids for non-text regions. If nothing is 
        detected by the OCR, it returns an empty dictionary.
        Example:
    
        {'pageId': {'img': pageImage, 
                    'bboxes': {'id1': [bbox], ... 'idn': [bbox] }, 
                    'text_bboxes': {'id1': [bbox], ... 'idn': [bbox] } 
        } }
    """
    _config = config + ' hocr'

    hocr_results = {}

    if isinstance(page_number, int):
        page_counter = None 
    else: 
        page_counter = 1
        # use a counter to keep track of page number
    
    for img in images:
        # print("extracting box for image: ", img)

        # resize image if it is too large
        if img.width > resize or img.height > resize:
            img.resize((resize, resize), Image.ANTIALIAS)
        else:
            pass
        horc_data = pytesseract.image_to_pdf_or_hocr(img, extension='hocr', config=_config)
        soup = BeautifulSoup(horc_data, 'html.parser')
        paragraphs = soup.find_all('p', class_='ocr_par')
        non_text_bboxes = {}
        text_bboxes = {}
        # paragraphs_ids = []
        # paragraph_confidence_scores = []
        # boxed_paragraphs = []
        for paragraph in paragraphs:
            # print('para',paragraph)
            title = paragraph.get('title')
            id = paragraph.get('id')
            # use to check if paragraph contains text
            text_element = paragraph.find('span', {'class': 'ocrx_word'})
            text =text_element.get_text()

            if title and text.strip() == "":
                bounding_box = title.split(';')[0].split(' ')[1:]
                bounding_box = [int(value) for value in bounding_box]
                
                non_text_bboxes[str(id)] = bounding_box
            else:
                bounding_box = title.split(';')[0].split(' ')[1:]
                bounding_box = [int(value) for value in bounding_box]
                text_bboxes[str(id)] = bounding_box

            if page_counter is not None: 
                _page_number = page_counter
                page_counter += 1
            else:
                _page_number = page_number

            if entry_id is not None:
                hocr_results[f'{entry_id}-page-{_page_number}'] = {'img': img, 
                                                            'bboxes': non_text_bboxes,
                                                            'text_bboxes': text_bboxes
                }
            else:
                hocr_results[f'page-{_page_number}'] = {'img': img, 
                                                    'bboxes': non_text_bboxes,
                                                    'text_bboxes': text_bboxes
                } 
    
    # hocr results may be empty if no parragraphs are recognized
    # during the OCR analysis. 

    return hocr_results


def crop_images_to_bbox(hocr_results: dict, output_dir:str, filter_size:int=50) -> None:
    """
    Crop images based on bounding boxes. Croped images are saved to output 
    directory as PNG files.

    Parameters
    -----------
    hocr_results: dict
        Dictionary with bounding boxes and ids for non-text regions 
    
    output_dir: str
        path to output directory for cropped images
    
    filter_size: int
        minimum size (width or height) of bounding box used to filter out images. 
        Default: 50 pixels

    Returns
    -------
    None

    """
    
    # TODO: UPDATE ALL functions to use new hocr_results format

    for page, content in hocr_results.items():

        for id in content['bboxes']:
            x1, y1, x2, y2 = content['bboxes'][id] # coordinates from top left corner
            width = x2 - x1
            height = y2 - y1
            if min(width, height) >= filter_size:
                cropped_image = content['img'].crop((x1, y1, x2, y2))
                cropped_image.save(f'{output_dir}/{page}-{id}.png')

    return None


def mark_bounding_boxes(hocr_results: dict, output_dir:str,  
                        filter_size:int=50, page_number:int=None, text_boxes:bool=False) -> None:
    """
    Draw bounding boxes on ocr images and save a copy to the output directory.

    Parameters
    ----------
    imges: dict
        Dictionary with bounding boxes and ids for non-text regions
    output_dir: str
        path to output directory to save marked images
    ids: list
        list of ids for bounding boxes. Optional.
    filter_size: int
        minimum size (width or height) f bounding box used to filter out images.
        Default: 50 pixels
    page_number: int
        page number to be drawn. Optional. If None, the HOCR page number is used.
    text_boxes: bool
        if True, text bounding boxes are also drawn. Default: False
    
    Returns
    --------
    None
    """


    for page, content in hocr_results.items():

        if len( content['bboxes']) != 0: # skip creating images for pages with no bounding boxes
            
            fig, ax = plt.subplots(1)

            plt.axis('off')
            # Display the image
            ax.imshow(content['img'])

            # Create a Rectangle patch
    
            
            # Plot image boxes
            for id in content['bboxes']:
                x1, y1, x2, y2 = content['bboxes'][id] # coordinates from top left corner
                width = x2 - x1
                height = y2 - y1
                if min(width, height) >= filter_size:
                    rect = patches.Rectangle((x1, y1), width, height, linewidth=1.5, edgecolor='r', facecolor='none')
                    ax.add_patch(rect)
                    tag_text = id
                    tag_x = x1
                    tag_y = y1
                    plt.text(tag_x, tag_y, tag_text, fontsize=9, color='blue', ha='left', va='center')

            # Plot text boxes
            if text_boxes:
                for id in content['text_bboxes']:
                    x1, y1, x2, y2 = content['text_bboxes'][id] # coordinates from top left corner
                    width = x2 - x1
                    height = y2 - y1
                    if min(width, height) >= filter_size:
                        rect = patches.Rectangle((x1, y1), width, height, linewidth=1.5, edgecolor='r', facecolor='none')
                        ax.add_patch(rect)
                        tag_text = id
                        tag_x = x1
                        tag_y = y1
                        plt.text(tag_x, tag_y, tag_text, fontsize=9, color='blue', ha='left', va='center')

            if page_number is not None:
                page = page_number
           
            plt.savefig(f'{output_dir}/{page}.png', dpi=400, bbox_inches='tight')    
        
            plt.close()
    
    return None


def filter_bbox_by_size(bboxes: dict, min_width: int = None, min_height: int = None, 
                  aspect_ratio: tuple[float, str] = [None, None] ) -> dict:
    """
    Filters bounding boxes based on size and aspect ratio of width and height.
    Aspect ratio is calculated as width/height.

    Parameters
    ----------
    bboxes: dict
        list of bounding boxes. Each bounding box is a list of coordinates
    
    min_width: int
        minimum width of bounding box. Optional.

    min_height: int
        minimum height of bounding box. Optional.

    aspect_ratio: tuple
        aspect ratio of bounding box to be filtered out. A tuple with a value of the aspect ratio (float)
        and an operator (string, either '<' or '>') indicating if filter excludes boxes 
        smaller than or larger than the aspect ratio. For example, (1.5, '>') will filter
        out boxes with aspect ratio larger than (>) 1.5, and (1.5, '<') will filter out
        boxes with aspect ratio smaller than (<) 1.5. Optional.
    
    Returns
    -------
    dict
        filtering results with bounding boxes and ids for non-text regions
    """
    
    if min_width is None and min_height is None and aspect_ratio is None:
        raise ValueError('At least one filtering parameter must be provided')
    
    # type checking
    if isinstance(aspect_ratio, tuple):
        # aspect = aspect_ratio[0]
        operator = aspect_ratio[1]
        if operator not in ['<', '>']:
            raise ValueError('Operator must be either "<" or ">"')

    if len(bboxes) == 0:
        return bboxes

    filtered_bboxes = {}
    for id in bboxes.keys():
        x1, y1, x2, y2 = bboxes[id]
        width = x2 - x1
        height = y2 - y1
        if min_width is not None and width < min_width:
            continue
        if min_height is not None and height < min_height:
            continue
        if aspect_ratio[0] is not None:
            if aspect_ratio[1] == '<':
                if width/height < aspect_ratio[0]:
                    continue
            elif aspect_ratio[1] == '>':
                if width/height > aspect_ratio[0]:
                    continue
        # overwrite bboxes with filtered bboxes
        filtered_bboxes[id] = bboxes[id]
    
    return filtered_bboxes


def filter_bbox_largest(bboxes: dict) -> dict:
    """
    Finds the largest bounding box in a set of bounding boxes.
    The largest bounding box is defined as the one with the largest area.

    Parameters
    ----------
    bboxes: dict
        bounding boxes. Each bounding box contains an id and a list of coordinates
    
    Returns
    -------
    dict
        largest bounding box as a dictionary with id and coordinates
    """
    
    if len(bboxes) == 0:
        return bboxes

    def compute_area(bbox: list) -> float:
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        return width * height

    bboxes_area = {key: compute_area(value) for key, value in bboxes.items()}
    largest_id_bbox = max(bboxes_area, key=bboxes_area.get)
    largest_bbox = {largest_id_bbox: bboxes[largest_id_bbox]}
 
    return largest_bbox


def filter_bbox_contained(bboxes: dict) -> dict:
    """
    Filters out bounding boxes that are completly contained by another bounding box.
    A bounding box is considered contained if all its coordinates are within the
    coordinates of another bounding box.

    Parameters
    ----------
    bboxes: dict
        bounding boxes. Each bounding box has an id and a list of coordinates
    
    Returns
    -------
    dict
        bounding boxes that are not completly contained by another bounding box.
        If two bounding boxes have the same coordinates, only one of them is kept.
    """
    if len(bboxes) == 0 or len(bboxes) == 1:
        return bboxes
    
    def is_contained(bbox1, bbox2):
        "Check if bbox1 is contained in bbox2"
        x1, y1, x2, y2 = bbox1
        x1_, y1_, x2_, y2_ = bbox2
        if x1_ <= x1 and y1_ <= y1 and x2_ >= x2 and y2_ >= y2:
            return True
        else:
            return False

    # remove element in input bboxes that contain the same coordinates
    unique_bboxes = {}
    for id, box in bboxes.items():
        if box in unique_bboxes.values():
            continue
        else:
            unique_bboxes[id] = box

    comparisons = [] # permuttion of boxes ids
    # compute permutations over boxes ids
    for permutation in itertools.permutations(unique_bboxes, 2):
        comparisons.append(permutation)

    no_contained_boxes = copy.deepcopy(unique_bboxes)
    # check if a bbox is contained by another bbox
    for comparison in comparisons:
        # print('comparison', comparison)
        if is_contained(unique_bboxes[comparison[0]], unique_bboxes[comparison[1]]): # retuns True if box 0 
            #is contained in box 1
            
            try: 
                # remove box that is contained by
                # any other box
                no_contained_boxes.pop(comparison[0])
            except KeyError:
                # Ensures that at least one of the boxes with the same coordinates is kept
                # in the final results
                no_contained_boxes[comparison[0]] = unique_bboxes[comparison[0]]
                pass # ignore value error when the box has already been removed
        else:
            continue

    return no_contained_boxes


if __name__ == '__main__':

    PDF_FILE = 'data-pipelines/data/caption-tests/multi-image-caption.pdf'
    # registry 1
    # PDF_FILE='data-pipelines/data/design-data100/00001_P5_Yilin_Zhou.pdf'
    # regisry 2
    # PDF_FILE='data-pipelines/data/design-data100/00002_P5PresentatieEricdeRidder_28jun.pdf' 
    # PDF_FILE= 'data-pipelines/data/design-data100/00002_RESEARCHBOOKEricdeRidder_P5Repository.pdf'
    # registry 3
    # PDF_FILE = 'data-pipelines/data/design-data100/00003/00003_Report_Giorgio_Larcher_vol.1.pdf'
    # PDF_FILE = 'data-pipelines/data/design-data100/00003/00003_Report_Giorgio_Larcher_vol.2.pdf'
    # PDF_FILE = 'data-pipelines/data/design-data100/00003/00003_Report_Giorgio_Larcher_vol.3.pdf'    
    OUTPUT_DIR = 'data-pipelines/data/ocr-test/00002/vol2-psm3-oem1'
    images = convert_pdf_to_image(PDF_FILE, dpi=200)

    print(images[0])

    region = [1000, 500, 2000, 1000]

    result = region_to_string(images[0], region )

    print(result)


    results = extract_bboxes_from_horc(images, config='--psm 3 --oem 1')
    # key_ = next(iter(results))
    # key_2 = next(iter(results))
    # print(results[key_], results[key_2])

    # boxes = {'id1':[0, 0, 100, 100], 'id2': [200, 300, 350, 400], 'id3': [10, 20, 90, 90],
    #          'id4':[10, 10, 90, 90], 'id5': [10, 10, 90, 90], 'id6': [10, 10, 15, 20],
    #            'id7':  [1000, 1000, 1200, 1200], 'id8': [200, 300, 350, 400], 'id9': [200, 300, 350, 400],}
    

    boxes2 = {'id1':[0, 0, 100, 210], 'id2': [80, 300, 350, 400], 
               'id7':  [1000, 1000, 1200, 1200]}
    
    # print(filter_bbox_by_size(boxes, min_width=100, min_height=100))
    # print(filter_bbox_largest(boxes))


    # print(filter_bbox_contained(boxes2))
 
    # mark_bounding_boxes(results, OUTPUT_DIR, filter_size=100)
    # crop_images_to_bbox(results, OUTPUT_DIR, filter_size=100)
