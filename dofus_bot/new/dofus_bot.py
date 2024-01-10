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
from map_data import Map, Coordinate
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


# Finished
def log(string, new_line=True):
    # Prints a string in the log of the gui
    gui_log.config(state=tk.NORMAL)
    gui_log.insert(tk.INSERT, string)
    if new_line:
        gui_log.insert(tk.INSERT, "\n")
    gui_log.config(state=tk.DISABLED)
    gui_log.see("end")


def calibrate():
    global game_region, current_coordinates, paths, market_coordinates, resources_of_interest, price_percentage, map_data
    reset_variables()
    try:
        price_percentage = int(price_percentage_input.get())/100
    except ValueError:
        price_percentage = 0
    # Remembers all resources of interest
    resources_of_interest = []
    if wheat_interested.get() == 1:
        resources_of_interest.append('wheat')
    if ash_interested.get() == 1:
        resources_of_interest.append('ash')
    if len(resources_of_interest) > 0:
        # Uses the menu buttons as a reference point
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
                top_left = screenshot_hsv[70:99, 16:150, :]
                lower_hsv = np.array([20, 0, 210])
                higher_hsv = np.array([45, 15, 230])
                top_left_filtered = cv2.inRange(top_left, lower_hsv, higher_hsv)
                # Finds and filters the coordinates
                coordinates = pytesseract.image_to_string(top_left_filtered)
                print('coordinates =', coordinates)
                split_coordinates = coordinates.split(',')
                current_coordinates = [int(split_coordinates[0]), int(split_coordinates[1])]
                try:
                    paths = []
                    path = []
                    path_coordinates = re.findall(r"\[(.*?)]", path_input.get())
                    for coordinate in path_coordinates:
                        coordinate_split = coordinate.split(',')
                        path.append([int(coordinate_split[0]), int(coordinate_split[1])])
                    paths = [path]
                    if path:
                        try:
                            # Reads the coordinates of the market
                            market_coordinates = market_coordinates_input.get()
                            market_split_coordinates = market_coordinates.split(',')
                            market_coordinates = [int(market_split_coordinates[0]), int(market_split_coordinates[1])]
                            try:
                                file = open('map', "rb")
                                map_data = pickle.load(file)
                                file.close()
                                log("Calibration successful.")
                            except FileNotFoundError:
                                game_region = (0, 0, 0, 0)
                                log("Calibration failed! Cannot find map data.")
                        except (IndexError, ValueError):
                            game_region = (0, 0, 0, 0)
                            log("Calibration failed! Invalid market coordinates.")
                    else:
                        game_region = (0, 0, 0, 0)
                        log("Calibration failed! Please enter a path.")
                except (IndexError, ValueError):
                    game_region = (0, 0, 0, 0)
                    log("Calibration failed! Invalid path.")
            except ValueError:
                game_region = (0, 0, 0, 0)
                log("Calibration failed! Position not visible.")
        else:
            game_region = (0, 0, 0, 0)
            log("Calibration failed! Menu buttons not visible.")
    else:
        game_region = (0, 0, 0, 0)
        log("Calibration failed! No resources selected.")


def update_gui():
    path_input.delete(0, "end")
    new_text = ''
    for coordinate in paths[0]:
        new_text += '[{}]'.format(coordinate)
    path_input.insert("end", new_text)


# Finished
def set_status(new_status):
    global status
    status = [new_status]


# Finished
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


# Possibly finished
def harvest_resources_on_screen():
    global resource_list
    # If no resources have yet been clicked, look for them
    if not resource_list:
        # Finds all resources of interest on this map
        coordinate_data = map_data.read_coordinate(current_coordinates)
        resource_coordinates = []
        for resource in coordinate_data.resources:
            for resource_of_interest in resources_of_interest:
                if resource[0] == resource_of_interest:
                    resource_coordinates.append(resource[1])
        print(resource_coordinates)
        if len(resource_coordinates) > 0:
            # Sorts the list so nearby resources get clicked first
            resource_list = [resource_coordinates.pop(0)]
            while len(resource_coordinates) > 0:
                # Calculates the distance from the last added/clicked resource to all other resources
                closest_resource = None
                closest_distance = None
                for resource in resource_coordinates:
                    distance = np.sqrt((resource[0]-resource_list[-1][0])**2+(resource[1]-resource_list[-1][1])**2)
                    if closest_distance is None or distance < closest_distance:
                        closest_resource = resource
                        closest_distance = distance
                resource_list.append(closest_resource)
                resource_coordinates.remove(closest_resource)
    else:
        resource = resource_list.pop(0)
        click_cursor_on(resource, shift=True, offset=offset)


# Finished
def harvest_resources():
    # If not at the right coordinate
    if current_coordinates != paths[-1][0]:
        move_to(paths[-1][0])
    else:
        # If all resources of a type have been clicked, remove it from the list
        harvest_resources_on_screen()
        # If all resources on this map have been checked
        if not resource_list:
            reset_variables(reset_status=False)
            log("Finished harvesting resources on this map.")
            previous_coordinate = paths[-1].pop(0)
            paths[-1].append(previous_coordinate)
            move_to(paths[-1][0])
            update_gui()


def sell_item(item_type):
    # TODO handle warning when price far below average
    # Sells 100 of an item
    # Returns True or False based on whether the item got sold successfully
    global last_known_price
    item_img = cv2.imread('{}_item.png'.format(item_type))
    screen_size = pyautogui.size()
    # Finds the item on the right half of the screen
    item = pyautogui.locateCenterOnScreen(item_img, confidence=0.90, region=(int(screen_size[0]/2), 0,
                                                                             int(screen_size[0]/2), screen_size[1]))
    if item is not None:
        screenshot = pyautogui.screenshot()
        screenshot_hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
        h, w = item_img.shape[:2]
        left = int(item[0]-(w/2)-2)
        right = int(item[0]+(w/2))
        top = int(item[1]-(h/2)-16)
        bottom = int(item[1]-(h/2))
        # Finds the amount of the resource in inventory
        resource_amount_cropped = screenshot_hsv[top:bottom, left:right, :]
        lower_hsv = np.array([0, 0, 255])
        higher_hsv = np.array([0, 0, 255])
        resource_amount_filtered = cv2.inRange(resource_amount_cropped, lower_hsv, higher_hsv)
        try:
            resource_amount = pytesseract.image_to_string(resource_amount_filtered, config='--psm 8')
            resource_amount = int(re.findall(r'\d+', resource_amount)[0])
        except IndexError:
            resource_amount = 1
        print('resource amount =', resource_amount)
        if resource_amount >= 100:
            click_cursor_on([item[0], item[1]], offset=offset)
            # If the price isn't known yet
            if last_known_price == 0:
                # Filters the text for sale to find a pack of 100
                time.sleep(1)
                screenshot = pyautogui.screenshot()
                screenshot_hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
                packs_cropped = screenshot_hsv[544:688, 448:473, :]
                lower_hsv = np.array([20, 0, 155])
                higher_hsv = np.array([45, 15, 200])
                packs_cropped_filtered = cv2.inRange(packs_cropped, lower_hsv, higher_hsv)
                # Looks for the number 100
                pack_100_template = cv2.imread('100.png', cv2.IMREAD_GRAYSCALE)
                h, w = pack_100_template.shape[:2]
                matches = cv2.matchTemplate(packs_cropped_filtered, pack_100_template, cv2.TM_SQDIFF_NORMED)
                # Looks left of the number 100 for the price
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matches)
                top_left = [int(min_loc[0]+448), int(min_loc[1]+544)]
                price_cropped = screenshot_hsv[top_left[1]:top_left[1]+16, top_left[0]+w:top_left[0]+126, :]
                price_cropped_filtered = cv2.inRange(price_cropped, lower_hsv, higher_hsv)
                # Reads the price
                price = pytesseract.image_to_string(price_cropped_filtered)
                price = price.replace(',', '')
                price = price.replace('.', '')
                print('price =', price)
                price = int(re.findall(r'\d+', price)[0])
                print('price =', price)
                last_known_price = int(price+price*price_percentage)
            # Input the price
            click_cursor_on([519, 282], offset=offset)
            pyautogui.keyDown('ctrl')
            pyautogui.press('a')
            pyautogui.keyUp('ctrl')
            pyautogui.press('backspace')
            for number in str(last_known_price):
                pyautogui.press(number)
            pyautogui.press('enter')
            return True
        else:
            last_known_price = 0
            return False
    else:
        last_known_price = 0
        return False


def sell_resources():
    global resources_to_check, status, paths
    if current_coordinates != market_coordinates:
        move_to(market_coordinates)
    else:
        market_text = pyautogui.locateCenterOnScreen('market_text.png')
        if market_text is None:
            coordinate_data = map_data.read_coordinate(current_coordinates)
            market_pos = []
            for resource in coordinate_data.resources:
                if resource[0] == 'resource_marketplace':
                    market_pos = resource[1]
                    break
            # If no market on this coordinate
            if not market_pos:
                reset_variables()
                log("No market found on this map. Bot stopped.")
            else:
                click_cursor_on([market_pos[0], market_pos[1]], offset=offset)
                # Sleeps to give the character time to walk to the market
                time.sleep(3)
        else:
            # If market is opened
            # Makes sure the sale tab is open
            sale_tab_button = pyautogui.locateCenterOnScreen('sale_tab_button.png')
            if sale_tab_button is not None:
                click_cursor_on([sale_tab_button[0], sale_tab_button[1]], offset=offset)
            # Makes sure the resources tab is open
            resources_button = pyautogui.locateCenterOnScreen('resources_inv_button.png')
            if resources_button is not None:
                click_cursor_on([resources_button[0], resources_button[1]], offset=offset)
            # If no resources have been sold yet
            if not resources_to_check:
                resources_to_check = resources_of_interest.copy()
            resource = resources_to_check[0]
            succeeded = sell_item(resource)
            # Remove the resource if it can't be sold (anymore)
            if not succeeded:
                resources_to_check.pop(0)
            # Check if all resources have been sold
            if not resources_to_check:
                close_button = pyautogui.locateCenterOnScreen('close_menu_button.png', confidence=0.90)
                click_cursor_on([close_button[0], close_button[1]], offset=offset)
                status.pop(-1)
                paths.pop(-1)
                print('last_known_price (should be 0) =', last_known_price)
                log("Finished selling resources.")


# Finished
def exit_map(direction):
    if direction == 'north':
        x_pos = game_region[0] + np.random.randint(30, game_region[2] - 31)
        y_pos = game_region[1] + np.random.randint(0, 16)
        click_cursor_on([x_pos, y_pos], shift=True, leave_map=True)
    elif direction == 'east':
        x_pos = game_region[0] + game_region[2] - np.random.randint(0, 30)
        y_pos = game_region[1] + np.random.randint(0, game_region[3] - 136)
        click_cursor_on([x_pos, y_pos], shift=True, leave_map=True)
    elif direction == 'south':
        x_pos = game_region[0] + np.random.randint(72, game_region[2] - 113)
        y_pos = game_region[1] + game_region[3] - np.random.randint(127, 135)
        click_cursor_on([x_pos, y_pos], shift=True, leave_map=True)
    elif direction == 'west':
        x_pos = game_region[0] + np.random.randint(0, 29)
        y_pos = game_region[1] + np.random.randint(0, game_region[3] - 136)
        click_cursor_on([x_pos, y_pos], shift=True, leave_map=True)
    else:
        reset_variables()
        log("ERROR: Invalid direction: {}".format(direction))


def navigate(goal):
    global paths
    # TODO use pathfinding
    go_north = False
    go_east = False
    go_south = False
    go_west = False
    moved = False
    # Checks in what directions the goal lies
    if current_coordinates[1] != goal[1]:
        coordinate_data = map_data.read_coordinate(current_coordinates)
        if current_coordinates[1] > goal[1]:
            go_north = True
        elif current_coordinates[1] < goal[1]:
            go_south = True
        else:
            reset_variables()
            log('ERROR: faulty coordinates.')
    if current_coordinates[0] != goal[0]:
        coordinate_data = map_data.read_coordinate(current_coordinates)
        if current_coordinates[0] > goal[0]:
            go_west = True
        elif current_coordinates[0] < goal[0]:
            go_east = True
        else:
            reset_variables()
            log('ERROR: faulty coordinates.')
    # Tries positioning vertically first
    if go_north and not moved:
        if coordinate_data.north_exit == 1:
            exit_map('north')
            moved = True
        else:
            # Check if the blockade can be bypassed
            if coordinate_data.east_exit == 1:
                coordinate_data_east = map_data.read_coordinate([current_coordinates[0]+1, current_coordinates[1]])
                if coordinate_data_east.north_exit == 1:
                    paths[-1].insert(0, [current_coordinates[0]+1, current_coordinates[1]-1])
                    exit_map('east')
                    moved = True
            if coordinate_data.west_exit == 1 and not moved:
                coordinate_data_west = map_data.read_coordinate([current_coordinates[0]-1, current_coordinates[1]])
                if coordinate_data_west.north_exit == 1:
                    paths[-1].insert(0, [current_coordinates[0]-1, current_coordinates[1]-1])
                    exit_map('west')
                    moved = True
    if go_south and not moved:
        if coordinate_data.south_exit == 1:
            exit_map('south')
            moved = True
        else:
            # Check if the blockade can be bypassed
            if coordinate_data.east_exit == 1:
                coordinate_data_east = map_data.read_coordinate([current_coordinates[0]+1, current_coordinates[1]])
                if coordinate_data_east.south_exit == 1:
                    paths[-1].insert(0, [current_coordinates[0]+1, current_coordinates[1]+1])
                    exit_map('east')
                    moved = True
            if coordinate_data.west_exit == 1 and not moved:
                coordinate_data_west = map_data.read_coordinate([current_coordinates[0]-1, current_coordinates[1]])
                if coordinate_data_west.south_exit == 1:
                    paths[-1].insert(0, [current_coordinates[0]-1, current_coordinates[1]+1])
                    exit_map('west')
                    moved = True
    if go_east and not moved:
        if coordinate_data.east_exit == 1:
            exit_map('east')
            moved = True
        else:
            # Check if the blockade can be bypassed
            if coordinate_data.north_exit == 1:
                coordinate_data_north = map_data.read_coordinate([current_coordinates[0], current_coordinates[1]-1])
                if coordinate_data_north.east_exit == 1:
                    paths[-1].insert(0, [current_coordinates[0]+1, current_coordinates[1]-1])
                    exit_map('north')
                    moved = True
            if coordinate_data.south_exit == 1 and not moved:
                coordinate_data_south = map_data.read_coordinate([current_coordinates[0], current_coordinates[1]+1])
                if coordinate_data_south.east_exit == 1:
                    paths[-1].insert(0, [current_coordinates[0]+1, current_coordinates[1]+1])
                    exit_map('south')
                    moved = True
    if go_west and not moved:
        if coordinate_data.west_exit == 1:
            exit_map('west')
            moved = True
        else:
            # Check if the blockade can be bypassed
            if coordinate_data.north_exit == 1:
                coordinate_data_north = map_data.read_coordinate([current_coordinates[0], current_coordinates[1]-1])
                if coordinate_data_north.west_exit == 1:
                    paths[-1].insert(0, [current_coordinates[0]-1, current_coordinates[1]-1])
                    exit_map('north')
                    moved = True
            if coordinate_data.south_exit == 1 and not moved:
                coordinate_data_south = map_data.read_coordinate([current_coordinates[0], current_coordinates[1]+1])
                if coordinate_data_south.west_exit == 1:
                    paths[-1].insert(0, [current_coordinates[0]-1, current_coordinates[1]+1])
                    exit_map('south')
                    moved = True
    # If no exit possible
    if not moved:
        reset_variables()
        log('Cannot find path to goal! Bot stopped.')


# Finished
def move_to(goal=None):
    global current_coordinates, coordinates_goal, status, paths
    # If a (new) goal has been set
    if goal is not None:
        coordinates_goal = goal
    if not paths or paths[-1][-1] != coordinates_goal:
        paths.append([coordinates_goal])
    # Copies the area where your position is shown
    screenshot = pyautogui.screenshot()
    screenshot_hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
    top_left = screenshot_hsv[70:99, 16:150, :]
    lower_hsv = np.array([20, 0, 210])
    higher_hsv = np.array([45, 15, 230])
    top_left_filtered = cv2.inRange(top_left, lower_hsv, higher_hsv)
    # Finds and filters the coordinates
    coordinates = pytesseract.image_to_string(top_left_filtered)
    print('coordinates =', coordinates)
    try:
        split_coordinates = coordinates.split(',')
        detected_coordinates = [int(split_coordinates[0]), int(split_coordinates[1])]
        # If has been moving before
        if status[-1] == 'moving':
            if detected_coordinates != current_coordinates:
                # If the map has changed
                current_coordinates = detected_coordinates
                log("Arrived at {}.".format(current_coordinates))
                if current_coordinates == paths[-1][0]:
                    # If arrived at the next coordinates
                    removed_coordinate = paths[-1].pop(0)
                    if status[-1] == 'harvest_resources':
                        # Loop coordinates if harvesting
                        paths[-1].append(removed_coordinate)
                # If the path list is now empty, delete it
                if not paths[-1]:
                    # If arrived at the final coordinates
                    status.pop(-1)
                    paths.pop(-1)
                    log("Finished moving.")
                else:
                    navigate(paths[-1][0])
        else:
            # If just started moving
            status.append('moving')
            current_coordinates = detected_coordinates
            if current_coordinates == paths[-1][-1]:
                status.pop(-1)
                log("Already at the correct position.")
            if current_coordinates == paths[-1][0]:
                # If arrived at the next coordinates
                paths[-1].pop(0)
                # If the path list is now empty, delete it
                if not paths[-1]:
                    paths.pop(-1)
            else:
                navigate(paths[-1][0])
    # If coordinates haven't been recognized, randomly happens sometimes
    except ValueError:
        print("Coordinates not recognized.")


# Finished
def inventory_full():
    global status
    log('Inventory is full.')
    status.append('sell_resources')
    sell_resources()


def battle():
    global status
    # Check if the end turn buttons is clickable to see if it's the player's/bot's turn
    player_turn = False
    close_button_battle_pos = pyautogui.locateCenterOnScreen('close_button_battle.png')
    if close_button_battle_pos is not None:
        # Check if the battle ended
        status.pop(-1)
        click_cursor_on([close_button_battle_pos[0], close_button_battle_pos[1]], offset=offset)
    else:
        # Checks the end turn button
        screenshot_end_turn_button = pyautogui.screenshot(region=(1324, 943, 135, 50))
        screenshot_end_turn_button_hsv = cv2.cvtColor(np.array(screenshot_end_turn_button), cv2.COLOR_RGB2HSV)
        lower_hsv = np.array([30, 255, 235])
        higher_hsv = np.array([35, 255, 255])
        end_turn_button_filtered = cv2.inRange(screenshot_end_turn_button_hsv, lower_hsv, higher_hsv)
        # Checks if the end turn putton is pressable
        if cv2.countNonZero(end_turn_button_filtered) > 0:
            player_turn = True
        if player_turn:
            end_turn_button_pos = [1391, 968]
            print('players turn')
            # Presses the button for a summon spell and see which tiles (if any) are blue/valid
            pyautogui.press(str(summon_button_input.get()))
            screenshot = pyautogui.screenshot()
            screenshot_hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
            lower_hsv = np.array([115, 195, 150])
            higher_hsv = np.array([120, 200, 155])
            blue_filtered = cv2.inRange(screenshot_hsv, lower_hsv, higher_hsv)
            contours, hierarchy = cv2.findContours(blue_filtered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                # If the summon spell is not on cooldown
                # Select a random tile to place the summon on
                selected_tile = random.randint(0, len(contours)-1)
                x, y, w, h = cv2.boundingRect(contours[selected_tile])
                click_cursor_on([int(x+w/2), int(y+h/2)], leave_map=True, offset=offset)
            click_cursor_on([end_turn_button_pos[0], end_turn_button_pos[1]], leave_map=True, offset=offset)


def check_screen():
    # TODO check if disconnected
    global status
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
        click_cursor_on([close_button_pos[0], close_button_pos[1]], leave_map=True, offset=offset)
    ready_button_pos = pyautogui.locateCenterOnScreen('ready_button.png')
    if ready_button_pos is not None:
        log('Entered battle.')
        status.append('battle')
        click_cursor_on([ready_button_pos[0], ready_button_pos[1]], leave_map=True, offset=offset)
    # TODO check pvp, trade? block?


# Finished
def reset_variables(reset_status=True):
    global status, resource_list, last_known_price
    if reset_status:
        status = []
    resource_list = []
    last_known_price = 0


def loop():
    # If the bot should be doing something
    if status:
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
    if status:
        print(status)
        if status[-1] == 'moving':
            move_to()
        elif status[-1] == 'harvest_resources':
            harvest_resources()
        elif status[-1] == 'sell_resources':
            sell_resources()
        elif status[-1] == 'battle':
            battle()
    gui.after(10, loop)


game_region = (0, 0, 0, 0)
status = []
resource_list = []
resources_to_check = []
map_data = Map()

current_coordinates = [0, 0]
coordinates_goal = []
paths = []
market_coordinates = [0, 0]
resources_of_interest = []
last_known_price = 0
price_percentage = 0

pixels_per_second = 1000  # how fast the cursor should move
delay = 0.10  # seconds to wait after each click
offset = 2     # max amount of pixels a click may be off from the center

# size of a grid tile in pixels
grid_width = 89
grid_height = 44

# Sets the work directory in the image folder so the images can easily be read
os.chdir('images')


# Creates the GUI
gui = tk.Tk()
gui.title("Dofus bot")

wheat_interested = tk.IntVar()
ash_interested = tk.IntVar()

path_text = tk.Label(gui, text="Current harvesting path: [x,y][x,y][x,y]")
path_input = tk.Entry(gui)
path_text.pack()
path_input.pack()

market_coordinates_text = tk.Label(gui, text="Nearest market position (e.g. 4,-17)")
market_coordinates_input = tk.Entry(gui)
market_coordinates_text.pack()
market_coordinates_input.pack()

price_percentage_text = tk.Label(gui, text="Percentage to add to the current minimum price")
price_percentage_input = tk.Entry(gui)
price_percentage_text.pack()
price_percentage_input.pack()

summon_button_text = tk.Label(gui, text="Shortcut button for a summon spell (e.g. 8)")
summon_button_input = tk.Entry(gui)
summon_button_text.pack()
summon_button_input.pack()

wheat_checkbox = tk.Checkbutton(gui, text='Wheat', variable=wheat_interested)
wheat_checkbox.pack()
ash_checkbox = tk.Checkbutton(gui, text='Ash', variable=ash_interested)
ash_checkbox.pack()

calibrate_button = tk.Button(text="Calibrate", command=calibrate)
calibrate_button.pack()

harvest_button = tk.Button(text="Harvest resources", command=lambda: set_status("harvest_resources"))
harvest_button.pack()

sell_button = tk.Button(text="Sell resources on nearest market", command=lambda: set_status("sell_resources"))
sell_button.pack()

gui_log = tkst.ScrolledText(gui, state=tk.DISABLED)
gui_log.pack()


gui.after(10, loop)
gui.mainloop()
