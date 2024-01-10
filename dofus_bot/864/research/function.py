import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image
import cv2
from matplotlib import pyplot as plt

# used for testing template matching methods??

img = cv2.imread('wheats_binary.png')

screenshot = pyautogui.screenshot()
hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2HSV)
lower_hsv = np.array([15, 30, 210])
higher_hsv = np.array([30, 90, 255])
filtered = cv2.inRange(hsv, lower_hsv, higher_hsv)

template = cv2.imread("wheat_binary.png")
w, h, d = template.shape
threshold = 0.33

positions = []
res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED)
loc = np.where(res >= threshold)
for pt in zip(*loc[::-1]):
    clone = False
    print(pt)
    for pos in positions:
        if abs(pos[0] - pt[0]) <= 5 and abs(pos[1] - pt[1]) <= 5:
            clone = True
            break
    if not clone:
        positions.append([pt[0], pt[1]])
positions_middle = []
for pos in positions:
    positions_middle.append([int(pos[0]+w*0.5), int(pos[1]+h*0.3)])

