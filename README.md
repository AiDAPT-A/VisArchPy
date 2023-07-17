# Data Pipelines

Pipelines for the extraction and processing of visuals from PDFs.

## Requirements

- Python 3.10 or newer 
- PIL
- [Tesseract v.4.0](https://tesseract-ocr.github.io/)

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

