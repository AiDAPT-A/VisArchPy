Data Extraction
=======================

This section briefly explains the motivation, tools and approaches used while developing the data extraction pipelines in *VisArchPy*. 

Data extraction aimed to extract architectural visuals (images) from PDF documents in a document repository of `TU Delft<https://www.tudelft.nl>`, including images' captions, while maintaining references to where a visual is located (page). Architectural visuals of interest were divided into two categories: image- and vector-based. Image-based visuals include photos, 3D renders and collages. Vector-based visuals include floorplans and maps embedded in the PDF in a scalable format. To achieve this, we explored several tools and approaches.

Tools 
-----

PyMuPDF and PyPDF2
"""""""""""""""""""

PyMuPDF and PyPDF2 were relatively successful in extracting image-based visuals. Out of the two, PyPDF2 was more successful in extracting image-based visuals. However, neither tool was able to extract captions and references to where a visual is located in the document. None of the tools could extract vector-based visuals in a usable format (e.g. SVG).
PyMuPDF is a Python binding for MuPDF, a lightweight PDF, XPS, and E-book viewer. PyPDF2 is a pure-python PDF library capable of splitting, merging, cropping, and transforming the pages of PDF files.

PDFMiner.six
"""""""""""""""""""
PDFMiner.six is a Python tool for extracting information from PDF documents. This tool offered the advantage of extracting all the elements of a PDF document as defined by the PDF standard. This meant that we could search for the elements of interest (e.g. images, figures, textbox, etc.) and extract them. 
However, it is not able to extract vector-based visuals directly. 


Tesseract
"""""""""""""""""""

Tesseract is an open-source OCR (Optical Character Recognition) engine. It is able to extract text from images. Although this tool was built to extract text from images, it can also extract visuals by discriminating between text and non-text elements. 

Approaches 
----------
We explored two approaches to extract visuals from PDF documents. The first approach focused on using PDFMiner.six to analyse all the elements of a PDF document as defined by the PDF standard and then search for the elements of interest (e.g. images, figures, textbox, etc.).
The second approach focused on using Tesseract to apply OCR to pages of PDF documents, locate regions considered as non-text, and assume that these regions are the visuals of interest. An analytical pipeline was developed for each approach. 


Approach 1: PDFMiner.six
"""""""""""""""""""""""""

The pipeline for this approach is as follows:

1. Extract the original metadata from MDOS file.
2. Search and collect image and text elements on each PDF document page.
3. Extract image elements and save them to a directory.
4. Search for text elements in the vicinity of extracted images, and that may contain keywords such as `Figure` indicating that the text element is a caption for the image.
5. Save original metadata and extracted metadata to a JSON file. Extracted metadata includes the location of the image in the PDF document, the location where the image was saved, and the caption of the image, among others.

Results
''''''''

.. note:: 
    See reports in the project channel. 

Artifacts
'''''''''

.. warning:: 
    - We cannot save CMYK images using PDFMiner.six. The tools don't have a method to handle CMYK images. But it can be implemented with some effort.
    - The accuracy of this approach is highly dependent on how the PDF document was created. For example, suppose the PDF document was created by first converting the pages of Word document into images, and then converting the images into a PDF document. In that case, the text elements will not be extracted.
    - This approach ignores many vector-based visuals because scalable visuals are embedded in a PDF as a text of binary streams, and we haven't found a way of discriminating between text elements that are scalable visuals and text elements that are not.

Approach 2: OCR with Tesseract
""""""""""""""""""""""""""""""""

1. Extract the original metadata from MDOS file.
2. Convert pages of PDF documents to images.
3. Apply OCR to images from step 2. Settings: `tesseract --psm 1 --oem 1`
4. Search and collect bounding boxes of non-text elements on each image from step 2.
5. Crop images from step 2 using bounding boxes from step 4, and save them to a directory.
6. Save the original metadata and extracted metadata to a JSON file (**not implemented**). 

Results
''''''''

.. note:: See reports in the project channel, and `this issue <https://github.com/AiDAPT-A/OpenDesign-Handbook/issues/30>`_.

Artifacts
'''''''''

.. warning:: 
    - the accuracy of this approach is highly dependent on the resolution of the images on each page. However, higher resolutions can positively or negatively affect the accuracy of identifying images.
    - This approach is more successful in identifying vector-based visuals but not in their original scalable format. The output is a raster image of the visual.
    - In many cases, this approach cannot identify the full extent of a vector visual. It is identified as multiple parts (bounding boxes) or not identified at all.

 
