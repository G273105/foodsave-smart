
# Database

This directory contains the MySQL database structure and supporting documentation for FoodSave Smart.

## Database Technology

Database management system: MySQL

The database is designed to support food surplus management, temperature monitoring, reservations, stock control and alerts.

Alex is responsible for implementing the database structure and providing the SQL setup file.

## Planned Files

- database.sql — a single SQL file containing table definitions, primary keys, foreign keys, relationships, constraints and demonstration data.
- data-dictionary.md — field names, data types and descriptions.
- Entity Relationship Diagram (ERD) — visual representation of the database structure and relationships.

The database will be created using the database.sql file.

## Database Tables

The agreed database design includes eight tables:

### 1. storage_locations

Stores information about monitored storage locations.

Columns:
- location_id
- name
- location_type
- is_active
- safety_state
- hold_reason
- updated_at

Initial demonstration data:
- Fridge 1, location_id = 1

### 2. devices

Stores registered monitoring devices and their associated storage locations.

Columns:
- device_id
- location_id
- source
- is_active
- is_primary

Initial demonstration devices:
- simulator-01 — SIMULATED
- esp32-01 — PHYSICAL

Both devices are associated with Fridge 1.

Initially, simulator-01 is the primary monitoring device.

### 3. temperature_readings

Stores temperature readings received by the Flask backend.

Columns:
- reading_id
- device_id
- temperature_c
- sensor_status
- received_at

Temperature readings are associated with registered devices.

When sensor_status is "error", temperature_c must be NULL.

### 4. categories

Stores food product categories.

Columns:
- category_id
- name

Example categories:
- Ready meal
- Bakery

### 5. batches

Stores available food batches and their stock information.

Columns:
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

Demonstration batches will include different prices, quantities and sell-by dates.

### 6. users

Stores application users and their roles.

Columns:
- user_id
- display_name
- role

Initial demonstration users will include:
- At least one student
- At least one staff member

### 7. reservations

Stores food reservations created by users.

Columns:
- reservation_id
- batch_id
- user_id
- quantity
- status
- created_at
- updated_at

The reservations table may initially be empty.

Reservations and stock validation will be managed through the Python Flask backend.

### 8. alerts

Stores application alerts associated with storage locations or food batches.

Columns:
- alert_id
- location_id
- batch_id
- alert_type
- message
- status
- created_at
- resolved_at

The alerts table may initially be empty.

Alerts will be managed through the Python Flask backend.

## Database Relationships

The planned relationships include:

- devices.location_id references storage_locations.location_id
- temperature_readings.device_id references devices.device_id
- batches.category_id references categories.category_id
- batches.location_id references storage_locations.location_id
- reservations.batch_id references batches.batch_id
- reservations.user_id references users.user_id
- alerts.location_id references storage_locations.location_id
- alerts.batch_id references batches.batch_id

Primary keys, foreign keys and constraints will be defined in database.sql.

The final SQL structure and data types must be confirmed with the backend developer before integration.

## Integration

Only the Python Flask backend communicates directly with MySQL.

The frontend, simulator and ESP32 communicate with Flask through the agreed API endpoints.

Temperature endpoint:
POST /api/temperatures

Fridge status endpoint:
GET /api/fridge/status

Health endpoint:
GET /api/health

The backend will:
- Validate incoming temperature readings.
- Store accepted readings in temperature_readings.
- Identify the primary monitoring device.
- Retrieve and update refrigerator status.
- Retrieve food batches and stock information.
- Calculate discounts.
- Manage reservations and stock availability.
- Record and retrieve alerts.

The frontend and monitoring devices must not connect directly to MySQL.

## Database Validation

The database implementation must be tested to:

- Confirm that database.sql executes successfully.
- Verify all eight tables.
- Verify primary and foreign keys.
- Check relationships and data constraints.
- Reject invalid stock quantities.
- Prevent reservations exceeding available stock.
- Verify that temperature readings are stored correctly.
- Support NULL temperatures for sensor errors.
- Confirm that saved data persists after application restart.
- Verify reservation transactions and stock consistency.

Database validation will be coordinated with the Flask backend developer.

## Repository Rules

- Commit database.sql and supporting documentation.
- Use demonstration data without real personal information.
- Do not commit database credentials, passwords or device tokens.
- Keep database connection credentials in local environment variables.
- Coordinate schema changes with affected team members.
- Keep the agreed table and column names consistent with the Flask backend.

## Current Status

The MySQL database structure and eight required tables have been specified for implementation.

The database setup file, database.sql, is being prepared by the database developer.

The Python Flask backend includes a MySQL connector configuration, but persistent database integration is not yet complete.

The final database implementation will be reviewed and tested before integration with the backend.
