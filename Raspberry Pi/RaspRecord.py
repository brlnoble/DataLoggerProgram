from time import time
import datetime
import GeneralCommands as GC #Custom file
import os

#Current directory path
path = GC.get_path()

#Make settings if it does not exist
GC.verify_settings(path)

#Make log file if it does not exist
GC.verify_logs(path)

currTime = datetime.datetime.fromtimestamp(time()) #Used for clock
chargeEnd = 'N' #Declaring for future use

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
    maxRecords = int(GC.get_settings('MaxRecords', path))
    chargeRecord = GC.get_settings('Record', path)
    emailSend = GC.get_settings('Email', path)
    emailAlert = GC.get_settings('EmailAlert', path)
    github = str(GC.get_settings('Github', path))

    #Check if the program should be recording
    if chargeRecord != 'N':
        #time to end the charge at, 1 hour extra safety
        chargeEnd = currTime + datetime.timedelta(seconds=((int(chargeRecord[:2])+1)*60*60)) 


#Get current settings
read_settings()

#See if logs need to be archived
GC.check_logs(path, maxRecords, currTime.strftime("%d-%B-%Y"))

#Setup variables for the program
lastRead = currTime - datetime.timedelta(seconds=(readInterval*60)) #Last time data was read
lastCheck = os.path.getmtime(path + "Program/Settings.txt") #Last time settings were modified

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~MAIN LOOP~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

while True:
    currTime = datetime.datetime.fromtimestamp(time())

    #Check if we should read the settings (have they been modified)
    #Check every 10s
    if currTime - datetime.timedelta(seconds=10) > datetime.datetime.fromtimestamp(lastCheck):
        if os.path.getmtime(path + "Program/Settings.txt") > lastCheck:
            read_settings()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Check if we should read the TC
    if currTime - datetime.timedelta(seconds=(readInterval*60)) > lastRead:
        #Record data
        currRead = GC.readTC(path,chargeRecord,currTime.strftime("%d %B, %Y - %I:%M:%S %p"))

        #If an error occured, add it to the log
        if currRead not in [True,False,'Read successful']:
            GC.error_log(path,currRead,currTime)

        #!!!!!GC.upload_Data(path, currTime)
        lastRead = currTime
        print('Read - ' + currTime.strftime("%I:%M:%S %p"))

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #If the charge has finished, stop recording to the charge log
        if chargeEnd not in ['N','Y'] and currTime > chargeEnd:
            #Update the settings now that the recording has finished
            chargeRecord = 'Y' #Will keep recording to all log file
            GC.update_settings(path,readInterval,tempWarn,maxRecords,chargeRecord,emailSend,emailAlert,github)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #If charge is done, see if we can close the program
        elif chargeEnd == 'Y':
            #If temperature is below 100F, stop recording to the all log file
            if currRead:
                chargeRecord = 'N'
                GC.update_settings(path,readInterval,tempWarn,maxRecords,chargeRecord,emailSend,emailAlert,github)

                #Close program
                break
