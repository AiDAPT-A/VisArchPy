"""A pipeline for extracting metadata from MODS files and imges from PDF files.
Author: Manuel Garcia
"""

import os
import pathlib
import shutil
import time

from pdfminer.high_level import extract_pages
from pdfminer.image import ImageWriter
from tqdm import tqdm
from aidapta.utils import extract_mods_metadata, get_entry_number_from_mods
from aidapta.captions import find_caption_by_bbox, find_caption_by_text
from aidapta.image import sort_layout_elements, create_output_dir
from aidapta.metadata import Document, Metadata, Visual


def main(entry_id: str,):
    start_time = time.time()

    # SELECT MODS FILE
    MODS_FILE = f"data-pipelines/data/actual-data/{entry_id}_mods.xml"

    # SELECT INPUT DIRECTORY
    INPUT_DIR = "data-pipelines/data/actual-data/"

    # SELECT OUTPUT DIRECTORY
    # if run multiple times to the same output directory, the images will be duplicated and 
    # metadata will be overwritten
    OUTPUT_DIR = INPUT_DIR

    # TEMPORARY DIRECTORY
    # this directory is used to store temporary files. PDF files are copied to this directory
    TMP_DIR = "data-pipelines/data/tmp/"

    # SETTINGS FOR THE IMAGE EXTRACTION
    IMG_SETTINGS = {"width": 100, "height": 100} # recommended values: 0, 0

    # CAPTION MATCH SETTINGS
    CAP_SETTINGS ={"method": "bbox",
            "offset": 14, # one unit equals 1/72 inch or 0.3528 mm
            "direction": "down", # all directions
            "keywords": ['figure', 'caption', 'figuur'] # no case sentitive
            }

    # EXTRACT METADATA FROM MODS FILE
    meta_blob = extract_mods_metadata(MODS_FILE)

    # get entry number from MODS file
    entry_number = get_entry_number_from_mods(MODS_FILE)

    # Create output directory for the entry
    entry_directory = create_output_dir(OUTPUT_DIR, entry_number)

    # FIND PDF FILES FOR A GIVEN ENTRY
    PDF_FILES = []
    for f in tqdm(os.listdir(INPUT_DIR), desc="Collecting PDF files", unit="files"):
        if f.startswith(entry_number) and f.endswith(".pdf"):
            PDF_FILES.append(INPUT_DIR+f)

    # INITIALISE METADATA OBJECT
    entry = Metadata()
    # add metadata from MODS file
    entry.set_metadata(meta_blob)
    # set web url. This is not part of the MODS file
    base_url = "http://resolver.tudelft.nl/" 
    entry.add_web_url(base_url)

    # PROCESS PDF FILES
    for pdf in PDF_FILES:
        print("--> Processing file:", pdf)
        # create document object
        pdf_document = Document(pdf)
        entry.add_document(pdf_document)

        # PREPARE OUTPUT DIRECTORY
        pdf_file_name = pathlib.Path(pdf_document.location).stem
        image_directory = create_output_dir(entry_directory, pdf_file_name)

        # PROCESS SINGLE PDF 
        pdf_pages = extract_pages(pdf_document.location)

        pages = []
        for page in tqdm(pdf_pages, desc="Reading pages", unit="pages"):
            elements = sort_layout_elements(page, img_height=IMG_SETTINGS["width"], img_width=IMG_SETTINGS["height"])
            pages.append(elements)

        for page in tqdm(pages, desc="Extracting images", total=len(pages), unit="pages"):

            iw = ImageWriter(image_directory)
        
            for img in page["images"]:
            
                visual = Visual(document_page=page["page_number"], document=pdf_document, bbox=img.bbox)
                
                # Search for captions using proximity to image Bboxes
                # This might generate multiple matches
                bbox_matches =[]
                for _text in page["texts"]:
                    match = find_caption_by_bbox(img, _text, offset=CAP_SETTINGS["offset"], 
                                                direction=CAP_SETTINGS["direction"])
                    if match:
                        bbox_matches.append(match)
                # Search for captions using text analysis (keywords)
                # if more than one bbox matches are found
                if len(bbox_matches) == 0:
                    pass # don't set any caption
                elif len(bbox_matches) == 1:
                    caption = ""
                    for text_line in bbox_matches[0]:
                        caption += text_line.get_text().strip() 
                    visual.set_caption(caption)
                else: # more than one matches in bbox_matches
                    for _text in bbox_matches:
                        text_match = find_caption_by_text(_text, keywords=CAP_SETTINGS["keywords"])
                    if text_match:
                        caption = ""
                        for text_line in bbox_matches[0]:
                            caption += text_line.get_text().strip() 
                    # Set the caption to the firt text match.
                    # All other matches will be ignored. 
                    # This may introduce mistakes
                        try:
                            visual.set_caption(caption)
                        except Warning: # ignore warnings when caption is already set.
                            pass
                        
                # TODO: https://github.com/pdfminer/pdfminer.six/pull/854
                # rename image name to include page number
                img.name =  str(entry_id) + "-page" + str(page["page_number"]) + "-" + img.name
                # save image to file
            
                try:
                    print(img)
                    print(img.stream, img.colorspace)
                    image_file_name =iw.export_image(img) # returns image file name, 
                    # which last part is automatically generated by pdfminer to guarantee uniqueness
                except ValueError as e:
                    print(f"Image has unsupported bit depth? Image:{img.name}")
                    raise e
                    

                # set location of image
                visual.set_location(os.path.join(image_directory, image_file_name))

                # add visual to entry
                entry.add_visual(visual)

    # ORGANIZE ENTRY FILES 
    # for data management purposes, the files are organized in the following way, after processing:
        # PDF and MODS files are copied to the TMP_DIR, 
        # and images are saved to subdirectories in the entry direct, subdirectory name is the pdf file name
        # e.g.:  00001/00001/page1-00001.png, 00001/00001/page2-00001.png

    # Copy MODS file and PDF files to output directory
    shutil.copy(MODS_FILE, TMP_DIR)
    for pdf in PDF_FILES:
        shutil.copy(pdf, TMP_DIR)

    end_time = time.time()
    print("total time", end_time - start_time)

    # SAVE METADATA TO JSON FILE
    entry.save_to_json(os.path.join(entry_directory,"metadata.json"))
    entry.save_to_csv(os.path.join(entry_directory,"metadata.csv"))

if __name__ == "__main__":
    
    # for id in range(11,12):
    str_id = str("11").zfill(5)
    main(str_id)
