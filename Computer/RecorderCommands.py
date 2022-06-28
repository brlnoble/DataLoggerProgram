import os
import json

# ~~~~~Directory of this program~~~~~
def get_path():
    return 'C:/Users/Darryn/Desktop/Code/DATA LOGGER PI/Raspberry Pi/JSON Migration/' #Path on RPi


# ~~~~~Removes the beginning of a string
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


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

# ~~~~~Check file modification~~~~~
def get_mtime(path,fileName):
    return os.path.getmtime(path + fileName)

# ~~~~~Make folder~~~~~
def make_folder(folderPath):
    os.makedirs(folderPath)
    
# ~~~~~Open folder~~~~~
def open_folder(path):
    os.startfile(os.path.realpath(path))
    
    
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
        if str(charge+' ') == c[:6]:
            return [False,c]
    return [True,'']

    
# ~~~~~Error Log~~~~~
def error_Log(path,err,currTime):
    with open(path+'Program/Error-Logs.txt','a') as f:
        f.writeline(currTime + ' ----- ' + err)
        
# ~~~~~Get Error Logs~~~~~
def get_err(path):
    path += "Program/"
    with open(path+"Error-Logs.txt",'r') as f:
        lines = f.readlines()
    return sorted(lines,reverse=True)

# ~~~~~Reuse Charge~~~~~
def reuse(path,cNum):
    charges = get_charges(path) #Get files
    for file in charges:
        if file[:6] == cNum+' ': #Find file
            os.rename(path+'Charges/'+file+'.csv',path+'Charges/'+file[:5]+'F'+file[5:]+'.csv') #Add F to the old file
            
# ~~~~~Overwrite Charge~~~~~
def overwrite(path,cNum):
    charges = get_charges(path)
    for file in charges:
        if file[:6] == cNum+' ':
            os.remove(path+'Charges/'+file+'.csv')
