import PySimpleGUI as sg
from tkinter import ttk
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
    
# ~~~~~Update settings window~~~~~
def update_setttings_display():
    event, values = window.read(timeout=100)
    window['interval'].update(value = GC.get_settings('Interval', path))
    window['temp'].update(value = tempWarn)
    window['logFile'].update(value = logFile)
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  MAIN WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Buttons
butCol = [
            [sg.Push(),sg.Button('Settings',size=(20,3), font=butFont, button_color='#1D2873'), sg.Push(), sg.Button('Live Log',size=(20,3), font=butFont, button_color='#02AB29'), sg.Push()],
            [sg.Push(),sg.Button('',size=(20,3), font=butFont, button_color='#111'), sg.Push(),sg.Button('Old Log',size=(20,3), font=butFont, button_color='#F5AC11'), sg.Push()],
        ]

#LAYOUT FOR ENTIRE WINDOW
wMain = [  
            [sg.Text('DATA LOGGER', key='Title', font=titleFont)],
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


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  SETTINGS WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wSet = [  
            [sg.Text('DATA LOGGER SETTINGS', font=titleFont)],
            [sg.Text('Interval (min):',size=(15,1), font=font), sg.Input(key='interval', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Temp Warning (F):',size=(15,1), font=font), sg.Input(key='temp', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Log File (.csv):',size=(15,1), font=font), sg.Input(key='logFile', enable_events=True,size=(15,1), font=font)],
            [sg.Text('',key='tips')],
            [sg.Push(), sg.Button('Submit',size=(10,2), font=butFont, button_color='#02AB29'), sg.Push(), sg.Button('Cancel',size=(10,2), font=butFont, button_color='#F5273A'), sg.Push()],
        ]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


tab_group = [
    [sg.Tab("Main", wMain, key="Main",element_justification='c')],
    [sg.Tab("Settings", wSet, key="Set",element_justification='c')],
]

layout = [
    [sg.TabGroup(tab_group, border_width=0, pad=(0, 0), key='TABGROUP')],
]

style = ttk.Style()
style.layout('TNotebook.Tab', []) # Hide tab bar

window = sg.Window("Data Logger", layout, no_titlebar = False, keep_on_top=True, location=(0, 0), element_justification='c').Finalize()
window.Maximize()





#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  MAIN LOOP  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
        
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    
    elif event == "Settings": #Switch to settings window
        window["Set"].select()
        update_setttings_display()
    elif event == "Cancel": #Return from settings window
        window["Main"].select()
    if event == 'interval' and values['interval'] and values['interval'][-1] not in ('0123456789'):
        wSet['interval'].update(values['interval'][:-1])
        
    if event == 'temp' and values['temp'] and values['temp'][-1] not in ('0123456789'):
        wSet['temp'].update(values['temp'][:-1])
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    elif event == 'Submit':
        
        #VERIFY THE FILE EXISTS
        file_exists = GC.does_this_exist(values['logFile'])
        
        #VERIFY INTERVAL WAS INPUT
        int_exists = True
        if values['interval'] == '' or int(values['interval']) > 100:
            int_exists = False
            
        #VERIFY TEMP WAS INPUT
        temp_exists = True
        if values['temp'] == '' or int(values['temp']) > 3000:
            temp_exists = False
        
        #SEE IF WE CAN SAVE THE FILE
        if file_exists and int_exists and temp_exists:
            with open(path + '\Settings.txt', 'w') as f:
                f.write('intervalReading = {}'.format(values['interval']))
                f.write('\n')
                f.write('tempWarning = {}'.format(values['temp']))
                f.write('\n')
                f.write('logFile = {}'.format(values['logFile']))
                read_settings()
                break
            
        #ERROR MESSAGES
        elif not file_exists:
            sg.popup('This file does not exist!',keep_on_top=True)
        
        elif not int_exists:
            sg.popup('Please input an interval less than 100 minutes',keep_on_top=True)
        
        elif not temp_exists:
            sg.popup('Please input a temperature less than 3000°F',keep_on_top=True)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    elif event == 'Live Log': #View the log chart
        import LoggingScreen
        
window.close()