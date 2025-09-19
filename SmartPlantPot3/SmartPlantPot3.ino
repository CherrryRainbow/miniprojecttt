#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11
#define SOIL_PIN 0
#define PUMP_PIN 10

const char* ssid = "TP-Link_ACAC";
const char* password = "49352061";
const char* serverUrl = "https://cherry-miniproject.onrender.com";

DHT dht(DHTPIN, DHTTYPE);

bool pumpState = false;
unsigned long lastSend = 0;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  pinMode(PUMP_PIN, OUTPUT);
  dht.begin();
  int i = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println(i++);
  }
}

void loop() {
  //millis() - lastSend > 5000 && 
  if (millis() - lastSend > 5000 && WiFi.status() == WL_CONNECTED) {
    lastSend = millis();

    float h = dht.readHumidity();
    float t = dht.readTemperature();
    float soil = analogRead(SOIL_PIN)/40.95;
    Serial.println(h);
    Serial.println(t);
    Serial.println(soil);
    HTTPClient http;
    http.begin(String(serverUrl) + "/data");
    http.addHeader("Content-Type", "application/json");
    String payload = "{\"temperature\":" + String(t) + 
                     ",\"humidity\":" + String(h) + 
                     ",\"soil\":" + String(soil) + "}";
    int code = http.POST(payload);
    http.end();

    // Check pump command
    HTTPClient http2;
    http2.begin(String(serverUrl) + "/pump_status");
    int code2 = http2.GET();
    if (code2 == 200) {
      String res = http2.getString();
      if (res.indexOf("on") > 0) {
        digitalWrite(PUMP_PIN, HIGH);
        pumpState = true;
      } else {
        digitalWrite(PUMP_PIN, LOW);
        pumpState = false;
      }
      Serial.println(pumpState);
    }
    http2.end();
  }
}
