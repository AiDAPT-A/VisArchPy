CLI Reference
======================


``visarch``
----------------------
VisArchPy: Data pipelines for extraction, transformation and visualization of architectural visuals in Python.

**Syntax**


.. code-block:: shell

    visarch [OPTIONS] COMMAND [ARGS]...

**Options**

      **-h, --help**  Show this message and exit.

**Commands**

      * **dino**       Transforms images into visual features using DinoV2.
      * **layout**     Extract images from PDF files using layout analysis.
      * **layoutocr**  Extract images from PDF files using layout and OCR analysis.
      * **ocr**        Extract images from PDF files using OCR analysis.
      * **viz**        Utility for visualizing architectural visuals.


Extraction Pipelines 
--------------------------------


``layout``
''''''''''''

Extract images from PDF files using layout analysis.

**Syntax**


.. code-block:: shell

   visarch layout [OPTIONS] COMMAND [ARGS]...

**Options**

  **-h, --help**  Show this message and exit.

**Commands**

  * **from-dir**   Extract images from all PDF files in a directory.
  * **from-file**  Extract images from a single PDF file.
  * **settings**   Show default settings for the pipeline.



``ocr``
''''''''''''

Extract images from PDF files using OCR analysis.

**Syntax**

.. code-block:: shell

      visarch ocr [OPTIONS] COMMAND [ARGS]...
      
**Options**

  **-h, --help**  Show this message and exit.

**Commands**

  * **from-dir**   Extract images from all PDF files in a directory.
  * **from-file**  Extract images from a single PDF file.
  * **settings**   Show default settings for the pipeline.


``layoutocr``
'''''''''''''''''

Extract images from PDF files using layout and OCR analysis.

**Syntax**

.. code-block:: shell

      visarch layoutocr [OPTIONS] COMMAND [ARGS]...
  
**Options**

  **-h, --help**  Show this message and exit.

**Commands**

  * **batch**      Batch processing for TU Delft's dataset.
  * **from-dir**   Extract images from all PDF files in a directory.
  * **from-file**  Extract images from a single PDF file.
  * **settings**   Show default settings for the pipeline.


Transformation Utilities
--------------------------------

``dino``
''''''''''''

Transforms images into visual features using DinoV2.

**Syntax**

.. code-block:: shell

      visarch dino [OPTIONS] COMMAND [ARGS]...
      
**Options**

  **-h, --help**  Show this message and exit.

**Commands**

  * **from-dir**   Extract features from all image files in a directory.
  * **from-file**  Extract features from a sigle image file.


Visualisation Utilities
--------------------------------

``viz``
''''''''''''

Utility for visualizing architectural visuals.

**Syntax**

.. code-block:: shell

      visarch viz [OPTIONS] COMMAND [ARGS]...
  
**Options**

  **-h, --help**  Show this message and exit.

**Commands**

  * **bbox-plot**  Creates a bounding box plot for images in a directory.

