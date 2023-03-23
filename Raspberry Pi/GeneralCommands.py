import os
import csv
from time import sleep
import RPi.GPIO as GPIO
from github import Github
import json

# ~~~~~Directory of this program~~~~~
def Get_Path():
    return '/mnt/diskstation1/1 - Mill/Data Logger/' #Path on RPi


# ~~~~~Make settings file if not present~~~~~
def Verify_Settings(path):
    if Does_This_Exist(path,'Program/Settings.json'):
        return True
    
    #Create file that could not be found
    settings = {
        "interval": 10,
        "temp_warn": 1300,
        "max_records": 1000,
        "charge_record": "N",
        "email_to": [
            "intern@uniondrawn.com"
        ],
        "enable_email": True,
        "github": "UNKNOWN"
    }
    Update_Settings(path, "all", settings)
    return False


# ~~~~~Update settings~~~~~
def Update_Settings(path,selection,value):
    if selection == "all":
        with open(path+"Program/Settings.json","w") as f:
            json.dump(value,f,indent=4)
        return
    
    current_settings = Get_Settings("all", path)
    current_settings[selection] = value
    
    with open(path+"Program/Settings.json","w") as f:
        json.dump(current_settings,f,indent=4)  
        
        
# ~~~~~Get the system settings~~~~~
def Get_Settings(selection, path):
    with open(path+"Program/Settings.json","r") as f:
        current_settings = json.load(f)
    
    if selection == "all":
        return current_settings
    return current_settings[selection]


# ~~~~~Check if a file exists~~~~~
def Does_This_Exist(path,fileName):
    return os.path.exists(path + fileName)


# ~~~~~Make folder~~~~~
def Make_Folder(folderPath):
    os.makedirs(folderPath)


# ~~~~~Make Log file if not present~~~~~
def Verify_Logs(path):
    if Does_This_Exist(path,'Program/AllTempLogs.csv'):
        return True
    
    with open(path + 'Program/AllTempLogs.csv', 'w', newline='') as f:
        
        writer = csv.writer(f)
        writer.writerow(['Time','Temp1','Temp2','Temp3','Temp4','Temp5','Temp6'])
        writer.writerow(['01/01/2022 00:01',1,1,1,1,1,1])
        writer.writerow(['01/01/2022 00:02',2,2,2,2,2,2])
        writer.writerow(['01/01/2022 00:03',3,3,3,3,3,3])
    return False
    

# ~~~~~Send email~~~~~
def Send_Email(TC,temp,time,warn):
    try:
        import smtplib, ssl
        with open(Get_Path() + 'Program/Email.json','r') as f:
            email_info = json.load(f)
            
        sender = email_info['username']
        receivers = Get_Settings('email_to',Get_Path())
        context = ssl.create_default_context()

        message = "From: Data Logger <{}>".format(email_info['username'])
        message += "\nSubject: Temperature Alert"
        message += "\n\nThermocouple: \t{}\nTemperature: \t{} F\nTime: \t\t{}"
        message += "\n\nThe furnace is set to alert when it exceeds {} F. You can change this in the data logger settings."
        message += "\n\n\n~~~This is a generated message from the data logger. Please do not reply.~~~"

        with smtplib.SMTP_SSL(email_info['server'],email_info['port'],context=context) as server:
            server.login(email_info['username'],email_info['password'])
            server.sendmail(sender, receivers, message.format(TC,temp,time,warn))
        return True
    except:
        return False
      

# ~~~~~Check log file length~~~~~
def Check_Logs(path,max_logs,current_date):
    csv_file = open(path + 'Program/AllTempLogs.csv')
    row_count = sum(1 for row in csv_file)
    csv_file.close()
    
    #If the file has more lines than the maximum, remake the file
    new_file = "Charges//" + "00000 -- Logs -- " + current_date + ".csv"
    if row_count > max_logs:
        os.rename(path+'Program/AllTempLogs.csv', path + new_file)        
        
        #Make the new file
        csv_file = []
        header = []
        with open(path+new_file, 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                csv_file.append(row)
    
        header = csv_file[0]
        csv_file = csv_file[-80:] #keep last 80 lines of the file
        
        with open(path+'Program/AllTempLogs.csv','w',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in csv_file:
                writer.writerow(row)
        
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~Read the TC and record to the network~~~~~
def Read_TC(path,charge,current_time,temp_warning,calibration_numbers):
    GPIO.setmode(GPIO.BOARD)
    
    #Initialize pin numbers for TC inputs
    TC1 = 16
    TC2 = 18
    TC3 = 22
    TC4 = 32
    TC5 = 37
    TC6 = 36
    tc_list = [TC1,TC2,TC3,TC4,TC5,TC6] #array of inputs
    
    #Initialize pin for amplifer controls
    CS = 29
    SCK = 31
    
    GPIO.setup(tc_list, GPIO.IN) #Setup inputs
    GPIO.setup([CS,SCK], GPIO.OUT) #Setup outputs
    GPIO.output(CS,GPIO.LOW) #start chip select as low (read mode)
    
    #Array for outputs
    tc_reading = ['',0,0,0,0,0,0] #String result
    tc_numbers = [00,0,0,0,0,0,0] #Float result
    
    #~~~Read the TC's~~~
    for j in range(15,-1,-1): #Read each of the 16 bits one at a 
        GPIO.output(SCK,GPIO.HIGH) #Output bit
        sleep(0.02)
        
        #Read the corresponding bit for each thermocouple
        for i in range(0,len(tc_list)):
            tc_numbers[i+1] |= (GPIO.input(tc_list[i]) << j)
        
        GPIO.output(SCK,GPIO.LOW) #Reset clock
        sleep(0.1)
    
    GPIO.output(CS,GPIO.HIGH) #Stop reading values
        
    	#Convert to Fahrenheit
    for i in range(1,len(tc_numbers)):
        tc_numbers[i] >>= 5
        tc_numbers[i] *= 9/5
        tc_numbers[i] += 32
        tc_numbers[i] += float(calibration_numbers["TC" + str(i)]) #Add the calibration offset
        if tc_numbers[i] >= 1870.00: #Cannot sense over this temperature - means furnace is off
            tc_numbers[i] = 00.00
        tc_reading[i] = f'{tc_numbers[i]:.2f}' #Format value as 00.00
    
    tc_reading[0] = current_time #Sets time for array
    
    #Try to write to the log, otherwise return error
    try:
        #Write to CSV log
        with open(path+'Program/AllTempLogs.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(tc_reading)

    except Exception as err:
        return err

    #Check if there is a charge file
    try:
        if charge not in ['N','Y']:
            header = []
            charge = charge[3:] + '.csv' #Remove duration and add 
            #If charge file does not exist, create it and add header + data
            if not Does_This_Exist(path+'Charges/',charge):
                header = ['Time','Temp1','Temp2','Temp3','Temp4','Temp5','Temp6']
                with open(path+'Charges/'+charge,'a',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    writer.writerow(tc_reading)

            #If charge file does exist, append data
            else:
                with open(path+'Charges/'+charge,'a',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(tc_reading)

    except Exception as err:
        return err

    #If the charge has finished
    if charge == 'Y':
        #If the furnace has cooled down, inform program to close and shutdown RPi
        if (float(tc_reading[4]) + float(tc_reading[6]))/2 < 100.00:
            return True
        return False

    #See if any of the thermocouples are over the temperature limit
    #Compare it to the average, if one TC is 300 over average it is likely an error
    avg = sum(tc_numbers) / (len(tc_numbers)-1) #Average temperature
    for i in range(1,len(tc_reading)):
        if tc_numbers[i] > float(temp_warning) and tc_numbers[i] > (300 + avg):
            return "Overtemp {} {}".format(i,tc_reading[i])
    return 'Read successful' 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    
def Upload_Data(path, current_time):
    
    #######################################################################
    #Try to write last 50 data points to online log
    
    try:
        csv_file = []
        header = []
        with open(path+'Program/AllTempLogs.csv', 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                csv_file.append(row)

        header = csv_file[0]
        csv_file = csv_file[-50:]
        
        with open(path+'Program/OnlineLog.csv','w',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in csv_file:
                writer.writerow(row)
    except Exception as err:
        return str(err)
    
    #######################################################################
    #Try to connect to Github
    
    try: 
        token = Get_Settings('github', path)
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
            repo.update_file(contents.path, "Updating temperature log" + str(current_time), content, contents.sha, branch="main")
            print(git_file + ' UPDATED')
        else:
            repo.create_file(git_file, "Updating temperature log" + str(current_time), content, branch="master")
            print(git_file + ' CREATED')
            
        return 'Uploaded to Github'
        
    except Exception as err:
        return str(err)
    



# ~~~~~Error Log~~~~~
def Error_Log(path,err,current_time):
    #Cannot access opened file
    if str(err)[:10] == "[Errno 16]":

        #Check if AllTempLogs
        if str(err)[-16:-1] == "AllTempLogs.csv":
            err = 'ERR 01: AllTempLogs is open'

        #Check if OnlineLog
        elif str(err)[-14:-1] == "OnlineLog.csv":
            err = 'ERR 02: OnlineLog is open'

        #Check if it is the charge file
        elif str(err)[-27:-1] == Get_Settings("charge_record")[3:]:
            err = 'ERR 03: Charge log file is open'

    #If incorrect Github token
    elif str(err)[:3] == "401":
        err = 'ERR 04: Invalid Github token'
        
    #If no internet connection
    elif str(err)[:19] == "HTTPSConnectionPool":
        err = 'ERR 10: No network access on the Raspberry Pi'
        
    #Unknown error
    else:
        err = "ERR00: " + str(err)

    print (str(err)+': '+current_time.strftime("%I:%M:%S %p"))

    #~~~Write to the error log file~~~
    with open(path+'Program/Error-Logs.txt','a') as f:
        f.write(current_time.strftime("%d-%b-%y - %I:%M:%S %p") + ': ' + str(err)+'\n')

    return err


# ~~~~~Recording Light~~~~~
def Record_Light(state):
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
        
# ~~~~~Calibration Numbers~~~~~
def Get_Calibration(path):
    with open(path+"Program/Calibration.json","r") as f:
        calibration_numbers = json.load(f)
    return calibration_numbers
