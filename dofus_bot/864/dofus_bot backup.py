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
    global status, last_click_pos, last_click_img
    status = 'farm_cereal'
    # takes a screenshot and finds all highlights
    pyautogui.keyDown('y')
    screenshot = pyautogui.screenshot(region=game_region)
    pyautogui.keyUp('y')
    img_hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
    lower_hsv = np.array([15, 30, 210])
    higher_hsv = np.array([30, 90, 255])
    img_filtered = cv2.inRange(img_hsv, lower_hsv, higher_hsv)
    # opens template for recognition
    template = cv2.imread('{}_binary.png'.format(cereal_type), cv2.IMREAD_GRAYSCALE)
    w, h = template.shape
    threshold = 0.33    # detection threshold in case of wheat
    # searches for the template and filters the best matches
    matches = cv2.matchTemplate(img_filtered, template, cv2.TM_CCOEFF_NORMED)
    positions = np.where(matches >= threshold)
    found_positions = []
    for match_pos in zip(*positions[::-1]):
        found_positions.append(match_pos)
    if len(found_positions) > 0:
        # checks if the same cereal has been detected multiple times
        cereal_pos = []
        for match_pos in found_positions:
            duplicate = False
            for pos in cereal_pos:
                if abs(pos[0] - match_pos[0]) <= 5 and abs(pos[1] - match_pos[1]) <= 5:
                    duplicate = True
                    break
            if not duplicate:
                # adds the position of the cereal
                cereal_pos.append([match_pos[0], match_pos[1]])
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
    else:
        last_click_pos = [0, 0]
        status = ''
        log("Finished farming.")

def farm_cereal():
    global status
    if game_region == (0,0,0,0):
        log("Bot has not been calibrated.")
    else:
        # check if dofus is in focus
        dofus_unfocused = pyautogui.locateCenterOnScreen('dofus_unfocused.png')
        if dofus_unfocused is not None:
            click_cursor_on([dofus_unfocused[0], dofus_unfocused[1]], leave_map=True)
        try:
            farm_cereal_on_screen(cereal_type_input.get())
            # follow_path()
        except (OSError, AttributeError):
            status = ''
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
    # checks if user wants to pause the bot
    if status != '':
        menu = pyautogui.locateOnScreen('main_menu.png')
        if menu is not None:
            status = ''
            last_clicked_pos = [0, 0]
            log("Bot activity stopped.")

def loop():
    check_popups()
    if status == 'farm_cereal':
        farm_cereal()
    gui.after(10, loop)

game_region = (0,0,0,0)
status = ''
last_click_img = []    # image of the first resource clicked
last_click_pos = [0, 0]

current_coordinates = [0,0]
current_path = []

confidence = 0.80   # finding resource matches
accuracy = 5    # distance in pixels between detections
pixels_per_second = 800 # how fast the cursor should move
delay = 0.25 # seconds to wait after each click
offset = 1     # max amount of pixels a click may be off from the center
resource_time = 3   # time it takes to gather a resource
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
