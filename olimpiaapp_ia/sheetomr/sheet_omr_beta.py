from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import imutils
import cv2

def readImage(localTestImagePath):
    image = cv2.imread(localTestImagePath)
    resized = imutils.resize(image, height=700)
    return resized

def edgeDetection(resized_image):
    #Convertir a escala de grises y eliminar ruido
    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    kernel = np.ones((3, 3), np.uint8)
    img_dilation = cv2.dilate(blurred, kernel, iterations=1)  
    edged = cv2.Canny(img_dilation, 75, 200)
    # cv2.imshow("Deteccion de bordes en la imagen", edged)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    #Correcci�n de iluminaci�n
    adaptive_thresh = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                cv2.THRESH_BINARY_INV,9,11)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    close = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
    dilate = cv2.dilate(close, kernel, iterations=1)
    result = 255 - dilate
    
    return edged, result

def findContours(edges_in_image, corrected_image, resized):
    # Encontrar contornos
    cnts = cv2.findContours(edges_in_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts=imutils.grab_contours(cnts)
    docCnt = None
    
    #Asegurarse que se encontr� al menos un contorno
    if len(cnts) > 0:
        #Ordenar los contornos por tama�o en orden descendiente
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
        cv2.drawContours(resized, [docCnt], -1, (0, 255, 0), 2)
        #resized = imutils.resize(resized, height=700)
        #Transformaci�n de perspectiva
        paper = four_point_transform(resized, docCnt.reshape(4, 2))
        warped = four_point_transform(corrected_image, docCnt.reshape(4, 2))
        # cv2.imshow("Hoja Detectada", resized)
        # cv2.imshow("Hoja Transformada",paper)
        # cv2.waitKey()
	
        thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        # cv2.imshow("Imagen binarizada", thresh)
        # cv2.waitKey()
        return thresh
    else:
	    #Si no se detecta el borde de la hoja (el contenido abarca toda la imagen),
	    #se usa el borde de la imagen
        h, w = resized.shape[:2]
        docCnt = np.array([
            [[0, 0]],         # Esquina superior izquierda
            [[w-1, 0]],       # Esquina superior derecha
            [[w-1, h-1]],     # Esquina inferior derecha
            [[0, h-1]]        # Esquina inferior izquierda
        ])
	    #Dibujar el contorno detectado
        cv2.drawContours(resized, [docCnt], -1, (0, 255, 0), 2)
        # cv2.imshow("Usando borde de la imagen", resized)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
        return resized
	



          