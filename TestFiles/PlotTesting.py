import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt


# MATPLOTLIB CODE HERE
plt.figure(1)
fig = plt.gcf()
DPI = fig.get_dpi()
# ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
fig.set_size_inches(400 * 2 / float(DPI), 400 / float(DPI))
# -------------------------------

df = pd.read_csv('9timeTest.csv',parse_dates=['Time'], 
            dayfirst=True)
x = df.Time

dates = list(range(0,len(x)))
print(dates)
print(x)

right = max(x) #most recent reading
#maxTime = right #global storage of above for Home button
left = 60 - 10 #make view to be towards the end of readings

#thermocouple 1
y = df.Temp1
plt.plot(x,y,linewidth=2,marker='o',label='TC1',color='#FF0000') 
#thermocouple 2
y = df.Temp2
plt.plot(x,y,linewidth=2,marker='o',label='TC2',color='#FFAA00')
#thermocouple 3
y = df.Temp3
plt.plot(x,y,linewidth=2,marker='o',label='TC3',color='#365BB0')
#thermocouple 4
y = df.Temp4
plt.plot(x,y,linewidth=2,marker='o',label='TC4',color='#444')
#thermocouple 5
y = df.Temp5
plt.plot(x,y,linewidth=2,marker='o',label='TC5',color='#00B366')
#thermocouple 6
y = df.Temp6
plt.plot(x,y,linewidth=2,marker='o',label='TC6',color='#AA00AA') 

plt.xlabel('Time')
plt.ylabel('Temperature')
#plt.xlim([x[len(x-1)],x[len(x)-10]]) #initial limits X
plt.ylim([0, 700]) #initial limits Y
plt.grid()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%I:%M:%S %p')) 
l4 = plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
        mode="expand", borderaxespad=0, ncol=6,frameon=False)

plotDisplay = True
plt.show()
