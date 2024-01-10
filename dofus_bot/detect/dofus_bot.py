import pyautogui
import time
import numpy as np

def calibrate():
    global game_region
    buttons_pos = pyautogui.locateCenterOnScreen('menu_buttons1080.png', confidence=confidence)
    if buttons_pos is not None:
        game_region = (buttons_pos[0]-1050, 23, 1271, pyautogui.size()[1]-63)
    else:
        buttons_pos = pyautogui.locateCenterOnScreen('menu_buttons864.png', confidence=confidence)
        if buttons_pos is not None:
            game_region = (buttons_pos[0]-826, 23, 836+165, pyautogui.size()[1]-63)
        else:
            game_region = (0,0,0,0)
            print("Calibration failed! Menu buttons not visible.")

def farm_cereal_on_screen(cereal_type):
    cereal = pyautogui.locateAllOnScreen('{}.png'.format(cereal_type), region=game_region, confidence=confidence)
    cereal_pos = []
    last_pos = (0, 0)
    for match in cereal:
        if abs(last_pos[0]-match[0]) >= accuracy and abs(last_pos[1]-match[1]) >= accuracy:
            last_pos = (match[0], match[1])
            cereal_pos.append(last_pos)
    first_click = False
    for pos in cereal_pos:
        x_offset = np.random.randint(-1*offset,offset)
        y_offset = np.random.randint(-1*offset,offset)
        x_pos = pos[0]-5+x_offset
        y_pos = pos[1]+5+y_offset
        if x_pos <= game_region[0]+30:
            x_pos = game_region[0]+30
        elif x_pos >= game_region[0]+game_region[2]-30:
            x_pos = game_region[0]+game_region[2]-30
        cursor_pos = pyautogui.position()
        distance = np.sqrt((cursor_pos[0]-x_pos)**2 + (cursor_pos[1]-y_pos)**2)
        pyautogui.moveTo(x_pos, y_pos, distance/pixels_per_second, pyautogui.easeOutQuad)
        percentage = np.random.randint(0,100)/100
        time.sleep(delay*percentage)
        pyautogui.click()
        if not first_click:
            time.sleep(time_to_reach_resource)
        first_click = True
        time.sleep(delay*(1-percentage))
    
    # only do this when character finished farming (possibly check gain number color)
    '''
    cereal = pyautogui.locateAllOnScreen('{}.png'.format(cereal_type), region=game_region, confidence=confidence)
    for check in cereal: # checks if still cereal left on screen
        farm_cereal_on_screen(cereal_type)  # runs function again
        break   # just once
    '''
    

game_region = (0,0,0,0)
screen_height = 0

confidence = 0.65   # finding image matches
accuracy = 3    # distance in pixels between detections
pixels_per_second = 800 # how fast the cursor should move
delay = 0.25 # seconds to wait after each click
offset = 20     # max amount of pixels a click may be off from the center
time_to_reach_resource = 3

calibrate()

if game_region != (0,0,0,0):
    img = pyautogui.screenshot("test.png", region=game_region)
    farm_cereal_on_screen("wheat")



