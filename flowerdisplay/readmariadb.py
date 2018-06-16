# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 19:44:49 2018

@author: Stefan Michel
"""
import pymysql.cursors
import pandas as pd
import matplotlib.pyplot as plt
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

df = pd.read_sql_query("SELECT str_to_date(date,'%Y-%m-%d %H:%i:%s') as date,p,temp,hum,analog FROM data", conn, index_col=["date"],parse_dates=["date"])

df['p']=df['p'].str.rstrip('hPa')
df['temp']=df['temp'].str.rstrip('C')
df['hum']=df['hum'].str.rstrip('%')
df['analog']=df['analog'].str.rstrip('V')

#df['date']=pd.to_datetime(df['date'])
df['p']     =pd.to_numeric(df['p'])     .interpolate(method='nearest')
df['temp']  =pd.to_numeric(df['temp'])  .interpolate(method='nearest')
df['hum']   =pd.to_numeric(df['hum'])   .interpolate(method='nearest')
df['analog']=pd.to_numeric(df['analog']).interpolate(method='nearest')

def norm_pressure(p,t):
    
   # Die vom Deutschen Wetterdienst empfohlene Reduktionsformel
   # https://de.wikipedia.org/wiki/Barometrische_H%C3%B6henformel

    h=355 # Hoehe Nuernberg
    
    M=0.02896   # mittlere molare Masse der Atmosphärengase (in kg mol^−1 )
    g=9.807     # die Schwerebeschleunigung (in s^-2)
    R=8.314     # die universelle Gaskonstante (in J K^−1 mol^−1)
    #t=15       # Hüttentemperatur (in °C)
    T=t+273.15  # die absolute Temperatur (in K)
    a=0.0065    # vertikaler Temperaturgradient (in K/m)
    f=(M*g/(R*(T+a*h/2)))*h
    
    return p*math.exp(f)

#create new column
df['p2']=df['p']

#fill new column
for index, row in df.iterrows():
    row['p2']=norm_pressure(row['p'],row['temp'])
    
#df['p'] = df['p'].map(lambda x: x.rstrip('hPa'))


print(df)

#df.plot(x='date',y='temp')
#df.plot(x='date',y='hum')
#df.plot(x='date',y='analog')
ax=df.plot(y=['p','p2','analog','temp','hum'],secondary_y=['p','p2'],figsize=[5,3])
ax.set_xlim(pd.Timestamp.now()- pd.Timedelta(days=1), pd.Timestamp.now())
ax=df.plot(y=['p','p2','analog','temp','hum'],secondary_y=['p','p2'],figsize=[5,3])
ax.set_xlim(pd.Timestamp.now()- pd.Timedelta(days=7), pd.Timestamp.now())

cursor.close()
conn.close()
                            