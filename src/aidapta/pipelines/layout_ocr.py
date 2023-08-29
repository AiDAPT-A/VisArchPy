"""A pipeline for extracting metadata from MODS files and imges from PDF files.
It applyes image search and analysis based  in two steps:
    First, it analyses the layout of the PDF file using the pdfminer.six library.
    Second, it applies OCR to the pages where no images were found by layout analysis.
Author: Manuel Garcia
"""

import os
import pathlib
import shutil
import time
import logging
import typer
import aidapta.ocr as ocr
from typing import Optional
from pdfminer.high_level import extract_pages
from pdfminer.image import ImageWriter
from tqdm import tqdm
from aidapta.utils import extract_mods_metadata, get_entry_number_from_mods
from aidapta.captions import find_caption_by_distance, find_caption_by_text, BoundingBox
from aidapta.layout import sort_layout_elements, create_output_dir
from aidapta.metadata import Document, Metadata, Visual, FilePath
from aidapta.captions import OffsetDistance
from typing_extensions import Annotated 
import pytesseract as tess

app = typer.Typer()

@app.command()
def layout_ocr(entry_range: str = typer.Argument(help="Range of entries to process. e.g.: 1-10"),
               data_directory: str = typer.Argument( help="path to directory containing MODS and pdf files"),
               output_directory: str = typer.Argument( help="path to directory where results will be saved"),
               temp_directory: Annotated[Optional[str], typer.Argument(help="temporary directory")] = None
               ) -> None:
    """Extracts metadata from MODS files and images from PDF files
      using layout and OCR analysis."""
    
    start_id = int(entry_range.split("-")[0])
    end_id = int(entry_range.split("-")[1])

    for id in range(start_id, end_id+1):
        str_id = str(id).zfill(5)

        pipeline(str_id,
                 data_directory,
                 output_directory,
                 temp_directory)


def pipeline(entry_id:str, data_directory: str, output_directory: str, temp_directory: str = None) -> None:
    """A pipeline for extracting metadata from MODS files and imges from PDF files
      using layout and OCR analysis.
      
    Parameters
    ----------

    entry_id : str
        The entry id, which is the same as the MODS file name without the extension.
    data_directory : str
        The path to the directory containing the MODS and PDF files.
    output_directory : str
        The path to the directory where the results will be saved.
      """
    
    start_time = time.time()
    #SETTINGS                              
    # SELECT INPUT DIRECTORY
    DATA_DIR = data_directory

    # SELECT OUTPUT DIRECTORY
    # if run multiple times to the same output directory, the images will be duplicated and 
    # metadata will be overwritten
    # This will become the root directory for a Visual object
    OUTPUT_DIR = output_directory # an absolute path is recommended   
    # SET MODS FILE
    entry_id = entry_id
    MODS_FILE = os.path.join(DATA_DIR, entry_id+"_mods.xml")

    # TEMPORARY DIRECTORY
    # this directory is used to store temporary files. PDF files are copied to this directory

    if temp_directory:
        TMP_DIR = temp_directory
    else:
        TMP_DIR = os.path.join("./tmp")

    # LAYOUT ANALYSIS SETTINGS
    
    layout_settings = {
        "caption": {
            "offset": [4, "mm"],
            "direction": "down",
            "keywords": ['figure', 'caption', 'figuur'] 
            },
        "image": {
            "width": 100,
            "height": 100,
        }
    }

    # OCR ANALYSIS SETTINGS

    ocr_settings = {
        "caption": {
            "offset": [10, "px"],
            "direction": "down",
            "keywords": ['figure', 'caption', 'figuur'] 
            },
        "image": {
            "width": 100,
            "height": 100,
        },
        "resolution": 200,
        "output_resolution": 300,
    }

    # Create output directory for the entry
    entry_directory = create_output_dir(OUTPUT_DIR, entry_id)
    
    # start logging
    logging.basicConfig(filename=os.path.join(OUTPUT_DIR, 
                        entry_id, entry_id + '.log'), 
                        encoding='utf-8', 
                        level=logging.INFO)
    
    logging.info("Starting Layout+OCR pipeline for entry: " + entry_id)

    # logging.info("Image settings: " + str(cfg.layout.image_settings))

    # EXTRACT METADATA FROM MODS FILE
    meta_blob = extract_mods_metadata(MODS_FILE)

    # FIND PDF FILES FOR A GIVEN ENTRY
    PDF_FILES = []
    for f in tqdm(os.listdir(DATA_DIR), desc="Collecting PDF files", unit="files"):
        if f.startswith(entry_id) and f.endswith(".pdf"):
            PDF_FILES.append(DATA_DIR+f)

    # INITIALISE METADATA OBJECT
    entry = Metadata()
    # add metadata from MODS file
    entry.set_metadata(meta_blob)
    # set web url. This is not part of the MODS file
    base_url = "http://resolver.tudelft.nl/" 
    entry.add_web_url(base_url)

    layout_offset_dist = OffsetDistance (layout_settings["caption"]["offset"][0], 
                                         layout_settings["caption"]["offset"][1])

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
               
        # ocr_directory = create_output_dir(image_directory, "ocr")

        # PROCESS SINGLE PDF 
        pdf_pages = extract_pages(pdf_document.location)

        pages = []
        for page in tqdm(pdf_pages, desc="Reading pages", unit="pages"):
            elements = sort_layout_elements(page, img_width=layout_settings["image"]["width"],
                                            img_height = layout_settings["image"]["height"] 
                                            )
            pages.append(elements)

        ocr_pages = []

        # PROCESS PAGE USING LAYOUT ANALYSIS
        for page in tqdm(pages, desc="layout analysis", total=len(pages), 
                         unit="sorted pages"):

            iw = ImageWriter(image_directory)

            if page["images"] == []: # collects pages where no images were found by layout analysis
                ocr_pages.append(page)
        
            for img in page["images"]:
            
                visual = Visual(document_page=page["page_number"], 
                                document=pdf_document, bbox=img.bbox)
                
                # Search for captions using proximity to image
                # This may generate multiple matches
         
                bbox_matches =[]
                for _text in page["texts"]:
                    match = find_caption_by_distance(
                        img, 
                        _text, 
                        offset= layout_offset_dist, 
                        direction= layout_settings["caption"]["direction"]
                    )
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
                        text_match = find_caption_by_text(_text, keywords=layout_settings["caption"]["keywords"])
                    if text_match:
                        caption = ""
                        for text_line in bbox_matches[0]:
                            caption += text_line.get_text().strip() 
                    # Set the caption to the first text match.
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
            
                try:
                    image_file_name =iw.export_image(img) # returns image file name, 
                    # which last part is automatically generated by pdfminer to guarantee uniqueness
                except ValueError:
                    # issue with MCYK images with 4 bits per pixel
                    # https://github.com/pdfminer/pdfminer.six/pull/854
                    logging.warning("Image with unsupported format wasn't saved:" + img.name)
                    pass
                    
                visual.set_location(FilePath(
                                         str(image_directory), 
                                         image_file_name
                                        ) 
                                    ) 
            
                # add visual to entry
                entry.add_visual(visual)

        # PROCESS PAGE USING OCR ANALYSIS
        for ocr_page in tqdm(ocr_pages, desc="OCR analysis", total=len(ocr_pages), unit="OCR pages"):

            # if page["images"] == []: # apply to pages where no images were found by layout analysis
                page_image = ocr.convert_pdf_to_image(
                    pdf_document.location, 
                    dpi= ocr_settings["resolution"], 
                    first_page=ocr_page["page_number"], 
                    last_page=ocr_page["page_number"],
                    )
 
                ocr_results = ocr.extract_bboxes_from_horc(
                    page_image, config='--psm 3 --oem 1', 
                    entry_id=entry_id, 
                    page_number=ocr_page["page_number"])
                
                if ocr_results:  # skips pages with no results
                    page_key = ocr_results.keys()
                    page_id = list(page_key)[0]

                    # FILTERING OCR RESULTS
                    # filter by bbox size
                    filtered_width_height = ocr.filter_bbox_by_size(
                                                            ocr_results[page_id]["bboxes"],
                                                            min_width= ocr_settings["image"]["width"],
                                                            min_height= ocr_settings["image"]["height"],
                                                            )
                    
                    ocr_results[page_id]["bboxes"] = filtered_width_height

                    # # filter bboxes that are extremely horizontally long 
                    filtered_ratio = ocr.filter_bbox_by_size(
                                                            ocr_results[page_id]["bboxes"],
                                                            aspect_ratio = (15/1, ">")
                                                            )
                    ocr_results[page_id]["bboxes"]= filtered_ratio      

                    # filter boxes with extremely vertically long
                    filtered_ratio = ocr.filter_bbox_by_size(ocr_results[page_id]["bboxes"],
                                                            aspect_ratio = (1/15, "<")
                                                            )
                    ocr_results[page_id]["bboxes"]= filtered_ratio              
            
                    # filter boxes contained by larger boxes
                    filtered_contained = ocr.filter_bbox_contained(ocr_results[page_id]["bboxes"])
                    ocr_results[page_id]["bboxes"]= filtered_contained
                    # print(ocr_page)

                    # exclude pages with no bboxes (a.k.a. no inner images)
                    if len (ocr_results[page_id]["bboxes"]) > 0:
                        for bbox_id in ocr_results[page_id]["bboxes"]: # loop over image boxes
                            print('box in ocr results ', bbox_id)
                            bbox_cords = ocr_results[page_id]["bboxes"][bbox_id]
                            print('coords', bbox_cords)
                            visual = Visual(document=pdf_document,
                                            document_page=ocr_page["page_number"],
                                            bbox=bbox_cords)
                            
                            # Search for captions using proximity to image
                            # This may generate multiple matches
                            bbox_matches =[]
                            bbox_object = BoundingBox(tuple(bbox_cords))

                            print(ocr_page)

                            # TODO: ocr results and layout analysis have bounding
                            # boxes in different coordinates. Implement conversion in BoundingBox class? Add abstractions for a homogeneous data
                            # model during processing? 
                            for text_box_id in ocr_page["text_bboxes"]:
                            
                                text_cords = ocr_page["text_bboxes"][text_box_id]
                                text_object = BoundingBox(tuple(text_cords))
                                match = find_caption_by_distance(
                                    bbox_object, 
                                    text_object, 
                                    offset= layout_offset_dist, 
                                    direction= layout_settings["caption"]["direction"]
                                )
                                if match:
                                    bbox_matches.append(match)
                            
                            if len(bbox_matches) == 0: # if more than one bbox matches, move to text analysis
                                pass
                            else:
                                # get text from image   
                                for match in bbox_matches:
                                    caption = tess.image_to_string(ocr_page[page_id]["image"],
                                            boxes = match.bbox
                                    )
                                try:
                                    visual.set_caption(caption)
                                except Warning: # ignore warnings when caption is already set.
                                    logging.warning("Caption already set for: " + bbox)
                            
                        
                #         visual.set_location(FilePath(str(image_directory), f'{page_id}-{bbox}.png' ))
                #         entry.add_visual(visual)

                # ocr.mark_bounding_boxes(ocr_results, OUTPUT_DIR, filter_size=100)    
                ocr.crop_images_to_bbox(ocr_results, OUTPUT_DIR)         
    
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
    print("temp_entry_directory", temp_entry_directory)

    mods_file_name = pathlib.Path(MODS_FILE).stem + ".xml"
    if not os.path.exists(os.path.join(temp_entry_directory, mods_file_name)):
        shutil.copy2(MODS_FILE, temp_entry_directory)

    for pdf in PDF_FILES:
        if not os.path.exists(os.path.join(temp_entry_directory, pdf)):
            shutil.copy2(pdf, temp_entry_directory)
    
    # SAVE METADATA TO files

    csv_file = str(os.path.join(entry_directory, entry_id) + "-metadata.csv")
    json_file = str(os.path.join(entry_directory, entry_id) + "-metadata.json")
    entry.save_to_csv(csv_file)
    entry.save_to_json(json_file)

    end_time = time.time()
    total_time = end_time - start_time
    logging.info("Total time: " + str(total_time))
    print("total time", total_time)
  
if __name__ == "__main__":
    
    pipeline("00000",
            "/home/manuel/Documents/devel/desing-handbook/data-pipelines/data/test/",
            "/home/manuel/Documents/devel/desing-handbook/data-pipelines/data/test/",
            "/home/manuel/Documents/devel/desing-handbook/data-pipelines/data/test/tmp/"
            )
