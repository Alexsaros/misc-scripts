import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image
import cv2

def do(nothing):
    global img_masked
    amount = cv2.getTrackbarPos('amount', 'image')
    k1h = cv2.getTrackbarPos('k1h', 'image')
    k1w = cv2.getTrackbarPos('k1w', 'image')
    k2h = cv2.getTrackbarPos('k2h', 'image')
    k2w = cv2.getTrackbarPos('k2w', 'image')
    k3h = cv2.getTrackbarPos('k3h', 'image')
    k3w = cv2.getTrackbarPos('k3w', 'image')

    img2 = highlight.copy()
    closing_kernel = np.ones((k1h, k1w), np.uint8)
    closing_kernel_ver = np.ones((k2h, k2w), np.uint8)
    closing_kernel_hor = np.ones((k3h, k3w), np.uint8)
    highlights = cv2.morphologyEx(img2, cv2.MORPH_CLOSE, closing_kernel)
    for x in range(amount - 1):
        highlights2 = cv2.morphologyEx(img2, cv2.MORPH_CLOSE, closing_kernel)
        highlights3 = cv2.morphologyEx(img2, cv2.MORPH_CLOSE, closing_kernel_ver)
        highlights4 = cv2.morphologyEx(img2, cv2.MORPH_CLOSE, closing_kernel_hor)
        highlights = highlights | highlights2 | highlights3 | highlights4
    cv2.imwrite('2.png', highlights)
    # Fill in the outside of the interactable objects
    h, w = highlights.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    highlights_outside = highlights.copy()
    cv2.floodFill(highlights_outside, mask, (0, 0), 255)
    cv2.imwrite('3.png', highlights_outside)
    # Add the inside of the highlights and the highlights together to form the object's shape
    highlights_insides = cv2.bitwise_not(highlights_outside)
    highlights_filled = highlights_insides | highlights
    highlights_filled = highlights_filled[10:-10, 10:-10]
    cv2.imwrite('4.png', highlights_filled)
    # Finds what's inside the highlighted areas
    img_masked = cv2.bitwise_and(img, img, mask=highlights_filled)
    cv2.imwrite('5.png', img_masked)

amount = 1
k1h = 0
k1w = 0
k2h = 0
k2w = 0
k3h = 0
k3w = 0

cv2.namedWindow("image")

cv2.createTrackbar("amount", "image", amount, 10, do)
cv2.createTrackbar("k1h", "image", k1h, 30, do)
cv2.createTrackbar("k1w", "image", k1w, 30, do)
cv2.createTrackbar("k2h", "image", k2h, 30, do)
cv2.createTrackbar("k2w", "image", k2w, 30, do)
cv2.createTrackbar("k3h", "image", k3h, 30, do)
cv2.createTrackbar("k3w", "image", k3w, 30, do)

img = cv2.imread('0.png')
highlight = cv2.imread('1.png', cv2.IMREAD_GRAYSCALE)
img_masked = img.copy()

while True:
    scale_percent = 40 # percent of original size
    width = int(img_masked.shape[1] * scale_percent / 100)
    height = int(img_masked.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    resized = cv2.resize(img_masked, dim, interpolation = cv2.INTER_AREA)
    cv2.imshow('image', resized)
    if (cv2.waitKey(1) & 0xFF == ord('q')):
        break

cv2.destroyAllWindows()
