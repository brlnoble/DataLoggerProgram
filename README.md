# DataLoggerProgram

After the Honeywell Minitrend GR paperless data recorder stopped working, my manager tasked me with creating one from scratch.
A new unit can cost well over $10,000 so I had a chance to save the company thousands if done right.

The goal for this project was to create a simple data logger to record and graph temperature of our stress relief annealing furnace.
Using a Raspberry Pi and Python, I completed this in as simple a manner as possible to ensure ease of repairability for after I complete my internship.

The unit has been successfully working since April 2022, and was completed for about $135 (well below the $10,000 of a commercial unit).

## General Goals
- [X] Read data from furnace thermocouples (using five MAX6675 K-type thermocouple amplifiers)
- [X] Record data at a given interval to a CSV file
- [X] Save settings in JSON files for easy access and modification
- [X] Simple and intuitive computer program UI based upon [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI)
- [X] Allow users to start and stop recording to save graphs
- [X] Access and use program from any computer on the plant network
- [X] Email alerts when temperature exceeds a set limit
- [X] Website for remote monitoring
___

## Program Screens
- [X] Main screen with options to:
  - [X] Change current settings
  - [X] View current readout (numerics) at locations within furnace
  - [X] View current readout (graphically)
  - [X] Open old graphs for viewing
  - [X] Open error logs
- [X] Settings menu to change parameters
  - [X] Recording interval step (minutes between data points)
  - [X] High temperature warning (to alert user)
  - [X] Email settings for alerts
  - [X] Manually calibrate readings with an offset
- [X] Graphical view of current readout
  - [X] Live graph of temperature readings
  - [X] Allow user to record a charge
  - [X] Interactive menu to change view and return 'home'
  - [X] Allow user to scroll through data history
  - [X] Show readout of selected data point
  - [X] Save plot as an image
- [X] Selection screen for previous charges
  - [X] List past charges
  - [X] Ability to search/filter charges
  - [X] When selected, pulls up data for viewing in the logging screen
- [X] Website to allow at home monitoring
  - [X] Data is posted to the website everytime a reading is made
  - [X] Simple and easy to read interface
  - [X] Found here: https://uds-furnace.github.io/View/
 
 ___
 
## Current Main Screen
<img src="https://user-images.githubusercontent.com/51976754/185397725-ff1bd335-63ec-4b3f-bb7b-c8f939374e31.png" width="900">

___

## Current Settings Screen
<img src="https://user-images.githubusercontent.com/51976754/185399754-94980a33-13c2-4598-bb70-f998a02ba25c.png" width="900">
<img src="https://user-images.githubusercontent.com/51976754/185398457-4fe0af09-c73a-4cfb-9b77-5ef2561c58cc.png" width="900">

___

## Current Logging Screen
<img src="https://user-images.githubusercontent.com/51976754/185398038-7673f9f0-9758-4de5-ae78-3c790f87d106.png" width="900">
<img src="https://user-images.githubusercontent.com/51976754/185398762-7e5b0d26-2478-4c2f-8d4e-21b3552f956d.gif" width="900">

___

## Current Charge Screen
<img src="https://user-images.githubusercontent.com/51976754/185398135-4fb30f44-47e3-40e2-a03f-00886319bbaa.png" width="900"> 
<img src="https://user-images.githubusercontent.com/51976754/185398247-b276e90c-2eb3-4c3b-844e-38b44eee320f.png" width="900">

___

## Photo of the Installed Unit
<img src="https://user-images.githubusercontent.com/51976754/185399193-5564c1a7-c0a6-42c3-befb-5af4616fdd23.png" width="900">
