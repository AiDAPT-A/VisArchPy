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

For example, to access the ``layout`` pipeline:

* To run the ``layout`` pipeline on a PDF file, do the following:

.. code-block:: shell

   visarch layout from-file <path-to-pdf-file> <path-output-directory>

* To run the ``layout`` pipeline on a directory containing PDF files, do the following:

.. code-block:: shell

   visarch layout from-dir <path-to-pdf-directory> <path-output-directory>

.. tip::

   Use ``visarch [PIPELINE] [SUBCOMMAND] -h`` for help.


Outputs
""""""""""""""""""""""""

Results from the data extraction pipelines (Layout, OCR, LayoutOCR) are save to the output directory and organized as follows:

.. code-block:: shell

   00000/  # results directory
   ├── pdf-001  # extracted image directory are saved to. One per PDF file
   ├── 00000-metadata.csv  # extracted metadata as CSV
   ├── 00000-metadata.json  # extracted metadata as JSON
   ├── 00000-settings.json  # settings used by pipeline
   └── 00000.log  # log file
