"""
Extracts captions from PDF pages 
"""

import re
from pdfminer.layout import LTTextContainer, LTImage, LTFigure
from typing import List
from shapely.geometry import Polygon

def find_caption_by_text(text_element:LTTextContainer, keywords: List = ['figure', 'caption', 'figuur']) -> LTTextContainer|bool:
    """do text analysis by matching caption keywords (e.g, figure, caption, Figure)
    in a PDF document element of type text using regular expressions. Matches are not case sentive.

    Params:
    -------
    - text_element: LTTextContainer object
    - keywords: list of keywords to match in the text element
    """
    

    if len(keywords) == 0:
        raise ValueError("List of keywords cannot be empty. Try adding adding at least one keyword")
    else:
        # constructs regular expression to match
        # textboxes that start with 
        words = []
        separator = '|'
        for word in keywords:
            if not isinstance(word, str):
                raise TypeError (f"Keyword must be of type string. {word} has type {type(word)}")
            words.append('^'+word.lower())
        regex = separator.join(words)

    if isinstance(text_element, LTTextContainer) and re.search(regex, text_element.get_text().lower()):
        return text_element
    else:
        return False


def find_caption_by_bbox(image:LTImage, text_element:LTTextContainer, offset:int=0, direction:str=None) -> LTTextContainer|bool:
    """
    Finds if the boudning box of a text element is withing certain distance (offset) 
    from the bounding box of an Image element.
    
    Params:
    -------
    - offset: distance from image to be compared with, Unit: 1/72 inch or about 0.3528 mm
    - direction: the directions the offeset will be applied to. Posibile values: right, left, down, up.  
      Default None (apply in all directions)

    Returs: text elemenet within offset distance
    """

    image_coords = image.bbox
    text_coords = text_element.bbox

    if direction == None or direction == "all":

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
    from pdfminer.layout import LTTextContainer,  LTImage, LTFigure
    # are LAParams only for text?
    
    pdf_2 ="data-pipelines/data/caption-tests/multi-image-caption.pdf"

    pdf_3 ="data-pipelines/data/caption-tests/multi-image-no-keyword.pdf"

    text_elements = []

    for page_layout in extract_pages(pdf_2):

        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text_elements.append(element)

    for e in text_elements:
        # print(e.get_text())
        match = find_caption_by_text(e, keywords=["Figure", "caption", "figuur" ])
        # print(match)
        if match is not False:
            print( match)
            print("===========================")

