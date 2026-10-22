# Database — FoodSave Smart

This directory contains the MySQL database structure and supporting
documentation for **FoodSave Smart**, the Fly-Tech internship project
addressing **UN SDG 12.3** (halving food waste) and **SDG 2.1** (affordable
food access for students).

The backend is a **Flask (Python) API**; the database is **MySQL 8.0.16+**.
Two temperature sources write to the database: a **Python simulator**
(`simulator-01`, `SIMULATED`) and a physical **ESP32** sensor
(`esp32-01`, `PHYSICAL`).

---

## Contents

| File | Purpose |
|---|---|
| `schema.sql` | Full DDL: 8 tables, FKs, CHECK constraints, indexes, base seed |
| `seed_products.sql` | Extended product seed (bakery, ready meals, fruit & veg) |
| `seed_users.sql` | Team + demo users (2 staff, 2 students) |
| `views.sql` | `latest_temperature_readings` view (last 10 per device) |
| `migrations/` | Ordered schema changes (`001_init`, `002_seed`, `003_users_reservations_constraints`) |
| `data-dictionary.md` | Field names, types, constraints, and descriptions |
| `../docs/erd.md` | Entity relationship diagram (Mermaid + Graphviz + DBML) |
| `../docs/case/` | DFDs and Use Case diagram for the viva |

---

## Schema at a glance

Eight tables:

| Table | Purpose |
|---|---|
| `storage_locations` | Fridges / storage units, with safety state and hold reason |
| `devices` | Temperature sensors attached to a location (`SIMULATED` / `PHYSICAL`) |
| `temperature_readings` | Time-series temperature data; `NULL` temp on sensor error |
| `categories` | Product categories (Ready meal, Bakery, Fruit & Veg) |
| `batches` | Inventory: price, quantity, allergens, sell-by date, availability |
| `users` | Students, staff, admins — with `email` (UNIQUE) and `password_hash` |
| `reservations` | Product holds with post-discount pricing and expiry |
| `alerts` | Safety/expiry alerts, linked to a location or a batch |

**Constraints enforced at DB level:**

- `batches.original_price_pence >= 0`, `batches.quantity_available >= 0`
- `reservations.quantity >= 1`
- `reservations.unit_price_pence >= 0`, `total_price_pence >= 0`
- `reservations.discount_percent BETWEEN 0 AND 100`
- `users.email` UNIQUE and NOT NULL; `users.password_hash` NOT NULL

**Indexes worth knowing:**

- `temperature_readings (device_id, received_at DESC, reading_id DESC)` — latest reading per device, no filesort
- `reservations (expires_at)` — expired-reservation queries
- `batches (sell_by_at)` — "expiring soon" queries

Full ERD: [`docs/erd.md`](../docs/erd.md).

---

## Planned / demonstration data

- **Users:** 2 students (Alex, Costel), 2 staff (Laurentiu, Florin), 1 admin (Marius)
- **Categories:** Ready meal, Bakery, Fruit & Veg
- **Devices:** `simulator-01` (SIMULATED, primary), `esp32-01` (PHYSICAL), both on Fridge 1
- **Batches:** 10 demo products across all three categories, with varied prices and expiry
- **Reservations:** created by the Flask backend during demo; seed script leaves the table empty
- **Temperature readings:** produced by the simulator at ~30s intervals
- **Alerts:** raised by the Flask backend when temperature thresholds are crossed

⚠️ **Placeholder password hashes.** Seeded users have
`password_hash = 'CHANGE_ME'`. This is **not a valid bcrypt hash** — any
login attempt will fail until real hashes are generated. Generate one with:

```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'changeme', bcrypt.gensalt()).decode())"

Last updated: 20 October 2026.

Included: `schema.sql`

Validation: Pending.
