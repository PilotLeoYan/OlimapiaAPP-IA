from imutils.perspective import four_point_transform
# Nota: Leo, 21/05/2025, 6:10 pm
# >> from imutils import contours
# Si no se va a usar "contours", entonces es mejor no importar "from imutils import contours"
from imutils import contours
import numpy as np
import imutils
import cv2


def readImage(image_path: str) -> np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]:
    return cv2.imread(image_path) # type: ignore

def edgeDetection(image: np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]) -> tuple[np.ndarray[tuple[int, int], np.dtype[np.uint8]],
                                                                                        np.ndarray[tuple[int, int], np.dtype[np.uint8]]]:
    #Convertir a escala de grises y eliminar ruido
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    kernel = np.ones((3, 3), np.uint8)
    img_dilation = cv2.dilate(blurred, kernel, iterations=1)  
    edged = cv2.Canny(img_dilation, 75, 200)
    
    return edged, gray # type: ignore

def findContours(edges_in_image: np.ndarray[tuple[int, int], np.dtype[np.uint8]], 
                 gray_image: np.ndarray[tuple[int, int], np.dtype[np.uint8]], 
                 image: np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]) -> tuple[np.ndarray[tuple[int, int], np.dtype[np.uint8]],
                                                                                       np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]]:
    # Encontrar contornos
    cnts = cv2.findContours(edges_in_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    docCnt = None
    
    #Asegurarse que se encontro al menos un contorno
    if len(cnts) > 0:
        #Ordenar los contornos por tamaño en orden descendiente
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
	    #Iteramos sobre los contornos
        for c in cnts:
		    #Aproximamos el contorno (de la hoja)
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            #Si el contorno aproximado tiene 4 puntos, asumimos que
            #encontramos la hoja de respuestas
            if len(approx) == 4:
                docCnt = approx
                break
          
    if docCnt is not None:
        #Dibujamos el contorno
        cv2.drawContours(image.copy(), [docCnt], -1, (0, 255, 0), 2)
        
        #Transformacion de perspectiva
        four_point_view_paper=four_point_transform(image, docCnt.reshape(4, 2))
        warped = four_point_transform(gray_image, docCnt.reshape(4, 2))
        thresh = cv2.threshold(warped.copy(), 0, 255, cv2.THRESH_BINARY_INV | 
                       cv2.THRESH_OTSU)[1]

        return thresh, four_point_view_paper # type: ignore
    
    #Si no se detecta el borde de la hoja (el contenido abarca toda la imagen),
	#se usa el borde de la imagen
    h, w = image.shape[:2]
    docCnt = np.array([
        [[0, 0]],         # Esquina superior izquierda
        [[w - 1, 0]],       # Esquina superior derecha
        [[w - 1, h - 1]],     # Esquina inferior derecha
        [[0, h - 1]]        # Esquina inferior izquierda
    ])
	#Dibujar el contorno detectado
    cv2.drawContours(image, [docCnt], -1, (0, 255, 0), 2)
    four_point_view_paper=four_point_transform(image, docCnt.reshape(4, 2))
    warped = four_point_transform(gray_image, docCnt.reshape(4, 2))
    thresh = cv2.threshold(warped.copy(), 0, 255, cv2.THRESH_BINARY_INV | 
                           cv2.THRESH_OTSU)[1]

    return thresh, four_point_view_paper # type: ignore

def cropImage(thresh_img: np.ndarray[tuple[int, int], np.dtype[np.uint8]], 
              orig_img: np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]) -> tuple[np.ndarray[tuple[int, int], np.dtype[np.uint8]],
                                                                                       np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]]:
    top_fraction = 0.12
    bottom_fraction = 0.04
    left_fraction = 0.05
    right_fraction = 0.05
    height, width = thresh_img.shape[:2]
    
    #Calcular los pixeles a cortar
    top = int(height * top_fraction)
    bottom = int(height * (1 - bottom_fraction))
    left = int(width * left_fraction)
    right = int(width * (1 - right_fraction))
    
    cropped_image_thresh = thresh_img[top:bottom, left:right]
    cropped_image_org = orig_img[top:bottom, left:right]

    return cropped_image_thresh, cropped_image_org  # type: ignore
   
def findBubbles(thresh_img: np.ndarray[tuple[int, int], np.dtype[np.uint8]], 
                paper: np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]) -> np.ndarray[tuple[int, int, int], np.dtype[np.uint8]] | None:
    thresh_copy = thresh_img.copy()
    cnts = cv2.findContours(thresh_copy, cv2.RETR_TREE, 
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    questionCnts = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        ar = w/float(h)
        
        if 20 <= w <= 70 and 20 <= h <= 70 and 0.7 <= ar <= 1.2:
            questionCnts.append(c)

    if len(questionCnts) > 0:
        bubbles_paper = paper.copy()
        cv2.drawContours(bubbles_paper, questionCnts, -1, (0, 0, 255), 2)
 
        return bubbles_paper
   
    return