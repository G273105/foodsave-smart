# FoodSave Smart monitoring — Costel

Components: simulate.py (synthetic data), esp32_receiver.py (standalone local receiver), and firmware/foodsave_monitor (physical ESP32+DHT11 monitor). Simulator and physical identifiers remain distinct.

## Local device receiver on Windows

Run from this directory:
```powershell
$env:DEVICE_TOKEN = "local-demo-only"
python .\esp32_receiver.py --host 0.0.0.0
```
Use the computer's LAN IPv4 in the ESP32 URL, for example http://192.168.1.100:5001/api/temperatures. ESP32 and PC must be mutually reachable; permit TCP 5001 only as appropriate for the private local network. Do not use 127.0.0.1 as the ESP32 destination. The receiver stores readings in memory only and is separate from the Flask/MySQL backend.

Readback: http://127.0.0.1:5001/api/fridge/status on the PC. Physical readings appear under esp32-01. Stop the simulator when demonstrating the physical device. Ctrl+C stops the receiver.

## Simulator

In a second PowerShell window:
```powershell
$env:DEVICE_TOKEN = "local-demo-only"
$env:TEMPERATURE_API_URL = "http://127.0.0.1:5001/api/temperatures"
python .\simulate.py --once
python .\simulate.py --sensor-error --once
```
Without --once the simulator repeats every 30 seconds. Simulated data uses simulator-01 and must not be relabelled as physical evidence.

## Tests

From repository root:
```powershell
python -m unittest discover -s monitoring -p "test_*.py"
```
The receiver integration tests import local_receiver.py, the canonical implementation; esp32_receiver.py is a thin launch wrapper with the same CLI.

verify_backend.py targets the earlier Flask-only integration and is retained for traceability. Review/adapt it with Laurentiu before use against the current MySQL-backed application; it is not evidence of current MySQL acceptance.

Firmware setup and hardware test checklist: firmware/README.md and ../docs/monitoring-hardware-status.md. API handoff: ../docs/monitoring-handoff.md.

Never commit config.h, Wi-Fi passwords, real tokens or database credentials.
## Online integration evidence — 29 October 2026

The physical ESP32 monitor communicates with the deployed Flask API over HTTPS.

The photographs show:
- The ESP32 and DHT11 hardware, with the Connection page reporting certificate verification and HTTP 201 acceptance.
- A matching temperature of 24.5°C on the physical device and the website.
- Separate physical ESP32 and simulator readings.

### Evidence files

- [ESP32 and DHT11 hardware](evidence/ESP32-DHT11.jpeg)
- [Server API screenshot](evidence/server%20api.png)
- [Physical device and website](evidence/WEBSERVER-ESP32.jpeg)

### API endpoints

- Send readings: `POST https://foodsave-smart.onrender.com/api/temperatures`
- Read latest readings: `GET https://foodsave-smart.onrender.com/api/fridge/status`
- Service health: `GET https://foodsave-smart.onrender.com/api/health`

Physical readings use `esp32-01`. Synthetic readings use `simulator-01`.
Humidity remains on the local display.
.......................................................................................................................................................................................
