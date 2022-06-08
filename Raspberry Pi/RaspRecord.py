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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    if chargeRecord not in ['N','Y']:
        #time to end the charge at, 1 hour extra safety
        chargeEnd = currTime + datetime.timedelta(seconds=((int(chargeRecord[:2])+1)*60*60)) 
        chargeRecord = chargeRecord[3:] + ".csv"
        print ('Charge: '+str(chargeRecord))
        print ('END: '+str(chargeEnd))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~Error handling~~~~~
def errors(err):
    #Sort through the errors and see what the problem is
    errMsg = GC.error_log(path,err,currTime)

    #AllTempLogs is open
    if errMsg[:6] == "ERR 01":
        lastRead = currTime + datetime.timedelta(seconds=10) #try again in 10s

    #OnlineLog is open
    elif errMsg[:6] == "ERR 02":
        lastRead = currTime

    #Charge file is open
    elif errMsg[:6] == "ERR 03":
        lastRead = currTime

    #Incorrect Github token
    elif errMsg[:6] == "ERR 04":
        lastRead = currTime

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Get current settings
read_settings()

#See if logs need to be archived
GC.check_logs(path, maxRecords, currTime.strftime("%d-%b-%y"))

#Setup variables for the program
lastRead = currTime - datetime.timedelta(seconds=(readInterval*60)) #Last time data was read
lastEdit = os.path.getmtime(path + "Program/Settings.txt") #Last time settings were modified
lastCheck = currTime

#Turn on recording light
GC.record_light(True)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~MAIN LOOP~~~~~~~~~~~~~~~~~~~~

while True:
    currTime = datetime.datetime.fromtimestamp(time())

    #Check if we should read the settings (have they been modified)
    #Check every 10s
    if currTime - datetime.timedelta(seconds=10) > lastCheck:
        if os.path.getmtime(path + "Program/Settings.txt") > lastEdit:
            print('SETTINGS CHANGED')
            read_settings()
            lastCheck = currTime
            lastEdit = os.path.getmtime(path+'Program/Settings.txt')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Check if we should read the TC
    if currTime - datetime.timedelta(seconds=(readInterval*60)) > lastRead:
        print ("~~~~~~~~~~")
        #Record data
        currRead = GC.readTC(path,chargeRecord,currTime.strftime("%d-%b-%y - %I:%M:%S %p"))

        #If an error occured, add it to the log
        if currRead not in [True,False,'Read successful']:
            errors(currRead)
        else:
            git = GC.upload_Data(path, currTime)
            lastRead = currTime
            print('Read - ' + currTime.strftime("%I:%M:%S %p"))

        #If error with Github
        if git != "Uploaded to Github":
            errors(git)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #If the charge has finished, stop recording to the charge log
        if chargeRecord not in ['N','Y'] and currTime > chargeEnd:
            #Update the settings now that the recording has finished
            chargeRecord = 'Y' #Will keep recording to all log file
            GC.update_settings(path,readInterval,tempWarn,maxRecords,chargeRecord,emailSend,emailAlert,github)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #If charge is done, see if we can close the program
        elif chargeRecord == 'Y':
            #If temperature is below 100F, stop recording to the all log file
            if currRead:
                chargeRecord = 'N'
                GC.update_settings(path,readInterval,tempWarn,maxRecords,chargeRecord,emailSend,emailAlert,github)

                #Turn off recording light
                GC.record_light=False

                #Close program
                break
