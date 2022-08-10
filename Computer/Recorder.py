import PySimpleGUI as sg
from tkinter import ttk
from time import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sys import exc_info

import RecorderCommands as RC #Custom file



# ~~~~~Close splash screen~~~~~
try:
    import pyi_splash #cannot from Spyder, only when compiled to EXE
    pyi_splash.close() #cannot run from Spyder, only when compiled to EXE
except:
    pass


#Current directory path
path = RC.get_path()
logFile = path + 'Program/AllTempLogs.csv'

# ~~~~~MAKE SURE THE SETTINGS FILE EXISTS~~~~~
if not RC.verify_settings(path):
    sg.popup('Settings file does not exist.\n\nA file with default values has been generated.',font=('Arial',20),keep_on_top=True,modal=True) #inform user it was not found
    

#Imbed image as Base64 string so the EXE can be a standalone file
furnacePic = b"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"
fireIcon = b'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAAAXNSR0IArs4c6QAAAuBJREFUSEvF109IFFEcB/Dv7Mzqrn/XDQxqjSDo0EoUUUG0FXWxIC0KzC5FdIgudcoyo6yQ8lAX+2dmgaAm2EWNhCByIdBC8+BB18WoVPQws390c9eZeTGz7ejs7Mju6Oa7vffm/T7vz2923lJYo0LpuPQqz0eIj6eC3W53n9Pp3LPKqBxueHi43+Vy7Y3FVuB0ojFsKa7ALMuSdKw0PqbdbpfNGEyzLMunBBOCjM+diBw8DlB6qaKNaLfbGQCCIdjy6S2sH14D4zPg2gdSmq9hOKexCmZPFBP9BP7nPemHLe53sHY1KJBAbAjUtaUZJgQF14+qEHGOgb++K72wpbcD1u6XamR8Glz7oLqNkGWTLeUztt05DerPrBrxTiFY0wjeuVtup3+OIbv+FgJ1rbq7kDJcUFmiDeadktvCx87KL2Zmd4tc97X0gWRYEuIpwRQfge1mqS4c3xG6XIPw4RMrgEURMJlgCnLIv1+RNBwuKUfoYpVxOP/heQSuPgUVCiL/wTltoN8TQNikaQ9dqIxuf4KS1FbbqstALYQxd+YastvqlDBkEwth/xiYWseSH79FxfemF/SPEfDF2g9dcvDtU6Dm51TzJht8EA6Nym3MvSLtmigKYuFGUAEOvuYvmv6k4NyGSjDeIdVgvqJf+bQwTYXARCZgEYF59Zbz23YheLfJGMz8GkFu/ZXFwdYI+JPflToz8+87QxPghXr1wdpm8Fu3G4OlUbbqUlALETkAcXAQDnjUcKzWWQhMZkafM2fA1/rVeHJJI03ctJLRpIiD4NKBP64DvFky5n/SDXG9Y2WwNNrsGURO4w2AFsGXf0u84lcOgKcwW/0MCzv2JUSlxqSSa+lo6V3Oe3wJ2DwEsXgymtXSGUtlMA+iZwsCjzpAcm26qCE4Fo0Kh2Ae7QFtfQ+TXwA/fwSRnWUgWTnLgrHO+BVjrS57WLPrrbQV6cR1L/RxB/R//8IklR2r9NBfLy1iLgM4NkgAAAAASUVORK5CYII='


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
    
# ~~~~~Alert across top~~~~~
def update_alert(msg):
    if msg != '':
        #Alert the user of an issue
        window['ErrorAlert'].update(msg)
        window['ErrorAlert'].update(background_color='#F5273A')
        
    else:
        #Hide alert
        window['ErrorAlert'].update('')
        window['ErrorAlert'].update(background_color='#EEE')
        


# ~~~~~UPDATE THERMOCOUPLE READINGS~~~~~
def update_tc_nums():
    df = pd.read_csv(logFile)
    
    window['lastRead'].update(value=df['Time'].values[-1]) #last time the file was written to
    
    for tc in range(1,7):
        window['TC' + str(tc)].update(str(round(df['Temp' + str(tc)].values[-1],1)) + '°F')
        
        #check high temperature limit
        if round(df['Temp' + str(tc)].values[-1],1) < int(settings['tempWarn']):
            window['TC' + str(tc)].update(background_color='#EEE')
                          
        else: #!!!Temperature over limit!!!
            window['TC' + str(tc)].update(background_color='#F5273A')
            update_alert('THERMOCOUPLE TC{} OVER LIMIT'.format(tc))
            
            
    
# ~~~~~Update settings window~~~~~
def update_settings_display():
    event, values = window.read(timeout=100)
    window['interval'].update(value = settings['interval'])
    window['temp'].update(value = settings['tempWarn'])
    window['maxRecords'].update(value = settings['maxRecords'])
    window['github'].update(value = settings['github'])
    
    if bool(settings['enableEmail']) == True:
        window['eBut'].update('Disable Emails')
    else:
        window['eBut'].update('Enable Emails')
        
    #Email listed as: one@email.com; two@email.com
    emailToStr = ''
    for i in range(0,len(settings['emailTo'])):
        emailToStr += str(settings['emailTo'][i]) +'; '
    window['email'].update(value = emailToStr[:-2])


# ~~~~~Include the Matplotlib figure in the canvas~~~~~
def draw_figure_w_toolbar(canvas, fig):
    #If already displaying, delete current graph
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    

# ~~~~~Updates thermocouples on right of graph~~~~~
def update_tc_graph():
    val = right - dataSlide[0]
    if len(dates) - 1 >= val and val > 0:
        window['TC_TL'].update(dates[val])
        window['TC1L'].update(str(round(df.Temp1[val],1)).zfill(5) + '°F')
        window['TC2L'].update(str(round(df.Temp2[val],1)).zfill(5) + '°F')
        window['TC3L'].update(str(round(df.Temp3[val],1)).zfill(5) + '°F')
        window['TC4L'].update(str(round(df.Temp4[val],1)).zfill(5) + '°F')
        window['TC6L'].update(str(round(df.Temp6[val],1)).zfill(5) + '°F')
    else:
        window['TC_TL'].update('Reading: \nUnavailable')
        window['TC1L'].update('000.0' + '°F')
        window['TC2L'].update('000.0' + '°F')
        window['TC3L'].update('000.0' + '°F')
        window['TC4L'].update('000.0' + '°F')
        window['TC6L'].update('000.0' + '°F')
    
    
# ~~~~~Update graphs when zooming~~~~~
def update_graph_view():
    plt.xlim(left,right) #size of viewport
    plt.locator_params(axis='x', nbins=(maxTime/(right-left))*10) #makes sure there are only 10 x-axis ticks at a time
    
    #Update data marker
    window['DataSlide'].update(range=(zoom,0))
    data_select() 

    
# ~~~~~Change red data marker~~~~~
def data_select():
    global lineSelect
    lineSelect.set_xdata(right-dataSlide[0])
    #Update axis without redrawing entire graph
    fig.canvas.draw()
    update_tc_graph()
    
    
# ~~~~~Update recording status~~~~~
def update_record(change):
    
    record = settings['chargeRecord']
    
    if record != 'N':    
        #Alert the user it is recording
        window['RecordAlert'].update('Currently Recording: ' + record[3:])
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
        
        #Update the button to start recording
        window['cRecord'].update('Record')
        window['cRecord'].update(button_color='#02AB29')
        
        #Enable changing the input boxes
        window['ChargeIn'].update(disabled=False)
        window['TempIn'].update(disabled=False)
        window['TimeIn'].update(disabled=False)
        
    if change:
        #Update settings file
        RC.update_settings(path,"chargeRecord",record)
        
        
# ~~~~~Record a charge~~~~~
def record_charge(charge):
    global chargeEnd
    chargeEnd = currTime + datetime.timedelta(hours=(int(charge[:2])+2)) #time to end the charge at, 2 hour extra safety
    RC.update_settings(path, "chargeRecord",charge)
    settings['chargeRecord'] = charge
    update_record(True)
    
    
# ~~~~~Save an image~~~~~
def img_save(titleText):
    if not RC.does_this_exist(path,"Figures\\"):
        RC.make_folder(path + "Figures\\")
        
    imgName = path + "Figures/" + currTime.strftime("%d-%B-%y - %I-%M-%S %p") + ".png"
    
    plt.legend(bbox_to_anchor=(0,1,1,0), loc="lower left", mode="expand", borderaxespad=0, ncol=6)
    lineSelect.set_visible(False)
    plt.title(titleText,fontsize=30,pad=30)
    plt.savefig(imgName, bbox_inches='tight')
    plt.legend('',frameon=False)
    lineSelect.set_visible(True)
    plt.title('')
    popWindow("Image saved in Figures folder.\n" + currTime.strftime("%d-%B-%y - %I-%M-%S %p") + ".png")
    RC.open_folder(imgName)
        

# ~~~~~MATPLOTLIB DISPLAY ALL THE GRAPH DATA~~~~~
def display_graph(fileName):
    # MATPLOTLIB CODE HERE
    global plt
    plt.clf()
    plt.figure(1)
    global fig
    fig = plt.gcf()
    DPI = fig.get_dpi()
    # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
    fig.set_size_inches(graphSize[0] / float(DPI), graphSize[1] / float(DPI)) #THESE MUST MATCH THE SIZE OF THE ABOVE CANVAS FOR THE GRAPH
    # -------------------------------

    global df
    df = pd.read_csv(fileName,parse_dates=['Time'], dayfirst=True)
    global dates
    dates = df['Time'].dt.strftime("%d-%b-%y \n %I:%M:%S %p")
    global x
    x = list(range(0,len(dates)))
        
    #thermocouple 1
    y = df.Temp1
    plt.plot(x,y,linewidth=2,marker='o',label='TC1',color='#FF0000')
    maxVal = max(y)
    #thermocouple 2
    y = df.Temp2
    plt.plot(x,y,linewidth=2,marker='o',label='TC2',color='#FFAA00') 
    maxVal = maxVal if maxVal > max(y) else max(y)
    #thermocouple 3
    y = df.Temp3
    plt.plot(x,y,linewidth=2,marker='o',label='TC3',color='#365BB0')
    maxVal = maxVal if maxVal > max(y) else max(y)
    #thermocouple 4
    y = df.Temp4
    plt.plot(x,y,linewidth=2,marker='o',label='TC4',color='#00B366')
    maxVal = maxVal if maxVal > max(y) else max(y)
    #thermocouple 6
    y = df.Temp6
    plt.plot(x,y,linewidth=2,marker='o',label='TC6',color='#AA00AA')
    maxVal = maxVal if maxVal > max(y) else max(y)
    
    update_tc_graph() #adds the readings on the right
    
    #Format the plot
    plt.rc('axes', labelsize=14)
    plt.xlabel('Time',fontweight='bold')
    plt.ylabel('Temperature',fontweight='bold')
    plt.xticks(x,dates) #adds dates to X axis
    plt.locator_params(axis='x', nbins=1.5*zoom) #number of labels on X axis
    plt.tight_layout(pad=2) #Removes whitespace from sides of plot

    
    #plt.xlim(left,right) #initial limits X
    global lineSelect
    lineSelect = plt.axvline(x=max(x)-1,linestyle=':',linewidth=3,color='black')
    
    #Check y limits
    ylimit = 800 if 800 > maxVal else int(-1 * maxVal // 100 * -1) * 100
    plt.ylim(0,ylimit) #initial limits Y
    plt.grid(visible=True)
    
    #Display the plot
    global plotDisplay
    plotDisplay = True #flag to prevent moving plot before it is shown
    draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig) #idk what half this does but its necessary
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   

#Window theme
sg.theme('DefaultNoMoreNagging')
font = ('Arial', 16)
butFont = ('Arial', 16, 'bold')
iconFont = ('Segoe UI Symbol',20,'bold')
tcFont = ('Courier New',16,'bold')
titleFont = ('Arial', 26, 'bold')
sg.theme_text_element_background_color(color = '#EEE')
sg.theme_text_color('#1D2873')
sg.theme_background_color('#EEE')

# ~~~~~VARIABLES~~~~~
settings = RC.get_settings("all", path)
currTime = datetime.datetime.fromtimestamp(time()) #used for clock
lastRead = currTime - datetime.timedelta(seconds=(int(settings['interval'])*60))
closeTime = currTime + datetime.timedelta(seconds=20*60*60)
emailTry = bool(settings['enableEmail']) #if we should be sending emails

lastEdit = RC.get_mtime(path,"Program/Settings.json") #Last time settings were modified
lastCheck = currTime #last time settings were checked

plotDisplay = False #flag for the plot display
chargeDisplay = False #flag for the charge view
activeScreen  = 'Main' #helps speed up the main loop


#Axes limits
zoom = 30
maxZoom = 300
minZoom = 5
left = 0
right = 0
maxTime = 0
stepSize = 1 #moves one data point, adjusts for the seconds to minutes conversion
graphSize = (1200, 550)
dataSlide = [1,zoom-1]



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
                        [sg.Text('Reading as of: ',font=butFont),sg.Text('',key='lastRead',font=font,pad=(0,30))],
            
            [sg.Push(),sg.Push(), sg.Text('TC6:',font=butFont),sg.Text('000.0',key='TC6', font=tcFont), 
             sg.Push(), sg.Text('TC5:',font=butFont),sg.Text('000.0',key='TC5', font=tcFont,text_color='#EEE'), 
             sg.Push(), sg.Text('TC4:',font=butFont),sg.Text('000.0',key='TC4', font=tcFont),sg.Push(),sg.Push()],
            
            [sg.Image(furnacePic,pad=(0,0))],
            
            [sg.Push(),sg.Push(), sg.Text('TC1:',font=butFont),sg.Text('000.0',key='TC1', font=tcFont), 
             sg.Push(), sg.Text('TC2:',font=butFont),sg.Text('000.0',key='TC2', font=tcFont), 
             sg.Push(), sg.Text('TC3:',font=butFont),sg.Text('000.0',key='TC3', font=tcFont),sg.Push(),sg.Push()],
            
            [sg.Text('',font=font)], #spacing
            [sg.Button('Exit Program',key='Exit',size=(20,3), font=butFont, button_color='#F5273A')],
            [sg.Push(),sg.Push(),sg.Button('Error Log',font=butFont,button_color='#333')], #Button for opening up error log
        ]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  SETTINGS WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wSet = [  
            [sg.Text('SETTINGS', font=titleFont,pad=(0,50))],
            
            [sg.Column([
                [sg.Text('Interval (min):',size=(15,1), font=font,justification='r'), sg.Input(key='interval', enable_events=True,size=(20,1), font=font)],
                [sg.Text('Temp Warning (F):',size=(15,1), font=font,justification='r'), sg.Input(key='temp', enable_events=True,size=(20,1), font=font)],
                [sg.Text('_'*56,font=font,pad=(0,20),text_color='#EEE')], #spacing
            ])],
            
            
            [sg.Text('Please do not change the following without consulting the manual.',font=butFont,pad=(0,10),text_color='#F5273A')],
            [sg.Column([
                [sg.Text('Alert Emails:',size=(15,1), font=font,justification='r'), sg.Multiline(key='email', enable_events=True,size=(25,3), font=font)],
                [sg.Text('Enable Alerts:',font=font,size=(15,1),justification='r'), sg.Button('Enable Emails',key='eBut',font=('Arial',10),size=(12,1),enable_events=True)],
                
                [sg.Text('Max Log Records:',size=(15,1), font=font,justification='r'), sg.Input(key='maxRecords', enable_events=True,size=(15,1), font=font)],
                [sg.Text('Github Key:',size=(15,1), font=font,justification='r'), sg.Input(key='github', enable_events=True,size=(41,1), font=font)],
            ])],
            
            [sg.Text('',key='tips',pad=(0,20))],
            [sg.Push(), sg.Button('Save Changes',key='Submit',size=(15,2), font=butFont, button_color='#02AB29'), sg.Push(), sg.Button('Cancel',size=(15,2), font=butFont, button_color='#F5273A'), sg.Push()],
        ]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  LOGGING WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Thermocouple graph reading
tcGraph = [ 
            [sg.Text('Reading at Black Line',font=butFont,justification='c')],
            [sg.Text()],
            [sg.Text('',key='TC_TL',font=font,justification='c')],
            [sg.Text('TC1: ',font=butFont,text_color='#FF0000'),sg.Text('1',font=tcFont,key='TC1L',text_color='#333')],
            [sg.Text('TC2: ',font=butFont,text_color='#FFAA00'),sg.Text('2',font=tcFont,key='TC2L',text_color='#333')],
            [sg.Text('TC3: ',font=butFont,text_color='#365BB0'),sg.Text('3',font=tcFont,key='TC3L',text_color='#333')],
            [sg.Text('TC4: ',font=butFont,text_color='#00B366'),sg.Text('4',font=tcFont,key='TC4L',text_color='#333')],
            [sg.Text('TC6: ',font=butFont,text_color='#AA00AA'),sg.Text('6',font=tcFont,key='TC6L',text_color='#333')],
            [sg.Text()],
            [sg.Button('Save Graph',key='saveBut',font=butFont,button_color="#F57627",size=(10,2))]
            
        ]

#Input boxes at top left
inputFormat = [
            [sg.Text('Charge Number:',size=(15,1), font=font,justification='r'), sg.Input(key='ChargeIn', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Temperature:',size=(15,1), font=font,justification='r'), sg.Input(key='TempIn', enable_events=True,size=(15,1), font=font)],
            [sg.Text('Duration:',size=(15,1), font=font,justification='r'), sg.Input(key='TimeIn', enable_events=True,size=(15,1), font=font)],
    ]

#Zoom buttons
zoomButFormat = [
            [sg.Button('➕',key="ZoomIn",size=(5,1), font=iconFont), sg.Button('➖',key="ZoomOut",size=(5,1), font=iconFont)]
    ]

#Scroll/homwe buttons
scrollButFormat = [
            [sg.Button('◀',key="Left",size=(10,1), font=iconFont),sg.Button('🏠',key='Home', size=(10,1), font=iconFont), sg.Button('▶',key="Right",size=(10,1), font=iconFont)],
    ]


# ~~~~~MAIN LAYOUT OF THE WHOLE SCREEN~~~~~
wLog = [  
            [sg.Column([
                [sg.Column(inputFormat,pad=(50,0)),sg.Column([[sg.Button('Record',key='cRecord',size=(10,2), font=butFont, button_color='#02AB29')]])],
                ],key='logInput')],
                       
            #WHERE THE MAGIC HAPPENS
            [sg.Column([
                [sg.Column(
                layout=[
                            #This is the slider at the top of the graph, moves the data selector
                            [sg.Slider(key='DataSlide',range=(zoom-1,1),default_value=1,size=(0,30),enable_events=True,orientation='h',expand_x=True,pad=((55,10),(5,0)),disable_number_display=True,trough_color='#EEE',background_color='#000')],
                            #This is the graph
                            [sg.Canvas(key='fig_cv',size=graphSize)], 
                            
                            #This is the slider at the bottom of the graph, moves the graph view
                            [sg.Slider(key='Slide',range=(zoom,maxTime),size=(0,30),enable_events=True,orientation='h',expand_x=True,pad=((55,10),(5,5)),disable_number_display=True,trough_color='#EEE',background_color='#1D2873')],
                            [sg.Column([
                                [sg.Column(scrollButFormat,pad=(20,5),background_color='#FFF'),sg.Text('',pad=(50,0),background_color='#FFF'),sg.Column(zoomButFormat,pad=(20,5),background_color='#FFF')]],justification='c',background_color='#FFF')],
                        ], #end layout
                
                    background_color='#FFF',pad=(10,10)), #graph/slider column settings
                ]],background_color='#1D2873'),
            sg.Column([
                [sg.Text('',font=font,key='cDesc',justification='c')],
                [sg.Text()],
                [sg.Column(tcGraph,element_justification='c',pad=(50,0))]
                ],element_justification='c')
            ], #end of column                
        ]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  CHARGE WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

chargeSearch = [
                [sg.Text('Search Charges',font=butFont,size=(24,2),justification='c')],
                [sg.Text('Charge:',font=font,size=(12,1),text_color="#333",justification='r'),sg.Input(key='charge_search',font=font,size=(12,2))],
                [sg.Text('Temperature:',font=font,size=(12,1),text_color="#333",justification='r'),sg.Input(key='temp_search',font=font,size=(12,2))],
                [sg.Text('Date:',font=font,size=(12,4),text_color="#333",justification='r'),
                        sg.Column([
                            [sg.Input(key='date_search',font=font,size=(12,2))],
                            [sg.Text("day/month/year\nOR\nmonth/year",font=('Arial',10),justification='c',size=(12,4),text_color="#777")],
                            ],element_justification='c')]
            ]

chargeSearchButtons = [
                [sg.Button('Search',key="charge_filter",font=font,size=(12,1),button_color="#F57627",pad=(0,10))],
                [sg.Button('Clear Search',key="charge_filter_clear",font=font,size=(12,1),pad=(0,10))], 
            ]

chargeSearchAll = [
                    [sg.Frame("",[
                        [sg.Frame("",[
                            [sg.Column(chargeSearch,element_justification='c')],
                            [sg.Column(chargeSearchButtons,element_justification='c')]
                        ],element_justification='c',relief='flat',pad=1)],
                    ],relief='flat',background_color='#777')]
            ]

wCharge = [
            [sg.Text('Please select a charge from the list below.\n',font=font,text_color='#333')],
            [sg.Text('')],
            [sg.Column(chargeSearchAll),sg.Text('',font=font,size=(5,1)),sg.Column([
                [sg.Text('Charge -- Temp -- Date',font=tcFont)], #format of information
                [sg.Listbox(values='',size=(27,20),font=('Courier New',16,'bold'),key='cList')] #listbox
                ],element_justification='c')
            ],
            [sg.Text()],
            [sg.Button('View',font=butFont,size=(16,2),button_color='#02AB29')]
        ]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  ERRLOG WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Open up the error log in a new window
def errWindow():
    errLayout = [
            [sg.VPush()],
            [sg.Text('Error Logs',font=titleFont)],
            [sg.Listbox(values=RC.get_err(path),size=(120,30),font=font)],
            [sg.Button('Close',key='errCancel',font=butFont,button_color='#F5273A',size=(10,2))],
            [sg.VPush()],
        ]
    return sg.Window("Data Logger - Error Log", errLayout, no_titlebar = False, keep_on_top=True, element_justification='c',modal=True,use_custom_titlebar=True,titlebar_icon=fireIcon,titlebar_font=font,finalize=True)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  CHARGE ERROR WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Open up the error log in a new window
def chargeWindow(cNum,oldNum):
    chargeLayout = [
            [sg.VPush()],
            [sg.Text('Charge Number Already in Use',font=titleFont)],
            [sg.Text('The charge you input is already in use. Please select an option as described below.',font=font)],
            [sg.Text(cNum + ' was recorded on '+oldNum[-9:],key='chargeINF',font=('Arial',18,'bold'),pad=(0,20),text_color='#F5273A')],
            [sg.Text('Overwrite: ',font=('Arial',16,'bold'),text_color='#22B366',size=(15,1)),sg.Text('Delete the old file, and start recording in a new file with number ' + cNum +'.\nUse this option if you messed up the previous recording.',font=font,pad=(0,10),size=(70,2))],
            [sg.Text('Redo Charge: ',font=('Arial',16,'bold'),text_color='#AA00AA',size=(15,1)),sg.Text('Keep the old file, and start recording in a new file with number ' + cNum + '.\nUse this option if the furnace failed and you are redoing the charge.',font=font,pad=(0,10),size=(70,2))],
            [sg.Text('',pad=(0,30))],
            [sg.Button('Overwrite',key='chargeOW',font=butFont,button_color='#00B366',size=(12,2)),
             sg.Button('Redo Charge',key='chargeRU',font=butFont,button_color='#AA00AA',size=(12,2)),
             sg.Button('Cancel',key='chargeCancel',font=butFont,button_color='#F5273A',size=(15,2),pad=((50,0),(0,0)))],
            [sg.VPush()]
        ]
    return sg.Window("Data Logger - Charge in Use", chargeLayout, no_titlebar = False, keep_on_top=True, element_justification='c',modal=True,use_custom_titlebar=True,titlebar_icon=fireIcon,titlebar_font=font,finalize=True)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  POPUP WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#For popup alerts
def popWindow(msg):
    popLayout = [
            [sg.Text('Alert',font=titleFont)],
            [sg.Text(msg,font=font,pad=(10,10))]
        ]
    return sg.Window("Data Logger - Alert", popLayout, no_titlebar = False, keep_on_top=True, element_justification='c',modal=True,finalize=True)

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
    [sg.Text(key='ErrorAlert',font=butFont,background_color='#EEEEEE',text_color='#FFF',expand_x=True,justification='c',pad=(0,0))],
    [sg.Text('DATA LOGGER', key='Title', font=titleFont,pad=(0,20)),sg.Button('Main Screen',size=(10,2), font=butFont, button_color='#F5273A',visible=False)],
    [sg.Text(key='Time',font=butFont)],
    [sg.TabGroup(tab_group, border_width=0, pad=(0, 0), key='TABGROUP')],
]

window, errWin, chargeWin = sg.Window("Data Logger", layout, no_titlebar = False, keep_on_top=True, location=(0, 0), element_justification='c',use_custom_titlebar=True,titlebar_icon=fireIcon,titlebar_font=font).Finalize(), None, None
window.Maximize()
window.set_icon(pngbase64=fireIcon)

style = ttk.Style()
style.layout('TNotebook.Tab', []) # Hide tab bar

#Update the charge if it is currently recording
update_record(False)
if settings['chargeRecord'] not in ['Y','N']:
    window['ChargeIn'].update(settings['chargeRecord'][3:8])
    window['TempIn'].update(settings['chargeRecord'][12:16])
    window['TimeIn'].update(settings['chargeRecord'][0:2])


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  MAIN LOOP  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


while True:

    try:
        windows,event, values = sg.read_all_windows(timeout=100)
        #See if window should be closed
        if event in (sg.WINDOW_CLOSED, "Exit"):
            if windows == window:
                break #Main window
            else:
                windows.close() #Other windows
        
        #Update the clock
        currTime = datetime.datetime.fromtimestamp(time())
        window['Time'].update(currTime.strftime("%d %B, %Y - %I:%M:%S %p"))
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Check if settings have changed every 10s
        if currTime - datetime.timedelta(seconds=10) > lastCheck:
            if RC.get_mtime(path, 'Program/Settings.json') > lastEdit:
                settings = RC.get_settings("all", path)
                update_record(False)
                lastEdit = RC.get_mtime(path, 'Program/Settings.json')
                lastCheck = currTime
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Check if it is time to update the TC readings
        if currTime - datetime.timedelta(seconds=(60)) > lastRead:
            lastRead = currTime
            update_tc_nums()
            
            #only update graph if we are viewing the live plot and not charges
            if plotDisplay and not chargeDisplay:
                #adjust view if looking at most recent point
                df = pd.read_csv(logFile,parse_dates=['Time'], dayfirst=True)
                if len(df.Temp1) -1 > maxTime:
                    if right == maxTime:
                        right += 1
                        left -= 1
                    display_graph(logFile)
                    update_graph_view()
                    
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  MISC WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if event == 'Main Screen': #RETURN TO MAIN SCREEN
            chargeDisplay = False
            window['Main Screen'].update(visible=False)
            window['Title'].update(visible=True)
            window["Main"].select()
            activeScreen = 'Main'
            
        if event == 'Error Log': #Open error log
            errWin = errWindow()
            errWin.Maximize()
            
        if event == 'errCancel':
            errWin.close()            
                
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
            
            display_graph(logFile)
            
            #~~~Setup initial axes~~~
            zoom = 30
            right = max(x) #most recent reading
            maxTime = right #global storage of above for Home button
            left = right - zoom #make view to be towards the end of readings
            window['Slide'].update(range=(zoom,maxTime)) #Update the slider on the bottom of the graph
            window['Slide'].update(value=maxTime) #Set slider to right side of graph
            update_graph_view()
                
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~BUTTON CLICK EVENTS~~~~~
        elif activeScreen == 'Log':
            
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
                zoom = 30
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
                
            elif event == 'DataSlide' and plotDisplay:
                dataSlide[0] = values['DataSlide']
                data_select()
            
            elif event == 'saveBut':
                #If viewing a charge
                if window['cDesc'].get() != '':
                    img_save(str(window['cDesc'].get()).split('\n')[1])
                #If viewing live log    
                else:
                    img_save('From ' + df.Time[left].strftime('%d-%b-%y %I:%M:%S %p') + ' to ' + df.Time[right].strftime('%d-%b-%y %I:%M:%S %p'))
         
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~RECORDING A CHARGE~~~~~
            elif event == 'ChargeIn' and values['ChargeIn'] and (values['ChargeIn'][-1] not in ('0123456789') or len(values['ChargeIn']) > 5):
                window['ChargeIn'].update(values['ChargeIn'][:-1])
                
            elif event == 'TempIn' and values['TempIn'] and (values['TempIn'][-1] not in ('0123456789') or len(values['TempIn']) > 4):
                window['TempIn'].update(values['TempIn'][:-1])
                
            elif event == 'TimeIn' and values['TimeIn'] and (values['TimeIn'][-1] not in ('0123456789') or len(values['TimeIn']) >4):
                window['TimeIn'].update(values['TimeIn'][:-1])
            
            
            #Recording a new charge
            elif event == 'cRecord' and settings['chargeRecord'] == 'N':
                #Verify inputs
                tCheck = False
                dCheck = False
                cCheck = [False,'']
                
                if values['ChargeIn'] and len(values['ChargeIn']) == 5:
                    cCheck = RC.check_charge(path,values['ChargeIn'])
                        
                    if not cCheck[0]: #CHARGE IS ALREADY IN USE
                        chargeWin = chargeWindow(values['ChargeIn'],cCheck[1])
                        chargeWin.Maximize()
                        
                        
                if values['TempIn'] and int(values['TempIn']) > 0:
                    tCheck = True
                if values['TimeIn'] and 50 > int(values['TimeIn']) > 0:
                    dCheck = True
                
                #~~~If all the inputs are good, record the charge~~~   
                if cCheck[0] and tCheck and dCheck:
                    charge = str(values['TimeIn']).zfill(2) + '-' + values['ChargeIn'] + ' -- ' + values['TempIn'].zfill(4) + ' -- ' + currTime.strftime("%d-%b-%y") #Filename to save
                    record_charge(charge)
                    
                    
                elif not tCheck:
                    popWindow('Please input a temperature.')
                elif not dCheck:
                    popWindow('Please input a duration less than 50 hours.')
            
                    
            
            #If stopping charge recording
            elif event == 'cRecord' and settings['chargeRecord'] != 'N':
                RC.update_settings(path, "chargeRecord",'N')
                settings['chargeRecord'] = 'N'
                update_record(True)
                popWindow('Recording cancelled.')
                
                
                
        # ~~~~~Charge in use window controls~~~~~
            if windows == chargeWin:
                if event == 'chargeCancel':
                    #chargeRecord = RC.get_settings('Record', path)
                    chargeWin.close()
                    
                elif event == 'chargeRU':
                    RC.reuse(path, settings['chargeRecord'][3:8])
                    chargeWin.close()
                    record_charge(settings['chargeRecord'])
                    
                elif event == 'chargeOW':
                    RC.overwrite(path, settings['chargeRecord'][3:8])
                    chargeWin.close()
                    record_charge(settings['chargeRecord'])
                    
                
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  CHARGE WINDOW  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        elif event == 'Old Log':
            window['Main Screen'].update(visible=True)
            window['Title'].update(visible=False)
            window['Charge'].select()
            activeScreen = 'Charge'
            window['cList'].update(values=RC.get_charges(path))
        
        elif activeScreen == 'Charge':
            if event == 'charge_filter_clear':
                window['charge_search'].update(value='')
                window['temp_search'].update(value='')
                window['date_search'].update(value='')
                
            elif event == 'charge_filter':
                window['cList'].update(values=RC.get_charges(path,values['charge_search'],values['temp_search'],values['date_search']))
                
            elif event == 'View' and values['cList']:
                window["Log"].select()
                window['logInput'].update(visible = False)
                window['cDesc'].update(visible=True)
                window['cDesc'].update('You are viewing:\n' + str(values['cList'][0]))
                activeScreen = 'Log'
                
                display_graph(path+'Charges/' + str(values['cList'][0]) + '.csv')
                chargeDisplay = True
                
                #~~~Setup initial axes~~~
                zoom = 30
                right = max(x) #most recent reading
                maxTime = right #global storage of above for Home button
                left = right - zoom #make view to be towards the end of readings
                window['Slide'].update(range=(zoom,maxTime)) #Update the slider on the bottom of the graph
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
                
            elif event == 'eBut':
                if window['eBut'].get_text() == 'Disable Emails':
                    window['eBut'].update('Enable Emails')
                else:
                    window['eBut'].update('Disable Emails')
                
                
            elif event == 'Submit':
                
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
                if int_exists and temp_exists and maxR_exists:
                    eAlert = True if window['eBut'].get_text() == 'Disable Emails' else False
                    
                    settingsNew = {
                        "interval": int(values['interval']),
                        "tempWarn": int(values['temp']),
                        "maxRecords": int(values['maxRecords']),
                        "chargeRecord": settings['chargeRecord'],
                        "emailTo": str(values ['email']).split("; "),
                        "enableEmail": bool(eAlert),
                        "github": values['github']
                    }
                    
                    RC.update_settings(path, "all", settingsNew)
                    popWindow('Settings have been changed successfully.')
                    window['Main Screen'].update(visible=False)
                    window['Title'].update(visible=True)
                    window["Main"].select()
                    
                    
                #ERROR MESSAGES                   
                if not int_exists:
                    popWindow('Please input an interval less than 100 minutes')
                
                elif not temp_exists:
                    popWindow('Please input a temperature less than 3000°F')
                    
                elif not maxR_exists:
                    popWindow('Please input a maximum number of records greater than 100')
        
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  ERROR HANDLING  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    #If an error happens, inform the user
    #Obviously I can't catch them all so the common ones have messages while anything else just spits out the error
    
    except Exception as err:
        print(err)
        
        if str(err) == "Missing column provided to 'parse_dates': 'Time'":
            popWindow("~~ERR 05~~\nCharge file contains no headers, cannot be read.")
        
        elif str(err) == "Can only use .dt accessor with datetimelike values":
            popWindow("~~ERR 06~~\nInvalid date in charge file, cannot be read.")
        
        elif str(err)[:10] == "[Errno 13]":
            sg.popup_timed("~~ERR 07~~\nThe log file is open! Please close it to continue.\nTrying again in 10s.",font=font,keep_on_top=True,non_blocking=True,auto_close_duration=5)
            currTime = datetime.datetime.fromtimestamp(time())
            lastRead = currTime - datetime.timedelta(seconds=(int(settings['interval'])*60-10)) #try again in 10s
        
        elif str(err) == "float division by zero":
            popWindow("~~ERR 08~~\nCharge file contains no data and cannot be read.\nCopy data from the log file to the charge file.")
        
        elif str(err) == "zero-size array to reduction operation minimum which has no identity":
            popWindow("~~ERR 09~~\nCharge cannot be displayed. Not enough data.")
        
        else: #catch all
            popWindow("~~ERR 00~~\n" + str(err))
            print('Error on line {}'.format(exc_info()[-1].tb_lineno), type(err).__name__, err)
            #~~~Write to the error log file~~~
            with open(path+'Program/Error-Logs.txt','a') as f:
                f.write(currTime.strftime("%d-%b-%y - %I:%M:%S %p") + ': ERR00: Line {} -- '.format(exc_info()[-1].tb_lineno) + str(err)+'\n')
        
window.close()




# ~~~~~ References ~~~~~
# https://github.com/PySimpleGUI/PySimpleGUI/issues/3946                                                Tab groups and hiding tabs
# https://stackoverflow.com/questions/48134269/python-pyinstaller-bundle-image-in-gui-to-onefile-exe    Include photo in EXE
# https://stackoverflow.com/a/63445581                                                                  Upload file to Github
# https://stackoverflow.com/a/5721805                                                                   Refresh page with Javascript
# https://www.geeksforgeeks.org/how-to-update-a-plot-on-same-figure-during-the-loop/                    Fixed scrolling bug
# https://stackoverflow.com/a/41642105                                                                  Get line number of error

# ~~~~~ Compile ~~~~~
#pyinstaller -wF --splash=splashLoad.jpg --icon=RecorderIcon.ico Recorder.py