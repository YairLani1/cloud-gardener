#include <Adafruit_Sensor.h>
#include <Adafruit_NeoPixel.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <stdlib.h> // Include for atof function

#define PUMP_PIN 3
#define LED_PIN 7
#define FAN_PIN 5
#define DHT_PIN 2  // Change this to the pin where your DHT22 is connected
#define S_TEMP_PIN 4
#define EC_PIN A0

#define LED_COUNT 50

#define RED_flash 255
#define GREEN_flash 255
#define BLUE_flash 255
#define time_flash 5

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
DHT dht(DHT_PIN, DHT22);
OneWire oneWire(S_TEMP_PIN);
DallasTemperature ds18b20(&oneWire);

void setup() {
  Serial.begin(9600);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  strip.begin();
  strip.show();
  dht.begin();
}

void colorFill(uint32_t color) {
  for (int i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, color);
  }
  strip.show();
}

int red = 0;
int green = 0;
int blue = 0;

void loop() {
  String receivedData = "";
  while (Serial.available()) {
    char c = Serial.read();
    receivedData += c;
  }

  if (receivedData.startsWith("id?")) {
    Serial.println("Arduino#0 + V2.3");
    Serial.println("Commands:");
    Serial.println("1");
    Serial.println("pump=?(Seconds,Power)");
    Serial.println("2");
    Serial.println("light=?(0-255)");
    Serial.println("r=?X(0-255)");
    Serial.println("g=?X(0-255)");
    Serial.println("b=?X(0-255)");
    Serial.println("light=flash");
    Serial.println("light?");
    Serial.println("3");
    Serial.println("fan=?(Seconds,Power)");
    Serial.println("4");
    Serial.println("dht?");
    Serial.println("5");
    Serial.println("s-temp?");
    Serial.println("6");
    Serial.println("ec?");
  }

  if (receivedData.startsWith("light?")) {
    //Serial.println("light is[R,G,B]"+String(red) + " " + String(green) + " " + String(blue));
    Serial.println(String(red) + "," +String(green) + "," +String(blue));
  }

  if (receivedData.startsWith("pump=")) {
    String data = receivedData.substring(5);
    int commaIndex = data.indexOf(',');
    if (commaIndex != -1) {
      int duration = data.substring(0, commaIndex).toInt();
      float power = atof(data.substring(commaIndex + 1).c_str());
      analogWrite(PUMP_PIN, power * 255);
      Serial.println("Pump ON for");
      Serial.println(duration);
      delay(duration * 1000);
      analogWrite(PUMP_PIN, 0);
    }
  }

  if (receivedData.startsWith("fan=")) {
    String data = receivedData.substring(4);
    int commaIndex = data.indexOf(',');
    if (commaIndex != -1) {
      int duration = data.substring(0, commaIndex).toInt();
      float power = atof(data.substring(commaIndex + 1).c_str());
      analogWrite(FAN_PIN, power * 255);
      Serial.println("Fan ON for");
      Serial.println(duration);
      delay(duration * 1000);
      analogWrite(FAN_PIN, 0);
    }
  }

  if (receivedData.startsWith("light=")) {
    String durationStr = receivedData.substring(6);
    int duration = durationStr.toInt();
    red = duration;
    blue = duration;
    green = duration;
    Serial.println("light is " + String(red) + " " + String(green) + " " + String(blue));
    colorFill(strip.Color(duration, duration, duration));
  }

  if (receivedData.startsWith("r=")) {
    String durationStr = receivedData.substring(2);
    int duration = durationStr.toInt();
    red = duration;
    Serial.println("red is ");
    Serial.println(duration);
    Serial.println("light is " + String(red) + " " + String(green) + " " + String(blue));
    colorFill(strip.Color(red, green, blue));
  }

  if (receivedData.startsWith("g=")) {
    String durationStr = receivedData.substring(2);
    int duration = durationStr.toInt();
    green = duration;
    Serial.println("green is ");
    Serial.println(duration);
    Serial.println("light is " + String(red) + " " + String(green) + " " + String(blue));
    colorFill(strip.Color(red, green, blue));
  }

  if (receivedData.startsWith("b=")) {
    String durationStr = receivedData.substring(2);
    int duration = durationStr.toInt();
    blue = duration;
    Serial.println("blue is ");
    Serial.println(duration);
    Serial.println("light=" + String(red) + " " + String(green) + " " + String(blue));
    colorFill(strip.Color(red, green, blue));
  }

  if (receivedData.startsWith("light=flash")) {
    colorFill(strip.Color(RED_flash, GREEN_flash, BLUE_flash));
    Serial.println("flash");
    delay(time_flash * 1000);
    colorFill(strip.Color(0, 0, 0));
    Serial.println("light= 0 0 0");
  }

  if (receivedData.startsWith("dht?")) {
    float temperature = dht.readTemperature();
    float humidity= dht.readHumidity();
    
    //Serial.print("Air-T(C): ");
    //Serial.print(temperature);
    //Serial.print(", H(%): ");
    //Serial.println(humidity);
    Serial.print(temperature);
    Serial.print(",");
    Serial.print(humidity);
    Serial.println();
  }
  
  if (receivedData.startsWith("ec?")) {
    // Read the analog value from the capacitive soil moisture sensor (YL-69)
    int moistureValue = analogRead(EC_PIN);

    // Map the sensor value to moisture percentage (adjust the mapping as needed)
    int moisturePercentage = map(moistureValue, 0, 1023, 0, 100);

    // Print the moisture sensor value and moisture percentage to the serial monitor
    Serial.print("Soil-M(V) ");
    Serial.print(moistureValue);
    Serial.print(" \ (%): ");
    Serial.println(moisturePercentage);
}

  if (receivedData.startsWith("s-temp?")) {
    // Read temperature from DS18B20 sensor
    ds18b20.requestTemperatures();
    float temperatureDS18B20 = ds18b20.getTempCByIndex(0);

    Serial.print("Soil-T(C): ");
    Serial.println(temperatureDS18B20);
  }

  delay(1000);
}

