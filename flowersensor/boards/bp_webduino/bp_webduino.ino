// (c) 2018 Stefan Michel, Phil
// for BananaPi Webduino / WittyCloud
// Flash Size: 4M
// CPU Freq: 80MHz
// Upload Speed: 115200
//
// https://github.com/knolleary/pubsubclient Version 2.6.0
//

#include "config.h"

#include <WiFiManager.h>
#include <Wire.h>
#include <PubSubClient.h>
#include <PubSubClientTools.h>

#define PIN_LED_RED    15
#define PIN_LED_BLUE   13
#define PIN_LED_GREEN  12
#define PIN_LED_WAKEUP 16

ADC_MODE(ADC_VCC);

#define NUM_SENSORS    4

WiFiClient espClient;
WiFiEventHandler stationConnectedHandler;
WiFiEventHandler stationDisconnectedHandler;
WiFiEventHandler stationGotIPHandler;
PubSubClient      msqttThinClient(MQTT_SERVER, 1883, espClient);
PubSubClientTools mqttFullClient(msqttThinClient);

struct MeasurementPoint
{
  uint32_t uTemperature;
  uint32_t uHumidity;
  uint32_t uBatteryVoltage;
};
MeasurementPoint measSensors[NUM_SENSORS];


String s="";

void setup()
{
  Serial.begin(115200);

  pinMode(PIN_LED_RED, OUTPUT);
  pinMode(PIN_LED_BLUE, OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  
  analogWrite(PIN_LED_RED, 0x01);
  analogWrite(PIN_LED_BLUE, 0x0);
  analogWrite(PIN_LED_GREEN, 0x0);

  Serial.println("Booting");

  stationConnectedHandler=WiFi.onStationModeConnected(&onStationConnected);
  stationDisconnectedHandler=WiFi.onStationModeDisconnected(&onStationDisconnected);
  stationGotIPHandler=WiFi.onStationModeGotIP(&onStationModeGotIP);

  WiFi.persistent(true);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.setAutoConnect(false);
  yield();

  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("Connecting");
    WiFi.begin(WIFI_SSID, WIFI_PSK);  
    yield();  
  }
 
  Serial.println("done");
}

void sendSensorToMqtt(unsigned uSensorId, struct MeasurementPoint &mp)
{
  String s;

  mqttFullClient.publish(s+"sensor/"+uSensorId+"/Temp",       s+mp.uTemperature+"C");
  mqttFullClient.publish(s+"sensor/"+uSensorId+"/Pressure",   s+"0hPa");
  mqttFullClient.publish(s+"sensor/"+uSensorId+"/Altitude",   s+"0m");
  mqttFullClient.publish(s+"sensor/"+uSensorId+"/Humidity",   s+mp.uHumidity+"%");
  mqttFullClient.publish(s+"sensor/"+uSensorId+"/Brightness", s+"0cd");
  mqttFullClient.publish(s+"sensor/"+uSensorId+"/Analog",     s+mp.uBatteryVoltage+"mV");
  yield();
}

void loop()
{
  uint32_t uVcc;  

  /*Vcc is shared for all sensors, only take it once*/
  uVcc=ESP.getVcc();


  for(uint8_t uX=0; uX<NUM_SENSORS ;++uX)
  {
    analogWrite(PIN_LED_BLUE, 0x01);

    delay(500); /*Let power settle*/
    analogWrite(PIN_LED_BLUE, 0x80);

    measSensors[uX].uTemperature=0;
    measSensors[uX].uHumidity=0;
    measSensors[uX].uBatteryVoltage=uVcc;


    analogWrite(PIN_LED_BLUE, 0x01);

    Serial.print("Sensor ");
    Serial.print(uX);
    Serial.print(" Temperature: ");
    Serial.print(measSensors[uX].uTemperature);
    Serial.print(" Humidity: ");
    Serial.print(measSensors[uX].uHumidity);
    Serial.print(" Battery: ");
    Serial.println(measSensors[uX].uBatteryVoltage);

    delay(10);/*Wait for full PIN down*/
  }

  /*Wait for WiFi if not yet ready*/
  uint32_t uStart=millis();
  while (WiFi.status() != WL_CONNECTED)
  {
    if(uStart+15*1000 < millis() )
    {
      Serial.print(uStart+15*1000);
      Serial.print(" ");
      Serial.print(millis());
      Serial.println(" Failed to connect, giving up.");
      break;
    }
    delay(500);
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.print(s+"Connecting to MQTT: "+MQTT_SERVER+" ... ");
    if (msqttThinClient.connect("ESP8266Client"))
    {
      Serial.println("connected");
      Serial.println("Sending data");
      for(uint8_t uX=0; uX<NUM_SENSORS ;++uX)
      {
          sendSensorToMqtt(uX, measSensors[uX]);
      }
    }
    else
    {
      Serial.println(s+"failed, rc="+msqttThinClient.state());
    }
  }
  
  msqttThinClient.disconnect();
  
  Serial.println("INFO: Closing the Wifi connection");
  WiFi.disconnect();

  analogWrite(PIN_LED_RED, 0x0);
  analogWrite(PIN_LED_BLUE, 0x0);
  analogWrite(PIN_LED_RED, 0x0);

  // this needs D0 - RST
  ESP.deepSleep(5*60*1000*1000);

  //never reach this line; reboot after deepSleep 
  delay(1000);
}
/*************************************/
/*           Wifi Handlers           */
/*************************************/
void onStationConnected(const WiFiEventStationModeConnected& evt)
{
  Serial.println("Station connected.");
  analogWrite(PIN_LED_RED, 0x0);
}

void onStationDisconnected(const WiFiEventStationModeDisconnected& evt)
{
  Serial.println("Station disconnected.");
  digitalWrite(PIN_LED_RED, HIGH);
  digitalWrite(PIN_LED_GREEN, LOW);
  analogWrite(PIN_LED_RED, 0x01);
  analogWrite(PIN_LED_GREEN, 0x0);
}

void onStationModeGotIP(const WiFiEventStationModeGotIP& evt)
{
  String s;
  
  Serial.println("Got an IP.");
  analogWrite(PIN_LED_GREEN, 0x02);
}
