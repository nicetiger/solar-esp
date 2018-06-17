#!/usr/local/bin/python3
"""
Created on Sun Jun  3 19:44:49 2018

@author: Stefan Michel, Phil
"""
import paho.mqtt.client as mqtt
import pymysql
from pymysql.err import IntegrityError,ProgrammingError
import datetime

#db = pymysql.connect(host='127.0.0.1', unix_socket='/run/mysqld/mysqld10.sock', user='flowers', passwd=None, db='mysql')
db = pymysql.connect(host='127.0.0.1', user='flowers', passwd=None, db='flowers')
cursor = db.cursor()

#db = sqlite3.connect("C:\\Users\Stefan\data.mydb")
#cursor = db.cursor()
#cursor.execute("DROP TABLE data;")
#db.commit()

cursor.execute("CREATE TABLE IF NOT EXISTS data (sensorId INTEGER UNSIGNED, \
                                                 date       DATETIME, \
                                                 temp       FLOAT, \
                                                 pressure   FLOAT, \
                                                 altitude   FLOAT, \
                                                 humidity   FLOAT, \
                                                 analog     FLOAT, \
                                                 brightness FLOAT, \
                                                 PRIMARY KEY (sensorId,date));")
db.commit()

def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("sensor/#")

def on_message(client, userdata, msg):
        aMsg=msg.topic.split("/")
        sTopic=aMsg[0]
        iSensorId=int(aMsg[1])
        sParameter=aMsg[2]

        now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
            if sParameter == "Analog":
                print(msg.topic + " " + str(msg.payload))
                cursor.execute("UPDATE data set analog = %f     WHERE sensorId = '%d' AND date = '%s';" % (float(msg.payload.decode('UTF-8').rstrip("mV")), iSensorId, now))
            if sParameter == "Brightness":
                print(msg.topic + " " + str(msg.payload))
                cursor.execute("UPDATE data set brightness = %f WHERE sensorId = '%d' AND date = '%s';" % (float(msg.payload.decode('UTF-8').rstrip("cd")), iSensorId, now))
        except (IntegrityError)  as e:
            print('sqlite error: ', e.args[0])
        db.commit()

cursor.execute("SELECT * FROM data ORDER BY date,sensorId;")

rows = cursor.fetchall()

for row in rows:
    print(row)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()

db.close()
