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


def read_data(item_type=""):
    status_log.delete('1.0', tk.END)
    status_log.insert(tk.INSERT, "reading")
    item_list = []
    i = 0
    while True:
        i += 1
        if item_type == "runes":
            img = cv2.imread("{}\\screenshots_runes\\screenshot{}.png".format(os.getcwd(), i))
        else:
            img = cv2.imread("{}\\screenshots\\screenshot{}.png".format(os.getcwd(), i))
        if img is None:
            break
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
                if found_price != '':
                    prices.append(found_price)
        # checks if prices have been missed
        if len(names) == len(prices):
            for x in range(len(names)):
                item_list.append([names[x], int(prices[x])])
        elif len(names) < len(prices):
            print("ERROR: missed names,", len(names), len(prices))
        else:
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
                name = names[x]
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
                                break
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
    if item_type == "runes":
        with open("rune_prices.pickle", 'wb') as f:
            pickle.dump(item_list, f)
    else:
        with open("item_prices.pickle", 'wb') as f:
            pickle.dump(item_list, f)
    print("Finished all!")
    status_log.delete('1.0', tk.END)
    status_log.insert(tk.INSERT, "finished reading data")
    ingredient_price_log.delete('1.0', tk.END)
    for item in item_list:
        ingredient_price_log.insert(tk.INSERT, "{}:\t\t{}\n".format(item[0], item[1])) 

def read_data_runes():
    read_data(item_type="runes")


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
