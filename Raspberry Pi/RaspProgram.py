from time import time
import datetime
import GeneralCommands as GC #Custom file

#Current directory path
path = GC.get_path()

#Make settings if it does not exist
GC.verify_settings(path)

#Make log file if it does not exist
GC.verify_logs(path)


# ~~~~~READ IN SETTING FILE~~~~~
def read_settings():
    #interval in minutes between reading the data
    global readInterval #make sure we change the global variables
    global tempWarn
    global logFile
    global maxRecords
    global chargeRecord
    global emailSend
    global emailAlert
    global github
    global chargeEnd
    readInterval = int(GC.get_settings('Interval', path)) #convert minutes to seconds, add 5 as a precautionary measure
    tempWarn = int(GC.get_settings('MaxTemp', path))
    logFile = 'AllTempLogs.csv'
    maxRecords = int(GC.get_settings('MaxRecords', path))
    chargeRecord = GC.get_settings('Record', path)
    emailSend = GC.get_settings('Email', path)
    emailAlert = GC.get_settings('EmailAlert', path)
    github = str(GC.get_settings('Github', path))
    
    if chargeRecord != 'N':
        chargeEnd = currTime + datetime.timedelta(seconds=((int(chargeRecord[:2])+2)*60*60)) #time to end the charge at, 2 hour extra safety 


currTime = datetime.datetime.fromtimestamp(time()) #used for clock
lastRead = currTime - datetime.timedelta(seconds=(readInterval*60)) #last time data was read
lastCheck = path.getmtime(path + "Settings.txt")
chargeEnd = currTime #time to stop recording charge


#See if logs need to be dumped
GC.check_logs(path, logFile, maxRecords, currTime.strftime("%d-%B-%Y"))

read_settings() #Get current settings



while True:
    currTime = datetime.datetime.fromtimestamp(time()) #current time
    
    #If the recording has finished, close the program
    if currTime > chargeEnd:
        break
    
    #Check if we should read the settings (have they been modified)    
    if currTime - datetime.timedelta(seconds=10) > lastCheck:
        if path.getmtime(path + "Settings.txt") > lastCheck:
            read_settings()
    
    #Check if we should read the TC
    if currTime - datetime.timedelta(seconds=(readInterval*60)) > lastRead:
        GC.read_tc(path, logFile, currTime.strftime("%d %B, %Y - %I:%M:%S %p"),chargeRecord[3:]) #Record data
        GC.upload_Data(path, currTime)
        
        #Check if a charge should stop recording
        if chargeRecord != 'N': 
            if currTime > chargeEnd:
                chargeRecord = 'N'
                chargeEnd = currTime
                
                #Update the settings now that the charge has stopped recording
                GC.update_settings(path, readInterval, tempWarn, logFile, maxRecords, chargeRecord, emailSend, emailAlert, github)