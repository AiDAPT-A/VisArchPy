"""
This example shows how to use the library
to extract metadata from an HTML page, and
download PDF files from the website of the
thesis repository at TU Delft
"""
from visarchpy import metadata

# EXTRACTING METADATA as a dictionary
print(">>> extracting metadata ...")
page_url = "https://repository.tudelft.nl/islandora/object/uuid%3A4457ef73-5f7e-47cd-9013-f2a78eca76df"

result = metadata.extract_metadata_from_html(page_url)
print(result)
print(">>> completed metadata extraction")

# DOWNLOADING PDF file from endpoint
file_endpoint= "https://repository.tudelft.nl/islandora/object/uuid%3A4457ef73-5f7e-47cd-9013-f2a78eca76df/datastream/OBJ/download" 
print(">>> downloading PDF file...")

metadata.download_PDF(file_endpoint, "examples/downloads")
print(">>> completed download")
