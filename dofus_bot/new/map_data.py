import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
import cv2
import keyboard
import os
import re
import random
import pickle
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


class Map:
    def __init__(self):
        self.map = np.zeros((200, 200), dtype=object)

    def read_coordinate(self, coordinates):
        x = coordinates[0] + 100
        y = coordinates[1] + 100
        return self.map[x, y]

    def edit_coordinate(self, coordinates, coordinate_object):
        x = coordinates[0] + 100
        y = coordinates[1] + 100
        self.map[x, y] = coordinate_object


class Coordinate:
    def __init__(self):
        self.resources = []
        self.north_exit = 0
        self.east_exit = 0
        self.south_exit = 0
        self.west_exit = 0


def read_coordinate():
    global coordinate_data
    coordinate_data = world_map.read_coordinate(coordinate)
    # If the coordinate hasn't been created yet
    if coordinate_data == 0:
        print('new coordinate')
        coordinate_data = Coordinate()


def update_coordinate():
    world_map.edit_coordinate(coordinate, coordinate_data)


def update_exits():
    global coordinate_data
    if north.get() == 1:
        coordinate_data.north_exit = 1
    else:
        coordinate_data.north_exit = 0
    if east.get() == 1:
        coordinate_data.east_exit = 1
    else:
        coordinate_data.east_exit = 0
    if south.get() == 1:
        coordinate_data.south_exit = 1
    else:
        coordinate_data.south_exit = 0
    if west.get() == 1:
        coordinate_data.west_exit = 1
    else:
        coordinate_data.west_exit = 0


def log(string, new_line=True):
    # Prints a string in the log of the gui
    gui_log.insert(tk.INSERT, string)
    if new_line:
        gui_log.insert(tk.INSERT, "\n")
    gui_log.see("end")


def show_info():
    north.set(coordinate_data.north_exit)
    east.set(coordinate_data.east_exit)
    south.set(coordinate_data.south_exit)
    west.set(coordinate_data.west_exit)
    map_text.delete(0, "end")
    map_text.insert(tk.INSERT, '{},{}'.format(coordinate[0], coordinate[1]))
    gui_log.delete('1.0', "end")
    log('Resources present on this coordinate:')
    for resource in coordinate_data.resources:
        log('{} at {}, {}'.format(resource[0], resource[1][0], resource[1][1]))


def change_coordinate(offset):
    global coordinate
    coordinate = [coordinate[0]+offset[0], coordinate[1]+offset[1]]


def add_resource():
    split_pos = resource_pos_input.get().split(',')
    coordinate_data.resources.append([resource_input.get(), [int(split_pos[0]), int(split_pos[1])]])
    resource_input.delete(0, "end")
    resource_pos_input.delete(0, "end")


def delete_coordinate():
    global coordinate_data
    coordinate_data = 0
    update_coordinate()


def save():
    file = open('map', "wb")
    pickle.dump(world_map, file)
    file.close()
    print('Map saved!')


def load():
    global world_map
    file = open('map', "rb")
    world_map = pickle.load(file)
    file.close()
    print('Map loaded!')


def loop():
    read_coordinate()
    update_coordinate()
    show_info()
    gui.after(10, loop)


if __name__ == '__main__':
    coordinate = [0, 0]
    coordinate_data = 0
    world_map = Map()

    # Creates the GUI
    gui = tk.Tk()
    gui.title("Map editor")

    frame_coordinate = tk.Frame(gui)
    up_button = tk.Button(frame_coordinate, text="Up", command=lambda: change_coordinate([0, -1]))
    up_button.pack()
    down_button = tk.Button(frame_coordinate, text="Down", command=lambda: change_coordinate([0, 1]))
    down_button.pack(side=tk.BOTTOM)
    left_button = tk.Button(frame_coordinate, text="Left", command=lambda: change_coordinate([-1, 0]))
    left_button.pack(side=tk.LEFT)
    map_text = tk.Entry(frame_coordinate, justify='center', width=9)
    map_text.pack(side=tk.LEFT)
    right_button = tk.Button(frame_coordinate, text="Right", command=lambda: change_coordinate([1, 0]))
    right_button.pack(side=tk.LEFT)
    frame_coordinate.pack()

    resource_text = tk.Label(gui, text="Resource type:")
    resource_input = tk.Entry(gui)
    resource_text.pack()
    resource_input.pack()

    resource_pos_text = tk.Label(gui, text="Resource position on screen: x,y")
    resource_pos_input = tk.Entry(gui)
    resource_pos_text.pack()
    resource_pos_input.pack()

    add_button = tk.Button(gui, text="Add resource", command=add_resource)
    add_button.pack()

    delete_button = tk.Button(gui, text="Delete data of this coordinate", command=delete_coordinate)
    delete_button.pack()

    save_button = tk.Button(gui, text="Save map", command=save)
    save_button.pack()

    load_button = tk.Button(gui, text="Load map", command=load)
    load_button.pack()

    north = tk.IntVar()
    east = tk.IntVar()
    south = tk.IntVar()
    west = tk.IntVar()

    north_checkbox = tk.Checkbutton(gui, text='North exit', variable=north, command=update_exits)
    north_checkbox.pack()
    east_checkbox = tk.Checkbutton(gui, text='East exit', variable=east, command=update_exits)
    east_checkbox.pack()
    south_checkbox = tk.Checkbutton(gui, text='South exit', variable=south, command=update_exits)
    south_checkbox.pack()
    west_checkbox = tk.Checkbutton(gui, text='West exit', variable=west, command=update_exits)
    west_checkbox.pack()

    gui_log = tkst.ScrolledText(gui, state=tk.NORMAL)
    gui_log.pack()

    gui.after(10, loop)
    gui.mainloop()
