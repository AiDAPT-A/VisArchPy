Data Extraction
=======================

The aim of data extraciotn is to extract architectural visuals from PDF documents along with their captions while maintainig refereces to where (page) in the document a visual is located. Architectural visual of interest can be devide in two categories: image-based visuals and vector-based visuals. Image-based visuals include photos, 3D renders and collages. Vector-based visuals include floorplans and maps embedded in the PDF in an scalable format. To achive this we explored several tools and approaches.

Tools 
-----

PyMuPDF and PyPDF2
"""""""""""""""""""

PyMuPDF and PyPDF2 were relatively successful in extracting image-based visual. Out of the two, PyPDF2 was more successful in extracting image-based visuals. However, both tools were not able to extract captions and references to where in the document a visual is located. And none of the tools were able to extract vector-based visuals in an usable format (e.g. SVG).
PyMuPDF is a Python binding for MuPDF, a lightweight PDF, XPS, and E-book viewer. PyPDF2 is a pure-python PDF library capable of splitting, merging together, cropping, and transforming the pages of PDF files.

PDFMiner.six
"""""""""""""""""""
PDFMiner.six is a Python tool for extracting information from PDF documents. This tool offered the advantage of extracting all the elements of a PDF document as defined by the PDF standard. This meant that we could search for the elements of interest (e.g. images, figures, textbox, etc.) and extract them. 
However, it is not able to extract vector-based visuals directly. 


Tesseract
"""""""""""""""""""

Tesseract is an open-source OCR (Optical Character Recognition) engine. It is able to extract text from images. Although this tool was build to extract text from images, it also can be used to extract visual by discriminating between text and non-text elements. 

Approaches 
----------
We explored two approaches to extract visuals from PDF documents. The first approach focused in using PDFMiner.six to analyse all the elements of a PDF document as defined by the PDF standard and then search for the elements of interest (e.g. images, figures, textbox, etc.).
The second approach focused on using Tesseract to apply OCR to pages of PDF document, locate regions considered as non-text, and assum that these regions are the visuals of interest. An analytical pipeline was developed for each approach. 


Approach 1: PDFMiner.six
"""""""""""""""""""""""""

The pipeline for this approach is as follows:

1. Extract original metdata from MDOS file.
2. Search and collect image and text elements on each page of the PDF document.
3. Extract image elements and save them to a directory.
4. Search for text elements in the vecinity of extrated images and that may contain keywords such as `Figure` indicating that the text element is a caption for the image.
5. Save original metadata and extracted metadata to a JSON file. Extracted metdata includes the location of the image in the PDF document, the location where the image was saved, the caption of the image, among others.

Results
''''''''

.. note:: 
    See reports in project channel. 

Artifacts
'''''''''

.. warning:: 
    - We cannot save CMYK images using PDFMiner.six. The tools doesn't have a method to hangle CMYK images. But, it can be implemented with some effort.
    - The accuracity of this approach is highly dependent on how the PDF document was created. For example, if the PDF document was created by firts converting a Word document into images, and then converting the images into a PDF document, then the text elements will not be extracted.
    - Many vector-based visuals are ignored by this approach because scalable visual are embeded in a PDF as text of binary streams and we haven't find a way of discriminating between text element that are scalable visuals and text elements that are not.

Approach 2: OCR with Tesseract
""""""""""""""""""""""""""""""""

1. Extract original metdata from MDOS file (**not implemented**)
2. Convert pages of PDF document to images.
3. Apply OCR to images from step 2. Settings: `tesseract --psm 1 --oem 1`
4. Search and collect bouding boxes of non-text elements on each image from step 2.
5. Crop images from step 2 using bounding boxes from step 4, and save them to a directory.
6. Save original metadata and extracted metadata to a JSON file (**not implemented**). 

Results
''''''''

.. note:: See reports in project channel, and `this issue <https://github.com/AiDAPT-A/OpenDesign-Handbook/issues/30>`_.

Artifacts
'''''''''

.. warning:: 
    - the accuracy of this approach is highly dependent on the resolution of the images of each page. However, higher resolutions can affect the accuracy of identifying images positively or negatively.
    - This approach is more successful in identifying vector-based visuals but not as their original scalable format. The output is a raster image of the visual.
    - In many cases this approach is not able to identify the full extent of a vector visual. Either it is idetified as multiple parts (bounding boxes) or it is not identified at all.

 