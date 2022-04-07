#---Brandon Noble, April 2022---

#Import everything we need
from time import time
import datetime
import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import GeneralCommands as GC

#Current directory path
path = GC.get_path()


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
        window['TC_T'].update(dates[right])
        window['TC1'].update(str(round(df.Temp1[right],1)) + '°F')
        window['TC2'].update(str(round(df.Temp2[right],1)) + '°F')
        window['TC3'].update(str(round(df.Temp3[right],1)) + '°F')
        window['TC4'].update(str(round(df.Temp4[right],1)) + '°F')
        window['TC5'].update(str(round(df.Temp5[right],1)) + '°F')
        window['TC6'].update(str(round(df.Temp6[right],1)) + '°F')
    else:
        window['TC_T'].update('Reading: \nUnavailable')
        window['TC1'].update('000.00' + '°F')
        window['TC2'].update('000.00' + '°F')
        window['TC3'].update('000.00' + '°F')
        window['TC4'].update('000.00' + '°F')
        window['TC5'].update('000.00' + '°F')
        window['TC6'].update('000.00' + '°F')
    
    
# ~~~~~Update graphs when zooming~~~~~
def update_graph_view():
    plt.xlim(left,right) #size of viewport
    #plt.locator_params(axis='x', nbins=50/(right-left))
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
    plt.xlabel('Time',fontweight='bold')
    plt.ylabel('Temperature',fontweight='bold')
    plt.xticks(x,dates) #adds dates to X axis
    plt.locator_params(axis='x', nbins=1.5*zoom) #number of labels on X axis
    plt.gca().spines['right'].set_color('#FF0000') #make rightmost axis red
    plt.gca().spines['right'].set_linewidth(5)
    #plt.xlim(left,right) #initial limits X
    plt.ylim([0,1200]) #initial limits Y
    plt.grid()
    
    #Adjust the legend to be above the graph
    #l4 = plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=6,frameon=False)
    
    #Display the plot
    global plotDisplay
    plotDisplay = True #flag to prevent moving plot before it is shown
    draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas) #idk what half this does but its necessary

    

# ~~~~~READ IN SETTING FILE~~~~~
readInterval = int(GC.get_settings('Interval', path))
tempWarn = int(GC.get_settings('MaxTemp', path))
logFile = GC.get_settings('LogFile', path)


# ~~~~~VARIABLES~~~~~
currTime = datetime.datetime.fromtimestamp(time()) #used for clock
lastRead = currTime
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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~Create the layout of the screen~~~~~
sg.theme('DefaultNoMoreNagging')
font = ('Arial', 16)
butFont = ('Arial', 16, 'bold')
iconFont = ('Calibri',24,'bold')
titleFont = ('Arial', 24, 'bold')
sg.theme_text_element_background_color('#EEE')
sg.theme_text_color('#1D2873')
sg.theme_background_color('#EEE')


#Thermocouple graph reading
tcGraph = [ 
            [sg.Text('Reading at Red Line',font=butFont,justification='c')],
            [sg.Text()],
            [sg.Text('',key='TC_T',font=font,justification='c')],
            [sg.Text('TC1: ',font=butFont,text_color='#FF0000'),sg.Text('1',font=font,key='TC1',text_color='#333')],
            [sg.Text('TC2: ',font=butFont,text_color='#FFAA00'),sg.Text('2',font=font,key='TC2',text_color='#333')],
            [sg.Text('TC3: ',font=butFont,text_color='#365BB0'),sg.Text('3',font=font,key='TC3',text_color='#333')],
            [sg.Text('TC4: ',font=butFont,text_color='#444'),sg.Text('4',font=font,key='TC4',text_color='#333')],
            [sg.Text('TC5: ',font=butFont,text_color='#00B366'),sg.Text('5',font=font,key='TC5',text_color='#333')],
            [sg.Text('TC6: ',font=butFont,text_color='#AA00AA'),sg.Text('6',font=font,key='TC6',text_color='#333')],
            
        ]

#Input boxes at top left
inputFormat = [
            [sg.Text('Charge Number:',size=(15,1), font=font), sg.Input(key='ChargeIn', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Temperature:',size=(15,1), font=font), sg.Input(key='TempIn', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Duration:',size=(15,1), font=font), sg.Input(key='TimeIn', enable_events=True,size=(15,1), font=font)],
    ]

#Submit/exit boxes at top right
topButFormat = [
            [sg.Button('Record',size=(10,2), font=butFont, button_color='#02AB29'), sg.Button('Exit',size=(10,2), font=butFont, button_color='#F5273A')],
    ]

#Zoom buttons
zoomButFormat = [
            [sg.Button('+',key="ZoomIn",size=(5,1), font=iconFont), sg.Button('-',key="ZoomOut",size=(5,1), font=iconFont)]
    ]

#Scroll/homwe buttons
scrollButFormat = [
            [sg.Button('🠔',key="Left",size=(10,1), font=iconFont),sg.Button('⌂',key='Home', size=(10,1), font=iconFont), sg.Button('🠖',key="Right",size=(10,1), font=iconFont)],
    ]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~MAIN LAYOUT OF THE WHOLE SCREEN~~~~~
layout = [  [sg.Text('DATA LOGGER PLOT', font=titleFont)],
            [sg.Column(inputFormat,pad=(50,0)),sg.Column(topButFormat)],
            
            #Plotting stuff
            [sg.Text('Current Time:',font=butFont),sg.Text(currTime.strftime("%d %B, %Y - %I:%M:%S %p"),key='Time',font=font)],
            [sg.Canvas(key='controls_cv')], #idk why this has to be here
            
            #WHERE THE MAGIC HAPPENS
            [sg.Column(
                layout=[
                            #This is the graph
                            [sg.Canvas(key='fig_cv',size=graphSize)], 
                            
                            #This is the slider at the bottom of the graph
                            [sg.Slider(key='Slide',range=(0,maxTime),size=(30,30),enable_events=True,orientation='h',expand_x=True,pad=(100,0),disable_number_display=True,trough_color='#ABC',background_color='#1D2973')],
                        ], #end layout
                    background_color='#8591AB',pad=(0, 10)), #graph/slider column settings
                sg.Column(tcGraph,element_justification='c',pad=(50,0))], #end of column
            
            [sg.Column(scrollButFormat,pad=(20,5)),sg.VerticalSeparator(pad=None),sg.Column(zoomButFormat,pad=(20,5))]
            ]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~DISPLAY WINDOW~~~~~
window = sg.Window('Custom Data Logger', layout, no_titlebar = False, keep_on_top = True, element_justification='c').Finalize()
window.Maximize() #show fullscreen

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
readInterval = (readInterval-7)/60+10 #read every 7s

# ~~~~~MAIN LOOP~~~~~
while True:
    event, values = window.read(timeout=50) #timeout is number of ms the screen refreshes
    
    #Update the clock
    currTime = datetime.datetime.fromtimestamp(time())
    window['Time'].update(currTime.strftime("%d %B, %Y - %I:%M:%S %p"))


    # ~~~~~INITIAL PLOT~~~~~
    if plotDisplay == False: #If not currently displaying plot, basically only run on startup
        display_graph(logFile)
        
        #~~~Setup initial axes~~~
        right = max(x) #most recent reading
        maxTime = right #global storage of above for Home button
        left = right - zoom #make view to be towards the end of readings
        window['Slide'].update(range=(0,maxTime)) #Update the slider on the bottom of the graph
        window['Slide'].update(value=maxTime) #Set slider to right side of graph
        update_graph_view()
        
    # ~~~~~Check if it is time to update the graph readings~~~~~
    if currTime - datetime.timedelta(seconds=readInterval) > lastRead:
        lastRead = currTime
        plt.clf()
        display_graph(logFile)
        update_graph_view()
        #update_tc_graph()
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    # ~~~~~BUTTON EVENTS~~~~~
    if event == 'Exit' or event == sg.WIN_CLOSED: #CLOSE PROGRAM
        break        
        
    # ~~~~~BUTTON CLICK EVENTS~~~~~
    elif event == 'Left' and plotDisplay:
        #Move the plot left
        left -= stepSize
        right -= stepSize
        window['Slide'].update(value=right) #adjsut slider
        update_graph_view()
        
    elif event =='Right' and plotDisplay:
        #Move plot right
        left += stepSize
        right += stepSize
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
        if zoom <= maxZoom:
            zoom = zoom + 1
            left = right - zoom
            update_graph_view()
        
    elif event == 'ZoomIn' and plotDisplay:
        #Zoom in graph
        if zoom >= minZoom:
            zoom = zoom - 1
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

window.close() #close the program
