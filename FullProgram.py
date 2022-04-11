import PySimpleGUI as sg
from tkinter import ttk
from time import time
import datetime
import pandas as pd
import GeneralCommands as GC #Custom file
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#Current directory path
path = GC.get_path()

# ~~~~~MAKE SURE THE SETTINGS FILE EXISTS~~~~~
if not GC.verify_settings(path):
    sg.popup('Settings file does not exist.\n\nA file with default values has been generated.',font=('Arial',20),keep_on_top=True) #inform user it was not found
    
# ~~~~~MAKE SURE THE LOG FILE EXISTS~~~~~
if not GC.verify_logs(path):
    sg.popup('Log file does not exist.\n\nA file with default values has been generated.',font=('Arial',20),keep_on_top=True) #inform user it was not found



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~READ IN SETTING FILE~~~~~
def read_settings():
    #interval in minutes between reading the data
    global readInterval #make sure we change the global variables
    global tempWarn
    global logFile
    global maxRecords
    global chargeRecord
    global emailSend
    readInterval = int(GC.get_settings('Interval', path))*60+5 #convert minutes to seconds, add 5 as a precautionary measure
    tempWarn = int(GC.get_settings('MaxTemp', path))
    logFile = GC.get_settings('LogFile', path)
    maxRecords = int(GC.get_settings('MaxRecords', path))
    chargeRecord = GC.get_settings('Record', path)
    emailSend = GC.get_settings('Email', path)
    
    
# ~~~~~UPDATE THERMOCOUPLE READINGS~~~~~
def update_tc_nums():
    df = pd.read_csv(path + logFile)
    window['lastRead'].update(value=df['Time'].values[-1]) #last time the file was written to
    
    for tc in range(1,7):
        window['TC' + str(tc)].update(str(round(df['Temp' + str(tc)].values[-1],1)) + '°F')
        
        #check high temperature limit
        if round(df['Temp' + str(tc)].values[-1],1) < tempWarn:
            window['TC' + str(tc)].update(background_color='#EEE')
                          
        else: #!!!Temperature over limit!!!
            window['TC' + str(tc)].update(background_color='#F5273A')
            GC.send_email('TC'+str(tc), tempWarn, currTime.strftime("%d %B, %Y - %I:%M %p"))
            
            #Alert the user it is recording
            window['RecordAlert'].update('THERMOCOUPLE TC{} OVER LIMIT'.format(tc))
            window['RecordAlert'].update(background_color='#F5273A')
            
    
    
# ~~~~~Update settings window~~~~~
def update_settings_display():
    event, values = window.read(timeout=100)
    window['interval'].update(value = GC.get_settings('Interval', path))
    window['temp'].update(value = tempWarn)
    window['logFile'].update(value = logFile)
    window['maxRecords'].update(value = maxRecords)
    window['email'].update(value = emailSend)


# ~~~~~Include the Matplotlib figure in the canvas~~~~~
def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)
    

# ~~~~~Updates thermocouples on right of graph~~~~~
def update_tc_graph():
    if len(dates) - 1 >= right:
        window['TC_TL'].update(dates[right])
        window['TC1L'].update(str(round(df.Temp1[right],1)) + '°F')
        window['TC2L'].update(str(round(df.Temp2[right],1)) + '°F')
        window['TC3L'].update(str(round(df.Temp3[right],1)) + '°F')
        window['TC4L'].update(str(round(df.Temp4[right],1)) + '°F')
        window['TC5L'].update(str(round(df.Temp5[right],1)) + '°F')
        window['TC6L'].update(str(round(df.Temp6[right],1)) + '°F')
    else:
        window['TC_TL'].update('Reading: \nUnavailable')
        window['TC1L'].update('000.00' + '°F')
        window['TC2L'].update('000.00' + '°F')
        window['TC3L'].update('000.00' + '°F')
        window['TC4L'].update('000.00' + '°F')
        window['TC5L'].update('000.00' + '°F')
        window['TC6L'].update('000.00' + '°F')
    
    
# ~~~~~Update graphs when zooming~~~~~
def update_graph_view():
    plt.xlim(left,right) #size of viewport
    plt.locator_params(axis='x', nbins=(maxTime/(right-left))*10) #makes sure there are only 10 x-axis ticks at a time
    draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas) #redraw graph
    update_tc_graph() #update TC text on right of graph
    
# ~~~~~Update recording status~~~~~
def update_record():
    
    if chargeRecord != 'N':    
        #Alert the user it is recording
        window['RecordAlert'].update('Currently Recording: ' + chargeRecord)
        window['RecordAlert'].update(background_color='#02AB29')
        
        #Update the button to stop recording
        window['cRecord'].update('Stop Recording')
        window['cRecord'].update(button_color='#F5273A')
        
        #Disable changing the input boxes
        window['ChargeIn'].update(disabled=True)
        window['TempIn'].update(disabled=True)
        window['TimeIn'].update(disabled=True)
        
        
    else:
        #Remove alert for the user
        window['RecordAlert'].update('')
        window['RecordAlert'].update(background_color='#EEE')
        
        #Update the button to stop recording
        window['cRecord'].update('Record')
        window['cRecord'].update(button_color='#02AB29')
        
        #Disable changing the input boxes
        window['ChargeIn'].update(disabled=False)
        window['TempIn'].update(disabled=False)
        window['TimeIn'].update(disabled=False)
        
    #Update settings file
    with open(path + 'Settings.txt', 'w') as f:
        f.write('intervalReading = {}\n'.format(readInterval))
        f.write('tempWarning = {}\n'.format(tempWarn))
        f.write('logFile = {}\n'.format(logFile))
        f.write('maxLogRecords = {}\n'.format(maxRecords))
        f.write('recordCharge = {}\n'.format(chargeRecord))

    

# ~~~~~MATPLOTLIB DISPLAY ALL THE GRAPH DATA~~~~~
def display_graph(fileName):
    # MATPLOTLIB CODE HERE
    global plt
    plt.figure(1)
    global fig
    fig = plt.gcf()
    DPI = fig.get_dpi()
    # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
    fig.set_size_inches(graphSize[0] / float(DPI), graphSize[1] / float(DPI)) #THESE MUST MATCH THE SIZE OF THE ABOVE CANVAS FOR THE GRAPH
    # -------------------------------

    global df
    df = pd.read_csv(path + str(fileName),parse_dates=['Time'], dayfirst=True)
    global dates
    dates = df['Time'].dt.strftime("%d/%b/%y \n %I:%M:%S %p")
    global x
    x = list(range(0,len(dates)))
        
    #thermocouple 1
    y = df.Temp1
    plt.plot(x,y,linewidth=2,marker='o',label='TC1',color='#FF0000') 
    #thermocouple 2
    y = df.Temp2
    plt.plot(x,y,linewidth=2,marker='o',label='TC2',color='#FFAA00')
    #thermocouple 3
    y = df.Temp3
    plt.plot(x,y,linewidth=2,marker='o',label='TC3',color='#365BB0')
    #thermocouple 4
    y = df.Temp4
    plt.plot(x,y,linewidth=2,marker='o',label='TC4',color='#444')
    #thermocouple 5
    y = df.Temp5
    plt.plot(x,y,linewidth=2,marker='o',label='TC5',color='#00B366')
    #thermocouple 6
    y = df.Temp6
    plt.plot(x,y,linewidth=2,marker='o',label='TC6',color='#AA00AA')
    
    update_tc_graph() #adds the readings on the right
    
    #Format the plot
    plt.rc('axes', labelsize=14)
    plt.xlabel('Time',fontweight='bold')
    plt.ylabel('Temperature',fontweight='bold')
    plt.xticks(x,dates) #adds dates to X axis
    plt.locator_params(axis='x', nbins=1.5*zoom) #number of labels on X axis
    plt.gca().spines['right'].set_color('#FF0000') #make rightmost axis red
    plt.gca().spines['right'].set_linewidth(5)
    plt.gca().spines['right'].set_linestyle((0,(1,5)))
    #plt.xlim(left,right) #initial limits X
    plt.ylim([0,1200]) #initial limits Y
    plt.grid(visible=True)
    
    #Adjust the legend to be above the graph
    #l4 = plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=6,frameon=False)
    
    #Display the plot
    global plotDisplay
    plotDisplay = True #flag to prevent moving plot before it is shown
    draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas) #idk what half this does but its necessary
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   

#Window theme
sg.theme('DefaultNoMoreNagging')
font = ("Arial, 16")
butFont = ('Airal', 16, 'bold')
iconFont = ('Calibri',20)
tcFont = ('Courier New',16,'bold')
titleFont = ('Arial', 26, 'bold')
sg.theme_text_element_background_color(color = '#EEE')
sg.theme_text_color('#1D2873')
sg.theme_background_color('#EEE')


# ~~~~~VARIABLES~~~~~
currTime = datetime.datetime.fromtimestamp(time()) #used for clock
lastRead = currTime
readInterval = 0
tempWarn = 0
maxRecords = 0

plotDisplay = False #flag for the plot display
chargeDisplay = False #flag for the charge view
chargeRecord = '' #flag for if we are currently recording a charge
activeScreen  = 'Main' #helps speed up the main loop
emailSend = '' #emails to send alerts to

#Axes limits
zoom = 10
maxZoom = 50
minZoom = 5
left = 0
right = 0
maxTime = 0
stepSize = (readInterval-7)/60 #moves one data point, adjusts for the seconds to minutes conversion
graphSize = (1200, 600)


read_settings() #Get current settings

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  MAIN WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Buttons
butCol = [
            [sg.Button('Settings',size=(20,3), font=butFont, button_color='#1D2873'), sg.Push(), sg.Button('View Previous Log',key='Old Log',size=(20,3), font=butFont, button_color='#F5AC11')],
            [sg.Button('View Current Readout',key='Live Log',size=(42,3), font=butFont, button_color='#02AB29')],
        ]

#LAYOUT FOR ENTIRE WINDOW
wMain = [  
            [sg.Column(butCol)],
            [sg.Text('',font=font)], #spacing
            [sg.Text('',font=font)], #spacing
            [sg.Text('',font=font)], #spacing
            [sg.Text('Reading as of: ',font=butFont),sg.Text('',key='lastRead',font=font)],
            
            [sg.Push(), sg.Text('TC1:',font=butFont),sg.Text('000.0',key='TC1', font=tcFont), 
             sg.Push(), sg.Text('TC2:',font=butFont),sg.Text('000.0',key='TC2', font=tcFont), 
             sg.Push(), sg.Text('TC3:',font=butFont),sg.Text('000.0',key='TC3', font=tcFont),sg.Push()],
            
            [sg.Push(), sg.Text('TC4:',font=butFont),sg.Text('000.0',key='TC4', font=tcFont), 
             sg.Push(), sg.Text('TC5:',font=butFont),sg.Text('000.0',key='TC5', font=tcFont), 
             sg.Push(), sg.Text('TC6:',font=butFont),sg.Text('000.0',key='TC6', font=tcFont),sg.Push()],
            
            [sg.Text('',font=font)], #spacing
            [sg.Button('Exit Program',key='Exit',size=(20,3), font=butFont, button_color='#F5273A')],
        ]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  SETTINGS WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wSet = [  
            [sg.Text('SETTINGS', font=titleFont,pad=(0,50))],
            [sg.Text('Interval (min):',size=(15,1), font=font), sg.Input(key='interval', enable_events=True,size=(20,1), font=font)],
            [sg.Text('Temp Warning (F):',size=(15,1), font=font), sg.Input(key='temp', enable_events=True,size=(20,1), font=font)],
            [sg.Text('Alert Emails:',size=(15,1), font=font), sg.Input(key='email', enable_events=True,size=(20,20), font=font)],
            [sg.Text('',font=font,pad=(0,30))], #spacing
            [sg.Text('Please do not change the following without consulting the manual.',font=butFont,pad=(0,10),text_color='#F5273A')],
            [sg.Text('Log File (.csv):',size=(15,1), font=font), sg.Input(key='logFile', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Max Log Records:',size=(15,1), font=font), sg.Input(key='maxRecords', enable_events=True,size=(15,1), font=font)],
            [sg.Text('',key='tips')],
            [sg.Push(), sg.Button('Submit',size=(10,2), font=butFont, button_color='#02AB29'), sg.Push(), sg.Button('Cancel',size=(10,2), font=butFont, button_color='#F5273A'), sg.Push()],
        ]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  LOGGING WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Thermocouple graph reading
tcGraph = [ 
            [sg.Text('Reading at Red Line',font=butFont,justification='c')],
            [sg.Text()],
            [sg.Text('',key='TC_TL',font=font,justification='c')],
            [sg.Text('TC1: ',font=butFont,text_color='#FF0000'),sg.Text('1',font=tcFont,key='TC1L',text_color='#333')],
            [sg.Text('TC2: ',font=butFont,text_color='#FFAA00'),sg.Text('2',font=tcFont,key='TC2L',text_color='#333')],
            [sg.Text('TC3: ',font=butFont,text_color='#365BB0'),sg.Text('3',font=tcFont,key='TC3L',text_color='#333')],
            [sg.Text('TC4: ',font=butFont,text_color='#444'),sg.Text('4',font=tcFont,key='TC4L',text_color='#333')],
            [sg.Text('TC5: ',font=butFont,text_color='#00B366'),sg.Text('5',font=tcFont,key='TC5L',text_color='#333')],
            [sg.Text('TC6: ',font=butFont,text_color='#AA00AA'),sg.Text('6',font=tcFont,key='TC6L',text_color='#333')],
            
        ]

#Input boxes at top left
inputFormat = [
            [sg.Text('Charge Number:',size=(15,1), font=font), sg.Input(key='ChargeIn', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Temperature:',size=(15,1), font=font), sg.Input(key='TempIn', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Duration:',size=(15,1), font=font), sg.Input(key='TimeIn', enable_events=True,size=(15,1), font=font)],
    ]

#Submit/exit boxes at top right
topButFormat = [
            
    ]

#Zoom buttons
zoomButFormat = [
            [sg.Button('+',key="ZoomIn",size=(5,1), font=iconFont), sg.Button('-',key="ZoomOut",size=(5,1), font=iconFont)]
    ]

#Scroll/homwe buttons
scrollButFormat = [
            [sg.Button('<--',key="Left",size=(10,1), font=iconFont),sg.Button('⌂',key='Home', size=(10,1), font=iconFont), sg.Button('-->',key="Right",size=(10,1), font=iconFont)],
    ]


# ~~~~~MAIN LAYOUT OF THE WHOLE SCREEN~~~~~
wLog = [  
            [sg.Column([
                [sg.Column(inputFormat,pad=(50,0)),sg.Column([[sg.Button('Record',key='cRecord',size=(10,2), font=butFont, button_color='#02AB29')]])],
                ],key='logInput')],
            [sg.Text('',font=butFont,key='cDesc')],
            
            #Plotting stuff
            [sg.Canvas(key='controls_cv')], #idk why this has to be here
            
            #WHERE THE MAGIC HAPPENS
            [sg.Column(
                layout=[
                            #This is the graph
                            [sg.Canvas(key='fig_cv',size=graphSize)], 
                            
                            #This is the slider at the bottom of the graph
                            [sg.Slider(key='Slide',range=(0,maxTime),size=(0,30),enable_events=True,orientation='h',expand_x=True,pad=(100,0),disable_number_display=True,trough_color='#333',background_color='#F5273A')],
                        ], #end layout
                    background_color='#8591AB',pad=(0, 10)), #graph/slider column settings
                sg.Column(tcGraph,element_justification='c',pad=(50,0))], #end of column
            
            [sg.Column(scrollButFormat,pad=(20,5)),sg.VerticalSeparator(pad=None),sg.Column(zoomButFormat,pad=(20,5))]
            ]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  CHARGE WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wCharge = [
            [sg.Text('Please select a charge from the list below.\n',font=font,text_color='#333')],
            [sg.Column(layout=[
                [sg.Text('Charge -- Temp -- Date',font=tcFont)],
                [sg.Text(''),sg.Listbox(values=GC.get_charges(path + 'Charges\\'),size=(27,15),font=('Courier New',16,'bold'),key='cList')] #the text is to align the title and box
            ] )],
            [sg.Button('Select',font=butFont,size=(10,2),button_color='#02AB29')]
    ]



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


tab_group = [
    [sg.Tab("Main", wMain, key="Main",element_justification='c',background_color='#EEEEEE')],
    [sg.Tab("Settings", wSet, key="Set",element_justification='c',background_color='#EEEEEE')],
    [sg.Tab("Logging", wLog, key="Log",element_justification='c',background_color='#EEEEEE')],
    [sg.Tab("Charge", wCharge, key="Charge",element_justification='c',background_color='#EEEEEE')],
]

layout = [
    [sg.Text(key='RecordAlert',font=butFont,background_color='#EEEEEE',text_color='#FFF',expand_x=True,justification='c',pad=(0,0))],
    [sg.Text('DATA LOGGER', key='Title', font=titleFont,pad=(0,20)),sg.Button('Main Screen',size=(10,2), font=butFont, button_color='#F5273A',visible=False)],
    [sg.Text(key='Time',font=butFont)],
    [sg.TabGroup(tab_group, border_width=0, pad=(0, 0), key='TABGROUP')],
]

window = sg.Window("Data Logger", layout, no_titlebar = False, keep_on_top=True, location=(0, 0), element_justification='c').Finalize()
window.Maximize()

style = ttk.Style()
style.layout('TNotebook.Tab', []) # Hide tab bar


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  MAIN LOOP  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
event, values = window.read(timeout=100)
update_tc_nums()

while True:

    event, values = window.read(timeout=100)

    #See if window should be closed
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    
    #Update the clock
    currTime = datetime.datetime.fromtimestamp(time())
    window['Time'].update(currTime.strftime("%d %B, %Y - %I:%M:%S %p"))
    
    #Check if it is time to update the TC readings
    if currTime - datetime.timedelta(seconds=readInterval) > lastRead:
        lastRead = currTime
        update_tc_nums()
        if plotDisplay and not chargeDisplay:
            plt.clf()
            display_graph(logFile)
            update_graph_view()
    
    if event == 'Main Screen': #RETURN TO MAIN SCREEN
        plotDisplay = False
        chargeDisplay = False
        window['Main Screen'].update(visible=False)
        window['Title'].update(visible=True)
        window["Main"].select()
        activeScreen = 'Main'
        
    
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  LOGGING WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    elif event == 'Live Log': #View the log chart
        window['Main Screen'].update(visible=True)
        window['Title'].update(visible=False)
        window["Log"].select()
        window['logInput'].update(visible = True)
        window['cDesc'].update(visible=False)
        window['cRecord'].update(disabled=False)
        activeScreen = 'Log'
        
        if plotDisplay == False: #If not currently displaying plot, basically only run on startup
            display_graph(logFile)
            
            #~~~Setup initial axes~~~
            zoom = 10
            right = max(x) #most recent reading
            maxTime = right #global storage of above for Home button
            left = right - zoom #make view to be towards the end of readings
            window['Slide'].update(range=(0,maxTime)) #Update the slider on the bottom of the graph
            window['Slide'].update(value=maxTime) #Set slider to right side of graph
            update_graph_view()
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~BUTTON CLICK EVENTS~~~~~
    elif activeScreen == 'Log':
        
        # if emailTry:
        #     if GC.send_email('TC1', tempWarn, currTime.strftime("%d %B, %Y - %I:%M:%S %p")):
        #         sg.popup('Email sent successfully.',font=font,keep_on_top=True)
        #         emailTry = False
        #     else:
        #         sg.popup('Failed to send email.',font=font,keep_on_top=True)
        #         emailTry = False
        
        if event == 'Left' and plotDisplay:
            #Move the plot left
            left -= 1
            right -= 1
            window['Slide'].update(value=right) #adjsut slider
            update_graph_view()
            
        elif event =='Right' and plotDisplay:
            #Move plot right
            left += 1
            right += 1
            if right < maxTime:
                window['Slide'].update(value=right) #adjsut slider
            else:
                window['Slide'].update(value=maxTime) #adjsut slider
            update_graph_view()
            
        elif event == 'Home' and plotDisplay:
            #Return to home view
            zoom = 10
            left = maxTime - zoom
            right = maxTime
            window['Slide'].update(value=right) #Return slider to right side
            update_graph_view()
        
        elif event == 'ZoomOut' and plotDisplay:
            #Zoom out graph
            if zoom < maxZoom:
                zoom = zoom + 5
                left = right - zoom
                update_graph_view()
            
        elif event == 'ZoomIn' and plotDisplay:
            #Zoom in graph
            if zoom > minZoom:
                zoom = zoom - 5
                left = right - zoom
                update_graph_view()
        
        elif event == 'Slide' and plotDisplay:
            right = values['Slide']
            left = values['Slide'] - zoom
            update_graph_view()
        
        elif event == 'C Plot':
            plt.clf()
            update_graph_view()
     
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~RECORDING A CHARGE~~~~~
        elif event == 'ChargeIn' and values['ChargeIn'] and (values['ChargeIn'][-1] not in ('0123456789') or len(values['ChargeIn']) > 5):
            window['ChargeIn'].update(values['ChargeIn'][:-1])
            
        elif event == 'TempIn' and values['TempIn'] and (values['TempIn'][-1] not in ('0123456789') or len(values['TempIn']) > 4):
            window['TempIn'].update(values['TempIn'][:-1])
            
        elif event == 'TimeIn' and values['TimeIn'] and (values['TimeIn'][-1] not in ('0123456789') or len(values['TimeIn']) >4):
            window['TimeIn'].update(values['TimeIn'][:-1])
        
        
        #Recording a new charge
        elif event == 'cRecord' and chargeRecord == 'N':
            #Verify inputs
            cCheck = False
            tCheck = False
            dCheck = False
            
            if values['ChargeIn'] and len(values['ChargeIn']) == 5:
                if(GC.check_charge(values['ChargeIn'], path + 'Charges\\')):
                    cCheck = True
                else:
                    sg.popup('This charge number is already in use!',font=font,keep_on_top=True)
                    
            if values['TempIn'] and int(values['TempIn']) > 0:
                tCheck = True
                if len(values['TempIn']) < 4:
                    values['TempIn'] = '0' + str(values['TempIn']) #zero pad for charge log
            if values['TimeIn'] and 50 > int(values['TimeIn']) > 0:
                dCheck = True
                
            #If all the inputs are good, record the charge    
            if cCheck and tCheck and dCheck:
                chargeRecord = values['ChargeIn'] + ' -- ' + values['TempIn'] + ' -- ' + currTime.strftime("%d-%b-%y") #Filename to save
                
                update_record()
                
                
                
            elif not cCheck:
                sg.popup('Please input a 5 digit charge number.',font=font,keep_on_top=True)
            elif not tCheck:
                sg.popup('Please input a temperature.',font=font,keep_on_top=True)
            elif not dCheck:
                sg.popup('Please input a duration less than 50 hours.',font=font,keep_on_top=True)
        
                
        
        #If stopping charge recording
        elif event == 'cRecord' and chargeRecord != 'N':
            chargeRecord = 'N'
            
            update_record()
            sg.popup('Recording cancelled.',font=font,keep_on_top=True)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  CHARGE WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    elif event == 'Old Log':
        window['Main Screen'].update(visible=True)
        window['Title'].update(visible=False)
        window['Charge'].select()
        #window['logInput'].update(visible = False) #hide the input boxes
        activeScreen = 'Charge'
        
    elif event == 'Select' and values['cList']:
        window["Log"].select()
        window['logInput'].update(visible = False)
        window['cDesc'].update(visible=True)
        window['cDesc'].update('You are viewing: ' + str(values['cList'][0]))
        activeScreen = 'Log'
        
        if plotDisplay == False: #If not currently displaying plot
            chargeDisplay = True
            display_graph('Charges\\' + str(values['cList'][0]) + '.csv')
            
            #~~~Setup initial axes~~~
            zoom = 10
            right = max(x) #most recent reading
            maxTime = right #global storage of above for Home button
            left = right - zoom #make view to be towards the end of readings
            window['Slide'].update(range=(0,maxTime)) #Update the slider on the bottom of the graph
            window['Slide'].update(value=maxTime) #Set slider to right side of graph
            update_graph_view()
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  SETTINGS WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    elif event == "Settings": #Switch to settings window
        window['Main Screen'].update(visible=True)
        window['Title'].update(visible=False)
        window["Set"].select()
        update_settings_display()
        activeScreen = 'Settings'
        
    elif activeScreen == 'Settings':
    
        if event == "Cancel": #Return from settings window
            window["Main"].select()
            window['Main Screen'].update(visible=False)
            window['Title'].update(visible=True)
            
        elif event == 'interval' and values['interval'] and values['interval'][-1] not in ('0123456789'):
            window['interval'].update(values['interval'][:-1])
            
        elif event == 'temp' and values['temp'] and values['temp'][-1] not in ('0123456789'):
            window['temp'].update(values['temp'][:-1])
            
        elif event == 'maxRecords' and values['maxRecords'] and values['maxRecords'][-1] not in ('0123456789'):
            window['maxRecords'].update(values['maxRecords'][:-1])
            
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
                
            #VERIFY RECORDS WAS INPUT
            maxR_exists = True
            if values['maxRecords'] == '' or int(values['maxRecords']) < 100:
                maxR_exists = False
            
            #SAVE THE FILE
            if file_exists and int_exists and temp_exists and maxR_exists:
                with open(path + 'Settings.txt', 'w') as f:
                    f.write('intervalReading = {}\n'.format(values['interval']))
                    f.write('tempWarning = {}\n'.format(values['temp']))
                    f.write('logFile = {}\n'.format(values['logFile']))
                    f.write('maxLogRecords = {}\n'.format(values['maxRecords']))
                    f.write('recordCharge = {}\n'.format(chargeRecord))
                    f.write('emailTo = {}'.format(values['email']))
                read_settings()
                sg.Popup('Settings have been changed successfully.',font=titleFont,keep_on_top=True)
                window['Main Screen'].update(visible=False)
                window['Title'].update(visible=True)
                window["Main"].select()
                
                
            #ERROR MESSAGES
            elif not file_exists:
                sg.popup('This file does not exist!',keep_on_top=True)
            
            elif not int_exists:
                sg.popup('Please input an interval less than 100 minutes',keep_on_top=True)
            
            elif not temp_exists:
                sg.popup('Please input a temperature less than 3000°F',keep_on_top=True)
                
            elif not maxR_exists:
                sg.popup('Please input a maximum number of records greater than 100',keep_on_top=True)
        
window.close()




# ~~~~~ References ~~~~~
# https://github.com/PySimpleGUI/PySimpleGUI/issues/3946        Tab groups and hiding tabs


# ~~~~~ Compile ~~~~~
#pyinstaller -wF --splash=splashLoad.jpg FullProgram.py
#pyinstaller -wF --splash=splashLoad.jpg --icon=test.ico FullProgram.py