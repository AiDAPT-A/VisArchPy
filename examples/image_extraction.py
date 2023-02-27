"""
This example shows how to extract
images from a PDF file to a directory
"""

from aidapta import image

# PDF file to be process
pdf_file = "./data/4563050_AmberLuesink_P5Report_TheRevivaloftheJustCity.pdf"

# Directory to store extracted images. If it doesn't
# exist, it will be created
img_dir = "./examples/img/"

print(">>> Extracting images, it may take a while...")

image.extract_images(pdf_file, img_dir)

print(">>> Finished extracting images")
