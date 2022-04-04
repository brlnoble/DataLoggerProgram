#---Brandon Noble, April 2022---

#Import everything we need
from time import time
import datetime
import PySimpleGUI as sg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
left = 0
right = 9
stepSize = .5*readInterval #size of the step for the 


# ~~~~~Create the layout of the screen~~~~~
sg.theme('DefaultNoMoreNagging')
font = ("Arial, 16")
butFont = ('Airal', 16, 'bold')
iconFont = ('Calibri',20)
titleFont = ('Arial', 20, 'bold')
sg.theme_text_element_background_color('#EEE')
sg.theme_text_color('#333')
sg.theme_background_color('#EEE')

layout = [  [sg.Text('DATA LOGGER', font=titleFont)],
            [sg.Text('Charge Number:',size=(15,1), font=font), sg.Input(key='-C-', enable_events=True,size=(15,1), font=font)],
            [sg.Text()],
            [sg.Push(), sg.Button('Record',size=(10,2), font=butFont), sg.Push(), sg.Button('Exit',size=(10,2), font=butFont, button_color='Red'), sg.Push()],
            
            #Plotting stuff
            [sg.Button('Plot',size=(5,2)),sg.Text(currTime.strftime("%d %B, %Y - %I:%M:%S %p"),key='Time',font=font)],
            [sg.Canvas(key='controls_cv')],
            [sg.Column(
                layout=[
                    [sg.Canvas(key='fig_cv',
                               # it's important that you set this size
                               size=(400 * 2, 400)
                               )]
                ],
                background_color='#DAE0E6',
                pad=(0, 0)
            )],
            [sg.Button('🠔',key="Left",size=(10,1), font=iconFont),sg.Button('⌂',key='Home', size=(10,1), font=iconFont), sg.Button('🠖',key="Right",size=(10,1), font=iconFont)]
            ]


# ~~~~~DISPLAY WINDOW~~~~~
window = sg.Window('Custom Data Logger', layout, no_titlebar = False, keep_on_top = False, location=(600, 200), element_justification='c')



# ~~~~~MAIN LOOP~~~~~
while True:
    event, values = window.read(timeout=100) #timeout is number of ms the screen refreshes
    
    #Update the clock
    currTime = datetime.datetime.fromtimestamp(time())
    window['Time'].update(currTime.strftime("%d %B, %Y - %I:%M:%S %p"))
    
    if event == 'Exit': #CLOSE PROGRAM
        break
    elif event == 'Plot':
        # MATPLOTLIB CODE HERE
        plt.figure(1)
        fig = plt.gcf()
        DPI = fig.get_dpi()
        # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
        fig.set_size_inches(400 * 2 / float(DPI), 400 / float(DPI))
        # -------------------------------

        df = pd.read_csv('9timeTest.csv')
        x = df.Time
        
        #thermocouple 1
        y = df.Temp1
        plt.plot(x,y,linewidth=2,marker='o',label='TC1',color='r') 
        #thermocouple 2
        y = df.Temp2
        plt.plot(x,y,linewidth=2,marker='o',label='TC2',color='c')
        #thermocouple 3
        y = df.Temp3
        plt.plot(x,y,linewidth=2,marker='o',label='TC3',color='g')
        #thermocouple 4
        y = df.Temp4
        plt.plot(x,y,linewidth=2,marker='o',label='TC4',color='purple')
        #thermocouple 5
        y = df.Temp5
        plt.plot(x,y,linewidth=2,marker='o',label='TC5',color='y')
        #thermocouple 6
        y = df.Temp6
        plt.plot(x,y,linewidth=2,marker='o',label='TC6',color='grey') 
        
        plt.xlabel('Time')
        plt.ylabel('Temperature')
        plt.xlim([left,right]) #initial limits X
        plt.ylim([0, 700]) #initial limits Y
        plt.grid()
        l4 = plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                mode="expand", borderaxespad=0, ncol=6,frameon=False)
        
        plotDisplay = True

        #Display the plot
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
        
        
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
        left = 0
        right = 9
        plt.xlim(left,right) #set limits
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas) #redraw figure
    
window.close()