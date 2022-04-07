import os
import sys

# ~~~~~Directory of this program~~~~~
def get_path():
    if getattr(sys, 'frozen', False): #If an executable, it needs to use this or it takes the temp folder as current path
        path = os.path.dirname(sys.executable)
    elif __file__: #if running as a python script
        path = os.path.dirname(__file__)
    return path


# ~~~~~Removes the beginning of a string
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


# ~~~~~Get the system settings~~~~~
def get_settings(selection, path):
    currSettings = []
    with open(path + '\Settings.txt', 'r') as f:
        currSettings = f.readlines()
    if selection == 'Interval':
        return remove_prefix(currSettings[0],'intervalReading = ').strip()
    elif selection == 'MaxTemp':
        return remove_prefix(currSettings[1],'tempWarning = ').strip()
    elif selection == 'LogFile':
        return remove_prefix(currSettings[2],'logFile = ').strip()
    

# ~~~~~Check if a file exists~~~~~
def does_this_exist(fileName):
    #VERIFY THE FILE EXISTS
    file_exists = os.path.exists(fileName)
    if not file_exists:
        path = get_path()
        file_exists = os.path.exists(path + '\\' + fileName)
    return file_exists