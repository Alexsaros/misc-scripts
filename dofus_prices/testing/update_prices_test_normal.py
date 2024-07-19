import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
import cv2
import pickle
import pytesseract
import pyautogui
import os
import time
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

img = cv2.imread('screenshot97.png')

item_list = []

cv2.namedWindow("image")

# rescale names for better text detection
name_column = img[:, :277, :]
scale = 1
width = int(name_column.shape[1]*scale)
height = int(name_column.shape[0]*scale)
dsize = (width, height)
name_column = cv2.resize(name_column, dsize)
# finds all of the item names
name_text = pytesseract.image_to_string(name_column)
names = []
# filter the found names
for found_name in name_text.split('\n'):
    if found_name != '' and found_name != '\x0c':
        names.append(found_name)
        print(found_name)
# rescale prices for better text detection
price_column = img[:, -136:, :]
scale = 5
width = int(price_column.shape[1]*scale)
height = int(price_column.shape[0]*scale)
dsize = (width, height)
price_column = cv2.resize(price_column, dsize)
# finds all of the prices
price_text = pytesseract.image_to_string(price_column, config="digits")
prices = []
for found_price in price_text.split('\n'):
    if found_price != '' and found_price != '\x0c' and found_price != ' ':
        found_price = found_price.replace(',', '')
        found_price = found_price.replace('.', '')
        prices.append(found_price)
# checks if prices have been missed
if len(names) == len(prices):
    for x in range(len(names)):
        item_list.append([names[x], int(prices[x])])
'''
else:
    print(len(names), len(prices))
    # highlights the pixels of the prices
    price_column = img[:, -136:, :]
    lh = 0
    ls = 0
    lv = 70
    hh = 255
    hs = 255
    hv = 255
    lower_hsv = np.array([lh, ls, lv])
    higher_hsv = np.array([hh, hs, hv])
    price_column_filtered = cv2.inRange(price_column, lower_hsv, higher_hsv)
    amount_of_rows = int(img.shape[0]/40)+1
    # iterates over the rows of items in the image
    for x in range(amount_of_rows):
        if x>-13 and x < 200:
            name = names[x]
            print('=============')
            print(name)
            # selects the row where the price is
            price_row = price_column[x*40:(x+1)*40, :, :]
            price_row_filtered = price_column_filtered[x*40:(x+1)*40, :]
            # selects only the area with text
            rows, cols = np.nonzero(price_row_filtered)
            left = cols.min()-3
            right = cols.max()+4
            top = rows.min()-3
            bottom = rows.max()+3
            price_row = price_row[top:bottom, left:right]
            # rescale for better text detection
            scale = 2
            width = int(price_row.shape[1]*scale)
            height = int(price_row.shape[0]*scale)
            dsize = (width, height)
            price_row = cv2.resize(price_row, dsize)
            # reads the price
            price_text = pytesseract.image_to_string(price_row, config="--psm 7 digits")
            price = ''
            for found_price in price_text.split('\n'):
                if found_price != '' and found_price != '\x0c':
                    # if the first digit got wrongly detected as 0
                    if found_price[0] == '0':
                        break
                    found_price = found_price.replace(',', '')
                    found_price = found_price.replace('.', '')
                    print(found_price)
                    if found_price != '' and found_price.isdigit():
                        price = found_price
                        break
            # if the price still has not been found, resize and try again
            if price == '':
                # rescale for better text detection
                scale = 5
                width = int(price_row.shape[1]*scale)
                height = int(price_row.shape[0]*scale)
                dsize = (width, height)
                price_row = cv2.resize(price_row, dsize)
                # reads the price
                price_text = pytesseract.image_to_string(price_row, config="--psm 7 digits")
                price = ''
                for found_price in price_text.split('\n'):
                    if found_price != '' and found_price != '\x0c':
                        # if the first digit got wrongly detected as 0
                        if found_price[0] == '0':
                            break
                        found_price = found_price.replace(',', '')
                        found_price = found_price.replace('.', '')
                        if found_price != '' and found_price.isdigit():
                            price = found_price
                            print(price)
                            break
            print("Found price for {}: {} k".format(name, price))
            if price == '' or name == '':
                print("ERROR! Missing data!")
                print(name)
                print(price)
            else:
                try:
                    item_list.append([name, int(price)])
                except ValueError as e:
                    print("ERROR: {}".format(e))
                    print(name)
                    print(price)
print("Finished all!")

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# finds all of the item names
name_column_hsv = img[:, :int(277*scale), :]
lh = 30
ls = 235
lv = 200
hh = 35
hs = 255
hv = 255
lower_hsv = np.array([lh, ls, lv])
higher_hsv = np.array([hh, hs, hv])
# creates binary names and reads them
name_filtered = cv2.inRange(name_column_hsv, lower_hsv, higher_hsv)
name_text = pytesseract.image_to_string(name_column_hsv)
names = []
# filter the found names
for found_name in name_text.split('\n'):
    if found_name != '' and found_name != '\x0c':
        print(found_name)
        names.append(found_name)
# filters all of the pixels of the price text

price_column = img[:, -int(136*scale):, :]
cv2.imshow("image", price_column)
price_filtered = cv2.inRange(price_column, lower_hsv, higher_hsv)
# finds all of the prices in the image
price_text = pytesseract.image_to_string(price_column, config="digits")
prices = []
for found_price in price_text.split('\n'):
    if found_price != '' and found_price != '\x0c' and found_price != ' ':
        found_price = found_price.replace(',', '')
        found_price = found_price.replace('.', '')
        print(found_price)
        prices.append(found_price)

lh = 0
ls = 0
lv = 70
hh = 255
hs = 255
hv = 255
lower_hsv = np.array([lh, ls, lv])
higher_hsv = np.array([hh, hs, hv])
price_column_hsv = hsv[:, -int(136*scale):, :]
price_column_filtered = cv2.inRange(price_column_hsv, lower_hsv, higher_hsv)
price_column = img[:, -int(136*scale):, :]
prices = []
amount_of_rows = int(img.shape[0]/int((40*scale))+1)
# iterates over the rows of items in the image
for x in range(amount_of_rows):
    name = names[x]
    # selects the row where the price is
    price_row = price_column[int(scale*(x*40)):int(scale*((x+1)*40)), :, :]
    price_row_filtered = price_column_filtered[int(scale*(x*40)):int(scale*((x+1)*40)), :]
    # selects only the area with text pixels
    rows, cols = np.nonzero(price_row_filtered)
    left = cols.min()-2
    right = cols.max()+3
    top = rows.min()-2
    bottom = rows.max()+3
    price_row = price_row[top:bottom, left:right]
    # reads the price
    price_text = pytesseract.image_to_string(price_row, config="--psm 7 digits")
    price = ''
    for found_price in price_text.split('\n'):
        if found_price != '' and found_price != '\x0c':
            # if the first digit got wrongly detected as 0
            if found_price[0] == '0':
                break
            found_price = found_price.replace(',', '')
            found_price = found_price.replace('.', '')
            price = found_price
            break
    # checks if the program missed some digits
    expected_digits = int(price_row.shape[1]/8)
    if price == '' or expected_digits > len(price):
        if expected_digits > 3:
            print("WARNING: expected digits:", expected_digits)
        # checks each digit separately
        price = ''
        for digit_counter in range(expected_digits):
            digit_img = price_row[:, -(7+3+digit_counter*8):-(1+digit_counter*8)]
            digit_text = pytesseract.image_to_string(digit_img, config="--psm 10 digits")
            for found_digit in digit_text.split('\n'):
                if found_digit != '' and found_digit != '\x0c':
                    price = found_digit + price
                    break
    print("Found price for {}:\t\t{} k".format(name, price))
    if price == '' or name == '':
        print("ERROR! Missing data!")
        print(name)
        print(price)
    else:
        try:
            item_list.append([name, int(price)])
        except ValueError as e:
            print("ERROR: {}".format(e))
            print(name)
            print(price)
print("Finished all!")
'''
