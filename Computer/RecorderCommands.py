import os
import json
from datetime import datetime

# ~~~~~Directory of this program~~~~~
def Get_Path():
    return '//DISKSTATION1/mill/1 - Mill/Data Logger/' #Path on RPi


# ~~~~~Removes the beginning of a string
def Remove_Prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


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
    
    currSet = Get_Settings("all", path)
    currSet[selection] = value
    
    with open(path+"Program/Settings.json","w") as f:
        json.dump(currSet,f,indent=4)


# ~~~~~Get the system settings~~~~~
def Get_Settings(selection, path):
    with open(path+"Program/Settings.json","r") as f:
        currSet = json.load(f)
    
    if selection == "all":
        return currSet
    return currSet[selection]
    

# ~~~~~Check if a file exists~~~~~
def Does_This_Exist(path,fileName):
    return os.path.exists(path + fileName)


# ~~~~~Check file modification~~~~~
def Get_M_Time(path,fileName):
    return os.path.getmtime(path + fileName)


# ~~~~~Make folder~~~~~
def Make_Folder(folderPath):
    os.makedirs(folderPath)


# ~~~~~Open folder~~~~~
def Open_Folder(path):
    os.startfile(os.path.realpath(path))
    
    
# ~~~~~Get saved charges~~~~~
def Get_Charges(path, charge_filter='', temp_filter='', date_filter=''):
    #Make sure folder exists
    if not Does_This_Exist(path,'Charges/'):
        os.mkdir(path+'Charges/') #create folder if not present
    
    path += 'Charges/'
    #Collect all files in folder
    files = [f.strip('.csv') for f in os.listdir(path) if os.path.exists(path + f)]
    
    #~~~~~~~~~~
    if charge_filter == '' and temp_filter == ''and date_filter == '': #If not filtering the search
        return sorted(files,reverse=True) #Return list newest to oldest
    
    #~~~~~~~~~~
    if charge_filter != '':
        filter_files = []
        for file in files:
            if charge_filter in file:
                filter_files.append(file)
        
        files = filter_files
        
    #~~~~~~~~~~    
    if temp_filter != '':
        if len(temp_filter) < 4:
            temp_filter = "0"+temp_filter
        filter_files = []
        for file in files:
            if temp_filter in file:
                filter_files.append(file)
        
        files = filter_files
    
    #~~~~~~~~~~
    if date_filter != '':
        #We must first format the time correctly
        timeConvert = ""
        allowedFormats = ["%d/%m/%Y","%d/%m/%y","%d/%b/%Y","%d/%b/%y", "%d-%m-%Y","%d-%m-%y","%d-%b-%Y","%d-%b-%y"]

        for dateFormat in allowedFormats:
            try:
                timeConvert = datetime.strptime(date_filter,dateFormat).strftime("%d-%b-%y")
                break
            except:
                pass #Ignore error
        
        #If unable to find date, see if user only input month and year
        if timeConvert == "":
            allowedFormats = [
                "%m/%Y","%m/%y","%b/%Y","%b/%y", 
                "%m-%Y","%m-%y","%b-%Y","%b-%y", 
                "%m, %Y","%m, %y","%b, %Y","%b, %y", 
                "%m %Y","%m %y","%b %Y","%b %y",
                "%B %y", "%B %Y", 
                "%B, %y", "%B, %Y",
                "%B-%y", "%B-%Y",
                "%B/%y", "%B/%Y", 
            ]

            for dateFormat in allowedFormats:
                try:
                    timeConvert = datetime.strptime(date_filter,dateFormat).strftime("%b-%y")
                    break
                except:
                    pass #Ignore error
            
            if timeConvert == "":
                return ["Invalid date entered","Could not complete search"]

        #Complete the search
        filter_files = []
        for file in files:
            if timeConvert in file:
                filter_files.append(file)
        
        files = filter_files
    
    #~~~~~~~~~~
    return sorted(files,reverse=True) #Return list newest to oldest

# ~~~~~Compare charges~~~~~
def Check_Charge(path,charge):
    files = Get_Charges(path)
    for c in files:
        if str(charge+' ') == c[:6]:
            return [False,c]
    return [True,'']

    
# ~~~~~Error Log~~~~~
def Error_Log(path,err,currTime):
    with open(path+'Program/Error-Logs.txt','a') as f:
        f.writeline(currTime + ' ----- ' + err)


# ~~~~~Get Error Logs~~~~~
def Get_Err(path):
    path += "Program/"
    with open(path+"Error-Logs.txt",'r') as f:
        lines = f.readlines()
    return sorted(lines,reverse=True)


# ~~~~~Reuse Charge~~~~~
def Reuse(path,cNum):
    charges = get_charges(path) #Get files
    for file in charges:
        if file[:6] == cNum+' ': #Find file
            os.rename(path+'Charges/'+file+'.csv',path+'Charges/'+file[:5]+'F'+file[5:]+'.csv') #Add F to the old file


# ~~~~~Overwrite Charge~~~~~
def Overwrite(path,cNum):
    charges = get_charges(path)
    for file in charges:
        if file[:6] == cNum+' ':
            os.remove(path+'Charges/'+file+'.csv')

# ~~~~~Scale Base64~~~~~
def Scale_Base64(base64_str,scale):
    from io import BytesIO
    from base64 import b64decode, b64encode
    from PIL import Image
    
    buffer = BytesIO()
    imgdata = b64decode(base64_str)
    img = Image.open(BytesIO(imgdata))
    width, height = img.size #Original size of image
    new_img = img.resize((round(width*scale), round(height*scale))) #Resize image
    new_img.save(buffer, format="PNG")
    img_b64 = b64encode(buffer.getvalue()) #Encode to base64
    return str(img_b64)[2:-1].encode()


# ~~~~~Calibration Numbers~~~~~
def Get_Calibration(path):
    with open(path+"Program/Calibration.json","r") as f:
        calibration_numbers = json.load(f)
    return calibration_numbers
    
def Save_Calibrations(path,values):
    with open(path+"Program/Calibration.json","w") as f:
            json.dump(values,f,indent=4)
    return