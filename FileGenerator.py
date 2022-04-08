import random
from time import time
import datetime
import csv
from time import sleep

currTime = datetime.datetime.fromtimestamp(time()) #used for clock
formTime = currTime.strftime("%d-%b-%y - %I:%M:%S %p")

numList = [19,27,18,25,18,21,35.5,50,75,100,125,150,225,300,350,400,500,600,600,600,550,500,350,200,50,21,25,20,17,21]
header = ['Time','Temp1','Temp2','Temp3','Temp4','Temp5','Temp6']
random.seed(22) #change me
num = random.uniform(0.7,1.3)
count = 0

with open('.\\Charges\\16226 -- 0600 -- 08-Apr-22.csv','w',newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for thing in numList:
        tList = [0,0,0,0,0,0,0]
        currTime = datetime.datetime.fromtimestamp(time())
        formTime = currTime.strftime("%d-%b-%y %I:%M:%S %p") #used for clock
        for i in range(1,7):
            num = random.uniform(0.7,1.3)
            tList[i] = num*thing
        tList[0] = formTime
        #tList[0] = count
        count += 1
        writer.writerow(tList)
        sleep(0.25)
        