import os
import csv
from time import sleep
import RPi.GPIO as GPIO
from github import Github

# ~~~~~Directory of this program~~~~~
def get_path():
    return '/diskstation1/share/1 - Mill/DATA/Brandon Stuff/CODE/Pi Logger/' #Path on RPi


# ~~~~~Removes the beginning of a string
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


# ~~~~~Get the system settings~~~~~
def get_settings(selection, path):
    currSettings = []
    with open(path + 'Program/Settings.txt', 'r') as f:
        currSettings = f.readlines()
    if selection == 'Interval':
        return remove_prefix(currSettings[0],'intervalReading = ').strip()
    elif selection == 'MaxTemp':
        return remove_prefix(currSettings[1],'tempWarning = ').strip()
    elif selection == 'MaxRecords':
        return remove_prefix(currSettings[2],'maxLogRecords = ').strip()
    elif selection == 'Record':
        return remove_prefix(currSettings[3],'recordCharge = ').strip()
    elif selection == 'Email':
        return remove_prefix(currSettings[4],'emailTo = ').strip()
    elif selection == 'EmailAlert':
        return remove_prefix(currSettings[5],'enableEmail = ').strip()
    elif selection == 'Github':
        return remove_prefix(currSettings[6],'github = ').strip()
    

# ~~~~~Check if a file exists~~~~~
def does_this_exist(path,fileName):
    return os.path.exists(path + fileName)

# ~~~~~Make folder~~~~~
def make_folder(folderPath):
    os.makedirs(folderPath)

# ~~~~~Make settings file if not present~~~~~
def verify_settings(path):
    if does_this_exist(path,'Program/Settings.txt'):
        return True
    
    #Create file that could not be found
    update_settings(path+'Program/', 10, 1300, 'AllTempLogs.csv', 1000, 'N', 'bbrindle@uniondrawn.com; intern@uniondrawn.com', True, 'UNKOWN')
    return False


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
#def send_email(TC,temp,time):
#    sendTo = get_settings('Email', get_path())
#    
#    try:
#        outlook = win32com.client.Dispatch('outlook.application')
#        mail = outlook.CreateItem(0)
#        mail.To = sendTo
#        mail.Subject = 'Temperature Alert'
#        mail.Body = "Thermocouple {} has exceeded {}°F at {}".format(TC,temp,time)
#        mail.Send()
#        return True
#    except:
#        return False
    
# ~~~~~Update settings~~~~~
def update_settings(path,intRead,tWarn,maxRecords,chargRec,emailTo,emailEnable,github):
    with open(path + 'Settings.txt', 'w') as f:
       f.write('intervalReading = {}\n'.format(intRead))
       f.write('tempWarning = {}\n'.format(tWarn))
       f.write('maxLogRecords = {}\n'.format(maxRecords))
       f.write('recordCharge = {}\n'.format(chargRec))
       f.write('emailTo = {}\n'.format(emailTo))
       f.write('enableEmail = {}\n'.format(emailEnable))
       f.write('github = {}'.format(github))
    

# ~~~~~Check log file length~~~~~
def check_logs(path,maxLogs,currDate):
    csvFile = open(path + 'Program/AllTempLogs.csv')
    rowCount = sum(1 for row in csvFile)
    csvFile.close()
    
    #If the file has more lines than the maximum, remake the file
    newFile = "Charges//" + "99999 -- Logs-- " + currDate + ".csv"
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
        csvFile = csvFile[-80:]
        
        with open(path+'Program/AllTempLogs.csv','w',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in csvFile:
                writer.writerow(row)
        
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~Read the TC and record to the network~~~~~
def readTC(path,charge,currTime):
    GPIO.setmode(GPIO.BOARD)

    #Initialize pin numbers for TC inputs
    TC1 = 16
    TC2 = 18
    TC3 = 22
    TC4 = 32
    TC5 = 11
    TC6 = 36
    tcList = [TC1,TC2,TC3,TC4,TC5,TC6] #array of inputs

    #Initialize pin for amplifer controls
    CS = 29
    SCK = 31

    GPIO.setup(tcList, GPIO.IN) #Setup inputs
    GPIO.setup([CS,SCK], GPIO.OUT) #Setup outputs
    GPIO.output(CS,GPIO.HIGH) #start chip select as high

    #Array for outputs
    tcRead  =['','0','0','0','0','0','0']


    for i in range(0,len(tcList)):
        read = 0
        GPIO.output(SCK,GPIO.HIGH)
        sleep(0.1)
        GPIO.output(CS,GPIO.LOW)
        sleep(0.1) 

        for j in range(15,-1,-1):
            GPIO.output(SCK,GPIO.LOW)
            sleep(0.02)
            read |= (GPIO.input(tcList[i]) << j)
            GPIO.output(SCK,GPIO.HIGH)
            sleep(0.02)

        GPIO.output(CS,GPIO.HIGH)
        sleep(0.1)
		#Convert to Fahrenheit
        read >>= 5
        read *= 9/5
        read += 32
        if read >= 1870.00:
            read = 00.00
        tcRead[i+1] = f'{read:.2f}'

    tcRead[0] = currTime #Sets time for array
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
            if not does_this_exist(path+'Charges/',charge):
                header = ['Time','Temp1','Temp2','Temp3','Temp4','Temp5','Temp6']
                with open(path+'Charges/'+charge,'a',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    writer.writerow(tcRead)

            else:
                with open(path+'Charges/'+charge,'a',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(tcRead)

    except Exception as err:
        GPIO.cleanup()
        return err
    print(f'{float(tcRead[4]):.2f}')
    print(f'{float(tcRead[6]):.2f}')

    #If the charge has finished
    if charge == 'Y':
        GPIO.cleanup()
        if (float(tcRead[4]) + float(tcRead[6]))/2 < 100.00:
            return True
        return False

    #Clear the GPIO so they are not in use
    GPIO.cleanup()
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
        return 'ERROR: ' + str(err)
    
    #######################################################################
    #Try to connect to Github
    
    try: 
        token = get_settings('Github', path)
        g = Github(token) #token key
        
        repo = g.get_user().get_repo("View") #Repository
        all_files = []
        contents = repo.get_contents("")
        print(repo)
    except Exception as err:
        error_log(path,err,currTime)
        return "ERROR: " + str(err)

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
        error_log(path,err,currTime)
        return 'ERROR: ' + str(err)
    



# ~~~~~Error Log~~~~~
def error_log(path,err,currTime):
    print(err)
#    with open(path+'Program/Error-Logs.txt','a') as f:
 #       f.write(str(currTime) + ' ----- ' + err)
