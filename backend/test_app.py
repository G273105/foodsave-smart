
import app as backend


def test_health_endpoint():
    client = backend.app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_temperature_without_token():
    client = backend.app.test_client()

    response = client.post(
        "/api/temperatures",
        json={
            "id": "simulator-01",
            "temperature": 4.6,
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 401


def test_safe_temperature():
    client = backend.app.test_client()

    response = client.post(
        "/api/temperatures",
        headers={
            "Authorization": f"Bearer {backend.DEVICE_TOKEN}"
        },
        json={
            "id": "simulator-01",
            "temperature": 4.6,
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 201
    assert response.get_json()["fridge_status"] == "SAFE"

def test_high_temperature_hold():
        client = backend.app.test_client()

        response = client.post(
            "/api/temperatures",
            headers={
                "Authorization": f"Bearer {backend.DEVICE_TOKEN}"
            },
            json={
                "id": "simulator-01",
                "temperature": 8.5,
                "sensor_status": "ok"
            }
        )

        assert response.status_code == 201
        assert response.get_json()["fridge_status"] == "HOLD"

def test_sensor_error_hold():
        client = backend.app.test_client()

        response = client.post(
            "/api/temperatures",
            headers={
                "Authorization": f"Bearer {backend.DEVICE_TOKEN}"
            },
            json={
                "id": "simulator-01",
                "temperature": None,
                "sensor_status": "error"
            }
        )

        assert response.status_code == 201
        assert response.get_json()["fridge_status"] == "HOLD"


def test_unknown_device():
    client = backend.app.test_client()

    response = client.post(
        "/api/temperatures",
        headers={
            "Authorization": f"Bearer {backend.DEVICE_TOKEN}"
        },
        json={
            "id": "unknown-device",
            "temperature": 4.6,
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 400


def test_invalid_temperature():
    client = backend.app.test_client()

    response = client.post(
        "/api/temperatures",
        headers={
            "Authorization": f"Bearer {backend.DEVICE_TOKEN}"
        },
        json={
            "id": "simulator-01",
            "temperature": "hot",
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 400


def test_esp32_does_not_change_fridge_status():
    client = backend.app.test_client()

    headers = {
        "Authorization": f"Bearer {backend.DEVICE_TOKEN}"
    }

    # First, the primary simulator sets the fridge to SAFE.
    client.post(
        "/api/temperatures",
        headers=headers,
        json={
            "id": "simulator-01",
            "temperature": 4.6,
            "sensor_status": "ok"
        }
    )

    # The ESP32 sends a high temperature.
    response = client.post(
        "/api/temperatures",
        headers=headers,
        json={
            "id": "esp32-01",
            "temperature": 8.5,
            "sensor_status": "ok"
        }
    )

    # ESP32 readings are accepted but do not control fridge status.
    assert response.status_code == 201
    assert response.get_json()["fridge_status"] == "SAFE"

    # Both device readings must be available.
    status_response = client.get("/api/fridge/status")
    readings = status_response.get_json()["latest_readings"]

    assert "simulator-01" in readings
    assert "esp32-01" in readings

