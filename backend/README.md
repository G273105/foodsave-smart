
# Backend

This directory contains the Python Flask application, API endpoints, business rules and automated backend tests for FoodSave Smart.

## Technology

- Python
- Flask
- MySQL
- pytest
- python-dotenv
- mysql-connector-python

## Implemented Functionality

The backend currently provides:

- GET /api/health
- POST /api/temperatures
- GET /api/fridge/status
- Bearer token authentication for temperature submissions
- JSON and temperature validation
- Support for simulator-01 and esp32-01
- SAFE, HOLD and UNKNOWN refrigerator status handling
- Sensor error validation
- UTC timestamps for received readings

The simulator is initially the primary monitoring device. ESP32 readings are accepted but do not override the simulator-controlled refrigerator status.

## Database

MySQL is the database technology for FoodSave Smart.

The backend includes db.py, which provides a MySQL connection function using environment variables.

The database structure will be supplied in a single database.sql file containing table definitions, relationships and sample data.

Temperature readings are currently stored in memory. Persistent MySQL storage will be implemented after the database schema is available.

## Automated Testing

Automated tests are implemented in test_app.py using pytest.

The current test suite includes eight tests covering:

- Health endpoint
- Missing authentication token
- SAFE temperature
- HOLD temperature
- Sensor error
- Unknown device
- Invalid temperature
- ESP32 monitoring behaviour

All eight tests passed during the latest local test run.

Run the tests from the project root:

python -m pytest backend/test_app.py -v

## Configuration

Environment variables are defined locally in backend/.env.

Use backend/.env.example as the configuration template.

Credentials and private tokens must not be committed to GitHub.

## Current Status

Completed:
- Initial Flask API implementation
- Device authentication and temperature validation
- Refrigerator status logic
- MySQL connector configuration
- API contract documentation
- Eight successful automated tests
- GitHub feature branch and Pull Request #3

Pending:
- Persistent MySQL storage
- Database-based device management
- Product and discount business logic
- Stock-safe reservations
- Alerts and reports
- Frontend and monitoring integration
- End-to-end testing
