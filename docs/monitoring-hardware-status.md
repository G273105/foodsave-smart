# Monitoring hardware status — 16 October 2026

Owner: Costel. Scope: ESP32 monitoring, local display and device-to-API communication.

## Evidence supplied by the operator

The photograph taken on 15 October at approximately 23:28 shows the physical display reporting 24.1 C, 65.0 % RH, Sensor OK, Wi-Fi Connected, Server Accepted and Last accepted 23:28:04. The device clock displays 15/10/2026 23:28:29. This demonstrates a physical reading and an API acknowledgement reported by the firmware. It does not prove integration with Laurentiu's Flask/MySQL backend.

The firmware was compiled and uploaded by the operator in Arduino IDE. Earlier screenshots exposed an incorrect Arduino Nano ESP32 target; the intended target is ESP32 Dev Module for this ESP32-WROOM-32E board. Exact successful build output for the final source revision has not been retained here. No complete ESP32 toolchain build has been performed by the assistant in this environment.

## Current component

- Four-inch 320x480 resistive display; photographed layout matches LCDWIKI E32R40T.
- ST7796S LCD and XPT2046 touch profile, based on manufacturer documentation.
- DHT11 data: GPIO32, repurposing the unused I2C SDA header.
- Wiring by connector labels: 3V3 to sensor +; IO32 to OUT; GND to -; IO25 unused. Colours are cable-specific, not a general standard.
- Home: temperature, humidity, UK date/time and connection states.
- History: temperature only, approximately 60 minutes in RAM; reset clears history.
- Humidity is display-only and retained in RAM samples, not added to the API.
- Small changed-field sprites reduce screen clearing; the physical flicker result still requires explicit acceptance.
- Touch remains disabled until calibrated; Serial h/g/c supports page navigation.

Manufacturer: https://www.lcdwiki.com/4.0inch_ESP32-32E_Display

## Acceptance still required

| Check | Current evidence |
| --- | --- |
| Physical temperature and humidity | Visible in supplied photograph |
| Wi-Fi and clock | Visible in supplied photograph |
| Local API acknowledgement | Accepted visible; server log/readback still needed |
| Touch calibration and navigation | Pending |
| History with real readings and sensor-error gaps | Pending |
| Sensor disconnect and null/error submission | Pending on hardware |
| Wi-Fi loss and recovery | Pending controlled test |
| Receiver outage and recovery | Pending controlled test |
| Incorrect token rejection | Pending physical-device test |
| Reboot and resumed operation | Pending controlled test |
| Flask integration and MySQL persistence | Pending joint test |

Tests of the simulator must not be described as physical ESP32 tests. Record firmware revision, date, expected and actual results for every additional test.
