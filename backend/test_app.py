
from unittest.mock import MagicMock

import pytest
import app as backend


@pytest.fixture(autouse=True)
def mock_mysql(monkeypatch):
    """Use a fake MySQL connection for every test."""
    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value = cursor
    connection.cursor.return_value.fetchone.return_value = None
    cursor.fetchone.return_value = {
        "safety_state": "HOLD",
        "hold_reason": "Awaiting valid simulator temperature"
    }

    # Simulate a successfully updated fridge.
    cursor.rowcount = 1

    monkeypatch.setattr(
        backend,
        "get_db_connection",
        lambda: connection
    )

    # Reset temporary application state between tests.
    backend.latest_readings.clear()
    backend.fridge_status = "HOLD"

    yield connection, cursor


@pytest.fixture
def client():
    return backend.app.test_client()


@pytest.fixture
def auth_headers():
    return {
        "Authorization": f"Bearer {backend.DEVICE_TOKEN}"
    }


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_temperature_without_token(client):
    response = client.post(
        "/api/temperatures",
        json={
            "id": "simulator-01",
            "temperature": 4.6,
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 401


def test_safe_temperature(client, auth_headers):
    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "simulator-01",
            "temperature": 4.6,
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 201
    assert response.get_json()["fridge_status"] == "SAFE"


def test_high_temperature_hold(client, auth_headers):
    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "simulator-01",
            "temperature": 24.5,
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 201
    assert response.get_json()["fridge_status"] == "HOLD"


def test_sensor_error_hold(client, auth_headers):
    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "simulator-01",
            "temperature": None,
            "sensor_status": "error"
        }
    )

    assert response.status_code == 201
    assert response.get_json()["fridge_status"] == "HOLD"


def test_unknown_device(client, auth_headers):
    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "unknown-device",
            "temperature": 4.6,
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 400


def test_invalid_temperature(client, auth_headers):
    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "simulator-01",
            "temperature": "hot",
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 400


def test_esp32_does_not_change_fridge_status(
    client, auth_headers, mock_mysql
):
    connection, cursor = mock_mysql

    # Primary simulator sets the fridge to SAFE.
    first_response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "simulator-01",
            "temperature": 4.6,
            "sensor_status": "ok"
        }
    )

    assert first_response.status_code == 201

    # The mocked database now reports SAFE.
    cursor.fetchone.return_value = {
        "safety_state": "SAFE",
        "hold_reason": None
    }

    # Secondary ESP32 must not override the primary simulator.
    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "esp32-01",
            "temperature": 24.5,
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 201
    assert response.get_json()["fridge_status"] == "SAFE"

    status_response = client.get("/api/fridge/status")
    readings = status_response.get_json()["latest_readings"]

    assert status_response.status_code == 200
    assert status_response.get_json()["status"] == "SAFE"
    assert "simulator-01" in readings
    assert "esp32-01" in readings


def test_missing_temperature_field(client, auth_headers):
    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "simulator-01",
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 400


def test_invalid_sensor_status(client, auth_headers):
    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "simulator-01",
            "temperature": 4.6,
            "sensor_status": "broken"
        }
    )

    assert response.status_code == 400


def test_invalid_json_payload(client, auth_headers):
    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        data='{"id": "simulator-01", "temperature": ',
        content_type="application/json"
    )

    assert response.status_code == 400


def test_temperature_saved_to_mysql(
    client, auth_headers, mock_mysql
):
    connection, cursor = mock_mysql

    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "simulator-01",
            "temperature": 4.6,
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 201

    sql_calls = [
        call.args[0]
        for call in cursor.execute.call_args_list
    ]

    assert any(
        "INSERT INTO temperature_readings" in sql
        for sql in sql_calls
    )

    assert any(
        "UPDATE storage_locations" in sql
        for sql in sql_calls
    )

    connection.commit.assert_called_once()


def test_esp32_does_not_update_mysql_fridge_state(
    client, auth_headers, mock_mysql
):
    connection, cursor = mock_mysql

    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "esp32-01",
            "temperature": 24.5,
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 201

    sql_calls = [
        call.args[0]
        for call in cursor.execute.call_args_list
    ]

    assert any(
        "INSERT INTO temperature_readings" in sql
        for sql in sql_calls
    )

    assert not any(
        "UPDATE storage_locations" in sql
        for sql in sql_calls
    )

    connection.commit.assert_called_once()


def test_database_failure_returns_503(
    client, auth_headers, mock_mysql
):
    connection, cursor = mock_mysql

    cursor.execute.side_effect = Exception(
        "Simulated database failure"
    )

    response = client.post(
        "/api/temperatures",
        headers=auth_headers,
        json={
            "id": "simulator-01",
            "temperature": 4.6,
            "sensor_status": "ok"
        }
    )

    assert response.status_code == 503
    assert response.get_json()["error"] == "Database unavailable"

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()
