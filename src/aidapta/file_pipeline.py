import time

from pdfminer.high_level import extract_pages
from pdfminer.image import ImageWriter
from pdfminer.layout import LTTextContainer, LTPage, LTTextBoxHorizontal, LTImage, LTFigure

from aidapta.utils import extract_mods_metadata
from aidapta.metadata import Document

pdf_2 ="data-pipelines/data/4563050_AmberLuesink_P5Report_TheRevivaloftheJustCity.pdf"
    # has 158283 figure elements


# SELECT MODS FILE
MODS_FILE = "data-pipelines/data/4Manuel_MODS.xml"
# SELECT PDF FILE
PDF_FILE = "data-pipelines/data/caption-tests/multi-image-caption.pdf"
# SELECT OUTPUT DIRECTORY
OUTPUT_DIR ="data-pipelines/img/pdfminer/"


# EXTRACT METADATA FROM MODS FILE

meta_blob = extract_mods_metadata(MODS_FILE)

pdf_document = Document(location=PDF_FILE, metadata=meta_blob)


# FOR EACH PAGE IN PDF FILE
    ## EXTRACT  AND SORT TEXT AND IMAGE ELEMENTS FROM PDF FILE
    
    ## SEARCH FOR CAPTIONS IN TEXT ELEMENTS
        ## ADD CAPTIONS TO METADATA
        ## SAVE IMAGE TO FILE
    
# SAVE METADATA TO JSON FILE








