# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 19:44:49 2018

@author: Stefan Michel
"""
import pymysql.cursors
import pandas as pd
import matplotlib.pyplot as plt

conn = pymysql.connect(host='192.168.?.?',
                             port=3307,
                             user='TBD',
                             password=None,
                             db='mysql',
                             charset='utf8mb4')
cursor = conn.cursor()

df = pd.read_sql("SELECT * FROM data", conn)

df['p']=df['p'].str.rstrip('hPa')
df['temp']=df['temp'].str.rstrip('C')
df['hum']=df['hum'].str.rstrip('%')
df['analog']=df['analog'].str.rstrip('V')

df['date']=pd.to_datetime(df['date'])
df['p']   =pd.to_numeric(df['p'])
df['temp']=pd.to_numeric(df['temp'])
df['hum'] =pd.to_numeric(df['hum'])
df['analog']=pd.to_numeric(df['analog'])

#print (df['p'])


#df['p'] = df['p'].map(lambda x: x.rstrip('hPa'))


print(df)

#df.plot(x='date',y='temp')
#df.plot(x='date',y='hum')
#df.plot(x='date',y='analog')
df.plot(x='date',y=['p','analog','temp','hum'],secondary_y='p',figsize=[15,10])

cursor.close()
conn.close()
                            