
# FoodSave Smart — IoT API Contract

## Backend
Framework: Python Flask
Development port: 5000

## Temperature endpoint
POST /api/temperatures

Headers:
Authorization: Bearer dev-test-token
Content-Type: application/json

## Simulator example
{
  "id": "simulator-01",
  "temperature": 4.6,
  "sensor_status": "ok"
}

## ESP32 example
{
  "id": "esp32-01",
  "temperature": 4.6,
  "sensor_status": "ok"
}

## Rules
- Send readings every 30 seconds.
- Temperature must be a JSON number.
- When the sensor fails, send:
  "temperature": null
  "sensor_status": "error"
- Only the active device controls fridge status.
- Initially the active device is simulator-01.
- Safe test range: 0 to 5 degrees Celsius.
- Outside this range: HOLD.
- Invalid token: HTTP 401.
- Invalid JSON or values: HTTP 400.
- Accepted reading: HTTP 201.

## Status endpoint
GET /api/fridge/status

Possible status values:
UNKNOWN
SAFE
HOLD

## Current limitations
- Data is stored in memory, not SQLite.
- No automatic detection of missing readings yet.
- No automatic switching between devices yet.
- No real reservation blocking yet.
- Temperature limits are provisional.

## Integration
Costel should implement both simulator and ESP32
using this JSON format.

The backend is currently running locally.
127.0.0.1 refers to the computer running Flask.

The token shown here is for local development only.
A private token must be configured before deployment.
