#---Brandon Noble, April 2022---

#Import everything we need
from time import time
import datetime
import PySimpleGUI as sg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import SecondLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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
    

# ~~~~~READ IN SETTING FILE~~~~~
fileLines = []
with open('settings.txt') as f:
    fileLines = f.readlines()

#interval in minutes between reading the data
readInterval = fileLines[0].split(" = ")
readInterval = int(readInterval[1].strip("\n")) #number of minutes

#high temperature warning in degrees F
tempWarn = fileLines[1].split(" = ")
tempWarn = int(tempWarn[1].strip("\n")) #degrees


# ~~~~~VARIABLES~~~~~
currTime = datetime.datetime.fromtimestamp(time()) #used for clock
plotDisplay = False #flag for the plot display


#Axes limits
zoom = 10
left = 0
right = 0
maxTime = 0
stepSize = readInterval #size of the step for the 


# ~~~~~Create the layout of the screen~~~~~
sg.theme('DefaultNoMoreNagging')
font = ("Arial, 16")
butFont = ('Airal', 16, 'bold')
iconFont = ('Calibri',20)
titleFont = ('Arial', 24, 'bold')
sg.theme_text_element_background_color('#EEE')
sg.theme_text_color('#1D2873')
sg.theme_background_color('#EEE')

layout = [  [sg.Text('DATA LOGGER PLOT', font=titleFont)],
            [sg.Text('Charge Number:',size=(15,1), font=font), sg.Input(key='Charge', enable_events=True,size=(15,1), font=font)],
            [sg.Text()],
            [sg.Push(), sg.Button('Record',size=(10,2), font=butFont, button_color='#02AB29'), sg.Push(), sg.Button('Exit',size=(10,2), font=butFont, button_color='#F5273A'), sg.Push()],
            
            #Plotting stuff
            [sg.Button('Plot',size=(5,2)),sg.Text(currTime.strftime("%d %B, %Y - %I:%M:%S %p"),key='Time',font=font)],
            [sg.Push(), sg.Text('TC1: 100.1', font=font), sg.Push(), sg.Text('TC2: 98.7', font=font), sg.Push(), sg.Text('TC3: 99.8', font=font), sg.Push()],
            [sg.Push(), sg.Text('TC4: 105.2', font=font), sg.Push(), sg.Text('TC5: 101.0', font=font), sg.Push(), sg.Text('TC6: 102.6', font=font), sg.Push()],
            [sg.Canvas(key='controls_cv')],
            [sg.Column(
                layout=[
                    [sg.Canvas(key='fig_cv',
                               # it's important that you set this size
                               size=(1500, 600)
                               )]
                ],
                background_color='#DAE0E6',
                pad=(0, 0)
            )],
            [sg.Button('🠔',key="Left",size=(10,1), font=iconFont),sg.Button('⌂',key='Home', size=(10,1), font=iconFont), sg.Button('🠖',key="Right",size=(10,1), font=iconFont)],
            [sg.Button('+',key="ZoomIn",size=(5,1), font=iconFont), sg.Text('   '),sg.Button('-',key="ZoomOut",size=(5,1), font=iconFont)]
            ]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~DISPLAY WINDOW~~~~~
window = sg.Window('Custom Data Logger', layout, no_titlebar = False, keep_on_top = True, location=(600, 200), element_justification='c').Finalize()
window.Maximize()



# ~~~~~MAIN LOOP~~~~~
while True:
    event, values = window.read(timeout=100) #timeout is number of ms the screen refreshes
    
    #Update the clock
    currTime = datetime.datetime.fromtimestamp(time())
    window['Time'].update(currTime.strftime("%d %B, %Y - %I:%M:%S %p"))
    
    if event == 'Exit' or event == sg.WIN_CLOSED: #CLOSE PROGRAM
        break
    elif event == 'Plot':
        # MATPLOTLIB CODE HERE
        plt.figure(1)
        fig = plt.gcf()
        DPI = fig.get_dpi()
        # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
        fig.set_size_inches(1500 / float(DPI), 600 / float(DPI))
        # -------------------------------

        df = pd.read_csv('9timeTest.csv',parse_dates=['Time'], dayfirst=True)
        dates = df['Time'].dt.strftime("%d/%b/%y \n %I:%M:%S %p")
        x = list(range(0,len(dates)))
        
        right = max(x) #most recent reading
        maxTime = right #global storage of above for Home button
        left = right - zoom #make view to be towards the end of readings
        
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
        
        #Format the plot
        plt.xlabel('Time',fontweight='bold')
        plt.ylabel('Temperature',fontweight='bold')
        plt.xticks(x,dates) #adds dates to X axis
        plt.locator_params(axis='x', nbins=1.5*zoom) #number of labels on X axis
        plt.xlim(left,right) #initial limits X
        plt.ylim([0, 700]) #initial limits Y
        plt.grid()
        
        #Adjust the legend to be above the graph
        l4 = plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=6,frameon=False)
        
        #Display the plot
        plotDisplay = True
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas) #idk what half this does but its necessary
        
        
    # ~~~~~BUTTON CLICK EVENTS~~~~~
    elif event == 'Left' and plotDisplay:
        #Move the plot left
        left -= stepSize
        right -= stepSize
        plt.xlim(left,right)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
        
    elif event =='Right' and plotDisplay:
        #Move plot right
        left += stepSize
        right += stepSize
        plt.xlim(left,right) #set limits
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas) #redraw figure
        
    elif event == 'Home' and plotDisplay:
        #Return to home view
        zoom = 10
        left = maxTime - zoom
        right = maxTime
        plt.xlim(left,right) #set limits
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas) #redraw figure
    
    elif event == 'ZoomIn' and plotDisplay:
        #Zoom in graph
        if zoom <= 9:
            zoom = zoom + 1
            left += zoom
            plt.xlim(left,right) #set limits
            draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas) #redraw figure
        
    elif event == 'ZoomOut' and plotDisplay:
        #Zoom out graph
        if zoom >= 2:
            zoom = zoom - 1
            left -= zoom
            plt.xlim(left,right) #set limits
            draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas) #redraw figure
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

window.close() #close the program