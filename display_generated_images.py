"""
This script was made to display images that were generated by a neural network.
The images will be displayed in fullscreen, with any newly generated/added images automatically being displayed.

Controls:
Escape = stop the script
Space = toggle displaying the prompt
"""
import os
import cv2
import numpy as np
import json

SUPPORTED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".dib", ".webp", ".sr", ".ras", ".tiff", ".tif")

# Path to the directory where the generated images are located
IMAGE_DIRECTORY = r"factorit_logos_selected"

# Create a new fullscreen window
cv2.namedWindow("Generated image", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Generated image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Detect the screen resolution based on the fullscreen window's size
window_dimensions = cv2.getWindowImageRect("Generated image")
screen_width = window_dimensions[2]
screen_height = window_dimensions[3]

show_prompt = False


def get_prompt(img_path):
    with open(img_path, 'rb') as file:
        # Check if the file is a PNG file by reading the first 8 bytes (PNG signature)
        signature = file.read(8)
        if signature[:8] != b'\x89PNG\r\n\x1a\n':
            print("Not a valid PNG file")
            return

        metadata = {}
        # Loop over each chunk in the image file
        while True:
            # Read the length of the current chunk
            length_bytes = file.read(4)
            if not length_bytes:
                break
            length = int.from_bytes(length_bytes, byteorder='big')

            # Read info from the chunk
            chunk_type = file.read(4).decode('ascii')
            data = file.read(length)
            crc = file.read(4)  # Cyclic Redundancy Check. Unused, but must be read

            # If it's a tEXt chunk, extract the metadata dictionary
            if chunk_type == 'tEXt':
                key, value = data.split(b'\x00', 1)
                metadata[key.decode('utf-8')] = json.loads(value)

        prompt = ''.join(metadata['prompt']['6']['inputs']['text'])
        return prompt


TEXT_HEIGHT = 30    # pixels


def add_text_to_image(image, text):
    chars_per_line = screen_width // 17
    words = text.split(' ')
    text_lines = []
    current_line = ""
    # Ensure line wrapping happens between words, to prevent words from being cut off
    for word in words:
        # Just add the word if this is a new line
        if not current_line:
            current_line = word
            continue
        # If the word would make the line too long, start a new line
        if len(current_line) + len(word) > chars_per_line:
            text_lines.append(current_line)
            current_line = word
            continue
        current_line += " " + word
    text_lines.append(current_line)

    for i, line in enumerate(text_lines, 1):
        text_pos_vert = TEXT_HEIGHT * i
        # First add the black border, then add the white text on top
        cv2.putText(image, line, (0, text_pos_vert), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 6, cv2.LINE_AA)
        cv2.putText(image, line, (0, text_pos_vert), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    return image


def scale_and_center_image(image):
    """
    Creates a black background, scales the image to fit the screen, and place it in the center of the screen.
    """
    # Create a black background to cover the entire screen
    background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    # Resize image to fit the screen, keeping the image ratio intact
    scaling_x = screen_width / image.shape[1]
    scaling_y = screen_height / image.shape[0]
    scaling = min(scaling_x, scaling_y)
    image = cv2.resize(image, (0, 0), fx=scaling, fy=scaling, interpolation=cv2.INTER_LINEAR)

    # Calculate the position to center the image
    x_position = (screen_width - image.shape[1]) // 2
    y_position = (screen_height - image.shape[0]) // 2
    # Paste the image on the black background at the calculated position
    background[y_position:y_position + image.shape[0], x_position:x_position + image.shape[1]] = image
    return background


def get_file_creation_time(filename):
    return os.path.getctime(os.path.join(IMAGE_DIRECTORY, filename))


while True:
    # Get all images in the directory
    files = os.listdir(IMAGE_DIRECTORY)
    image_names = [img_file for img_file in files if img_file.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)]
    # Sort images based on creation time
    image_names = sorted(image_names, key=get_file_creation_time)

    # Get the latest image
    latest_image = image_names[-1]
    image_path = os.path.join(IMAGE_DIRECTORY, latest_image)
    img = cv2.imread(image_path)

    # Position the image
    img = scale_and_center_image(img)

    # Add the prompt that was used to generate the image
    if show_prompt:
        prompt = get_prompt(image_path)
        add_text_to_image(img, prompt)

    # Show the image
    cv2.imshow("Generated image", img)

    # Wait for a short period while handling input
    key_input = cv2.waitKey(2000)
    # If the user pressed the escape key, quit the program
    if key_input == 27:
        break
    # If the user pressed space, toggle showing the prompt
    elif key_input == 32:
        show_prompt = not show_prompt

cv2.destroyAllWindows()

