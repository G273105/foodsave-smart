
import math
import os
from datetime import datetime, timezone

from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)

# Development-only token.
DEVICE_TOKEN = os.getenv("DEVICE_TOKEN")

if not DEVICE_TOKEN:
    raise RuntimeError("DEVICE_TOKEN is not configured")
# Provisional temperature limits for testing.
MIN_SAFE_TEMP = 0.0
MAX_SAFE_TEMP = 5.0

# The simulator initially controls the fridge status.
ACTIVE_DEVICE_ID = "simulator-01"

# Temporary in-memory data.
latest_readings = {}
fridge_status = "UNKNOWN"


@app.get("/api/health")
def health_check():
    return jsonify({
        "status": "ok",
        "project": "FoodSave Smart",
        "message": "Backend is running successfully"
    }), 200


@app.get("/api/fridge/status")
def get_fridge_status():
    return jsonify({
        "location_id": 1,
        "active_device_id": ACTIVE_DEVICE_ID,
        "status": fridge_status,
        "latest_readings": latest_readings
    }), 200


@app.post("/api/temperatures")
def receive_temperature():
    global fridge_status

    # Step 1: Verify the device token.
    authorization = request.headers.get("Authorization", "")

    if authorization != f"Bearer {DEVICE_TOKEN}":
        return jsonify({
            "error": "Unauthorized device"
        }), 401

    # Step 2: Read the incoming JSON.
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON is required"
        }), 400

    device_id = data.get("id")
    temperature = data.get("temperature")
    sensor_status = data.get("sensor_status")

    # Step 3: Validate the device.
    if device_id not in ("simulator-01", "esp32-01"):
        return jsonify({
            "error": "Unknown device ID"
        }), 400

    # Step 4: Validate sensor status.
    if sensor_status not in ("ok", "error"):
        return jsonify({
            "error": "Invalid sensor status"
        }), 400

    # Step 5: Validate temperature.
    if temperature is not None:
        if not isinstance(temperature, (int, float)) or isinstance(temperature, bool):
            return jsonify({
                "error": "Temperature must be a number"
            }), 400

        if not math.isfinite(temperature):
            return jsonify({
                "error": "Temperature must be finite"
            }), 400

        if not -50 <= temperature <= 100:
            return jsonify({
                "error": "Temperature outside valid range"
            }), 400

    if sensor_status == "ok" and temperature is None:
        return jsonify({
            "error": "Temperature is required"
        }), 400

    if sensor_status == "error" and temperature is not None:
        return jsonify({
            "error": "Temperature must be null when sensor status is error"
        }), 400
    
    # Step 6: Store the latest reading.
    reading = {
        "id": device_id,
        "temperature": temperature,
        "sensor_status": sensor_status,
        "received_at": datetime.now(timezone.utc).isoformat()
    }

    latest_readings[device_id] = reading

    # Step 7: Only the active device changes fridge status.
    if device_id == ACTIVE_DEVICE_ID:
        if (
            sensor_status != "ok"
            or temperature is None
            or not MIN_SAFE_TEMP <= temperature <= MAX_SAFE_TEMP
        ):
            fridge_status = "HOLD"
        else:
            fridge_status = "SAFE"

    return jsonify({
        "message": "Temperature received",
        "reading": reading,
        "fridge_status": fridge_status
    }), 201


if __name__ == "__main__":
    app.run(debug=True, port=5000)
