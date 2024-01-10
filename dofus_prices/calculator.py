import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
import cv2
import pickle
import pytesseract
import pyautogui
import re
import time
from recipes import Item
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

rune_names = {
    "ap ga": "ap",
    "mp ga": "mp",
    "range": "range",
    "summo": "summons",
    "dam": "damage",
    "me dam per": "melee_damage",
    "me res per": "melee_resistance",
    "ra dam per": "ranged_damage",
    "ra res per": "ranged_resistance",
    "spe dam per": "spell_damage",
    "we dam per": "weapon_damage",
    "cri": "critical",
    "hea": "heals",
    "dam ref": "reflect",
    "ap red": "ap_reduction",
    "mp red": "mp_reduction",
    "ap res": "ap_parry",
    "mp res": "mp_parry",
    "neutral res per": "neutral_resistance_percentage",
    "earth res per": "earth_resistance_percentage",
    "fire res per": "fire_resistance_percentage",
    "water res per": "water_resistance_percentage",
    "air res per": "air_resistance_percentage",
    "hunting": "hunting_weapon",
    "neutral dam": "neutral_damage",
    "earth dam": "earth_damage",
    "fire dam": "fire_damage",
    "water dam": "water_damage",
    "air dam": "air_damage",
    "cri dam": "critical_damage",
    "psh dam": "pushback_damage",
    "tra": "traps_damage",
    "loc": "lock",
    "dod": "dodge",
    "prospe": "prospecting",
    "wis": "wisdom",
    "pow": "power",
    "tra per": "traps_power",
    "neutral res": "neutral_resistance",
    "earth res": "earth_resistance",
    "fire res": "fire_resistance",
    "water res": "water_resistance",
    "air res": "air_resistance",
    "cri res": "critical_resistance",
    "psh res": "pushback_resistance",
    "stre": "strength",
    "int": "intelligence",
    "cha": "chance",
    "agi": "agility",
    "pod": "pods",
    "vit": "vitality",
    "ini": "initiative"
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
   

def load_rune_prices():
    with open("rune_prices.pickle", 'rb') as f:
        rune_prices_temp = pickle.load(f)
    for rune in rune_prices_temp:
        # removes everything that isn't a letter or space
        rune_name = rune[0].lower()
        rune_name = re.sub(r'[^a-z ]+', '', rune_name)
        rune_name = rune_name[:-5]  # removes the rune part of the name
        # sets rune prices
        if rune_name in rune_names:
            if rune_names[rune_name] == "pods" or rune_names[rune_name] == "initiative":
                rune_prices[rune_names[rune_name]] = rune[1]/10
            elif rune_names[rune_name] == "vitality":
                rune_prices[rune_names[rune_name]] = rune[1]/5
            else:
                rune_prices[rune_names[rune_name]] = rune[1]
    rune_price_log.delete('1.0', tk.END)
    for rune in rune_prices:
        rune_price_log.insert(tk.INSERT, "{}:\t\t{}\n".format(rune, rune_prices[rune])) 


def load_ingredient_data():
    global item_prices
    item_prices = []
    with open("item_prices.pickle", 'rb') as f:
        item_prices_temp = pickle.load(f)
    for item in item_prices_temp:
        # removes everything that isn't a letter or space
        item_name = item[0].lower()
        item_name = re.sub(r'[^a-z ]+', '', item_name)
        # checks if the item is not a rune
        if item_name[-4:] != "rune":
            # check if item is a duplicate of last item
            if len(item_prices) == 0 or [item_name, item[1]] != item_prices[-1]:
                item_prices.append([item_name, item[1]])
    ingredient_price_log.delete('1.0', tk.END)
    for item in item_prices:
        ingredient_price_log.insert(tk.INSERT, "{}:\t\t{}\n".format(item[0], item[1])) 


def load_recipe_data():
    global recipes, item_profits
    recipes = []
    item_profits = []
    with open("recipes.pickle", 'rb') as f:
        recipes = pickle.load(f)
    for recipe in recipes:
        recipe_error = False
        ingredient_list = []
        total_cost = 0
        for ingredient in recipe.ingredients:
            ingredient_list.append([ingredient[0], ingredient[1]])
            # searches the saved item data for the ingredient and price
            ingredient_found = False
            for item in item_prices:
                if item[0] == ingredient[1]:
                    # ingredient cost*amount
                    if recipe.name[:5] == "pushn":
                        print(item[1], ingredient[0], ingredient[1], float(item[1])*float(ingredient[0]))
                    total_cost += float(item[1])*float(ingredient[0])
                    ingredient_found = True
                    break
            if not ingredient_found:
                recipe_error = True
                print("WARNING: unable to find ingredient {} for {}".format(ingredient, recipe.name))
        total_sink = 0
        regular_profits = 0
        try:
            # calculates profits without focus
            for stat in recipe.stats:
                total_sink += float(stat[0])*rune_sink[stat[1]]
                regular_profits += float(stat[0])*rune_prices[stat[1]]*0.50 # assumes runes drop 50% of the time
            best_profits = ["no_focus", regular_profits]
            # calculates profits with focus
            for stat in recipe.stats:
                focus_sink = total_sink*0.5+float(stat[0])*rune_sink[stat[1]]*0.5
                profit = (focus_sink/rune_sink[stat[1]])*rune_prices[stat[1]]*0.50  # assumes runes drop 50% of the time
                if profit > best_profits[1]:
                    best_profits = [stat[1], profit]
            best_profits = [best_profits[0], best_profits[1]*0.10]  # profit assuming a 10% rune modifier
            profit_percentage = best_profits[1]/total_cost
        except KeyError as e:
            recipe_error = True
            print("WARNING: {} for {}".format(e, recipe.name))
        if not recipe_error:
            item_profits.append([recipe.name, best_profits[0], profit_percentage, total_cost, best_profits[1]-total_cost, ingredient_list])
    item_profits.sort(key=lambda x: x[4], reverse=True)
    for item in item_profits:
        item_profit_log.insert(tk.INSERT, "{} using {}: {}\n cost: {}\t\tprofit: {}\n".format(item[0], item[1], item[2], int(item[3]), int(item[4])))
        for ingredient in item[5]:
            item_profit_log.insert(tk.INSERT, " {} {}\n".format(ingredient[0], ingredient[1]))


item_prices = []
recipes = []
item_profits = []

# Creates the GUI
gui = tk.Tk()
gui.title("Dofus rune price calculator")

load_runes_button = tk.Button(gui, text='Load rune prices', command=load_rune_prices)
load_runes_button.grid(row = 0, column = 0)

load_ingredients_button = tk.Button(gui, text='Load ingredient data', command=load_ingredient_data)
load_ingredients_button.grid(row = 0, column = 1)

load_recipes_button = tk.Button(gui, text='Load recipe data', command=load_recipe_data)
load_recipes_button.grid(row = 0, column = 2)

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

gui.mainloop()
