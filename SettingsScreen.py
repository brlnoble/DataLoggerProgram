import PySimpleGUI as sg
import os
import sys
from os.path import exists

#-----PATH-----
if getattr(sys, 'frozen', False): #If an executable, it needs to use this or it takes the temp folder as current path
    path = os.path.dirname(sys.executable)
elif __file__: #if running as a python script
    path = os.path.dirname(__file__)
    
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


# ~~~~~Create the layout of the screen~~~~~
sg.theme('DefaultNoMoreNagging')
font = ('Arial',16)
butFont = ('Airal', 16, 'bold')
iconFont = ('Calibri', 20)
titleFont = ('Arial', 24, 'bold')
sg.theme_text_element_background_color(color='#ABC')
sg.theme_text_color('#1D2873')
sg.theme_background_color('#ABC')

layout = [  [sg.Text('DATA LOGGER SETTINGS', font=titleFont)],
            [sg.Text('Interval (min):',size=(15,1), font=font), sg.Input(key='interval', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Temp Warning (F):',size=(15,1), font=font), sg.Input(key='temp', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Log File (.csv):',size=(15,1), font=font), sg.Input(key='logFile', enable_events=True,size=(15,1), font=font)],
            [sg.Text('',key='tips')],
            [sg.Push(), sg.Button('Submit',size=(10,2), font=butFont, button_color='#02AB29'), sg.Push(), sg.Button('Exit',size=(10,2), font=butFont, button_color='#F5273A'), sg.Push()],
            ]


# ~~~~~DISPLAY WINDOW~~~~~
window = sg.Window('Custom Data Logger', layout, no_titlebar = False, keep_on_top=True, element_justification='c')

# ~~~~~UPDATE CURRENT VALUES IN FORM~~~~~
currSettings = []
intSet = ''
tempSet = ''
with open(path + '\Settings.txt', 'r') as f:
    currSettings = f.readlines()
    
intSet = remove_prefix(currSettings[0],'intervalReading = ').strip()
tempSet = remove_prefix(currSettings[1],'tempWarning = ').strip()
logFile = remove_prefix(currSettings[2],'logFile = ').strip()


event, values = window.read(timeout=100)
window['interval'].update(value = intSet)
window['temp'].update(value = tempSet)
window['logFile'].update(value = logFile)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
while True:
    event, values = window.read(timeout=100)
        
    if event == 'Exit' or event == sg.WIN_CLOSED: #CLOSE PROGRAM
        break
    if event == 'interval' and values['interval'] and values['interval'][-1] not in ('0123456789'):
        window['interval'].update(values['interval'][:-1])
        
    if event == 'temp' and values['temp'] and values['temp'][-1] not in ('0123456789'):
        window['temp'].update(values['temp'][:-1])
        
        
    elif event == 'Submit':
        
        #VERIFY THE FILE EXISTS
        file_exists = exists(values['logFile'])
        if not file_exists:
            file_exists = exists(path + '\\' + values['logFile'])
        
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
                break
            
        #ERROR MESSAGES
        elif not file_exists:
            window['tips'].update('This file does not exist')
        
        elif not int_exists:
            window['tips'].update('Please input an interval less than 100 minutes')
        
        elif not temp_exists:
            window['tips'].update('Please input a temp less than 3000')

window.close()