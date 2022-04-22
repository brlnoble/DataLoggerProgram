# DataLoggerProgram

After the Honeywell Minitrend GR paperless data recorder stopped working, my manager tasked me with creating one from scratch.
A new unit can cost well over $10,000 so I had a chance to save the company thousands if done right.

The goal for this project was to create a simple data logger to record and graph temperature of our stress annealing furnace.
Using an Arduino Uno and Python, I hope to complete this in as simple a manner as possible to ensure ease of repairability for after I complete my internship.

## General Goals
- [X] Read data from thermocouples (using six MAX6675 K-type thermocouple amplifiers)
- [X] Record data at a given interval to a .csv file
- [X] Save settings in a .txt file for access and modification
- [X] Simple and intuitive UI based upon PySimpleGUI
- [X] Allow users to start and stop charge recording to save graphs
- [X] Access and use program from computer
- [X] Email alerts when temperature exceeds a set limit
- [X] Main program for recording, changing settings, and viewing (FullProgram.py)
- [ ] Viewer program only for seeing current readouts and past charges (ViewingProgram.py)



## Program Screens
- [X] Main screen with options to:
  - [X] Change current settings
  - [X] View current readout (numerics) at locations within furnace (see Furnace.png, open side is door)
  - [X] View current readout button (graphically)
  - [X] Open an old graph for viewing
- [X] Settings menu to change parameters
  - [X] Recording interval step (minutes between data points)
  - [X] High temperature warning (to alert user)
  - [X] Change log file location
  - [X] Change maximum records saved in log file
- [X] Graphical view of current readout
  - [X] Live update graph
  - [X] Allow user to record a charge (input charge number)
  - [X] Interactive menu to change view and return home
  - [X] Allow user to scroll through data
  - [X] Show readout of selected data
 
## Current Main Screen
Reading as normal

<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/PicMainScreen-14-04-22.jpg" width="800">
Error reading data

<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/PicMainScreenErr-14-04-22.jpg" width="800">

## Current Settings Screen
<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/PicSettingsScreen-14-04-22.jpg" width="800">

## Current Logging Screen
<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/PicLoggingScreen-08-04-22.jpg" width="800">
<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/PicLoggingScreenRecord-11-04-22.jpg" width="800">

## Current Charge Screen
<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/PicChargeScreen-08-04-22.jpg" width="400"> 
<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/PicLogScreen-08-04-22.jpg" width="800">

## Error Handling
- [X] Serial communication:
  - [X] Notify user if no Arduino is connected on the selected port
  - [X] Notify if unable to send signal to Arduino
  - [X] Notify if unable to receive signal from Arduino
- [X] Inform user if log file is open and cannot be written to
- [X] Charge cannot be viewed because of missing data
- [ ] Thermocouples not reading values, returning NaN
