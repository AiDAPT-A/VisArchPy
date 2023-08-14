"""
Extracts captions from PDF pages 
"""

import re
from pdfminer.layout import LTTextContainer, LTImage, LTFigure
from typing import List
from shapely.geometry import Polygon

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


def find_caption_by_bbox(image_object:LTImage|tuple, text_object:LTTextContainer|tuple, offset:int=0, direction:str=None
                         ) -> LTTextContainer|bool:
    """
    Finds if the boudning box of a text element is withing certain distance (offset) 
    from the bounding box of an Image element.
    
    Parameters
    -----------
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
    offset: int
        distance from image to be compared with, Unit: 1/72 inch or about 0.3528 mm
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
        if image_object or text_object of type tupple is not of size 4 

    """

    if isinstance(image_object, LTImage):
        image_coords = image_object.bbox
    else:
        if len(image_object) != 4:
            raise ValueError("image coordinates must be a tupple of 4 elements \
                             (x0, y0, x1, y1)") 
        image_coords = image_object
    
    if isinstance(text_object, LTTextContainer):
        text_coords = text_object.bbox
    else:
        if len(text_object) != 4:
            raise ValueError("text coordinates must be a tupple of 4 elements \
                             (x0, y0, x1, y1)") 
        text_coords = text_object

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
                              (image_coords[0]- offset, image_coords[1]- offset),
                              (image_coords[2]+ offset, image_coords[1]- offset),
                              # top:
                              (image_coords[2]+ offset, image_coords[3]+ offset),
                              (image_coords[0]- offset, image_coords[3]+ offset),
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
                              (image_coords[2], image_coords[3] + offset),
                              (image_coords[0], image_coords[3]+ offset),
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
                              (image_coords[0], image_coords[1]- offset),
                              (image_coords[2], image_coords[1]- offset),
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
                              (image_coords[2]+ offset, image_coords[1]),
                              # top:
                              (image_coords[2]+offset, image_coords[3]),
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
                              (image_coords[0] - offset, image_coords[1]),
                              (image_coords[2], image_coords[1]),
                              # top:
                              (image_coords[2], image_coords[3]),
                              (image_coords[0] - offset, image_coords[3]),
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
                            (image_coords[0], image_coords[1]- offset),
                            (image_coords[2] + offset, image_coords[1]- offset),
                            # top:
                            (image_coords[2] + offset, image_coords[3]),
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
                            (image_coords[0] - offset, image_coords[1]),
                            (image_coords[2], image_coords[1]),
                            # top:
                            (image_coords[2], image_coords[3] + offset),
                            (image_coords[0] - offset, image_coords[3]+ offset),
                        ])
            
    text_bbox = Polygon(  [(text_coords[0], text_coords[1]),
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

    for e in text_elements:
        # print(e.get_text())
        print(e.bbox)
        match = find_caption_by_text(e, keywords=["Figure", "caption", "figuur" ])
        print(match)
        if match is not False:
            print( match)
            print("===========================")

