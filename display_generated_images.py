import os
import time
import cv2
import numpy as np

directory_to_watch = r"factorit_logos_selected"

image_shown = ""
processed_images = set()

# Get screen dimensions
screen_width, screen_height = 2560, 1440  # Adjust these values according to your screen resolution

while True:
    # List all files in the directory
    current_files = os.listdir(directory_to_watch)
    
    images = [img_file for img_file in current_files if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    current_images = set(images)
    new_images = current_images-processed_images

    if len(new_images) > 0:
        for i in new_images:
            image_shown = i
            break
        img = cv2.imread(os.path.join(directory_to_watch, image_shown))

        # Resize image to fit the screen
        scaling_x = screen_width/img.shape[1]
        scaling_y = screen_height/img.shape[0]
        scaling = min(scaling_x, scaling_y)
        img = cv2.resize(img, (0, 0), fx=scaling, fy=scaling, interpolation=cv2.INTER_LINEAR)

    # Calculate the position to center the image
    x_position = (screen_width - img.shape[1]) // 2
    y_position = (screen_height - img.shape[0]) // 2

    # Create a black canvas (background) with screen dimensions
    background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    # Paste the image on the black canvas at the calculated position
    background[y_position:y_position + img.shape[0], x_position:x_position + img.shape[1]] = img

    # Create a new fullscreen window if it does not already exist
    cv2.namedWindow("Generated image", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Generated image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # Show the image
    cv2.imshow("Generated image", background)

    processed_images = current_images
    # Wait for a short period before checking again
    key_input = cv2.waitKey(5000)
    # If the user pressed the escape key, quit the program
    if key_input == 27:
        break

cv2.destroyAllWindows()

