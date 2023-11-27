Quick Start  
=============

Start here if you are new to VisArchPy.

Installation
-------------

VisArchPy requires the following dependencies:

Dependencies
""""""""""""""""""

* Python 3.10 or newer 
* `Tesseract v4.0 or recent <https://tesseract-ocr.github.io/>`_
* `PyTorch v2.1 or recent <https://pytorch.org/get-started/locally/>`_


Installing from PyPI
""""""""""""""""""""""""

After installing the dependencies, install VisArchPy using ``pip``.

.. code-block:: bash

   pip install visarchpy


Installing from source
""""""""""""""""""""""""

1. Install the dependencies.

2. Clone the repository.
    
   .. code-block:: shell
    
      git clone https://github.com/AiDAPT-A/VisArchPy.git
    
3. Go to the root of the repository.
   
   .. code-block:: shell
   
      cd VisArchPy/
   
4. Install the package using `pip`.

   .. code-block:: shell 
    
      pip install .

Usage
------

The quickest way to get started with VisArchPy is to use the command line interface (CLI). Once installed you can access the CLI by typing ``visarch`` in the terminal. 

.. code-block:: shell

   visarch -h

To access a particular pipeline or tool:

.. code-block:: shell

   visarch [PIPELINE] -h


* run the ``layout`` pipeline on a PDF file, do the following:

.. code-block:: shell

   visarch layout from-file <path-to-pdf-file> <path-output-directory>

* run the ``layout`` pipeline on directory containing PDF files, do the following:

.. code-block:: shell

   visarch layout from-dir <path-to-pdf-directory> <path-output-directory>

.. tip::

   Use ``visarch [PIPELINE] [SUBCOMMAND] -h`` for help.

[CONTINUE HERE]

.. ### Results:

.. Results from the data extraction pipelines (Layout, OCR, LayoutOCR) are save to the output directory. Results are organized as following:

.. ```shell
.. 00000/  # results directory
.. ├── pdf-001  # directory where images are saved to. One per PDF file
.. ├── 00000-metadata.csv  # extracted metadata as CSV
.. ├── 00000-metadata.json  # extracted metadata as JSON
.. ├── 00000-settings.json  # settings used by pipeline
.. └── 00000.log  # log file
.. ```

.. ## Settings

.. The pipeline's settings determine how visual extraction from PDF files is performed. Settings must be passed as a JSON file on the CLI. Settings may must include all items listed below. The values showed belowed are the defaults.

.. ```python
.. {
..     "layout": { # setting for layout analysis
..         "caption": { 
..             "offset": [ # distance used to locate captions
..                 4,
..                 "mm"
..             ],
..             "direction": "down", # direction used to locate captions
..             "keywords": [  # keywords used to find captions based on text analysis
..                 "figure",
..                 "caption",
..                 "figuur"
..             ]
..         },
..         "image": { # images smaller than these dimensions will be ignored
..             "width": 120,
..             "height": 120
..         }
..     },
..     "ocr": {  # settings for OCR analysis
..         "caption": {
..             "offset": [
..                 50,
..                 "px"
..             ],
..             "direction": "down",
..             "keywords": [
..                 "figure",
..                 "caption",
..                 "figuur"
..             ]
..         },
..         "image": {
..             "width": 120,
..             "height": 120
..         },
..         "resolution": 250, # dpi to convert PDF pages to images before OCR
..         "resize": 30000  # total pixels. Larger OCR inputs are downsize to this before OCR
..     }
.. }
.. ```

.. When no seetings are passed to a pipeline, the defaults are used. To print the default seetting to the terminal use:

.. ```shell
.. visarch [PIPELINE] settings
.. ```

