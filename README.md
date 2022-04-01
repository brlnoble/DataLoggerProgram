# DataLoggerProgram

After the Honeywell Minitrend GR paperless data recorder stopped working, my manager tasked me with creating one from scratch.
A new unit can cost well over $10,000 so I had a chance to save the company thousands if done right.

The goal for this project was to create a simple data logger to record and graph temperature of our stress annealing furnace.
Using a Raspberry Pi and Python, I hope to complete this in as simple a manner as possible to ensure ease of repairability for after I complete my internship.

- [ ] Read data from thermocouples
- [ ] Record data at a given interval to a .csv file
- [ ] Save settings in a .txt file for access and modification
- [ ] Simple and intuitive UI based upon PySimpleGUI
- [ ] Allow users to start and stop charge recording to save graphs
- [ ] Access and use program from computer



------------PROGRAM SCREENS------------
- [ ] Main screen with options to:
  - [ ] Change current settings
  - [ ] View current readout (numerics)
  - [ ] View current readout (graphically)
  - [ ] Open an old graph for viewing
- [ ] Settings menu to change parameters
  - [ ] Recording interval step (minutes between data points)
  - [ ] High temperature warning (to alert user)
- [ ] Graphical view of current readout
  - [ ] Live update graph
  - [ ] Allow user to record a charge (input charge number)
  - [ ] Interactive menu to change view and return home
