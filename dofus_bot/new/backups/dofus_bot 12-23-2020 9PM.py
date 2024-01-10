import pyautogui
import time
import numpy as np
import tkinter as tk
import tkinter.scrolledtext as tkst
import cv2
import keyboard
import os
import re
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
    global status, game_region, current_coordinates, current_path, market_pos, resources_of_interest
    reset_variables()
    # Remembers all resources of interest
    resources_of_interest = []
    if wheat_interested.get() == 1:
        resources_of_interest.append('wheat')
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
                try:
                    # Reads the coordinates of the market
                    market_coordinates = market_pos_input.get()
                    market_split_coordinates = market_coordinates.split(',')
                    market_pos = [int(market_split_coordinates[0]), int(market_split_coordinates[1])]
                    log("Calibration successful.")
                except (IndexError, ValueError) as e:
                    game_region = (0, 0, 0, 0)
                    log("Calibration failed! Invalid market coordinates.")
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


def hover_find(pos, text):
    # Hovers the cursor over a position to find a text that appears
    cursor_pos = pyautogui.position()
    distance = np.sqrt((cursor_pos[0]-pos[0])**2 + (cursor_pos[1]-pos[1])**2)
    pyautogui.moveTo(pos[0], pos[1], distance/pixels_per_second, pyautogui.easeOutQuad)
    screenshot = pyautogui.screenshot(region=game_region)
    # Filters white text
    img_hsv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
    lower_hsv = np.array([5, 10, 155])
    higher_hsv = np.array([15, 20, 235])
    image_filtered = cv2.inRange(img_hsv, lower_hsv, higher_hsv)
    text_found = pytesseract.image_to_string(image_filtered)
    if text_found.find(text) != -1:
        return True
    else:
        return False


def harvest_resources_on_screen(resource_type):
    global clicked_resource, resource_list
    try:
        # opens template for recognition
        template = cv2.imread('{}_masked.png'.format(resource_type))
        # If no resources have yet been spotted, look for them
        if not resource_list:
            threshold = 0.40    # detection threshold in case of wheat
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
            # Creates a temporary border around the image for processing
            h, w = highlights_filtered.shape[:2]
            highlights_bordered = np.zeros((h+40, w+40), np.uint8)
            highlights_bordered[20:-20, 20:-20] = highlights_filtered
            # Closes any gaps in the highlights
            closing_kernel = np.ones((17, 17), np.uint8)
            highlights = cv2.morphologyEx(highlights_bordered, cv2.MORPH_CLOSE, closing_kernel)
            # Fill in the outside of the interactable objects
            h, w = highlights.shape[:2]
            mask = np.zeros((h+2, w+2), np.uint8)
            highlights_outside = highlights.copy()
            cv2.floodFill(highlights_outside, mask, (0, 0), 255)
            # Add the inside of the highlights and the highlights together to form the object's shape
            highlights_insides = cv2.bitwise_not(highlights_outside)
            highlights_filled = highlights_insides | highlights
            highlights_filled = highlights_filled[20:-20, 20:-20]
            # Finds what's inside the highlighted areas
            img = cv2.cvtColor(np.array(screenshot_highlight), cv2.COLOR_RGB2BGR)
            img_masked = cv2.bitwise_and(img, img, mask=highlights_filled)
            # Searches for the template and filters the best matches
            matches = cv2.matchTemplate(img_masked, template, cv2.TM_SQDIFF_NORMED)
            positions = np.where(matches <= threshold)
            # Mirrors the template and look again for mirrored versions
            template_mirrored = cv2.flip(template, 1)
            matches_mirrored = cv2.matchTemplate(img_masked, template_mirrored, cv2.TM_SQDIFF_NORMED)
            positions_mirrored = np.where(matches_mirrored <= threshold)
            # Places all positions together with their confidence in a list and sort the list on confidence
            sorted_pos = []
            for pos in zip(*positions[::-1]):
                sorted_pos.append([pos[0], pos[1], matches[pos[1], pos[0]]])
            for pos in zip(*positions_mirrored[::-1]):
                sorted_pos.append([pos[0], pos[1], matches[pos[1], pos[0]]])
            sorted_pos.sort(key=lambda x: x[2])
            if len(sorted_pos) > 0:
                # Checks if the same resource has been detected multiple times
                resource_list_filtered = []
                for match_pos in sorted_pos:
                    duplicate = False
                    for pos in resource_list_filtered:
                        if abs(pos[0] - match_pos[0]) <= grid_width/2.5 and abs(
                                pos[1] - match_pos[1]) <= grid_height/2.5:
                            duplicate = True
                            break
                    if not duplicate:
                        # Adds the position of the resource to the resource list
                        resource_list_filtered.append([match_pos[0], match_pos[1]])
                # Sorts the list so nearby resources get clicked first
                resource_list = []
                resource_list.append(resource_list_filtered.pop(0))
                while len(resource_list_filtered) > 0:
                    # Calculates the distance from the last added/clicked resource to all other resources
                    closest_resource = None
                    closest_distance = None
                    for resource in resource_list_filtered:
                        distance = np.sqrt((resource[0]-resource_list[-1][0])**2+(resource[1]-resource_list[-1][1])**2)
                        if closest_distance is None or distance < closest_distance:
                            closest_resource = resource
                            closest_distance = distance
                    resource_list.append(closest_resource)
                    resource_list_filtered.remove(closest_resource)
            # If no resources have been found
            else:
                clicked_resource = True
        else:
            h, w = template.shape[:2]
            resource = resource_list.pop(0)
            middle_pos = [int(resource[0] + w * 0.5), int(resource[1] + h * 0.15)]
            click_cursor_on([middle_pos[0] + game_region[0], middle_pos[1] + game_region[1]], shift=True, offset=offset)
            clicked_resource = True
    except (OSError, AttributeError):
        reset_variables()
        log("Invalid resource type.")


def harvest_resources():
    global resources_to_check
    # If no resources have been checked yet on this map
    if not resources_to_check:
        resources_to_check = resources_of_interest.copy()
    resource = resources_to_check[0]
    # If all resources of a type have been clicked, remove it from the list
    if clicked_resource and not resource_list:
        resources_to_check.pop(0)
    else:
        harvest_resources_on_screen(resource)
    # If all resources on this map have been checked
    if not resources_to_check:
        reset_variables(reset_status=False)
        log("Finished harvesting resources on this map.")
        follow_path()


def sell_item(item_type):
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
        resource_amount = pytesseract.image_to_string(resource_amount_filtered)
        resource_amount = int(re.findall(r'\d+', resource_amount)[0])
        if resource_amount >= 100:
            click_cursor_on([item[0], item[1]], offset=offset)
            # If the price isn't known yet
            if last_known_price == 0:
                pack_text = pyautogui.locateOnScreen('market_pack.png', confidence=0.90)
                # Filters the text beneath pack to find a pack of 100 for sale
                packs_cropped = screenshot_hsv[pack_text[1]+22:pack_text[1]+144, pack_text[0]:pack_text[0]+pack_text[2], :]
                lower_hsv = np.array([30, 0, 160])
                higher_hsv = np.array([45, 15, 200])
                packs_cropped_filtered = cv2.inRange(packs_cropped, lower_hsv, higher_hsv)
                pack_100_template = cv2.imread('100.png', cv2.IMREAD_GRAYSCALE)
                matches = cv2.matchTemplate(packs_cropped, pack_100_template, cv2.TM_SQDIFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matches)
                cv2.imwrite('omg.png', packs_cropped_filtered)
                pack_size_1 = pytesseract.image_to_string(packs_cropped_1_filtered)
                print(pack_size_1)
                pack_size_1 = int(re.findall(r'\d+', pack_size_1)[0])
                # Check the first 3 rows to see which contains a pack size of 100
                print(pack_size_1)
                price_cropped = None
                if pack_size_1 != 100:
                    packs_cropped_2 = screenshot_hsv[pack_text[1]+62:pack_text[1]+104, pack_text[0]:pack_text[0]+pack_text[2], :]
                    packs_cropped_2_filtered = cv2.inRange(packs_cropped_2, lower_hsv, higher_hsv)
                    pack_size_2 = pytesseract.image_to_string(packs_cropped_2_filtered)
                    pack_size_2 = int(re.findall(r'\d+', pack_size_2)[0])
                    if pack_size_2 != 100:
                        packs_cropped_3 = screenshot_hsv[pack_text[1]+104:pack_text[1]+144, pack_text[0]:pack_text[0]+pack_text[2], :]
                        packs_cropped_3_filtered = cv2.inRange(packs_cropped_3, lower_hsv, higher_hsv)
                        pack_size_3 = pytesseract.image_to_string(packs_cropped_3_filtered)
                        pack_size_3 = int(re.findall(r'\d+', pack_size_3)[0])
                        if pack_size_3 != 100:
                            reset_variables()
                            log('ERROR: cannot find price for a batch of 100 {}. Bot stopped.'.format(item_type))
                        else:
                            price_cropped = screenshot_hsv[pack_text[1]+104:pack_text[1]+144,
                                              pack_text[0]+pack_text[2]:pack_text[0]+126, :]
                    else:
                        price_cropped = screenshot_hsv[pack_text[1]+62:pack_text[1]+104,
                                          pack_text[0]+pack_text[2]:pack_text[0]+126, :]
                else:
                    price_cropped = screenshot_hsv[pack_text[1]+22:pack_text[1]+62,
                                      pack_text[0]+pack_text[2]:pack_text[0]+126, :]
                if price_cropped is not None:
                    price_cropped_filtered = cv2.inRange(price_cropped, lower_hsv, higher_hsv)
                    price = pytesseract.image_to_string(price_cropped_filtered)
                    price = int(re.findall(r'\d+', pack_size_1)[0])
                    print(price)

            return True
        else:
            last_known_price = 0
            return False
    else:
        last_known_price = 0
        return False


def sell_on_market():
    global resources_to_check
    market_text = pyautogui.locateCenterOnScreen('market_text.png')
    if market_text is None:
        # If the market isn't open yet
        # Takes a screenshot with and without highlight
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
        # Searches for the template and filters the best matches
        template_market = cv2.imread('market_binary.png', cv2.IMREAD_GRAYSCALE)
        matches = cv2.matchTemplate(highlights_filtered, template_market, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matches)
        h, w = template_market.shape[:2]
        position = [int(min_loc[0]+(w/2)+game_region[0]), int(min_loc[1]+(h/2)+ game_region[1])]
        # Hovers over the best match and see if the market text popped up
        if hover_find(position, 'Resource Marketplace'):
            click_cursor_on([position[0], position[1]], offset=offset)
        else:
            reset_variables()
            log("Can't find market. Bot activity stopped.")
    else:
        # If market is open
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
            reset_variables(reset_status=False)
            log("Finished selling resources. Bot stopped.")


def sell_resources():
    if current_coordinates[1] != market_pos[1]:
        if current_coordinates[1] > market_pos[1]:
            exit_map('north')
        elif current_coordinates[1] < market_pos[1]:
            exit_map('south')
        else:
            reset_variables()
            log('ERROR: faulty coordinates.')
    elif current_coordinates[0] != market_pos[0]:
        if current_coordinates[0] > market_pos[0]:
            exit_map('west')
        elif current_coordinates[0] < market_pos[0]:
            exit_map('east')
        else:
            reset_variables()
            log('ERROR: faulty coordinates.')
    elif current_coordinates == market_pos:
        sell_on_market()
        reset_variables()
        log('Reached market. Bot stopped.')
    else:
        reset_variables()
        log('ERROR: faulty coordinates.')


def exit_map(direction):
    global status, previous_status
    previous_status = status
    status = 'moving'
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


def follow_path():
    if current_path:
        direction = current_path.pop(0)
        current_path.append(direction)
        if direction == 'n':
            log("Heading north.")
            exit_map('north')
        elif direction == 'e':
            log("Heading east.")
            exit_map('east')
        elif direction == 's':
            log("Heading south.")
            exit_map('south')
        elif direction == 'w':
            log("Heading west.")
            exit_map('west')
        else:
            reset_variables()
            log("ERROR: invalid direction {}.".format(direction))
        update_gui()
    else:
        reset_variables()
        log("No path set to follow. Bot stopped.")


def inventory_full():
    global status
    log('Inventory is full.')
    status = 'sell_resources'
    sell_resources()


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
            # Wait with doing something else until you finish moving
            if status != 'moving':
                inventory_full()
        click_cursor_on([close_button_pos[0], close_button_pos[1]], leave_map=True)
    if status == 'moving':
        # Copies the area where your position is shown
        top_left = screenshot_hsv[70:97, 16:150, :]
        lower_hsv = np.array([15, 0, 215])
        higher_hsv = np.array([30, 20, 230])
        top_left_filtered = cv2.inRange(top_left, lower_hsv, higher_hsv)
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
    # TODO check pvp, trade, battle


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
    if status == 'harvest_resources':
        harvest_resources()
    elif status == 'sell_resources':
        sell_resources()
    gui.after(10, loop)


game_region = (0, 0, 0, 0)
status = ''
previous_status = ''
global_status = ''
clicked_resource = False
resource_list = []
resources_to_check = []

current_coordinates = [0, 0]
current_path = []
market_pos = [0, 0]
resources_of_interest = []
last_known_price = 0

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

path_text = tk.Label(gui, text="Current path: (n)orth (e)ast (s)outh (w)est")
path_input = tk.Entry(gui)
path_text.pack()
path_input.pack()

market_pos_text = tk.Label(gui, text="Nearest market position: x,y")
market_pos_input = tk.Entry(gui)
market_pos_text.pack()
market_pos_input.pack()

wheat_checkbox = tk.Checkbutton(gui, text='Wheat', variable=wheat_interested)
wheat_checkbox.pack()

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
