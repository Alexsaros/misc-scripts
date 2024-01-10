import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
import cv2
import pickle
import pytesseract
import pyautogui
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


class Item:
    ingredients = []
    stats = []
    
    def __init__(self, name):
        self.name = name

    def add_ingredient(self, amount, ingredient_name):
        self.ingredients.append([amount, ingredient_name])

    def add_stat(self, amount, stat_name):
        self.stats.append([amount, stat_name])

    def clear_ingredients(self):
        self.ingredients = []

    def clear_stats(self):
        self.stats = []


def load_item():
    item_stats_log.delete('1.0', tk.END)
    ingredients_log.delete('1.0', tk.END)
    requested_item = item_name.get('1.0', tk.END)
    item_match = False
    for item in item_data:
        if item.name == requested_item:
            item_match = True
            for stat in item.stats:
                item_stats_log.insert(tk.INSERT, "{} {}\n".format(stat[0], stat[1]))
            for ingredient in item.ingredients:
                ingredients_log.insert(tk.INSERT, "{} {}\n".format(ingredient[0], ingredient[1]))
            break
    if not item_match:
        item_name.delete('1.0', tk.END)
        item_name.insert(tk.END, "NOT FOUND")


def save_item():
    current_item_name = item_name.get('1.0', tk.END)
    # Checks if the item has been saved before
    new_item = True
    for item in item_data:
        if item.name == current_item_name:
            new_item = False
            current_item = item
            item_data.remove(item)
            break
    if new_item:
        current_item = Item(current_item_name)
    current_item.clear_ingredients()
    current_item.clear_stats()
    item_stats_list = item_stats_log.get('1.0', tk.END)
    # Splits each line
    item_stats = item_stats_list.split('\n')
    for stat in item_stats:
        if stat != '':
            # Splits each number/word
            split = stat.split(' ')
            amount = split.pop(0)
            complete_stat_name = split.pop(0)
            for word in split:
                complete_stat_name += " {}".format(word)
            current_item.add_stat(amount, complete_stat_name)
    ingredients_list = ingredients_log.get('1.0', tk.END)
    # Splits each line
    ingredients = ingredients_list.split('\n')
    for ingredient in ingredients:
        if ingredient != '':
            # Splits each number/word
            split = ingredient.split(' ')
            amount = split.pop(0)
            complete_ingredient_name = split.pop(0)
            for word in split:
                complete_ingredient_name += " {}".format(word)
            current_item.add_ingredient(amount, complete_ingredient_name)
    # Checks if the inputted data is empty
    if not (current_item.ingredients == [] and current_item.stats == []):
        item_data.append(current_item)
    with open("recipes.pickle", 'wb') as f:
        pickle.dump(item_data, f)
    item_name.delete('1.0', tk.END)
    item_stats_log.delete('1.0', tk.END)
    ingredients_log.delete('1.0', tk.END)
    print_data()


def main():
    pass

if __name__ == "__main__":

    def print_data():
        saved_items_log.delete('1.0', tk.END)
        for item in reversed(item_data):
            saved_items_log.insert(tk.INSERT, "{}".format(item.name))


    # Read saved data
    item_data = []
    try:
        with open("recipes.pickle", 'rb') as f:
            item_data = pickle.load(f)
    except FileNotFoundError as e:
        pass


    # Creates the GUI
    gui = tk.Tk()
    gui.title("Dofus item editor")

    item_name = tk.Text(gui, height = 1, width = 30)
    item_name.grid(row = 0, column = 0)

    load_item = tk.Button(gui, text='Load item info', command=load_item)
    load_item.grid(row = 0, column = 1)

    save_item = tk.Button(gui, text='Save item info', command=save_item)
    save_item.grid(row = 0, column = 2)

    saved_items_text = tk.Label(gui, text="Saved items")
    saved_items_log = tkst.ScrolledText(gui, height=53, width=50)
    saved_items_text.grid(row = 1, column = 0)
    saved_items_log.grid(row = 2, column = 0, sticky=tk.N+tk.S+tk.E+tk.W)

    item_stats_text = tk.Label(gui, text="Item stats")
    item_stats_log = tkst.ScrolledText(gui, height=53, width=50)
    item_stats_text.grid(row = 1, column = 1)
    item_stats_log.grid(row = 2, column = 1, sticky=tk.N+tk.S+tk.E+tk.W)

    ingredients_text = tk.Label(gui, text="Item profits")
    ingredients_log = tkst.ScrolledText(gui, height=53, width=50)
    ingredients_text.grid(row = 1, column = 2)
    ingredients_log.grid(row = 2, column = 2, sticky=tk.N+tk.S+tk.E+tk.W)

    tk.Grid.columnconfigure(gui, 2, weight=1)
    tk.Grid.rowconfigure(gui, 2, weight=1)

    print_data()

    gui.mainloop()

