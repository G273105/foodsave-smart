
import math
import os
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from functools import wraps
from pathlib import Path

import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db_connection


# ------------------------------------------------------------
# APPLICATION CONFIGURATION
# ------------------------------------------------------------

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)

# Public API endpoints and local frontend development.
CORS(
    app,
    resources={
        r"/api/health": {"origins": "*"},
        r"/api/fridge/status": {"origins": "*"},
        r"/api/products": {"origins": "*"},
        r"/api/auth/*": {
            "origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
        },
    },
)

DEVICE_TOKEN = os.getenv("DEVICE_TOKEN")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not DEVICE_TOKEN:
    raise RuntimeError("DEVICE_TOKEN is not configured")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured")

try:
    JWT_EXPIRATION_MINUTES = int(
        os.getenv("JWT_EXPIRATION_MINUTES", "60")
    )
except ValueError as exc:
    raise RuntimeError(
        "JWT_EXPIRATION_MINUTES must be an integer"
    ) from exc

if JWT_EXPIRATION_MINUTES <= 0:
    raise RuntimeError(
        "JWT_EXPIRATION_MINUTES must be positive"
    )


# ------------------------------------------------------------
# PROJECT CONFIGURATION
# ------------------------------------------------------------

MIN_SAFE_TEMP = 0.0
MAX_SAFE_TEMP = 5.0

LOCATION_ID = 1
ACTIVE_DEVICE_ID = "simulator-01"

DEVICE_IDS = {
    "simulator-01": 1,
    "esp32-01": 2,
}

# Retained for compatibility with existing tests.
latest_readings = {}
fridge_status = "HOLD"


# ------------------------------------------------------------
# JWT UTILITIES
# ------------------------------------------------------------

def create_access_token(user_id, role):
    """Create a signed JWT for an authenticated user."""

    if (
        isinstance(user_id, bool)
        or not isinstance(user_id, int)
        or user_id <= 0
    ):
        raise ValueError("user_id must be a positive integer")

    if role not in ("STUDENT", "STAFF", "ADMIN"):
        raise ValueError("Invalid user role")

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(
            minutes=JWT_EXPIRATION_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm="HS256",
    )


def verify_access_token(token):
    """Validate a JWT and return its identity claims."""

    if not isinstance(token, str) or not token:
        return None

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
            options={
                "require": ["sub", "role", "iat", "exp"]
            },
        )

        user_id = int(payload["sub"])

        if user_id <= 0 or str(user_id) != payload["sub"]:
            return None

        if payload["role"] not in (
            "STUDENT",
            "STAFF",
            "ADMIN",
        ):
            return None

        return {
            "user_id": user_id,
            "role": payload["role"],
        }

    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError,
        KeyError,
    ):
        return None


def login_required(function):
    """Require a valid JWT for protected API endpoints."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        authorization = request.headers.get(
            "Authorization", ""
        )

        if not authorization.startswith("Bearer "):
            return jsonify({
                "error": "Authentication required"
            }), 401

        token = authorization[7:].strip()
        claims = verify_access_token(token)

        if claims is None:
            return jsonify({
                "error": "Invalid or expired token"
            }), 401

        return function(claims, *args, **kwargs)

    return wrapper


# ------------------------------------------------------------
# AUTHENTICATION VALIDATION
# ------------------------------------------------------------

def normalize_email(value):
    """Validate and normalise an email address."""

    if not isinstance(value, str):
        return None

    email = value.strip().lower()

    if len(email) > 254:
        return None

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.fullmatch(pattern, email):
        return None

    return email


def validate_password(password):
    """Apply minimum password requirements."""

    if not isinstance(password, str):
        return False

    return 8 <= len(password) <= 128


def public_user(user):
    """Return user information without sensitive fields."""

    return {
        "user_id": user["user_id"],
        "display_name": user["display_name"],
        "email": user["email"],
        "role": user["role"],
    }


# ------------------------------------------------------------
# REGISTER
# ------------------------------------------------------------

@app.post("/api/auth/register")
def register_user():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON is required"
        }), 400

    display_name = data.get("display_name")
    email = normalize_email(data.get("email"))
    password = data.get("password")

    if (
        not isinstance(display_name, str)
        or not 2 <= len(display_name.strip()) <= 100
    ):
        return jsonify({
            "error": "Display name must contain 2 to 100 characters"
        }), 400

    if email is None:
        return jsonify({
            "error": "A valid email address is required"
        }), 400

    if not validate_password(password):
        return jsonify({
            "error": "Password must contain 8 to 128 characters"
        }), 400

    display_name = display_name.strip()

    # Public registration cannot assign privileged roles.
    role = "STUDENT"

    password_hash = generate_password_hash(password)

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = %s
            LIMIT 1
            """,
            (email,),
        )

        if cursor.fetchone() is not None:
            return jsonify({
                "error": "Email already registered"
            }), 409

        cursor.execute(
            """
            INSERT INTO users
                (display_name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            """,
            (
                display_name,
                email,
                password_hash,
                role,
            ),
        )

        user_id = cursor.lastrowid
        connection.commit()

        user = {
            "user_id": user_id,
            "display_name": display_name,
            "email": email,
            "role": role,
        }

        return jsonify({
            "message": "Registration successful",
            "user": user,
        }), 201

    except Exception as exc:
        if connection is not None:
            connection.rollback()

        if getattr(exc, "errno", None) == 1062:
            return jsonify({
                "error": "Email already registered"
            }), 409

        app.logger.exception("Registration failed")

        return jsonify({
            "error": "Database unavailable"
        }), 503

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------

@app.post("/api/auth/login")
def login_user():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON is required"
        }), 400

    email = normalize_email(data.get("email"))
    password = data.get("password")

    if email is None or not isinstance(password, str):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                user_id,
                display_name,
                email,
                password_hash,
                role
            FROM users
            WHERE email = %s
            LIMIT 1
            """,
            (email,),
        )

        user = cursor.fetchone()

        if (
            user is None
            or not check_password_hash(
                user["password_hash"],
                password,
            )
        ):
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        token = create_access_token(
            user["user_id"],
            user["role"],
        )

        return jsonify({
            "message": "Login successful",
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": JWT_EXPIRATION_MINUTES * 60,
            "user": public_user(user),
        }), 200

    except Exception:
        app.logger.exception("Login failed")

        return jsonify({
            "error": "Database unavailable"
        }), 503

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ------------------------------------------------------------
# CURRENT USER
# ------------------------------------------------------------

@app.get("/api/auth/me")
@login_required
def get_current_user(claims):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                user_id,
                display_name,
                email,
                role
            FROM users
            WHERE user_id = %s
            LIMIT 1
            """,
            (claims["user_id"],),
        )

        user = cursor.fetchone()

        if user is None:
            return jsonify({
                "error": "User not found"
            }), 401

        return jsonify({
            "user": public_user(user)
        }), 200

    except Exception:
        app.logger.exception(
            "Failed to retrieve current user"
        )

        return jsonify({
            "error": "Database unavailable"
        }), 503

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------

@app.get("/api/health")
def health_check():
    return jsonify({
        "status": "ok",
        "project": "Food Save Smart",
        "message": "Backend is running successfully",
    }), 200


# ------------------------------------------------------------
# FRIDGE STATUS
# ------------------------------------------------------------

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
            (LOCATION_ID,),
        )

        location = cursor.fetchone()

        if location is None:
            return jsonify({
                "error": "Fridge not found"
            }), 404

        readings = {}

        for api_device_id, mysql_device_id in DEVICE_IDS.items():
            cursor.execute(
                """
                SELECT
                    temperature_c,
                    sensor_status,
                    received_at
                FROM temperature_readings
                WHERE device_id = %s
                ORDER BY received_at DESC, reading_id DESC
                LIMIT 1
                """,
                (mysql_device_id,),
            )

            latest = cursor.fetchone()

            if latest is None:
                continue

            received_at = latest["received_at"]

            if isinstance(received_at, datetime):
                received_at = received_at.isoformat()
            else:
                received_at = str(received_at)

            temperature = latest["temperature_c"]

            if temperature is not None:
                temperature = float(temperature)

            readings[api_device_id] = {
                "id": api_device_id,
                "temperature": temperature,
                "sensor_status": latest["sensor_status"],
                "received_at": received_at,
            }

        return jsonify({
            "location_id": LOCATION_ID,
            "active_device_id": ACTIVE_DEVICE_ID,
            "status": location["safety_state"],
            "hold_reason": location["hold_reason"],
            "latest_readings": readings,
        }), 200

    except Exception:
        app.logger.exception(
            "Failed to retrieve fridge status"
        )

        return jsonify({
            "error": "Database unavailable"
        }), 503

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ------------------------------------------------------------
# TEMPERATURE MONITORING
# ------------------------------------------------------------

@app.post("/api/temperatures")
def receive_temperature():
    global fridge_status

    authorization = request.headers.get(
        "Authorization", ""
    )

    if authorization != f"Bearer {DEVICE_TOKEN}":
        return jsonify({
            "error": "Unauthorized device"
        }), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON is required"
        }), 400

    device_id = data.get("id")
    temperature = data.get("temperature")
    sensor_status = data.get("sensor_status")

    if device_id not in DEVICE_IDS:
        return jsonify({
            "error": "Unknown device ID"
        }), 400

    if sensor_status not in ("ok", "error"):
        return jsonify({
            "error": "Invalid sensor status"
        }), 400

    if temperature is not None:
        if (
            not isinstance(temperature, (int, float))
            or isinstance(temperature, bool)
        ):
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
            (
                DEVICE_IDS[device_id],
                temperature,
                sensor_status,
            ),
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
                (
                    new_status,
                    hold_reason,
                    LOCATION_ID,
                ),
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Fridge location not found"
                )

        connection.commit()

    except Exception:
        if connection is not None:
            connection.rollback()

        app.logger.exception("Failed to save temperature")

        return jsonify({
            "error": "Database unavailable"
        }), 503

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

    reading = {
        "id": device_id,
        "temperature": temperature,
        "sensor_status": sensor_status,
        "received_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    latest_readings[device_id] = reading

    if new_status is not None:
        fridge_status = new_status

    return jsonify({
        "message": "Temperature received",
        "reading": reading,
        "fridge_status": fridge_status,
    }), 201


# ------------------------------------------------------------
# AUTOMATIC DISCOUNTS
# ------------------------------------------------------------

def calculate_discount(sell_by_at, now):
    """
    Calculate discounts based on remaining shelf life.

    More than 24 hours: 0%
    12 to 24 hours: 25%
    6 to under 12 hours: 50%
    Under 6 hours: 75%

    Expired products cannot be reserved.
    """

    if sell_by_at is None:
        return 0

    remaining_hours = (
        sell_by_at - now
    ).total_seconds() / 3600

    if remaining_hours <= 0:
        return 0

    if remaining_hours < 6:
        return 75

    if remaining_hours < 12:
        return 50

    if remaining_hours <= 24:
        return 25

    return 0


def calculate_discounted_price(
    original_price_pence,
    discount_percent,
):
    """Calculate a discounted price in integer pence."""

    original = Decimal(
        str(original_price_pence)
    )

    discounted = (
        original
        * Decimal(100 - discount_percent)
        / Decimal(100)
    )

    return int(
        discounted.quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )


# ------------------------------------------------------------
# PRODUCTS API
# ------------------------------------------------------------

@app.get("/api/products")
def get_products():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # FIX: Avoid the reserved MySQL identifier current_time.
        cursor.execute(
            "SELECT NOW() AS current_time"
        )

        now = cursor.fetchone()["current_time"]

        cursor.execute(
            """
            SELECT safety_state, hold_reason
            FROM storage_locations
            WHERE location_id = %s
            """,
            (LOCATION_ID,),
        )

        fridge = cursor.fetchone()

        if fridge is None:
            return jsonify({
                "error": "Fridge not found"
            }), 404

        fridge_safe = (
            fridge["safety_state"] == "SAFE"
        )

        cursor.execute(
            """
            SELECT
                batch_id,
                name,
                category_id,
                location_id,
                allergens_json,
                original_price_pence,
                quantity_available,
                sell_by_at,
                availability_status
            FROM batches
            WHERE availability_status = %s
              AND quantity_available > 0
              AND sell_by_at > %s
              AND location_id = %s
            ORDER BY sell_by_at ASC, batch_id ASC
            """,
            ("AVAILABLE", now, LOCATION_ID),
        )

        products = cursor.fetchall()

        for product in products:
            discount_percent = calculate_discount(
                product["sell_by_at"],
                now,
            )

            discounted_price_pence = (
                calculate_discounted_price(
                    product["original_price_pence"],
                    discount_percent,
                )
            )

            product["discount_percent"] = discount_percent
            product["discounted_price_pence"] = (
                discounted_price_pence
            )

            # Products remain visible during temperature HOLD.
            # Reservation eligibility is enforced separately.
            product["can_reserve"] = fridge_safe

            if fridge_safe:
                product["reservation_status"] = "AVAILABLE"
                product["reservation_message"] = None
            else:
                product["reservation_status"] = (
                    "DISABLED_TEMPERATURE_HOLD"
                )
                product["reservation_message"] = (
                    "Temporarily unavailable - "
                    "temperature safety check"
                )

            if product["sell_by_at"] is not None:
                product["sell_by_at"] = (
                    product["sell_by_at"].isoformat()
                )

        return jsonify({
            "count": len(products),
            "fridge_status": fridge["safety_state"],
            "hold_reason": fridge["hold_reason"],
            "products": products,
        }), 200

    except Exception:
        app.logger.exception(
            "Failed to retrieve products"
        )

        return jsonify({
            "error": "Database unavailable"
        }), 503

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ------------------------------------------------------------
# RESERVATIONS API
# ------------------------------------------------------------

@app.post("/api/reservations")
@login_required
def create_reservation(claims):
    """
    Create a reservation for an authenticated user.

    Reservations require:
    - An existing user.
    - An active and SAFE fridge.
    - An available, unexpired product.
    - Sufficient stock.

    Row locks and transactions help prevent overselling.
    """

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON is required"
        }), 400

    batch_id = data.get("batch_id")
    quantity = data.get("quantity", 1)

    if type(batch_id) is not int or batch_id <= 0:
        return jsonify({
            "error": "batch_id must be a positive integer"
        }), 400

    if type(quantity) is not int or quantity < 1:
        return jsonify({
            "error": "quantity must be a positive integer"
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Verify that the authenticated user still exists.
        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = %s
            LIMIT 1
            """,
            (claims["user_id"],),
        )

        if cursor.fetchone() is None:
            connection.rollback()

            return jsonify({
                "error": "User not found"
            }), 401

        # Lock fridge state during the reservation.
        cursor.execute(
            """
            SELECT
                safety_state,
                hold_reason,
                is_active
            FROM storage_locations
            WHERE location_id = %s
            FOR UPDATE
            """,
            (LOCATION_ID,),
        )

        location = cursor.fetchone()

        if location is None:
            connection.rollback()

            return jsonify({
                "error": "Fridge not found"
            }), 404

        if (
            not location["is_active"]
            or location["safety_state"] != "SAFE"
        ):
            connection.rollback()

            return jsonify({
                "error": "Reservations disabled while fridge is unsafe",
                "fridge_status": location["safety_state"],
                "hold_reason": location["hold_reason"],
            }), 409

        # Lock product row to prevent overselling.
        cursor.execute(
            """
            SELECT
                batch_id,
                location_id,
                original_price_pence,
                quantity_available,
                sell_by_at,
                availability_status
            FROM batches
            WHERE batch_id = %s
            FOR UPDATE
            """,
            (batch_id,),
        )

        batch = cursor.fetchone()

        if (
            batch is None
            or batch["location_id"] != LOCATION_ID
        ):
            connection.rollback()

            return jsonify({
                "error": "Product not found"
            }), 404

        # FIX: Use a non-reserved alias for the database clock.
        cursor.execute(
            "SELECT NOW() AS current_time"
        )

        now = cursor.fetchone()["current_time"]

        if (
            batch["availability_status"] != "AVAILABLE"
            or batch["sell_by_at"] is None
            or batch["sell_by_at"] <= now
        ):
            connection.rollback()

            return jsonify({
                "error": "Product is no longer available"
            }), 409

        if batch["quantity_available"] < quantity:
            connection.rollback()

            return jsonify({
                "error": "Insufficient stock"
            }), 409

        # Calculate automatic discount.
        discount_percent = calculate_discount(
            batch["sell_by_at"],
            now,
        )

        unit_price_pence = calculate_discounted_price(
            batch["original_price_pence"],
            discount_percent,
        )

        total_price_pence = unit_price_pence * quantity

        # Create reservation using the existing schema.
        cursor.execute(
            """
            INSERT INTO reservations
                (batch_id, user_id, quantity, status)
            VALUES (%s, %s, %s, %s)
            """,
            (
                batch_id,
                claims["user_id"],
                quantity,
                "PENDING",
            ),
        )

        reservation_id = cursor.lastrowid

        # Reduce stock within the same transaction.
        cursor.execute(
            """
            UPDATE batches
            SET quantity_available = quantity_available - %s
            WHERE batch_id = %s
              AND quantity_available >= %s
            """,
            (
                quantity,
                batch_id,
                quantity,
            ),
        )

        if cursor.rowcount != 1:
            raise RuntimeError("Stock update failed")

        connection.commit()

        return jsonify({
            "message": "Reservation created",
            "reservation": {
                "reservation_id": reservation_id,
                "batch_id": batch_id,
                "user_id": claims["user_id"],
                "quantity": quantity,
                "status": "PENDING",
                "discount_percent": discount_percent,
                "unit_price_pence": unit_price_pence,
                "total_price_pence": total_price_pence,
            },
            "pricing_note": (
                "Price is not yet stored in reservations"
            ),
        }), 201

    except Exception:
        if connection is not None:
            connection.rollback()

        app.logger.exception(
            "Failed to create reservation"
        )

        return jsonify({
            "error": "Database unavailable"
        }), 503

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ------------------------------------------------------------
# LOCAL DEVELOPMENT
# ------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
