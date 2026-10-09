# Database

This directory contains the SQLite database structure and supporting documentation for FoodSave Smart.

## Planned files
- schema.sql — tables, relationships, constraints and indexes.
- seed.sql — demonstration data for development and testing.
- data-dictionary.md — field names, types and descriptions.
- Entity relationship diagram (ERD).

## Planned data
- Demonstration users and roles.
- Food categories and batches.
- Reservations and collection records.
- Temperature readings and sensor status.
- Alerts.

Device-to-storage-location mapping remains subject to team agreement.

## Integration
Only the Flask backend accesses the database.

The frontend and temperature sender communicate with the backend through the agreed API.

Schema changes must be agreed with the backend developer and any other affected team members.

## Validation
- Verify that the schema and seed scripts run successfully.
- Check relationships and data constraints.
- Reject negative stock and invalid reservation quantities.
- Verify that saved data remains available after restart.
- Work with the backend developer to test reservation transactions.

## Repository rules
Commit SQL scripts and documentation.

Do not commit local database files, passwords, device tokens or real personal data.

## Status
Planned. Implementation has not started.
