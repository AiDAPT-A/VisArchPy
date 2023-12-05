"""Data pipelines for extracting metadata from MODS files and imges from
PDF files.
Author: Manuel Garcia Alvarez
"""

import os
import pathlib
import shutil
import time
import logging
import json
from logging import Logger
import visarchpy.ocr as ocr
from pdfminer.high_level import extract_pages
from pdfminer.image import ImageWriter
from pdfminer.pdfparser import PDFSyntaxError
from tqdm import tqdm
from visarchpy.utils import create_output_dir
from visarchpy.captions import find_caption_by_distance, find_caption_by_text
from visarchpy.captions import BoundingBox
from visarchpy.pdf import sort_layout_elements
from visarchpy.metadata import Document, Metadata, Visual, FilePath, extract_mods_metadata
from visarchpy.captions import Offset
from pdfminer.pdftypes import PDFNotImplementedError
from pdfminer.layout import LTPage
from abc import ABC, abstractmethod

# Disable PIL image size limit
import PIL.Image
PIL.Image.MAX_IMAGE_PIXELS = None


# Common interface for all pipelines
class Pipeline(ABC):
    """Abstract base class for all pipelines."""

    def __init__(self, data_directory: str, output_directory: str,
                 settings: dict = None, metadata_file: str = None,
                 temp_directory: str = None, ignore_id: bool = False) -> None:
        """"
        Parameters
        ----------

        data_directory : str
            The path to a directory containing the PDF files to be processed.
        output_directory : str
            The path to a directory where the results will be saved.
        metadata_file : str
            path to a MODS file containing metadata to be associated to the
            extracted images. If no file is provided, the fields in the output
            metadata file will be empty.
        temp_directory : str
            If provided PDF files in the data directory will be copied to this
            directory. This is useful for data management purposes, and it was
            introduced to manage the TU Delft dataset. Defaults to None.
        ignore_id : bool
            If True, it won't filter PDF by ID (TU Delft dataset specific). Defaults to False.
            As a result, all PDF files in the data directory will be processed.

        """
        self.data_directory = data_directory
        self.output_directory = output_directory
        self.settings = settings
        self.metadata_file = metadata_file
        self.temp_directory = temp_directory
        self.ignore_id = ignore_id

    @property
    def settings(self) -> dict:
        """Gets settings for the pipeline."""
        return self._settings

    @settings.setter
    def settings(self, settings: dict) -> None:
        """Sets the settings for the pipeline."""
        self._settings = settings

    @property
    def metadata_file(self) -> str:
        """Gets the path to the metadata file.
        """
        return self._metadata_file

    @metadata_file.setter
    def metadata_file(self, metadata_file: str) -> None:
        """Sets the path to the metadata file.
        """
        self._metadata_file = metadata_file

    @property
    def temp_directory(self) -> str:
        """Gets the path to the temporary directory.
        """
        return self._temp_directory

    @temp_directory.setter
    def temp_directory(self, temp_directory: str) -> None:
        """Sets the path to the temporary directory.
        """
        self._temp_directory = temp_directory

    @property
    def ignore_id(self) -> bool:
        """Gets the ignore_id flag.
        """
        return self._ignore_id
    
    @ignore_id.setter
    def ignore_id(self, ignore_id: bool) -> None:
        """Sets the ignore_id flag.
        """
        self._ignore_id = ignore_id

    @abstractmethod
    def run(self) -> dict:
        """Run the pipeline."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Returns a string representation of the pipeline."""
        properties = vars(self)
        return f'{self.__class__.__name__} Pipeline: {properties}'


def extract_visuals_by_layout(pdf: str, metadata: Metadata, data_dir: str,
                              output_dir: str, pdf_file_dir: str,
                              layout_settings: dict, logger: Logger,
                              entry_id: str = None,
                              ) -> dict:
    """Extract visuals from a PDF file using layout analysis to
    a directory.

    Parameters
    ----------
    pdf : str
        Path to the PDF file as returned by find_pdf_files().
    metadata: Metadata
        A Metadata object to store metadata of extracted visuals.
    data_dir : str
        Path to the input directory containing the PDF file.
    output_dir : str
        Path to the output directory where visuals will be saved.
    pdf_file_dir : str
        Name of a directory where the results will be saved. This
        directory will be created inside the output directory.
    logger : Logger
        A logger object.
    entry_id : str
        Identifier of the entry being processed.
    layout_settings : dict
        A dictionary containing the settings for the layout analysis.

    Returns
    -------

    dict
        A dictionary containing the extracted visuals.
        example:

        ```python
        {'no_images_pages': <list of pages where no images were found>,
        "metadata": <Metadata object>}
        ```

    Raises
    ------
    Warning PDFSyntaxError
        If the PDF file is malformed or corrupted.
    Warning AssertionError
        If the PDF file contains an unsupported font.
    Warning TypeError
        If PDF file encounters a bug with pdfminer.
    Warning ValueError
        If image writer cannot save MCYK images with 4 bits per pixel.
        Issue: https://github.com/pdfminer/pdfminer.six/pull/854
    Warning UnboundLocalError
        If image writer's decoder doesn't support image stream.
    Warning PDFNotImplementedError
        If image writer encounters that PDF stream has an unsupported format.
    Warning PIL.UnidentifiedImageError
        If image writer encounters an error with io.BytesIO.
    Warning IndexError
        If image writer encounters an error with PNG predictor for some image.
    Warning KeyError
        If image writer encounters an error with JBIG2Globals decoder.
    Warning TypeError
        If image writer encounters an error with PDFObjRef filter.
    """

    pdf_root = data_dir
    pdf_file_path = os.path.basename(pdf).split("/")[-1]  # file name
    # with extension
    logger.info("Processing file: " + pdf_file_path)

    # create document object
    pdf_formatted_path = FilePath(root_path=pdf_root, file_path=pdf_file_path)
    pdf_document = Document(pdf_formatted_path)
    metadata.add_document(pdf_document)

    # PREPARE OUTPUT DIRECTORY
    # a directory is created for each PDF file
    entry_directory = os.path.join(output_dir, entry_id)
    # returns a pathlib object
    image_directory = create_output_dir(entry_directory, pdf_file_dir)
    # PROCESS PDF
    pdf_pages = extract_pages(pdf_document.location.full_path())
    pages = []
    no_image_pages = []  # collects pages where no images were found
    # by layout analysis
    # this checks for malformed or corrupted PDF files, and
    # unsupported fonts and some bugs in pdfminer

    try:
        for page in tqdm(pdf_pages, desc="Sorting pages layout\
                            analysis", unit="pages"):
            elements = sort_layout_elements(
                page,
                img_width=layout_settings["layout"]["image"]["width"],
                img_height=layout_settings["layout"]["image"]["height"]
            )
            pages.append(elements)

    except PDFSyntaxError:  # skip malformed or corrupted PDF files
        logger.error("PDFSyntaxError. Couldn't read: "
                     + pdf_document.location.file_path)
        Warning("PDFSyntaxError. Couldn't read: " +
                pdf_document.location.file_path)
    except AssertionError as e:  # skip unsupported fonts
        logger.error("AssertionError. Unsupported font: "
                     + pdf_document.location.file_path + str(e))
        Warning("AssertionError. Unsupported font: " +
                pdf_document.location.file_path + str(e))
    except TypeError as e:  # skip bug in pdfminer
        # no_image_pages.append(page) # pass page to OCR analysis
        logger.error("TypeError. Bug with Predictor: "
                     + pdf_document.location.file_path + str(e))
        Warning("TypeError. Bug with Predictor: " +
                pdf_document.location.file_path + str(e))
    else:
        # TODO: test this only happnes when no exception is raised
        del elements  # free memory

    layout_offset_dist = Offset(layout_settings["layout"]["caption"]
                                ["offset"][0],
                                layout_settings["layout"]["caption"]
                                ["offset"][1])
    
    # PROCESS PAGE USING LAYOUT ANALYSIS
    for page in tqdm(pages,
                     desc="layout analysis", total=len(pages),
                     unit="sorted pages"):

        iw = ImageWriter(image_directory)

        if page["images"] == []:  # collects pages where no images
            # were found by layout analysis # TODO: fix this
            no_image_pages.append(page)
        for img in page["images"]:
            visual = Visual(document_page=page["page_number"],
                            document=pdf_document,
                            bbox=img.bbox, bbox_units="pt")
            # Search for captions using proximity to image
            # This may generate multiple matches
            bbox_matches = []
            for _text in page["texts"]:
                match = find_caption_by_distance(
                    img,
                    _text,
                    offset=layout_offset_dist,
                    direction=layout_settings["layout"]["caption"]["direction"]
                    )
                if match:
                    bbox_matches.append(match)
            # Search for captions using proximity (offset) and text
            # analyses (keywords)
            if len(bbox_matches) == 0:
                pass  # don't set any caption
            elif len(bbox_matches) == 1:
                caption = ""
                for text_line in bbox_matches[0]:
                    caption += text_line.get_text().strip() 
                visual.set_caption(caption)  # TODO: fix this
            else:  # more than one matches in bbox_matches
                for _text in bbox_matches:
                    text_match = find_caption_by_text(
                        _text,
                        keywords=layout_settings["layout"]["caption"]
                        ["keywords"]
                        )
                if text_match:
                    caption = ""
                    for text_line in bbox_matches[0]:
                        caption += text_line.get_text().strip()
                # Set the caption to the first text match.
                # All other matches will be ignored.
                # This may introduce errors, but it is better than
                # having multiple captions
                    try:
                        visual.set_caption(caption)  # TODO: fix this
                    except Warning:  # ignore warnings when caption is
                        # already set.
                        logger.warning("Caption already set for image: "+img.name)
                        Warning("Caption already set for image: "+img.name)
                        pass

            # rename image name to include page number
            img.name = str(entry_id)+"-page"+str(
                page["page_number"])+"-"+img.name
            # save image to file
            try:
                image_file_name = iw.export_image(img)
                # returns image file name,
                # which last part is automatically generated by
                # pdfminer to guarantee uniqueness
            except ValueError:
                # issue with MCYK images with 4 bits per pixel
                # https://github.com/pdfminer/pdfminer.six/pull/854
                logger.warning("Image with unsupported format wasn't\
                                saved:" + img.name)
                Warning("Image with unsupported format wasn't saved:"
                        + img.name)
            except UnboundLocalError:
                logger.warning("Decocder doesn't support image stream,\
                                therefore not saved:" + img.name)
                Warning("Decocder doesn't support image stream,\
                                therefore not saved:" + img.name)
            except PDFNotImplementedError:
                logger.warning("PDF stream unsupported format,  image\
                                not saved:" + img.name)
                Warning("PDF stream unsupported format,  image\
                                not saved:" + img.name)
            except PIL.UnidentifiedImageError:
                logger.warning("PIL.UnidentifiedImageError io.BytesIO,\
                                image not saved:" + img.name)
                Warning("PIL.UnidentifiedImageError io.BytesIO,\
                                image not saved:" + img.name)
            except IndexError:  # avoid decoding errors in PNG
                # predictor for some images
                logger.warning("IndexError, png predictor/decoder\
                                failed:" + img.name)
                Warning("IndexError, png predictor/decoder\
                        failed:" + img.name)
            except KeyError:  # avoid decoding error of JBIG2 images
                logger.warning("KeyError, JBIG2Globals decoder failed:"
                               + img.name)
                Warning("KeyError, JBIG2Globals decoder failed:"
                        + img.name)
            except TypeError:  # avoid filter error with PDFObjRef
                logger.warning("TypeError, filter error PDFObjRef:"
                               + img.name)
                Warning("TypeError, filter error PDFObjRef:"
                        + img.name)
            else:
                visual.set_location(
                                    FilePath(root_path=output_dir,
                                             file_path=entry_id
                                             + '/' + pdf_file_dir
                                             + '/' + image_file_name))
                # add visual to entry
                metadata.add_visual(visual)
    del pages  # free memory

    return {'no_images_pages': no_image_pages, "metadata": metadata}


def extract_visuals_by_ocr(metadata: Metadata, data_dir: str,
                           output_dir: str, pdf_file_dir: str, logger: Logger,
                           entry_id: str = None, ocr_settings: dict = None,
                           pdf: str = None,
                           lt_pages: list[LTPage] = None) -> dict:
    """Extract visuals from a PDF file using OCR analysis to
    a directory.

    Parameters
    ----------
    metadata: Metadata
        A Metadata object to store metadata of extracted visuals.
    data_dir : str
        Path to the input directory containing the PDF file.
    output_dir : str
        Path to the output directory where visuals will be saved.
    pdf_file_dir : str
        Name of a directory where the results will be saved. This
        directory will be created inside the output directory.
    logger : Logger
        A logger object.
    entry_id : str
        Identifier of the entry being processed.
    ocr_settings : dict
        A dictionary containing setting for OCR analysis.
    pdf : str
        Path to the PDF file as returned by find_pdf_files(). If
        None, 'lt_pages' must be provided.
    lt_pages : list[LTPage]
        A list of pdfminer.six type pages to be processed. If None,
        'pdf' must be provided.

    Returns
    -------

    dict
        A dictionary containing the extracted visuals.
        example:

        ```python
        {'no_images_pages': <list of pages where no images were found>,
        "metadata": <Metadata object>}
        ```

    Raises
    ------

    ValueError
        If no PDF file or LTPage list is provided.

    """

    if pdf is None and lt_pages is None:
        raise ValueError("No PDF file or LTPage list. At least one\
                         of them must be provided.")

    if isinstance(lt_pages, list) and len(lt_pages) == 0:
        # This handles the case: chaining layout analysis and
        # OCR analysis, and layout analysis returns an empty
        # list of pages
        logger.warning("Found empty list of LTPages. No OCR performed.")
        Warning("lt_pages contains an empy list. No OCR performed.")
        return {'no_images_pages': [], "metadata": metadata}

    pdf_root = data_dir

    if pdf:
        pdf_file_path = os.path.basename(pdf).split("/")[-1]  # file name
    elif lt_pages is not None:  # to process empty list of pages
        # get last document in list. This assums that the last document
        # is the document being processed when the metadata object is
        # reused
        pdf_file_path = metadata.documents[-1].location.file_path
    logger.info("Processing file: " + pdf_file_path)

    # create document object
    pdf_formatted_path = FilePath(root_path=pdf_root, file_path=pdf_file_path)
    pdf_document = Document(pdf_formatted_path)
    metadata.add_document(pdf_document)

    # PREPARE OUTPUT DIRECTORY
    # a directory is created for each PDF file
    entry_directory = os.path.join(output_dir, entry_id)
    # returns a pathlib object
    image_directory = create_output_dir(entry_directory, pdf_file_dir)
    # PROCESS PDF
    # pdf_pages = extract_pages(pdf_document.location.full_path())
    no_image_pages = []  # collects pages where no images were found

    # PROCESS PAGE USING OCR ANALYSIS
    logger.info("OCR input image resolution (DPI): " + str(
        ocr_settings["ocr"]["resolution"]))

    if lt_pages is not None:
        pages = lt_pages
    else:
        pdf_pages = extract_pages(pdf)  # returns generator
        # intantiate generator
        
        # TODO: find a better way to make this works for both cases:
        # when OCR should be performed on all pages, and when it should
        # be performed only on pages where no images were found by layout.
        # This is a temporary solution.
        pages = []
        try:
            for page in pdf_pages:
                elements = sort_layout_elements(
                    page,
                    img_width=ocr_settings["ocr"]["image"]["width"],
                    img_height=ocr_settings["ocr"]["image"]["height"]
                )
                
                pages.append(elements)

        except PDFSyntaxError:  # skip malformed or corrupted PDF files
            logger.error("PDFSyntaxError. Couldn't read: " + pdf)
        except AssertionError as e:  # skip unsupported fonts
            # no_image_pages.append(page) # pass page to OCR analysis
            logger.error("AssertionError. Unsupported font: " + pdf + str(e))
        except TypeError as e:  # skip bug in pdfminer
            # no_image_pages.append(page) # pass page to OCR analysis
            logger.error("TypeError. Bug with Predictor: " + pdf + str(e))
        else:
            del elements  # free memory

    for page in tqdm(pages, desc="OCR analysis",  total=len(pages),
                     unit="OCR pages"):

        page_image = ocr.convert_pdf_to_image(  
            pdf_formatted_path.full_path(),
            dpi=ocr_settings["ocr"]["resolution"],
            first_page=page["page_number"],
            last_page=page["page_number"],
            )

        ocr_results = ocr.extract_bboxes_from_horc(
            page_image, config=ocr_settings["ocr"]["tesseract"],
            entry_id=entry_id,
            page_number=page["page_number"],
            resize=ocr_settings["ocr"]["resize"]
            )

        if ocr_results:  # skips pages with no results
            page_key = ocr_results.keys()
            page_id = list(page_key)[0]

            # FILTERING OCR RESULTS
            # filter by bbox size
            filtered_width_height = ocr.filter_bbox_by_size(
                                    ocr_results[page_id]["bboxes"],
                                    min_width=ocr_settings["ocr"]["image"]
                                    ["width"],
                                    min_height=ocr_settings["ocr"]["image"]
                                    ["height"],
                                    )

            ocr_results[page_id]["bboxes"] = filtered_width_height

            # # filter bboxes that are extremely horizontally long
            filtered_ratio = ocr.filter_bbox_by_size(
                                                    ocr_results[page_id]
                                                    ["bboxes"],
                                                    aspect_ratio=(20/1, ">")
                                                    )
            ocr_results[page_id]["bboxes"] = filtered_ratio

            # filter boxes with extremely vertically long
            filtered_ratio = ocr.filter_bbox_by_size(ocr_results[page_id]
                                                     ["bboxes"],
                                                     aspect_ratio=(1/20, "<")
                                                     )
            ocr_results[page_id]["bboxes"] = filtered_ratio

            # filter boxes contained by larger boxes
            filtered_contained = ocr.filter_bbox_contained(ocr_results[page_id]
                                                           ["bboxes"])
            ocr_results[page_id]["bboxes"] = filtered_contained

            # exclude pages with no bboxes (a.k.a. no inner images)
            if len(ocr_results[page_id]["bboxes"]) > 0:
                # loop over imageboxes
                for bbox_id in ocr_results[page_id]["bboxes"]:
                    # bbox of image in page
                    bbox_cords = ocr_results[page_id]["bboxes"][bbox_id]

                    visual = Visual(document=pdf_document,
                                    document_page=page["page_number"],
                                    bbox=bbox_cords, bbox_units="px")

                    # Search for captions using proximity to image
                    # This may generate multiple matches
                    bbox_matches = []
                    bbox_object = BoundingBox(tuple(bbox_cords),
                                              ocr_settings["ocr"]["resolution"])

                    for text_box in ocr_results[page_id]["text_bboxes"].items():

                        text_cords = text_box[1]
                        text_object = BoundingBox(tuple(text_cords),
                                                  ocr_settings["ocr"]
                                                  ["resolution"])

                        _offset = Offset(ocr_settings["ocr"]["caption"]
                                         ["offset"][0],
                                         ocr_settings["ocr"]["caption"]
                                         ["offset"][1])
                        match = find_caption_by_distance(
                            bbox_object,
                            text_object,
                            offset=_offset,
                            direction=ocr_settings["ocr"]["caption"]
                            ["direction"]
                        )
                        if match:
                            bbox_matches.append(match)

                    if len(bbox_matches) == 0:  # if more than one bbox 
                        # matches, skip and do text analysis
                        pass
                    else:
                        # get text from image
                        for match in bbox_matches:
                            ocr_caption = ocr.region_to_string(page_image[0],
                                                               match.bbox_px(),
                                                               config=ocr_settings["ocr"]["tesseract"])

                            if ocr_caption:
                                try:
                                    visual.set_caption(ocr_caption)
                                except Warning:  # ignore warnings when caption
                                    # is already set.
                                    logger.warning("Caption already set for: "
                                                   + str(match.bbox()))

                    visual.set_location(FilePath(root_path=output_dir,
                                                 file_path=entry_id + '/'
                                                 + pdf_file_dir + '/'
                                                 + f'{page_id}-{bbox_id}.png'))

                    metadata.add_visual(visual)

        ocr.crop_images_to_bbox(ocr_results, image_directory)
        del page_image  # free memory

    return {'no_images_pages': no_image_pages, "metadata": metadata}


def find_pdf_files(directory: str, prefix: str = None) -> list:
    """
    Finds PDF files that match a given prefix.

    Parameters
    ----------
    directory : str
        Path to the directory where the PDF files are located.
    prefix : str
        sequence of characters to be be matched to the file name.
        If no prefix is provided, all PDF files in the
        data directory will be returned.

    Returns
    -------
    list
        List of paths to PDF files. Resulting path is a combination of the
        directory path and the file name.
    """

    pdf_files = []
    for f in tqdm(os.listdir(directory), desc="Collecting PDF files",
                  unit="files"):
        if prefix:
            if f.startswith(prefix) and f.endswith(".pdf"):
                pdf_files.append(directory+f)
        else:
            if f.endswith(".pdf"):
                pdf_files.append(directory+f)

    print("Found PDF files: ", len(pdf_files))

    return pdf_files


def start_logging(name: str, log_file: str, entry_id: str) -> Logger:
    """Starts logging to a file.

    Parameters
    ----------
    name : str
        Name of the logger.
    log_file : str
        Path to the log file.
    entry_id : str
        Identifier of the entry being processed.

    Returns
    -------
        Logger

    """
    logger = logging.getLogger(name)
    # Set the logging level to INFO (or any other desired level)
    logger.setLevel(logging.INFO)
    # Create a file handler to save log messages to a file
    file_handler = logging.FileHandler(log_file)
    # Create a formatter to specify the log message format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -\
                                  %(message)s')
    file_handler.setFormatter(formatter)
    # Add the file handler to the logger
    logger.addHandler(file_handler)
    logger.info(f"Starting {name} pipeline for entry: " + entry_id)

    return logger


def manage_input_files(pdf_files: list, destination_dir: str,
                       mods_file: str = None) -> None:
    """copy MODS and PDF files to a directory.

    Parameters
    ----------
    pdf_files : list
        List of paths to PDF files.
    destination_dir : str
        Path to the directory where the files will be copied to.
    mods_file : str, optional
        Path to the MODS file. The default is None.

    Returns
    -------
    None.

    """

    if mods_file:
        mods_file_name = pathlib.Path().stem + ".xml"
        if not os.path.exists(os.path.join(destination_dir, mods_file_name)):
            shutil.copy2(mods_file, destination_dir)

    if len(pdf_files) > 0:
        for pdf in pdf_files:
            if not os.path.exists(os.path.join(destination_dir,
                                  os.path.basename(pdf))):
                shutil.copy2(pdf, destination_dir)

    return None


class Layout(Pipeline):
    """A pipeline for extracting metadata and visuals from PDF
      files using a layout analysis. Layout analysis recursively
      checks elements in the PDF file and sorts them into images,
      text, and other elements.
    """

    def run(self) -> dict:
        """Run the pipeline."""
        print("Running layout pipeline")

        start_time = time.time()
        # INPUT DIRECTORY
        DATA_DIR = self.data_directory
        # OUTPUT DIRECTORY
        # if run multiple times to the same output directory, the images will
        # be duplicated and metadata will be overwritten
        # This will become the root path for a Visual object
        OUTPUT_DIR = self.output_directory  # an absolute path is recommended
        # SET MODS FILE and extract metadata
        # initialize metdata object
        meta_entry = Metadata()
        if self.metadata_file and not self.ignore_id:
            MODS_FILE = self.metadata_file
            entry_id = pathlib.Path(MODS_FILE).stem.split("_")[0]
            # EXTRACT METADATA FROM MODS FILE
            meta_blob = extract_mods_metadata(MODS_FILE)
            # add metadata from MODS file
            meta_entry.set_metadata(meta_blob)
        elif self.metadata_file and self.ignore_id:
            MODS_FILE = self.metadata_file
            entry_id = '00000'  # a default entry id
            # EXTRACT METADATA FROM MODS FILE
            meta_blob = extract_mods_metadata(MODS_FILE)
            # add metadata from MODS file
            meta_entry.set_metadata(meta_blob)
        elif not self.metadata_file and self.ignore_id:
            MODS_FILE = None  # no MODS file is provided
            #  therefore no metadata is added
            entry_id = '00000'  # a default entry id
            # no MODS file is provided

        if self.ignore_id:
            search_prefix = None
        else:
            search_prefix = pathlib.Path(MODS_FILE).stem.split("_")[0]

        if self.settings is None:
            raise ValueError("No settings provided")

        # Create output directory for the entry
        entry_directory = create_output_dir(OUTPUT_DIR, entry_id)

        # start logging
        logger = start_logging('layout',
                               os.path.join(entry_directory,
                                            entry_id + '.log'),
                               entry_id)


        # set web url. This is not part of the MODS file
        base_url = "http://resolver.tudelft.nl/"
        meta_entry.add_web_url(base_url)

        # FIND PDF FILES in data directory
        PDF_FILES = find_pdf_files(DATA_DIR, prefix=search_prefix)
        logger.info("PDF files in entry: " + str(len(PDF_FILES)))

        # PROCESS PDF FILES
        pdf_document_counter = 1
        results = {}
        for pdf in PDF_FILES:

            print("--> Processing file:", pdf)
            pdf_file_dir = 'pdf-' + str(pdf_document_counter).zfill(3)

            results = extract_visuals_by_layout(pdf, meta_entry, DATA_DIR,
                                                OUTPUT_DIR, pdf_file_dir,
                                                self.settings, logger,
                                                entry_id,
                                                )

            pdf_document_counter += 1

        end_time = time.time()
        processing_time = end_time - start_time
        logger.info("Processing time: " + str(processing_time) + " seconds")
        logger.info("Extracted visuals: " + str(meta_entry.total_visuals))

        # SAVE METADATA TO files
        csv_file = str(os.path.join(entry_directory, entry_id)
                       + "-metadata.csv")
        json_file = str(os.path.join(entry_directory, entry_id)
                        + "-metadata.json")
        meta_entry.save_to_csv(csv_file)
        meta_entry.save_to_json(json_file)

        if not meta_entry.uuid:
            logger.warning("No identifier found in MODS file")

        # SAVE settings to json file
        settings_file = str(os.path.join(entry_directory, entry_id)
                            + "-settings.json")
        with open(settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

        # TEMPORARY DIRECTORY
        # this directory is used to store temporary files.
        if self.temp_directory:

            TMP_DIR = self.temp_directory
            temp_entry_directory = create_output_dir(
                os.path.join(TMP_DIR, entry_id)
            )
            logger.info("Managing file and copying to: " + str(temp_entry_directory))
            manage_input_files(PDF_FILES, temp_entry_directory, MODS_FILE)
            logger.info("Done managing files")

        logger.info("Done")
        return results


class OCR(Pipeline):
    """A pipeline for extracting metadata and visuals from PDF
        files using OCR analysis. OCR analysis extracts images
        from PDF files using Tesseract OCR.
        """

    def run(self):
        """Run the pipeline."""
        print("Running OCR pipeline")

        start_time = time.time()
        # INPUT DIRECTORY
        DATA_DIR = self.data_directory
        # OUTPUT DIRECTORY
        # if run multiple times to the same output directory, the images will
        # be duplicated and metadata will be overwritten
        # This will become the root path for a Visual object
        OUTPUT_DIR = self.output_directory  # an absolute path is recommended
        # SET MODS FILE
                # SET MODS FILE and extract metadata
        # initialize metdata object
        meta_entry = Metadata()
        if self.metadata_file and not self.ignore_id:
            MODS_FILE = self.metadata_file
            entry_id = pathlib.Path(MODS_FILE).stem.split("_")[0]
            # EXTRACT METADATA FROM MODS FILE
            meta_blob = extract_mods_metadata(MODS_FILE)
            # add metadata from MODS file
            meta_entry.set_metadata(meta_blob)
        elif self.metadata_file and self.ignore_id:
            MODS_FILE = self.metadata_file
            entry_id = '00000'  # a default entry id
            # EXTRACT METADATA FROM MODS FILE
            meta_blob = extract_mods_metadata(MODS_FILE)
            # add metadata from MODS file
            meta_entry.set_metadata(meta_blob)
        elif not self.metadata_file and self.ignore_id:
            MODS_FILE = None  # no MODS file is provided
            #  therefore no metadata is added
            entry_id = '00000'  # a default entry id
            # no MODS file is provided

        if self.ignore_id:
            search_prefix = None
        else:
            search_prefix = pathlib.Path(MODS_FILE).stem.split("_")[0]

        if self.settings is None:
            raise ValueError("No settings provided")

        # Create output directory for the entry
        entry_directory = create_output_dir(OUTPUT_DIR, entry_id)

        # start logging
        logger = start_logging('OCR',
                               os.path.join(entry_directory,
                                            entry_id + '.log'),
                               entry_id)


        # set web url. This is not part of the MODS file
        base_url = "http://resolver.tudelft.nl/"
        meta_entry.add_web_url(base_url)
        # FIND PDF FILES in data directory
        PDF_FILES = find_pdf_files(DATA_DIR, prefix=search_prefix)
        logger.info("PDF files in entry: " + str(len(PDF_FILES)))

        # PROCESS PDF FILES
        pdf_document_counter = 1
        results = {}
        for pdf in PDF_FILES:

            print("--> Processing file:", pdf)
            pdf_file_dir = 'pdf-' + str(pdf_document_counter).zfill(3)

            results = extract_visuals_by_ocr(meta_entry, DATA_DIR,
                                             OUTPUT_DIR, pdf_file_dir,
                                             logger,
                                             entry_id, self.settings,
                                             pdf=pdf
                                             )

            pdf_document_counter += 1

        end_time = time.time()
        processing_time = end_time - start_time
        logger.info("Processing time: " + str(processing_time) + " seconds")
        logger.info("Extracted visuals: " + str(meta_entry.total_visuals))

        # SAVE METADATA TO files
        csv_file = str(os.path.join(entry_directory, entry_id)
                       + "-metadata.csv")
        json_file = str(os.path.join(entry_directory, entry_id)
                        + "-metadata.json")
        meta_entry.save_to_csv(csv_file)
        meta_entry.save_to_json(json_file)

        if not meta_entry.uuid:
            logger.warning("No identifier found in MODS file")

        # SAVE settings to json file
        settings_file = str(os.path.join(entry_directory, entry_id)
                            + "-settings.json")
        with open(settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

        # TEMPORARY DIRECTORY
        # this directory is used to store temporary files.
        if self.temp_directory:

            TMP_DIR = self.temp_directory
            temp_entry_directory = create_output_dir(
                os.path.join(TMP_DIR, entry_id)
            )
            logger.info("Managing file and copying to: " + str(temp_entry_directory))
            manage_input_files(PDF_FILES, temp_entry_directory, MODS_FILE)
            logger.info("Done managing files")
        
        logger.info("Done")
        return results


class LayoutOCR(Pipeline):
    """A pipeline for extracting metadata and visuals from PDF
        files that combines layout and OCR analysis. Layout analysis
        recursively checks elements in the PDF file and sorts them into images,
        text, and other elements. OCR analysis extracts images using
        Tesseract OCR.

        It applyes image search and analysis in two steps:
        First, it analyses the layout of the PDF file using the pdfminer.six
        library.
        Second, it applies OCR to the pages where no images were found by
        layout analysis.
        """

    def run(self):
        """Run the pipeline."""
        print("Running layout+OCR pipeline")

        start_time = time.time()
        # INPUT DIRECTORY
        DATA_DIR = self.data_directory
        # OUTPUT DIRECTORY
        # if run multiple times to the same output directory, the images will
        # be duplicated and metadata will be overwritten
        # This will become the root path for a Visual object
        OUTPUT_DIR = self.output_directory  # an absolute path is recommended
        # SET MODS FILE and extract metadata
        # initialize metdata object
        meta_entry = Metadata()
        if self.metadata_file and not self.ignore_id:
            MODS_FILE = self.metadata_file
            entry_id = pathlib.Path(MODS_FILE).stem.split("_")[0]
            # EXTRACT METADATA FROM MODS FILE
            meta_blob = extract_mods_metadata(MODS_FILE)
            # add metadata from MODS file
            meta_entry.set_metadata(meta_blob)
        elif self.metadata_file and self.ignore_id:
            MODS_FILE = self.metadata_file
            entry_id = '00000'  # a default entry id
            # EXTRACT METADATA FROM MODS FILE
            meta_blob = extract_mods_metadata(MODS_FILE)
            # add metadata from MODS file
            meta_entry.set_metadata(meta_blob)
        elif not self.metadata_file and self.ignore_id:
            MODS_FILE = None  # no MODS file is provided
            #  therefore no metadata is added
            entry_id = '00000'  # a default entry id
            # no MODS file is provided

        if self.ignore_id:
            search_prefix = None
        else:
            search_prefix = pathlib.Path(MODS_FILE).stem.split("_")[0]

        if self.settings is None:
            raise ValueError("No settings provided")

        # Create output directory for the entry
        entry_directory = create_output_dir(OUTPUT_DIR, entry_id)

        # start logging
        logger = start_logging('layout+OCR',
                               os.path.join(entry_directory,
                                            entry_id + '.log'),
                               entry_id)


        # set web url. This is not part of the MODS file
        base_url = "http://resolver.tudelft.nl/"
        meta_entry.add_web_url(base_url)

        # FIND PDF FILES in data directory
        PDF_FILES = find_pdf_files(DATA_DIR, prefix=search_prefix)
        logger.info("PDF files in entry: " + str(len(PDF_FILES)))

        # PROCESS PDF FILES
        pdf_document_counter = 1
        results = {}
        for pdf in PDF_FILES:

            print("--> Processing file:", pdf)
            pdf_file_dir = 'pdf-' + str(pdf_document_counter).zfill(3)

            # Step 1: Layout analysis
            layout_results = extract_visuals_by_layout(
                pdf, meta_entry, DATA_DIR, OUTPUT_DIR, pdf_file_dir,
                self.settings, logger, entry_id)
            
            # Step 2: OCR analysis on pages where no images were found
            # by step 1.
            results = extract_visuals_by_ocr(
                meta_entry, DATA_DIR, OUTPUT_DIR, pdf_file_dir,
                logger, entry_id, self.settings,
                lt_pages=layout_results["no_images_pages"])

            pdf_document_counter += 1

        end_time = time.time()
        processing_time = end_time - start_time
        logger.info("Processing time: " + str(processing_time) + " seconds")
        logger.info("Extracted visuals: " + str(meta_entry.total_visuals))

        # SAVE METADATA TO files
        csv_file = str(os.path.join(entry_directory, entry_id)
                       + "-metadata.csv")
        json_file = str(os.path.join(entry_directory, entry_id)
                        + "-metadata.json")
        meta_entry.save_to_csv(csv_file)
        meta_entry.save_to_json(json_file)

        if not meta_entry.uuid:
            logger.warning("No identifier found in MODS file")

        # SAVE settings to json file
        settings_file = str(os.path.join(entry_directory, entry_id)
                            + "-settings.json")
        with open(settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

        # TEMPORARY DIRECTORY
        # this directory is used to store temporary files.
        if self.temp_directory:

            TMP_DIR = self.temp_directory
            temp_entry_directory = create_output_dir(
                os.path.join(TMP_DIR, entry_id)
            )
            logger.info("Managing file and copying to: " + str(temp_entry_directory))
            manage_input_files(PDF_FILES, temp_entry_directory, MODS_FILE)
            logger.info("Done managing files")

        logger.info("Done")
        return results


if __name__ == "__main__":

    data_dir = './tests/data/00001/'  # this most end with a slash
    output_dir = './tests/data/layout/'
    tmp_dir = './tests/data/tmp/'
    # metadata_file = './tests/data/00001/00001_mods.xml'
    metadata_file = './tests/data/00001/00001_mods.xml'

    layout_settings = {"layout": {
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
    }

    ocr_settings = {"ocr": {
        "caption": {
            "offset": [50, "px"],
            "direction": "down",
            "keywords": ['figure', 'caption', 'figuur']
            },
        "image": {
            "width": 120,
            "height": 120,
        },
        "resolution": 250,  # dpi, default for ocr analysis,
        "resize": 30000,  # px, if image is larger than this, it will be
        # resized before performing OCR,
        # this affect the quality of output images
        "tesseract": "--psm 3 --oem 1"  # tesseract config flags
    }
    }

    settings = layout_settings | ocr_settings


    # p = Layout(data_directory=data_dir, output_directory=output_dir, metadata_file=metadata_file, settings=layout_settings, temp_directory=tmp_dir)

    p = OCR(data_directory=data_dir, output_directory=output_dir, metadata_file=metadata_file, settings=ocr_settings)

    r  = p.run()  # run pipeline


