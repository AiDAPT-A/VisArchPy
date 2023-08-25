"""
A library for applyin Optic Character Recognition with Tesseract
to PDF files.
Author: Manuel Garcia
"""

import itertools
import pytesseract
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from PIL.Image import Image
from tqdm import tqdm



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
                             page_number:int =None, entry_id: str=None) -> dict:
    """
    Extract bounding boxes for non-text regions from hOCR document.

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
    
    Returns
    -------
    dict
        Dictionary with bounding boxes and ids for non-text regions
        Example:
    
        {'page': {'img': None, 'bboxes': [], 'ids': []} }
    """
    _config = config + ' hocr'

    results = {}

    if isinstance(page_number, int):
        page_counter = None 
    else: 
        page_counter = 1
        # use a counter to keep track of page number
    
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
            

            if page_counter is not None: 
                page_number = page_counter
                page_counter += 1
            else:
                page_number = page_number

            if entry_id is not None:
                results[f'{entry_id}-page-{page_number}'] = {'img': img, 'bboxes': non_text_bboxes,
                                                              'ids': paragraphs_ids}
            else:
                results[f'page-{page_number}'] = {'img': img, 'bboxes': non_text_bboxes, 
                                                  'ids': paragraphs_ids}
        
    return results


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

    
    for page, results in hocr_results.items():
        for bounding_box, id in zip(results['bboxes'], results['ids']):
            x1, y1, x2, y2 = bounding_box # coordinates from top left corner
            width = x2 - x1
            height = y2 - y1
            if min(width, height) >= filter_size:
                cropped_image = results['img'].crop((x1, y1, x2, y2))
                cropped_image.save(f'{output_dir}/{page}-id-{id}.png')

    return None


def mark_bounding_boxes(hocr_results: dict, output_dir:str, ids:list=None, 
                        filter_size:int=50, page_number:int=None) -> None:
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
    
    Returns
    --------
    None
    """
    # if len(images) != len(bbox):
    #     raise ValueError('images and bbox must be of same length')


    for page, result in hocr_results.items():

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

            if page_number is not None:
                page = page_number
           
            plt.savefig(f'{output_dir}/{page}.png', dpi=200, bbox_inches='tight')    
        
            plt.close()
    
    return None


def filter_bbox_by_size(bboxes: list, min_width: int = None, min_height: int = None, 
                  aspect_ratio: tuple[float, str] = [None, None] ) -> list:
    """
    Filters bounding boxes based on size and aspect ratio of width and height.
    Aspect ratio is calculated as width/height.

    Parameters
    ----------
    bboxes: list
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
    list
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

    print("input bboxes", bboxes)
    if len(bboxes) == 0:
        return bboxes

    filtered_bboxes = []
    for bbox in bboxes:
        x1, y1, x2, y2 = bbox
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
        filtered_bboxes.append(bbox)
    
    return filtered_bboxes


def filter_bbox_largest(bboxes: list) -> list:
    """
    Finds the largest bounding box in a list of bounding boxes.
    The largest bounding box is defined as the one with the largest area.

    Parameters
    ----------
    bboxes: list
        list of bounding boxes. Each bounding box is a list of coordinates
    
    Returns
    -------
    list
        largest bounding box as a list of coordinates
    """
    
    if len(bboxes) == 0:
        return bboxes

    def compute_area(bbox):
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        return width * height

    largest_bbox = max(bboxes, key=compute_area)
    
    return largest_bbox


def filter_bbox_contained(bboxes: list) -> list:
    """
    Filters out bounding boxes that are completly contained by another bounding box.
    A bounding box is considered contained if all its coordinates are within the
    coordinates of another bounding box.

    Parameters
    ----------
    bboxes: list
        list of bounding boxes. Each bounding box is a list of coordinates
    
    Returns
    -------
    list
        lis of bounding boxes that are not completly contained by another bounding box
    """
    if len(bboxes) == 0 or len(bboxes) == 1:
        return bboxes
    
    def is_contained(bbox1, bbox2):
        "Check if bbox1 is contained in bbox"
        x1, y1, x2, y2 = bbox1
        x1_, y1_, x2_, y2_ = bbox2
        if x1_ <= x1 and y1_ <= y1 and x2_ >= x2 and y2_ >= y2:
            return True
        else:
            return False

    # remove duplicates in input list of bboxes
    unique_bboxes = []
    for item in bboxes:
        if item not in unique_bboxes:
            unique_bboxes.append(item)

    # generate all possible permutations of unique bboxes
    comparisons = []
    for permutation in itertools.permutations(unique_bboxes, 2):
        comparisons.append(permutation)

    # check if a bbox is contained by another bbox
    for comparison in comparisons:
        if is_contained(comparison[0], comparison[1]): # retuns True if box 0 
            #is contained in box 1
            try: 
                # remove box 0  form the list of boxes
                # if it is contained in box 1
                unique_bboxes.remove(comparison[0])
            except ValueError:
                pass # ignore value error when the box has already been removed

    return unique_bboxes


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

    # results = extract_bboxes_from_horc(images, config='--psm 3 --oem 1')
    # key_ = next(iter(results))
    # key_2 = next(iter(results))
    # print(results[key_], results[key_2])

    boxes = [[0, 0, 100, 100], [200, 300, 350, 400], [10, 20, 90, 90],[10, 10, 90, 90], [10, 10, 90, 90], [10, 10, 15, 20],  [1000, 1000, 1100, 1100]]
    

    print(filter_bbox_contained(boxes))
 
    # marked_bounding_boxes(results, OUTPUT_DIR, filter_size=100)
    # crop_images_to_bbox(results, OUTPUT_DIR, filter_size=100)
