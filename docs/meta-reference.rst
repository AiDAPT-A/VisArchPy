Metadata Reference
======================

This section describes the metadata fields that are used in the `metadata.json` file. Most of the metadata fields are based on the `MODS <https://www.loc.gov/standards/mods/>`_ standard, however some fields are added to support TU Delft specific fields, and metadata of extracted images (visuals).



.. table:: Metadata fields in **metadata.json** file.
        
   ================================ ========================================= ==============================================================================
    Field                           Explanation                                Expected values
   ================================ ========================================= ==============================================================================
   *documents* [2]_                 | List of documment processed 
                                    | by the pipeline                                 
   *documents.location* [2]_        Location of the document                  | ``{ root_path: string,``
                                                                              | ``file_path: string }``
   *persons* [3]_                   | List of persons involved in 
                                    | documents                                 array of persons
   *persons.name*                   Name of the person                          string
   *persons.role*                   Role of the person                          string
   *faculty* [3]_                   List of faculties involved in documents     array of faculties
   *faculty.name*                   Name of the faculty                         string
   *faculty.departments*            List of departments in the faculty          ``[{ name: string }]``
   *mods_file* [2]_                 Path the MODS file                          string
   *title* [3]_                     Title of thesis                             string
   *abstract* [3]_                  Abstract of thesis                          array of strings
   *submission_date* [3]_           Submission date of thesis                   ``YYYY-MM-DD``
   *thesis_type* [3]_               Type of thesis                              array of strings
   *subjects* [3]_                  List of subjects                            array of strings
   *copyright* [3]_                 Copyrigth information                       array of strings
   *languages* [3]_                 List of languages                           array of `language identifiers <https://www.rfc-editor.org/info/rfc3066>`_
   *uuid* [1]_                      Repository unique identifier                string
   *iid* [3]_                       Repository identifier                       string
   *media_type* [3]_                Media type of resource                      array
   *issuance* [3]_                  Issuance of resource                        array
   *digital_origin* [3]_            Digital origin of resource                  string
   *doi*  [3]_                      Digital Object Identifier                   string
   *edition*  [3]_                  Edition of resource                         string
   *extent* [3]_                    Extent of resource                          array
   *form* [3]_                      Form of resource                            array
   *classification* [3]_            Classification of resource                  array
   *collection* [3]_                Catalog collection                          string
   *geo_code* [3]_                  Geographic code                             string
   *corp_names* [3]_                Corporate names                             array
   *creators* [3]_                  Creators of resource                        array
   *physical_description* [3]_      Physical description of resource            array
   *physical_location* [3]_         Physical location of resource               array
   *pid* [3]_                       Persistent identifier                       string
   *publication_place* [3]_         Publication place of resource               array
   *publisher* [3]_                 Publisher of resource                       array
   *purl* [3]_                      Persistent URL                              string
   *type_resource* [3]_             Type of resource                            string
   *web_url* [1]_                   Web URL of resource                         string
   *total_visuals* [2]_             | Total number of extracted visuals         integer
                                    | for documents in *documents*                 
   *visuals* [2]_                   List of extracted visuals                  array of visuals
   *visuals.document*               Document where the visual is located       same as *documents.location*
   *visuals.document_page*          Document page where visual is located      integer
   *visuals.bbox*                   Bounding box of visual                     array of floats
   *visuals.bbox_units*             Units of the bounding box                  ``pt`` (point), ``px`` (pixel)
   *visuals.id*                     Unique identifier of visual                string
   *visuals.caption*                Extracted caption of visual                array of strings
   *visuals.visual_type*            Type of visual                             string
   *visuals.location*               Location where extracte visual is stored   same as *documents.location*
   ================================ ========================================= ==============================================================================

.. rubric:: Footnotes

.. [1] TU Delft specific field.
.. [2] VisArchPy specific field.
.. [3] MODS related field.


Metadata File Example
---------------------

.. code-block:: json

    {
    "documents": [
        {
            "location": {
                "root_path": "./tests/data/00001/",
                "file_path": "00001_sample.pdf"
            }
        }
    ],
    "persons": [
        {
            "name": "Rom, O.",
            "role": "mentor"
        },
        {
            "name": "Bir, H.",
            "role": "mentor"
        },
        {
            "name": "Jen, P.",
            "role": "mentor"
        },
        {
            "name": "Hans, Y.",
            "role": "author"
        }
    ],
    "faculty": [
        {
            "name": "Architecture",
            "departments": [
                {
                    "name": "Architecture"
                }
            ]
        }
    ],
    "mods_file": "./tests/data/00001/00001_mods.xml",
    "title": "Resource title",
    "abstract": [
        "This is an example."
    ],
    "submission_date": "2020-09-03",
    "thesis_type": [
        "master thesis"
    ],
    "subjects": [
        "Mapping",
        "Mental Border"
    ],
    "copyright": [
        "(c) 2020 Hans, Y."
    ],
    "languages": [
        {
            "code": "en",
            "authority": "rfc3066"
        }
    ],
    "uuid": "uuid:0008286e-f16c-4e7b-8334-fe36fe9b09e4",
    "iid": null,
    "media_type": [],
    "issuance": [],
    "digital_origin": null,
    "doi": null,
    "edition": null,
    "extent": [],
    "form": [],
    "classification": [],
    "collection": null,
    "geo_code": null,
    "corp_names": [],
    "creators": [],
    "physical_description": [],
    "physical_location": [],
    "pid": null,
    "publication_place": [],
    "publisher": [],
    "purl": [],
    "type_resource": "text",
    "web_url": "http://resolver.tudelft.nl/uuid:0008286e-f16c",
    "total_visuals": 1,
    "visuals": [
        {
            "document": {
                "location": {
                    "root_path": "./tests/data/00001/",
                    "file_path": "00001_sample.pdf"
                }
            },
            "document_page": 1,
            "bbox": [
                49.9742,
                143.462,
                234.7092,
                331.342
            ],
            "bbox_units": "pt",
            "id": "5e5cc208-cd2c-4b09-a61a-5b6203d111b7",
            "caption": [
                "Figure 1: Caption of the figure extracted from document."
            ],
            "visual_type": null,
            "location": {
                "root_path": "./tests/data/layout/",
                "file_path": "00001/pdf-001/00001-page1-Im0.0.jpg"
            }
        }
    ]
    }


Metadata Classes
-------------------------

VisArchPy provides handles metdata extracted from the MODS file (if given) and extracted images (visuals) using the following classes:

.. autoclass:: visarchpy.metadata.FilePath
   :members:
   :undoc-members:


.. autoclass:: visarchpy.metadata.Person
   :members:
   :undoc-members:

.. autoclass:: visarchpy.metadata.Department
   :members:
   :undoc-members:

.. autoclass:: visarchpy.metadata.Faculty
   :members:
   :undoc-members:

.. autoclass:: visarchpy.metadata.Document
   :members:
   :undoc-members:

.. autoclass:: visarchpy.metadata.Visual
    :members:
    :undoc-members:

.. autoclass:: visarchpy.metadata.Metadata
    :members:
    :undoc-members: