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
    global settings
    global chargeEnd
    settings = GC.get_settings("all", path)

    #Check if the program should be recording
    if settings['chargeRecord'] not in ['N','Y']:
        #time to end the charge at, 1 hour extra safety
        if settings['chargeRecord'] != 'N':
            chargeEnd = currTime + datetime.timedelta(hours=((int(settings['chargeRecord'][:2])+1))) 

    elif settings['chargeRecord'] == 'N': #If recording cancelled
        chargeEnd = 'N'

    print ('Charge: '+str(settings['chargeRecord']))
    print ('END: '+str(chargeEnd))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~Error handling~~~~~
def errors(err):
    #Check if high temp alert
    if str(err)[:8] == "Overtemp":
        err = str(err)
        print (err)
        global emailTry
        if emailTry:
            GC.send_email(err[9:10],err[11:],currTime.strftime("%d-%b-%y - %I:%M:%S %p"),settings['tempWarn'])
            emailTry = False
    else:
        #Sort through the errors and see what the problem is
        errMsg = GC.error_log(path,err,currTime)
        global lastRead

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
emailTry = bool(settings['enableEmail'])

#See if logs need to be archived
GC.check_logs(path, settings['maxRecords'], currTime.strftime("%d-%b-%y"))

#Setup variables for the program
lastRead = currTime - datetime.timedelta(minutes=int(settings['interval'])) #Last time data was read
lastEdit = os.path.getmtime(path + "Program/Settings.json") #Last time settings were modified
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
        if os.path.getmtime(path + "Program/Settings.json") > lastEdit:
            print('SETTINGS CHANGED')
            read_settings()
            lastCheck = currTime
            lastEdit = os.path.getmtime(path+'Program/Settings.json')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Check if we should read the TC
    if currTime - datetime.timedelta(minutes=int(settings['interval'])) > lastRead:
        print ("~~~~~~~~~~")
        #Record data
        currRead = GC.readTC(path,settings['chargeRecord'],currTime.strftime("%d-%b-%y - %I:%M:%S %p"),settings['tempWarn'])

        #If an error occured, add it to the log
        if currRead not in [True,False,'Read successful'] and str(currRead)[:8] != "Overtemp":
            errors(currRead)

        else:
            #If there is a thermocouple over the temperature limit
            if str(currRead)[:8] == "Overtemp":
                errors(currRead)

            git = GC.upload_Data(path, currTime)
            lastRead = currTime
            print('Read - ' + currTime.strftime("%I:%M:%S %p"))

            #If error with Github
            if git != "Uploaded to Github":
                errors(git)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #If the charge has finished, stop recording to the charge log
        if settings['chargeRecord'] not in ['N','Y'] and currTime > chargeEnd:
            #Update the settings now that the recording has finished
            settings['chargeRecord'] = 'Y' #Will keep recording to all log file
            GC.update_settings(path, 'chargeRecord', 'Y')
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #If charge is done, see if we can close the program
        elif settings['chargeRecord'] == 'Y':
            #If temperature is below 100F, stop recording to the all log file
            if currRead:
                settings['chargeRecord'] = 'N'
                GC.update_settings(path,'chargeRecord','N')

                #Turn off recording light
                GC.record_light=False

                #Close program
                break
