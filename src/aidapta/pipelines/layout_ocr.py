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
import json
import copy
import aidapta.ocr as ocr
from typing import Optional
from pdfminer.high_level import extract_pages
from pdfminer.image import ImageWriter
from pdfminer.pdfparser import PDFSyntaxError
from tqdm import tqdm
from aidapta.utils import extract_mods_metadata, get_entry_number_from_mods
from aidapta.captions import find_caption_by_distance, find_caption_by_text, BoundingBox
from aidapta.layout import sort_layout_elements, create_output_dir
from aidapta.metadata import Document, Metadata, Visual, FilePath
from aidapta.captions import OffsetDistance
from typing_extensions import Annotated 
from pdfminer.pdftypes import PDFNotImplementedError

# Disable PIL image size limit
import PIL.Image
PIL.Image.MAX_IMAGE_PIXELS = None


app = typer.Typer()

@app.command()
def run(entry_range: str = typer.Argument(help="Range of entries to process. e.g.: 1-10"),
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
    # This will become the root path for a Visual object
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
            "width": 120,
            "height": 120,
        }
    }

    # OCR ANALYSIS SETTINGS

    ocr_settings = {
        "caption": {
            "offset": [50, "px"],
            "direction": "down",
            "keywords": ['figure', 'caption', 'figuur'] 
            },
        "image": {
            "width": 120,
            "height": 120,
        },
        "resolution": 250, # dpi, default for ocr analysis,
        "resize": 30000, # px, if image is larger than this, it will be resized before performing OCR,
         # this affect the quality of output images
    }

    # Create output directory for the entry
    entry_directory = create_output_dir(OUTPUT_DIR, entry_id)
    
    # start logging
    logger = logging.getLogger('layout_ocr')

    # Set the logging level to INFO (or any other desired level)
    logger.setLevel(logging.INFO)

    # Create a file handler to save log messages to a file
    log_file = os.path.join(OUTPUT_DIR, entry_id, entry_id + '.log')
    file_handler = logging.FileHandler(log_file)

    # Create a formatter to specify the log message format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)
    
    logger.info("Starting Layout+OCR pipeline for entry: " + entry_id)

    # logging.info("Image settings: " + str(cfg.layout.image_settings))

    # EXTRACT METADATA FROM MODS FILE
    meta_blob = extract_mods_metadata(MODS_FILE)

    # FIND PDF FILES FOR A GIVEN ENTRY
    PDF_FILES = []
    for f in tqdm(os.listdir(DATA_DIR), desc="Collecting PDF files", unit="files"):
        if f.startswith(entry_id) and f.endswith(".pdf"):
            PDF_FILES.append(DATA_DIR+f)
    
    logger.info("PDF files in entry: " + str(len(PDF_FILES)))

    # INITIALISE METADATA OBJECT
    entry = Metadata()
    # add metadata from MODS file
    entry.set_metadata(meta_blob)

    # print('meta blob', meta_blob)
    # set web url. This is not part of the MODS file
    base_url = "http://resolver.tudelft.nl/" 
    entry.add_web_url(base_url)

    layout_offset_dist = OffsetDistance (layout_settings["caption"]["offset"][0], 
                                         layout_settings["caption"]["offset"][1])

    ocr_offset_dist = OffsetDistance (ocr_settings["caption"]["offset"][0], 
                                         ocr_settings["caption"]["offset"][1])

    # PROCESS PDF FILES
    pdf_document_counter = 1
    start_processing_time = time.time()
    for pdf in PDF_FILES:
        # print("--> Processing file:", pdf)
        pdf_root = DATA_DIR
        pdf_file_path = os.path.basename(pdf).split("/")[-1] # file name with extension
        logger.info("Processing file: " + pdf_file_path)
        # create document object
        pdf_formatted_path = FilePath(root_path=pdf_root, file_path=pdf_file_path)
        pdf_document = Document(pdf_formatted_path)
        entry.add_document(pdf_document)

        # PREPARE OUTPUT DIRECTORY
        pdf_file_name = 'pdf-' + str(pdf_document_counter).zfill(3)
        image_directory = create_output_dir(entry_directory, 
                                            pdf_file_name) # returns a pathlib object
               
        # ocr_directory = create_output_dir(image_directory, "ocr")

        # PROCESS SINGLE PDF 
        pdf_pages = extract_pages(pdf_document.location.full_path())
        pages = []

        # this checks for malformed or corrupted PDF files
        ### ==================================== ###
        try:
            for page in tqdm(pdf_pages, desc="Sorting pages layout analysis", unit="pages"):
                elements = sort_layout_elements(page, img_width=layout_settings["image"]["width"],
                                                img_height = layout_settings["image"]["height"] 
                                                )
                pages.append( elements )
        except PDFSyntaxError: # skip malformed or corrupted PDF files
            logger.error("PDFSyntaxError. Couldn't read: " + pdf_document.location.file_path ) 
        finally:
            del elements # free memory

        no_image_pages = []

        # PROCESS PAGE USING LAYOUT ANALYSIS
        for page in tqdm(pages, desc="layout analysis", total=len(pages), 
                         unit="sorted pages"):

            iw = ImageWriter(image_directory)

            if page["images"] == []: # collects pages where no images were found by layout analysis # TODO: fix this
                no_image_pages.append(page)
        
            for img in page["images"]:
            
                visual = Visual(document_page=page["page_number"], 
                                document=pdf_document, bbox=img.bbox, bbox_units="pt")
                
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
                    visual.set_caption(caption) #TODO: fix this
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
                            visual.set_caption(caption) # TODO: fix this
                        except Warning: # ignore warnings when caption is already set.
                            logger.warning("Caption already set for image: " + img.name)
                            pass
                        
                # rename image name to include page number
                img.name =  str(entry_id) + "-page" + str(page["page_number"]) + "-" + img.name
                # save image to file
            
                try:
                    image_file_name =iw.export_image(img) # returns image file name, 
                    # which last part is automatically generated by pdfminer to guarantee uniqueness
                    # print("image file name", image_file_name)
                except ValueError:
                    # issue with MCYK images with 4 bits per pixel
                    # https://github.com/pdfminer/pdfminer.six/pull/854
                    logger.warning("Image with unsupported format wasn't saved:" + img.name)
                except UnboundLocalError:
                    logger.warning("Decocder doesn't support image stream, therefore not saved:" + img.name)
                except PDFNotImplementedError:
                    logger.warning("PDF stream unsupported format,  image not saved:" + img.name)
                except PIL.UnidentifiedImageError:
                    logger.warning("PIL.UnidentifiedImageError io.BytesIO,  image not saved:" + img.name)
                except IndexError: # avoid decoding errors in PNG predictor for some images
                    logger.warning("IndexError, png predictor/decoder failed:" + img.name)
                except KeyError: # avoid decoding error of JBIG2 images
                    logger.warning("KeyError, JBIG2Globals decoder failed:" + img.name)
                else:
                    visual.set_location(FilePath( root_path=OUTPUT_DIR, file_path= entry_id + '/'  + pdf_file_name + '/' + image_file_name))
            
                    # add visual to entry
                    entry.add_visual(visual)

        pdf_document_counter += 1
        del pages # free memory

        # PROCESS PAGE USING OCR ANALYSIS
        logger.info("OCR input image resolution (DPI): " + str(ocr_settings["resolution"]))
        for page in tqdm(no_image_pages, desc="OCR analysis", total=len(no_image_pages), unit="OCR pages"):

            # if page["images"] == []: # apply to pages where no images were found by layout analysis
     
            page_image = ocr.convert_pdf_to_image( # returns a list with one element
                pdf_document.location.full_path(), 
                dpi= ocr_settings["resolution"], 
                first_page=page["page_number"], 
                last_page=page["page_number"],
                )

            
            ocr_results = ocr.extract_bboxes_from_horc(
                page_image, config='--psm 3 --oem 1', 
                entry_id=entry_id, 
                page_number=page["page_number"],
                resize=ocr_settings["resize"]
                )
            

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
                                                        aspect_ratio = (20/1, ">")
                                                        )
                ocr_results[page_id]["bboxes"]= filtered_ratio      

                # filter boxes with extremely vertically long
                filtered_ratio = ocr.filter_bbox_by_size(ocr_results[page_id]["bboxes"],
                                                        aspect_ratio = (1/20, "<")
                                                        )
                ocr_results[page_id]["bboxes"]= filtered_ratio              
        
                # filter boxes contained by larger boxes
                filtered_contained = ocr.filter_bbox_contained(ocr_results[page_id]["bboxes"])
                ocr_results[page_id]["bboxes"]= filtered_contained

                # print("OCR text boxes: ", ocr_results[page_id]["text_bboxes"])

                # exclude pages with no bboxes (a.k.a. no inner images)
                # print("searching ocr captions")
                if len (ocr_results[page_id]["bboxes"]) > 0:
                    for bbox_id in ocr_results[page_id]["bboxes"]: # loop over image boxes

                        bbox_cords = ocr_results[page_id]["bboxes"][bbox_id] # bbox of image in page

                        visual = Visual(document=pdf_document,
                                        document_page=page["page_number"],
                                        bbox=bbox_cords, bbox_units="px")
                        
                        # Search for captions using proximity to image
                        # This may generate multiple matches
                        bbox_matches =[]
                        bbox_object = BoundingBox(tuple(bbox_cords), ocr_settings["resolution"])

                        # print('searching for caption for: ', bbox_id)
                        for text_box in ocr_results[page_id]["text_bboxes"].items():

                            # print("text box: ", text_box)

                            text_cords = text_box[1]
                            text_object = BoundingBox(tuple(text_cords), ocr_settings["resolution"])
                            match = find_caption_by_distance(
                                bbox_object, 
                                text_object, 
                                offset= ocr_offset_dist,
                                direction= ocr_settings["caption"]["direction"]
                            )
                            if match:
                                bbox_matches.append(match)
                                # print('matched text id: ', text_box[0])
                                # print(match)
                        
                        # print('found matches: ', len(bbox_matches))

                        # print(bbox_matches)
                        # caption = None
                        if len(bbox_matches) == 0: # if more than one bbox matches, move to text analysis
                            pass
                        else:
                            # get text from image   
                            for match in bbox_matches:
                                # print(match.bbox_px())
                                ########################
                                # TODO: decode text from strings. Tests with multiple image files.

                                ocr_caption = ocr.region_to_string(page_image[0], match.bbox_px(), config='--psm 3 --oem 1')
                                # print('ocr box: ', match.bbox_px())
                                # print('orc caption: ', ocr_caption)
                        
                                if ocr_caption:
                                    try:
                                        visual.set_caption(ocr_caption)
                                    except Warning: # ignore warnings when caption is already set.
                                        logger.warning("Caption already set for: " + str(match.bbox()))
                    

                        visual.set_location(FilePath(root_path=OUTPUT_DIR, file_path= entry_id + '/'  + pdf_file_name + '/' + f'{page_id}-{bbox_id}.png'))

                        # visual.set_location(FilePath(str(image_directory), f'{page_id}-{bbox_id}.png' ))

                        entry.add_visual(visual)

            ocr.crop_images_to_bbox(ocr_results, image_directory)         
            del page_image # free memory

    end_processing_time = time.time()
    processing_time = end_processing_time - start_processing_time
    logger.info("PDF processing time: " + str(processing_time))
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


    if len(PDF_FILES) > 0:
        for pdf in PDF_FILES:
            if not os.path.exists(os.path.join(temp_entry_directory, os.path.basename(pdf) )):
                shutil.copy2(pdf, temp_entry_directory)
        
    logger.info("Extracted visuals: " + str(entry.total_visuals))

    # SAVE METADATA TO files
    csv_file = str(os.path.join(entry_directory, entry_id) + "-metadata.csv")
    json_file = str(os.path.join(entry_directory, entry_id) + "-metadata.json")
    entry.save_to_csv(csv_file)
    entry.save_to_json(json_file)

    if not entry.uuid:
        logger.warning("No identifier found in MODS file")

    # SAVE settings to json file
    settings_file = str(os.path.join(entry_directory, entry_id) + "-settings.json")
    with open(settings_file, 'w') as f:
        json.dump({"layout": layout_settings, "ocr": ocr_settings}, f, indent=4)
        

    end_time = time.time()
    total_time = end_time - start_time
    logger.info("Total time: " + str(total_time))
    print("total time", total_time)
  
if __name__ == "__main__":
    
    # app()

    pipeline("00193",
            "/home/manuel/Documents/devel/desing-handbook/data-pipelines/data/pdf-issues/",
            "/home/manuel/Documents/devel/desing-handbook/data-pipelines/data/test/",
            "/home/manuel/Documents/devel/desing-handbook/data-pipelines/data/test/tmp/"
            )
    