"""
Extracts captions from PDF pages 
"""

# pdfminer.six

from pdfminer.high_level import extract_text
import os
import re
from typing import List

def find_image_caption_by_text(pdf_file:str) -> List:
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

if __name__ == '__main__':
    
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer, LTTextBoxHorizontal

    # # single image, single caption
    # pdf_1 ="data-pipelines/data/caption-tests/single-image-caption.pdf"
    # found = find_image_caption_by_text(pdf_1)
    
    # # multiple images and captions
    pdf_2 ="data-pipelines/data/caption-tests/multi-image-caption.pdf"
    found = find_image_caption_by_text(pdf_2)
    print(found)

    # for page_layout in extract_pages(pdf_2):
    #     for element in page_layout:
    #         if isinstance(element, LTTextContainer):
                
    #             _text = element.get_text()
    #             print(type(_text))
    #             print(_text)
    #             print('---------------------')


    # # only text, null case
    # pdf_3 ="data-pipelines/data/caption-tests/only-text.pdf"
    # found = find_image_caption_by_text(pdf_3)

    # print(found)