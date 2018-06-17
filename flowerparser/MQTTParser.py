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

cursor.execute("CREATE TABLE IF NOT EXISTS data(date CHAR(20) UNIQUE, \
                                                temp     VARCHAR(20), \
                                                pressure VARCHAR(20), \
                                                altitude VARCHAR(20), \
                                                humidity VARCHAR(20), \
                                                analog   VARCHAR(20));")
db.commit()

def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("sensor/#")

def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        aMsg=msg.topic.split("/")
        sTopic=aMsg[0]
        iSensorId=aMsg[1]
        sParameter=aMsg[2]

        now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S");
        try:
            cursor.execute("INSERT IGNORE INTO data(date) VALUES('%s');" % now)
            if sParameter == "Temp":
                cursor.execute("UPDATE data set temp = '%s' where date = '%s';" % (msg.payload.decode('UTF-8'),now))
            if sParameter == "Pressure":
                cursor.execute("UPDATE data set pressure = '%s' where date = '%s';" % (msg.payload.decode('UTF-8'),now))
            if sParameter == "Altitude":
                cursor.execute("UPDATE data set altitude = '%s' where date = '%s';" % (msg.payload.decode('UTF-8'),now))
            if sParameter == "Humidity":
                cursor.execute("UPDATE data set humidity = '%s' where date = '%s';" % (msg.payload.decode('UTF-8'),now))
            if sParameter == "Analog":
                cursor.execute("UPDATE data set analog = '%s' where date = '%s';" % (msg.payload.decode('UTF-8'),now))
        except (IntegrityError)  as e:
            print('sqlite error: ', e.args[0])
        db.commit()

cursor.execute("SELECT * FROM data;")

rows = cursor.fetchall()

for row in rows:
    print(row)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()

db.close()
