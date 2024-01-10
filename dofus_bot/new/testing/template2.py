import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image
import cv2
from matplotlib import pyplot as plt

img = cv2.imread('1.png')
template = cv2.imread("wheat_masked.png")
h, w = template.shape[:2]


#methods = ['cv2.TM_CCOEFF_NORMED']
#methods = ['cv2.TM_CCORR']
methods = ['cv2.TM_SQDIFF_NORMED']
#methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

imgs = ['1.png', '2.png', '3.png', '4.png']

grid_width = 89
grid_height = 44

i=0
for img_name in imgs:
    i += 1
    threshold = 0.39
    # threshold between 0.39 and 0.42
    # for sqdiff normed
    img = cv2.imread(img_name)
    copy = img.copy()
    method = eval('cv2.TM_SQDIFF_NORMED')

    sorted_pos = []

    res = cv2.matchTemplate(copy,template,method)
    loc = np.where(res <= threshold)
    for pos in zip(*loc[::-1]):
        sorted_pos.append([pos[0], pos[1], res[pos[1],pos[0]]])
    flipHorizontal = cv2.flip(template, 1)
    res = cv2.matchTemplate(copy,flipHorizontal,method)
    loc = np.where(res <= threshold)
    for pos in zip(*loc[::-1]):
        sorted_pos.append([pos[0], pos[1], res[pos[1],pos[0]]])
    sorted_pos.sort(key=lambda x: x[2])

    resource_list = []
    for match_pos in sorted_pos:
        duplicate = False
        for pos in resource_list:
            if abs(pos[0] - match_pos[0]) <= grid_width/2.5 and abs(
                    pos[1] - match_pos[1]) <= grid_height/2.5:
                duplicate = True
                break
        if not duplicate:
            resource_list.append([match_pos[0], match_pos[1]])

    amount = 0
    for pt in resource_list:
        amount += 1
        cv2.rectangle(copy, (pt[0], pt[1]), (pt[0] + w, pt[1] +h), (255,255,255), 2)
        #cv2.rectangle(copy, top_left, bottom_right, (255,0,0), 2)

    cv2.imwrite('res{}.png'.format(i), copy)
cv2.destroyAllWindows()
