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

    _text = extract_text(pdf_file)

    # convert text to lowercase and split lines
    text_lines = _text.lower().splitlines()

    captions = []
    for line in text_lines:
        if re.search('^figure|^caption|^figuur', line):
            captions.append(line)
    
    return  captions

if __name__ == '__main__':
    
    # # single image, single caption
    # pdf_1 ="data-pipelines/data/caption-tests/single-image-caption.pdf"
    # found = find_image_caption_by_text(pdf_1)
    
    # # multiple images and captions
    pdf_2 ="data-pipelines/data/caption-tests/multi-image-caption.pdf"
    found = find_image_caption_by_text(pdf_2)

    # # only text, null case
    # pdf_3 ="data-pipelines/data/caption-tests/only-text.pdf"
    # found = find_image_caption_by_text(pdf_3)

    print(found)