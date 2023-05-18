import cv2
import imutils
import numpy as np
import pytesseract
import re

# Tesseract path (change it according to your own path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def readPlate(img):
    # Filter process
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 50, 200)
    try:
        # Contour process
        cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) 
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:20][::-1]
        screenCnt = None
        # Contour filtering
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.035 * peri, True)
            if len(approx) == 4:
                (x, y, w, h) = cv2.boundingRect(approx)
                aspectRatio = float(w) / float(h)
                if aspectRatio >= 4 and aspectRatio <= 4.9:
                    screenCnt = approx
                    break
        
        if screenCnt is not None:
            # Masking process
            mask = np.zeros(gray.shape, np.uint8)
            cv2.drawContours(mask, [screenCnt], 0, 255, -1,)
            cv2.bitwise_and(img, img, mask=mask)
            # Cropping process
            (x, y) = np.where(mask == 255)
            (topx, topy) = (np.min(x), np.min(y))
            (bottomx, bottomy) = (np.max(x), np.max(y))
            Cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

            # Median filter
            median = np.median(Cropped)
            if 120 < median < 250:
                cv2.drawContours(img, [screenCnt], -1, (50, 50, 255), 2)

                text = pytesseract.image_to_string(Cropped)
                text = text.replace(" ", "")
                text = text.upper()
                text = ''.join(e for e in text if e.isalnum())

                # If first character is letter, delete
                while text[0].isalpha():
                    text = text[1:]
                
                # If last character is letter, delete
                while not text[-1].isdigit():
                    text = text[:-1]
                
                """
                The license plate structure can be in one of the following three formats:
                1) First two characters are numbers, third character is a letter, and the last four characters are numbers.
                2) First two characters are numbers, the following two characters are letters, and the last three or four characters are numbers.
                3) First two characters are numbers, the following three characters are letters, and the last two or three characters are numbers.
                """
                regex = r"^(?:\d{2}[A-Z]\d{4}|\d{2}[A-Z]{2}\d{3,4}|\d{2}[A-Z]{3}\d{2,3})$"

                if re.match(regex, text):
                  cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 2)  # If the license plate is detected, draw a green contour around it
                  print("PLATE: ", text)
                  cv2.putText(img, text, Cropped.shape, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    except Exception:
        pass
    return img