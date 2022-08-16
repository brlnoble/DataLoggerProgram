#This file is used to simply start the program and record the RPi's address for VNC
import subprocess
from time import time
import datetime
from GeneralCommands import Get_Path

path = Get_Path()+'Program/'

ip = str(subprocess.check_output(['hostname', '-I'])).split(' ')[0].replace("b'", "")
current_time=datetime.datetime.fromtimestamp(time()).strftime("%d %B, %Y - %I:%M:%S %p")

#IP address for the RPi on the local network. Used for VNC viewer connection
with open(path+'RPi-IP.txt','w') as f:
    f.write(current_time+' --- '+ip)

print ('Startup complete.')
print ()
print ('~~~~~ Initializing Recording Program ~~~~~')

#Run the recording program
subprocess.call('sudo python /home/RaspRecord.py',shell=True)

#Shutdown RPi now that recording has finished
#subprocess.call("sudo nohup shutdown -h now", shell=True)
