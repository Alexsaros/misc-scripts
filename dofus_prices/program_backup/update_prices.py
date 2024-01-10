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


def search_list():
    status_log.delete('1.0', tk.END)
    status_log.insert(tk.INSERT, "searching")
    encyclopaedia_pos = pyautogui.locateOnScreen('encyclopaedia.png')
    if encyclopaedia_pos is not None:
        items_window = [encyclopaedia_pos[0]-172, encyclopaedia_pos[1]+139, 787, 634]
        # Click to make sure the window is in focus
        pyautogui.moveTo(items_window[0]+328, items_window[1]+21, 0.5)
        pyautogui.click()
        previous_screenshot = None
        i = 0
        finished = False
        while not finished:
            i += 1
            screenshot = pyautogui.screenshot(region=(items_window[0], items_window[1], items_window[2], items_window[3]))
            screenshot = np.array(screenshot)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            if (screenshot == previous_screenshot).all():
                finished = True
            else:
                cv2.imwrite("{}\\screenshots\\screenshot{}.png".format(os.getcwd(), i), screenshot)
                previous_screenshot = screenshot
                pyautogui.scroll(-600)
                time.sleep(0.1)
        status_log.delete('1.0', tk.END)
        status_log.insert(tk.INSERT, "finished searching")
    else:
        status_log.delete('1.0', tk.END)
        status_log.insert(tk.INSERT, "ERROR: Encyclopaedia not found!")

def search_list_runes():
    status_log.delete('1.0', tk.END)
    status_log.insert(tk.INSERT, "searching")
    encyclopaedia_pos = pyautogui.locateOnScreen('encyclopaedia.png')
    if encyclopaedia_pos is not None:
        items_window = [encyclopaedia_pos[0]-172, encyclopaedia_pos[1]+139, 787, 634]
        # Click to make sure the window is in focus
        pyautogui.moveTo(items_window[0]+328, items_window[1]+21, 0.5)
        pyautogui.click()
        previous_screenshot = None
        i = 0
        finished = False
        while not finished:
            i += 1
            screenshot = pyautogui.screenshot(region=(items_window[0], items_window[1], items_window[2], items_window[3]))
            screenshot = np.array(screenshot)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            if (screenshot == previous_screenshot).all():
                finished = True
            else:
                cv2.imwrite("{}\\screenshots_runes\\screenshot{}.png".format(os.getcwd(), i), screenshot)
                previous_screenshot = screenshot
                pyautogui.scroll(-600)
                time.sleep(0.1)
        status_log.delete('1.0', tk.END)
        status_log.insert(tk.INSERT, "finished searching")
    else:
        status_log.delete('1.0', tk.END)
        status_log.insert(tk.INSERT, "ERROR: Encyclopaedia not found!")


def read_data():
    status_log.delete('1.0', tk.END)
    status_log.insert(tk.INSERT, "reading")
    item_list = []
    i = 0
    while True:
        i += 1
        img = cv2.imread("{}\\screenshots\\screenshot{}.png".format(os.getcwd(), i))
        if img is None:
            break
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        name_column = hsv[:, :277, :]
        lh = 30
        ls = 235
        lv = 200
        hh = 35
        hs = 255
        hv = 255
        lower_hsv = np.array([lh, ls, lv])
        higher_hsv = np.array([hh, hs, hv])
        name_filtered = cv2.inRange(name_column, lower_hsv, higher_hsv)
        # finds all of the names in the image
        name_text = pytesseract.image_to_string(name_filtered)
        names = []
        for found_name in name_text.split('\n'):
            if found_name != '' and found_name != '\x0c':
                if found_name[:3] == "Cha":
                    print(found_name)
                names.append(found_name)
        price_column = hsv[:, -136:, :]
        lh = 0
        ls = 0
        lv = 140
        hh = 60
        hs = 10
        hv = 255
        lower_hsv = np.array([lh, ls, lv])
        higher_hsv = np.array([hh, hs, hv])
        price_filtered = cv2.inRange(price_column, lower_hsv, higher_hsv)
        # finds all of the prices in the image
        price_text = pytesseract.image_to_string(price_filtered, config="digits")
        prices = []
        for found_price in price_text.split('\n'):
            if found_price != '' and found_price != '\x0c' and found_price != ' ':
                found_price = found_price.replace(',', '')
                found_price = found_price.replace('.', '')
                prices.append(found_price)
        # if nothing went wrong with detecting the prices
        if len(names) == len(prices):
            for x in range(len(names)):
                item_list.append([names[x], int(prices[x])])
        else:   # else go through the image row by row
            amount_of_rows = int(img.shape[0]/40)+1
            # iterates over the rows of items in the image
            for x in range(amount_of_rows):
                name_row = name_filtered[x*40:(x+1)*40, :]
                name_text = pytesseract.image_to_string(name_row)
                name = ''
                for found_name in name_text.split('\n'):
                    if found_name != '' and found_name != '\x0c':
                        name = found_name
                        break
                price_row = price_filtered[x*40:(x+1)*40, :]
                price_text = pytesseract.image_to_string(price_row, config="digits")
                price = ''
                for found_price in price_text.split('\n'):
                    if found_price != '' and found_price != '\x0c':
                        found_price = found_price.replace(',', '')
                        found_price = found_price.replace('.', '')
                        price = found_price
                        break
                # if it's a single digit price and has therefore not been found:
                if price == '':
                    price_text = pytesseract.image_to_string(price_row, config="--psm 10 digits")
                    for found_price in price_text.split('\n'):
                        if found_price != '' and found_price != '\x0c' and found_price != ' ':
                            found_price = found_price.replace(',', '')
                            found_price = found_price.replace('.', '')
                            price = found_price
                            break
                # if it still hasn't been found, check the last 3 digits separately
                if price == '':
                    first_digit_image = price_row[:, -15:-6]
                    first_digit_text = pytesseract.image_to_string(first_digit_image, config="--psm 10 digits")
                    second_digit_image = price_row[:, -23:-14]
                    second_digit_text = pytesseract.image_to_string(second_digit_image, config="--psm 10 digits")
                    third_digit_image = price_row[:, -30:-22]
                    third_digit_text = pytesseract.image_to_string(third_digit_image, config="--psm 10 digits")
                    first_digit = ''
                    second_digit = ''
                    third_digit = ''
                    for digit_value in first_digit_text.split('\n'):
                        if digit_value != '' and digit_value != '\x0c' and digit_value != ' ':
                            digit_value = digit_value.replace(',', '')
                            digit_value = digit_value.replace('.', '')
                            first_digit = digit_value
                            break
                    for digit_value in second_digit_text.split('\n'):
                        if digit_value != '' and digit_value != '\x0c' and digit_value != ' ':
                            digit_value = digit_value.replace(',', '')
                            digit_value = digit_value.replace('.', '')
                            second_digit = digit_value
                            break
                    for digit_value in third_digit_text.split('\n'):
                        if digit_value != '' and digit_value != '\x0c' and digit_value != ' ':
                            digit_value = digit_value.replace(',', '')
                            digit_value = digit_value.replace('.', '')
                            third_digit = digit_value
                            break
                    if third_digit != '' and second_digit != '' and first_digit != '':
                        price = "{}{}{}".format(third_digit, second_digit, first_digit)
                        print("WARNING: item with 3 digit price!")
                        print(name)
                        print(price)
                    elif second_digit != '' and first_digit != '':
                        price = "{}{}".format(second_digit, first_digit)
                    elif first_digit != '':
                        price = "{}".format(first_digit)
                    #print("Found price for {}: {} k".format(name, price))
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
        print("Finished {}".format(i))
    with open("item_prices.pickle", 'wb') as f:
        pickle.dump(item_list, f)
    print("Finished all!")
    status_log.delete('1.0', tk.END)
    status_log.insert(tk.INSERT, "finished reading data")

def read_data_runes():
    status_log.delete('1.0', tk.END)
    status_log.insert(tk.INSERT, "reading")
    item_list = []
    i = 0
    while True:
        i += 1
        img = cv2.imread("{}\\screenshots_runes\\screenshot{}.png".format(os.getcwd(), i))
        if img is None:
            break
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        name_column = hsv[:, :277, :]
        lh = 30
        ls = 235
        lv = 200
        hh = 35
        hs = 255
        hv = 255
        lower_hsv = np.array([lh, ls, lv])
        higher_hsv = np.array([hh, hs, hv])
        name_filtered = cv2.inRange(name_column, lower_hsv, higher_hsv)
        # finds all of the names in the image
        name_text = pytesseract.image_to_string(name_filtered)
        names = []
        for found_name in name_text.split('\n'):
            if found_name != '' and found_name != '\x0c':
                names.append(found_name)
        price_column = hsv[:, -136:, :]
        lh = 0
        ls = 0
        lv = 140
        hh = 60
        hs = 10
        hv = 255
        lower_hsv = np.array([lh, ls, lv])
        higher_hsv = np.array([hh, hs, hv])
        price_filtered = cv2.inRange(price_column, lower_hsv, higher_hsv)
        # finds all of the prices in the image
        price_text = pytesseract.image_to_string(price_filtered, config="digits")
        prices = []
        for found_price in price_text.split('\n'):
            if found_price != '' and found_price != '\x0c' and found_price != ' ':
                found_price = found_price.replace(',', '')
                found_price = found_price.replace('.', '')
                prices.append(found_price)
        # if nothing went wrong with detecting the prices
        if len(names) == len(prices):
            for x in range(len(names)):
                item_list.append([names[x], int(prices[x])])
        else:   # else go through the image row by row
            amount_of_rows = int(img.shape[0]/40)+1
            # iterates over the rows of items in the image
            for x in range(amount_of_rows):
                name_row = name_filtered[x*40:(x+1)*40, :]
                name_text = pytesseract.image_to_string(name_row)
                name = ''
                for found_name in name_text.split('\n'):
                    if found_name != '' and found_name != '\x0c':
                        name = found_name
                        break
                price_row = price_filtered[x*40:(x+1)*40, :]
                price_text = pytesseract.image_to_string(price_row, config="digits")
                price = ''
                for found_price in price_text.split('\n'):
                    if found_price != '' and found_price != '\x0c':
                        found_price = found_price.replace(',', '')
                        found_price = found_price.replace('.', '')
                        price = found_price
                        break
                # if it's a single digit price and has therefore not been found:
                if price == '':
                    price_text = pytesseract.image_to_string(price_row, config="--psm 10 digits")
                    for found_price in price_text.split('\n'):
                        if found_price != '' and found_price != '\x0c' and found_price != ' ':
                            found_price = found_price.replace(',', '')
                            found_price = found_price.replace('.', '')
                            price = found_price
                            break
                # if it still hasn't been found, check the last 3 digits separately
                if price == '':
                    first_digit_image = price_row[:, -15:-6]
                    first_digit_text = pytesseract.image_to_string(first_digit_image, config="--psm 10 digits")
                    second_digit_image = price_row[:, -23:-14]
                    second_digit_text = pytesseract.image_to_string(second_digit_image, config="--psm 10 digits")
                    third_digit_image = price_row[:, -30:-22]
                    third_digit_text = pytesseract.image_to_string(third_digit_image, config="--psm 10 digits")
                    first_digit = ''
                    second_digit = ''
                    third_digit = ''
                    for digit_value in first_digit_text.split('\n'):
                        if digit_value != '' and digit_value != '\x0c' and digit_value != ' ':
                            digit_value = digit_value.replace(',', '')
                            digit_value = digit_value.replace('.', '')
                            first_digit = digit_value
                            break
                    for digit_value in second_digit_text.split('\n'):
                        if digit_value != '' and digit_value != '\x0c' and digit_value != ' ':
                            digit_value = digit_value.replace(',', '')
                            digit_value = digit_value.replace('.', '')
                            second_digit = digit_value
                            break
                    for digit_value in third_digit_text.split('\n'):
                        if digit_value != '' and digit_value != '\x0c' and digit_value != ' ':
                            digit_value = digit_value.replace(',', '')
                            digit_value = digit_value.replace('.', '')
                            third_digit = digit_value
                            break
                    if third_digit != '' and second_digit != '' and first_digit != '':
                        price = "{}{}{}".format(third_digit, second_digit, first_digit)
                        print("WARNING: item with 3 digit price!")
                        print(name)
                        print(price)
                    elif second_digit != '' and first_digit != '':
                        price = "{}{}".format(second_digit, first_digit)
                    elif first_digit != '':
                        price = "{}".format(first_digit)
                    #print("Found price for {}: {} k".format(name, price))
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
        print("Finished {}".format(i))
    with open("rune_prices.pickle", 'wb') as f:
        pickle.dump(item_list, f)
    print("Finished all!")
    status_log.delete('1.0', tk.END)
    status_log.insert(tk.INSERT, "finished reading data")


# Creates the GUI
gui = tk.Tk()
gui.title("Dofus price reader")

search_ingredients_button = tk.Button(gui, text='Search list', command=search_list)
search_ingredients_button.grid(row = 0, column = 0)

read_data_button = tk.Button(gui, text='Read data', command=read_data)
read_data_button.grid(row = 0, column = 1)

search_ingredients_button = tk.Button(gui, text='Search rune list', command=search_list_runes)
search_ingredients_button.grid(row = 0, column = 2)

read_rune_data_button = tk.Button(gui, text='Read rune data', command=read_data_runes)
read_rune_data_button.grid(row = 0, column = 3)

status_text = tk.Label(gui, text="Status")
status_log = tkst.ScrolledText(gui, height=53, width=50)
status_text.grid(row = 1, column = 0)
status_log.grid(row = 2, column = 0, sticky=tk.N+tk.S+tk.E+tk.W)

ingredient_price_text = tk.Label(gui, text="Prices")
ingredient_price_log = tkst.ScrolledText(gui, height=53, width=50)
ingredient_price_text.grid(row = 1, column = 1)
ingredient_price_log.grid(row = 2, column = 1, sticky=tk.N+tk.S+tk.E+tk.W)

tk.Grid.columnconfigure(gui, 2, weight=1)
tk.Grid.rowconfigure(gui, 2, weight=1)


status_log.delete('1.0', tk.END)
status_log.insert(tk.INSERT, "idle")

gui.mainloop()
