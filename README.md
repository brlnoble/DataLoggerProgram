# DataLoggerProgram

After the Honeywell Minitrend GR paperless data recorder stopped working, my manager tasked me with creating one from scratch.
A new unit can cost well over $10,000 so I had a chance to save the company thousands if done right.

The goal for this project was to create a simple data logger to record and graph temperature of our stress annealing furnace.
Using an Raspberry Pi and Python, I hope to complete this in as simple a manner as possible to ensure ease of repairability for after I complete my internship.

## General Goals
- [X] Read data from thermocouples (using five MAX6675 K-type thermocouple amplifiers)
- [X] Record data at a given interval to a .csv file
- [X] Save settings in JSON files for access and modification
- [X] Simple and intuitive computer program UI based upon [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI)
- [X] Allow users to start and stop charge recording to save graphs
- [X] Access and use program from computer
- [X] Email alerts when temperature exceeds a set limit


## Program Screens
- [X] Main screen with options to:
  - [X] Change current settings
  - [X] View current readout (numerics) at locations within furnace (see Furnace.png, open side is door)
  - [X] View current readout (graphically)
  - [X] Open an old graph for viewing
  - [X] Open error logs
- [X] Settings menu to change parameters
  - [X] Recording interval step (minutes between data points)
  - [X] High temperature warning (to alert user)
  - [X] Change log file location
  - [X] Change maximum records saved in log file
  - [X] Email settings
  - [X] Manually calibrate readings with an offset
- [X] Graphical view of current readout
  - [X] Live update graph
  - [X] Allow user to record a charge (input charge number)
  - [X] Interactive menu to change view and return home
  - [X] Allow user to scroll through data
  - [X] Show readout of selected data
  - [X] Save plot as an image
- [X] Selection screen for previous charges
  - [X] List past charges
  - [X] Ability to search/filter charges
  - [X] When selected, pulls up data for viewing in the logging screen
- [X] Website to allow at home monitoring
  - [X] Data is posted to the website everytime a reading is made
  - [X] Simple and easy to read interface
  - [X] Found here: https://uds-furnace.github.io/View/
 
## Current Main Screen
<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/Images/PicMainScreen-16-06-22.jpg" width="900">

## Current Settings Screen
<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/Images/PicSettingsScreen-16-06-22.jpg" width="900">

## Current Logging Screen
<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/Images/ViewScreenGIFnew.gif" width="900">

## Current Charge Screen
<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/Images/PicChargeSelectScreen-11-08-22.jpg" width="900"> 
<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/Images/PicChargeViewScreen-28-06-22.jpg" width="900">

## Photo of the Installed Unit
<img src="https://github.com/brlnoble/DataLoggerProgram/blob/main/Images/Unit.jpg" width="900">
