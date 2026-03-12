#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "Motog73";
const char* password = "81225273";

const char* potholeUrl = "http://10.151.128.45:5000/api/pothole";
const char* liveUrl = "http://10.151.128.45:5000/api/live";
const char* deviceId = "ESP32_VEHICLE_1";

const int trigPin = 1;
const int echoPin = 2;
const int buzzerPin = 4;

const float NORMAL_ROAD_DISTANCE_CM = 12.0;
const float POTHOLE_DEPTH_THRESHOLD_CM = 1;
const int REQUIRED_CONSECUTIVE_READINGS = 3;
const unsigned long SENSOR_TIMEOUT = 30000;

int consecutivePotholeReads = 0;
unsigned long lastReadingTime = 0;
unsigned long lastLiveUpdateTime = 0;
const int READ_INTERVAL_MS = 100;
const int LIVE_UPDATE_INTERVAL_MS = 1000;

void setup() {
  Serial.begin(115200);
  
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);
  
  connectToWiFi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }

  if (millis() - lastReadingTime >= READ_INTERVAL_MS) {
    lastReadingTime = millis();
    
    float distanceCm = readDistance();
    
    if (distanceCm > 0) {
      Serial.print("Distance: ");
      Serial.print(distanceCm);
      Serial.println(" cm");
      
      detectPothole(distanceCm);
      
      if (millis() - lastLiveUpdateTime >= LIVE_UPDATE_INTERVAL_MS) {
        lastLiveUpdateTime = millis();
        sendLiveDistance(distanceCm);
      }
    }
  }
}

float readDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  long duration = pulseIn(echoPin, HIGH, SENSOR_TIMEOUT);
  
  if (duration == 0) {
    Serial.println("Sensor timeout!");
    return 0;
  }
  
  float distance = (duration * 0.0343) / 2.0;
  
  return distance;
}

void detectPothole(float measuredDistance) {
  if (measuredDistance > (NORMAL_ROAD_DISTANCE_CM + POTHOLE_DEPTH_THRESHOLD_CM)) {
    consecutivePotholeReads++;
    Serial.print("Abnormal depth detected. Count: ");
    Serial.println(consecutivePotholeReads);
    
    if (consecutivePotholeReads >= REQUIRED_CONSECUTIVE_READINGS) {
      Serial.println(">>> POTHOLE CONFIRMED <<<");
      
      digitalWrite(buzzerPin, HIGH);
      
      float depthDifference = measuredDistance - NORMAL_ROAD_DISTANCE_CM;
      
      sendDetectionData(depthDifference);
      
      delay(500);
      digitalWrite(buzzerPin, LOW);
      
      consecutivePotholeReads = 0;
      
      delay(1500); 
    }
  } else {
    consecutivePotholeReads = 0;
  }
}

void sendLiveDistance(float currentDistance) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(liveUrl);
    http.addHeader("Content-Type", "application/json");
    
    String payload = "{\"device_id\":\"" + String(deviceId) + "\", \"distance_cm\":" + String(currentDistance) + "}";
    
    int httpResponseCode = http.POST(payload);
    http.end();
  }
}

void sendDetectionData(float depthDelta) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    http.begin(potholeUrl);
    http.addHeader("Content-Type", "application/json");
    
    String payload = "{\"device_id\":\"" + String(deviceId) + "\", \"depth_cm\":" + String(depthDelta) + ", \"status\":\"detected\"}";
    
    Serial.println("Sending data to server: " + payload);
    
    int httpResponseCode = http.POST(payload);
    
    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      String response = http.getString();
      Serial.println(response);
    } else {
      Serial.print("Error sending HTTP request: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
  } else {
    Serial.println("WiFi Disconnected. Cannot send data.");
  }
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi network: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("");
    Serial.println("WiFi connection failed.");
  }
}
