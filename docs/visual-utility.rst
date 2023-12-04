Visualisation Utilities
==============================

Data visualisation utilities help with the visual exploration of image datasets. The current utilities **viz** provide tools for visualising propertied for an image dataset. 

Viz
---------------
*VisArchPy* offers one visualization utility to create a *bounding box plot*, **bbox-plot** for short. This plot provides an overview of the shapes and sizes of images in a data set. 



Examples
""""""""""""""""

The following examples show how to create a *bbox plot* using a collection of images stored in a directory.



       .. tabs::

          .. code-tab:: bash  CLI

             visarch viz bbox-plot <path-image-directory>

          .. code-tab:: py

                from visarchpy.dino.transformer import get_image_paths, plot_bboxes

                img_dir='/home/manuel/Documents/devel/data/plot'
                img_plot = get_image_paths(img_dir)  # finds images in the directory

                plot_bboxes(img_plot, cmap='gist_heat_r')  # creates and shows plot

.. tip::
    Use ``visarch viz [SUBCOMMAND] -h`` to see which options are available in the CLI. Or consult the :ref:`python api` if using Python.


Outputs
----------------

The ``viz`` will show the plot on screen by default. However, it is possible to save the plot as a file. The plot supports any colour map supported by `Matplotlib. <https://matplotlib.org/stable/users/explain/colors/colormaps.html>`_


.. image:: img/all-plot-heat.png
      :alt: Example of a bounding box plot for an image dataset containing 1000 images
      :align: center
      :width: 100%
