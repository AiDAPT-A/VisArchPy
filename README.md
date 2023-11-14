# VisArchPy

Data pipelines for extraction and analysis of architectural visuals in Python.

- [x] Extraction of architectural visuals from PDF documents.
- [x] Extraction of features from images using the DinoV2 model.
- [x] Analytics for exploring results.

## Requiremtns

- Python 3.10 or newer 
- [Tesseract v4.0](https://tesseract-ocr.github.io/)
- [PyTorch v2.1 or recent](https://pytorch.org/get-started/locally/)

## Installing the AiDAT-A library

1. Create a virtual environment:
    ```shell
    python3 -m venv .venv/
    ```
2. Clone the repository.
3. Install required aidapta package. From the repository root run:

    ```shell
    pip install -e .
    ```

## Pipelines

The pakcage implements two case-specific pipelines for the extraction visuals from PDF files.

1. The `image_pipeline.py`, uses `PDFMiner.six` to analyse the elements in a PDF file and extract visual and captions. We called this approache **layout analysis**.
2. The `image_ocr_pipeline.py`, uses *layout analysis* and **OCR analysis** to extract visual. The OCR analysis uses **Tesseract** to improve the extraction of drawing and floorplans.

## Running the Pipelines

1. Open the pipeline of your choice using Python
2. Configure the settings
3. Run

## Pipeline Settings
The following settings determine how image extraction is performed and they impact the outcomes.

**Image Settings:** `width` and `height` exlcude images in the PDF which size smaller than the values provided (pixels). If values for `width` and `height` are different, the smaller value will be used to exclude images. 
If present, the `ocr_output_resolution` defines the resolution of images used in OCR analysis, and therefore the resolution of extrated images. Higher resolutions do not necessarily improve the accuracy of the analysis.

```python
IMG_SETTINGS = {"width": 100, # pixels
                "height": 100, # recommended values: 0
                "ocr_output_resolution": 200, # dpi
                }
```

**Caption Settings:** strategy to look for captions during **layout analysis**. The `ofset` defines a maximum distance to look for captions around an image's bounding box; the `direction` defines the derection relative to the image that will be used to look for captions (using `all` increases the search area but might create more mismatches); and `keywords` is a list of words that are expected at the very beginning of a caption. *For example, it is commom to start captions with 'Figure' in academic documents.*


```python
CAP_SETTINGS ={"method": "bbox",
            "offset": 14, # one unit equals 1/72 inch or 0.3528 mm
            "direction": "down", # all directions
            "keywords": ['figure', 'caption', 'figuur'], # case insentitive
            "ocr_output_resolution": 200, # dpi
            }
```
