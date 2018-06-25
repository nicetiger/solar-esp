#!/usr/local/bin/python3
"""
Created on Sun Jun  3 19:44:49 2018

@author: Stefan Michel, Phil
"""
import paho.mqtt.client as mqtt
import pymysql
from pymysql.err import IntegrityError,ProgrammingError,InternalError
import datetime
import json


####################
#Configuration part:
####################

listSensorGroups = [[0,1,2,3],[4,5,6,7]]                  #Defines which sensors are attached to the same ESP
dtConsiderConnectedSeconds=datetime.timedelta(seconds=10) #Defines the maximum time between messages before considering it a new update

print ("MQTTParser starts")

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

listLastUpdate = [datetime.datetime.now()]*(len(listSensorGroups)+1)

#Return the number of the sensor group that the given sensor is part of
def getSensorGroup ( iSensorId ):
    idx=0
    while idx < len(listSensorGroups):
        idxSensor=0
        while idxSensor < len(listSensorGroups[idx]):
            if listSensorGroups[idx][idxSensor] == iSensorId:
                return idx
            idxSensor+=1
        idx+=1
    return len(listSensorGroups)

#Return the time that should be used in the table for a given sensorId
#this will update the listLastUpdate if the sensor was not updated within dtConsiderConnectedSeconds
def calcUpdateTime ( iSensorId ):
    now=datetime.datetime.now()
    idxSensor=getSensorGroup(iSensorId)
    if listLastUpdate[idxSensor]+dtConsiderConnectedSeconds < now:
        listLastUpdate[idxSensor]=now
    return listLastUpdate[idxSensor]

#cursor.execute("DROP TABLE data;")
#db.commit()

cursor.execute("CREATE TABLE IF NOT EXISTS data (sensorId INTEGER UNSIGNED, \
                                                 date       DATETIME, \
                                                 temp       FLOAT, \
                                                 pressure   FLOAT, \
                                                 altitude   FLOAT, \
                                                 humidity   FLOAT, \
                                                 voltage    FLOAT, \
                                                 brightness FLOAT, \
                                                 PRIMARY KEY (sensorId,date));")
conn.commit()

def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("sensor/#")

def on_message(client, userdata, msg):
        aMsg=msg.topic.split("/")
        sTopic=aMsg[0]
        iSensorId=int(aMsg[1])
        sParameter=aMsg[2]

        now=calcUpdateTime(iSensorId).strftime('%Y-%m-%d %H:%M:%S')
        try:
            cursor.execute("INSERT IGNORE INTO data(sensorId, date) VALUES('%d','%s');" % (iSensorId, now))
            if sParameter == "Temp":
                print(msg.topic + " " + str(msg.payload))
                cursor.execute("UPDATE data set temp = %f       WHERE sensorId = '%d' AND date = '%s';" % (float(msg.payload.decode('UTF-8').rstrip("C")), iSensorId, now))
            if sParameter == "Pressure":
                print(msg.topic + " " + str(msg.payload))
                cursor.execute("UPDATE data set pressure = %f   WHERE sensorId = '%d' AND date = '%s';" % (float(msg.payload.decode('UTF-8').rstrip("hPa")), iSensorId, now))
            if sParameter == "Altitude":
                print(msg.topic + " " + str(msg.payload))
                cursor.execute("UPDATE data set altitude = %f   WHERE sensorId = '%d' AND date = '%s';" % (float(msg.payload.decode('UTF-8').rstrip("m")), iSensorId, now))
            if sParameter == "Humidity":
                print(msg.topic + " " + str(msg.payload))
                cursor.execute("UPDATE data set humidity = %f   WHERE sensorId = '%d' AND date = '%s';" % (float(msg.payload.decode('UTF-8').rstrip("%")), iSensorId, now))
            if sParameter == "Voltage":
                print(msg.topic + " " + str(msg.payload))
                cursor.execute("UPDATE data set voltage = %f     WHERE sensorId = '%d' AND date = '%s';" % (float(msg.payload.decode('UTF-8').rstrip("mV")), iSensorId, now))
            if sParameter == "Brightness":
                print(msg.topic + " " + str(msg.payload))
                cursor.execute("UPDATE data set brightness = %f WHERE sensorId = '%d' AND date = '%s';" % (float(msg.payload.decode('UTF-8').rstrip("cd")), iSensorId, now))
        except (IntegrityError)  as e:
            print('sql error: ', e.args[0])
        except (ValueError) as e:
            print('Failed to parse: ', e.args[0])
        except (InternalError) as e:
            print('sql error: ', e.args[0])
        conn.commit()

cursor.execute("SELECT date,UNIX_TIMESTAMP(date) AS udate,temp,pressure,humidity,voltage,brightness FROM data ORDER BY udate DESC,sensorId limit 10;")

rows = cursor.fetchall()

for row in rows:
    print(row)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()

conn.close()
