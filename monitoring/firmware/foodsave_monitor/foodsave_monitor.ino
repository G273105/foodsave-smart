// FoodSave Smart: DHT11 monitoring and optional touchscreen UI.
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <time.h>
#if __has_include("config.h")
#include "config.h"
#endif
#include "config_defaults.h"
#include "display_options.h"
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>

constexpr uint32_t READING_INTERVAL_MS = 30000;
constexpr size_t HISTORY_CAPACITY = 121;
constexpr const char *DEVICE_ID = "esp32-01";

struct Sample {
  uint32_t uptimeMs;
  time_t measuredAt;
  float temperature;
  bool valid;
  float humidity;
  bool humidityValid;
};

// Future touchscreen rendering reads this state; errors are gaps in the graph.
struct MonitorState {
  float temperature = NAN;
  float humidity = NAN;
  const char *sensorStatus = "Not configured";
  const char *serverStatus = "Not sent";
  int lastHttpCode = 0;
  bool acceptedOnce = false;
  uint32_t lastAcceptedMs = 0;
  time_t lastAcceptedAt = 0;
  Sample history[HISTORY_CAPACITY];
  size_t nextSample = 0;
  size_t sampleCount = 0;
} monitor;

DHT *sensor = nullptr;
uint32_t lastReadingMs = 0;
uint32_t lastReconnectMs = 0;
struct SendResult { const char *status; int code; bool accepted; time_t at; uint32_t ms; };
QueueHandle_t resultQueue;
float outgoingTemperature;
bool outgoingValid;
volatile bool sending = false;
void uiBegin();
void uiTick();

time_t clockTime() {
  time_t now = time(nullptr);
  return now >= 1700000000 ? now : 0;
}

void printState() {
  Serial.printf("Sensor: %s | Temperature: ", monitor.sensorStatus);
  if (isfinite(monitor.temperature)) Serial.print(monitor.temperature, 1);
  else Serial.print("--");
  Serial.printf(" C | Wi-Fi: %s | Server: %s | HTTP: %d\n",
                WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected",
                monitor.serverStatus, monitor.lastHttpCode);
  Serial.print("Humidity: ");
  if (isfinite(monitor.humidity)) Serial.print(monitor.humidity, 1);
  else Serial.print("--");
  Serial.println(" % RH");
  if (!clockTime()) Serial.println("Time not synchronised");
  if (monitor.acceptedOnce)
    Serial.printf("Last accepted: %lu seconds ago\n",
                  static_cast<unsigned long>((millis() - monitor.lastAcceptedMs) / 1000));
}

void sendReading(bool valid) {
  SendResult result = {"Not sent", 0, false, 0, 0};
  if (WiFi.status() != WL_CONNECTED) {
    result.status = "No connection";
    xQueueOverwrite(resultQueue, &result);
    return;
  }
  if (!strlen(MONITOR_API_URL) || !strlen(MONITOR_DEVICE_TOKEN)) {
    result.status = "Not configured";
    xQueueOverwrite(resultQueue, &result);
    return;
  }
  JsonDocument payload;
  payload["id"] = DEVICE_ID;
  if (valid) payload["temperature"] = outgoingTemperature;
  else payload["temperature"] = nullptr;
  payload["sensor_status"] = valid ? "ok" : "error";
  String body;
  serializeJson(payload, body);

  WiFiClient plainClient;
  WiFiClientSecure secureClient;
  HTTPClient http;
  String url = MONITOR_API_URL;
  url.trim();
  bool started = false;
  if (url.startsWith("http://")) {
    if (!MONITOR_ALLOW_LOCAL_HTTP) {
      result.status = "HTTP disabled in config";
      xQueueOverwrite(resultQueue, &result);
      return;
    }
    started = http.begin(plainClient, url);
  } else if (url.startsWith("https://")) {
    if (!strlen(MONITOR_ROOT_CA)) {
      result.status = "HTTPS CA missing";
      xQueueOverwrite(resultQueue, &result);
      return;
    }
    secureClient.setCACert(MONITOR_ROOT_CA);
    started = http.begin(secureClient, url);
  } else {
    result.status = "URL must start http(s)";
    xQueueOverwrite(resultQueue, &result);
    return;
  }
  if (!started) {
    result.status = "HTTP begin failed";
    xQueueOverwrite(resultQueue, &result);
    return;
  }
  http.setConnectTimeout(3000);
  http.setTimeout(5000);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", String("Bearer ") + MONITOR_DEVICE_TOKEN);
  result.status = "Sending";
  int code = http.POST(body);
  result.code = code;
  if (code == 201) {
    JsonDocument response;
    DeserializationError error = deserializeJson(response, http.getString());
    JsonVariant reading = response["reading"];
    bool matches = !error && reading["id"].is<const char *>() &&
                   String(reading["id"].as<const char *>()) == DEVICE_ID &&
                   reading["sensor_status"].is<const char *>() &&
                   String(reading["sensor_status"].as<const char *>()) == (valid ? "ok" : "error");
    if (valid)
      matches = matches && reading["temperature"].is<float>() &&
                fabsf(reading["temperature"].as<float>() - outgoingTemperature) < 0.01f;
    else
      matches = matches && reading["temperature"].isNull();
    if (matches) {
      result.status = "Accepted";
      result.accepted = true;
      result.ms = millis();
      result.at = clockTime();
    } else result.status = "Invalid acknowledgement";
  } else result.status = code > 0 ? "Rejected" : "No response";
  http.end();
  xQueueOverwrite(resultQueue, &result);
}

void networkWorker(void *) {
  sendReading(outgoingValid);
  vTaskDelete(nullptr);
}

void takeReading() {
  monitor.temperature = sensor->readTemperature();
  monitor.humidity = sensor->readHumidity();
  if (!isfinite(monitor.humidity) || monitor.humidity < 0 || monitor.humidity > 100)
    monitor.humidity = NAN;
  bool valid = isfinite(monitor.temperature);
  monitor.sensorStatus = valid ? "OK" : "Error";
  monitor.history[monitor.nextSample] = {millis(), clockTime(), monitor.temperature, valid, monitor.humidity, isfinite(monitor.humidity)};
  monitor.nextSample = (monitor.nextSample + 1) % HISTORY_CAPACITY;
  if (monitor.sampleCount < HISTORY_CAPACITY) ++monitor.sampleCount;
  if (!sending) {
    outgoingTemperature = monitor.temperature;
    outgoingValid = valid;
    sending = true;
    monitor.serverStatus = "Sending";
    if (xTaskCreate(networkWorker, "monitor-http", 12288, nullptr, 1, nullptr) != pdPASS) {
      sending = false;
      monitor.serverStatus = "Worker unavailable";
    }
  }
  printState();
}

void setup() {
  Serial.begin(115200);
  delay(250);
  Serial.println("Firmware: HUMIDITY-FIX4-DIAGNOSTICS");
  Serial.printf("Local HTTP allowed: %s\n", MONITOR_ALLOW_LOCAL_HTTP ? "YES" : "NO");
  String configuredUrl = MONITOR_API_URL;
  configuredUrl.trim();
  Serial.printf("URL scheme: %s | URL length: %u | DHT GPIO: %d\n",
    configuredUrl.startsWith("http://") ? "HTTP" :
    configuredUrl.startsWith("https://") ? "HTTPS" : "INVALID",
    static_cast<unsigned>(configuredUrl.length()), MONITOR_DHT_PIN);
  Serial.println("FoodSave Smart monitor — firmware draft");
  resultQueue = xQueueCreate(1, sizeof(SendResult));
  uiBegin();
  setenv("TZ", MONITOR_TIMEZONE, 1);
  tzset();
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  if (strlen(MONITOR_WIFI_SSID)) WiFi.begin(MONITOR_WIFI_SSID, MONITOR_WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  setenv("TZ", MONITOR_TIMEZONE, 1);
  tzset();
  if (!resultQueue) { monitor.serverStatus = "Queue unavailable"; return; }
  if (MONITOR_DHT_PIN < 0 || MONITOR_DHT_PIN > 33) {
    Serial.println("Confirm the board GPIO before configuring the DHT11. No readings will be sent.");
    return;
  }
  sensor = new DHT(MONITOR_DHT_PIN, DHT11);
  sensor->begin();
  // Allow sensor start-up time; subsequent readings are 30 seconds apart.
  lastReadingMs = millis() - READING_INTERVAL_MS + 2000;
}

void loop() {
  SendResult result;
  if (resultQueue && xQueueReceive(resultQueue, &result, 0) == pdTRUE) {
    monitor.serverStatus = result.status;
    monitor.lastHttpCode = result.code;
    if (result.accepted) {
      monitor.acceptedOnce = true;
      monitor.lastAcceptedMs = result.ms;
      monitor.lastAcceptedAt = result.at;
    }
    sending = false;
    printState();
  }
  uiTick();
  uint32_t now = millis();
  if (strlen(MONITOR_WIFI_SSID) && WiFi.status() != WL_CONNECTED &&
      now - lastReconnectMs >= 15000) {
    lastReconnectMs = now;
    WiFi.reconnect();
  }
  if (sensor && !sending && now - lastReadingMs >= READING_INTERVAL_MS) {
    lastReadingMs = now;
    takeReading();
  }
  delay(10);
}

#include "monitor_ui.h"
