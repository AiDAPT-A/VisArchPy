Transformation Utilities
==============================

Data transformation utilities help with extracting visual features from images. The current utilities extract visual features using the DinoV2 model and store the results as CSV and pickle files.
*VisArchPy* provides one transformation utility: dino.


Dino 
---------------
Utility functions to extract visual features using `DINOv2 <https://github.com/facebookresearch/dinov2>`_ model and the **huggingface** `transformers <https://huggingface.co/transformers/>`_ 
package.


Examples
""""""""""""""""

The following examples show how to extract visual features of images using the **facebook/dinov2-small** model.

.. tabs::

    .. tab:: Single Image

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

                # save features as Pandas data frame to CSV file
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

                """ results will be saved in a subdirectory named after the image directory
                with the output directory as parent directory
                """
                
                image_dir = './my-images/'
                model = 'facebook/dinov2-small'  
                output_dir = './dinov2'  # directory to save outputs

                output_dir = os.path.join(output_dir, os.path.basename(image_dir.rstrip('/')))
                os.makedirs(output_dir, exist_ok=True)
                files = os.listdir(input_dir)

                for file in tqdm(files, desc="Extracting features", unit="images"):
                    # fetch name of image file
                    filename = os.path.basename(file).split('.')[0]

                    # extract visual features
                    try:
                        results = transform_to_dinov2(os.path.join(image_dir, file), model)
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


Outputs
----------------

The ``dino`` transformation tools transform images in a directory into tensors and  Python objects. The results are organized as follows.


.. code-block:: shell

   dinov2  # default output directory
    └── pdf-001  # directory named after the input directory
        ├── 00001-page1-Im0.csv  # Pytorch tensor as Pandas dataframe
        ├── 00001-page1-Im0.pickle  # Huggingface object with full model outputs
        ├── 00001-page1-Im1.csv
        ├── 00001-page1-Im1.pickle
        ├── 00001-page1-Im2.csv
        └── 00001-page1-Im2.pickle

.. important::
    
    * The ``dino`` transformation tools will overwrite existing files in the output directory. 
    * The *tensor* in the CSV files is a Pytorch tensor converted to a Pandas data frame. The *object* in the pickle files is a Huggingface object with the full model outputs. See the `Huggingface documentation <https://huggingface.co/transformers/main_classes/output.html>`_ for more information.

