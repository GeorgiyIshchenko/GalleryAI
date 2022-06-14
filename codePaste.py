import os
import sys
from time import sleep
import keyboard

GET_PATH = ['./ai/', './core/', './photosii/', './photosii/templates']
WRITE_FILENAME = True
ALT_SLEEP_TIME = 0.6
SKIP_PRECOMMENT = True
WITH_BORDERS = True

sleep(2)

keyboard.add_hotkey('escape', sys.exit)

for curPath in GET_PATH:
    files = []
    for filename in os.listdir(curPath):
        files.append(filename)

    files.sort(reverse=True)
    files.sort(key=lambda x: x[0])

    for filename in files:
        if filename.split('.')[-1] == "py" or filename.split('.')[-1] == "html":
            with open(os.path.join(curPath, filename), 'r') as f:
                try:
                    data = f.readlines()
                    if WRITE_FILENAME:
                        keyboard.send('ctrl+i')
                        keyboard.write(filename)
                        keyboard.send('ctrl+i')
                        keyboard.send('enter')

                    if WITH_BORDERS:
                        keyboard.send('alt')  # borders on
                        sleep(ALT_SLEEP_TIME)
                        keyboard.send('z')
                        keyboard.send('f')
                        keyboard.send('u')
                        keyboard.send('i')

                    keyboard.release('alt')
                    skip = None
                    one = False
                    stop = False
                    for line in data:
                        if not stop:
                            if line.find('/*') != -1 and skip == None:
                                skip = True
                            elif line.find('*/') != -1:
                                skip = False
                                one = True
                                continue
                            if skip:
                                continue
                            if one:
                                one = False
                                stop = True
                                continue
                        keyboard.write(line)
                        sleep(0.025)
                    sleep(2)

                    keyboard.send('alt')
                    sleep(ALT_SLEEP_TIME)
                    keyboard.send('c')
                    keyboard.send('g')  # page
                    keyboard.send('g')

                    if WITH_BORDERS:
                        keyboard.send('alt')  # borders off
                        sleep(ALT_SLEEP_TIME)
                        keyboard.send('z')
                        keyboard.send('f')
                        keyboard.send('u')
                        keyboard.send('i')
                except:
                    print('err')
