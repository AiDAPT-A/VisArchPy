"""
Extracts captions from PDF pages 
"""

# pdfminer.six

from pdfminer.high_level import extract_text
from pdfminer.layout import LTTextContainer, LTTextBoxHorizontal, LTImage, LTFigure, LAParams
import os
import re
from typing import List
from shapely.geometry import Polygon

def find_caption_by_text(pdf_file:str) -> List:
    """do text analysis by matching caption keywords (e.g, figure, caption, Figure)
    in a PDF document, using regular expressions
    """

    captions = []
    for page_layout in extract_pages(pdf_file):
        for element in page_layout:
            # identify if the text is part of a caption using keyworks, e.g., Figure
            if isinstance(element, LTTextContainer) and re.search('^figure|^caption|^figuur', element.get_text().lower()):
                # the following is necessary to remove break line `\n` from captions
                # that spans multiple lines
                caption_line = ''
                for text_line in element:
                    caption_line += text_line.get_text().strip()
                
                captions.append(caption_line)
    
    return  captions

def find_caption_by_bbox(image:LTImage, text_element:LTTextContainer, offset:int=0, direction:str=None) -> LTTextContainer:
    """
    Finds if the boudning box of a text element is withing certain distance (offset) 
    from the bounding box of an Image element.
    
    Params:
    offset: distance from image to be compared with
    direction: the directions the offeset will be applied to. Posibile values: right, left, down, up, 
    None (apply in all directions)

    Returs: text elemenet withing offset distance
    """


    image_coords = image.bbox
    text_coords = text_element.bbox

    if direction == None:

        image_bbox = Polygon([
                              # bottom
                              (image_coords[0]- offset, image_coords[1]- offset),
                              (image_coords[2]+ offset, image_coords[1]- offset),
                              # top:
                              (image_coords[2]+ offset, image_coords[3]+ offset),
                              (image_coords[0]- offset, image_coords[3]+ offset),
                        ])
    
    if direction == "down":
        image_bbox = Polygon([
                              # bottom
                              (image_coords[0], image_coords[1]- offset),
                              (image_coords[2], image_coords[1]- offset),
                              # top:
                              (image_coords[2], image_coords[3]),
                              (image_coords[0], image_coords[3]),
                        ])
        
    if direction == "right":
        image_bbox = Polygon([
                              # bottom
                              (image_coords[0], image_coords[1]),
                              (image_coords[2]+ offset, image_coords[1]),
                              # top:
                              (image_coords[2]+offset, image_coords[3]),
                              (image_coords[0], image_coords[3]),
                        ])

    text_bbox = Polygon(  [(text_coords[0], text_coords[1]),
                            (text_coords[2], text_coords[1]),
                            (text_coords[2], text_coords[3]),
                            (text_coords[0], text_coords[3]),
                    ])

    if image_bbox.intersects(text_bbox):
        return text_element
    else:
        return False

if __name__ == '__main__':
    
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer, LTTextBoxHorizontal, LTImage, LTFigure, LAParams
    # are LAParams only for text?
    

    # # single image, single caption
    # pdf_1 ="data-pipelines/data/caption-tests/single-image-caption.pdf"
    # found = find_image_caption_by_text(pdf_1)
    
    # # multiple images and captionsclea
    pdf_2 ="data-pipelines/data/caption-tests/multi-image-caption.pdf"
    # found = find_caption_by_text(pdf_2)
    # print(found)

    pdf_3 ="data-pipelines/data/caption-tests/multi-image-no-keyword.pdf"



    text_elements = []

    # for page_layout in extract_pages(pdf_2):
    for page_layout in extract_pages(pdf_3):

        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text_elements.append(element)
                # _text = element.get_text()
                # print(type(_text))
                # laparams = LAParams()
                # print(element.analyze(laparams))
            
    # print(text_elements)

    image_elements =[]
    # for page_layout in extract_pages(pdf_2):
    for page_layout in extract_pages(pdf_3):

        for element in page_layout:
            if isinstance(element, LTFigure):
                
                # _text = element.get_text()
                # print(type(_text))
                # laparams = LAParams()
                # print(element.analyze(laparams))
                for img in element:
                    if isinstance(img, LTImage):
                        image_elements.append(img)

    # for img in image_elements:
    #     for e in text_elements:
    #         match = find_caption_by_bbox(img, e, offset=10, direction=None )
    #         if match is not False:
    #             print(img, match)
    #             print("===========================")

    for img in image_elements:
        for e in text_elements:
            match = find_caption_by_bbox(img, e, offset=10, direction="right" )
            if match is not False:
                print(img, match)
                print("===========================")
