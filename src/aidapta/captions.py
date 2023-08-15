"""
Extracts captions from PDF pages 
"""

import re
from pdfminer.layout import LTTextContainer, LTImage, LTFigure
from typing import List
from shapely.geometry import Polygon
from dataclasses import dataclass
from aidapta.utils import mm_to_point

@dataclass
class BoundingBox:
    """ 
    represents a bounding box of an element in the form (x0, y0, x1, y1).
    Coordinates represent the lower-left corner (x0, y0) and the upper-right corner (x1, y1).
    """

    element: tuple 

    def __post_init__(self):
        if len(self.element) != 4:
            raise ValueError("bounding box must be a tupple of 4 elements \
                             (x0, y0, x1, y1)")

    def bbox(self) -> tuple:
        """returns the coordinates of the bounding box"""
        return self.element    
    

@dataclass
class OffsetDistance:
    """ 
    represents an offset distance in the form (distance, unit).
    """

    distance: float 
    unit: str

    def __post_init__(self):
        if self.unit not in ["mm", "px"]:
            raise ValueError("unit must be either mm or px (pixels)")


def find_caption_by_text(text_element:LTTextContainer, keywords: List = ['figure', 'caption', 'figuur']
                         ) -> LTTextContainer|bool:
    """do text analysis by matching caption keywords (e.g, figure, caption, Figure)
    in a PDF document element of type text using regular expressions. Matches are not case sentive.

    Parameters
    ----------
    text_element: LTTextContainer object
        text element to be analyzed
    keywords: list
        list of keywords to match in the text element
  
    Returns
    -------
    LTTextContainer object or bool
        False if no match is found, otherwise the
        text element that matches any of the keywords

    Raises
    ------
    ValueError
        if list of keywords is empty
    TypeError
        if keyword is not a string
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


def find_caption_by_bbox(image_object:LTImage|BoundingBox, text_object:LTTextContainer|BoundingBox, offset:OffsetDistance, direction:str=None
                         ) -> LTTextContainer|bool:
    """
    Finds if the boudning box of a text element is within certain distance (offset) 
    from the bounding box of an Image element.
    
    Parameters
    ----------
    image_object: LTImage object or tuple
        Image whose bounding box will be used as reference.
        Either a single LTImage object or a list of coordinates
        of the form (x0, y0, x1, y1), where (x0, y0) is the lower-left
        corner and (x1, y1) the upper-right corner.
    text_object: LTTextContainer object
        text element whose bounding box will be compared with the image bounding box.
        Either a single LTTextContainer object or a list of coordinates
        of the form (x0, y0, x1, y1), where (x0, y0) is the lower-left
        corner and (x1, y1) the upper-right corner.
    offset: OffsetDistance object
        distance from image within which the text element will be searched.
    direction: str
        the directions the offeset will be applied around the image bounding box. 
        Default None, which applies offect in 'all' directions. Posibile values: right, 
        left, down, up, right-down, left-up, all.

    Returns
    -------
    LTTextContainer object or bool
        False if no match is found, otherwise the
        text elemenet within offset distance
    
    Raises
    ------
    ValueError
        if direction is not one of the following: right, left, down, up, right-down, 
        left-up, all
    TypeError
        if offset is in pixels and image_object is not a BoundingBox object. This 
        is to insure that the offset is applied in the same units as the image bounding box.
    """

    image_coords = image_object.bbox
    text_coords = text_object.bbox

    if offset.unit == "mm": # Bbox from pdfminer are in points
        offset_distance = mm_to_point(offset.distance)

    if direction not in ["right", "left", "down", "up", "right-down", "left-up", "all", None]:
        raise ValueError("direction must be either right, left, down, up, right-down, left-up, all")
    
    if offset.unit == "px" and not isinstance(image_object, BoundingBox):
        raise TypeError("offset in pixels can only be used with a BoundingBox object")
    
    if direction == None or direction == "all":
        '''
         ____________________
        |       offset       |
        |  ++++++++++++++++  |
        |  +              +  |
        |  + image bbox   +  |
        |  +              +  |
        |  +              +  |
        |  ++++++++++++++++  | 
        |____________________|  
        
        '''

        image_bbox = Polygon([
                              # bottom
                              # coodinates [x, y, x, y]
                              (image_coords[0]- offset_distance, image_coords[1]- offset_distance),
                              (image_coords[2]+ offset_distance, image_coords[1]- offset_distance),
                              # top:
                              (image_coords[2]+ offset_distance, image_coords[3]+ offset_distance),
                              (image_coords[0]- offset_distance, image_coords[3]+ offset_distance),
                        ])


    if direction == "up":
        '''
         ______________
        |    offset    | 
        ++++++++++++++++  
        +              +  
        + image bbox   +  
        +              +  
        +              +  
        ++++++++++++++++   
        
        '''
        image_bbox = Polygon([
                              # bottom
                              # coodinates [x, y, x, y]
                              (image_coords[0], image_coords[1]),
                              (image_coords[2], image_coords[1]),
                              # top:
                              (image_coords[2], image_coords[3] + offset_distance),
                              (image_coords[0], image_coords[3]+ offset_distance),
                        ])

    if direction == "down":
        '''
        ++++++++++++++++  
        +              +  
        + image bbox   +  
        +              +  
        +              +  
        ++++++++++++++++ 
        |___ offset____|  
        
        '''
        image_bbox = Polygon([
                              # bottom
                              # coodinates [x, y, x, y]
                              (image_coords[0], image_coords[1]- offset_distance),
                              (image_coords[2], image_coords[1]- offset_distance),
                              # top:
                              (image_coords[2], image_coords[3]),
                              (image_coords[0], image_coords[3]),
                        ])
        
    if direction == "right":
        '''
        ++++++++++++++++ --  
        +              + o |
        + image bbox   + f |
        +              + f |
        +              + s |
        ++++++++++++++++ --   
          
        '''
        image_bbox = Polygon([
                              # bottom
                              (image_coords[0], image_coords[1]),
                              (image_coords[2]+ offset_distance, image_coords[1]),
                              # top:
                              (image_coords[2]+offset_distance, image_coords[3]),
                              (image_coords[0], image_coords[3]),
                        ])
        
    if direction == "left":
        '''
         -- ++++++++++++++++  
        | o +              +  
        | f + image bbox   +  
        | f +              +  
        | s +              +  
         -- ++++++++++++++++   
            
        '''
        image_bbox = Polygon([
                              # bottom
                              (image_coords[0] - offset_distance, image_coords[1]),
                              (image_coords[2], image_coords[1]),
                              # top:
                              (image_coords[2], image_coords[3]),
                              (image_coords[0] - offset_distance, image_coords[3]),
                        ])
        
    if direction == "down-right":
        '''
        ++++++++++++++++---  
        +              +  |  
        + image bbox   +  |  
        +              +  | 
        +              +  | 
        ++++++++++++++++  | 
        |___ offset_______|  
        
        '''
        image_bbox = Polygon([
                            # bottom
                            # coodinates [x, y, x, y]
                            (image_coords[0], image_coords[1]- offset_distance),
                            (image_coords[2] + offset_distance, image_coords[1]- offset_distance),
                            # top:
                            (image_coords[2] + offset_distance, image_coords[3]),
                            (image_coords[0], image_coords[3]),
                        ])
        
    if direction == "up-left":

        '''
          _________________
         |      offset     | 
         |  ++++++++++++++++  
         |  +              +  
         |  + image bbox   +  
         |  +              +  
         |  +              +  
         ---++++++++++++++++   
        
        '''
        image_bbox = Polygon([
                            # bottom
                            # coodinates [x, y, x, y]
                            (image_coords[0] - offset_distance, image_coords[1]),
                            (image_coords[2], image_coords[1]),
                            # top:
                            (image_coords[2], image_coords[3] + offset_distance),
                            (image_coords[0] - offset_distance, image_coords[3]+ offset_distance),
                        ])
            
    text_bbox = Polygon(  [
                            (text_coords[0], text_coords[1]),
                            (text_coords[2], text_coords[1]),
                            (text_coords[2], text_coords[3]),
                            (text_coords[0], text_coords[3]),
                    ])

    if image_bbox.intersects(text_bbox):
        return text_object
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


    # for e in text_elements:
    #     # print(e.get_text())
    #     print(e.bbox)
    #     match = find_caption_by_text(e, keywords=["Figure", "caption", "figuur" ])
    #     print(match)
    #     if match is not False:
    #         print( match)
    #         print("===========================")

