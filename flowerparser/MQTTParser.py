#!/usr/local/bin/python3
"""
Created on Sun Jun  3 19:44:49 2018

@author: Stefan Michel
"""
import paho.mqtt.client as mqtt
import pymysql
from pymysql.err import IntegrityError,ProgrammingError
import datetime

db = pymysql.connect(host='127.0.0.1', unix_socket='/run/mysqld/mysqld10.sock', user='TBD', passwd=None, db='mysql')
cursor = db.cursor()

#db = sqlite3.connect("C:\\Users\Stefan\data.mydb")
#cursor = db.cursor()
#cursor.execute("DROP TABLE data;")
#db.commit()


cursor.execute("CREATE TABLE IF NOT EXISTS data(date CHAR(20) UNIQUE,temp VARCHAR(20), p VARCHAR(20), hum VARCHAR(20), analog VARCHAR(20));")
db.commit()

def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("test/#")

def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S");
        try:
            cursor.execute("INSERT IGNORE INTO data(date) VALUES('%s');" % now)
            if msg.topic == "test/Temp":
                cursor.execute("UPDATE data set temp = '%s' where date = '%s';" % (msg.payload.decode('UTF-8'),now))
            if msg.topic == "test/Pressure":
                cursor.execute("UPDATE data set p = '%s' where date = '%s';" % (msg.payload.decode('UTF-8'),now))
            if msg.topic == "test/Analog":
                cursor.execute("UPDATE data set analog = '%s' where date = '%s';" % (msg.payload.decode('UTF-8'),now))
            if msg.topic == "test/Humidity":
                cursor.execute("UPDATE data set hum = '%s' where date = '%s';" % (msg.payload.decode('UTF-8'),now))
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
