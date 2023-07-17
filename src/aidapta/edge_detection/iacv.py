'''
Package for 1:1 Interactive Architecture Prototypes course - Computer vision part
'''

#PACKAGES
from scipy.spatial import distance as dist
import cv2
from imutils import perspective
from imutils import contours
import imutils
import matplotlib.pyplot as plt
import math
import numpy as np
from scipy.spatial import distance as dist
import shapely
from shapely.geometry import Polygon, LineString, Point

#SETTINGS
color_edge    = (0, 255, 0)   #bounding box
color_text    = (0, 255, 0)   #text
color_line    = (255, 0, 255) #middle lines (crossing in middle of object)
color_bpoints = (0, 0, 255)   #bounding box angle points
color_mpoints = (255, 0, 0)   #bounding box middle points
color_cross   = (0, 0, 255)   #center of mass color


#UTILITIES
# def midpoint(ptA, ptB):
#     return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def pixpermetric(img, ref, metric="cm", show=False):
    h, w = img.shape[0], img.shape[1]
    if isinstance(ref, float) or isinstance(ref, int): 
        pixpm = w/ref
        if show: print(f"Pixels per {metric} in X and Y = {pixpm:.2f}")
    else: 
        refw, refh = ref[0], ref[1]
        pixpm = [h/refh, w/refw]
        if show: print(f"Pixels per {metric} in Y = {pixpm[0]:.2f} \nPixels per {metric} in X = {pixpm[1]:.2f}")
    return pixpm

def pix2metric(dim, pixpm, metric="cm",show=False):
    dimY, dimX = dim[0], dim[1]
    if isinstance(pixpm, float) or isinstance(pixpm, int): d = [dimY/pixpm, dimX/pixpm]
    else: d = [dimY/pixpm[0], dimX/pixpm[1]]
    if show: print(f"The size of the bounding box frame is: {d[0]:.2f}{metric} x {d[1]:.2f}{metric} (height x width) /n")
    return d

# def getbbox(cnts):
#     bboxs = [] #create empty list to store the bounding box data
#     for c in cnts:
#         # compute the rotated bounding box of the contour
#         box = cv2.minAreaRect(c)
#         box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
#         box = np.array(box, dtype="int")
        
#         # order the points in the contour such that 
#         # they would appear in top-left, 
#         # top-right, bottom-right, and bottom-left order
#         bboxs.append(perspective.order_points(box))
    
#     return bboxs

# def getcm(bboxs):
#     cms = [] #create empty list to store the center of mass data
#     for box in bboxs:
#         cm_y = np.sum(box[:,0])/4
#         cm_x = np.sum(box[:,1])/4
#         cms.append([cm_y, cm_x])
#     return cms

# def draw_cross(img, center, color, d=10, t=3):
#     cv2.line(img,
#              (center[0] - d, center[1] - d), (center[0] + d, center[1] + d),
#              color, t, cv2.LINE_AA, 0)
#     cv2.line(img,
#              (center[0] + d, center[1] - d), (center[0] - d, center[1] + d),
#              color, t, cv2.LINE_AA, 0) 

def contours2polygons(cnts):
  polygons = []
  for cnt in cnts:
    cnt = cnt.squeeze()
    if len(cnt) < 4: continue
    polygons.append(Polygon(cnt))
  return polygons

#IMAGE PROCESSING

#_simple
def getshape(img):
    h, w, dim = img.shape
    print(f"Shape of the image is {h} x {w} x {dim} (height x width x dimension)")
    
def imresize(img, w_resize=500):
    h, w = img.shape[0], img.shape[1]
    h_resize = int(h / w * w_resize)
    dim = (w_resize, h_resize)
    img_resize = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return img_resize

def rgb2gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def border2color(image, color=[255, 255, 255], off=10):

    image[:,  :off] = np.array(color)
    image[:, -off:] = np.array(color)
    image[:off,  :] = np.array(color)
    image[-off:, :] = np.array(color)

    return image

def concat_images_horizontally(images):
    imgs_to_stack = []
    for image in images:
        if len(image.shape) == 2:
            imgs_to_stack.append(np.stack([image]*3, axis=2))
        elif len(image.shape) == 3:
            imgs_to_stack.append(image)
        else: raise(NotImplementedError)
    return np.concatenate(imgs_to_stack, axis=1)


#_filter
def edge(img, e_range=(75,100)):
    return cv2.Canny(img, e_range[0], e_range[1]) #simple edge detector

def dilate(img, ksize=3, iterations=1):
    return cv2.dilate(img, (ksize, ksize), iterations=iterations)

def erode(img, ksize=3, iterations=1):
    return cv2.erode(img, (ksize, ksize), iterations=iterations)

def blur(img, ksize=5):
    return cv2.GaussianBlur(img, (ksize, ksize), 0)


# _advanced
def findcnts(img, a_min=100):
    
    # `cnts_` is a list with all contours, `cnts` with the real ones
    cnts_ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_ = imutils.grab_contours(cnts_)
    (cnts_, _) = contours.sort_contours(cnts_)
    
    cnts = [] #create empty list to store the 'real' contour data
    
    for c in cnts_:
        # if the contour is not sufficiently large, ignore it
        if cv2.contourArea(c) < a_min: continue
        cnts.append(c)

    return cnts

def warp(img, cnt):

    rect = cv2.minAreaRect(cnt)
    box  = cv2.boxPoints(rect)
    box  = np.int0(box)
    w_rect = int(rect[1][0])
    h_rect = int(rect[1][1])
    
    #get source and distance points
    src_pts = box.astype("float32")
    dst_pts = np.array([[0, h_rect-1],
                        [0, 0],
                        [w_rect-1, 0],
                        [w_rect-1, h_rect-1]], dtype="float32")
    
    #perspective transform and warping of the image based on rectangular reference frame
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(img, M, (w_rect, h_rect))
    
    return warped


#IMAGE PLOTTING

def imshow(img, figsize=[10, 10], axis=False):
    imgp = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #color annotation is different for plt.imshow and cv2.imread
    plt.figure(figsize=figsize)
    if axis==False: plt.axis('off')    
    plt.imshow(imgp)

def plot_polygon(polygon, ax, **kwargs):
  x, y = polygon.exterior.xy
  ax.plot(x, y, **kwargs)
    
# def drawbbox(img, bboxs, pixpm=None, dimbbox=None):
    
#     #copy image
#     img = img.copy()
    
#     for bbox in bboxs:
        
#         #draw contours
#         cv2.drawContours(img, [bbox.astype("int")], -1, color_edge, 2)
        
#         # loop over the original points and draw them
#         for (x, y) in bbox:
#             cv2.circle(img, (int(x), int(y)), 5, color_bpoints, -1)
        
#         # unpack the ordered bounding box, then compute the midpoint 
#         # between the top-left and top-right coordinates, followed 
#         # by the midpoint between bottom-left and bottom-right coordinates
#         (tl, tr, br, bl) = bbox
#         (tltrX, tltrY) = midpoint(tl, tr)
#         (blbrX, blbrY) = midpoint(bl, br)

#         # compute the midpoint between the top-left and top-right points, 
#         # followed by the midpoint between the top-righ and bottom-right
#         (tlblX, tlblY) = midpoint(tl, bl)
#         (trbrX, trbrY) = midpoint(tr, br)

#         # draw the midpoints on the image
#         cv2.circle(img, (int(tltrX), int(tltrY)), 5, color_mpoints, -1)
#         cv2.circle(img, (int(blbrX), int(blbrY)), 5, color_mpoints, -1)
#         cv2.circle(img, (int(tlblX), int(tlblY)), 5, color_mpoints, -1)
#         cv2.circle(img, (int(trbrX), int(trbrY)), 5, color_mpoints, -1)

#         # draw lines between the midpoints
#         cv2.line(img, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
#             color_line, 2)
#         cv2.line(img, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
#             color_line, 2)

#         # compute the Euclidean distance between the midpoints
#         dimA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
#         dimB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
        
#         if pixpm is not None:
#             # if the pixels per metric has not been initialized, then compute 
#             # it as the ratio of pixels to supplied metric (in this case, inches)
#             d = pix2metric([dimA, dimB], pixpm)
#         elif dimbbox is not None:
#             d = dimbbox

#         # draw the object sizes on the image
#         cv2.putText(img, "{:.2f} cm".format(d[0]),
#             (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
#             0.65, color_text, 2)
#         cv2.putText(img, "{:.2f} cm".format(d[1]),
#             (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
#             0.65, color_text, 2)
    
#     imshow(img)
        
# def drawcm(img, cms, pixpm):
    
#     for cm in cms:

#         # distance per metric
#         cm_metric = pix2metric(cm, pixpm)

#         # draw cross in the middle
#         draw_cross(img, (int(cm[0]), int(cm[1])), color_cross)

#         # draw the object sizes on the image
#         cv2.putText(img, "{:.2f} cm".format(cm_metric[0]),
#             (int(cm[0] - 25), int(cm[1] - 25)), cv2.FONT_HERSHEY_SIMPLEX,
#             0.65, color_text, 2)
#         cv2.putText(img, "{:.2f} cm".format(cm_metric[1]),
#             (int(cm[0] + 25), int(cm[1] + 6)), cv2.FONT_HERSHEY_SIMPLEX,
#             0.65, color_text, 2)
    
#     #show image
#     imshow(img)
    
# def findelement(dim, bboxs, pixpm):

#     dim = np.array(dim)
#     d = []
    
#     for bbox in bboxs:

#         (tl, tr, br, bl) = bbox
#         (tltrX, tltrY) = midpoint(tl, tr)
#         (blbrX, blbrY) = midpoint(bl, br)

#         # compute the midpoint between the top-left and top-right points, 
#         # followed by the midpoint between the top-righ and bottom-right
#         (tlblX, tlblY) = midpoint(tl, bl)
#         (trbrX, trbrY) = midpoint(tr, br)

#         # compute the Euclidean distance between the midpoints
#         dimA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
#         dimB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
        
#         if pixpm is not None:
#             # if the pixels per metric has not been initialized, then compute 
#             # it as the ratio of pixels to supplied metric (in this case, inches)
#             d.append(pix2metric([dimA, dimB], pixpm))

    
#     #get difference and find closest point (based on euclidian distance)
#     d = np.array(d)
#     eucl = np.sqrt(np.sum(np.power(d - dim, 2), axis=1))

#     #find using argsort (finds argument)
#     idx = np.argsort(eucl)[0]

#     return idx

def get_angles(vec_1,vec_2):
    """
    return the angle, in degrees, between two vectors
    """
    
    dot = np.dot(vec_1,vec_2)
    det = np.cross(vec_1,vec_2)
    angle_in_rad = np.arctan2(det,dot)
    return np.degrees(angle_in_rad)


def simplify_by_angle(poly_in, deg_tol=1):
    '''Try to remove persistent coordinate points that remain after
    simplify, convex hull, or something, etc. with some trig instead

    poly_in: shapely Polygon
    deg_tol: degree tolerance for comparison between successive vectors
    '''
    ext_poly_coords = poly_in.exterior.coords[:]
    vector_rep = np.diff(ext_poly_coords, axis=0)
    num_vectors = len(vector_rep)
    angles_list = []
    for i in range(0, num_vectors):
        angles_list.append(np.abs(get_angles(vector_rep[i], vector_rep[(i + 1) % num_vectors])))

    #   get mask satisfying tolerance
    thresh_vals_by_deg = np.where(np.array(angles_list) > deg_tol)

    new_idx = list(thresh_vals_by_deg[0] + 1)
    new_vertices = [ext_poly_coords[idx] for idx in new_idx]

    return Polygon(new_vertices)


# simplify contours with shapely
def simplify_polygons(polygons):
    polygons_simplified = []
    for pol in polygons:
        deg_tol = 26 #@param
        pol_simple = simplify_by_angle(pol, deg_tol = deg_tol)
        pol_simple = pol_simple.simplify(tolerance=4)
        polygons_simplified.append(pol_simple)
    return polygons_simplified

def get_hole_polygons_from_contours(cnts, a_min, a_max):
  polygons = []
  for cnt in cnts:
    cnt = cnt.squeeze()
    if len(cnt) < 4: continue
    pol = Polygon(cnt)
    if a_min < pol.area < a_max:
      pol_intersects = False
      if len(polygons) > 0:
        for p in polygons:
          if pol.intersects(p):
            pol_intersects = True
      if not pol_intersects: 
        deg_tol = 26 #@param
        pol_simple = simplify_by_angle(pol, deg_tol = deg_tol)
        pol_simple = pol_simple.simplify(tolerance=3)
        polygons.append(pol_simple)
  return polygons

def get_largest_edge_from_polygon(pol):
  x, y = pol.exterior.coords.xy

  x = np.array(x)
  y = np.array(y)

  dx = x[:-1] - x[1:]
  dy = y[:-1] - y[1:]

  dxy2 = np.sqrt(np.power(dx, 2) + np.power(dy, 2))

  argmax = np.argmax(dxy2)
  max_line = np.stack([x[argmax:argmax+2], y[argmax:argmax+2]], axis=1)
  return LineString(max_line)

def get_angle_from_line(line, pol):
    pt1 = Point(line.coords[0])
    pt2 = Point(line.coords[1])
    x_diff = pt2.x - pt1.x
    y_diff = pt2.y - pt1.y
    angle_temp = math.degrees(math.atan2(y_diff, x_diff))
    polvec = np.sum(np.power(pol.centroid.coords.xy, 2))
    linevec = np.sum(np.power(line.coords.xy, 2))
    if polvec < linevec:
      angle = 90 - angle_temp
    else:
      angle = 270 - angle_temp
    return angle

def plot_robot_grab(img, pol, ax):
    
    # get line and centroid coordinates
    line = get_largest_edge_from_polygon(pol)
    angle = get_angle_from_line(line, pol)
    line_coords = np.array(line.coords.xy)
    line_centroid_coords = np.array(line.centroid.coords.xy)

    ax.imshow(img)
    # set color, marker type, markersize, and linewidth to your preference!
    ax.plot(line_coords[0], line_coords[1], marker='o', markersize=7, linewidth=3)

    x = float(line_centroid_coords[0])
    y = float(line_centroid_coords[1])
    dx = math.sin((90+angle)/360*2*math.pi)*20
    dy = math.cos((90+angle)/360*2*math.pi)*20
    ax.plot(x, y, marker='o', markersize=10, color='orange')
    ax.arrow(x, y, dx, dy, head_starts_at_zero=True, width=3, ls='', fc='orange')
    circle = plt.Circle((x, y), 45, color='orange', ls='--', fill=False, lw=3)
    ax.add_patch(circle)

    return line_centroid_coords, angle