import fitz
import io
from PIL import Image

import fitz 

pdf_classic = "data/RethinkWaste_research_paper_LisaUbbens_4397436.pdf"
pdf2 = "data/4563050_AmberLuesink_P5Report_TheRevivaloftheJustCity.pdf"

# open PDF document
pdf_doc = fitz.open(pdf_classic) 


for i in range(len(pdf_doc)): 
    for img in pdf_doc.get_page_images(i): 
        xref = img[0] 
        pix = fitz.Pixmap(pdf_doc, xref) 
        if pix.n < 5:       # this is GRAY or RGB 

            # pix.writePNG("p%s-%s.png" % (i, xref)) 
            pix.save("p%s-%s.png" % (i, xref), 'PNG')
        else:               # CMYK: convert to RGB first 
            pix1 = fitz.Pixmap(fitz.csRGB, pix) 

            # pix1.writePNG("p%s-%s.png" % (i, xref)) 
            pix.save("p%s-%s.png" % (i, xref), 'PNG')

            pix1 = None 

        pix = None 