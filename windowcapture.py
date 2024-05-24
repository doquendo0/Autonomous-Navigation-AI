import numpy as np
import win32gui, win32ui, win32con
from threading import Lock
import ctypes
import pygetwindow as gw
from win32com.client import GetObject
import os

# Query DPI Awareness
a = ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(ctypes.c_int()))
# Set DPI Awareness
b = ctypes.windll.shcore.SetProcessDpiAwareness(2)

class WindowCapture:
    # Properties
    lock = None
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0
    runOnce = False
    previousWindowName = None

    def __init__(self, window_name=None, border_pixels=8, titlebar_pixels=112, right_side=0, left_side=0, bottom_side=0):
        # create a thread lock object
        self.lock = Lock()

        # Capture entire screen if no window name was given
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            # Find the handle for the window we want to capture
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception('Window not found: {}'.format(window_name))

        # define monitor width and height
        #self.w = 2560
        #self.h = 1440

        # Get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # Cut off the window border and title bar
        self.w = self.w - (border_pixels*2) - right_side
        self.h = self.h - titlebar_pixels - border_pixels - bottom_side
        self.cropped_x = border_pixels + left_side
        self.cropped_y = titlebar_pixels

        # Set the cropped coordinates offset for translating the screenshot image into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    # Captures a screenshot of the specified window and process it for use with OpenCV
    def get_screenshot(self):  

        # Get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj=win32ui.CreateDCFromHandle(wDC)
        cDC=dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # Save the screenshot
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype = 'uint8')
        img.shape = (self.h, self.w, 4)

        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # Drop the alpha channel to avoid the cv.matchTemplate() error
        img = img[...,:3]

        # Make the image contiguous in memory to prevent potential errors
        img = np.ascontiguousarray(img)

        return img

    @staticmethod
    # List all of the visible windows
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
           if win32gui.IsWindowVisible(hwnd):
              print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # Close all instances of cmd
    def closecmd(self):  
        WMI = GetObject('winmgmts:')
        processes = WMI.InstancesOf('Win32_Process')
        for p in WMI.ExecQuery('select * from Win32_Process where Name="cmd.exe"'):
            os.system("taskkill /pid "+str(p.Properties_('ProcessId').Value))

    # Brings the specified window to the front and activates it
    def bring_window_to_front(self, bot_vision_window):
        if self.previousWindowName == bot_vision_window:
            self.runOnce = False
        self.previousWindowName = bot_vision_window
        
        if self.runOnce:
            return

        try:
            outputwindow = gw.getWindowsWithTitle(bot_vision_window)
            if outputwindow != []:
                try:
                    outputwindow[0].activate()
                except:
                    outputwindow[0].minimize()
                    outputwindow[0].restore()
                    
            win = gw.getWindowsWithTitle(bot_vision_window)[0]
            win.activate()
            self.runOnce = True
        except Exception:
            print("Cannot bring the window to the front")
    
    # Convert the given position to screen coordinates
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)