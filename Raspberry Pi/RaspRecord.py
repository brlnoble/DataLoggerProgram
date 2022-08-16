from time import time
import datetime
import GeneralCommands as GC #Custom file
import os

#Current directory path
path = GC.Get_Path()

#Make settings if it does not exist
GC.Verify_Settings(path)

#Make log file if it does not exist
GC.Verify_Logs(path)

current_time = datetime.datetime.fromtimestamp(time()) #Used for clock

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~READ IN SETTING FILE~~~~~
def Read_Settings():
    global settings
    global charge_end
    settings = GC.Get_Settings("all", path)

    #Check if the program should be recording
    if settings['charge_record'] not in ['N','Y']:
        #time to end the charge at, 1 hour extra safety
        if settings['charge_record'] != 'N':
            charge_end = current_time + datetime.timedelta(hours=((int(settings['charge_record'][:2])+1))) 

    elif settings['charge_record'] == 'N': #If recording cancelled
        charge_end = 'N'

    print ('Charge: '+str(settings['charge_record']))
    print ('End: '+str(charge_end))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~Error handling~~~~~
def Errors(err):
    #Check if high temp alert
    if str(err)[:8] == "Overtemp":
        err = str(err)
        print (err)
        global email_try
        if email_try:
            GC.Send_Email(err[9:10],err[11:],current_time.strftime("%d-%b-%y - %I:%M:%S %p"),settings['temp_warn'])
            email_try = False
    else:
        #Sort through the errors and see what the problem is
        error_msg = GC.Error_Log(path,err,current_time)
        global last_tc_read

        #AllTempLogs is open
        if error_msg[:6] == "ERR 01":
            last_tc_read = current_time + datetime.timedelta(seconds=10) #try again in 10s

        #OnlineLog is open
        elif error_msg[:6] == "ERR 02":
            last_tc_read = current_time

        #Charge file is open
        elif error_msg[:6] == "ERR 03":
            last_tc_read = current_time

        #Incorrect Github token
        elif error_msg[:6] == "ERR 04":
            last_tc_read = current_time

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Get current settings
charge_end = 'N'
Read_Settings()
email_try = bool(settings['enable_email'])

#Get the calibration numbers
calibration_numbers = GC.Get_Calibration(path)

#See if logs need to be archived
GC.Check_Logs(path, settings['max_records'], current_time.strftime("%d-%b-%y"))

#Setup variables for the program
last_tc_read = current_time - datetime.timedelta(minutes=int(settings['interval'])) #Last time data was read

last_settings_edit = os.path.getmtime(path + "Program/Settings.json") #Last time settings were modified
last_settings_check = current_time

last_calibration_edit = os.path.getmtime(path+"Program/Calibration.json") #Last time the calibration numbers were modified
last_calibration_check = current_time

#Turn on recording light
GC.Record_Light(True)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~MAIN LOOP~~~~~~~~~~~~~~~~~~~~

while True:
    current_time = datetime.datetime.fromtimestamp(time())

    #Check if we should read the settings (have they been modified)
    #Check every 10s
    if current_time - datetime.timedelta(seconds=10) > last_settings_check:
        if os.path.getmtime(path + "Program/Settings.json") > last_settings_edit:
            print('SETTINGS CHANGED')
            Read_Settings()
            last_settings_check = current_time
            last_settings_edit = os.path.getmtime(path+'Program/Settings.json')
            
    #Check if we should read the calibration numbers (have they been modified)
    #Check every 10s
    if current_time - datetime.timedelta(seconds=10) > last_calibration_check:
        if os.path.getmtime(path + "Program/Calibration.json") > last_calibration_edit:
            print('CALIBRATIONS CHANGED')
            calibration_numbers = GC.Get_Calibration(path)
            last_calibration_check = current_time
            last_calibration_edit = os.path.getmtime(path+'Program/Settings.json')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Check if we should read the TC
    if current_time - datetime.timedelta(minutes=int(settings['interval'])) > last_tc_read:
        print ("~~~~~~~~~~")
        #Record data
        current_tc_read = GC.Read_TC(path,settings['charge_record'],current_time.strftime("%d-%b-%y - %I:%M:%S %p"),settings['temp_warn'],calibration_numbers)

        #If an error occured, add it to the log
        if current_tc_read not in [True,False,'Read successful'] and str(current_tc_read)[:8] != "Overtemp":
            Errors(current_tc_read)

        else:
            #If there is a thermocouple over the temperature limit
            if str(current_tc_read)[:8] == "Overtemp":
                Errors(current_tc_read)

            git = GC.Upload_Data(path, current_time)
            last_tc_read = current_time
            print('Read - ' + current_time.strftime("%I:%M:%S %p"))

            #If error with Github
            if git != "Uploaded to Github":
                Errors(git)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #If the charge has finished, stop recording to the charge log
        if settings['charge_record'] not in ['N','Y'] and current_time > charge_end:
            #Update the settings now that the recording has finished
            settings['charge_record'] = 'Y' #Will keep recording to all log file
            GC.Update_Settings(path, 'charge_record', 'Y')
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #If charge is done, see if we can close the program
        elif settings['charge_record'] == 'Y':
            #If temperature is below 100F, stop recording to the all log file
            if current_tc_read:
                settings['charge_record'] = 'N'
                GC.Update_Settings(path,'charge_record','N')

                #Turn off recording light
                GC.Record_Light=False

                #Close program
                break
