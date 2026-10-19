import math
import os
from datetime import datetime, timezone
from pathlib import Path
from flask_cors import CORS


from dotenv import load_dotenv
from flask import Flask, jsonify, request
from db import get_db_connection

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/api/health": {"origins": "*"},
        r"/api/fridge/status": {"origins": "*"}
    }
)

DEVICE_TOKEN = os.getenv("DEVICE_TOKEN")

if not DEVICE_TOKEN:
    raise RuntimeError("DEVICE_TOKEN is not configured")

# Provisional safety limits for the project.
MIN_SAFE_TEMP = 0.0
MAX_SAFE_TEMP = 5.0

LOCATION_ID = 1
ACTIVE_DEVICE_ID = "simulator-01"

# Mapping between API device identifiers and Alex's MySQL IDs.
DEVICE_IDS = {
    "simulator-01": 1,
    "esp32-01": 2
}

# Kept temporarily for compatibility with existing tests.
latest_readings = {}
fridge_status = "HOLD"


@app.get("/api/health")
def health_check():
    return jsonify({
        "status": "ok",
        "project": "FoodSave Smart",
        "message": "Backend is running successfully"
    }), 200


@app.get("/api/fridge/status")
def get_fridge_status():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT safety_state, hold_reason
            FROM storage_locations
            WHERE location_id = %s
            """,
            (LOCATION_ID,)
        )

        location = cursor.fetchone()

        if location is None:
            return jsonify({"error": "Fridge not found"}), 404

        return jsonify({
            "location_id": LOCATION_ID,
            "active_device_id": ACTIVE_DEVICE_ID,
            "status": location["safety_state"],
            "hold_reason": location["hold_reason"],
            "latest_readings": latest_readings
        }), 200

    except Exception:
        app.logger.exception("Failed to retrieve fridge status")
        return jsonify({"error": "Database unavailable"}), 503

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


@app.post("/api/temperatures")
def receive_temperature():
    global fridge_status

    # Step 1: Authenticate the device.
    authorization = request.headers.get("Authorization", "")

    if authorization != f"Bearer {DEVICE_TOKEN}":
        return jsonify({"error": "Unauthorized device"}), 401

    # Step 2: Validate JSON.
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON is required"}), 400

    device_id = data.get("id")
    temperature = data.get("temperature")
    sensor_status = data.get("sensor_status")

    # Step 3: Validate device ID.
    if device_id not in DEVICE_IDS:
        return jsonify({"error": "Unknown device ID"}), 400

    # Step 4: Validate sensor status.
    if sensor_status not in ("ok", "error"):
        return jsonify({"error": "Invalid sensor status"}), 400

    # Step 5: Validate temperature.
    if temperature is not None:
        if (
            not isinstance(temperature, (int, float))
            or isinstance(temperature, bool)
        ):
            return jsonify({"error": "Temperature must be a number"}), 400

        if not math.isfinite(temperature):
            return jsonify({"error": "Temperature must be finite"}), 400

        if not -50 <= temperature <= 100:
            return jsonify({"error": "Temperature outside valid range"}), 400

    if sensor_status == "ok" and temperature is None:
        return jsonify({"error": "Temperature is required"}), 400

    if sensor_status == "error" and temperature is not None:
        return jsonify({
            "error": "Temperature must be null when sensor status is error"
        }), 400

    # Step 6: Determine safety state.
    new_status = None
    hold_reason = None

    if device_id == ACTIVE_DEVICE_ID:
        if sensor_status == "error":
            new_status = "HOLD"
            hold_reason = "Simulator sensor error"
        elif not MIN_SAFE_TEMP <= temperature <= MAX_SAFE_TEMP:
            new_status = "HOLD"
            hold_reason = "Temperature outside safe range"
        else:
            new_status = "SAFE"

    # Step 7: Save the reading and safety state in MySQL.
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO temperature_readings
                (device_id, temperature_c, sensor_status)
            VALUES (%s, %s, %s)
            """,
            (DEVICE_IDS[device_id], temperature, sensor_status)
        )

        if new_status is not None:
            cursor.execute(
                """
                UPDATE storage_locations
                SET safety_state = %s,
                    hold_reason = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE location_id = %s
                """,
                (new_status, hold_reason, LOCATION_ID)
            )

            if cursor.rowcount != 1:
                raise RuntimeError("Fridge location not found")

        connection.commit()

    except Exception:
        if connection is not None:
            connection.rollback()

        app.logger.exception("Failed to save temperature")
        return jsonify({"error": "Database unavailable"}), 503

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

    # Step 8: Update temporary API cache after successful commit.
    reading = {
        "id": device_id,
        "temperature": temperature,
        "sensor_status": sensor_status,
        "received_at": datetime.now(timezone.utc).isoformat()
    }

    latest_readings[device_id] = reading

    if new_status is not None:
        fridge_status = new_status

    return jsonify({
        "message": "Temperature received",
        "reading": reading,
        "fridge_status": fridge_status
    }), 201


if __name__ == "__main__":
    app.run(debug=True, port=5000)
