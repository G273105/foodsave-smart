# Database — FoodSave Smart

This directory contains the MySQL database schema and supporting design documentation for FoodSave Smart, a university project addressing food waste and affordable food access.

The application uses a Python Flask backend connected to a MySQL database hosted on Aiven. Temperature monitoring supports simulated readings and physical ESP32 sensor data.

## Repository Contents

| File | Purpose |
|---|---|
| `shema.sql` | SQL schema defining eight database tables |
| `ERD.png` | Entity Relationship Diagram |
| `context diagram.png` | System context diagram |
| `Level 1 — Main processes.png` | Level 1 Data Flow Diagram |
| `Level 2a — Process 1 Ingest Temperature Reading.png` | Temperature ingestion Data Flow Diagram |
| `Level 2b — Process 3 Process Reservation.png` | Reservation processing Data Flow Diagram |
| `README.md` | Database documentation |

## Database Structure

The SQL schema defines eight tables:

| Table | Purpose |
|---|---|
| `storage_locations` | Refrigeration locations and safety status |
| `devices` | Temperature monitoring devices |
| `temperature_readings` | Temperature measurements and sensor status |
| `categories` | Food product categories |
| `batches` | Food inventory, quantities, prices and expiry details |
| `users` | User accounts, authentication and roles |
| `reservations` | Food reservations and associated details |
| `alerts` | Food safety and expiry alerts |

## System Integration

The database supports user authentication, food inventory, reservations, temperature monitoring and safety alerts.

Additional project documentation is available in the repository's `docs/` directory.
