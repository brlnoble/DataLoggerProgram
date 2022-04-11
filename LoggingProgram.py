import GeneralCommands as GC
from time import time, sleep
import datetime
import csv

path = GC.get_settings('Path', 'Pi') #path of the main program

# ~~~~~Settings~~~~~
def read_settings():
    #interval in minutes between reading the data
    global readInterval #make sure we change the global variables
    global tempWarn
    global logFile
    global maxRecords
    global chargeRecord
    global emailSend
    global emailAlert
    readInterval = int(GC.get_settings('Interval', path)) #convert minutes to seconds, add 5 as a precautionary measure
    tempWarn = int(GC.get_settings('MaxTemp', path))
    logFile = GC.get_settings('LogFile', path)
    maxRecords = int(GC.get_settings('MaxRecords', path))
    chargeRecord = GC.get_settings('Record', path)
    emailSend = GC.get_settings('Email', path)
    emailAlert = GC.get_settings('EmailAlert', path)
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

read_settings() #get the current settings


readInterval = 2

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

currTime = datetime.datetime.fromtimestamp(time()) #current time
lastRead = currTime

while True:
    currTime = datetime.datetime.fromtimestamp(time()) #current time
    
    if currTime - datetime.timedelta(seconds=(readInterval*1)) > lastRead:
        print('Recording Data')
        # tList = [currTime.strftime("%d-%b-%y %I:%M:%S %p"),0,0,0,0,0,0]
        # with open(path+logFile,'a',newline='') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(tList)
            
        if chargeRecord != 'N':
            print('Recording charge')
            
            if not GC.does_this_exist(path+'Charges\\'+chargeRecord+'.csv'):
                tList = [currTime.strftime("%d-%b-%y %I:%M:%S %p"),0,0,0,0,0,0]
                header = ['Time','Temp1','Temp2','Temp3','Temp4','Temp5','Temp6']
                with open(path+'Charges\\'+chargeRecord+'.csv','w',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    writer.writerow(tList)
            else:
                tList = [currTime.strftime("%d-%b-%y %I:%M:%S %p"),0,0,0,0,0,0]
                with open(path+'Charges\\'+chargeRecord+'.csv','a',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(tList)
                
        
        lastRead = currTime #record last reading