import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image
import cv2


def log(string, new_line=True):
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
        game_region = (buttons_pos[0]-826, 23, 1001, pyautogui.size()[1]-63)
        coordinates = coordinates_input.get()
        if coordinates != "" and "," in coordinates:
            split_coordinates = coordinates.split(',')
            current_coordinates = [int(split_coordinates[0]),int(split_coordinates[1])]
            current_path = path_input.get()
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
    path_input.delete(0, "end")
    path_input.insert(0, "{}".format(current_path))

def click_cursor_on(pos, offset=0, leave_map=False):
    if offset > 0:
        x_offset = np.random.randint(-1*offset, offset)
        y_offset = np.random.randint(-1*offset, offset)
        pos[0] = pos[0]+x_offset
        pos[1] = pos[1]+y_offset
    if not leave_map:
        if pos[0] < game_region[0]+30:
            pos[0] = game_region[0]+30
        elif pos[0] > game_region[0]+game_region[2]-30:
            pos[0] = game_region[0]+game_region[2]-30
        if pos[1] < game_region[1]+14:
            pos[1] = game_region[1]+14
        elif pos[1] > game_region[1]+game_region[3]-108:
            pos[1] = game_region[1]+game_region[3]-108
    cursor_pos = pyautogui.position()
    distance = np.sqrt((cursor_pos[0]-pos[0])**2 + (cursor_pos[1]-pos[1])**2)
    pyautogui.moveTo(pos[0], pos[1], distance/pixels_per_second, pyautogui.easeOutQuad)
    percentage = np.random.randint(0,100)/100
    time.sleep(delay*percentage)
    pyautogui.click()
    time.sleep(delay*(1-percentage))

def farm_cereal_on_screen(cereal_type):
    global status, resource_list
    # opens template for recognition
    template = cv2.imread('{}_binary.png'.format(cereal_type), cv2.IMREAD_GRAYSCALE)
    w, h = template.shape
    threshold = 0.25    # detection threshold in case of wheat (between 0.21 and 0.33)
    if resource_list == []:
        # takes a screenshot and finds all highlights
        pyautogui.keyDown('y')
        screenshot = pyautogui.screenshot(region=game_region)
        pyautogui.keyUp('y')
        img_hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
        lower_hsv = np.array([15, 30, 210])
        higher_hsv = np.array([30, 90, 255])
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
                    if abs(pos[0] - match_pos[0]) <= 10 and abs(pos[1] - match_pos[1]) <= 10:
                        duplicate = True
                        break
                if not duplicate:
                    # adds the position of the cereal to the resource list
                    resource_list.append([match_pos[0], match_pos[1]])
    else:
        middle_pos = [int(resource_list[0][0]+w*0.5), int(resource_list[0][1]+h*0.3)]
        pyautogui.keyDown('shift')
        click_cursor_on([middle_pos[0]+game_region[0], middle_pos[1]+game_region[1]], offset=offset)
        pyautogui.keyUp('shift')
        resource_list.pop(0)
    if len(resource_list) == 0:
        reset_variables()
        log("No cereal left on screen.")

def farm_cereal():
    global status
    if status[:11] != 'farm_cereal':
        status = 'farm_cereal_on_screen'
    if game_region == (0,0,0,0):
        log("Bot has not been calibrated.")
    else:
        print(status)
        # check if dofus is in focus
        dofus_unfocused = pyautogui.locateCenterOnScreen('dofus_unfocused.png')
        if dofus_unfocused is not None:
            click_cursor_on([dofus_unfocused[0], dofus_unfocused[1]], leave_map=True)
        try:
            if status == 'farm_cereal_on_screen':
                farm_cereal_on_screen(cereal_type_input.get())
                if len(resource_list) == 0:
                    follow_path()
        except (OSError, AttributeError):
            status = ''
            log("Invalid cereal type.")

def follow_path():
    global current_coordinates, status, current_path
    if current_path != '':
        status = 'farm_cereal_moving'
        direction = current_path[0]
        current_path = current_path[1:]+direction
        if direction == 'l':    # FIX DIRECTIONS, ARE OFF
            x_pos = game_region[0]-np.random.randint(22, 23)
            y_pos = np.random.randint(game_region[1], game_region[1]+(game_region[3])-108)
            pyautogui.keyDown('shift')
            click_cursor_on([x_pos, y_pos])
            pyautogui.keyUp('shift')
            current_coordinates = [current_coordinates[0]-1,current_coordinates[1]]
        elif direction == 'r':
            x_pos = game_region[0]+game_region[2]+np.random.randint(1, 23)
            y_pos = np.random.randint(game_region[1], game_region[1]+(game_region[3])-108)
            pyautogui.keyDown('shift')
            click_cursor_on([x_pos, y_pos])
            pyautogui.keyUp('shift')
            current_coordinates = [current_coordinates[0]+1,current_coordinates[1]]
        elif direction == 'u':
            x_pos = game_region[0]+24+np.random.randint(0, game_region[2]-48)
            y_pos = game_region[1]+np.random.randint(0, 13)
            pyautogui.keyDown('shift')
            click_cursor_on([x_pos, y_pos])
            pyautogui.keyUp('shift')
            current_coordinates = [current_coordinates[0],current_coordinates[1]-1]
        elif direction == 'd':
            x_pos = game_region[0]+56+np.random.randint(0, game_region[2]-144)
            y_pos = game_region[1]+game_region[3]-np.random.randint(102, 107)
            pyautogui.keyDown('shift')
            click_cursor_on([x_pos, y_pos])
            pyautogui.keyUp('shift')
            current_coordinates = [current_coordinates[0],current_coordinates[1]+1]
        else:
            log("Error in path.")
        update_gui()

def check_popups():
    global status
    # checks if user wants to pause the bot
    if status != '':
        menu = pyautogui.locateOnScreen('main_menu.png')
        if menu is not None:
            reset_variables()
            log("Bot activity stopped.")

def reset_variables(reset_status=True):
    global status, resource_list
    if reset_status:
        status = ''
    resource_list = []

def loop():
    check_popups()
    if status[:11] == 'farm_cereal':
        farm_cereal()
    gui.after(10, loop)

game_region = (0,0,0,0)
status = ''
resource_list = []

current_coordinates = [0,0]
current_path = ''

# confidence = 0.80   # finding resource matches
accuracy = 5    # distance in pixels between detections
pixels_per_second = 800 # how fast the cursor should move
delay = 0.25 # seconds to wait after each click
offset = 1     # max amount of pixels a click may be off from the center
max_wait_time = 30  # seconds to wait when nothing is happening



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

gui.after(10, loop)
gui.mainloop()
