# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 19:44:49 2018

@author: Stefan Michel
"""
import pymysql.cursors
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import json
import math

with open('settings.json') as json_data_file:
    settings = json.load(json_data_file)
print(settings)

conn = pymysql.connect(
        host=settings["mysql"]["host"],
        port=settings["mysql"]["port"],
        user=settings["mysql"]["user"],
        password=settings["mysql"]["password"],
        db=settings["mysql"]["database"],
        charset='utf8mb4')
cursor = conn.cursor()

df = pd.read_sql_query("SELECT date,pressure,temp,humidity,voltage FROM data", conn, index_col=["date"],parse_dates=["date"])

df['pressure']=df['pressure'].interpolate(method='nearest')
df['temp']    =df['temp']    .interpolate(method='nearest')
df['humidity']=df['humidity'].interpolate(method='nearest')
df['voltage'] =df['voltage'] .interpolate(method='nearest')

def norm_pressure(p,t):
    
   # Die vom Deutschen Wetterdienst empfohlene Reduktionsformel
   # https://de.wikipedia.org/wiki/Barometrische_H%C3%B6henformel

    h=settings["station"]["height"] # Hoehe Nuernberg
    
    M=0.02896   # mittlere molare Masse der Atmosphärengase (in kg mol^−1 )
    g=9.807     # die Schwerebeschleunigung (in s^-2)
    R=8.314     # die universelle Gaskonstante (in J K^−1 mol^−1)
    #t=15       # Hüttentemperatur (in °C)
    T=t+273.15  # die absolute Temperatur (in K)
    a=0.0065    # vertikaler Temperaturgradient (in K/m)
    f=(M*g/(R*(T+a*h/2)))*h
    
    return p*math.exp(f)

#create new column
df['pressure_norm']=df['pressure']

#fill new column
for index, row in df.iterrows():
    row['pressure_norm']=norm_pressure(row['pressure'],row['temp'])

print(df)


#df.plot(x='date',y='temp')
#df.plot(x='date',y='hum')
#df.plot(x='date',y='analog')
print("plot1")
ax=df.plot(y=['pressure','pressure_norm','voltage','temp','humidity'],secondary_y=['pressure','pressure_norm'],figsize=[8,5])
dStart=pd.Timestamp.now()- pd.Timedelta(days=1)
dEnd=pd.Timestamp.now()
ax.set_xlim(dStart, dEnd)
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0,24,24)))
ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H-%M'))
ax.xaxis.set_tick_params(which='minor', bottom = 'on')
ax.xaxis.grid(True, which='minor', linestyle='-', linewidth=0.25)
ax.xaxis.grid(True, which='major', linestyle='-', linewidth=1)
for tick in ax.get_xaxis().get_major_ticks():
    tick.set_pad(10)
ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
ax.yaxis.set_tick_params(which='minor', left = 'on')
ax.yaxis.grid(True, which='minor', linestyle='-', linewidth=0.25)
ax.yaxis.grid(True, which='major', linestyle='-', linewidth=1)

print("plot2")
ax=df.plot(y=['pressure','pressure_norm','voltage','temp','humidity'],secondary_y=['pressure','pressure_norm'],figsize=[8,5])
dStart=pd.Timestamp.now()- pd.Timedelta(days=7)
dEnd=pd.Timestamp.now()
ax.set_xlim(dStart, dEnd)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,6)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H'))
ax.xaxis.set_tick_params(which='minor', bottom = 'on')
ax.xaxis.grid(True, which='minor', linestyle='-', linewidth=0.25)
ax.xaxis.grid(True, which='major', linestyle='-', linewidth=1)
for tick in ax.get_xaxis().get_major_ticks():
    tick.set_pad(10)
ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
ax.yaxis.set_tick_params(which='minor', left = 'on')
ax.yaxis.grid(True, which='minor', linestyle='-', linewidth=0.25)
ax.yaxis.grid(True, which='major', linestyle='-', linewidth=1)





print("closing")
cursor.close()
conn.close()
print("done.")
              