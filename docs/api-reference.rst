.. _python api:

Python Reference
==========================

The API reference for the most relevant features in the *visarchpy* package. For other features, please refer to the source code.



Extraction Pipelines
-------------------------

All data extraction pipelines inherit from the :class:`Pipeline` abstract class.

.. autoclass:: visarchpy.pipelines.Pipeline
   :members:
   :undoc-members:

.. autoclass:: visarchpy.pipelines.Layout
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: visarchpy.pipelines.OCR
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: visarchpy.pipelines.LayoutOCR
   :members:
   :undoc-members:
   :show-inheritance:

Transformation Utilities
-----------------------------

.. automodule:: visarchpy.dino.transformer
   :members:

Visualization Utilities
-----------------------

Functions for analyzing and visualizing extracted data.

.. autofunction:: visarchpy.analytics.plot_bboxes





