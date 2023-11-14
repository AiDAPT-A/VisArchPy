import iacv as iacv

import cv2
import os

image = cv2.imread('data-pipelines/src/aidapta/edge_detection/page-19-id-par_1_7.png')

iacv.imshow(image)


ex = 100 #@param 
ey = 100 #@param
image_edge = iacv.edge(image, e_range = [ex, ey])
iacv.imshow(image_edge)