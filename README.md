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
- Database: MySQL.
- Frontend: HTML, CSS and JavaScript.
- Monitoring: ESP32 firmware and a temperature simulator.
- Design: Penpot.
- Collaboration: GitHub Issues, Projects and pull requests.
- Backend testing: pytest.

## Repository structure

| Directory | Purpose |
|---|---|
| frontend/ | Website pages, styles and API integration |
| backend/ | Flask API, business logic and backend tests |
| database/ | MySQL scripts, ERD and data dictionary |
| monitoring/ | ESP32 firmware, simulator and setup instructions |
| design/ | User research, prototypes and usability evidence |
| docs/ | Technical agreements, planning, meeting records and test evidence |

## Team responsibilities

| Team member | GitHub username | Main directory | Responsibility |
|---|---|---|---|
| Costel | @G273105 | monitoring/ | IoT monitoring, ESP32 firmware, temperature simulator and monitoring integration |
| Laurentiu | To be confirmed | backend/ | Python Flask backend, API endpoints, business logic and backend tests |
| Alex | To be confirmed | database/ | MySQL database schema, SQL scripts, ERD and database documentation |
| Florin | To be confirmed | frontend/ | Frontend development, web design and API integration |
| Marius | To be confirmed | design/ | User experience design, web research, usability testing and quality assurance |

The docs/ directory is shared by the team.

Marius coordinates quality assurance activities. Each member remains responsible for testing their own component.

Team-wide Scrum responsibilities and overall integration ownership must be agreed by all members.

## Temperature integration

The temperature sender uses the agreed API contract:

- Endpoint: POST /api/temperatures.
- Proposed transmission interval: 30 seconds.
- JSON fields: id, temperature and sensor_status.
- Temperature unit: degrees Celsius.
- Sensor status: ok or error.
- On sensor failure: temperature is null and sensor_status is error.
- Authentication: a bearer token in the Authorization header.
- Timestamp: recorded by the backend when the message is received.

Device identifiers:

- esp32-01 for the physical device.
- simulator-01 for simulated readings.

The backend currently accepts readings from both identifiers. The simulator is used as the primary source for the demonstration refrigerator status, while ESP32 readings are accepted without overriding that status.

Both device readings are available through the refrigerator status endpoint.

The association between devices, storage locations and food batches will be finalised during MySQL integration.

## Implemented backend functionality

The initial Python Flask backend includes:

- GET /api/health for checking backend availability.
- POST /api/temperatures for receiving temperature readings.
- GET /api/fridge/status for retrieving refrigerator status and latest readings.
- Bearer token authentication for temperature submissions.
- Validation of device identifiers, temperature values and sensor status.
- SAFE and HOLD refrigerator status handling.
- Support for sensor-error messages containing a null temperature.
- UTC timestamps for received readings.
- Separate handling of simulator and ESP32 readings.

Temperature readings are currently stored in memory. Persistent MySQL storage is planned but has not yet been completed.

Temperature thresholds are provisional demonstration values and must not be treated as certified food-safety limits.

## Automated backend testing

Automated API tests are implemented using pytest in backend/test_app.py.

The current test suite covers:

1. Health-check endpoint.
2. Rejection of temperature requests without authentication.
3. SAFE status for a valid temperature reading.
4. HOLD status for a high temperature reading.
5. HOLD status following a sensor error.
6. Rejection of an unknown device identifier.
7. Rejection of an invalid temperature value.
8. Verification that ESP32 readings do not override the simulator-controlled refrigerator status.

All eight tests passed locally during the latest recorded test run.

These tests verify the current Flask API behaviour. They do not yet verify MySQL persistence or full integration with the monitoring hardware and frontend.

## GitHub guide for team members

Download the [GitHub working procedure](docs/FoodSave_Smart_GitHub_Team_Procedure_EN_GB.docx?raw=true) for step-by-step instructions on branches, file uploads, draft pull requests, reviews and merging.

Each member works on their own branch. Costel coordinates reviews and merges approved contributions into main.

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

Planned integration checks include:

- Batch creation and catalogue display.
- Reservation stock updates and overselling protection.
- Cancellation and collection without duplicate effects.
- Backend price and countdown calculations.
- Temperature ingestion and sensor-error handling with MySQL persistence.
- Data persistence after restart.
- Integration with the ESP32 and temperature simulator.
- Mobile layouts, keyboard navigation and usability.

Keep genuine meeting records, decisions, identifiable contributions and test results.

Each member is responsible for their individual weekly portfolio and academic article.

## Local setup

The Flask backend has been developed and tested locally using Python, PyCharm and pytest.

Backend configuration and API details are documented in:

- backend/README.md
- backend/API_CONTRACT.md
- backend/.env.example
- backend/requirements.txt

Full application setup instructions will be updated after the database, frontend and monitoring components are integrated.

## Repository rules

- Use British English for code comments, interface text and project documentation.
- Keep credentials and device tokens out of GitHub.
- Commit MySQL SQL scripts rather than local database files.
- Use demonstration data without real personal information.
- Clearly distinguish proposed, implemented and verified features.
- Obtain peer review before merging feature branches into main.

## Current status

The initial Flask backend has been implemented and tested locally.

Completed backend activities include:

- Flask project setup and environment configuration.
- Authenticated temperature API development.
- Refrigerator SAFE/HOLD status handling.
- Simulator and ESP32 device validation.
- API contract documentation.
- Automated pytest testing with eight successful tests.
- Git commits and publication of backend changes on a dedicated feature branch.
- Pull Request #3 opened for peer review.

The Flask backend is being prepared for integration with the MySQL database developed by the database team member.

Remaining work includes MySQL persistence, business logic for food batches and reservations, frontend integration, monitoring integration and end-to-end testing.

The backend pull request remains subject to peer review and merging into the main branch.