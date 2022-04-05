import PySimpleGUI as sg

# ~~~~~Create the layout of the screen~~~~~
sg.theme('DefaultNoMoreNagging')
font = ("Arial, 16")
butFont = ('Airal', 16, 'bold')
iconFont = ('Calibri',20)
titleFont = ('Arial', 24, 'bold')
sg.theme_text_element_background_color(color=None)
sg.theme_text_color('#1D2873')
sg.theme_background_color('#EEE')

layout = [  [sg.Text('DATA LOGGER SETTINGS', font=titleFont)],
            [sg.Text('Interval (min):',size=(15,1), font=font), sg.Input(key='interval', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Temp Warning (F):',size=(15,1), font=font), sg.Input(key='temp', enable_events=True,size=(15,1), font=font)],
            [sg.Text()],
            [sg.Push(), sg.Button('Submit',size=(10,2), font=butFont, button_color='#02AB29'), sg.Push(), sg.Button('Exit',size=(10,2), font=butFont, button_color='#F5273A'), sg.Push()],
            ]


# ~~~~~DISPLAY WINDOW~~~~~
window = sg.Window('Custom Data Logger', layout, no_titlebar = True, keep_on_top=True, location=(600, 200), element_justification='c')

while True:
    event, values = window.read(timeout=100)
        
    if event == 'Exit' or event == sg.WIN_CLOSED: #CLOSE PROGRAM
        break
    if event == 'interval' and values['interval'] and values['interval'][-1] not in ('0123456789'):
        window['interval'].update(values['interval'][:-1])
    if event == 'temp' and values['temp'] and values['temp'][-1] not in ('0123456789'):
        window['temp'].update(values['temp'][:-1])
    elif event == 'Submit':
        with open('Settings.txt', 'w') as f:
            f.write('intervalReading = {}'.format(values['interval']))
            f.write('\n')
            f.write('tempWarning = {}'.format(values['temp']))
            break

window.close()