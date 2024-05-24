import pygetwindow as gw
import cv2 as cv
import win32gui, win32con, win32api
import math
import random
import keyboard
from windowcapture import WindowCapture
from pyHM import mouse
from time import sleep
from threading import Lock

class botFunctions:

    state = None # Current state of the bot
    keys = [] # List to store the keys to be pressed
    
    def __init__(self, window_name):
        self.wincap = WindowCapture(window_name)
        self.toggle_aimclick_state = 0
        self.toggle_movement_state = 0
        self.text = None
        self.lock = Lock()

    # Gets the center coordinates of the window
    def get_window_center(self, window_title):
        # Find the window by title
        window = gw.getWindowsWithTitle(window_title)[0]

        # Get the window handle
        hwnd = window._hWnd

        # Get the window rectangle
        window_rect = win32gui.GetWindowRect(hwnd)

        # Calculate the center coordinates
        x = (window_rect[0] + window_rect[2]) // 2
        y = (window_rect[1] + window_rect[3]) // 2

        return x, y

    # Gets the click points (center points) of the rectangle
    def get_click_points(r):
        points = []
        
        # Looping all the locations and drawing their r
        for (x, y, w, h) in r:
            centerX = (w - x) / 2 + x
            centerY = (h - y) / 2 + y

            # Save the points
            points.append((centerX, centerY))

        return points
    
    # Finds the coordinates of the closest target
    def findClosestTargetCoords(self, rectangles):
        if rectangles != []:
            targets = botFunctions.get_click_points(rectangles)
            target = self.wincap.get_screen_position(targets[0])
            target_pos = int(target[0]), int(target[1])
            return target_pos

    # Aims at the closest target and clicks
    def aimandclick(self, rectangles):
        if self.toggle_aimclick_state == 1:
            if rectangles != []:         
                x, y = self.findClosestTargetCoords(rectangles)
                try:
                    mouse.move(x, y, multiplier=0.01)
                except Exception:
                    print("Mouse Movement Exception")
                self.click()
    
    # Aims at the closest target
    def aim(self, rectangles):
        if self.toggle_aimclick_state == 1:
            if rectangles != []:
                x, y = self.findClosestTargetCoords(rectangles)
                try:
                    mouse.move(x, y, multiplier=0.01)
                except Exception:
                    print("ignored the exception")

    # Click directly to a specific window
    def send_left_click(window_handle, x, y):
        # Set the window as the foreground window
        win32gui.SetForegroundWindow(window_handle)

        # Convert screen coordinates to client coordinates
        point = win32gui.ScreenToClient(window_handle, (x, y))
        x, y = point

        # Send left mouse button down and up events
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    # Click function directly from windows
    def click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        sleep(.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0) 

    # Show the button press texts
    def paste_text_button_press(self, screenshot):
        font = cv.FONT_HERSHEY_SIMPLEX
        fontSize = 1
        color = (100, 255, 0)
        thickness = 2
        lineType = cv.LINE_AA

        if len(self.keys) > 0:
            if len(self.keys) > 1:
                current_key = ''.join(self.keys)
            else:
                current_key = self.keys[0]
            cv.putText(screenshot, str(current_key), (150, 115), font, fontSize, color, thickness, lineType) # put on combined_image to not affect the detection below
        else:
            cv.putText(screenshot, "N/A", (140, 115), font, 0.9, (255, 0, 0), thickness, lineType) # put on combined_image to not affect the detection below

        cv.putText(screenshot, "Pressing", (7, 115), font, 0.9, (0, 0, 0), thickness, lineType)    
        cv.putText(screenshot, "Bot State", (7, 300), font, fontSize, (255, 255, 255), thickness, lineType)    
        cv.putText(screenshot, self.state, (7, 350), font, fontSize, (255, 255, 255), thickness, lineType)    

    # Display the current bot states
    def paste_text_toggle(self, screenshot):
        if self.toggle_aimclick_state == 0:
            self.text = 'Aimbot OFF'
            cv.putText(screenshot, self.text, (7, 150), cv.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2, cv.LINE_AA)
        elif self.toggle_aimclick_state == 1:
            self.text = 'Aimbot ON'
            cv.putText(screenshot, self.text, (7, 150), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2, cv.LINE_AA)
        
        if self.toggle_movement_state == 0:
            self.text = 'Movement OFF'
            cv.putText(screenshot, self.text, (7, 250), cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv.LINE_AA)
        elif self.toggle_movement_state == 1:
            self.text = 'Movement ON'
            cv.putText(screenshot, self.text, (7, 250), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv.LINE_AA)

    # Toggle the bot states
    def button_press_click_state(self):
        if keyboard.is_pressed('p') and self.toggle_aimclick_state == 0:
            sleep(.3)
            self.toggle_aimclick_state = 1
        elif keyboard.is_pressed('p') and self.toggle_aimclick_state == 1:
            sleep(.3)
            self.toggle_aimclick_state = 0
            
        if keyboard.is_pressed('m') and self.toggle_movement_state == 0:
            sleep(.3)
            self.toggle_movement_state = 1
        elif keyboard.is_pressed('m') and self.toggle_movement_state == 1:
            sleep(.3)
            self.toggle_movement_state = 0
            self.release(self.keys)

    # Calculate the angle relative to the player's position
    def calculate_angle(self, player_x, player_y, target_x, target_y):
        angle_in_radians = math.atan2(-(player_y - target_y), player_x - target_x)
        angle_in_degrees = math.degrees(angle_in_radians)
        angle_in_degrees = (angle_in_degrees + 360) % 360
        return angle_in_degrees
    # Calculate the distance between two points
    def calculate_distance(self, x1, y1, x2, y2):
        d = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return d
    # Presses and releases a list of keys
    def perform_keyboard_action(self, keys):
        for key in keys:
            keyboard.press(key)
        sleep(0.1)
        for key in keys:
            keyboard.release(key)
    # Presses a list of keys
    def press(self, keys):
        if keys: # If there are keys in the list, the press them.
            for key in keys:
                keyboard.press(key)
    # Releases a list of keys
    def release(self, keys):
        if keys: # If there are key presses
            for key in keys:
                keyboard.release(key)
            keys.clear()
    # Professional movement that searches for targets, chargest at them, avoids collisions, and runs away
    def proMovement(self, rectangles, player_x, player_y):
        if self.toggle_movement_state == 1:
            if len(rectangles) > 0: # If it detects an target

                target_x, target_y = self.findClosestTargetCoords(rectangles)
                
                player_radius = 150 # First radius
                player_radius2 = 200 # Second Radius
                player_y += 50
                
                # Distance Formula: distance = sqrt((x2-x1)^2 + (y2-y1)^2)
                # Need to flip the y-axis because this isnt the standard Cartesian coordinate system
                distance = self.calculate_distance(target_x, target_y, player_x, player_y)

                # Calculate the angle relative to the player's position: angle = atan2(y2-y1, x2-x1)
                #angle = self.calculate_angle(player_x, player_y, target_x, target_y)
                angle = self.calculate_angle(target_x, target_y, player_x, player_y,)

                # Determine the movement direction based on angle and distance
                # Check distance from player radius
                if distance > player_radius:
                    self.state = "charging"
                    # Moving toward
                    if angle < 30 or angle >= 330:
                        if not keyboard.is_pressed('d'):
                            self.release(self.keys)
                            self.keys.append('d')
                            self.press(self.keys)
                    elif 30 <= angle < 60:
                        if not keyboard.is_pressed('d') and not keyboard.is_pressed('w'):
                            self.release(self.keys)
                            self.keys.extend(['d', 'w'])
                            self.press(self.keys)
                    elif 60 <= angle < 120:
                        if not keyboard.is_pressed('w'):  
                            self.release(self.keys)
                            self.keys.append('w')
                            self.press(self.keys)
                    elif 120 <= angle < 150:
                        if not keyboard.is_pressed('a') and not keyboard.is_pressed('w'):
                            self.release(self.keys)
                            self.keys.extend(['a', 'w'])
                            self.press(self.keys)
                    elif 150 <= angle < 210:
                        if not keyboard.is_pressed('a'):  
                            self.release(self.keys)
                            self.keys.append('a')
                            self.press(self.keys)
                    elif 210 <= angle < 240:
                        if not keyboard.is_pressed('a') and not keyboard.is_pressed('s'):
                            self.release(self.keys)
                            self.keys.extend(['a', 's'])
                            self.press(self.keys)
                    elif 240 <= angle < 300:
                        if not keyboard.is_pressed('s'):  
                            self.release(self.keys)
                            self.keys.append('s')
                            self.press(self.keys)
                    elif 300 <= angle < 330:
                        if not keyboard.is_pressed('d') and not keyboard.is_pressed('s'):
                            self.release(self.keys)
                            self.keys.extend(['d', 's'])
                            self.press(self.keys)
                # Moving away until target is outside radius
                elif distance <= player_radius:
                    self.state = "fleeing"
                    # Check angle ranges for movement directions
                    if angle < 30 or angle >= 330:
                        if not keyboard.is_pressed('a'):  
                            self.release(self.keys)
                            self.keys.append('a')
                            self.press(self.keys)
                    elif 30 <= angle < 60:
                        if not keyboard.is_pressed('a') and not keyboard.is_pressed('s'):
                            self.release(self.keys)
                            self.keys.extend(['a', 's'])
                            self.press(self.keys)
                    elif 60 <= angle < 120:
                        if not keyboard.is_pressed('s'):  
                            self.release(self.keys)
                            self.keys.append('s')
                            self.press(self.keys)
                    elif 120 <= angle < 150:
                        if not keyboard.is_pressed('d') and not keyboard.is_pressed('s'):
                            self.release(self.keys)
                            self.keys.extend(['d', 's'])
                            self.press(self.keys)
                    elif 150 <= angle < 210:
                        if not keyboard.is_pressed('d'):  
                            self.release(self.keys)
                            self.keys.append('d')
                            self.press(self.keys)
                    elif 210 <= angle < 240:
                        if not keyboard.is_pressed('d') and not keyboard.is_pressed('w'):
                            self.release(self.keys)
                            self.keys.extend(['d', 'w'])
                            self.press(self.keys)
                    elif 240 <= angle < 300:
                        if not keyboard.is_pressed('w'):  
                            self.release(self.keys)
                            self.keys.append('w')
                            self.press(self.keys)
                    elif 300 <= angle < 330:
                        if not keyboard.is_pressed('a') and not keyboard.is_pressed('w'):
                            self.release(self.keys)
                            self.keys.extend(['a', 'w'])
                            self.press(self.keys)
                    # Moving away until target is outside radius2
                    elif distance <= player_radius2 and distance > player_radius:
                        self.state = "fleeing"
                        # Check angle ranges for movement directions
                        if angle < 30 or angle >= 330:
                            if not keyboard.is_pressed('a'):  
                                self.release(self.keys)
                                self.keys.append('a')
                                self.press(self.keys)
                        elif 30 <= angle < 60:
                            if not keyboard.is_pressed('a') and not keyboard.is_pressed('s'):
                                self.release(self.keys)
                                self.keys.extend(['a', 's'])
                                self.press(self.keys)
                        elif 60 <= angle < 120:
                            if not keyboard.is_pressed('s'):  
                                self.release(self.keys)
                                self.keys.append('s')
                                self.press(self.keys)
                        elif 120 <= angle < 150:
                            if not keyboard.is_pressed('d') and not keyboard.is_pressed('s'):
                                self.release(self.keys)
                                self.keys.extend(['d', 's'])
                                self.press(self.keys)
                        elif 150 <= angle < 210:
                            if not keyboard.is_pressed('d'):  
                                self.release(self.keys)
                                self.keys.append('d')
                                self.press(self.keys)
                        elif 210 <= angle < 240:
                            if not keyboard.is_pressed('d') and not keyboard.is_pressed('w'):
                                self.release(self.keys)
                                self.keys.extend(['d', 'w'])
                                self.press(self.keys)
                        elif 240 <= angle < 300:
                            if not keyboard.is_pressed('w'):  
                                self.release(self.keys)
                                self.keys.append('w')
                                self.press(self.keys)
                        elif 300 <= angle < 330:
                            if not keyboard.is_pressed('a') and not keyboard.is_pressed('w'):
                                self.release(self.keys)
                                self.keys.extend(['a', 'w'])
                                self.press(self.keys)
            else:
                self.state = "searching"
                self.randomMovement()

        else:
            if self.keys:
                self.keys.clear()
                
    # Moves in random directions
    def randomMovement(self):
        if self.toggle_movement_state == 1:
                
            keys = ['w', 'a', 's', 'd', 'aw', 'dw', 'as', 'ds']

            key = random.choice(keys)

            if key == 'aw':
                if not keyboard.is_pressed(key):  
                    self.release(self.keys)
                    self.keys.extend(['a', 'w'])
                    self.press(self.keys)
                    (0.5)
            elif key == 'dw':
                if not keyboard.is_pressed(key):  
                    self.release(self.keys)
                    self.keys.extend(['d', 'w'])
                    self.press(self.keys)
                    (0.5)
            elif key == 'as':
                if not keyboard.is_pressed(key):  
                    self.release(self.keys)
                    self.keys.extend(['a', 's'])
                    self.press(self.keys)
                    (0.5)
            elif key == 'ds':
                if not keyboard.is_pressed(key):  
                    self.release(self.keys)
                    self.keys.extend(['d', 's'])
                    self.press(self.keys)
                    (0.5)
            else:
                self.release(self.keys)
                self.keys.append(key)
                self.press(self.keys)
                (0.5)

        else:
            if self.keys:
                self.keys.clear()

    def press_release(self, key_list):
        for key in key_list:
            keyboard.press(key)

        for key in key_list:
            keyboard.release(key)   
        self.keys.clear()      