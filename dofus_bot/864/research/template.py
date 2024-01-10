import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image
import cv2
from matplotlib import pyplot as plt

img = cv2.imread('wheats_binary.png')
template = cv2.imread("wheat_binary.png")
w, h, d = template.shape

methods = ['cv2.TM_CCOEFF_NORMED','cv2.TM_CCORR_NORMED'] 

i=0
for meth in methods:
    i += 1
    threshold = 0.33
    # ccoeff between (0.21 and 0.33)
    # ccorr between (0.35 and 0.43)
    copy = img.copy()
    method = eval(meth)

    res = cv2.matchTemplate(copy,template,method)
    # min_cal, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    #top_left = max_loc
    #bottom_right = (top_left[0] + w, top_left[1] + h)
    loc = np.where(res >= threshold)
    amount = 0
    for pt in zip(*loc[::-1]):
        amount += 1
        print(amount)
        cv2.rectangle(copy, pt, (pt[0] + w, pt[1] +h), (0,0,255), 2)
        #cv2.rectangle(copy, top_left, bottom_right, 255, 2)

    cv2.imwrite('res{}.png'.format(i), copy)
cv2.destroyAllWindows()
