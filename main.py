import cv2 as cv
import numpy as np
import torch
import keyboard
import math
from time import time
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from bot import botFunctions
from windowcapture import WindowCapture

window_name = 'diep.io - Google Chrome'
bot_vision_window = 'Bot Vision'

folder_path = 'yolov5-master'
weights_path = 'best.pt'

# Initialize the botFunctions Class
bf = botFunctions(window_name)

# Loading Detector
model = torch.hub.load(folder_path, 'custom', path = weights_path, source = 'local', force_reload = True).autoshape()

# Get the pixel coordinates of the center of the window
center_x, center_y = bf.get_window_center(window_name)

# Initialize the WindowCapture Class
wincap = WindowCapture(window_name)

# Bring the game window to the front
wincap.bring_window_to_front(window_name)

# Get the Image of the Game for the Height of the Menu
screenshot = wincap.get_screenshot()

# Properties Menu
menu_width = 200
menu_height = screenshot.shape[0]
menu_color = (0, 0, 255) 
menu_text_color = (255, 255, 255)
menu_text = 'Properties'
menu_font = cv.FONT_HERSHEY_COMPLEX_SMALL
menu_fontSize = 1
menu_thickness = 2

# Create the Menu Image
menu_image = np.zeros((menu_height, menu_width, 3), dtype=np.uint8)
menu_image[:] = menu_color

# Add Text to the Menu
text_size_width = cv.getTextSize(menu_text, menu_font, menu_fontSize, menu_thickness)[0]
text_position = (0, 25)
cv.putText(menu_image, menu_text, text_position, cv.FONT_HERSHEY_SIMPLEX, 1, menu_text_color, 2)

# FPS Font Settings
fps_font = cv.FONT_HERSHEY_SIMPLEX
fps_fontSize = 1
fps_color = (100, 255, 0)
fps_thickness = 2
fps_lineType = cv.LINE_AA

while True:

    # Time when we finish processing for this frame
    start_time = time()

    # Get an Updated Image of the Game
    screenshot = wincap.get_screenshot()

    # Convert the color space
    screenshot_new = cv.cvtColor(screenshot, cv.COLOR_BGRA2RGB)

    x_size = screenshot_new.shape[1]
    y_size = screenshot_new.shape[0]

    # passing converted screenshot into model
    # 800 since the model was trained with that resolution, if lowered the fps will increase but the detection results will decrease
    # results = model(screenshot_new, 800)
    results = model(screenshot_new, 600)

    # confidence score
    model.conf = 0.75

    # Access the predicted bounding box coordinates
    targetCoords = results.xyxy

    # READING OUTPUT FROM MODEL AND DETERMINING DISTANCES TO TARGETS FROM CENTER OF THE WINDOW
    # Get number of targets / num of the rows of .xyxy[0] array
    targetNum = targetCoords[0].shape[0]

    # Reset distances array to prevent duplicating items
    distances = []
    rectangles = []

    # Cycle through results and get closest result
    for i in range(targetNum):

        # (x, y) is the position of the target
        # (w, h) is the width and height of the drawn rectangle
        x = int(targetCoords[0][i, 0])
        y = int(targetCoords[0][i, 1])
        w = int(targetCoords[0][i, 2])
        h = int(targetCoords[0][i, 3])

        # Determine the center position
        centerX = (w - x) / 2 + x
        centerY = (h - y) / 2 + y

        # class name positions
        cnposX = (w - 50 - x) / 2 + x
        cnposY = (h - 55 - y) / 2 + y

        # show class name detected indexs from tensor array list
        show = targetCoords[0][i, 5].item()

        # Display Results(boxes)
        cv.rectangle(screenshot_new, (x,y), (w, h), (255, 0, 0), 1, cv.LINE_4)
        #cv.rectangle(combined_image, (x,y), (w, h), (255, 0, 0), 1, cv.LINE_4)

        # Show Class Names 
        cv.putText(screenshot_new, model.names[int(show)], (int(cnposX), int(cnposY)), 0, 0.5, (0, 0, 0), 1, cv.LINE_AA)

        # Calculate the distance from the center of the screen to the target
        distance = math.sqrt(((centerX - x_size / 2) ** 2) + ((centerY - y_size / 2) ** 2))

        distances.append(distance)

        # Get the shortest distance from the array (distances)
        closest = 2000

        # Get the shortest distance from the array (distances)
        for i in range(0, len(distances)):
            if distances[i] < closest:
                closest = distances[i]
                closestTarget = i

    # If we found results, run this
    if targetNum != 0:
        if len(targetCoords) > 0:

            # Getting the coordinates of the closest target
            x = float(targetCoords[0][closestTarget, 0])
            y = float(targetCoords[0][closestTarget, 1])
            w = float(targetCoords[0][closestTarget, 2])
            h = float(targetCoords[0][closestTarget, 3])

            rectangles = [[int(x), int(y), int(w), int(h)]]

    # Display Results(the boxes)
    # results.display(render=True)

    # Draw the radiuses
    cv.circle(screenshot_new, (int(x_size/2), int(y_size/2)), 135, (255, 24, 24),2)
    cv.circle(screenshot_new, (int(x_size/2), int(y_size/2)), 185, (224, 136, 58),2)

    # Combine the Menu and Game Screenshot
    screenshot_menu = np.concatenate((menu_image, screenshot_new), axis=1)

    fps = int(1 / (time() - start_time))

    # Putting the FPS Count on the Frame
    cv.putText(screenshot_menu, str(fps), (7, 70), fps_font, fps_fontSize, fps_color, fps_thickness, fps_lineType) # put on combined_image to not affect the detection below

    # Visual text for current button press
    bf.paste_text_button_press(screenshot_menu)
    
    # Visual text for aim and movement toggle
    bf.paste_text_toggle(screenshot_menu)

    # Display the images
    cv.imshow(bot_vision_window, cv.cvtColor(screenshot_menu, cv.COLOR_RGB2BGR))
    # cv.imshow('Computer Vision', screenshot)

    # loop_time = time()

    d = Thread(target=bf.button_press_click_state).start()

    # Toggle Aimbot Thread
    t = Thread(target=bf.aimandclick, args=(rectangles,)).start()

    # Toggle Movement Thread
    g = ThreadPoolExecutor(max_workers = 1).submit(bf.proMovement, rectangles, center_x, center_y)

    wincap.bring_window_to_front(bot_vision_window)

    wincap.bring_window_to_front(window_name)

    # Press 'q' to Exit Window
    key = cv.waitKey(1)
    if keyboard.is_pressed('q'):
        cv.destroyAllWindows()
        wincap.closecmd()
        break

    # Press 'v' to take a screenshot
    # elif keyboard.is_pressed('v'):
    #     cv.imwrite('C:/Users/Mare/Documents/db/images/{}.png'.format(loop_time), screenshot)
    #     sleep(.5)