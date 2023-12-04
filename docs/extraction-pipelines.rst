Data Extraction Pipelines
=========================

Data extraction pipelines are used to extract metadata and images from PDF files. These pipelines can be used to extract data from a single PDF file or a directory of PDF files, using the CLI and the ``visarch`` command or as a Python package. 
*VisArchPy* provides three different extraction pipelines: Layout, OCR, and LayoutOCR.  


Layout Pipeline
---------------
Extracts metadata and visuals (images) from PDF files using a layout analysis. Layout analysis uses the algorithm in `pdfminer.six <https://pdfminersix.readthedocs.io/en/latest/topic/converting_pdf_to_text.html#layout-analysis-algorithm>`_  to recursively check elements in a PDF file and sort them into images, text, etc.


Examples
""""""""""""""""

The following examples show how to extract images and metadata from PDF files using the **Layout** pipeline. 


.. tabs::

    .. tab:: Sigle PDF

       .. tabs::

          .. code-tab:: bash  CLI

            visarch layout from-file <path-to-pdf-file> <path-output-directory>

       .. tabs::

          .. code-tab:: py

            "Not available"

    .. tab:: Multiple PDFs

       .. tabs::

          .. code-tab:: bash  CLI

            visarch layout from-dir <path-pdf-directory> <path-output-directory>

       .. tabs::

          .. code-tab:: py

            from visarchpy.pipelines import Layout

            pipeline = Layout('path-to-data-dir', 'path-to-output-dir', 
                             metadata_file='path-to-mods-file', 
                             settings=None, # use default settings 
                             )

            pipeline.run()


.. tip::
    Use ``visarch layout [SUBCOMMAND] -h`` to see which options are available in the CLI. Or consult the :ref:`python api` if using Python.


OCR Pipeline
------------
Extracts metadata and visuals (images) from PDF files using OCR analysis. OCR analysis extracts images from PDF files using `Tesseract OCR <https://tesseract-ocr.github.io/>`_.


Examples
""""""""""""""""

The following examples show how to extract images and metadata from PDF files using the **OCR** pipeline. 

.. tabs::

    .. tab:: Sigle PDF

       .. tabs::

          .. code-tab:: bash CLI

            visarch ocr from-file <path-to-pdf-file> <path-output-directory>

       .. tabs::

          .. code-tab:: py

            "Not available"

    .. tab:: Multiple PDFs

       .. tabs::

          .. code-tab:: bash  CLI

            visarch ocr from-dir <path-pdf-directory> <path-output-directory>

       .. tabs::

          .. code-tab:: py

            from visarchpy.pipelines import OCR

            pipeline = OCR('path-to-data-dir', 'path-to-output-dir', 
                          metadata_file='path-to-mods-file', 
                          settings=None, # use default settings 
                          )

            pipeline.run()


.. tip::
    Use ``visarch ocr [SUBCOMMAND] -h`` to see which options are available in the CLI. Or consult the :ref:`python api` if using Python.


LayoutOCR Pipeline
------------------

Extracts metadata and visuals (images) from PDF files using a combination of Layout and OCR analysis. This pipeline first uses the layout analysis to extract images from PDF files. Then, it applies OCR analysis pages in the PDF file that did not produce any images using the first analysis. This condition avoids extracting the same images twice; however, it may miss images not detected by any of the analyses.

Examples
""""""""""""""""

The following examples show how to extract images and metadata from PDF files using the **LayoutOCR** pipeline. 

.. tabs::

    .. tab:: Sigle PDF

       .. tabs::

          .. code-tab:: bash CLI

            visarch layoutocr from-file <path-to-pdf-file> <path-output-directory>

       .. tabs::

          .. code-tab:: py

            "Not available"

    .. tab:: Multiple PDFs

       .. tabs::

          .. code-tab:: bash  CLI

            visarch layoutocr from-dir <path-pdf-directory> <path-output-directory>

       .. tabs::

          .. code-tab:: py

            from visarchpy.pipelines import LayoutOCR

            pipeline = LayoutOCR('path-to-data-dir', 'path-to-output-dir', 
                                metadata_file='path-to-mods-file', 
                                settings=None, # use default settings 
                                )

            pipeline.run()


.. tip::
    Use ``visarch ocr [SUBCOMMAND] -h`` to see which options are available in the CLI. Or consult the :ref:`python api` if using Python.


Pipeline Outputs
----------------

All extraction pipelines result in the following outputs. Outputs are saved to the ``<output directory>``.

.. code-block:: shell

   <output-directory>
    └──00000/  # result directory
       ├── pdf-001  # PDF directory, one per PDF. Extracted images are saved here.
       ├── 00000-metadata.csv  # extracted metadata as CSV
       ├── 00000-metadata.json  # extracted metadata as JSON
       ├── 00000-settings.json  # a copy of settings used by the pipeline
       └── 00000.log  # processing log file

.. warning::
    Be mindful when running the pipeline multiple times on the same ``<output-directory``.
    The ``00000`` directory is created if it does not exist. However, if it exists, the pipeline will overwrite/update its contents. 

       * **pdf-001:**  existing images are kept, new images are added.
       * **00000-metadata.csv:**  existing metadata will be overwritten.
       * **00000-metadata.json:**  existing metadata will be overwritten.
       * **00000-settings.json:**  existing settings will be overwritten.
       * **00000.log:** existing records are kept, new records are added.


Settings
---------

The pipeline settings determine how image extraction is performed. By default, the pipelines use the settings in ``visarchpy/default-settings.json``. However, these settings can be overwritten by passing custom settings to the pipeline.

Default settings can be shown on the terminal by using the following command:

.. code-block:: shell
   
    visarch [PIPELINE] settings


Default Setting
""""""""""""""""

Extraction pipelines use the following default settings:

.. code-block:: json
    
    {
        "layout": { 
            "caption": { 
                "offset": [ 
                    4,
                    "mm"
                ],
                "direction": "down", 
                "keywords": [  
                    "figure",
                    "caption",
                    "figuur"
                ]
            },
            "image": { 
                "width": 120,
                "height": 120
            }
        },
        "ocr": {  
            "caption": {
                "offset": [
                    50,
                    "px"
                ],
                "direction": "down",
                "keywords": [
                    "figure",
                    "caption",
                    "figuur"
                ]
            },
            "image": {
                "width": 120,
                "height": 120
            },
            "resolution": 250,
            "resize": 30000,
            "tesseract" : "--psm 1 --oem 3"
        }
    }


.. table:: Settings for the data extraction pipelines in VisArchPy.
        
    ======================= ===================================== =================================
     Setting                Meaning                               Expected values
    ======================= ===================================== =================================
    *layout*                Group settings for Layout analysis
    *ocr*                   Group settings for OCR analysis
    *caption.offset*        | Distance around an image boundary   | ``[ number, "mm" ]`` (for layout)
                            | where captions will be searched     | ``[ number, "px" ]`` (for OCR) 
                            | for                                                    
    *caption.direction*     | Direction relative to an image 
                            | where captions are searched for     | ``all, up, down,``
                            |                                     | ``right, left ```
                            |                                     | ``down-right, up-left,``      
    *caption.keywords*      | Keywords used to find captions      | ``[keyword1, keyword2, ...]``
                            | based on text analysis                          
    *image.width*           | minimum width of an image to be     ``integer`` 
                            | extracted, in pixels                              
    *image.height*          | minimum height of an image to be    ``integer`` 
                            | extracted, in pixels
    *ocr.resolution*        | DPI used to convert PDF pages       ``integer``
                            | into images before applying OCR
    *ocr.resize*            | Maximum width and height of PDF     ``integer``
                            | page used as input by Tesseract.    
                            | in pixels. If page conversion       
                            | results in a larger image, it will  
                            | be downsized to fit this value.     
                            | Tesseract maximum values  for       
                            | width and height is :math:`2^{15}`    
    *ocr.tesseract*         | Tesseract command line options      ``string``
                            | passed to Tesseract. See Tesseract  
                            | man page [1]_ for more 
                            | information.
    ======================= ===================================== =================================

.. [1] `Tesseract options <https://github.com/tesseract-ocr/tesseract/blob/main/doc/tesseract.1.asc>`_

Custom Settings
""""""""""""""""""

When defining custom settings, the schema defined above should be used. Note that settings for different extraction approaches are grouped together. When using a pipeline that implements only one approach, settings for the other can be omitted. Custom settings can be passed to a pipeline as a JSON file (CLI) or a dictionary (Python).

.. tabs::

    .. code-tab:: bash  CLI

        visarch layoutocr from-file --settings <settings-file> <path-pdf-directory> \
        <path-output-directory>

    .. code-tab:: py

        from visarchpy.pipelines import LayoutOCR

        custom_settings = {}  # a dictionary with custom settings following schema above

        pipeline = LayoutOCR('path-to-data-dir', 'path-to-output-dir', 
                            metadata_file='path-to-mods-file', 
                            settings=custom_settings
                            )

        pipeline.run()

