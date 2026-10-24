# ESP32 monitoring firmware

Hardware: four-inch 320x480 ESP32-WROOM-32E board, photographed layout matching LCDWIKI E32R40T; DHT11 on GPIO32. Manufacturer pin reference: https://www.lcdwiki.com/4.0inch_ESP32-32E_Display

## Features

Temperature and display-only humidity every 30 seconds; unchanged three-field API contract; null/error on temperature failure; separate HTTP worker; Wi-Fi reconnection; UK clock; Home/History/Connection pages; changed-field rendering to reduce flicker. History holds approximately 60 minutes of temperature samples in RAM and resets after reboot. Humidity is stored locally in the sample buffer but is not plotted or sent to the API.

## Arduino setup

1. Install esp32 by Espressif Systems, Adafruit DHT sensor library, Adafruit Unified Sensor, ArduinoJson 7 and TFT_eSPI by Bodmer.
2. Keep every file in foodsave_monitor together and open foodsave_monitor.ino.
3. Copy config.example.h to config.h; configure private Wi-Fi settings, MONITOR_DHT_PIN 32, API URL and token. config_defaults.h supplies missing values safely. Never commit config.h.
4. Copy TFT_eSPI_Setup_E32R40T.h into the library User_Setups directory. Select it from TFT_eSPI/User_Setup_Select.h instead of the previous setup. Do not include it only from the sketch: the library is compiled separately.
5. Select ESP32 Dev Module and the actual serial COM port. Arduino Nano ESP32 is a different target and must not be used for this board.
6. Verify, then Upload. Serial Monitor uses 115200 baud.

Display is enabled in display_options.h for the already exercised board profile. Calibration is still disabled. Preserve any known-good local touch settings rather than replacing them with placeholders.

## DHT11 wiring

With power disconnected, connect sensor + to header 3V3, OUT to IO32 and - to GND. Leave IO25 unused. These use the I2C header as general GPIO; no I2C peripheral may use GPIO32 simultaneously. Follow the board labels, not wire colours. The photographed module has produced temperature and humidity readings at 3.3V. Do not pull ESP32 data to 5V.

## Local server

Run monitoring/esp32_receiver.py with --host 0.0.0.0 on the PC. Use the PC LAN IPv4 in MONITOR_API_URL, for example http://192.168.1.100:5001/api/temperatures, and set MONITOR_ALLOW_LOCAL_HTTP true for the trusted local demonstration network. Supply the same privately configured token to receiver and device. No real credentials are included here.

HTTPS requires MONITOR_ROOT_CA; certificate verification is not bypassed. FIX4 Serial startup prints firmware version, HTTP enablement and URL scheme/length without credentials. Diagnostic statuses distinguish disabled HTTP, missing HTTPS CA, invalid scheme, failed HTTP initialisation, rejection and no response.

## Touch and validation

Until calibrated, use Serial h=Home, g=History, c=Connection. Run TFT_eSPI's Touch_calibrate example with the same display rotation, copy its five values into MONITOR_TOUCH_CALIBRATION and enable MONITOR_TOUCH_CALIBRATED. Then test all three tabs on the physical panel. No calibration values are invented.

A photograph supplied by Costel shows physical temperature, humidity, connected Wi-Fi, local time and Accepted from the standalone receiver. Current exact source plus final build configuration has not been compared byte-for-byte with the uploaded firmware. The assistant has not compiled this source using the ESP32 toolchain. Hardware fault/recovery tests, graph and touch acceptance and Flask/MySQL integration remain pending. See docs/monitoring-hardware-status.md.

Six host Python tests cover the simulator and standalone receiver, not firmware hardware or database persistence. Earlier UI mock tests are not equivalent to an ESP32 build.
