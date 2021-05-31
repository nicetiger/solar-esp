// (c) 2018 Stefan Michel
// for Wemos D1 mini pro
// Flash Size: 16M
// CPU Freq: 80MHz
// Upload Speed: 921600
//
// dependency to:
// https://github.com/Seeed-Studio/Grove_BME280 Version 1.0.2
// https://github.com/knolleary/pubsubclient Version 2.6.0
//

#include "config.h"

#include <Seeed_BME280.h>
#include <WiFiManager.h>
#include <Wire.h>
#include <PubSubClient.h>
#include <PubSubClientTools.h>

BME280 bme280;

#define LED D4

WiFiClient espClient;

String s="";

os_timer_t myTimer;

void timerCallback(void *pArg) {
  // something strange happened
  Serial.print("Timer was triggered. Restarting...");
  delay(5);
  ESP.restart();
} 

void setup() {
  Serial.begin(74880);
  delay(500);

  pinMode(LED,OUTPUT);

  //timer to go to sleep again if something hangs
  os_timer_setfn(&myTimer, timerCallback, NULL);
  os_timer_arm(&myTimer, 30000, true);

  //Manual Wifi
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PSK);
  int counter = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    counter++;
    if (counter>60)
    {
      //cannot connect after 30sec
      ESP.deepSleep(1000000*60);
    }
  }
  WiFi.persistent(true);

  Serial.println("setup bme280");
  //hangs without i2c device
  if(!bme280.init()){
     Serial.println("Device error!");
  }
  Serial.println("done");
}

void writeToMqtt(float temp,float p,float altitude,float humidity,float analog)
{
  PubSubClient client(MQTT_SERVER, 1883, espClient);
  PubSubClientTools mqtt(client);
  
  while (!client.connected()) 
  {
    Serial.print(s+"Connecting to MQTT: "+MQTT_SERVER+" ... ");
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
    } else {
      Serial.println(s+"failed, rc="+client.state());
    }
  }
  mqtt.publish(s+"sensor/"+SENSOR_ID+"/Temp", s+temp);
  mqtt.publish(s+"sensor/"+SENSOR_ID+"/Pressure", s+p);
  mqtt.publish(s+"sensor/"+SENSOR_ID+"/Altitute", s+altitude);
  mqtt.publish(s+"sensor/"+SENSOR_ID+"/Humidity", s+humidity);
  mqtt.publish(s+"sensor/"+SENSOR_ID+"/Voltage", s+analog);
  delay(100);
  client.disconnect();
}

void loop() {
  digitalWrite(LED,HIGH);
  delay(250);
  digitalWrite(LED,LOW);
  delay(250);

  //get and print temperatures
  float temp = bme280.getTemperature();
  Serial.print("Temp: ");
  Serial.print(temp);
  Serial.println("C");

  
  float pressure = bme280.getPressure(); // pressure in Pa
  float p = pressure/100.0 ; // pressure in hPa
  Serial.print("Pressure: ");
  Serial.print(p);
  Serial.println("hPa");


  //get and print altitude data
  float altitude = bme280.calcAltitude(pressure);
  Serial.print("Altitude: ");
  Serial.print(altitude);
  Serial.println("m");


  float humidity = bme280.getHumidity();
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println("%");

  float analog=analogRead(A0)/500.0*4.6; 
  Serial.print("Sensor: ");
  Serial.print(analog);
  Serial.println("V");

  writeToMqtt(temp,p,altitude,humidity,analog);

  Serial.println("INFO: Closing the Wifi connection");
  WiFi.disconnect();

  // this needs D0 - RST
  ESP.deepSleep(1000000*60);

  //never reach this line; reboot after deepSleep 
  //delay(1000);
}
