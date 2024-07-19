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

game_region = (0,0,0,0)

confidence = 0.45   # finding image matches
accuracy = 5    # distance in pixels between detections
pixels_per_second = 800 # how fast the cursor should move
delay = 0.25 # seconds to wait after each click
offset = 1     # max amount of pixels a click may be off from the center
resource_time = 3   # time it takes to gather a resource
max_wait_time = 30  # seconds to wait when nothing is happening

current_coordinates = [0,0]
current_path = []

def nothing():
    pass

cv2.namedWindow("image")

lh = 20
ls = 0
lv = 210
hh = 45
hs = 15
hv = 230

cv2.createTrackbar("lh", "image", lh, 255, nothing)
cv2.createTrackbar("ls", "image", ls, 255, nothing)
cv2.createTrackbar("lv", "image", lv, 255, nothing)
cv2.createTrackbar("hh", "image", hh, 255, nothing)
cv2.createTrackbar("hs", "image", hs, 255, nothing)
cv2.createTrackbar("hv", "image", hv, 255, nothing)

image = cv2.imread('again.png')

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
