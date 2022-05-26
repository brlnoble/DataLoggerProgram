import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

#Initialize pin numbers for TC inputs
TC1 = 16
TC2 = 18
TC3 = 22
TC4 = 32
TC6 = 36
tcList = [TC1, TC2, TC3, TC4, TC6] #array of inputs

#Initialize pin for amplifer controls
CS = 29
SCK = 31

GPIO.setup(tcList, GPIO.IN) #Setup inputs
GPIO.setup([CS,SCK], GPIO.OUT) #Setup outputs

#Array for outputs
tcRead  =[0,0,0,0,0]

def readTC(TC):
	read = 0
	GPIO.output(SCK,GPIO.HIGH) #See if this fixes things
	GPIO.output(CS,GPIO.LOW)	

	for j in range(15,-1,-1):
		GPIO.output(SCK,GPIO.LOW)
		sleep(0.01)
		read |= (GPIO.input(TC) << j)
		GPIO.output(SCK,GPIO.HIGH)
		sleep(0.01)

	GPIO.output(CS,GPIO.HIGH)
	return read


#Only checking if the one thermocouple works so far
reading = readTC(TC4)
print('Reading: ' + str(reading))
reading >>= 3
print('R-Shift 3: ' + str(reading))
reading *= 0.25
print('1/4 R: ' + str(reading))
reading *= 9/5
reading += 32
print(f'Fahrenheit: {reading:.2f}')

GPIO.cleanup()

