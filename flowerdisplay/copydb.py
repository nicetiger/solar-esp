# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 19:44:49 2018

Database Migration


@author: Stefan Michel
"""
import pymysql.cursors
import json
import re

def strtofloat(s):
    try:
        matchObj =re.match(r"(\d*\.\d*)", s)
        if matchObj is not None:
            return float(matchObj.group(1))
        else:
            return None
    except TypeError:
       return None
       
with open('settings.json') as json_data_file:
    settings = json.load(json_data_file)
print(settings)

conn1 = pymysql.connect(
        host=settings["mysql"]["host"],
        port=settings["mysql"]["port"],
        user=settings["mysql"]["user"],
        password=settings["mysql"]["password"],
        db=settings["mysql"]["database"],
        charset='utf8mb4')
cursor1 = conn1.cursor()

#cursor1.execute("CREATE DATABASE sensors;")

cursor1.execute("SELECT str_to_date(date,'%Y-%m-%d %H:%i:%s') as date,p,temp,hum,analog FROM data;")
cursor1.close()
conn1.close()

conn2 = pymysql.connect(
        host=settings["mysql"]["host"],
        port=settings["mysql"]["port"],
        user=settings["mysql"]["user"],
        password=settings["mysql"]["password"],
        db="sensors",
        charset='utf8mb4')
cursor2 = conn2.cursor()

cursor2.execute("CREATE TABLE IF NOT EXISTS data (sensorId INTEGER UNSIGNED, \
                                                  date       DATETIME, \
                                                  temp       FLOAT, \
                                                  pressure   FLOAT, \
                                                  altitude   FLOAT, \
                                                  humidity   FLOAT, \
                                                  voltage    FLOAT, \
                                                  brightness FLOAT, \
                                                  PRIMARY KEY (sensorId,date));")
rows = cursor1.fetchall()
 
for row in rows:
    row2=(
    str(row[0]),
    strtofloat(row[1]),
    strtofloat(row[2]),
    strtofloat(row[3]),
    strtofloat(row[4]))
    print(row2)
    cursor2.execute('REPLACE INTO data (sensorId,date,pressure,temp,humidity,voltage) VALUES (1,%s, %s, %s, %s, %s);',row2)

cursor2.close()
conn2.commit()
conn2.close()