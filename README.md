# FoodSave Smart

**CPU4106 Group Project | Team Green | Fly-Tech Internship Scenario**

**Food Waste Reduction and Smart Temperature Monitoring**

FoodSave Smart is a web-based food waste reduction platform developed as part of the CPU4106 Group Project. The application combines food inventory management, expiry-based discounts, student reservations and IoT temperature monitoring to support more sustainable food distribution.

The project addresses the United Nations Sustainable Development Goals:

- **SDG 12.3:** Reduce food waste.
- **SDG 2.1:** Improve access to safe, nutritious and affordable food.

The system is implemented using Python, Flask, JavaScript and MySQL, with the frontend and backend deployed on Render and the database hosted on Aiven.

---

## 1. Live Application

**Frontend:** https://foodsave-smart-1.onrender.com/

**Backend API (Health Check):** https://foodsave-smart.onrender.com/api/health

**Backend API (Products):** https://foodsave-smart.onrender.com/api/products

**GitHub Repository:** https://github.com/G273105/foodsave-smart

FoodSave Smart is available online for demonstration and academic assessment.

The frontend communicates with the Flask backend through API endpoints, while persistent application data is managed using the Aiven-hosted MySQL database.

---

## 2. Live Demo — Access for Assessors

Assessors and visitors can explore FoodSave Smart using a fictional student demonstration account.

### Public Demo Account — Staff

| Field | Details |
|---|---|
| Name | Maria (Demo User) |
| Email | maria@example.com |
| Password | Connect2internet@ |
| Application role | STAFF |

The demonstration account allows users to:

- Browse the food catalogue.
- View product prices, availability and expiry-based discounts.
- Create food reservations.
- View reservation history.
- Cancel existing reservations.
- Observe product availability changes associated with food safety monitoring.

**Important:** This account is intended exclusively for demonstration and academic assessment. It uses fictional user information and does not provide staff or administrator privileges.

Demonstration reservations may affect the shared test inventory.

### Administrator Demonstration

During the live viva, the Scrum Master will use the existing **Laurentiu administrator account** to demonstrate authorised administrative functionality, role-based access control and secure temperature simulation.

Administrator credentials are not publicly disclosed.

### Team Accounts and Role-Based Access

All five project members have individual application accounts for testing and demonstrating appropriate system functionality.

FoodSave Smart supports three application roles:

| Role | Access |
|---|---|
| STUDENT | Browse products, create reservations and manage personal reservation history |
| STAFF | Access authorised operational functionality, including temperature simulation |
| ADMIN | Access administrator-authorised functions and system demonstration controls |

Application permissions are separate from academic project responsibilities.

For example, a team member's responsibility as Database Developer or Scrum Master does not automatically determine their role within the application.

Authentication and role checks protect restricted API functionality.

---

## 3. Project Objectives

FoodSave Smart was developed to:

1. Reduce avoidable food waste through better visibility of food approaching its expiry date.
2. Improve student access to discounted food.
3. Provide a searchable food catalogue with availability information.
4. Apply expiry-based discounts through backend business logic.
5. Allow authenticated students to reserve and cancel food items.
6. Maintain inventory consistency following reservations and cancellations.
7. Monitor refrigeration temperatures using simulated and physical sensor sources.
8. Apply food safety restrictions when unsafe conditions are detected.
9. Demonstrate secure access control and persistent database integration.
10. Deliver a functional, testable and publicly accessible computing solution.

---

## 4. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Frontend | HTML, CSS and JavaScript | User interface and client-side functionality |
| Backend | Python and Flask | REST API and application business logic |
| Database | MySQL | Persistent application data |
| Database hosting | Aiven | Managed MySQL database |
| Frontend hosting | Render | Public website deployment |
| Backend hosting | Render | Flask API deployment |
| Development environment | PyCharm | Python development, debugging and testing |
| Version control | Git and GitHub | Collaborative source control and integration |
| Backend testing | pytest | Automated Python API tests |
| Frontend testing | JavaScript test suite | Automated frontend checks |
| IoT monitoring | ESP32 and Python simulator | Physical and simulated temperature monitoring |
| Project management | Agile Scrum, GitHub and Gantt chart | Planning, coordination and progress tracking |

The application uses HTTP-based API communication and JSON data exchange between its components.

---

## 5. System Architecture

FoodSave Smart consists of four integrated layers.

### Frontend

The frontend provides the student-facing website, including authentication, product browsing, availability information, reservations and reservation history.

### Backend

The Flask backend handles business logic, authentication, permissions, inventory operations, reservations, expiry-based discounts and temperature monitoring.

### Database

The MySQL database, hosted on Aiven, stores the application's persistent data.

The schema contains eight principal tables:

- `storage_locations`
- `devices`
- `temperature_readings`
- `categories`
- `batches`
- `users`
- `reservations`
- `alerts`

### IoT Monitoring

Temperature readings are supported through a Python simulator and the ESP32 hardware monitoring component.

The system distinguishes simulated readings from physical sensor readings to support testing, traceability and demonstration.

---

## 6. Implemented Functionality

### Authentication and Access Control

FoodSave Smart provides authenticated access to application functionality.

Role-based restrictions distinguish STUDENT, STAFF and ADMIN access levels.

Restricted simulator operations require appropriate authorisation.

### Food Catalogue

Users can browse food batches and view relevant product information, including prices, availability and expiry-related information.

Product availability is determined by backend business rules rather than relying exclusively on frontend display logic.

### Expiry-Based Discounts

The backend calculates food discounts according to the remaining time before expiry.

This supports the project's food waste reduction objective by encouraging the reservation of suitable food approaching its expiry date.

### Reservations and Inventory Management

Authenticated students can reserve available food products.

The backend validates reservation requests and updates inventory through database operations designed to prevent inconsistent stock changes.

### Reservation Cancellation

Users can cancel eligible reservations.

The system updates the reservation state and restores the relevant stock quantity where applicable.

### Reservation History

Authenticated users can view their reservation records through the application interface.

### Temperature Monitoring

The system receives temperature data from simulated and physical monitoring sources.

The backend validates incoming readings and evaluates food safety conditions.

### SAFE/HOLD Food Safety Logic

Refrigeration safety is represented through SAFE and HOLD conditions.

When an unsafe temperature is detected, affected food availability is restricted.

During functional testing, the following scenarios were demonstrated:

| Simulated temperature | Expected state | Observed behaviour |
|---|---|---|
| 4.5°C | SAFE | Reservations permitted when other eligibility conditions are satisfied |
| 24.5°C | HOLD | Reservations blocked for affected stock |

These examples demonstrate the integration between temperature monitoring and reservation safety controls.

---

## 7. Testing and Validation

Testing formed a substantial part of the development and integration process.

The project combined automated testing with functional verification of the deployed application.

### Automated Test Results

| Test suite | Tests passed |
|---|---:|
| Backend — Python/pytest | 46 |
| Frontend — JavaScript tests | 30 |
| **Total** | **76** |

**Result: 76 automated tests passed in the recorded test runs.**

The automated test suites provide evidence of successful verification of the tested behaviours.

### Functional Testing

Additional functional verification covered:

- Student and administrator authentication.
- Access control for restricted functionality.
- Product catalogue availability.
- Expiry-based discount behaviour.
- Reservation creation.
- Reservation cancellation.
- Inventory quantity updates.
- Reservation history.
- Simulated temperature input.
- SAFE/HOLD transitions.
- Reservation restrictions under unsafe temperature conditions.
- Frontend and backend communication.
- Persistence through the MySQL database.
- Availability of the deployed application.

Testing evidence is maintained through screenshots, terminal outputs, application demonstrations and GitHub development history.

Passing automated tests does not eliminate all possible defects. Hardware-specific limitations and environmental dependencies are identified separately in the supporting documentation.

---

## 8. IoT Monitoring and Food Safety

FoodSave Smart combines temperature monitoring with inventory availability rules.

Two device categories are represented:

| Device | Type | Purpose |
|---|---|---|
| `simulator-01` | SIMULATED | Controlled temperature testing and demonstrations |
| `esp32-01` | PHYSICAL | ESP32-based temperature monitoring |

The simulator enables repeatable safety scenarios without requiring the physical sensor to be adjusted manually.

Restricted temperature simulation is protected through authenticated application access.

The system distinguishes simulation results from the status of the physical hardware. A successful simulation does not independently establish that a physical sensor is currently online.

---

## 9. Agile Scrum and Project Management

The project followed an Agile Scrum-inspired development approach.

Planning and coordination included:

- Defined responsibilities for each of the five team members.
- A project Gantt chart and milestone tracking.
- Task allocation and progress updates.
- GitHub Issues and collaborative branch development.
- Review and integration of team deliverables.
- Communication of technical dependencies and interface requirements.
- Testing and verification before final integration.
- Preparation of evidence for individual portfolios, the academic article and live viva.

The Scrum Master coordinated implementation dependencies, technical communication and overall integration activities.

### Working Process

1. Create or select a GitHub Issue with clear acceptance criteria.
2. Assign an owner and identify the relevant development task.
3. Create a dedicated task or feature branch.
4. Implement and test the proposed changes.
5. Open a pull request and document the changes.
6. Obtain peer review where applicable.
7. Merge after appropriate checks.
8. Record relevant test evidence and update documentation.

Changes affecting shared API fields, database structures or user workflows should be discussed with the relevant component owners.

### Project Board

The project uses the following workflow statuses:

- Backlog
- Ready
- In Progress
- Review
- Testing
- Done

A task is considered complete when its agreed requirements have been met, relevant checks have passed and supporting evidence has been recorded.

---

## 10. GitHub Collaboration and Integration

The team used GitHub branches and pull requests to integrate contributions from different project components.

Backend development and integration were managed through a dedicated feature branch.

### Main Integration

**Pull Request #3**

Integrated the backend development branch and associated work into the main repository.

The merge included 38 commits from the feature branch.

### Documentation Update

**Pull Request #11**

Updated the database README to correspond with the files actually present in the repository.

The database documentation references the existing SQL schema and design diagrams without requiring additional database scripts or schema changes.

These integration activities provide evidence of version control, collaborative development, peer coordination and repository maintenance.

---

## 11. Design and Database Documentation

The repository contains design materials supporting the development and validation of the system.

### Database Documentation

The `database/` directory contains:

- `shema.sql` — SQL schema defining eight tables.
- `ERD.png` — Entity Relationship Diagram.
- `context diagram.png` — System context diagram.
- `Level 1 — Main processes.png` — Level 1 Data Flow Diagram.
- `Level 2a — Process 1 Ingest Temperature Reading.png` — temperature ingestion process.
- `Level 2b — Process 3 Process Reservation.png` — reservation processing.

Additional documentation is available in the backend, frontend, monitoring and `docs/` directories.

The diagrams support the explanation of system processes, information flows and database relationships during the assessment viva.

---

## 12. Deployment and Hosting

FoodSave Smart uses a publicly accessible deployment architecture.

**Frontend:** Render static website.

**Backend:** Render-hosted Flask application.

**Database:** Aiven-hosted MySQL.

The frontend communicates with the backend through the deployed API endpoints.

Database credentials, authentication secrets, device credentials and other sensitive configuration values are not intended to be committed to the repository.

Deployment settings and environment-specific configuration are managed separately from the published source code.

Availability may depend on the current state of the hosting services and connected components.

---

## 13. Repository Structure

The repository is organised by project component.

| Directory | Purpose |
|---|---|
| `backend/` | Flask application, backend tests and API documentation |
| `frontend/` | Website implementation and frontend tests |
| `database/` | MySQL schema and design diagrams |
| `monitoring/` | IoT monitoring and firmware-related documentation |
| `design/` | Supporting design documentation |
| `docs/` | Team procedures and integration documentation |

Individual directories contain additional documentation where applicable.

---

## 14. Development and Local Setup

The backend can be developed and tested locally with Python, a virtual environment and the required dependencies.

Backend setup and technical details are maintained in the repository documentation:

- `backend/README.md`
- `backend/API_CONTRACT.md`
- `backend/.env.example`
- `backend/requirements.txt`

The frontend and monitoring components have their own supporting files and documentation.

A suitable MySQL configuration and appropriate local environment variables are required for database-dependent functionality.

Credentials, API secrets and device tokens must not be committed to GitHub.

---

## 15. Repository Rules

The team follows these repository and documentation principles:

- Use British English for project documentation.
- Maintain clear commit messages and descriptive pull requests.
- Avoid committing passwords, database credentials and device secrets.
- Use fictional demonstration accounts rather than real student personal information.
- Document implementation decisions and relevant limitations accurately.
- Keep database and API documentation consistent with the implemented system.
- Coordinate shared changes with the relevant component owners.
- Preserve genuine test evidence and collaboration records.
- Distinguish completed functionality from proposed improvements.

---

## 16. Project Outcomes and Limitations

FoodSave Smart demonstrates an integrated computing solution combining a web frontend, Flask API, persistent MySQL database and temperature-aware food availability rules.

Key outcomes include:

- A publicly deployed web application.
- Integrated frontend and backend functionality.
- Persistent database operations through Aiven.
- Authenticated food reservation workflows.
- Expiry-based food discounting.
- Reservation cancellation and stock restoration.
- Simulated IoT temperature monitoring.
- Food safety restrictions linked to unsafe temperature conditions.
- Role-based authorisation.
- 76 passing automated tests across the recorded backend and frontend test suites.
- Collaborative development and integration through GitHub.

### Limitations

The application is an academic demonstration rather than a production food distribution service.

Physical sensor availability and connectivity must be assessed independently from simulated readings.

The public demo account shares application test data and should not be used for storing personal information.

The current evidence supports the tested scenarios and implemented functionality; it does not constitute a formal production security or food safety certification.

---

## 17. Academic Assessment and Live Viva

FoodSave Smart was developed as part of the **CPU4106 Group Project**.

The assessment evidence includes:

- Functional computing artefact.
- Agile project planning documentation.
- Database and system design diagrams.
- Individual weekly learning portfolios.
- Individual academic articles.
- Automated and functional test evidence.
- Group PowerPoint presentation.
- Live application demonstration.
- Viva questions and answers.

During the presentation, the team will explain the project problem, SDG relevance, design decisions, implementation, testing results, limitations and individual contributions.

The fictional Maria account is provided for independent student-level testing. Administrator functionality will be demonstrated by the authorised project representative.

---

## 18. Conclusion

FoodSave Smart demonstrates how web development, database technologies and IoT monitoring can be combined to address food waste and improve access to discounted food.

The project also demonstrates practical learning in software engineering, Agile collaboration, backend development, API integration, database management, system testing, cloud deployment and technical documentation.

The implementation provides a working foundation for future development and illustrates the value of combining sustainability objectives with an integrated computing solution.

**Developed by Team Green — CPU4106 Group Project.**
