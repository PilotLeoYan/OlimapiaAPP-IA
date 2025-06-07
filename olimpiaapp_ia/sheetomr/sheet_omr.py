import numpy as np
import cv2
from imutils import grab_contours
from imutils.perspective import four_point_transform
#from pyzbar.pyzbar import decode


def readImage(path):
    image = cv2.imread(path, cv2.IMREAD_REDUCED_COLOR_8)

    if image is None:
        raise ValueError('file could not be read, check with os.path.exists()')
    return image

def rescale(image):
    new_height: int = 1000
    new_width: int = 750

    new_image = cv2.resize(image, (new_width, new_height))
    return new_image

def rgb2gray(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def gray2edges(gray):
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    kernel = np.ones((3, 3), np.uint8)
    img_dilation = cv2.dilate(blurred, kernel, iterations=1)  
    edges = cv2.Canny(img_dilation, 30, 100)
    return edges

def findContours(gray, edges, strict=False):
    cnts = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = grab_contours(cnts)
    docCnt = None

    if len(cnts) > 0:
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) == 4:
                docCnt = approx
                break

    if docCnt is not None:
        warped = four_point_transform(gray, docCnt.reshape(4, 2))
        threshold = cv2.adaptiveThreshold(
            warped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        return threshold
    
    if strict:
        raise Exception('edit this exception')
    
def cropImage(threshold):
    top_fraction = 0.12
    bottom_fraction = 0.04
    left_fraction = 0.05
    right_fraction = 0.05
    height, width = threshold.shape[:2]

    top = int(height * top_fraction)
    bottom = int(height * (1 - bottom_fraction))
    left = int(width * left_fraction)
    right = int(width * (1 - right_fraction))

    cropped_threshold = threshold[top:bottom, left:right]
    return cropped_threshold

def split2vertical(cropped_threshold):
    height, width = cropped_threshold.shape[:2]
    part_height = int(height * 0.09)
    part_width = width // 2

    left = cropped_threshold[part_height:, 0:part_width]
    right = cropped_threshold[part_height:, part_width:2 * part_width]

    part_height2 = int(len(right) * (1 - 0.13))
    return left, right[:part_height2]

@FutureWarning
def detectAnswers(threshold):
    img = cv2.GaussianBlur(threshold, (5, 5), 0)

    circles = cv2.HoughCircles(
        img,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=25,
        param1=70,
        param2=25,
        minRadius=6,
        maxRadius=15
    )