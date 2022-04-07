import PySimpleGUI as sg
from tkinter import ttk
from time import time
import datetime
import pandas as pd
import GeneralCommands as GC
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#Current directory path
path = GC.get_path()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~READ IN SETTING FILE~~~~~
def read_settings():
    #interval in minutes between reading the data
    global readInterval #make sure we change the global variables
    global tempWarn
    global logFile
    global maxRecords
    readInterval = int(GC.get_settings('Interval', path))*60+5 #convert minutes to seconds, add 5 as a precautionary measure
    tempWarn = int(GC.get_settings('MaxTemp', path))
    logFile = GC.get_settings('LogFile', path)
    maxRecords = int(GC.get_settings('MaxRecords', path))
    
    
# ~~~~~UPDATE THERMOCOUPLE READINGS~~~~~
def update_tc_nums():
    df = pd.read_csv(path + '\9timeTest.csv')
    window['lastRead'].update(value=df['Time'].values[-1]) #last time the file was written to
    
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
    window['maxRecords'].update(value = maxRecords)


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
    df = pd.read_csv(path + '\\' + str(fileName),parse_dates=['Time'], dayfirst=True)
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
    plt.grid()
    
    #Adjust the legend to be above the graph
    #l4 = plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=6,frameon=False)
    
    #Display the plot
    global plotDisplay
    plotDisplay = True #flag to prevent moving plot before it is shown
    draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas) #idk what half this does but its necessary
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   

sg.theme('DefaultNoMoreNagging')
font = ("Arial, 16")
butFont = ('Airal', 16, 'bold')
iconFont = ('Calibri',20)
tcFont = ('Courier New',16,'bold')
titleFont = ('Arial', 26, 'bold')
sg.theme_text_element_background_color(color = '#EEEEEE')
sg.theme_text_color('#1D2873')
sg.theme_background_color('#EEEEEE')


# ~~~~~VARIABLES~~~~~
currTime = datetime.datetime.fromtimestamp(time()) #used for clock
lastRead = currTime
readInterval = 0
tempWarn = 0
maxRecords = 0

plotDisplay = False #flag for the plot display

#Axes limits
zoom = 10
maxZoom = 50
minZoom = 5
left = 0
right = 0
maxTime = 0
stepSize = (readInterval-7)/60 #moves one data point, adjusts for the seconds to minutes conversion
graphSize = (1200, 600)


read_settings()

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
            [sg.Text('Reading as of: ',font=butFont),sg.Text('',key='lastRead',font=font)],
            
            [sg.Push(), sg.Text('TC1:',font=butFont),sg.Text('000.0',key='TC1', font=tcFont), 
             sg.Push(), sg.Text('TC2:',font=butFont),sg.Text('000.0',key='TC2', font=tcFont), 
             sg.Push(), sg.Text('TC3:',font=butFont),sg.Text('000.0',key='TC3', font=tcFont),sg.Push()],
            
            [sg.Push(), sg.Text('TC4:',font=butFont),sg.Text('000.0',key='TC4', font=tcFont), 
             sg.Push(), sg.Text('TC5:',font=butFont),sg.Text('000.0',key='TC5', font=tcFont), 
             sg.Push(), sg.Text('TC6:',font=butFont),sg.Text('000.0',key='TC6', font=tcFont),sg.Push()],
            
            [sg.Text('',font=font)], #spacing
            [sg.Button('Exit',size=(10,2), font=butFont, button_color='#F5273A')],
        ]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  SETTINGS WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wSet = [  
            [sg.Text('SETTINGS', font=titleFont,pad=(0,50))],
            [sg.Text('Interval (min):',size=(15,1), font=font), sg.Input(key='interval', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Temp Warning (F):',size=(15,1), font=font), sg.Input(key='temp', enable_events=True,size=(15,1), font=font)],
            [sg.Text('',font=font,pad=(0,30))],
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
            [sg.Text('TC1: ',font=butFont,text_color='#FF0000'),sg.Text('1',font=font,key='TC1L',text_color='#333')],
            [sg.Text('TC2: ',font=butFont,text_color='#FFAA00'),sg.Text('2',font=font,key='TC2L',text_color='#333')],
            [sg.Text('TC3: ',font=butFont,text_color='#365BB0'),sg.Text('3',font=font,key='TC3L',text_color='#333')],
            [sg.Text('TC4: ',font=butFont,text_color='#444'),sg.Text('4',font=font,key='TC4L',text_color='#333')],
            [sg.Text('TC5: ',font=butFont,text_color='#00B366'),sg.Text('5',font=font,key='TC5L',text_color='#333')],
            [sg.Text('TC6: ',font=butFont,text_color='#AA00AA'),sg.Text('6',font=font,key='TC6L',text_color='#333')],
            
        ]

#Input boxes at top left
inputFormat = [
            [sg.Text('Charge Number:',size=(15,1), font=font), sg.Input(key='ChargeIn', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Temperature:',size=(15,1), font=font), sg.Input(key='TempIn', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Duration:',size=(15,1), font=font), sg.Input(key='TimeIn', enable_events=True,size=(15,1), font=font)],
    ]

#Submit/exit boxes at top right
topButFormat = [
            [sg.Button('Record',size=(10,2), font=butFont, button_color='#02AB29'), sg.Button('Main Screen',size=(10,2), font=butFont, button_color='#F5273A')],
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
wLog = [  #[sg.Text('DATA LOGGER PLOT', font=titleFont)],
            [sg.Column(inputFormat,pad=(50,0)),sg.Column(topButFormat)],
            
            #Plotting stuff
            #[sg.Text('Current Time:',font=butFont),sg.Text(currTime.strftime("%d %B, %Y - %I:%M:%S %p"),key='Time',font=font)],
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


tab_group = [
    [sg.Tab("Main", wMain, key="Main",element_justification='c',background_color='#EEEEEE')],
    [sg.Tab("Settings", wSet, key="Set",element_justification='c',background_color='#EEEEEE')],
    [sg.Tab("Logging", wLog, key="Log",element_justification='c',background_color='#EEEEEE')],
]

layout = [
    [sg.Text('DATA LOGGER', key='Title', font=titleFont,pad=(0,50))],
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
        window['interval'].update(values['interval'][:-1])
        
    if event == 'temp' and values['temp'] and values['temp'][-1] not in ('0123456789'):
        window['temp'].update(values['temp'][:-1])
        
    if event == 'maxRecords' and values['maxRecords'] and values['maxRecords'][-1] not in ('0123456789'):
        window['maxRecords'].update(values['maxRecords'][:-1])
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  SETTINGS WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
        
        #SEE IF WE CAN SAVE THE FILE
        if file_exists and int_exists and temp_exists and maxR_exists:
            with open(path + '\Settings.txt', 'w') as f:
                f.write('intervalReading = {}'.format(values['interval']))
                f.write('\n')
                f.write('tempWarning = {}'.format(values['temp']))
                f.write('\n')
                f.write('logFile = {}'.format(values['logFile']))
                f.write('\n')
                f.write('maxLogRecords = {}'.format(values['maxRecords']))
                read_settings()
                break
            
        #ERROR MESSAGES
        elif not file_exists:
            sg.popup('This file does not exist!',keep_on_top=True)
        
        elif not int_exists:
            sg.popup('Please input an interval less than 100 minutes',keep_on_top=True)
        
        elif not temp_exists:
            sg.popup('Please input a temperature less than 3000°F',keep_on_top=True)
            
        elif not maxR_exists:
            sg.popup('Please input a maximum number of records greater than 100',keep_on_top=True)
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  LOGGING WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    elif event == 'Live Log': #View the log chart
        window["Log"].select()
        if plotDisplay == False: #If not currently displaying plot, basically only run on startup
            display_graph(logFile)
            
            #~~~Setup initial axes~~~
            right = max(x) #most recent reading
            maxTime = right #global storage of above for Home button
            left = right - zoom #make view to be towards the end of readings
            window['Slide'].update(range=(0,maxTime)) #Update the slider on the bottom of the graph
            window['Slide'].update(value=maxTime) #Set slider to right side of graph
            update_graph_view()
            
    elif event == 'Main Screen': #RETURN FROM LOG
        plotDisplay = False
        window["Main"].select()
        
    # ~~~~~BUTTON CLICK EVENTS~~~~~
    elif event == 'Left' and plotDisplay:
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
        
window.close()




# ~~~~~ References ~~~~~
# https://github.com/PySimpleGUI/PySimpleGUI/issues/3946        Tab groups and hiding tabs