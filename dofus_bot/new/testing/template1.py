import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image
import cv2
from matplotlib import pyplot as plt

img = cv2.imread('gray1.png', cv2.IMREAD_GRAYSCALE)
template = cv2.imread("wha1.png", cv2.IMREAD_GRAYSCALE)
w, h = template.shape


#methods = ['cv2.TM_CCOEFF_NORMED']
#methods = ['cv2.TM_CCORR']
methods = ['cv2.TM_SQDIFF_NORMED']
#methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

i=0
for meth in methods:
    i += 1
    threshold = 0.5
    # ccoeff between (0.20 and ?0.XX?)
    # ccorr between (0.35 and 0.43)
    '''
    img1 = cv2.imread('3.png', cv2.IMREAD_GRAYSCALE)
    img = cv2.imread('1.png')
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_hsv = np.array([15, 5, 130])
    higher_hsv = np.array([35, 80, 255])
    img_filtered = cv2.inRange(img_hsv, lower_hsv, higher_hsv)
    
    kernel = np.ones((int(h/2),int(w/2)),np.uint8)
    closing = cv2.morphologyEx(img1, cv2.MORPH_CLOSE, kernel)
    filtered = cv2.bitwise_and(img,img,mask=closing)
    cv2.imwrite('res{}.png'.format(i), filtered)
    '''

    copy = img.copy()
    method = eval(meth)

    res = cv2.matchTemplate(copy,template,method)

    loc = np.where(res <= threshold)
    amount = 0
    for pt in zip(*loc[::-1]):
        amount += 1
        cv2.rectangle(copy, pt, (pt[0] + w, pt[1] +h), 255, 2)

    cv2.imwrite('res{}.png'.format(i), copy)
    plt.subplot(121), plt.imshow(res, cmap='gray')
    plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(img, cmap='gray')
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.suptitle(meth)
    plt.savefig('{}.png'.format(meth))
