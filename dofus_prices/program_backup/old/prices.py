import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
import cv2
import pickle
import pytesseract
import pyautogui
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

rune_names = {
    "Ap Ga": "ap",
    "Mp Ga": "mp",
    "Range": "range",
    "Summo": "summons",
    "Dam": "damage",
    "Me Dam Per": "melee_damage",
    "Me Res Per": "melee_resistance",
    "Ra Dam Per": "ranged_damage",
    "Ra Res Per": "ranged_resistance",
    "Spe Dam Per": "spell_damage",
    "We Dam Per": "weapon_damage",
    "Cri": "critical",
    "Hea": "heals",
    "Dam Ref": "reflect",
    "Ap Red": "ap_reduction",
    "Mp Red": "mp_reduction",
    "Ap Res": "ap_parry",
    "Mp Res": "mp_parry",
    "Neutral Res Per": "neutral_resistance_percentage",
    "Earth Res Per": "earth_resistance_percentage",
    "Fire Res Per": "fire_resistance_percentage",
    "Water Res Per": "water_resistance_percentage",
    "Air Res Per": "air_resistance_percentage",
    "Hunting": "hunting_weapon",
    "Neutral Dam": "neutral_damage",
    "Earth Dam": "earth_damage",
    "Fire Dam": "fire_damage",
    "Water Dam": "water_damage",
    "Air Dam": "air_damage",
    "Cri Dam": "critical_damage",
    "Psh Dam": "pushback_damage",
    "Tra": "traps_damage",
    "Loc": "lock",
    "Dod": "dodge",
    "Prospe": "prospecting",
    "Wis": "wisdom",
    "Pow": "power",
    "Tra Per": "traps_power",
    "Neutral Res": "neutral_resistance",
    "Earth Res": "earth_resistance",
    "Fire Res": "fire_resistance",
    "Water Res": "water_resistance",
    "Air Res": "air_resistance",
    "Cri Res": "critical_resistance",
    "Psh Res": "pushback_resistance",
    "Stre": "strength",
    "Int": "intelligence",
    "Cha": "chance",
    "Agi": "agility",
    "Pod": "pods",
    "Vit": "vitality",
    "Ini": "initiative"
}

rune_sink = {
    "ap": 100,
    "mp": 90,
    "range": 51,
    "summons": 30,
    "damage": 20,
    "melee_damage": 15,
    "melee_resistance": 15,
    "ranged_damage": 15,
    "ranged_resistance": 15,
    "spell_damage": 15,
    "weapon_damage": 15,
    "critical": 10,
    "heals": 10,
    "reflect": 10,
    "ap_reduction": 7,
    "mp_reduction": 7,
    "ap_parry": 7,
    "mp_parry": 7,
    "neutral_resistance_percentage": 6,
    "earth_resistance_percentage": 6,
    "fire_resistance_percentage": 6,
    "water_resistance_percentage": 6,
    "air_resistance_percentage": 6,
    "hunting_weapon": 5,
    "neutral_damage": 5,
    "earth_damage": 5,
    "fire_damage": 5,
    "water_damage": 5,
    "air_damage": 5,
    "critical_damage": 5,
    "pushback_damage": 5,
    "traps_damage": 5,
    "lock": 4,
    "dodge": 4,
    "prospecting": 3,
    "wisdom": 3,
    "power": 2,
    "traps_power": 2,
    "neutral_resistance": 2,
    "earth_resistance": 2,
    "fire_resistance": 2,
    "water_resistance": 2,
    "air_resistance": 2,
    "critical_resistance": 2,
    "pushback_resistance": 2,
    "strength": 1,
    "intelligence": 1,
    "chance": 1,
    "agility": 1,
    "pods": 0.25,
    "vitality": 0.2,
    "initiative": 0.1
}

rune_prices = {
    "ap": 0,
    "mp": 0,
    "range": 0,
    "summons": 0,
    "damage": 0,
    "melee_damage": 0,
    "melee_resistance": 0,
    "ranged_damage": 0,
    "ranged_resistance": 0,
    "spell_damage": 0,
    "weapon_damage": 0,
    "critical": 0,
    "heals": 0,
    "reflect": 0,
    "ap_reduction": 0,
    "mp_reduction": 0,
    "ap_parry": 0,
    "mp_parry": 0,
    "neutral_resistance_percentage": 0,
    "earth_resistance_percentage": 0,
    "fire_resistance_percentage": 0,
    "water_resistance_percentage": 0,
    "air_resistance_percentage": 0,
    "hunting_weapon": 0,
    "neutral_damage": 0,
    "earth_damage": 0,
    "fire_damage": 0,
    "water_damage": 0,
    "air_damage": 0,
    "critical_damage": 0,
    "pushback_damage": 0,
    "traps_damage": 0,
    "lock": 0,
    "dodge": 0,
    "prospecting": 0,
    "wisdom": 0,
    "power": 0,
    "traps_power": 0,
    "neutral_resistance": 0,
    "earth_resistance": 0,
    "fire_resistance": 0,
    "water_resistance": 0,
    "air_resistance": 0,
    "critical_resistance": 0,
    "pushback_resistance": 0,
    "strength": 0,
    "intelligence": 0,
    "chance": 0,
    "agility": 0,
    "pods": 0,
    "vitality": 0,
    "initiative": 0
}


def print_prices():
    rune_price_log.delete('1.0', tk.END)
    for rune in rune_prices:
        rune_price_log.insert(tk.INSERT, "{}:\t\t{}\n".format(rune, rune_prices[rune]))    


def read_text(image):
    # Filters the white text
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lh = 0
    ls = 0
    lv = 140
    hh = 60
    hs = 10
    hv = 255
    lower_hsv = np.array([lh, ls, lv])
    higher_hsv = np.array([hh, hs, hv])
    image_binary = cv2.inRange(image_hsv, lower_hsv, higher_hsv)
    # Reads the text
    text = pytesseract.image_to_string(image_binary)
    # Looks for the rune name
    rune_index = text.find(" Rune")
    if rune_index != -1:
        rune_name = text[:rune_index]
        rune = rune_names[rune_name]
        # Looks for the rune price
        price_index = text.find("price")
        if price_index != -1:
            kamas_index = text.find(" k", price_index)
            if kamas_index == -1:
                kamas_index = text.find("k", price_index)
            if kamas_index != -1:
                rune_price = text[price_index+6:kamas_index]
                rune_price = rune_price.replace(',', '')
                rune_prices[rune] = rune_price
                with open("rune_prices.pickle", 'wb') as f:
                    pickle.dump(rune_prices, f)

def loop():
    screenshot = pyautogui.screenshot(region=(705, 223, 861, 418))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    if read_text_bool.get() == 1:
        read_text(screenshot)
    print_prices()
    gui.after(100, loop)

# Read saved data
try:
    with open("rune_prices.pickle", 'rb') as f:
        rune_prices = pickle.load(f)
except FileNotFoundError as e:
    pass


# Creates the GUI
gui = tk.Tk()
gui.title("Dofus rune price calculator")

read_text_bool = tk.IntVar()
read_text_checkbox = tk.Checkbutton(gui, text='Read text', variable=read_text_bool)
read_text_checkbox.grid(row = 0, column = 0)

rune_price_text = tk.Label(gui, text="Rune prices")
rune_price_log = tkst.ScrolledText(gui, height=53, width=50)
rune_price_text.grid(row = 1, column = 0)
rune_price_log.grid(row = 2, column = 0, sticky=tk.N+tk.S+tk.E+tk.W)

ingredient_price_text = tk.Label(gui, text="Ingredient prices")
ingredient_price_log = tkst.ScrolledText(gui, height=53, width=50)
ingredient_price_text.grid(row = 1, column = 1)
ingredient_price_log.grid(row = 2, column = 1, sticky=tk.N+tk.S+tk.E+tk.W)

item_profit_text = tk.Label(gui, text="Item profits")
item_profit_log = tkst.ScrolledText(gui, height=53, width=50)
item_profit_text.grid(row = 1, column = 2)
item_profit_log.grid(row = 2, column = 2, sticky=tk.N+tk.S+tk.E+tk.W)

tk.Grid.columnconfigure(gui, 2, weight=1)
tk.Grid.rowconfigure(gui, 2, weight=1)

gui.after(100, loop)
gui.mainloop()
