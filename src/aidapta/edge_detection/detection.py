import iacv as iacv

import cv2
import os


image = cv2.imread('/home/manuel/Documents/devel/desing-handbook/data-pipelines/src/aidapta/edge_detection/page-19-id-par_1_7.png')

# cv2.imshow('original', image)
# cv2.waitKey(5000);
print(f"Shape of the image: {image.shape}")  

ex = 100 #@param 
ey = 100 #@param
image_edge = iacv.edge(image, e_range = [ex, ey])

cv2.imshow('edged', image_edge)
cv2.waitKey(50000);

# check whether gray scale
print(f"Shape of the image: {image_edge.shape}")


cnts, hierarchy = cv2.findContours(image_edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

print(f"The number of detected contours: {len(cnts)}")
print(f"First contour: {cnts[0].squeeze()}")
print(f"Length of first contour, ie number of points: {len(cnts[0])}")

cnt = cnts[0]
rect = cv2.minAreaRect(cnt)
box = cv2.boxPoints(rect)
print(box)

from shapely.geometry import Polygon

polygon = Polygon(box)
print(polygon)



import matplotlib.pyplot as plt

# to make sure delft is well promoted ;)
delft_color = "#00A6D6"

# fig settings
fs = 10
fig, ax = plt.subplots(1,1,figsize=(fs, fs))
ax.axis('off')

# plot image; plot polygon 
# (you can simply plot them by writing two lines!)
ax.imshow(image)
# set color, marker type, markersize, and linewidth to your preference!
iacv.plot_polygon(polygon, ax, color=delft_color, marker='o', markersize=10, linewidth=3)