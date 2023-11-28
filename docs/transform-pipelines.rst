Transformation Pipelines
==============================

Data tranformation pipelines provide utilities to extract visual features from images. The current utilities extract visual features uing the DinoV2 model, and store the results as CSV files and pickle files.
*VisArchPy* provides one transformation pipeline: dino.


Dino 
---------------
Utility functions to extract visual features using `DINOv2 <https://github.com/facebookresearch/dinov2>`_ model and the **huggingface** `transformers <https://huggingface.co/transformers/>`_ 
package.


Examples
""""""""""""""""

The following examples show how to extract visual features of images using the **facebook/dinov2-small** model.

.. tabs::

    .. tab:: Sigle Image

       .. tabs::

          .. code-tab:: bash  CLI

             visarch dino from-file <path-image-file>

       .. tabs::

          .. code-tab:: py

                import os
                from visarchpy.dino.transformer import (transform_to_dinov2, 
                                                        save_csv_dinov2, 
                                                        save_pickle_dinov2) 

                image_file = './test-image.png'
                model = 'facebook/dinov2-small'  
                output_dir = './dinov2'  # directory to save outputs
                os.makedirs(output_dir, exist_ok=True)

                # fetch name of image file
                filename = os.path.basename(imgae_file).split('.')[0]

                # extract visual features
                results = transform_to_dinov2(iamge_file, model)

                # save features as pandas dataframe to CSV file
                save_csv_dinov2(os.path.join(output, filename + '.csv'), results['tensor'])
                
                # save model outputs to pickle file
                save_pickle_dinov2(os.path.join(output, filename + '.pickle'), results['object'])


    .. tab:: Multiple Images

       .. tabs::

          .. code-tab:: bash  CLI

             visarch dino from-file <path-image-directory>

       .. tabs::

          .. code-tab:: py

                import os
                from visarchpy.dino.transformer import (transform_to_dinov2, 
                                                        save_csv_dinov2, 
                                                        save_pickle_dinov2) 

                """ results will be saved in a subdirectory named after the input directory
                and with the output directory as parent directory
                """
                
                input_dir = './my-images/'
                model = 'facebook/dinov2-small'  
                output_dir = './dinov2'  # directory to save outputs

                output_dir = os.path.join(output_dir, os.path.basename(input_dir.rstrip('/')))
                os.makedirs(output_dir, exist_ok=True)
                files = os.listdir(input_dir)

                for file in tqdm(files, desc="Extracting features", unit="images"):
                    filename = os.path.basename(file).split('.')[0]

                    # extract visual features
                    try:
                        results = transform_to_dinov2(os.path.join(input_dir, file), model)
                    except IOError:  # prevents raising error when file is not an image
                        print(f"WARNING: Directory contain that's not an image: {file}. Skipping...")
                        continue
                        
                    else:
                        # save features as pandas dataframe to CSV file
                        save_csv_dinov2(os.path.join(output_dir, filename + '.csv'), 
                                       results['tensor'])
                    
                        # save to pickle file
                        save_pickle_dinov2(os.path.join(output_dir, filename + '.pickle'),
                                           results['object'])
                

.. tip::
    Use ``visarch dino [SUBCOMMAND] -h`` to see which options are available in the CLI. Or consult the :ref:`python api` if using Python.

Pipeline Outputs
----------------

All extraction pipeline result in the following outputs. Outputs are saved to the ``<output directory>``.

.. code-block:: shell

   <output-directory>
    └──00000/  # result directory
       ├── pdf-001  # PDF directory, one per PDF. Extracted images are saved here.
       ├── 00000-metadata.csv  # extracted metadata as CSV
       ├── 00000-metadata.json  # extracted metadata as JSON
       ├── 00000-settings.json  # a copy of settings used by pipeline
       └── 00000.log  # processing log file

.. warning::
    Be mindful when running the pipeline multiple times on the same ``<output-directory``.
    The ``00000`` directory is created if it does not exist. However, if exists, the pipeline will overwrite/update its contents. 

       * **pdf-001:**  existing images are kept, new images are added.
       * **00000-metadata.csv:**  existing metadata will be overwritten.
       * **00000-metadata.json:**  existing metadata will be overwritten.
       * **00000-settings.json:**  existing settings will be overwritten.
       * **00000.log:** existing recodrs are kept, new records are added.


Settings
---------

The pipelines settings determine how image extraction is performed. By default, the pipelines use the settings in ``visarchpy/default-settings.json``. However, these settings can be overwritten by passing custom settings to the pipeline.

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
            "resize": 30000 
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
    *caption.direction*     | Derection relative to an image 
                            | where captions are searched for     | ``all, up, down,``
                            |                                     | ``right, left ```
    *caption.keywords*      | Keywords used to find captions      | ``[keyword1, keyword2, ...]``
                            | based on text analysis                          
    *image.width*           | minimum width of an image to be     ``integer`` 
                            | extracted, in pixels                              
    *image.height*          | minimum height of an image to be    ``integer`` 
                            | extracted, in pixels
    *ocr.resolution*        | DPI used to convert PDF pages       ``integer``
                            | into images befor applying OCR
    *ocr.resize*            | Maximum width and height of PDF     ``integer``
                            | page used as input by Tesseract.    
                            | in pixels. If page conversion       
                            | results in a larger image, it will  
                            | be downsized to fit this value.     
                            | Tesseract maximum values  for       
                            | width and height is :math:`2^{15}`    
    ======================= ===================================== =================================



Custom Settings
""""""""""""""""""

When defining custom setting, the schema defined above should be used. Note that settings for different extraction approaches are grouped together. When using a pipeline that implements only one approach, settigs for the other approach can be ommitted. Custom settings can be passed to a pipeline as a JSON file (CLI) or as a dictionary (Python).

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

