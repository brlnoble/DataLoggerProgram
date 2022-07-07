import os
import csv
from time import sleep
import RPi.GPIO as GPIO
from github import Github
import json

# ~~~~~Directory of this program~~~~~
def get_path():
    return '/diskstation1/share/1 - Mill/Data Logger/' #Path on RPi


# ~~~~~Make settings file if not present~~~~~
def verify_settings(path):
    if does_this_exist(path,'Program/Settings.json'):
        return True
    
    #Create file that could not be found
    settings = {
        "interval": 10,
        "tempWarn": 1300,
        "maxRecords": 1000,
        "chargeRecord": "N",
        "emailTo": [
            "intern@uniondrawn.com"
        ],
        "enableEmail": True,
        "github": "UNKNOWN"
    }
    update_settings(path, "all", settings)
    return False


# ~~~~~Update settings~~~~~
def update_settings(path,selection,value):
    if selection == "all":
        with open(path+"Program/Settings.json","w") as f:
            json.dump(value,f,indent=4)
        return
    
    currSet = get_settings("all", path)
    currSet[selection] = value
    
    with open(path+"Program/Settings.json","w") as f:
        json.dump(currSet,f,indent=4)  
        
        
# ~~~~~Get the system settings~~~~~
def get_settings(selection, path):
    with open(path+"Program/Settings.json","r") as f:
        currSet = json.load(f)
    
    if selection == "all":
        return currSet
    return currSet[selection]


# ~~~~~Check if a file exists~~~~~
def does_this_exist(path,fileName):
    return os.path.exists(path + fileName)


# ~~~~~Make folder~~~~~
def make_folder(folderPath):
    os.makedirs(folderPath)


# ~~~~~Make Log file if not present~~~~~
def verify_logs(path):
    if does_this_exist(path,'Program/AllTempLogs.csv'):
        return True
    
    with open(path + 'Program/AllTempLogs.csv', 'w', newline='') as f:
        
        writer = csv.writer(f)
        writer.writerow(['Time','Temp1','Temp2','Temp3','Temp4','Temp5','Temp6'])
        writer.writerow(['01/01/2022 00:01',1,1,1,1,1,1])
        writer.writerow(['01/01/2022 00:02',2,2,2,2,2,2])
        writer.writerow(['01/01/2022 00:03',3,3,3,3,3,3])
    return False
    

# ~~~~~Send email~~~~~
def send_email(TC,temp,time,warn):
    try:
        import smtplib, ssl
        with open(get_path() + 'Program/Email.json','r') as f:
            emailInfo = json.load(f)
            
        sender = emailInfo['username']
        receivers = get_settings('emailTo',get_path())
        context = ssl.create_default_context()

        message = "From: Data Logger <{}>".format(emailInfo['username'])
        message += "\nSubject: Temperature Alert"
        message += "\n\nThermocouple: \t{}\nTemperature: \t{} F\nTime: \t\t{}"
        message += "\n\nThe furnace is set to alert when it exceeds {} F. You can change this in the data logger settings."
        message += "\n\n\n~~~This is a generated message from the data logger. Please do not reply.~~~"

        with smtplib.SMTP_SSL(emailInfo['server'],emailInfo['port'],context=context) as server:
            server.login(emailInfo['username'],emailInfo['password'])
            server.sendmail(sender, receivers, message.format(TC,temp,time,warn))
        return True
    except:
        return False
      

# ~~~~~Check log file length~~~~~
def check_logs(path,maxLogs,currDate):
    csvFile = open(path + 'Program/AllTempLogs.csv')
    rowCount = sum(1 for row in csvFile)
    csvFile.close()
    
    #If the file has more lines than the maximum, remake the file
    newFile = "Charges//" + "00000 -- Logs -- " + currDate + ".csv"
    if rowCount > maxLogs:
        os.rename(path+'Program/AllTempLogs.csv', path + newFile)        
        
        #Make the new file
        csvFile = []
        header = []
        with open(path+newFile, 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                csvFile.append(row)
    
        header = csvFile[0]
        csvFile = csvFile[-80:] #keep last 80 lines of the file
        
        with open(path+'Program/AllTempLogs.csv','w',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in csvFile:
                writer.writerow(row)
        
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~Read the TC and record to the network~~~~~
def readTC(path,charge,currTime,tempWarn):
    GPIO.setmode(GPIO.BOARD)
    
    #Initialize pin numbers for TC inputs
    TC1 = 16
    TC2 = 18
    TC3 = 22
    TC4 = 32
    TC5 = 37
    TC6 = 36
    tcList = [TC1,TC2,TC3,TC4,TC5,TC6] #array of inputs
    
    #Initialize pin for amplifer controls
    CS = 29
    SCK = 31
    
    GPIO.setup(tcList, GPIO.IN) #Setup inputs
    GPIO.setup([CS,SCK], GPIO.OUT) #Setup outputs
    GPIO.output(CS,GPIO.LOW) #start chip select as low (read mode)
    
    #Array for outputs
    tcRead = ['',0,0,0,0,0,0] #String result
    tcNums = [00,0,0,0,0,0,0] #Float result
    
    #~~~Read the TC's~~~
    for j in range(15,-1,-1): #Read each of the 16 bits one at a 
        GPIO.output(SCK,GPIO.HIGH) #Output bit
        sleep(0.02)
        
        #Read the corresponding bit for each thermocouple
        for i in range(0,len(tcList)):
            tcRead[i+1] |= (GPIO.input(tcList[i]) << j)
        
        GPIO.output(SCK,GPIO.LOW) #Reset clock
        sleep(0.1)
    
    GPIO.output(CS,GPIO.HIGH) #Stop reading values
        
    	#Convert to Fahrenheit
    for i in range(1,len(tcNums)):
        tcNums[i] >>= 5
        tcNums[i] *= 9/5
        tcNums[i] += 32
        if tcNums[i] >= 1870.00: #Cannot sense over this temperature - means furnace is off
            tcNums[i] = 00.00
        tcRead[i] = f'{tcNums[i]:.2f}' #Format value as 00.00
    
    tcRead[0] = currTime #Sets time for array
    
    #Try to write to the log, otherwise return error
    try:
        #Write to CSV log
        with open(path+'Program/AllTempLogs.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(tcRead)

    except Exception as err:
        return err

    #Check if there is a charge file
    try:
        if charge not in ['N','Y']:
            header = []
            charge = charge[3:] + '.csv' #Remove duration and add 
            #If charge file does not exist, create it and add header + data
            if not does_this_exist(path+'Charges/',charge):
                header = ['Time','Temp1','Temp2','Temp3','Temp4','Temp5','Temp6']
                with open(path+'Charges/'+charge,'a',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    writer.writerow(tcRead)

            #If charge file does exist, append data
            else:
                with open(path+'Charges/'+charge,'a',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(tcRead)

    except Exception as err:
        return err

    #If the charge has finished
    if charge == 'Y':
        #If the furnace has cooled down, inform program to close and shutdown RPi
        if (float(tcRead[4]) + float(tcRead[6]))/2 < 100.00:
            return True
        return False

    #See if any of the thermocouples are over the temperature limit
    #Compare it to the average, if one TC is 300 over average it is likely an error
    avg = sum(tcNums) / len(tcNums) #Average temperature
    for i in range(1,len(tcRead)):
        if tcNums[i] > float(tempWarn) and (tcNums[i] < 300 + avg):
            return "Overtemp {} {}".format(i,tcRead[i])
    return 'Read successful' 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    
def upload_Data(path, currTime):
    
    #######################################################################
    #Try to write last 50 data points to online log
    
    try:
        csvFile = []
        header = []
        with open(path+'Program/AllTempLogs.csv', 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                csvFile.append(row)

        header = csvFile[0]
        csvFile = csvFile[-50:]
        
        with open(path+'Program/OnlineLog.csv','w',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in csvFile:
                writer.writerow(row)
    except Exception as err:
        return str(err)
    
    #######################################################################
    #Try to connect to Github
    
    try: 
        token = get_settings('github', path)
        g = Github(token) #token key
        
        repo = g.get_user().get_repo("View") #Repository
        all_files = []
        contents = repo.get_contents("")
    except Exception as err:
        return str(err)

    #######################################################################
    #Try to upload the file to Github
    
    try:
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file = file_content
                all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))
    
        with open(path + 'Program/OnlineLog.csv', 'r') as file: #file to open
            content = file.read()
    
        #Upload to Github
        git_file = 'OnlineLog.csv'
        if git_file in all_files:
            contents = repo.get_contents(git_file)
            repo.update_file(contents.path, "Updating temperature log" + str(currTime), content, contents.sha, branch="main")
            print(git_file + ' UPDATED')
        else:
            repo.create_file(git_file, "Updating temperature log" + str(currTime), content, branch="master")
            print(git_file + ' CREATED')
            
        return 'Uploaded to Github'
        
    except Exception as err:
        return str(err)
    



# ~~~~~Error Log~~~~~
def error_log(path,err,currTime):
    #Cannot access opened file
    if str(err)[:10] == "[Errno 16]":

        #Check if AllTempLogs
        if str(err)[-16:-1] == "AllTempLogs.csv":
            err = 'ERR 01: AllTempLogs is open'

        #Check if OnlineLog
        elif str(err)[-14:-1] == "OnlineLog.csv":
            err = 'ERR 02: OnlineLog is open'

        #Check if it is the charg file
        elif str(err)[-27:-1] == get_settings("Record")[3:]:
            err = 'ERR 03: Charge log file is open'

    #If incorrect Github token
    elif str(err)[:3] == "401":
        err = 'ERR 04: Invalid Github token'

    print (str(err)+': '+currTime.strftime("%I:%M:%S %p"))

    #~~~Write to the error log file~~~
    with open(path+'Program/Error-Logs.txt','a') as f:
        f.write(currTime.strftime("%d-%b-%y - %I:%M:%S %p") + ': ' + str(err)+'\n')

    return err


# ~~~~~Recording Light~~~~~
def record_light(state):
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11,GPIO.OUT) #LED
    GPIO.setup(3,GPIO.OUT) #FAN

    if state:
        GPIO.output(11,GPIO.HIGH)
        GPIO.output(3,GPIO.HIGH)
        print ('....RECORD START....')
    else:
        GPIO.output(11,GPIO.LOW)
        GPIO.output(3,GPIO.LOW)
        print ('....RECORD STOP....')
