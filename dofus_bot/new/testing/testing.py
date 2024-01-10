import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image
import cv2


buttons_pos = pyautogui.locateCenterOnScreen('menu_buttons.png', confidence=0.80)
image = np.array(pyautogui.screenshot())
image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
print(buttons_pos)
print(buttons_pos[0])
image[buttons_pos[1]][buttons_pos[0]] = [0,255,0]

cv2.namedWindow("image")

while True:
    cv2.imshow('image', image)
    if (cv2.waitKey(1) & 0xFF == ord('q')):
        break

cv2.destroyAllWindows()
