# FoodSave Smart

A university canteen food-surplus application developed for the CPU4106 Group Project.

## Project purpose

FoodSave Smart aims to reduce food waste by helping canteen staff publish surplus food and allowing students to reserve available portions for collection.

The project supports UN Sustainable Development Goal 12: Responsible Consumption and Production.

## Intended users

- Students browsing and reserving available food.
- Canteen staff managing food batches and confirming collection.

## Planned features

- Staff creation of food batches with categories, allergens, prices, quantities and collection deadlines.
- Student catalogue showing available food.
- Automatic price reductions and countdowns calculated by the backend.
- Reservations with stock validation and protection against overselling.
- Reservation cancellation and staff confirmation of collection.
- Temperature monitoring using an ESP32 and a physical sensor.
- Temperature simulator for development and testing.
- Alerts and reports based on confirmed collections.
- Responsive and accessible interfaces for mobile and desktop.

Discount rules, alert thresholds, device mapping and hardware delivery dates remain subject to team agreement.

Temperature monitoring provides information about the monitored storage location. It does not certify food safety or extend collection deadlines.

## Technology stack

- Backend: Python and Flask.
- Database: SQLite.
- Frontend: HTML, CSS and JavaScript.
- Monitoring: ESP32 firmware and a temperature simulator.
- Design: Penpot.
- Collaboration: GitHub Issues, Projects and pull requests.

## Repository structure

| Directory | Purpose |
|---|---|
| frontend/ | Website pages, styles and API integration |
| backend/ | Flask API, business logic and backend tests |
| database/ | SQL scripts, ERD and data dictionary |
| monitoring/ | ESP32 firmware, simulator and setup instructions |
| design/ | User research, prototypes and usability evidence |
| docs/ | Technical agreements, planning, meeting records and test evidence |

## Team responsibilities

| Team member | GitHub username | Main directory | Responsibility |
|---|---|---|---|
| Costel | @G273105 | monitoring/ | IoT monitoring, ESP32 firmware, temperature simulator and monitoring integration |
| Laurentiu | To be confirmed | backend/ | Python Flask backend, API endpoints, business logic and backend tests |
| Alex | To be confirmed | database/ | SQLite schema, SQL scripts, ERD and database documentation |
| Florin | To be confirmed | frontend/ | Frontend development, web design and API integration |
| Marius | To be confirmed | design/ | User experience design, web research, usability testing and quality assurance |

The docs/ directory is shared by the team.

Marius coordinates quality assurance activities. Each member remains responsible for testing their own component.

Team-wide Scrum responsibilities and overall integration ownership must be agreed by all members.

## Temperature integration

The proposed temperature sender uses:

- Endpoint: POST /api/temperatures.
- Transmission interval: 30 seconds.
- JSON fields: id, temperature and sensor_status.
- Temperature unit: degrees Celsius.
- Sensor status: ok or error.
- On sensor failure: temperature is null and sensor_status is error.
- Authentication: a bearer token in the Authorization header.
- Timestamp: recorded by the backend when the message is received.

Proposed identifiers:
- esp32-01 for the physical device.
- simulator-01 for simulated readings.

The backend distinguishes physical and simulated readings and manages the agreed association between devices, storage locations and food batches.

## Working process

1. Create or select a GitHub Issue with clear acceptance criteria.
2. Assign an owner and update its status in GitHub Projects.
3. Create a task branch from the latest main.
4. Implement and test the change.
5. Open a pull request linked to the Issue.
6. Obtain a review from another team member.
7. Merge after the relevant checks have passed.
8. Record test evidence and update documentation.

Discuss changes to shared API fields, database structure or user flows with the affected owners before implementation.

## Project board

Task statuses:
- Backlog
- Ready
- In Progress
- Review
- Testing
- Done

A task is Done when its acceptance criteria are met, the work is integrated, the relevant checks have passed and supporting evidence is recorded.

## Testing and evidence

Planned checks include:
- Batch creation and catalogue display.
- Reservation stock updates and overselling protection.
- Cancellation and collection without duplicate effects.
- Backend price and countdown calculations.
- Temperature ingestion and sensor-error handling.
- Data persistence after restart.
- Mobile layouts, keyboard navigation and usability.

Keep genuine meeting records, decisions, identifiable contributions and test results.

Each member is responsible for their individual weekly portfolio and academic article.

## Local setup

Application setup and run instructions will be added when the first runnable components are available.

## Repository rules

- Use British English for code comments, interface text and project documentation.
- Keep credentials and device tokens out of GitHub.
- Commit SQL scripts rather than local database files.
- Use demonstration data without real personal information.
- Clearly distinguish proposed, implemented and verified features.

## Current status

Initial project structure and documentation are being prepared.

Technical agreements remain subject to team approval. Application functionality has not yet been verified.
