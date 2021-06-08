from pynput import keyboard
import time
import os
import sys
import json
from contextlib import contextmanager

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try: yield
        finally: 
            sys.stdout = old_stdout
            sys.stderr = old_stderr


password = 'passW0rd!'
# count = 0 #keep track of password index for array
requirement = 400 #the number of lines we want in the file
buffer = [] 
totalData = []
startTime = None
endTime = None
shift_modifier = False
key_presses = 0
counter = 0
user = ''

def welcomeUser():
    global user 
    
    user = input('What is your name (no spaces)? \n') or 'data'
    user_file = f'{user}.txt'
    file = open(f'{user}.txt', 'a+')
    file = open(f'{user}.txt', 'r+')
    length = len(file.readlines())
    print('Welcome! Please input the password `{0}` {1} more times.'.format(password, requirement - length))
    print("Press enter to submit your password entry.")

def main():
    try:
        write_file(collect(2,0), (f'{user}.txt'))
    except KeyboardInterrupt:
        if (query_yes_no("Do you want to save your data?")): 
            write_file(totalData)
        else: print('Data not saved')
        sys.exit()
 
    # # global count
    # if (count == len(password)):
    #     print('hi')
    #     if (buffer == password):
    #         #write to file
    #         print('hi')

def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

def on_press(key):
    try:
        #TODO log time and key in len(password) array
        print('alphanumeric key {0} pressed'.format(
            key.char))
        count = count +1
        print(count)
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def push_down(key):
    global startTime
    global buffer
    global shift_modifier
    global key_presses
    global counter
    
    # potentially exit the listener
    if key == keyboard.Key.enter:
        endTime = time.time()
        key_presses = 0
        return False
    
    # process alphanumeric
    try:
        if startTime == None:
            startTime = time.time()
        buffer.append( (key.char, "DOWN", time.time() - startTime) )
        key_presses += 1
        print("\r" + "*" * key_presses, end ="")
    except AttributeError:
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            shift_modifier = True

def release(key):
    global startTime
    global buffer
    global shift_modifier
    
    try:
        if shift_modifier:
            buffer.append( (buffer[-1][0], "UP", time.time() - startTime) )
            shift_modifier = False
        else:
            buffer.append( (key.char, "UP", time.time() - startTime) )
    except AttributeError:
        pass

def password_entered(index, opener):
    global buffer
    for newIndex in range(index, len(buffer)):
        potentialCloser = buffer[newIndex]
        if potentialCloser[1] == "DOWN" and potentialCloser[0] == opener[0]:
            return True
    return False

def ensureCompleted():
    global endTime
    global startTime
    global buffer
    for index, opener in enumerate(buffer):

        # if this is already a closing entry, ignore it
        if opener[1] == "UP": continue
        
        # otherwise, check it's closed
        if not password_entered(index, opener):
            buffer.append((opener[0], "UP", endTime - startTime))

def find_prev(key):
    global buffer
    first = True
    for entry in buffer[::-1]:
        if first:
            first = False
            continue
        if entry[0] == key and entry[1] == "DOWN": return entry
        if entry[0] == key and entry[1] == "UP": return None
    return None

def find_prev_from_index(key, index):
    global buffer
    first = True
    index -= 1
    while index >= 0:
        entry = buffer[index]
        if entry[0] == key and entry[1] == "DOWN": return entry
        if entry[0] == key and entry[1] == "UP": return None
        index -=1
    return None

def clearRogueUps():
    global buffer
    if buffer[-1][1] == "UP":
        data = find_prev(buffer[-1][0])
        if data == None or data[1] == "UP":
            del buffer[-1]
    
    index = 0
    while True:
        if index == len(buffer): break
        entry = buffer[index]
        if entry[1] == "UP":
            data = find_prev_from_index(entry[0], index)
            if data == None or data[1] == "UP":
                del buffer[index]
                continue
        index += 1

def passwordProperlyEntered():
    global buffer
    global password
    
    buildString = ""
    for entry in buffer:
        if entry[1] == "DOWN": buildString += entry[0]
    return buildString == password

def collect(numPasswordsNeeded, numRunupNeeded, verbose = True):
    global buffer
    global endTime
    global startTime
    global shift_modifier
    global key_presses
    global counter
    
    if verbose: welcomeUser()
    totalData = []

    i = 0
    while i < numPasswordsNeeded + numRunupNeeded:
        with keyboard.Listener(on_press=push_down, on_release=release) as listener:
            listener.join()
        
        # ensure that all entries in the data are closed
        ensureCompleted()
        clearRogueUps()
        
        # clear the global variables again
        startTime = None
        endTime = None
        shift_modifier = False
        key_presses = 0
        counter = 0
        if passwordProperlyEntered():
            if i >= numRunupNeeded:
                totalData.append(buffer)
            if verbose: print("\nFantastic, now enter the password again! \
                (Trial {} of {}).".format(i + 1, numPasswordsNeeded + numRunupNeeded))
            i += 1
        else: print("\nPassword mis-entered.  Try again:")

        buffer = []


    if verbose: print("Great - we've finished gathering training data from you.  Please wait while we process this information")
    return totalData

def write_file(data=totalData, file=f'{user}.txt'):
    print(f'user_file: {user}')
    print(f'user: {user}')
    print(data)
    f = open(file, 'a+')
    json.dump(data, f)
    f.close()

# Collect events until released
# with keyboard.Listener(
                #write file
        # if(count >= len(password))
            #check to see if password is correct. if so, add data to file
        # on_press=on_press,
        # on_release=on_release) as listener:
    # listener.join()

# # ...or, in a non-blocking fashion:
# listener = keyboard.Listener(
#     on_press=on_press,
#     on_release=on_release)
# listener.start()

if __name__ == "__main__":
    main()
