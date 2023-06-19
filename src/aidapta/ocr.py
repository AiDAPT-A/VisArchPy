'''OCR pipeline with Tesseract'''

import pytesseract
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Convert PDF to image
IMAGES = convert_from_path('data-pipelines/data/actual-data/00001_multi-image-caption.pdf', dpi=300)
OUTPUT_DIR = 'data-pipelines/data/ocr-test/0001'

# tessaeract options
config = r'--oem 1 --psm 1 hocr' # Engine Neural nets LSTM only. Auto page segmentation with OSD

page_counter = 1
# Extract OCR data as hOCR document
for img in IMAGES:
    horc_data = pytesseract.image_to_pdf_or_hocr(img, extension='hocr', config=config)
    soup = BeautifulSoup(horc_data, 'html.parser')
    paragraphs = soup.find_all('p', class_='ocr_par')

    paragraphs_bounding_boxes = []
    paragraphs_ids = []
    # paragraph_confidence_scores = []
    # boxed_paragraphs = []
    for paragraph in paragraphs:
        title = paragraph.get('title')
        id = paragraph.get('id')
        if title:
            bounding_box = title.split(';')[0].split(' ')[1:]
            bounding_box = [int(value) for value in bounding_box]
            paragraphs_bounding_boxes.append(bounding_box)
            paragraphs_ids.append(id) 
        
    for bounding_box, id in zip(paragraphs_bounding_boxes, paragraphs_ids):
        x, y, w, h = bounding_box
        cropped_image = img.crop((x, y, w, h))
        # cropped_image.save(f'data-pipelines/data/ocr-test/image-{id}.jpg')

##########################################
# Plotting bounding boxes

    fig, ax = plt.subplots(1)

    # Display the image
    ax.imshow(img)

    # Create a Rectangle patch
    for bounding_box, id in zip(paragraphs_bounding_boxes, paragraphs_ids):
        x, y, w, h = bounding_box
        rect = patches.Rectangle((x, y), w - x, h - y, linewidth=2, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        tag_text = id
        tag_x = x
        tag_y = y
        plt.text(tag_x, tag_y, tag_text, fontsize=12, color='blue', ha='left', va='center')

    plt.savefig(f'{OUTPUT_DIR}/page-{page_counter}.png')
    # plt.show()
