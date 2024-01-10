import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image
import cv2
import random
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def nothing():
    pass

cv2.namedWindow("image")
'''
# ITEM NAME
lh = 30
ls = 245
lv = 220
hh = 35
hs = 255
hv = 255

# ALTERNATIVE PRICE HSV
lh = 20
ls = 0
lv = 125
hh = 40
hs = 10
hv = 200
#----
lh = 0
ls = 0
lv = 140
hh = 60
hs = 10
hv = 255
'''

lh = 0
ls = 0
lv = 140
hh = 60
hs = 10
hv = 255

lh = 0
ls = 0
lv = 70
hh = 255
hs = 255
hv = 255

cv2.createTrackbar("lh", "image", lh, 255, nothing)
cv2.createTrackbar("ls", "image", ls, 255, nothing)
cv2.createTrackbar("lv", "image", lv, 255, nothing)
cv2.createTrackbar("hh", "image", hh, 255, nothing)
cv2.createTrackbar("hs", "image", hs, 255, nothing)
cv2.createTrackbar("hv", "image", hv, 255, nothing)

image = cv2.imread('screenshot2.png')

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
while True:
    lh = cv2.getTrackbarPos('lh', 'image')
    ls = cv2.getTrackbarPos('ls', 'image')
    lv = cv2.getTrackbarPos('lv', 'image')
    hh = cv2.getTrackbarPos('hh', 'image')
    hs = cv2.getTrackbarPos('hs', 'image')
    hv = cv2.getTrackbarPos('hv', 'image')
    lower_hsv = np.array([lh, ls, lv])
    higher_hsv = np.array([hh, hs, hv])
    image_filter = cv2.inRange(hsv, lower_hsv, higher_hsv)
    resource_amount = pytesseract.image_to_string(image_filter)
    print(resource_amount)

    cv2.imshow('image', hsv)
    cv2.imshow('filter1', image_filter)
    if (cv2.waitKey(1) & 0xFF == ord('q')):
        cv2.imwrite("wheats_binary4.png", image_filter)
        break

cv2.destroyAllWindows()
