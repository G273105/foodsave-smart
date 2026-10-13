
# FoodSave Smart — IoT API Contract

## Backend
Framework: Python Flask
Development port: 5000
Database: MySQL
Database setup file: database/database.sql

The Flask backend receives temperature readings, validates
incoming data and determines the status of Fridge 1.

MySQL will provide persistent storage for the application.

## Database Structure

The database is prepared by Alex using MySQL.

One file, database/database.sql, will contain the table
definitions, relationships, primary and foreign keys,
and sample data.

The database consists of eight planned tables:

1. storage_locations
   - location_id
   - name
   - location_type
   - is_active
   - safety_state
   - hold_reason
   - updated_at

2. devices
   - device_id
   - location_id
   - source
   - is_active
   - is_primary

3. temperature_readings
   - reading_id
   - device_id
   - temperature_c
   - sensor_status
   - received_at

4. categories
   - category_id
   - name

5. batches
   - batch_id
   - name
   - category_id
   - location_id
   - allergens_json
   - original_price_pence
   - quantity_available
   - sell_by_at
   - created_at
   - availability_status

6. users
   - user_id
   - display_name
   - role

7. reservations
   - reservation_id
   - batch_id
   - user_id
   - quantity
   - status
   - created_at
   - updated_at

8. alerts
   - alert_id
   - location_id
   - batch_id
   - alert_type
   - message
   - status
   - created_at
   - resolved_at

The initial test data will include Fridge 1, two devices,
sample food categories, products and users.

Reservations and alerts may initially remain empty.

The final table definitions and data types will be
confirmed with Alex before database integration.

## Monitoring Devices

Storage location:
- location_id: 1
- name: Fridge 1

Registered devices:
- simulator-01: SIMULATED
- esp32-01: PHYSICAL

Both devices are associated with Fridge 1.

Both active devices may submit temperature readings.
Initially, simulator-01 is the primary monitoring source.

Only the primary monitoring source determines the
current fridge safety status.

## Temperature Endpoint

POST /api/temperatures

Headers:
Authorization: Bearer <DEVICE_TOKEN>
Content-Type: application/json

### Simulator Example

{
  "id": "simulator-01",
  "temperature": 4.6,
  "sensor_status": "ok"
}

### ESP32 Example

{
  "id": "esp32-01",
  "temperature": 4.6,
  "sensor_status": "ok"
}

### Sensor Error Example

{
  "id": "simulator-01",
  "temperature": null,
  "sensor_status": "error"
}

## Temperature Validation Rules

- Devices send readings every 30 seconds.
- Temperature values are measured in Celsius.
- Valid readings require sensor_status = "ok".
- Valid temperatures must be JSON numbers.
- Valid temperatures must be finite.
- Accepted input range: -50 to 100 degrees Celsius.
- Sensor errors require sensor_status = "error".
- Sensor errors require temperature = null.
- Unknown device IDs are rejected.
- Invalid authentication tokens are rejected.
- Only the primary device controls fridge status.

## Demonstration Temperature Rules

- 0 to 5 degrees Celsius: SAFE.
- Outside this range: HOLD.
- Sensor errors from the primary device: HOLD.
- No valid primary-device reading yet: UNKNOWN.

These are provisional demonstration thresholds,
not certified food-safety limits.

## HTTP Responses

- HTTP 200: Successful status or health request.
- HTTP 201: Temperature reading accepted.
- HTTP 400: Invalid JSON, device ID or temperature data.
- HTTP 401: Invalid or missing device token.

## Health Endpoint

GET /api/health

Returns the current backend health response.

## Fridge Status Endpoint

GET /api/fridge/status

Possible fridge status values:
- UNKNOWN
- SAFE
- HOLD

The response includes:
- location_id
- active_device_id
- status
- latest_readings

## MySQL Integration

The Flask backend will connect to the MySQL database.

The integration will support:
- Saving temperature readings.
- Retrieving registered devices.
- Identifying the primary monitoring device.
- Reading and updating fridge status.
- Retrieving products and stock levels.
- Applying expiry-based discount rules.
- Creating and managing reservations.
- Recording and retrieving alerts.

The backend is responsible for application logic.

The frontend communicates with Flask through HTTP APIs
and does not connect directly to MySQL.

The simulator and ESP32 also communicate with Flask,
not directly with MySQL.

## Current Implementation Status

Implemented:
- Flask development server.
- Device token authentication.
- Temperature endpoint.
- JSON and temperature validation.
- Health endpoint.
- Fridge status endpoint.
- SAFE/HOLD demonstration logic.
- Support for simulator-01 and esp32-01 identifiers.

Pending:
- MySQL connection and persistent storage.
- Database-based device activity checks.
- Database-based primary device selection.
- Automatic missing-reading detection.
- Automatic switching between monitoring sources.
- Product, discount and reservation endpoints.
- Persistent alerts and reservation blocking.

Temperature readings are currently stored temporarily
in application memory until MySQL integration is completed.

## Integration Responsibilities

Costel:
- Simulator and ESP32 implementation.
- Temperature transmission every 30 seconds.
- Agreed JSON request format.

Alex:
- MySQL database structure.
- Eight database tables and relationships.
- One database/database.sql file.
- Sample data and database setup instructions.

Laurentiu:
- Python Flask backend.
- API endpoints and validation.
- MySQL integration.
- Fridge status and application business rules.

Florin:
- Frontend implementation.
- Integration with backend API endpoints.

Marius:
- UX design and testing.
- User flows and validation of application behaviour.

## Development and Security

The backend currently runs locally on port 5000.

Local address:
http://127.0.0.1:5000

127.0.0.1 refers to the computer running Flask.

Device tokens must be configured through environment
variables and must not be committed to GitHub.

MySQL credentials must also be stored privately
and must not be committed to GitHub.

The development API must be tested with the MySQL
database before final integration and demonstration.
