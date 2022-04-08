import os
import sys
import csv

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
    with open(path + 'Settings.txt', 'r') as f:
        currSettings = f.readlines()
    if selection == 'Interval':
        return remove_prefix(currSettings[0],'intervalReading = ').strip()
    elif selection == 'MaxTemp':
        return remove_prefix(currSettings[1],'tempWarning = ').strip()
    elif selection == 'LogFile':
        return remove_prefix(currSettings[2],'logFile = ').strip()
    elif selection == 'MaxRecords':
        return remove_prefix(currSettings[3],'maxLogRecords = ').strip()
    

# ~~~~~Check if a file exists~~~~~
def does_this_exist(fileName):
    #VERIFY THE FILE EXISTS
    file_exists = os.path.exists(fileName)
    if not file_exists:
        path = get_path()
        file_exists = os.path.exists(path + '\\' + fileName)
    return file_exists


# ~~~~~Make settings file if not present~~~~~
def verify_settings(path):
    if does_this_exist(path + 'Settings.txt'):
        return True
    
    #Create file that could not be found
    with open(path + 'Settings.txt', 'w') as f:
       f.write('intervalReading = {}'.format(10))
       f.write('\n')
       f.write('tempWarning = {}'.format(1300))
       f.write('\n')
       f.write('logFile = {}'.format('AllTempLogs.csv'))
       f.write('\n')
       f.write('maxLogRecords = {}'.format(1000))
    
    return False


# ~~~~~Make Log file if not present~~~~~
def verify_logs(path):
    logFile = get_settings('LogFile', path)
    if does_this_exist(path + logFile):
        return True
    
    with open(path + logFile, 'w', newline='') as f:
        
        writer = csv.writer(f)
        writer.writerow(['Time','Temp1','Temp2','Temp3','Temp4','Temp5','Temp6'])
        writer.writerow(['01/01/2022 00:03',1,1,1,1,1,1])
        writer.writerow(['01/01/2022 00:02',2,2,2,2,2,2])
        writer.writerow(['01/01/2022 00:01',3,3,3,3,3,3])
    
    
# ~~~~~Get saved charges~~~~~
def get_charges(path):
    files = [f.strip('.csv') for f in os.listdir(path) if os.path.exists(path + f)] #collect all files in the folder
    return files
    
    
    
    