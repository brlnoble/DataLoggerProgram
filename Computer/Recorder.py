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
    import pyi_splash #Used in the compiled EXE only
    pyi_splash.close()
except:
    pass



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Application Functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~Record a charge~~~~~
def Record_Charge(charge):
    global charge_end
    charge_end = current_time + datetime.timedelta(hours=(int(charge[:2])+2)) #time to end the charge at, 2 hour extra safety
    RC.update_settings(path, "chargeRecord",charge)
    settings['chargeRecord'] = charge
    Update_Recording_Banner(True)
    

# ~~~~~Update settings window~~~~~
def Update_Settings_Display():
    event, values = window.read(timeout=100)
    window['interval'].update(value = settings['interval'])
    window['temp'].update(value = settings['tempWarn'])
    window['maxRecords'].update(value = settings['maxRecords'])
    window['github'].update(value = settings['github'])
    
    if bool(settings['enableEmail']) == True:
        window['enable_email_alerts'].update('Disable Emails')
    else:
        window['enable_email_alerts'].update('Enable Emails')
        
    #Email listed as: one@email.com; two@email.com
    emailToStr = ''
    for i in range(0,len(settings['emailTo'])):
        emailToStr += str(settings['emailTo'][i]) +'; '
    window['email'].update(value = emailToStr[:-2])

# ~~~~~Change active screen~~~~~
def Change_Active_Screen(screen):
    window['goto_main'].update(visible=True) #Show button for returning to main screen
    window['Title'].update(visible=False) #Hide the title
    window[screen].select() #Change to the specified screen
    global active_screen
    active_screen = screen #Save the screen

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ User notifications ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~Update recording status~~~~~
def Update_Recording_Banner(change):
    
    record = settings['chargeRecord']
    
    if record != 'N':    
        #Alert the user it is recording
        window['recording_banner'].update('Currently Recording: ' + record[3:])
        window['recording_banner'].update(background_color='#02AB29')
        
        #Update the button to stop recording
        window['charge_record_btn'].update('Stop Recording')
        window['charge_record_btn'].update(button_color='#F5273A')
        
        #Disable changing the input boxes
        window['charge_input'].update(disabled=True)
        window['temp_input'].update(disabled=True)
        window['time_input'].update(disabled=True)
    else:
        #Remove alert for the user
        window['recording_banner'].update('')
        window['recording_banner'].update(background_color='#EEE')
        
        #Update the button to start recording
        window['charge_record_btn'].update('Record')
        window['charge_record_btn'].update(button_color='#02AB29')
        
        #Enable changing the input boxes
        window['charge_input'].update(disabled=False)
        window['temp_input'].update(disabled=False)
        window['time_input'].update(disabled=False)
        
    if change:
        #Update settings file
        RC.update_settings(path,"chargeRecord",record)
        
# ~~~~~Alert across top~~~~~
def Update_Alert_Banner(msg):
    if msg != '':
        #Alert the user of an issue
        window['alert_banner'].update(msg)
        window['alert_banner'].update(background_color='#F5273A')
        
    else:
        #Hide alert
        window['alert_banner'].update('')
        window['alert_banner'].update(background_color='#EEE')
        
        
# ~~~~~UPDATE THERMOCOUPLE READINGS~~~~~
def Update_Main_Screen_TC():
    df = pd.read_csv(log_file)
    
    window['lastRead'].update(value=df['Time'].values[-1]) #last time the file was written to
    
    for tc in range(1,7):
        window['TC' + str(tc)].update(str(round(df['Temp' + str(tc)].values[-1],1)) + '°F')
        
        #check high temperature limit
        if round(df['Temp' + str(tc)].values[-1],1) < int(settings['tempWarn']):
            window['TC' + str(tc)].update(background_color='#EEE')
                          
        else: #!!!Temperature over limit!!!
            window['TC' + str(tc)].update(background_color='#F5273A')
            Update_Alert_Banner('THERMOCOUPLE TC{} OVER LIMIT'.format(tc))


# ~~~~~Pop up window~~~~~
def Popup_Window(msg):
    #The frames add a small blue border around the outside, otherwise the popup blends into the other windows
    popLayout = [
        [sg.Frame("",
            [
                [sg.Frame("",
                    [
                        [sg.Text('Alert',font=titleFont)],
                        [sg.Text(msg,font=font,pad=(10,10))],
                    ],pad=2,relief='flat',expand_x=True)
                ]
            ],relief='flat',background_color='#1D2873',pad=0,expand_x=True)
        ]
    ]
    
    return sg.Window("Data Logger - Alert", popLayout, keep_on_top=True, element_justification='c',modal=True,finalize=True)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Graph Updating ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~Updates thermocouples on right of graph~~~~~
def Update_Log_Screen_TC():
    val = right - select_data_slider[0]
    if len(dates) - 1 >= val and val > 0:
        window['TC_Title_Log'].update(dates[val])
        window['TC1_Log'].update(str(round(df.Temp1[val],1)).zfill(5) + '°F')
        window['TC2_Log'].update(str(round(df.Temp2[val],1)).zfill(5) + '°F')
        window['TC3_Log'].update(str(round(df.Temp3[val],1)).zfill(5) + '°F')
        window['TC4_Log'].update(str(round(df.Temp4[val],1)).zfill(5) + '°F')
        window['TC6_Log'].update(str(round(df.Temp6[val],1)).zfill(5) + '°F')
    else:
        window['TC_Title_Log'].update('Reading: \nUnavailable')
        window['TC1_Log'].update('000.0' + '°F')
        window['TC2_Log'].update('000.0' + '°F')
        window['TC3_Log'].update('000.0' + '°F')
        window['TC4_Log'].update('000.0' + '°F')
        window['TC6_Log'].update('000.0' + '°F')
    
    
# ~~~~~Update graphs when zooming~~~~~
def Update_Graph_View():
    plt.xlim(left,right) #size of viewport
    plt.locator_params(axis='x', nbins=(max_time/(right-left))*10) #makes sure there are only 10 x-axis ticks at a time
    
    #Update data marker
    window['select_data_slider'].update(range=(zoom,0))
    Select_Data() 

    
# ~~~~~Change red data marker~~~~~
def Select_Data():
    global lineSelect
    lineSelect.set_xdata(right-select_data_slider[0])
    #Update axis without redrawing entire graph
    fig.canvas.draw()
    Update_Log_Screen_TC()
    
    
# ~~~~~Save an image~~~~~
def Save_Graph_As_Image(titleText):
    if not RC.does_this_exist(path,"Figures\\"):
        RC.make_folder(path + "Figures\\")
        
    imgName = path + "Figures/" + current_time.strftime("%d-%B-%y - %I-%M-%S %p") + ".png"
    
    plt.legend(bbox_to_anchor=(0,1,1,0), loc="lower left", mode="expand", borderaxespad=0, ncol=6)
    lineSelect.set_visible(False)
    plt.title(titleText,fontsize=30,pad=30)
    plt.savefig(imgName, bbox_inches='tight')
    plt.legend('',frameon=False)
    lineSelect.set_visible(True)
    plt.title('')
    Popup_Window("Image saved in Figures folder.\n" + current_time.strftime("%d-%B-%y - %I-%M-%S %p") + ".png")
    RC.open_folder(imgName)
    

# ~~~~~Include the Matplotlib figure in the canvas~~~~~
def Add_Graph_To_Canvas(canvas, fig):
    #If already displaying, delete current graph
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


# ~~~~~MATPLOTLIB DISPLAY ALL THE GRAPH DATA~~~~~
def Display_Graph(fileName):
    global plt
    plt.clf()
    plt.figure(1)
    global fig
    fig = plt.gcf()
    DPI = fig.get_dpi()
    fig.set_size_inches(graphSize[0] / float(DPI), graphSize[1] / float(DPI)) #THESE MUST MATCH THE SIZE OF THE ABOVE CANVAS FOR THE GRAPH

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
    
    Update_Log_Screen_TC() #adds the readings on the right
    
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
    global plot_display
    plot_display = True #flag to prevent moving plot before it is shown
    Add_Graph_To_Canvas(window['fig_cv'].TKCanvas, fig)
    
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Application Screen Related ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~Change dimenions based on screen size~~~~~
def Check_Screen_Size():
    screen_check = sg.Window("",layout=[[]],finalize=True)
    
    screen_dimensions = screen_check.get_screen_dimensions()
    screen_check.close()

    global scale_factor
    global furnace_pic
    global fire_icon
    
    #If the screen is the standard dimensions
    if screen_dimensions == (1920,1080):
        scale_factor = 1.0
        
    #If the screen is NOT the standard dimensions
    else:
        scale_factor = screen_dimensions[1]/1080.0
                
        furnace_pic = RC.scale_base64(furnace_pic, scale_factor)
        fire_icon = RC.scale_base64(fire_icon, scale_factor)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Additional Screens ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~Error log~~~~~
def Create_Error_Log_Window():
    errLayout = [
        [sg.VPush()],
        [sg.Text('Error Logs',font=titleFont)],
        [sg.Listbox(values=RC.get_err(path),size=(120,30),font=font)],
        [sg.Button('Close',key='errCancel',font=butFont,button_color='#F5273A',size=(10,2))],
        [sg.VPush()],
    ]
    #Open up the error log in a new window
    return sg.Window("Data Logger - Error Log", errLayout, keep_on_top=True, element_justification='c',modal=True,finalize=True)


# ~~~~~Charge is already in use~~~~~
def Create_Charge_In_Use_Window(cNum,oldNum):
    chargeLayout = [
        [sg.VPush()],
        [sg.Text('Charge Number Already in Use',font=titleFont)],
        [sg.Text('The charge you input is already in use. Please select an option as described below.',font=font)],
        [sg.Text(cNum + ' was recorded on '+oldNum[-9:],key='charge_inputF',font=butFont,pad=(0,20),text_color='#F5273A')],
        [sg.Text('Overwrite: ',font=butFont,text_color='#22B366',size=(15,1)),sg.Text('Delete the old file, and start recording in a new file with number ' + cNum +'.\nUse this option if you messed up the previous recording.',font=font,pad=(0,10),size=(70,2))],
        [sg.Text('Redo Charge: ',font=butFont,text_color='#AA00AA',size=(15,1)),sg.Text('Keep the old file, and start recording in a new file with number ' + cNum + '.\nUse this option if the furnace failed and you are redoing the charge.',font=font,pad=(0,10),size=(70,2))],
        [sg.Text('',pad=(0,30))],
        [sg.Button('Overwrite',key='chargeOW',font=butFont,button_color='#00B366',size=(12,2)),
         sg.Button('Redo Charge',key='chargeRU',font=butFont,button_color='#AA00AA',size=(12,2)),
         sg.Button('Cancel',key='chargeCancel',font=butFont,button_color='#F5273A',size=(15,2),pad=((50,0),(0,0)))],
        [sg.VPush()]
    ]
    #Open up the 'charge already in use' in a new window
    return sg.Window("Data Logger - Charge in Use", chargeLayout, keep_on_top=True, element_justification='c',modal=True,finalize=True)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Startup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#Current directory path
path = RC.get_path()
log_file = path + 'Program/AllTempLogs.csv'

#MAKE SURE THE SETTINGS FILE EXISTS
if not RC.verify_settings(path):
    Popup_Window('Settings file does not exist.\n\nA file with default values has been generated.') #inform user it was not found
    

#Imbed image as Base64 string so the EXE can be a standalone file
furnace_pic = b"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"
fire_icon = b'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAAAXNSR0IArs4c6QAAAuBJREFUSEvF109IFFEcB/Dv7Mzqrn/XDQxqjSDo0EoUUUG0FXWxIC0KzC5FdIgudcoyo6yQ8lAX+2dmgaAm2EWNhCByIdBC8+BB18WoVPQws390c9eZeTGz7ejs7Mju6Oa7vffm/T7vz2923lJYo0LpuPQqz0eIj6eC3W53n9Pp3LPKqBxueHi43+Vy7Y3FVuB0ojFsKa7ALMuSdKw0PqbdbpfNGEyzLMunBBOCjM+diBw8DlB6qaKNaLfbGQCCIdjy6S2sH14D4zPg2gdSmq9hOKexCmZPFBP9BP7nPemHLe53sHY1KJBAbAjUtaUZJgQF14+qEHGOgb++K72wpbcD1u6XamR8Glz7oLqNkGWTLeUztt05DerPrBrxTiFY0wjeuVtup3+OIbv+FgJ1rbq7kDJcUFmiDeadktvCx87KL2Zmd4tc97X0gWRYEuIpwRQfge1mqS4c3xG6XIPw4RMrgEURMJlgCnLIv1+RNBwuKUfoYpVxOP/heQSuPgUVCiL/wTltoN8TQNikaQ9dqIxuf4KS1FbbqstALYQxd+YastvqlDBkEwth/xiYWseSH79FxfemF/SPEfDF2g9dcvDtU6Dm51TzJht8EA6Nym3MvSLtmigKYuFGUAEOvuYvmv6k4NyGSjDeIdVgvqJf+bQwTYXARCZgEYF59Zbz23YheLfJGMz8GkFu/ZXFwdYI+JPflToz8+87QxPghXr1wdpm8Fu3G4OlUbbqUlALETkAcXAQDnjUcKzWWQhMZkafM2fA1/rVeHJJI03ctJLRpIiD4NKBP64DvFky5n/SDXG9Y2WwNNrsGURO4w2AFsGXf0u84lcOgKcwW/0MCzv2JUSlxqSSa+lo6V3Oe3wJ2DwEsXgymtXSGUtlMA+iZwsCjzpAcm26qCE4Fo0Kh2Ae7QFtfQ+TXwA/fwSRnWUgWTnLgrHO+BVjrS57WLPrrbQV6cR1L/RxB/R//8IklR2r9NBfLy1iLgM4NkgAAAAASUVORK5CYII='

# ~~~~~Stylize the window~~~~~
#Window theme
sg.theme('DefaultNoMoreNagging')
sg.theme_text_element_background_color(color = '#EEE')
sg.theme_text_color('#1D2873')
sg.theme_background_color('#EEE')

Check_Screen_Size() #Check screen scaling

#Fonts, scale according to the screen size
font = ('Arial', int(16*scale_factor))
butFont = ('Arial', int(16*scale_factor), 'bold')
iconFont = ('Segoe UI Symbol',int(20*scale_factor),'bold')
tcFont = ('Courier New',int(16*scale_factor),'bold')
titleFont = ('Arial', int(26*scale_factor), 'bold')
chargeFont = ('Courier New',int(16*scale_factor),'bold')

graphSize = (round(1200*scale_factor), round(550*scale_factor))

sg.set_options(use_custom_titlebar=True,titlebar_icon=fire_icon,titlebar_font=font) #Set the titlebar


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


settings = RC.get_settings("all", path) #CONTAINS ALL THE SETTINGS

current_time = datetime.datetime.fromtimestamp(time()) #used for 'clock'. Current time
last_reading_time = current_time - datetime.timedelta(seconds=(int(settings['interval'])*60)) #last time the TCs were read

last_settings_edit = RC.get_mtime(path,"Program/Settings.json") #Last time settings were modified
last_settings_check = current_time #last time settings were checked

plot_display = False #flag for the plot display
charge_display = False #flag for the charge view
active_screen  = 'main_screen' #helps speed up the main loop by only checking code revelant to each screen


#Axes limits
zoom = 30
max_zoom = 300
min_zoom = 5
left = 0
right = 0
max_time = 0
select_data_slider = [1,zoom-1]


################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main Window ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




butCol = [
            [sg.Button('Settings',key='goto_settings',size=(20,3), font=butFont, button_color='#1D2873'), sg.Push(), sg.Button('View Previous Log',key='goto_charge',size=(20,3), font=butFont, button_color='#F5AC11')],
            [sg.Button('View Current Readout',key='goto_live',size=(42,3), font=butFont, button_color='#02AB29')],
        ]


main_screen_layout = [  
            [sg.Column(butCol)], [sg.Text('Reading as of: ',font=butFont),sg.Text('',key='lastRead',font=font,pad=(0,30))],
            
            #TCs along the top of the furnace display
            [sg.Push(),sg.Push(), sg.Text('TC6:',font=butFont),sg.Text('000.0',key='TC6', font=tcFont), 
             sg.Push(), sg.Text('TC5:',font=butFont),sg.Text('000.0',key='TC5', font=tcFont,text_color='#EEE'), 
             sg.Push(), sg.Text('TC4:',font=butFont),sg.Text('000.0',key='TC4', font=tcFont),sg.Push(),sg.Push()],
            
            #Furnace display image
            [sg.Image(furnace_pic,pad=(0,0))],
            
            #TCs along the bottom of the furnace display
            [sg.Push(),sg.Push(), sg.Text('TC1:',font=butFont),sg.Text('000.0',key='TC1', font=tcFont), 
             sg.Push(), sg.Text('TC2:',font=butFont),sg.Text('000.0',key='TC2', font=tcFont), 
             sg.Push(), sg.Text('TC3:',font=butFont),sg.Text('000.0',key='TC3', font=tcFont),sg.Push(),sg.Push()],
            
            [sg.Text('',font=font)], #spacing
            [sg.Button('Exit Program',key='close_program_btn',size=(20,3), font=butFont, button_color='#F5273A')],
            
            #Open up the documentation or the error log
            [sg.Button('Help',font=butFont,button_color='#F57627',size=(10,2)),sg.Push(),sg.Push(),sg.Button('Error Log',key='goto_error',font=butFont,button_color='#333',size=(10,2))],
        ]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Settings Window ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


settings_screen_layout = [  
            [sg.Text('SETTINGS', font=titleFont,pad=(0,50))],
            
            #Settings the user will be most likely to change
            [sg.Column([
                [sg.Text('Interval (min):',size=(15,1), font=font,justification='r'), sg.Input(key='interval', enable_events=True,size=(20,1), font=font,tooltip="Number of minutes between readings")],
                [sg.Text('Temp Warning (F):',size=(15,1), font=font,justification='r'), sg.Input(key='temp', enable_events=True,size=(20,1), font=font,tooltip="High temperature limit. \nWhen exceeded it will trigger warnings.")],
                [sg.Text('_'*56,font=font,pad=(0,20),text_color='#EEE')], #spacing
            ])],
            
            #Warn the user to consult manual
            [sg.Text('Please do not change the following without consulting the manual.',font=butFont,pad=(0,10),text_color='#F5273A')],
            
            #More advanced settings, unlikely to be changed by user
            [sg.Column([
                [sg.Text('Alert Emails:',size=(15,1), font=font,justification='r'), sg.Multiline(key='email', enable_events=True,size=(25,3), font=font,tooltip="Enter emails to send high temperature alerts to. \nSeparate with a ' ;'")],
                [sg.Text('Enable Alerts:',font=font,size=(15,1),justification='r'), sg.Button('Enable Emails',key='enable_email_alerts',font=('Arial',10),size=(12,1),enable_events=True)],
                
                [sg.Text('Max Log Records:',size=(15,1), font=font,justification='r'), sg.Input(key='maxRecords', enable_events=True,size=(15,1), font=font,tooltip="Maximum records in the general log file (does not affect individual charges)")],
                [sg.Text('Github Key:',size=(15,1), font=font,justification='r'), sg.Input(key='github', enable_events=True,size=(41,1), font=font,tooltip="Github key used for uploading to the website: \nhttps://uds-furnace.github.io/View/")],
            ])],
            
            [sg.Text('',key='tips',pad=(0,20))],
            [sg.Push(), sg.Button('Save Changes',key='Submit',size=(15,2), font=butFont, button_color='#02AB29'), sg.Push(), sg.Button('Cancel',size=(15,2), font=butFont, button_color='#F5273A'), sg.Push()],
        ]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Log View Window ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Thermocouple graph reading on the right
tcGraph = [ 
            [sg.Text('Reading at Black Line',font=butFont,justification='c')],
            [sg.Text()],
            [sg.Text('',key='TC_Title_Log',font=font,justification='c')],
            [sg.Text('TC1: ',font=butFont,text_color='#FF0000'),sg.Text('1',font=tcFont,key='TC1_Log',text_color='#333')],
            [sg.Text('TC2: ',font=butFont,text_color='#FFAA00'),sg.Text('2',font=tcFont,key='TC2_Log',text_color='#333')],
            [sg.Text('TC3: ',font=butFont,text_color='#365BB0'),sg.Text('3',font=tcFont,key='TC3_Log',text_color='#333')],
            [sg.Text('TC4: ',font=butFont,text_color='#00B366'),sg.Text('4',font=tcFont,key='TC4_Log',text_color='#333')],
            [sg.Text('TC6: ',font=butFont,text_color='#AA00AA'),sg.Text('6',font=tcFont,key='TC6_Log',text_color='#333')],
            [sg.Text()],
            [sg.Button('Save Graph',key='save_image_btn',font=butFont,button_color="#F57627",size=(10,2))]
            
        ]

#Input boxes at top of screen
inputFormat = [
            [sg.Text('Charge Number:',size=(15,1), font=font,justification='r'), sg.Input(key='charge_input', enable_events=True,size=(15,1), font=font,tooltip="5 digit charge number.\nFor example: '16328'")],
            [sg.Text('Temperature:',size=(15,1), font=font,justification='r'), sg.Input(key='temp_input', enable_events=True,size=(15,1), font=font,tooltip="Temperature without units.\nFor example: '600'")],
            [sg.Text('Duration:',size=(15,1), font=font,justification='r'), sg.Input(key='time_input', enable_events=True,size=(15,1), font=font,tooltip="Duration in hours")],
    ]

#Zoom buttons for navigating graph
zoomButFormat = [
            [sg.Button('➕',key="ZoomIn",size=(5,1), font=iconFont), sg.Button('➖',key="ZoomOut",size=(5,1), font=iconFont)]
    ]

#Scroll/home buttons for navigating graph
scrollButFormat = [
            [sg.Button('◀',key="Left",size=(10,1), font=iconFont),sg.Button('🏠',key='Home', size=(10,1), font=iconFont), sg.Button('▶',key="Right",size=(10,1), font=iconFont)],
    ]


#Layout of entire screen
log_screen_layout = [  
            #Input for recording & buttons to do so
            [sg.Column([
                [sg.Column(inputFormat,pad=(50,0)),sg.Column([[sg.Button('Record',key='charge_record_btn',size=(10,2), font=butFont, button_color='#02AB29')]])],
                ],key='recording_input_boxes')],
                       
            #Graph and navigation
            [sg.Column([
                [sg.Column(
                    layout=[
                            #This is the slider at the top of the graph, moves the data selector
                            [sg.Slider(key='select_data_slider',range=(zoom-1,1),default_value=1,size=(0,30),enable_events=True,orientation='h',expand_x=True,pad=((55,10),(5,0)),disable_number_display=True,trough_color='#EEE',background_color='#000')],
                            
                            #This is the graph
                            [sg.Canvas(key='fig_cv',size=graphSize)], 
                            
                            #This is the slider at the bottom of the graph, moves the graph view
                            [sg.Slider(key='position_slider',range=(zoom,max_time),size=(0,30),enable_events=True,orientation='h',expand_x=True,pad=((55,10),(5,5)),disable_number_display=True,trough_color='#EEE',background_color='#1D2873')],
                            
                            #Buttons to naviagate, zoom, and return home
                            [sg.Column([
                                [sg.Column(scrollButFormat,pad=(20,5),background_color='#FFF'),sg.Text('',pad=(50,0),background_color='#FFF'),sg.Column(zoomButFormat,pad=(20,5),background_color='#FFF')]],justification='c',background_color='#FFF')],
                    ], #end layout
                
                    background_color='#FFF',pad=(10,10)), #graph/slider column settings
                ]],background_color='#1D2873'),
            
            #TC readout at the black line
            sg.Column([
                [sg.Text('',font=font,key='charge_description',justification='c')],
                [sg.Text('')],
                [sg.Column(tcGraph,element_justification='c',pad=(50,0))]
                ],element_justification='c')
            ],                
        ]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Old Log Window ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Search section on the left of the screen
chargeSearch = [
                [sg.Text('Search Charges',font=butFont,size=(24,2),justification='c')],
                [sg.Text('You can filter the list on the right by searching for any combination of the below.',font=('Arial',10),text_color='#777',size=(36,3))],
                [sg.Text('Charge:',font=font,size=(12,1),text_color="#333",justification='r'),sg.Input(key='charge_search',font=font,size=(12,2),tooltip="Charge number such as '16328'")],
                [sg.Text('Temperature:',font=font,size=(12,1),text_color="#333",justification='r'),sg.Input(key='temp_search',font=font,size=(12,2),tooltip="Temperature without units, such as '600'")],
                
                #Date search is a little more complicated because of the additional information for the user
                [sg.Text('Date:',font=font,size=(12,4),text_color="#333",justification='r'),
                        sg.Column([
                            [sg.Input(key='date_search',font=font,size=(12,2),tooltip="Format as dd/mm/yyyy or enter a month and year")],
                            [sg.Text("day/month/year",font=('Arial',10,'bold'),justification='c',size=(12,1),text_color="#777",pad=0)],
                            [sg.Text("OR",font=('Arial',10),justification='c',size=(12,1),text_color="#777",pad=0)],
                            [sg.Text("month/year",font=('Arial',10,'bold'),justification='c',size=(12,1),text_color="#777",pad=0)],
                        ],element_justification='c')]
            ]

#Buttons to clear the search boxes or to perform the search
chargeSearchButtons = [
                [sg.Button('Search',key="charge_filter",font=font,size=(12,2),button_color="#F57627",pad=(0,10))],
                [sg.Button('Clear Search',key="charge_filter_clear",font=font,size=(12,1),pad=(0,10))], 
            ]

#Combine the search boxes and buttons in a frame to add a small outside border
#Outside frame makes the border, inside frame determines the border width
chargeSearchAll = [
                    [sg.Frame("",
                        [
                            [sg.Frame("",
                                [
                                    [sg.Column(chargeSearch,element_justification='c')],
                                    [sg.Column(chargeSearchButtons,element_justification='c',pad=10)]
                                ],element_justification='c',relief='flat',pad=1)],
                        ],relief='flat',background_color='#777')]
            ]

#Collection of the above layouts
charge_screen_layout = [
            [sg.Text('Please select a charge from the list below, then click View to display the graph.',font=font,text_color='#333')],
            [sg.Text('')],
            
            #Title and listbox for the charges
            [sg.Column(chargeSearchAll),sg.Text('',font=font,size=(5,1)),sg.Column([
                [sg.Text('Charge -- Temp -- Date',font=tcFont)], #format of information
                [sg.Listbox(values='',size=(27,20),font=chargeFont,key='old_recording_list')] #listbox
                ],element_justification='c')
            ],
            
            [sg.Text()],
            [sg.Button('View',font=butFont,size=(16,2),button_color='#02AB29')]
        ]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ COMBINE ALL WINDOWS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#This compiles all the screens in the program
tab_group = [
    [sg.Tab("Main", main_screen_layout, key="main_screen",element_justification='c',background_color='#EEEEEE')],
    [sg.Tab("Settings", settings_screen_layout, key="settings_screen",element_justification='c',background_color='#EEEEEE')],
    [sg.Tab("Logging", log_screen_layout, key="log_screen",element_justification='c',background_color='#EEEEEE')],
    [sg.Tab("Charge", charge_screen_layout, key="charge_screen",element_justification='c',background_color='#EEEEEE')],
]

#Final layout for the main window object
layout = [
    [sg.Text(key='recording_banner',font=butFont,background_color='#EEEEEE',text_color='#FFF',expand_x=True,justification='c',pad=(0,0))], #Banner across the top that shows when we are recording
    [sg.Text(key='alert_banner',font=butFont,background_color='#EEEEEE',text_color='#FFF',expand_x=True,justification='c',pad=(0,0))], #Banner across the top that shows when there is a temperature alert
    [sg.Text('DATA LOGGER', key='Title', font=titleFont,pad=(0,20)),sg.Button('Main Screen',key='goto_main',size=(10,2), font=butFont, button_color='#F5273A',visible=False)],
    [sg.Text(key='clock',font=butFont)],
    [sg.TabGroup(tab_group, border_width=0, pad=(0, 0), key='TABGROUP')],
]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CREATE WINDOW FOR APPLICATION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

window, error_window, charge_in_use_window = sg.Window("Data Logger", layout, keep_on_top=True, location=(0, 0), element_justification='c',finalize=True), None, None
window.Maximize() #Make it full screen
window.set_icon(pngbase64=fire_icon) #Add the taskbar icon

#Hide the tabs bar from the screen
style = ttk.Style()
style.layout('TNotebook.Tab', [])


################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################


#Update the charge if it is currently recording
Update_Recording_Banner(False)
if settings['chargeRecord'] not in ['Y','N']:
    window['charge_input'].update(settings['chargeRecord'][3:8])
    window['temp_input'].update(settings['chargeRecord'][12:16])
    window['time_input'].update(settings['chargeRecord'][0:2])
    

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN LOOP ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

while True:

    #Wrap everything in a try except to catch any errors
    try:
        
        #Read all windows for events
        windows,event, values = sg.read_all_windows(timeout=100)
        
        #See if window should be closed
        if event in (sg.WINDOW_CLOSED, "close_program_btn"):
            if windows == window:
                break #Close main window
            else:
                windows.close() #Close other windows
        
        
        #Update the 'clock' at the top of the screen
        current_time = datetime.datetime.fromtimestamp(time())
        window['clock'].update(current_time.strftime("%d %B, %Y - %I:%M:%S %p"))
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        #Check if settings have changed every 10s
        if current_time - datetime.timedelta(seconds=10) > last_settings_check:
            if RC.get_mtime(path, 'Program/Settings.json') > last_settings_edit:
                settings = RC.get_settings("all", path)
                Update_Recording_Banner(False)
                last_settings_edit = RC.get_mtime(path, 'Program/Settings.json')
                last_settings_check = current_time
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        #Check every 60s if it is time to update the TC readings
        if current_time - datetime.timedelta(seconds=(60)) > last_reading_time:
            last_reading_time = current_time
            Update_Main_Screen_TC()
            
            #only update graph if we are viewing the live plot and not charges
            if plot_display and not charge_display:
                #adjust view if looking at most recent point
                df = pd.read_csv(log_file,parse_dates=['clock'], dayfirst=True)
                if len(df.Temp1) -1 > max_time:
                    if right == max_time:
                        right += 1
                        left -= 1
                        
                    Display_Graph(log_file)
                    Update_Graph_View()
         
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Misc Commands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        #RETURN TO MAIN SCREEN
        if event == 'goto_main': 
            charge_display = False
            window['goto_main'].update(visible=False)
            window['Title'].update(visible=True)
            window["main_screen"].select()
            active_screen = 'main_screen'

        
                
        # ~~~~~Charge in use window controls~~~~~
        if windows == charge_in_use_window:
            if event == 'chargeCancel':
                charge_in_use_window.close()
                
            elif event == 'chargeRU':
                RC.reuse(path, settings['chargeRecord'][3:8])
                charge_in_use_window.close()
                Record_Charge(settings['chargeRecord'])
                
            elif event == 'chargeOW':
                RC.overwrite(path, settings['chargeRecord'][3:8])
                charge_in_use_window.close()
                Record_Charge(settings['chargeRecord'])
         
        # ~~~~~Error log window controls~~~~~
        if windows == error_window:
            #Close error log window
            if event == 'errCancel':
                error_window.close()
                    
                    
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN SCREEN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        if active_screen == 'main_screen':
            
            # ~~~~~Open up the live log screen~~~~~
            if event == 'goto_live':
                Change_Active_Screen('log_screen')
                window['recording_input_boxes'].update(visible = True) #Show input buttons for recording charges
                window['charge_description'].update(visible=False) #Hide charge description
                window['charge_record_btn'].update(disabled=False) #Enable recording
                
                Display_Graph(log_file)
                
                #~~~Setup initial axes~~~
                zoom = 30
                right = max(x) #most recent reading
                max_time = right #global storage of above for Home button
                left = right - zoom #make view to be towards the end of readings
                window['position_slider'].update(range=(zoom,max_time)) #Update the slider on the bottom of the graph
                window['position_slider'].update(value=max_time) #Set slider to right side of graph
                Update_Graph_View()
                
                
            # ~~~~~Open up the old log screen~~~~~
            elif event == 'goto_charge':
                Change_Active_Screen('charge_screen')
                window['old_recording_list'].update(values=RC.get_charges(path))
                
            # ~~~~~Open up the settings screen~~~~~
            elif event == "goto_settings":
                Change_Active_Screen('settings_screen')
                Update_Settings_Display()
                
    
            #~~~~~Open error log~~~~~
            elif event == 'goto_error':
                error_window = Create_Error_Log_Window()
                error_window.Maximize()
                
            #~~~~~Open up documentation~~~~~
            elif event == 'Help': 
                #try:
                    #startfile(path+r"Program\Installation & Instructions\Data Logger Documentation.docx")
                window.minimize()
                #except:
                    #Popup_Window("Documentation could not be found.\nCheck //DISKSTATION1/mill/1 - Mill/Data Logger/Program/Installation & Instructions/Data Logger Documentation.docx")
                
                
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOG SCREEN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        elif active_screen == 'log_screen':
            
            #Move the plot left
            if event == 'Left' and plot_display:
                left -= 1
                right -= 1
                window['position_slider'].update(value=right) #adjsut slider
                Update_Graph_View()
                
            #Move plot right
            elif event =='Right' and plot_display:
                left += 1
                right += 1
                if right < max_time:
                    window['position_slider'].update(value=right) #adjsut slider
                else:
                    window['position_slider'].update(value=max_time) #adjsut slider
                Update_Graph_View()
                
            #Return to home view
            elif event == 'Home' and plot_display:
                zoom = 30
                left = max_time - zoom
                right = max_time
                window['position_slider'].update(value=right) #Return slider to right side
                Update_Graph_View()
            
            #Zoom out graph
            elif event == 'ZoomOut' and plot_display:
                if zoom < max_zoom:
                    zoom = zoom + 5
                    left = right - zoom
                    Update_Graph_View()
                
            #Zoom in graph
            elif event == 'ZoomIn' and plot_display:
                if zoom > min_zoom:
                    zoom = zoom - 5
                    left = right - zoom
                    Update_Graph_View()
            
            #Move graph location according to scrollbar
            elif event == 'position_slider' and plot_display:
                right = values['position_slider']
                left = values['position_slider'] - zoom
                Update_Graph_View()
                
            #Move the data readout according to scrollbar
            elif event == 'select_data_slider' and plot_display:
                select_data_slider[0] = values['select_data_slider']
                Select_Data()
            
            #Save a screenshot of the graph
            elif event == 'save_image_btn':
                #If viewing a charge
                if window['charge_description'].get() != '':
                    Save_Graph_As_Image(str(window['charge_description'].get()).split('\n')[1])
                    
                #If viewing live log    
                else:
                    Save_Graph_As_Image('From ' + df.Time[left].strftime('%d-%b-%y %I:%M:%S %p') + ' to ' + df.Time[right].strftime('%d-%b-%y %I:%M:%S %p'))
         

            elif event == 'charge_input' and values['charge_input'] and (values['charge_input'][-1] not in ('0123456789') or len(values['charge_input']) > 5):
                window['charge_input'].update(values['charge_input'][:-1])
                
            elif event == 'temp_input' and values['temp_input'] and (values['temp_input'][-1] not in ('0123456789') or len(values['temp_input']) > 4):
                window['temp_input'].update(values['temp_input'][:-1])
                
            elif event == 'time_input' and values['time_input'] and (values['time_input'][-1] not in ('0123456789') or len(values['time_input']) >4):
                window['time_input'].update(values['time_input'][:-1])
            

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Recording a Charge ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
            #Recording a new charge
            elif event == 'charge_record_btn' and settings['chargeRecord'] == 'N':
                #For verifying inputs
                tCheck = False
                dCheck = False
                cCheck = [False,'']
                
                #Make sure charge number is valid
                if values['charge_input'] and len(values['charge_input']) == 5:
                    cCheck = RC.check_charge(path,values['charge_input'])
                        
                    if not cCheck[0]: #CHARGE IS ALREADY IN USE
                        charge_in_use_window = Create_Charge_In_Use_Window(values['charge_input'],cCheck[1])
                        charge_in_use_window.Maximize()
                        
                #Validate temperature
                if values['temp_input'] and int(values['temp_input']) > 0:
                    tCheck = True
                    
                #Validate duration
                if values['time_input'] and 50 > int(values['time_input']) > 0:
                    dCheck = True
                
                # ~~~~~If all the inputs are good, record the charge~~~~~
                if cCheck[0] and tCheck and dCheck:
                    #Start recording the charge
                    #Filename is charge -- temperature -- date
                    Record_Charge(str(values['time_input']).zfill(2) + '-' + values['charge_input'] + ' -- ' + values['temp_input'].zfill(4) + ' -- ' + current_time.strftime("%d-%b-%y"))
                    
                # ~~~~~Inform user of bad inputs~~~~~    
                elif not tCheck:
                    Popup_Window('Please input a temperature.')
                elif not dCheck:
                    Popup_Window('Please input a duration less than 50 hours.')
            
            # ~~~~~Stop charge recording~~~~~
            elif event == 'charge_record_btn' and settings['chargeRecord'] != 'N':
                RC.update_settings(path, "chargeRecord",'N')
                settings['chargeRecord'] = 'N'
                Update_Recording_Banner(True)
                Popup_Window('Recording cancelled.')
                
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ OLD CHARGE SCREEN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        
        elif active_screen == 'charge_screen':
            
            #Display the old charge if the user has selected something
            if event == 'View' and values['old_recording_list']:
                Change_Active_Screen('log_screen')
                window['recording_input_boxes'].update(visible = False)
                window['charge_description'].update(visible=True)
                window['charge_description'].update('You are viewing:\n' + str(values['old_recording_list'][0]))
                
                Display_Graph(path+'Charges/' + str(values['old_recording_list'][0]) + '.csv')
                charge_display = True #Viewing a charge and not the live view
                
                #Setup initial axes
                zoom = 30
                right = max(x) #most recent reading
                max_time = right #global storage of above for Home button
                left = right - zoom #make view to be towards the end of readings
                window['position_slider'].update(range=(zoom,max_time)) #Update the slider on the bottom of the graph
                window['position_slider'].update(value=max_time) #Set slider to right side of graph
                Update_Graph_View()
            
            #Clear the search boxes
            elif event == 'charge_filter_clear':
                window['charge_search'].update(value='')
                window['temp_search'].update(value='')
                window['date_search'].update(value='')
                
            #Searching to filter results
            elif event == 'charge_filter':
                window['old_recording_list'].update(values=RC.get_charges(path,values['charge_search'],values['temp_search'],values['date_search']))
            
            
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SETTINGS SCREEN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        elif active_screen == 'settings_screen':
            
            #Return to main screen
            if event == "Cancel":
                window["main_screen"].select()
                window['goto_main'].update(visible=False)
                window['Title'].update(visible=True)
                active_screen = 'main_screen'
                
            #Prevent invalid characters in the interval box
            elif event == 'interval' and values['interval'] and values['interval'][-1] not in ('0123456789'):
                window['interval'].update(values['interval'][:-1])
            
            #Prevent invalid characters in the temperature box
            elif event == 'temp' and values['temp'] and values['temp'][-1] not in ('0123456789'):
                window['temp'].update(values['temp'][:-1])
                
            #Prevent invalid characters in the max records box
            elif event == 'maxRecords' and values['maxRecords'] and values['maxRecords'][-1] not in ('0123456789'):
                window['maxRecords'].update(values['maxRecords'][:-1])
                
            #Enable/disable email alerts, and inform user
            elif event == 'enable_email_alerts':
                if window['enable_email_alerts'].get_text() == 'Disable Emails':
                    window['enable_email_alerts'].update('Enable Emails')
                    Popup_Window("You have disabled alert emails. They will NOT be sent.")
                else:
                    window['enable_email_alerts'].update('Disable Emails')
                    Popup_Window("You have enabled alert emails. They WILL be sent.")
                
            #Verify and then save the settings    
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
                    eAlert = True if window['enable_email_alerts'].get_text() == 'Disable Emails' else False
                    
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
                    Popup_Window('Settings have been changed successfully.')
                    window['goto_main'].update(visible=False)
                    window['Title'].update(visible=True)
                    window["main_screen"].select()
                    active_screen = 'main_screen'
                    
                    
                #ERROR MESSAGES                   
                if not int_exists:
                    Popup_Window('Please input an interval less than 100 minutes')
                
                elif not temp_exists:
                    Popup_Window('Please input a temperature less than 3000°F')
                    
                elif not maxR_exists:
                    Popup_Window('Please input a maximum number of records greater than 100')

    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    #If an error happens, inform the user
    #Obviously I can't catch them all so the common ones have messages while anything else just spits out the error
        
    except Exception as err:
        print(err)
        
        if str(err) == "Missing column provided to 'parse_dates': 'Time'":
            Popup_Window("~~ERR 05~~\nCharge file contains no headers, cannot be read.")
        
        elif str(err) == "Can only use .dt accessor with datetimelike values":
            Popup_Window("~~ERR 06~~\nInvalid date in charge file, cannot be read.")
        
        elif str(err)[:10] == "[Errno 13]":
            sg.popup_timed("~~ERR 07~~\nThe log file is open! Please close it to continue.\nTrying again in 10s.",font=font,keep_on_top=True,non_blocking=True,auto_close_duration=5)
            current_time = datetime.datetime.fromtimestamp(time())
            last_reading_time = current_time - datetime.timedelta(seconds=(int(settings['interval'])*60-10)) #try again in 10s
        
        elif str(err) == "float division by zero":
            Popup_Window("~~ERR 08~~\nCharge file contains no data and cannot be read.\nCopy data from the log file to the charge file.")
        
        elif str(err) == "zero-size array to reduction operation minimum which has no identity":
            Popup_Window("~~ERR 09~~\nCharge cannot be displayed. Not enough data.")
        
        else: #catch all
            Popup_Window("~~ERR 00~~\n" + str(err))
            print('Error on line {}'.format(exc_info()[-1].tb_lineno), type(err).__name__, err)
            
            #~~~Write to the error log file~~~
            with open(path+'Program/Error-Logs.txt','a') as f:
                f.write(current_time.strftime("%d-%b-%y - %I:%M:%S %p") + ': ERR00: Line {} -- '.format(exc_info()[-1].tb_lineno) + str(err)+'\n')


#If the user exits the program, close the window            
window.close()
