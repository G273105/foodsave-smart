# Monitoring

Costel owns the temperature sender, simulator and physical ESP32 integration.

## Agreed message format

Send to `POST /api/temperatures` every 30 seconds with `Content-Type: application/json` and `Authorization: Bearer <DEVICE_TOKEN>`.

Normal reading:
```json
{"id":"esp32-01","temperature":4.6,"sensor_status":"ok"}
```

Sensor error:
```json
{"id":"esp32-01","temperature":null,"sensor_status":"error"}
```

Temperature is in Celsius. The backend records the time of receipt. The simulator uses `simulator-01`; it does not claim to provide physical measurements.

## Simulator: Windows PowerShell

Requires Python 3.11 or later; no extra packages are needed.

From the repository root:
```powershell
python monitoring/simulate.py --dry-run
python monitoring/simulate.py --sensor-error --dry-run
$env:TEMPERATURE_API_URL = "http://127.0.0.1:5000/api/temperatures"
$env:DEVICE_TOKEN = "<token configured privately on the backend>"
python monitoring/simulate.py --once
python monitoring/simulate.py --sensor-error --once
python monitoring/simulate.py
```

Replace the placeholder with the backend token locally. Do not share or commit it. Stop continuous sending with Ctrl+C. The simulator reports HTTP rejection and checks that the acknowledgement matches its payload. It retries connection failures after 30 seconds in continuous mode; it does not queue old readings.

The URL above works only when Flask runs on the same computer. For an ESP32, use the Flask computer's LAN IP address, not localhost. Never transmit tokens through an untrusted plain HTTP network.

## Current backend dependency

At review time, the backend exists in PR #3 at commit `9030a66bf2f9717e4f3236436211e681e762291c`, not main. Check out that branch separately to run it; the monitoring branch does not include backend code.

Install its requirements and configure DEVICE_TOKEN before starting Flask. For a local simulator, run `python backend/app.py`. For a trusted LAN hardware demo, Laurentiu must arrange LAN access. One development-only command is:
```powershell
python -m flask --app backend/app.py run --host 0.0.0.0 --port 5000
```

Do not enable debug mode for LAN testing. Allow the port only on the intended private network.

PR #3 currently:
- Accepts both identifiers, but only simulator-01 changes fridge status.
- Provides GET /api/fridge/status, not GET /api/temperatures/latest.
- Keeps data in memory; restart loses readings.
- Does not detect stale readings.
- Uses provisional SAFE/HOLD labels. These are demo classifications, not food-safety certification.

Agree with Laurentiu how to select esp32-01 for the hardware demonstration. Device-to-location and batch mapping remains unconfirmed.

## Tests
```powershell
python -m unittest discover -s monitoring -p "test_*.py" -v
```

The automated sender tests verify JSON, the HTTP path, token header and rejection handling against a local test listener. They do not prove SQLite persistence, dashboard display or physical sensor operation.

## Physical hardware: pending information

Confirm the exact ESP32 board and sensor model before writing sensor-specific firmware or wiring instructions. Record the selected GPIO, power supply and sensor connections after checking the hardware documentation.

## Status

Simulator implemented. Physical firmware and hardware validation remain pending. Record integration evidence separately from automated sender checks.
