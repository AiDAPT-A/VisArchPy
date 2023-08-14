"""A pipeline for extracting metadata from MODS files and imges from PDF files.
Author: Manuel Garcia
"""

import hydra
import os
import pathlib
import shutil
import time
import logging
import aidapta.ocr as ocr
from pdfminer.high_level import extract_pages
from pdfminer.image import ImageWriter
from tqdm import tqdm
from aidapta.utils import extract_mods_metadata, get_entry_number_from_mods
from aidapta.captions import find_caption_by_bbox, find_caption_by_text
from aidapta.layout import sort_layout_elements, create_output_dir
from aidapta.metadata import Document, Metadata, Visual, FilePath
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="", config_name="config")
def main(cfg: DictConfig) -> None:

    start_time = time.time()

    #SETTINGS                              

    # SELECT INPUT DIRECTORY
    INPUT_DIR = cfg.dir.input # an absolute path is recommended,

    # SELECT OUTPUT DIRECTORY
    # if run multiple times to the same output directory, the images will be duplicated and 
    # metadata will be overwritten
    # This will become the root directory for a Visual object
    OUTPUT_DIR = cfg.dir.output # an absolute path is recommended   
    # SET MODS FILE
    entry_id = cfg.entry
    MODS_FILE = os.path.join(INPUT_DIR, entry_id+"_mods.xml")

    # TEMPORARY DIRECTORY
    # this directory is used to store temporary files. PDF files are copied to this directory
    TMP_DIR = cfg.dir.temp 
    
    # Create output directory for the entry
    entry_directory = create_output_dir(OUTPUT_DIR, entry_id)
    
    # start logging
    logging.basicConfig(filename=os.path.join(OUTPUT_DIR, entry_id, entry_id + '.log'), encoding='utf-8', level=logging.INFO)
    logging.info("Starting pipeline for entry: " + entry_id)

    logging.info("Image settings: " + str(cfg.layout.image_settings))

    # EXTRACT METADATA FROM MODS FILE
    meta_blob = extract_mods_metadata(MODS_FILE)

    # FIND PDF FILES FOR A GIVEN ENTRY
    PDF_FILES = []
    for f in tqdm(os.listdir(INPUT_DIR), desc="Collecting PDF files", unit="files"):
        if f.startswith(entry_id) and f.endswith(".pdf"):
            PDF_FILES.append(INPUT_DIR+f)

    # INITIALISE METADATA OBJECT
    entry = Metadata()
    # add metadata from MODS file
    entry.set_metadata(meta_blob)
    # set web url. This is not part of the MODS file
    base_url = "http://resolver.tudelft.nl/" 
    entry.add_web_url(base_url)

    # PROCESS PDF FILES
    start_processing_time = time.time()
    for pdf in PDF_FILES:
        print("--> Processing file:", pdf)
        logging.info("Processing file: " + pdf)
        # create document object
        pdf_document = Document(pdf)
        entry.add_document(pdf_document)

        # PREPARE OUTPUT DIRECTORY
        pdf_file_name = pathlib.Path(pdf_document.location).stem
        image_directory = create_output_dir(entry_directory, 
                                            pdf_file_name) # returns a pathlib object
        
        ocr_directory = create_output_dir(image_directory, "ocr")

        # PROCESS SINGLE PDF 
        pdf_pages = extract_pages(pdf_document.location)

        pages = []
        for page in tqdm(pdf_pages, desc="Reading pages", unit="pages"):
            elements = sort_layout_elements(page, img_height = cfg.layout.image_settings.width, 
                                            img_width=cfg.layout.image_settings.height)
            pages.append(elements)

        ocr_pages = []
        # PROCESS PAGE USING LAYOUT ANALYSIS
        for page in tqdm(pages, desc="layout analysis", total=len(pages), 
                         unit="sorted pages"):

            iw = ImageWriter(image_directory)

            if page["images"] == []:
                ocr_pages.append(page)
        
            for img in page["images"]:
            
                visual = Visual(document_page=page["page_number"], 
                                document=pdf_document, bbox=img.bbox)
                
                # Search for captions using proximity to image
                # This may generate multiple matches
                bbox_matches =[]
                for _text in page["texts"]:
                    match = find_caption_by_bbox(img, _text, offset= cfg.layout.caption_settings.offset, 
                                                direction= cfg.layout.caption_settings.direction)
                    if match:
                        bbox_matches.append(match)
                # Search for captions using proximity (offset) and text analyses (keywords)
                if len(bbox_matches) == 0: # if more than one bbox matches, move to text analysis
                    pass # don't set any caption
                elif len(bbox_matches) == 1:
                    caption = ""
                    for text_line in bbox_matches[0]:
                        caption += text_line.get_text().strip() 
                    visual.set_caption(caption)
                else: # more than one matches in bbox_matches
                    for _text in bbox_matches:
                        text_match = find_caption_by_text(_text, keywords=cfg.layout.caption_settings.keywords)
                    if text_match:
                        caption = ""
                        for text_line in bbox_matches[0]:
                            caption += text_line.get_text().strip() 
                    # Set the caption to the first text match.
                    # TODO: implement recording multiple matches when no single match can be ruled out
                    # All other matches will be ignored. 
                    # This may introduce errors, but it is better than having multiple captions
                        try:
                            visual.set_caption(caption)
                        except Warning: # ignore warnings when caption is already set.
                            logging.warning("Caption already set for image: " + img.name)
                            pass
                        
                # rename image name to include page number
                img.name =  str(entry_id) + "-page" + str(page["page_number"]) + "-" + img.name
                # save image to file
            
                # TODO: https://github.com/pdfminer/pdfminer.six/pull/854
                try:
                    image_file_name =iw.export_image(img) # returns image file name, 
                    # which last part is automatically generated by pdfminer to guarantee uniqueness
                except ValueError:
                    # issue with MCYK images with 4 bits per pixel
                    logging.warning("Image with unsupported format wasn't saved:" + img.name)
                    pass
                    
                visual.set_location( FilePath(
                                         str(image_directory), image_file_name
                                        ) 
                                    ) 
            
                # add visual to entry
                entry.add_visual(visual)

        # PROCESS PAGE USING OCR ANALYSIS
        for ocr_page in tqdm(ocr_pages, desc="OCR analysis", total=len(ocr_pages), unit="OCR pages"):

            # if page["images"] == []: # apply to pages where no images were found by layout analysis
                page_image = ocr.convert_pdf_to_image(pdf_document.location, dpi= cfg.ocr.resolution, first_page=ocr_page["page_number"], last_page=ocr_page["page_number"])
                ocr_results = ocr.extract_bboxes_from_horc(page_image, config='--psm 3 --oem 1', entry_id=entry_id, page_number=ocr_page["page_number"])
                ocr.marked_bounding_boxes(ocr_results, ocr_directory, filter_size=100)      
    
    end_processing_time = time.time()
    processing_time = end_processing_time - start_processing_time
    logging.info("PDF processing time: " + str(processing_time))
    # ORGANIZE ENTRY FILES 
    # for data management purposes, the files are organized in the following way, after processing:
        # PDF and MODS files are copied to the TMP_DIR, 
        # and images are saved to subdirectories in the entry direct, subdirectory name is the pdf file name
        # e.g.:  00001/00001/page1-00001.png, 00001/00001/page2-00001.png

    # Copy MODS file and PDF files to output directory
    temp_entry_directory = create_output_dir( os.path.join(TMP_DIR, entry_id))

    mods_file_name = pathlib.Path(MODS_FILE).stem + ".xml"
    if not os.path.exists(os.path.join(temp_entry_directory, mods_file_name)):
        shutil.copy2(MODS_FILE, temp_entry_directory)

    for pdf in PDF_FILES:
        if not os.path.exists(os.path.join(temp_entry_directory, pdf)):
            shutil.copy2(pdf, temp_entry_directory)
    
    # SAVE METADATA TO files
    # json_file = str(os.path.join(entry_directory, entry_id) + "-metadata.json")
    csv_file = str(os.path.join(entry_directory, entry_id) + "-metadata.csv")
    json_file = str(os.path.join(entry_directory, entry_id) + "-metadata.json")

    end_time = time.time()
    total_time = end_time - start_time
    logging.info("Total time: " + str(total_time))
    print("total time", total_time)
  
if __name__ == "__main__":
    
    # for id in range(11,12):
    str_id = str(1).zfill(5)
    main()
