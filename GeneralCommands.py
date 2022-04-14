import os
import sys
import csv
import win32com.client
import serial
from time import sleep

# ~~~~~Directory of this program~~~~~
def get_path():
    if getattr(sys, 'frozen', False): #If an executable, it needs to use this or it takes the temp folder as current path
        path = os.path.dirname(sys.executable)
    elif __file__: #if running as a python script
        path = os.path.dirname(__file__)
    return path + '\\'


# ~~~~~Removes the beginning of a string
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


# ~~~~~Get the system settings~~~~~
def get_settings(selection, path):
    currSettings = []
    if path == 'Pi':
        path = get_path()
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
    elif selection == 'Record':
        return remove_prefix(currSettings[4],'recordCharge = ').strip()
    elif selection == 'Email':
        return remove_prefix(currSettings[5],'emailTo = ').strip()
    elif selection == 'EmailAlert':
        return remove_prefix(currSettings[6],'enableEmail = ').strip()
    elif selection == 'Port':
        return remove_prefix(currSettings[7],'port = ').strip()
    

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
       f.write('intervalReading = {}\n'.format(10))
       f.write('tempWarning = {}\n'.format(1300))
       f.write('logFile = {}'.format('AllTempLogs.csv\n'))
       f.write('maxLogRecords = {}\n'.format(1000))
       f.write('recordCharge = N\n')
       f.write('emailTo = {}\n'.format('bbrindle@uniondrawn.com; intern@uniondrawn.com'))
       f.write('enableEmail = {}\n'.format(True))
       f.write('port = {}'.format('COM4'))
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
    return False
    
    
# ~~~~~Get saved charges~~~~~
def get_charges(path):
    #Make sure folder exists
    if not does_this_exist(path):
        os.mkdir(path) #create folder if not present
    
    #Collect all files in folder
    files = [f.strip('.csv') for f in os.listdir(path) if os.path.exists(path + f)] #collect all files in the folder
    return files
    

# ~~~~~Compare charges~~~~~
def check_charge(charge,path):
    files = get_charges(path)
    
    for c in files:
        if str(charge) == c[:5]:
            return False
    return True


# ~~~~Send email~~~~~
def send_email(TC,temp,time):
    sendTo = get_settings('Email', get_path())
    
    try:
        outlook = win32com.client.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = sendTo
        mail.Subject = 'Temperature Alert'
        mail.Body = "Thermocouple {} has exceeded {}°F at {}".format(TC,temp,time)
        mail.Send()
        return True
    except:
        print("Unable to send")
        return False
    
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~Read thermocouples~~~~~
def read_tc(path, logFile, port, currTime):
    tList = [currTime,0,0,0,0,0,0]
    
    try:
        arduino = serial.Serial(port=port, baudrate=9600, timeout=3)
        sleep(4) #wait for connection to establish
        
    #unable to connect to port    
    except:
        tList = [currTime,-111,-111,-111,-111,-111,-111]
        
        with open(path+logFile,'a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(tList)
        return 'err1: Unable to open port ' + str(port)
    
    
    try:
        arduino.write(bytes("R", 'utf-8')) #inform the Arduino it should read code
        
    #unable to send data to port    
    except:
        tList = [currTime,'err2','err2','err2','err2','err2','err2']
        
        with open(path+logFile,'a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(tList)
        return 'err2: Unable to write to port ' + str(port)
    
    
    try:
        # for i in range(0,6):
        sleep(1) #wait half a second before reading
        readings = arduino.readline().decode('UTF-8')[1:]
        arduino.close()
        
        #Clean up readings
        readings = readings.split("/")
        for i in range(1,7):
            tList[i] = float(readings[i-1])
        
        with open(path+logFile,'a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(tList)
        
        return '' #NO ERROR, READING SUCCESS
    
    #unable to read data from the port
    except:
        arduino.close()
        tList = [currTime,'err3','err3','err3','err3','err3','err3']
        
        with open(path+logFile,'a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(tList)
        return 'err3: Unable to read from port ' + str(port)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    
    