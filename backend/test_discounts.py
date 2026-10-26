
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

import app as backend


# ------------------------------------------------------------
# DISCOUNT RULE TESTS
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "hours, expected_discount",
    [
        (48, 0),
        (25, 0),
        (24, 25),
        (18, 25),
        (12, 25),
        (11, 50),
        (6, 50),
        (5, 75),
        (1, 75),
        (0, 0),
        (-1, 0),
    ]
)
def test_discount_by_remaining_time(
    hours,
    expected_discount
):
    now = datetime(2026, 10, 20, 12, 0, 0)
    sell_by = now + timedelta(hours=hours)

    result = backend.calculate_discount(
        sell_by,
        now
    )

    assert result == expected_discount


@pytest.mark.parametrize(
    "original, discount, expected",
    [
        (1000, 0, 1000),
        (1000, 25, 750),
        (1000, 50, 500),
        (1000, 75, 250),
        (199, 50, 100),
        (150, 75, 38),
    ]
)
def test_discounted_price(
    original,
    discount,
    expected
):
    result = backend.calculate_discounted_price(
        original,
        discount
    )

    assert result == expected


# ------------------------------------------------------------
# PRODUCT API TEST FIXTURES
# ------------------------------------------------------------

@pytest.fixture
def client():
    return backend.app.test_client()


@pytest.fixture
def mock_products_database(monkeypatch):
    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value = cursor

    now = datetime(2026, 10, 20, 12, 0, 0)

    product = {
        "batch_id": 10,
        "name": "Bread Pack",
        "category_id": 2,
        "location_id": 1,
        "allergens_json": '["gluten"]',
        "original_price_pence": 200,
        "quantity_available": 6,
        "sell_by_at": now + timedelta(hours=5),
        "availability_status": "AVAILABLE"
    }

    state = {
        "safety_state": "SAFE",
        "hold_reason": None,
        "products": [product]
    }

    def fake_execute(sql, params=None):
        normalized = " ".join(sql.lower().split())

        if "select now()" in normalized:
            cursor.fetchone.return_value = {
                "db_now": now
            }

        elif "from storage_locations" in normalized:
            cursor.fetchone.return_value = {
                "safety_state": state["safety_state"],
                "hold_reason": state["hold_reason"]
            }

        elif "from batches" in normalized:
            cursor.fetchall.return_value = [
                item.copy()
                for item in state["products"]
            ]

    cursor.execute.side_effect = fake_execute

    monkeypatch.setattr(
        backend,
        "get_db_connection",
        lambda: connection
    )

    return state


# ------------------------------------------------------------
# PRODUCT API TESTS
# ------------------------------------------------------------

def test_products_safe_fridge(
    client,
    mock_products_database
):
    response = client.get("/api/products")

    assert response.status_code == 200

    data = response.get_json()

    assert data["fridge_status"] == "SAFE"
    assert data["count"] == 1

    product = data["products"][0]

    assert product["can_reserve"] is True
    assert product["discount_percent"] == 75
    assert product["original_price_pence"] == 200
    assert product["discounted_price_pence"] == 50
    assert product["reservation_status"] == "AVAILABLE"


def test_products_hold_fridge(
    client,
    mock_products_database
):
    mock_products_database["safety_state"] = "HOLD"
    mock_products_database["hold_reason"] = (
        "Temperature outside safe range"
    )

    response = client.get("/api/products")

    assert response.status_code == 200

    data = response.get_json()

    assert data["fridge_status"] == "HOLD"
    assert data["count"] == 1

    product = data["products"][0]

    # Product remains visible.
    assert product["name"] == "Bread Pack"

    # Reservation is disabled.
    assert product["can_reserve"] is False

    assert product["reservation_status"] == (
        "DISABLED_TEMPERATURE_HOLD"
    )

    # Discount remains visible.
    assert product["discount_percent"] == 75
    assert product["discounted_price_pence"] == 50


def test_products_empty_list(
    client,
    mock_products_database
):
    mock_products_database["products"] = []

    response = client.get("/api/products")

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 0
    assert data["products"] == []


def test_products_fridge_not_found(
    client,
    mock_products_database,
    monkeypatch
):
    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value = cursor

    cursor.fetchone.side_effect = [
        {"db_now": datetime(2026, 10, 20)},
        None
    ]

    monkeypatch.setattr(
        backend,
        "get_db_connection",
        lambda: connection
    )

    response = client.get("/api/products")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Fridge not found"


def test_products_database_failure(
    client,
    monkeypatch
):
    def failing_connection():
        raise RuntimeError("Simulated database failure")

    monkeypatch.setattr(
        backend,
        "get_db_connection",
        failing_connection
    )

    response = client.get("/api/products")

    assert response.status_code == 503

    assert response.get_json()["error"] == (
        "Database unavailable"
    )


def test_products_cors_header(
    client,
    mock_products_database
):
    response = client.get(
        "/api/products",
        headers={
            "Origin": "http://localhost:3000"
        }
    )

    assert response.status_code == 200

    assert response.headers.get(
        "Access-Control-Allow-Origin"
    ) == "http://localhost:3000"
