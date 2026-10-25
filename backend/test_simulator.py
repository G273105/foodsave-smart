from unittest.mock import MagicMock

import pytest
import app as backend


@pytest.fixture
def client():
    return backend.app.test_client()


@pytest.fixture
def fake_database(monkeypatch):
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor

    state = {
        "role": "ADMIN",
        "fridge_status": "HOLD",
        "hold_reason": "Awaiting valid temperature",
        "temperature": None,
    }

    def fake_execute(sql, params=None):
        query = " ".join(sql.lower().split())

        if "update storage_locations" in query:
            state["fridge_status"] = params[0]
            state["hold_reason"] = params[1]

        elif "insert into temperature_readings" in query:
            state["temperature"] = params[1]

    def fake_fetchone():
        query = " ".join(cursor.execute.call_args.args[0].lower().split())

        if "from users" in query:
            if state["role"] is None:
                return None
            return {"role": state["role"]}

        return None

    cursor.execute.side_effect = fake_execute
    cursor.fetchone.side_effect = fake_fetchone
    cursor.rowcount = 1

    monkeypatch.setattr(
        backend,
        "get_db_connection",
        lambda: connection,
    )

    backend.latest_readings.clear()
    backend.fridge_status = "HOLD"

    return state, connection, cursor


def headers_for(role):
    token = backend.create_access_token(1, role)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("role", ["ADMIN", "STAFF"])
@pytest.mark.parametrize(
    ("temperature", "expected_status"),
    [(4.5, "SAFE"), (24.5, "HOLD")],
)
def test_authorised_simulator_control(
    client, fake_database, role, temperature, expected_status
):
    state, connection, cursor = fake_database
    state["role"] = role

    response = client.post(
        "/api/simulator/temperature",
        headers=headers_for(role),
        json={"temperature": temperature},
    )

    assert response.status_code == 201
    assert response.get_json()["fridge_status"] == expected_status
    assert state["fridge_status"] == expected_status
    assert state["temperature"] == temperature
    connection.commit.assert_called_once()


def test_student_cannot_control_simulator(client, fake_database):
    state, connection, cursor = fake_database
    state["role"] = "STUDENT"

    response = client.post(
        "/api/simulator/temperature",
        headers=headers_for("STUDENT"),
        json={"temperature": 4.5},
    )

    assert response.status_code == 403
    connection.commit.assert_not_called()


def test_missing_authentication(client, fake_database):
    response = client.post(
        "/api/simulator/temperature",
        json={"temperature": 4.5},
    )

    assert response.status_code == 401


def test_invalid_temperature(client, fake_database):
    response = client.post(
        "/api/simulator/temperature",
        headers=headers_for("ADMIN"),
        json={"temperature": 15},
    )

    assert response.status_code == 400


def test_deleted_user_cannot_control_simulator(client, fake_database):
    state, connection, cursor = fake_database
    state["role"] = None

    response = client.post(
        "/api/simulator/temperature",
        headers=headers_for("ADMIN"),
        json={"temperature": 4.5},
    )

    assert response.status_code == 401
    connection.commit.assert_not_called()


def test_role_change_revokes_access(client, fake_database):
    state, connection, cursor = fake_database
    state["role"] = "STUDENT"

    response = client.post(
        "/api/simulator/temperature",
        headers=headers_for("ADMIN"),
        json={"temperature": 4.5},
    )

    assert response.status_code == 403
    connection.commit.assert_not_called()