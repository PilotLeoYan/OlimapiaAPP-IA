import numpy as np
import cv2
import imutils
from imutils.perspective import four_point_transform
from pyzbar.pyzbar import decode


def readImage(path):
    image = cv2.imread(path, cv2.IMREAD_REDUCED_COLOR_4)

    if image is None:
        raise ValueError('file could not be read, check with os.path.exists()')
    return image

def rgb2gray(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def gray2edges(gray):
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    kernel = np.ones((3, 3), np.uint8)
    img_dilation = cv2.dilate(blurred, kernel, iterations=1)  
    edges = cv2.Canny(img_dilation, 75, 200)
    return edges

def findContours(gray, edges, strict=False):
    cnts = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
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

def detectAnswers(threshold):
    circles = cv2.HoughCircles(
        threshold,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=10,
        param1=10,
        param2=10,
        minRadius=6,
        maxRadius=15
    )

    answers = {}
    if circles is None:
        raise NotImplementedError('change this exception')
        
    circles = np.round(circles[0, :]).astype(np.int32)

    rows = {}
    # (x=first column, y=second column, r=third column) per row
    for x, y, r in circles:
        row_found = False
        for row_y in rows:
            if abs(row_y - y) <= r * 2:
                rows[row_y].append((x, y, r))
                row_found = True
                break

        if not row_found:
            rows[y] = [(x, y, r)]

    for row_y in sorted(rows.keys()):
        row_bubbles = sorted(rows[row_y], key=lambda b: b[0])
        bubble_status = []

        for x, y, r in row_bubbles:
            mask = np.zeros_like(threshold)
            cv2.circle(mask, (x, y), r, 255, -1) # type: ignore
            roi = cv2.bitwise_and(threshold, threshold, mask=mask)

            sqr_r = r ** 2
            total_area = np.pi * sqr_r
            filled_pixels = np.sum(roi == 255)
            fill_ratio = filled_pixels / total_area
            bubble_status.append((x, y, r, fill_ratio))

        marked_bubble = None
        for idx, (x, y, r, fill_ratio) in enumerate(bubble_status):
            if fill_ratio > 0.35:
                marked_bubble = idx
                break

        if marked_bubble is not None:
            answers[row_y] = chr(65 + marked_bubble)
            cv2.circle(
                threshold,
                (row_bubbles[marked_bubble][0], row_bubbles[marked_bubble][1]),
                row_bubbles[marked_bubble][2],
                (255, 0, 0),
                3
            )
        else:
            answers[row_y] = "?"
        
    return threshold, answers # type: ignore