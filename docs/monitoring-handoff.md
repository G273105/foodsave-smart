# Monitoring integration handoff — Team Green

Date: 12 October 2026. Owner: Costel. Mapping and access decisions still require team agreement.

## Sender contract confirmed by Costel

- POST /api/temperatures, JSON, every 30 seconds.
- Physical identifier: esp32-01. Simulator identifier: simulator-01.
- Fields: id (string), temperature (Celsius number or null), sensor_status (ok or error).
- ok requires a finite numeric temperature; error requires null.
- Authorization: Bearer <DEVICE_TOKEN>, configured locally and shared privately.
- The backend records the receipt time. No RSSI, humidity or sender timestamp is added.

## Normal reading

```json
{"id":"simulator-01","temperature":4.6,"sensor_status":"ok"}
```

## Sensor error

```json
{"id":"simulator-01","temperature":null,"sensor_status":"error"}
```

For physical readings, replace only the identifier with esp32-01.

## Information required from Laurentiu

1. Reachable API URL for the selected test environment and private token configuration.
2. LAN access when testing physical ESP32: Flask must listen on the LAN interface, with debug disabled. A remote colleague's localhost cannot be reached from Costel's device.
3. Agreement on choosing the active device. PR #3 hard-codes simulator-01; esp32-01 readings currently do not change fridge status.
4. Confirmation of device-to-storage-location mapping, with Alex. Proposed location: Fridge 1. The backend associates batches; the sender does not send batch IDs.
5. A stale-reading rule, proposed as 90 seconds without a new accepted reading. Offline/unknown must not retain a misleading current SAFE label.
6. SQLite integration and confirmation of persistence. Current HTTP 201 confirms only in-memory acceptance.

No CORS change is needed for a Python simulator or ESP32 HTTP client. Browser frontend origin configuration is a separate concern.

## Verified against PR #3

Backend source: 9030a66bf2f9717e4f3236436211e681e762291c.
Executed locally through a real HTTP listener using Flask 3.1.3 and python-dotenv 1.2.4. No physical hardware or remote server was used.

Eight checks passed: health, simulator readback, receipt timestamp, invalid-token rejection, sensor-error acceptance, physical-payload acceptance, unknown-device rejection and missing-normal-temperature rejection. The simulator's real send_reading function also received and verified an HTTP 201 acknowledgement.

One check failed: error status with numeric temperature returned HTTP 201 instead of HTTP 400.

Suggested backend correction, before storing the reading:

```python
if sensor_status == "error" and temperature is not None:
    return jsonify({"error": "Temperature must be null when the sensor reports an error"}), 400
```

This is a proposed correction for Laurentiu to review; his branch has not been modified.

The SAFE/HOLD thresholds are provisional demonstration rules, not food-safety certification. SQLite, stale detection, screen operation and dashboard integration remain unverified.

## Repeat the integration check

In a checkout containing the PR #3 backend and monitoring files:

```powershell
python -m pip install -r backend/requirements.txt
python monitoring/verify_backend.py --backend backend/app.py
```

The checker uses a temporary random token and an isolated local server. Its changes are confined to process memory. Exit code 1 reports a contract failure.

## Hardware scope

DHT11 confirmed. Four-inch 320x480 resistive-touch ESP32 board selected; board revision, GPIO mapping and display/touch drivers remain unconfirmed. Firmware pin assignments must wait for that information. The simulator is independent of it.
