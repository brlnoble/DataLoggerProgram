import PySimpleGUI as sg

sg.theme('DefaultNoMoreNagging')
font = ("Arial, 16")
butFont = ('Airal', 16, 'bold')
iconFont = ('Calibri',20)
titleFont = ('Arial', 20, 'bold')
sg.theme_text_element_background_color('#EEE')
sg.theme_text_color('#333')
sg.theme_background_color('#EEE')


layout = [  [sg.Text('DATA LOGGER', font=titleFont)],
            [sg.Text()],
            [sg.Button('Change Settings',size=(10,2), font=butFont, button_color='Grey'), sg.Push(), sg.Button('View Log',size=(10,2), font=butFont, button_color='Green')],
            [sg.Text()],
            [sg.Button('Exit',size=(10,2), font=butFont, button_color='Red')],
            ]

window = sg.Window('Custom Data Logger', layout, no_titlebar = True, keep_on_top=True, location=(600, 200), element_justification='c')

while True:
    event, values = window.read(timeout=100)
        
    if event == 'Exit': #CLOSE PROGRAM
        break
    elif event == 'Change Settings': #Change the settings
        import SettingsScreen
    elif event == 'View Log': #View the log chart
        import LoggingScreen
    
window.close()