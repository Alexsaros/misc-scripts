import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image


def log(string, new_line=True):
    gui_log.config(state=tk.NORMAL)
    gui_log.insert(tk.INSERT, string)
    if new_line:
        gui_log.insert(tk.INSERT, "\n")
    gui_log.config(state=tk.DISABLED)
    gui_log.see("end")

def calibrate():
    global game_region, current_coordinates, current_path
    buttons_pos = pyautogui.locateCenterOnScreen('menu_buttons.png', confidence=confidence)
    if buttons_pos is not None:
        game_region = (buttons_pos[0]-826, 23, 1001, pyautogui.size()[1]-63)
        coordinates = coordinates_input.get()
        if coordinates != "" and "," in coordinates:
            split_coordinates = coordinates.split(',')
            current_coordinates = [int(split_coordinates[0]),int(split_coordinates[1])]
            current_path = []
            for direction in path_input.get():
                current_path.append(direction)
            log("Calibration succesful.")
        else:
            game_region = (0,0,0,0)
            log("Calibration failed! Invalid coordinates.")
    else:
        game_region = (0,0,0,0)
        log("Calibration failed! Menu buttons not visible.")

def update_gui():
    coordinates_input.delete(0, "end")
    coordinates_input.insert(0, "{},{}".format(current_coordinates[0], current_coordinates[1]))

def click_cursor_on(pos):
    cursor_pos = pyautogui.position()
    distance = np.sqrt((cursor_pos[0]-pos[0])**2 + (cursor_pos[1]-pos[1])**2)
    pyautogui.moveTo(pos[0], pos[1], distance/pixels_per_second, pyautogui.easeOutQuad)
    percentage = np.random.randint(0,100)/100
    time.sleep(delay*percentage)
    pyautogui.click()
    time.sleep(delay*(1-percentage))

def farm_cereal_on_screen(cereal_type):
    cereal_img = Image.open('{}.png'.format(cereal_type))
    cereal = pyautogui.locateAllOnScreen(cereal_img, region=game_region, confidence=confidence)
    cereal_pos = []
    last_pos = (0, 0)
    # makes sure one resource doesn't get detected multiple times
    for match in cereal:
        if abs(last_pos[0]-match[0]) >= accuracy and abs(last_pos[1]-match[1]) >= accuracy:
            last_pos = (match[0], match[1])
            cereal_pos.append(last_pos)
    first_click = True
    for pos in cereal_pos:
        # selects random position on resources
        x_offset = np.random.randint(-1*offset,offset)
        y_offset = np.random.randint(-1*offset,offset)
        x_pos = pos[0]+int(cereal_img.size[0]/2)+x_offset
        y_pos = pos[1]+int(cereal_img.size[1]/2)+y_offset
        # makes sure you don't leave the map
        if x_pos < game_region[0]+30:
            x_pos = game_region[0]+30
        elif x_pos > game_region[0]+game_region[2]-30:
            x_pos = game_region[0]+game_region[2]-30
        if y_pos < game_region[1]+14:
            y_pos = game_region[1]+14
        elif y_pos > game_region[1]+game_region[3]-108:
            y_pos = game_region[1]+game_region[3]-108
        # moves cursor to resource and clicks
        click_cursor_on([x_pos, y_pos])
        # waits until first resource is reached
        if first_click:
            first_click = False
            first_cereal = pyautogui.screenshot(region=(pos[0],pos[1],10,10))
            first_cereal_pos = 1
            start_time = time.time()
            while first_cereal_pos is not None:
                first_cereal_pos = pyautogui.locateOnScreen(first_cereal)
                if time.time()-start_time >= max_wait_time:
                    break
        if pos == cereal_pos[-1]:
            final_cereal = pyautogui.screenshot(region=(pos[0],pos[1],10,10))
    
    if len(cereal_pos) > 0:
        # waits until finished gathering all resources
        final_cereal_pos = 1
        start_time = time.time()
        while final_cereal_pos is not None:
            final_cereal_pos = pyautogui.locateOnScreen(final_cereal)
            if time.time()-start_time >= max_wait_time-resource_time:
                break
        time.sleep(resource_time)
        # checks if still cereal left on screen
        cereal = pyautogui.locateAllOnScreen(cereal_img, region=game_region, confidence=confidence)
        for check in cereal:
            farm_cereal_on_screen(cereal_type)  # runs function again
            break   # just once

def farm_cereal():
    if game_region == (0,0,0,0):
        log("Bot has not been calibrated.")
    else:
        try:
            farm_cereal_on_screen(cereal_type_input.get())
            log("Finished farming.")
            follow_path()
        except OSError:
            log("Invalid cereal type.")

def follow_path():
    global current_coordinates
    if current_path != []:
        direction = current_path.pop(0)
        current_path.append(direction)  # TODO
        if direction == 'l':
            x_pos = game_region[0]+np.random.randint(0, 23)
            y_pos = np.random.randint(game_region[1], game_region[1]+(game_region[3])-108)
            click_cursor_on([x_pos, y_pos])
            current_coordinates = [current_coordinates[0]-1,current_coordinates[1]]
        elif direction == 'r':
            x_pos = game_region[0]+np.random.randint(0, 23)
            y_pos = np.random.randint(game_region[1], game_region[1]+(game_region[3])-108)
            click_cursor_on([x_pos, y_pos])
            current_coordinates = [current_coordinates[0]+1,current_coordinates[1]]
        elif direction == 'u':
            x_pos = game_region[0]+np.random.randint(0, 23)
            y_pos = np.random.randint(game_region[1], game_region[1]+(game_region[3])-108)
            click_cursor_on([x_pos, y_pos])
            current_coordinates = [current_coordinates[0],current_coordinates[1]-1]
        elif direction == 'd':
            x_pos = game_region[0]+np.random.randint(0, 23)
            y_pos = np.random.randint(game_region[1], game_region[1]+(game_region[3])-108)
            click_cursor_on([x_pos, y_pos])
            current_coordinates = [current_coordinates[0],current_coordinates[1]+1]
        else:
            log("Error in path.")
        update_gui()

game_region = (0,0,0,0)

confidence = 0.45   # finding image matches
accuracy = 5    # distance in pixels between detections
pixels_per_second = 800 # how fast the cursor should move
delay = 0.25 # seconds to wait after each click
offset = 1     # max amount of pixels a click may be off from the center
resource_time = 3   # time it takes to gather a resource
max_wait_time = 30  # seconds to wait when nothing is happening

current_coordinates = [0,0]
current_path = []


gui = tk.Tk()
gui.title("Dofus bot")

coordinates_text = tk.Label(gui, text="Current coordinates: x,y")
coordinates_input = tk.Entry(gui)
coordinates_text.pack()
coordinates_input.pack()

path_text = tk.Label(gui, text="Current path: (u)p (d)own (l)eft (r)ight")
path_input = tk.Entry(gui)
path_text.pack()
path_input.pack()

calibrate_button = tk.Button(text="Calibrate", command=calibrate)
calibrate_button.pack()

cereal_type_text = tk.Label(gui, text="Cereal type:")
cereal_type_input = tk.Entry(gui)
cereal_type_text.pack()
cereal_type_input.pack()
farm_button = tk.Button(text="Farm cereal", command=farm_cereal)
farm_button.pack()

gui_log = tkst.ScrolledText(gui, state=tk.DISABLED)
gui_log.pack()

gui.mainloop()
