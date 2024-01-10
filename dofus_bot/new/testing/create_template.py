import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image
import cv2
from matplotlib import pyplot as plt

img = cv2.imread('wheat_highlighted.png')
template = cv2.imread("wheat_binary_new.png", cv2.IMREAD_GRAYSCALE)
h, w = template.shape[:2]

# Creates some space around the outline
copied_template = np.zeros((h+10, w+10), np.uint8)
copied_template[5:-5, 5:-5] = template

# Fills any gaps in the outline
kernel = np.ones((5, 5), np.uint8)
outline = cv2.morphologyEx(copied_template, cv2.MORPH_CLOSE, kernel)

# Floodfills the outside
h, w = outline.shape[:2]
mask = np.zeros((h+2, w+2), np.uint8)
outline_copy = outline.copy()
cv2.floodFill(outline, mask, (0, 0), 255)

#invert
im_floodfill_inv = cv2.bitwise_not(outline)
im_out = outline_copy | im_floodfill_inv
im_out = im_out[5:-5, 5:-5]

masked_img = cv2.bitwise_and(img, img, mask=im_out)

cv2.imwrite('masked.png', masked_img)
