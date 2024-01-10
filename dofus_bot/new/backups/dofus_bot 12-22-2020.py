import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
import cv2
import keyboard
import os
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


def log(string, new_line=True):
    # Prints a string in the log of the gui
    gui_log.config(state=tk.NORMAL)
    gui_log.insert(tk.INSERT, string)
    if new_line:
        gui_log.insert(tk.INSERT, "\n")
    gui_log.config(state=tk.DISABLED)
    gui_log.see("end")


def calibrate():
    global status, game_region, current_coordinates, current_path
    reset_variables()
    buttons_pos = pyautogui.locateCenterOnScreen('menu_buttons.png', confidence=0.80)
    if buttons_pos is not None:
        # Sets the area of the game screen as game region
        # Takes the width of the bottom gui as screen width
        # Takes the complete height of the game from bottom gui to the topmost pixel of dofus
        game_region = (buttons_pos[0]-1050, 23, 1272, 1017)
        try:
            # Finds the current coordinates
            screenshot = pyautogui.screenshot()
            screenshot_hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
            # Copies the area where your position is shown
            top_left = screenshot_hsv[70:97, 16:150, :]
            lower_hsv = np.array([15, 0, 215])
            higher_hsv = np.array([30, 20, 230])
            top_left_filtered = cv2.inRange(top_left, lower_hsv, higher_hsv)
            # Finds and filters the coordinates
            coordinates = pytesseract.image_to_string(top_left_filtered)
            split_coordinates = coordinates.split(',')
            current_coordinates = [int(split_coordinates[0]), int(split_coordinates[1])]
            current_path = []
            for direction in path_input.get():
                current_path.append(direction)
            log("Calibration successful.")
        except ValueError:
            game_region = (0, 0, 0, 0)
            log("Calibration failed! Position not visible.")
    else:
        game_region = (0, 0, 0, 0)
        log("Calibration failed! Menu buttons not visible.")


def update_gui():
    path_input.delete(0, "end")
    for direction in current_path:
        path_input.insert("end", direction)


def set_status(new_status):
    global status
    status = new_status


def click_cursor_on(pos, offset=0, shift=False, leave_map=False):
    # Clicks on a given position with a given maximum offset
    # leave_map determines if you will click outside the map border or not
    # shift determines if the click should be done while holding shift
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
    percentage = np.random.randint(0, 100)/100
    if shift:
        pyautogui.keyDown('shift')
    time.sleep(delay*percentage)
    pyautogui.click()
    time.sleep(delay*(1-percentage))
    if shift:
        pyautogui.keyUp('shift')


def harvest_resource_on_screen(resource_type):
    global clicked_resource, resource_list
    try:
        # opens template for recognition
        template = cv2.imread('{}_binary.png'.format(resource_type), cv2.IMREAD_GRAYSCALE)
        # If no resources have yet been spotted, look for them
        if not resource_list:
            threshold = 0.20    # detection threshold in case of wheat
            min_resource_distance = 10    # minimal distance between resources in pixels
            # takes a screenshot with and without highlight
            screenshot = pyautogui.screenshot(region=game_region)
            pyautogui.keyDown('y')
            screenshot_highlight = pyautogui.screenshot(region=game_region)
            pyautogui.keyUp('y')
            # Filters the color white from both screenshots
            lower_hsv = np.array([15, 5, 130])
            higher_hsv = np.array([35, 80, 255])
            img_hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
            img_filtered = cv2.inRange(img_hsv, lower_hsv, higher_hsv)
            img_highlight_hsv = cv2.cvtColor(np.array(screenshot_highlight), cv2.COLOR_RGB2HSV)
            img_highlight_filtered = cv2.inRange(img_highlight_hsv, lower_hsv, higher_hsv)
            # Takes only the white that appeared when holding the y button
            highlights_filtered = img_highlight_filtered - img_filtered
            # searches for the template and filters the best matches
            matches = cv2.matchTemplate(highlights_filtered, template, cv2.TM_CCOEFF_NORMED)
            positions = np.where(matches >= threshold)
            found_positions = []
            for match_pos in zip(*positions[::-1]):
                found_positions.append(match_pos)
            if len(found_positions) > 0:
                # checks if the same resource has been detected multiple times
                resource_list = []
                for match_pos in found_positions:
                    duplicate = False
                    for pos in resource_list:
                        if abs(pos[0] - match_pos[0]) <= min_resource_distance and abs(pos[1] - match_pos[1]) <= min_resource_distance:
                            duplicate = True
                            break
                    if not duplicate:
                        # adds the position of the resource to the resource list
                        resource_list.append([match_pos[0], match_pos[1]])
            # If no resources have been found
            else:
                clicked_resource = True
        else:
            w, h = template.shape
            resource = resource_list.pop(0)
            middle_pos = [int(resource[0] + w * 0.5), int(resource[1] + h * 0.15)]
            click_cursor_on([middle_pos[0] + game_region[0], middle_pos[1] + game_region[1]], shift=True, offset=offset)
            clicked_resource = True
    except (OSError, AttributeError):
        reset_variables()
        log("Invalid resource type.")


def harvest_resource():
    # If all resources on the screen have been clicked
    if clicked_resource and not resource_list:
        reset_variables(reset_status=False)
        log("Finished harvesting resources on this map.")
        follow_path()
    else:
        harvest_resource_on_screen(resource_type_input.get())


def follow_path():
    global status, previous_status
    previous_status = status
    status = 'moving'
    if current_path:
        direction = current_path.pop(0)
        current_path.append(direction)
        if direction == 'n':
            log("Heading north.")
            x_pos = game_region[0]+np.random.randint(30, game_region[2]-31)
            y_pos = game_region[1]+np.random.randint(0, 16)
            click_cursor_on([x_pos, y_pos], shift=True, leave_map=True)
        elif direction == 'e':
            log("Heading east.")
            x_pos = game_region[0]+game_region[2]-np.random.randint(0, 30)
            y_pos = game_region[1]+np.random.randint(0, game_region[3]-136)
            click_cursor_on([x_pos, y_pos], shift=True, leave_map=True)
        elif direction == 's':
            log("Heading south.")
            x_pos = game_region[0]+np.random.randint(72, game_region[2]-113)
            y_pos = game_region[1]+game_region[3]-np.random.randint(127, 135)
            click_cursor_on([x_pos, y_pos], shift=True, leave_map=True)
        elif direction == 'w':
            log("Heading west.")
            x_pos = game_region[0]+np.random.randint(0, 29)
            y_pos = game_region[1]+np.random.randint(0, game_region[3]-136)
            click_cursor_on([x_pos, y_pos], shift=True, leave_map=True)
        else:
            log("Error in path.")
        update_gui()
    else:
        reset_variables()
        log("No path set to follow. Bot stopped.")


def inventory_full():
    # TODO What to do if inventory is full
    log('Inventory is full.')
    reset_variables()
    log('Bot stopped.')


def check_screen():
    global status, current_coordinates
    screenshot = pyautogui.screenshot()
    screenshot_hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
    close_button_pos = pyautogui.locateCenterOnScreen('close_button.png')
    if close_button_pos is not None:
        # Finds the message that popped up
        message_window = screenshot_hsv[close_button_pos[1]-3:close_button_pos[1]+16, close_button_pos[0]-277:close_button_pos[0]-60, :]
        lower_hsv = np.array([20, 225, 90])
        higher_hsv = np.array([25, 255, 250])
        message_filtered = cv2.inRange(message_window, lower_hsv, higher_hsv)
        message_text = pytesseract.image_to_string(message_filtered)
        if message_text[:17] == 'Unable to Harvest':
            inventory_full()
        click_cursor_on([close_button_pos[0], close_button_pos[1]], leave_map=True)
    if status == 'moving':
        top_left = screenshot_hsv[70:97, 16:150, :]
        lower_hsv = np.array([15, 0, 215])
        higher_hsv = np.array([30, 20, 230])
        top_left_filtered = cv2.inRange(top_left, lower_hsv, higher_hsv)
        # Copies the area where your position is shown
        # Finds and filters the coordinates
        coordinates = pytesseract.image_to_string(top_left_filtered)
        try:
            split_coordinates = coordinates.split(',')
            detected_coordinates = [int(split_coordinates[0]), int(split_coordinates[1])]
            if detected_coordinates != current_coordinates:
                status = previous_status
                current_coordinates = detected_coordinates
                log("Arrived at {}".format(current_coordinates))
        # If coordinates haven't been recognized, randomly happens sometimes
        except ValueError:
            pass
    # TODO check some things


def reset_variables(reset_status=True):
    global status, previous_status, resource_list, clicked_resource
    if reset_status:
        status = ''
        previous_status = ''
    resource_list = []
    clicked_resource = False


def loop():
    # If the bot should be doing something
    if status != '':
        # Check if the bot should be stopped
        if keyboard.is_pressed('esc'):
            reset_variables()
            log("Bot activity stopped.")
        else:
            # Checks if the bot is ready to be used
            if game_region == (0, 0, 0, 0):
                reset_variables()
                log("Bot has not been calibrated.")
            else:
                # Makes sure Dofus is in focus
                dofus_unfocused = pyautogui.locateCenterOnScreen('dofus_unfocused.png')
                if dofus_unfocused is not None:
                    click_cursor_on([dofus_unfocused[0], dofus_unfocused[1]], leave_map=True)
                check_screen()
    if status == 'harvest_resource':
        harvest_resource()
    gui.after(10, loop)


game_region = (0, 0, 0, 0)
status = ''
previous_status = ''
clicked_resource = False
resource_list = []

current_coordinates = [0, 0]
current_path = []

pixels_per_second = 800  # how fast the cursor should move
delay = 0.25  # seconds to wait after each click
offset = 2     # max amount of pixels a click may be off from the center

# Sets the work directory in the image folder so the images can easily be read
os.chdir('images')

# Creates the GUI
gui = tk.Tk()
gui.title("Dofus bot")

path_text = tk.Label(gui, text="Current path: (n)orth (e)ast (s)outh (w)est")
path_input = tk.Entry(gui)
path_text.pack()
path_input.pack()

calibrate_button = tk.Button(text="Calibrate", command=calibrate)
calibrate_button.pack()

resource_type_text = tk.Label(gui, text="Resource type:")
resource_type_input = tk.Entry(gui)
resource_type_text.pack()
resource_type_input.pack()
harvest_button = tk.Button(text="Harvest resources", command=lambda: set_status("harvest_resource"))
harvest_button.pack()

gui_log = tkst.ScrolledText(gui, state=tk.DISABLED)
gui_log.pack()


gui.after(10, loop)
gui.mainloop()
