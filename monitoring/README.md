# Monitoring

This directory contains the temperature simulator, ESP32 firmware and setup instructions for FoodSave Smart.

## Planned features
- Read temperature from a sensor connected to an ESP32.
- Send a reading to the Flask API every 30 seconds.
- Report sensor errors.
- Provide a simulator for testing without physical hardware.

## API integration
Endpoint: POST /api/temperatures

Headers:
- Content-Type: application/json
- Authorization: Bearer <DEVICE_TOKEN>

Normal reading:
```json
{
  "id": "esp32-01",
  "temperature": 4.6,
  "sensor_status": "ok"
}
Sensor error:
{
  "id": "esp32-01",
  "temperature": null,
  "sensor_status": "error"
}
Temperature is expressed in degrees Celsius. The backend records the time of receipt.
The proposed simulator identifier is simulator-01. The backend should distinguish simulated readings from physical sensor readings.
Device-to-storage-location mapping remains subject to team agreement.
Configuration
Configure the API URL and device token locally.
Do not commit device tokens or Wi-Fi credentials to GitHub.
Validation
- Verify that normal readings are accepted and stored.
- Verify that sensor errors are recorded without a false temperature value.
- Check that readings appear on the dashboard.
- Check that transmission resumes after reconnection.
Status
Planned. Implementation has not started.
