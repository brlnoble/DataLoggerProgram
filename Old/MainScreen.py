import PySimpleGUI as sg
from time import time
import datetime
import pandas as pd
import GeneralCommands as GC

#-----PATH-----
path = GC.get_path()
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~READ IN SETTING FILE~~~~~
def read_settings():
    #interval in minutes between reading the data
    global readInterval #make sure we change the global variable  
    global tempWarn #make sure we change the global variable
    global logFile
    readInterval = int(GC.get_settings('Interval', path))*60+5
    tempWarn = int(GC.get_settings('MaxTemp', path))
    logFile = GC.get_settings('LogFile', path)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    
# ~~~~~UPDATE THERMOCOUPLE READINGS~~~~~
def update_tc_nums():
    df = pd.read_csv(path + '\9timeTest.csv')
    window['lastRead'].update(value=df['Time'].values[-1]) #last time the file was written to
    #window['lastRead'].update(value=lastRead)
    
    window['TC1'].update(str(round(df['Temp1'].values[-1],1)) + '°F')
    window['TC2'].update(str(round(df['Temp2'].values[-1],1)) + '°F')
    window['TC3'].update(str(round(df['Temp3'].values[-1],1)) + '°F')
    window['TC4'].update(str(round(df['Temp4'].values[-1],1)) + '°F')
    window['TC5'].update(str(round(df['Temp5'].values[-1],1)) + '°F')
    window['TC6'].update(str(round(df['Temp6'].values[-1],1)) + '°F')
    
    

sg.theme('DefaultNoMoreNagging')
font = ("Arial, 16")
butFont = ('Airal', 16, 'bold')
iconFont = ('Calibri',20)
tcFont = ('Courier New',16,'bold')
titleFont = ('Arial', 24, 'bold')
sg.theme_text_element_background_color(color = '#EEEEEE')
sg.theme_text_color('#1D2873')
sg.theme_background_color('#EEEEEE')


# ~~~~~VARIABLES~~~~~
currTime = datetime.datetime.fromtimestamp(time()) #used for clock
lastRead = currTime
readInterval = 0
tempWarn = 0

read_settings()

#Buttons
butCol = [
            [sg.Push(),sg.Button('Settings',size=(20,3), font=butFont, button_color='#1D2873'), sg.Push(), sg.Button('Live Log',size=(20,3), font=butFont, button_color='#02AB29'), sg.Push()],
            [sg.Push(),sg.Button('',size=(20,3), font=butFont, button_color='#111'), sg.Push(),sg.Button('Old Log',size=(20,3), font=butFont, button_color='#F5AC11'), sg.Push()],
        ]

#LAYOUT FOR ENTIRE WINDOW
layout = [  [sg.Text('DATA LOGGER', key='Title', font=titleFont)],
            [sg.VPush()],
            [sg.Text(key='Time',font=butFont)],
            [sg.VPush()],
            [sg.Column(butCol)],
            [sg.VPush()],
            
            [sg.Text('Reading as of: ',font=butFont),sg.Text('',key='lastRead',font=font)],
            
            [sg.Push(), sg.Text('TC1:',font=butFont),sg.Text('000.0',key='TC1', font=tcFont), 
             sg.Push(), sg.Text('TC2:',font=butFont),sg.Text('000.0',key='TC2', font=tcFont), 
             sg.Push(), sg.Text('TC3:',font=butFont),sg.Text('000.0',key='TC3', font=tcFont),sg.Push()],
            
            [sg.Push(), sg.Text('TC4:',font=butFont),sg.Text('000.0',key='TC4', font=tcFont), 
             sg.Push(), sg.Text('TC5:',font=butFont),sg.Text('000.0',key='TC5', font=tcFont), 
             sg.Push(), sg.Text('TC6:',font=butFont),sg.Text('000.0',key='TC6', font=tcFont),sg.Push()],
            
            [sg.VPush()],
            [sg.Button('Exit',size=(10,2), font=butFont, button_color='#F5273A')],
            [sg.VPush()],
        ]

window = sg.Window('Custom Data Logger', layout, no_titlebar = False, keep_on_top=True, location=(0, 0), element_justification='c').Finalize()
#window.Maximize()

event, values = window.read(timeout=100)
update_tc_nums()

while True:
    event, values = window.read(timeout=100)
        
    #Update the clock
    currTime = datetime.datetime.fromtimestamp(time())
    window['Time'].update(currTime.strftime("%d %B, %Y - %I:%M:%S %p"))
    
    #Check if it is time to update the TC readings
    if currTime - datetime.timedelta(seconds=readInterval) > lastRead:
        #print(currTime.strftime("%d %B, %Y - %I:%M:%S %p"))
        lastRead = currTime
        update_tc_nums()

        
    if event == 'Exit' or event == sg.WIN_CLOSED: #CLOSE PROGRAM
        break
    elif event == 'Settings': #Change the settings
        import SettingsScreen
        #os.startfile(path + '\SettingsScreen.exe') #runs in a separate thread, does not change the settings on completion
        read_settings()
        #window['Title'].update(str(readInterval))
    elif event == 'Live Log': #View the log chart
        import LoggingScreen
    
window.close()
