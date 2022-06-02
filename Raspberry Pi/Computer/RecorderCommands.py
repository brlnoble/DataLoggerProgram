import os

# ~~~~~Directory of this program~~~~~
def get_path():
    return '//DISKSTATION1/mill/1 - Mill/DATA/Brandon Stuff/CODE/Pi Logger/' #Path on RPi


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

# ~~~~~Check file modification~~~~~
def get_mtime(path,fileName):
    return os.path.getmtime(path + fileName)

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
    
    
# ~~~~~Get saved charges~~~~~
def get_charges(path):
    #Make sure folder exists
    if not does_this_exist(path,'Charges/'):
        os.mkdir(path+'Charges/') #create folder if not present
    
    path += 'Charges/'
    #Collect all files in folder
    files = [f.strip('.csv') for f in os.listdir(path) if os.path.exists(path + f)] #collect all files in the folder
    return sorted(files,reverse=True) #Return list newest to oldest
    

# ~~~~~Compare charges~~~~~
def check_charge(path,charge):
    files = get_charges(path)
    
    for c in files:
        if str(charge) == c[:5]:
            return False
    return True

    
# ~~~~~Update settings~~~~~
def update_settings(path,intRead,tWarn,maxRecords,chargRec,emailTo,emailEnable,github):
    with open(path + 'Program/Settings.txt', 'w') as f:
       f.write('intervalReading = {}\n'.format(intRead))
       f.write('tempWarning = {}\n'.format(tWarn))
       f.write('maxLogRecords = {}\n'.format(maxRecords))
       f.write('recordCharge = {}\n'.format(chargRec))
       f.write('emailTo = {}\n'.format(emailTo))
       f.write('enableEmail = {}\n'.format(emailEnable))
       f.write('github = {}'.format(github)) 


# ~~~~~Error Log~~~~~
def error_Log(path,err,currTime):
    with open(path+'Program/Error-Logs.txt','a') as f:
        f.writeline(currTime + ' ----- ' + err)

