from pynput import keyboard
import datetime
import time
import os
import sys

global password = 'passW0rd'
global count = 0 #keep track of password index for array

def on_press(key):
    try:
        #TODO log time and key in len(password) array
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(
        if (count >= len(password)):
            #check to see if password is correct. if so, add data to file
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

# # ...or, in a non-blocking fashion:
# listener = keyboard.Listener(
#     on_press=on_press,
#     on_release=on_release)
# listener.start()