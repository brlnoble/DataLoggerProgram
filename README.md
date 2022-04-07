# DataLoggerProgram

After the Honeywell Minitrend GR paperless data recorder stopped working, my manager tasked me with creating one from scratch.
A new unit can cost well over $10,000 so I had a chance to save the company thousands if done right.

The goal for this project was to create a simple data logger to record and graph temperature of our stress annealing furnace.
Using a Raspberry Pi and Python, I hope to complete this in as simple a manner as possible to ensure ease of repairability for after I complete my internship.

## General Goals
- [ ] Read data from thermocouples
- [ ] Record data at a given interval to a .csv file
- [X] Save settings in a .txt file for access and modification
- [X] Simple and intuitive UI based upon PySimpleGUI
- [ ] Allow users to start and stop charge recording to save graphs
- [X] Access and use program from computer



## Program Screens
- [ ] Main screen with options to:
  - [X] Change current settings
  - [X] View current readout (numerics)
  - [X] View current readout (graphically)
  - [ ] Open an old graph for viewing
- [X] Settings menu to change parameters
  - [X] Recording interval step (minutes between data points)
  - [X] High temperature warning (to alert user)
  - [X] Change log file location
  - [X] Change maximum records saved in log file
- [ ] Graphical view of current readout
  - [X] Live update graph
  - [ ] Allow user to record a charge (input charge number)
  - [X] Interactive menu to change view and return home
  - [X] Allow user to scroll through data
  - [X] Show readout of selected data
 
## Current Main Screen
![Current Main Screen](https://github.com/brlnoble/DataLoggerProgram/blob/main/PicMainScreen-07-04-22.jpg)

## Current Settings Screen
![Current Main Screen](https://github.com/brlnoble/DataLoggerProgram/blob/main/PicSettingsScreen-07-04-22.jpg)

## Current Logging Screen
![Current Log Screen](https://github.com/brlnoble/DataLoggerProgram/blob/main/PicLoggingScreen-07-04-22.jpg)
