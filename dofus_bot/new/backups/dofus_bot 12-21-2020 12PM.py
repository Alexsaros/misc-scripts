import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image
import cv2
import keyboard
import os


def log(string, new_line=True):
    # Prints a string in the log of the gui
    gui_log.config(state=tk.NORMAL)
    gui_log.insert(tk.INSERT, string)
    if new_line:
        gui_log.insert(tk.INSERT, "\n")
    gui_log.config(state=tk.DISABLED)
    gui_log.see("end")


def calibrate():
    global game_region, current_coordinates, current_path
    buttons_pos = pyautogui.locateCenterOnScreen('menu_buttons.png', confidence=0.80)
    if buttons_pos is not None:
        # Sets the area of the game screen as game region
        # Takes the width of the bottom gui as screen width
        # Takes the complete height of the game from bottom gui to the topmost pixel of dofus
        game_region = (buttons_pos[0]-1050, 23, 1272, pyautogui.size()[1]-40)
        coordinates = coordinates_input.get()
        if coordinates != "" and "," in coordinates:
            split_coordinates = coordinates.split(',')
            current_coordinates = [int(split_coordinates[0]),int(split_coordinates[1])]
            current_path = []
            for direction in path_input.get():
                current_path.append(direction)
            log("Calibration successful.")
        else:
            game_region = (0,0,0,0)
            log("Calibration failed! Invalid coordinates.")
    else:
        game_region = (0,0,0,0)
        log("Calibration failed! Menu buttons not visible.")


def update_gui():
    coordinates_input.delete(0, "end")
    coordinates_input.insert(0, "{},{}".format(current_coordinates[0], current_coordinates[1]))

def set_status(new_status):
    global status
    status = new_status

def click_cursor_on(pos, offset=0, leave_map=False):
    # Clicks on a given position with a given maximum offset
    # leave_map determines if you will click outside the map border or not
    if offset > 0:
        x_offset = np.random.randint(-1*offset, offset)
        y_offset = np.random.randint(-1*offset, offset)
        pos[0] = pos[0]+x_offset
        pos[1] = pos[1]+y_offset
    # Makes sure you don't accidentally move to a different map
    if not leave_map:
        if pos[0] < game_region[0]+30:
            pos[0] = game_region[0]+30
        elif pos[0] > game_region[0]+game_region[2]-31:
            pos[0] = game_region[0]+game_region[2]-31
        if pos[1] < game_region[1]+17:
            pos[1] = game_region[1]+17
        elif pos[1] > game_region[1]+game_region[3]-136:
            pos[1] = game_region[1]+game_region[3]-136
    cursor_pos = pyautogui.position()
    distance = np.sqrt((cursor_pos[0]-pos[0])**2 + (cursor_pos[1]-pos[1])**2)
    pyautogui.moveTo(pos[0], pos[1], distance/pixels_per_second, pyautogui.easeOutQuad)
    # Sleeps for a random small amount of time before and after clicking
    percentage = np.random.randint(0,100)/100
    time.sleep(delay*percentage)
    pyautogui.click()
    time.sleep(delay*(1-percentage))


def farm_cereal_on_screen(cereal_type):
    global status, last_click_pos, last_click_img, resource_list
    status = 'farm_cereal'
    # opens template for recognition
    template = cv2.imread('{}_binary.png'.format(cereal_type), cv2.IMREAD_GRAYSCALE)
    # If no resources have yet been spotted, look for them
    if not resource_list:
        threshold = 0.25    # detection threshold in case of wheat
        min_resource_distance = 10    # minimal distance between resources in pixels
        # takes a screenshot and finds all highlights
        pyautogui.keyDown('y')
        screenshot = pyautogui.screenshot(region=game_region)
        pyautogui.keyUp('y')
        img_hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
        lower_hsv = np.array([15, 5, 130])
        higher_hsv = np.array([35, 80, 255])
        img_filtered = cv2.inRange(img_hsv, lower_hsv, higher_hsv)
        # searches for the template and filters the best matches
        matches = cv2.matchTemplate(img_filtered, template, cv2.TM_CCOEFF_NORMED)
        positions = np.where(matches >= threshold)
        found_positions = []
        for match_pos in zip(*positions[::-1]):
            found_positions.append(match_pos)
        if len(found_positions) > 0:
            # checks if the same cereal has been detected multiple times
            resource_list = []
            for match_pos in found_positions:
                duplicate = False
                for pos in resource_list:
                    if abs(pos[0] - match_pos[0]) <= min_resource_distance and abs(pos[1] - match_pos[1]) <= min_resource_distance:
                        duplicate = True
                        break
                if not duplicate:
                    # adds the position of the cereal to the resource list
                    resource_list.append([match_pos[0], match_pos[1]])
        else:
            pass
            # TODO: add what to do if no resources are found, currently repeats
    else:
        w, h = template.shape
        screenshot = np.array(pyautogui.screenshot(region=game_region))
        # If a resource has already been clicked
        if last_click_pos != [0, 0]:
            current_resource_img = screenshot[last_click_pos[1]:last_click_pos[1]+h, last_click_pos[0]:last_click_pos[0]+w]
            if np.any(last_click_img != current_resource_img):  # if the resource changed
                next_resource = False
                for cereal in resource_list:
                    if next_resource:
                        log(last_click_pos)
                        middle_pos = [int(cereal[0]+w*0.5), int(cereal[1]+h*0.3)]
                        click_cursor_on([middle_pos[0]+game_region[0], middle_pos[1]+game_region[1]], offset=offset)
                        last_click_pos = cereal
                        if resource_list[-1] == cereal:
                            time.sleep(resource_time)
                            reset_variables()
                            log("Finished farming.")
                        break
                    if last_click_pos == cereal:
                        next_resource = True
        else:
            # clicks and remembers first resource
            middle_pos = [int(resource_list[0][0]+w*0.5), int(resource_list[0][1]+h*0.15)]
            click_cursor_on([middle_pos[0]+game_region[0], middle_pos[1]+game_region[1]], offset=offset)
            last_click_pos = resource_list[0]
            last_click_img = screenshot[resource_list[0][1]:resource_list[0][1]+h, resource_list[0][0]:resource_list[0][0]+w]
'''
            # checks if last clicked cereal has been harvested/selected
            log(cereal_pos)
            if last_click_pos != [0, 0]:
                current_resource_img = img_filtered[last_click_pos[1]:last_click_pos[1]+h, last_click_pos[0]:last_click_pos[0]+w]
                if np.any(last_click_img != current_resource_img):  # if the resource changed
                    next_resource = False
                    for cereal in cereal_pos:
                        if next_resource:
                            middle_pos = [int(cereal[0]+w*0.5), int(cereal[1]+h*0.3)]
                            click_cursor_on([middle_pos[0]+game_region[0], middle_pos[1]+game_region[1]], offset=offset)
                            last_click_pos = cereal
                            last_click_img = img_filtered[cereal[1]:cereal[1]+h, cereal[0]:cereal[0]+w]
                            break
                        if abs(cereal[0] - last_click_pos[0]) <= 5 and abs(cereal[1] - last_click_pos[1]) <= 5:
                            next_resource = True
                    pass
            else:
                middle_pos = [int(cereal_pos[0][0]+w*0.5), int(cereal_pos[0][1]+h*0.3)]
                click_cursor_on([middle_pos[0]+game_region[0], middle_pos[1]+game_region[1]], offset=offset)
                last_click_pos = cereal_pos[0]
                last_click_img = img_filtered[cereal_pos[0][1]:cereal_pos[0][1]+h, cereal_pos[0][0]:cereal_pos[0][0]+w]
'''
def farm_cereal():
    global status
    try:
        farm_cereal_on_screen(cereal_type_input.get())
        # TODO implement follow_path()
    except (OSError, AttributeError):
        reset_variables()
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

def check_popups():
    global status
    # TODO check some things

def reset_variables(reset_status=True):
    global status, last_click_img, last_click_pos, resource_list
    if reset_status:
        status = ''
    last_click_img = []
    last_click_pos = [0, 0]
    resource_list = []

def loop():
    # If the bot should be doing something
    if status != '':
        # Check if the bot should be stopped
        if keyboard.is_pressed('esc'):
            reset_variables()
            log("Bot activity stopped.")
        else:
            # Checks if the bot is ready to be used
            if game_region == (0,0,0,0):
                reset_variables()
                log("Bot has not been calibrated.")
            else:
                # Makes sure Dofus is in focus
                dofus_unfocused = pyautogui.locateCenterOnScreen('dofus_unfocused.png')
                if dofus_unfocused is not None:
                    click_cursor_on([dofus_unfocused[0], dofus_unfocused[1]], leave_map=True)
                check_popups()
    if status == 'farm_cereal':
        farm_cereal()
    gui.after(10, loop)

game_region = (0,0,0,0)
status = ''
last_click_img = []    # image of the first resource clicked
last_click_pos = [0, 0]
resource_list = []

current_coordinates = [0,0]
current_path = []

confidence = 0.80   # finding resource matches
accuracy = 5    # distance in pixels between detections
pixels_per_second = 800  # how fast the cursor should move
delay = 0.25  # seconds to wait after each click
offset = 2     # max amount of pixels a click may be off from the center
resource_time = 3   # time it takes to gather a resource
max_wait_time = 30  # seconds to wait when nothing is happening

# Sets the work directory in the image folder so the images can easily be read
os.chdir('images')

# Creates the GUI
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
farm_button = tk.Button(text="Farm cereal", command=lambda: set_status("farm_cereal"))
farm_button.pack()

gui_log = tkst.ScrolledText(gui, state=tk.DISABLED)
gui_log.pack()


gui.after(10, loop)
gui.mainloop()
