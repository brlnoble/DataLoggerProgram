import RPi.GPIO as GPIO
from time import sleep
from time import time
import datetime
import csv

GPIO.setmode(GPIO.BOARD)

#Initialize pin numbers for TC inputs
TC1 = 16
TC2 = 18
TC3 = 22
TC4 = 32
TC5 = 11
TC6 = 36
tcList = [TC1,TC2,TC3,TC4,TC5,TC6] #array of inputs

#Initialize pin for amplifer controls
CS = 29
SCK = 31

GPIO.setup(tcList, GPIO.IN) #Setup inputs
GPIO.setup([CS,SCK], GPIO.OUT) #Setup outputs
GPIO.output(CS,GPIO.HIGH) #start chip select as high

#Array for outputs
tcRead  =['','0','0','0','0','0','0']

#Variables
path ='/diskstation1/share/1 - Mill/DATA/Brandon Stuff/CODE/' 

def readTC(tcList):
	for i in range(0,len(tcList)):
		read = 0
		GPIO.output(SCK,GPIO.HIGH) #See if this fixes things
		GPIO.output(CS,GPIO.LOW)
	 
		for j in range(15,-1,-1):
			GPIO.output(SCK,GPIO.LOW)
			sleep(0.01)
			read |= (GPIO.input(tcList[i]) << j)
			GPIO.output(SCK,GPIO.HIGH)
			sleep(0.01)

		GPIO.output(CS,GPIO.HIGH)

		#Convert to Fahrenheit
		read >>= 5
		read *= 9/5
		read += 32
		tcRead[i+1] = f'{read:.2f}'

currTime=datetime.datetime.fromtimestamp(time()).strftime("%d %B, %Y - %I:%M:%S %p")
tcRead[0] = currTime 
#Check if the thing works lol
readTC(tcList)

print('----- '+currTime+' -----')
for i in range(0,len(tcRead)):
	print(tcRead[i])

#Write to CSV log
with open(path+'OnlineLog.csv','a',newline='') as f:
	writer = csv.writer(f)
	writer.writerow(tcRead)

#Clear the GPIO so they are not in use
GPIO.cleanup()
