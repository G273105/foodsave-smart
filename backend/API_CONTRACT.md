# FoodSave Smart — Backend API Integration Contract

**Project:** FoodSave Smart  
**Module:** CPU4106  
**Backend:** Python Flask  
**Frontend:** Florin  
**Backend API:** Laurentiu  
**Database schema:** Alex  
**Status:** Integration preparation — database-dependent operations not yet fully verified

## 1. Base URLs

Production backend:

`https://foodsave-smart.onrender.com`

Frontend preview:

`https://food-save-smart.co.uk/dist/index.html#browse`

Local backend:

`http://127.0.0.1:5000`

The frontend must communicate with Flask through HTTP/HTTPS API requests. It must not connect directly to MySQL.

The frontend currently uses demonstration data and local reservation behaviour. Real API integration is pending.

## 2. GET /api/products

**Purpose:** Retrieve available food products, automatically calculated discounts and reservation eligibility.

**Authentication:** Not required.

**Request:**

`GET https://foodsave-smart.onrender.com/api/products`

**Successful response: HTTP 200**

Example response structure (illustrative values):

```json
{
  "count": 1,
  "fridge_status": "SAFE",
  "hold_reason": null,
  "products": [
    {
      "batch_id": 19,
      "name": "Sandwich",
      "category_id": 1,
      "location_id": 1,
      "allergens_json": null,
      "original_price_pence": 400,
      "quantity_available": 8,
      "sell_by_at": "2026-10-21T12:00:00",
      "availability_status": "AVAILABLE",
      "discount_percent": 50,
      "discounted_price_pence": 200,
      "can_reserve": true,
      "reservation_status": "AVAILABLE",
      "reservation_message": null
    }
  ]
}
```

This example illustrates the response structure. It is not a confirmed response from the production database.

### Product fields

| Field | Meaning |
|---|---|
| `batch_id` | Unique batch identifier used for reservations |
| `name` | Product name |
| `category_id` | Category identifier |
| `location_id` | Storage location |
| `allergens_json` | Allergen information from the database |
| `original_price_pence` | Original price in GBP pence |
| `discount_percent` | Discount calculated by Flask |
| `discounted_price_pence` | Final price calculated by Flask |
| `quantity_available` | Remaining stock |
| `sell_by_at` | Product expiry/sell-by date and time |
| `availability_status` | Product availability status |
| `can_reserve` | Whether the frontend should enable reservation |
| `reservation_status` | Reservation eligibility code |
| `reservation_message` | Message explaining why reservation is disabled |

### Frontend requirements

Florin must:

- Display product names and available quantities.
- Display the original price and discounted price.
- Display the discount percentage.
- Display the remaining time until `sell_by_at`.
- Disable reservation when `can_reserve` is `false`.
- Display `reservation_message` when provided.
- Use `batch_id` when submitting reservations.

Prices are provided in integer pence.

For example:

- `original_price_pence: 400` means £4.00.
- `discounted_price_pence: 200` means £2.00.

The frontend may divide pence by 100 for GBP display, but must not recalculate the discount or final selling price.

### Expiry countdown

The backend supplies `sell_by_at`.

The frontend may calculate the countdown for display purposes, but it must not use the countdown as the authoritative decision about reservation eligibility.

The backend performs the final expiry and stock checks.

**Important:** The API currently returns a date-time string without an explicit timezone offset. Timezone handling must be agreed before implementing a reliable production countdown.

### Product filtering

The current backend returns only batches meeting all of these conditions:

- `availability_status = AVAILABLE`
- `quantity_available > 0`
- `sell_by_at` is later than the database's current time
- `location_id = 1`

Expired, out-of-stock and otherwise unavailable batches are excluded from the response.

The frontend therefore cannot display these excluded products or their individual unavailable reasons using the current endpoint.

Products remain visible during a fridge temperature HOLD, but reservation is disabled.

## 3. Automatic Discount Rules

Discounts are calculated by Flask using the remaining time before `sell_by_at`.

| Time remaining | Discount |
|---|---|
| More than 24 hours | 0% |
| More than or equal to 12 hours, up to 24 hours | 25% |
| More than or equal to 6 hours, under 12 hours | 50% |
| More than 0 hours, under 6 hours | 75% |
| Expired | Not eligible for reservation |

The backend uses decimal arithmetic and rounds the final price to the nearest penny, with half-up rounding.

**Florin must not implement independent discount calculations in JavaScript.**

The frontend should display the values returned by the API.

## 4. Fridge Safety and Reservation Eligibility

The fridge status is included in the products response.

Possible safety states:

- `SAFE`
- `HOLD`

When the fridge is SAFE, the current products endpoint marks returned products as:

```json
{
  "can_reserve": true,
  "reservation_status": "AVAILABLE",
  "reservation_message": null
}
```

When the fridge is on HOLD, the current products endpoint marks returned products as:

```json
{
  "can_reserve": false,
  "reservation_status": "DISABLED_TEMPERATURE_HOLD",
  "reservation_message": "Temporarily unavailable - temperature safety check"
}
```

Florin should display the backend message and disable the reservation button.

The reservation endpoint also checks whether the fridge is active. This additional check is not currently included in the products endpoint's `can_reserve` calculation.

Therefore, `can_reserve` is a frontend indicator, not a guarantee that a reservation will succeed.

## 5. POST /api/auth/register

**Purpose:** Register a new student account.

**Authentication:** Not required.

**Request:**

```json
{
  "display_name": "Example Student",
  "email": "student@example.com",
  "password": "ExamplePassword123"
}
```

Validation rules:

- Display name: 2–100 characters after trimming.
- Email: valid email format.
- Password: 8–128 characters.
- Public registrations automatically receive the `STUDENT` role.

**Successful response: HTTP 201**

```json
{
  "message": "Registration successful",
  "user": {
    "user_id": 1,
    "display_name": "Example Student",
    "email": "student@example.com",
    "role": "STUDENT"
  }
}
```

Possible errors:

- `400`: Invalid input.
- `409`: Email already registered.
- `503`: Database unavailable.

**Warning:** Registration creates a database record. Do not use this endpoint against the shared database until integration testing has been approved.

## 6. POST /api/auth/login

**Purpose:** Authenticate an existing user.

**Authentication:** Not required.

**Request:**

```json
{
  "email": "student@example.com",
  "password": "ExamplePassword123"
}
```

**Successful response: HTTP 200**

```json
{
  "message": "Login successful",
  "access_token": "<JWT_ACCESS_TOKEN>",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "user_id": 1,
    "display_name": "Example Student",
    "email": "student@example.com",
    "role": "STUDENT"
  }
}
```

`expires_in` is expressed in seconds and depends on backend configuration. The current default is 3600 seconds.

Possible errors:

- `400`: Invalid JSON.
- `401`: Invalid email or password.
- `503`: Database unavailable.

The frontend must never expose passwords or JWT signing secrets in its source code.

## 7. GET /api/auth/me

**Purpose:** Retrieve the currently authenticated user.

**Authentication:** JWT required.

**Header:**

`Authorization: Bearer <JWT_ACCESS_TOKEN>`

**Successful response: HTTP 200**

```json
{
  "user": {
    "user_id": 1,
    "display_name": "Example Student",
    "email": "student@example.com",
    "role": "STUDENT"
  }
}
```

Possible errors:

- `401`: Missing, invalid or expired token, or user not found.
- `503`: Database unavailable.

## 8. POST /api/reservations

**Purpose:** Create a reservation for an authenticated user.

**Authentication:** JWT required.

**Headers:**

```text
Authorization: Bearer <JWT_ACCESS_TOKEN>
Content-Type: application/json
```

**Request:**

```json
{
  "batch_id": 19,
  "quantity": 1
}
```

Both values must be positive integers. If `quantity` is omitted, the backend defaults to 1.

**Successful response: HTTP 201**

```json
{
  "message": "Reservation created",
  "reservation": {
    "reservation_id": 42,
    "batch_id": 19,
    "user_id": 1,
    "quantity": 1,
    "status": "PENDING",
    "discount_percent": 50,
    "unit_price_pence": 200,
    "total_price_pence": 200
  },
  "pricing_note": "Price is not yet stored in reservations"
}
```

These identifiers and prices are illustrative.

### Reservation validation

The backend verifies:

1. The JWT is valid.
2. The authenticated user exists.
3. The fridge is active and SAFE.
4. The product exists in the configured location.
5. The product is AVAILABLE and not expired.
6. The requested quantity is available.

If all checks pass, the backend inserts a PENDING reservation and reduces the available stock within a database transaction.

### Possible reservation errors

| HTTP | Error |
|---|---|
| 400 | Invalid JSON, batch ID or quantity |
| 401 | Authentication required, invalid token or user not found |
| 404 | Fridge or product not found |
| 409 | Unsafe fridge, unavailable product or insufficient stock |
| 503 | Database unavailable |

The frontend must display an appropriate message when reservation fails.

**Important:** This endpoint writes to the database and reduces stock. It must not be tested against the shared database until the team approves integration testing.

Reservation database compatibility has not yet been fully verified against the final schema.

## 9. GET /api/fridge/status

**Purpose:** Retrieve fridge safety information and latest device readings.

**Authentication:** Not required.

**Request:**

`GET /api/fridge/status`

**Successful response: HTTP 200**

Illustrative structure:

```json
{
  "location_id": 1,
  "active_device_id": "simulator-01",
  "status": "HOLD",
  "hold_reason": "Awaiting valid simulator temperature",
  "latest_readings": {}
}
```

The endpoint reads the fridge safety state and latest temperature readings from MySQL.

`latest_readings` is now retrieved from the database, rather than relying on the in-memory cache.

Possible errors:

- `404`: Fridge not found.
- `503`: Database unavailable.

## 10. GET /api/health

**Purpose:** Verify that Flask is responding.

**Authentication:** Not required.

**Successful response: HTTP 200**

```json
{
  "status": "ok",
  "project": "Food Save Smart",
  "message": "Backend is running successfully"
}
```

This endpoint does not verify MySQL connectivity.

## 11. POST /api/temperatures

**Purpose:** Accept temperature readings from the simulator or ESP32.

**Authentication:** Private device token, not user JWT.

**Header:**

`Authorization: Bearer <DEVICE_TOKEN>`

**Example request:**

```json
{
  "id": "simulator-01",
  "temperature": 4.6,
  "sensor_status": "ok"
}
```

Accepted device IDs:

- `simulator-01`
- `esp32-01`

Only the simulator currently controls the fridge SAFE/HOLD state.

The frontend must not receive or store the private device token.

This endpoint is intended for Costel's simulator and ESP32 integration.

## 12. Current CORS Configuration

The backend currently allows cross-origin requests to:

- `/api/health`
- `/api/fridge/status`
- `/api/products`

Authentication endpoints currently allow only configured localhost development origins.

The production frontend origin:

`https://food-save-smart.co.uk`

is not yet included in the authentication CORS configuration.

The reservation endpoint does not currently have an explicit CORS rule.

**Before live frontend integration, backend CORS settings must be updated and tested.**

This document does not authorise any immediate changes to the shared database.

## 13. Frontend Integration Responsibilities

**Florin — Frontend**

- Replace demonstration product data with API responses when integration is approved.
- Display prices and discounts received from Flask.
- Display expiry countdowns.
- Show reservation eligibility and backend error messages.
- Implement login and registration forms.
- Attach JWT tokens to protected requests.
- Submit reservations using `batch_id` and `quantity`.
- Handle loading states, empty results and API failures.
- Avoid recalculating backend prices or reservation eligibility.

**Laurentiu — Backend**

- Maintain Flask API endpoints.
- Calculate discounts and final prices.
- Validate user authentication.
- Enforce reservation restrictions.
- Protect stock updates through transactions.
- Finalise production CORS configuration.
- Coordinate API integration with Florin.
- Verify database compatibility after Alex completes the schema.

**Alex — Database**

- Finalise and publish the official MySQL schema.
- Confirm required tables, columns, relationships and constraints.
- Coordinate schema compatibility with the backend.

**Costel — IoT**

- Integrate the simulator and ESP32 with the temperature endpoint.
- Keep device authentication credentials private.

**Marius — UX and QA**

- Review usability and accessibility.
- Validate frontend behaviour and error messaging.
  - Support integration testing.

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ## 14. Current Project Status

Implemented in the supplied Flask source:

- JWT authentication utilities.
- Registration, login and current-user endpoints.
- Product retrieval and automatic discounts.
- Reservation creation logic.
- Temperature monitoring and fridge status.
- Health check.
- Database transactions for reservation creation and stock reduction.

Pending verification or integration:

- Final MySQL schema compatibility.
- Production CORS for frontend authentication and reservations.
- End-to-end frontend/backend integration.
- Real reservation flow validation.
- Complete display of expired and out-of-stock products, if required.
- Confirmed timezone convention for expiry countdowns.
- Persistent reservation pricing, if required by the final database design.

**Integration rule:** Until the final database schema is approved, no test should create, update or delete records in the shared Aiven database.