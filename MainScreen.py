import PySimpleGUI as sg
from time import time
import datetime

sg.theme('DefaultNoMoreNagging')
font = ("Arial, 16")
butFont = ('Airal', 16, 'bold')
iconFont = ('Calibri',20)
tcFont = ('Courier New',16,'bold')
titleFont = ('Arial', 24, 'bold')
sg.theme_text_element_background_color(color = None)
sg.theme_text_color('#1D2873')
sg.theme_background_color('#EEEEEE')


currTime = datetime.datetime.fromtimestamp(time()) #used for clock

#Buttons
butCol = [
            [sg.Push(),sg.Button('Settings',size=(20,3), font=butFont, button_color='#1D2873'), sg.Push(), sg.Button('Live Log',size=(20,3), font=butFont, button_color='#02AB29'), sg.Push()],
            [sg.Push(),sg.Button('',size=(20,3), font=butFont, button_color='#111'), sg.Push(),sg.Button('Old Log',size=(20,3), font=butFont, button_color='#F5AC11'), sg.Push()],
        ]

#LAYOUT FOR ENTIRE WINDOW
layout = [  [sg.Text('DATA LOGGER', font=titleFont)],
            [sg.VPush()],
            [sg.Text(key='Time',font=butFont)],
            [sg.VPush()],
            [sg.Column(butCol)],
            [sg.Push(),sg.Text('',key='TC1', font=tcFont), sg.Push(), sg.Text('',key='TC2', font=tcFont), sg.Push(), sg.Text('',key='TC3', font=tcFont),sg.Push()],
            [sg.Push(),sg.Text('',key='TC4', font=tcFont), sg.Push(), sg.Text('',key='TC5', font=tcFont), sg.Push(), sg.Text('',key='TC6', font=tcFont),sg.Push()],
            [sg.VPush()],
            [sg.Button('Exit',size=(10,2), font=butFont, button_color='#F5273A')],
            [sg.VPush()],
        ]

window = sg.Window('Custom Data Logger', layout, no_titlebar = False, keep_on_top=True, location=(0, 0), element_justification='c').Finalize()
window.Maximize()

while True:
    event, values = window.read(timeout=100)
    
    #Update the clock
    currTime = datetime.datetime.fromtimestamp(time())
    window['Time'].update(currTime.strftime("%d %B, %Y - %I:%M:%S %p"))
    
    window['TC1'].update('TC1: ' + '000.0')
    window['TC2'].update('TC2: ' + '000.0')
    window['TC3'].update('TC3: ' + '000.0')
    window['TC4'].update('TC4: ' + '000.0')
    window['TC5'].update('TC5: ' + '000.0')
    window['TC6'].update('TC6: ' + '000.0')
        
    if event == 'Exit' or event == sg.WIN_CLOSED: #CLOSE PROGRAM
        break
    elif event == 'Settings': #Change the settings
        import SettingsScreen
    elif event == 'Live Log': #View the log chart
        import LoggingScreen
    
window.close()