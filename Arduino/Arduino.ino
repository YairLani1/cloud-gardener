#include <Adafruit_Sensor.h>
#include <Adafruit_NeoPixel.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <stdlib.h> // Include for atof function

#define PUMP_PIN 3
#define LED_PIN 7
#define FAN_PIN 5
String FAN_Status = "0";
String Pump_Status = "0|0";
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
    Serial.println("Arduino#0 + V2.5");
    Serial.println("Commands:");
    Serial.println("1");
    Serial.println("pump=?(Seconds,Power)");
     Serial.println("pump?");
    Serial.println("2");
    Serial.println("light=?(red|green|blue)(0-255)");
    Serial.println("light?(red|green|blue)");
    Serial.println("3");
    Serial.println("fan=?(Power)");
    Serial.println("fan?");
    Serial.println("4");
    Serial.println("dht?(Celsius|HumidityPercent)");
    Serial.println("5");
    Serial.println("s-temp?");
    Serial.println("6");
    Serial.println("ec?(Volts)");
  }

  if (receivedData.startsWith("light?")) {
    //Serial.println("light is[R,G,B]"+String(red) + " " + String(green) + " " + String(blue));
    Serial.println(String(red) + "|" +String(green) + "|" +String(blue));
  }
  
  if (receivedData.startsWith("light=")) {
    String rgbValues = receivedData.substring(6);  // Get the string after "light="
    rgbValues.trim();  // Remove any extra spaces

    // Find positions of the '|' delimiters
    int firstDelimiter = rgbValues.indexOf('|');
    int secondDelimiter = rgbValues.indexOf('|', firstDelimiter + 1);

    // Extract the individual RGB values as strings
    String redStr = rgbValues.substring(0, firstDelimiter);
    String greenStr = rgbValues.substring(firstDelimiter + 1, secondDelimiter);
    String blueStr = rgbValues.substring(secondDelimiter + 1);

    // Convert the extracted strings to integers
    red = redStr.toInt();
    green = greenStr.toInt();
    blue = blueStr.toInt();

    // Update the LED strip with the specified color
    colorFill(strip.Color(green,red,blue));
    Serial.println("light=" + String(red) + "|" +String(green) + "|" +String(blue));

}

  
  
  if (receivedData.startsWith("pump=")) {
    String data = receivedData.substring(5);
    int commaIndex = data.indexOf('|');
    if (commaIndex != -1) {
      Pump_Status = data.substring(0, commaIndex) +"|"+ data.substring(commaIndex + 1).c_str();
      float duration = atof(data.substring(0, commaIndex).c_str());
      float power = atof(data.substring(commaIndex + 1).c_str());
      analogWrite(PUMP_PIN, power * 255);
      char powerChar[8];  // Adjust size as needed
      char durationChar[8];
      // Use dtostrf to convert float to string with 2 decimal places
      
      dtostrf(power, 6, 2, powerChar);  // 6 is total width, 2 is decimal precision
      dtostrf(duration, 6, 2, durationChar);
      String powerStr = String(powerChar);
      String durationStr = String(durationChar);
      // Print the combined string in one line
      powerStr.trim();
      durationStr.trim();
      
      Serial.println("pump=" + String(durationStr)+"|"+String(powerStr));
      delay(duration * 1000);
      analogWrite(PUMP_PIN, 0);
    }
  }
  
  if (receivedData.startsWith("pump?")) {
    Serial.println(Pump_Status);
    Pump_Status = "0|0";
    
  }
  

  if (receivedData.startsWith("fan=")) {
    String data = receivedData.substring(4);
    float power = atof(data.c_str());
    FAN_Status = data.c_str();
    if (power==0){
      FAN_Status = "0"; 
    }
    char powerChar[8];  // Adjust size as needed
    // Use dtostrf to convert float to string with 2 decimal places
    dtostrf(power, 6, 2, powerChar);  // 6 is total width, 2 is decimal precision
    String powerStr = String(powerChar);
    powerStr.trim();
    analogWrite(FAN_PIN, power * 255);
    Serial.println("fan="+String(powerStr));
    
  }
  
  if (receivedData.startsWith("fan?")) {
    Serial.println(FAN_Status);
  }
    

 




  if (receivedData.startsWith("dht?")) {
    float temperature = dht.readTemperature();
    float humidity= dht.readHumidity();
    // Create buffer arrays to hold the formatted strings
    char temperatureChar[8];  // Adjust size as needed
    char humidityChar[8];
    // Use dtostrf to convert float to string with 2 decimal places
    dtostrf(temperature, 6, 2, temperatureChar);  // 6 is total width, 2 is decimal precision
    dtostrf(humidity, 6, 2, humidityChar);
    String humidityStr = String(humidityChar);
    String temperatureStr = String(temperatureChar);
    // Print the combined string in one line
    humidityStr.trim();
    temperatureStr.trim();
    Serial.println(String(temperatureStr) + "|" + String(humidityStr));
    
  }
  
  if (receivedData.startsWith("ec?")) {
    // Read the analog value from the capacitive soil moisture sensor (YL-69)
    float ArduinoVoltage = 5.0;
    int conductiveValue = analogRead(EC_PIN);
    // Map the sensor value to moisture percentage (adjust the mapping as needed)
    int conductiveprecetage = map(conductiveValue, 0, 1023, 0, 100);
    float conductiveVolts = ArduinoVoltage-conductiveprecetage*ArduinoVoltage/100.0;
    // Print the moisture sensor value and moisture percentage to the serial monitor
    Serial.println(conductiveVolts);

}

  if (receivedData.startsWith("s-temp?")) {
    // Read temperature from DS18B20 sensor
    ds18b20.requestTemperatures();
    float temperatureDS18B20 = ds18b20.getTempCByIndex(0);
    //Serial.print("Soil-T(C): ");
    Serial.println(temperatureDS18B20);
  }
  
  if (receivedData.startsWith("hidroFan=")) {
    Serial.println(String(receivedData));
  }
  

  delay(1000);
}

