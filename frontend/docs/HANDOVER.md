# Team integration handover

## Front-end delivery status

The required front-end flows are implemented and independently tested. The handover is ready for backend connection and browser acceptance review. It is not yet a verified end-to-end deployment.

The deployed website remains in independent-review mode to avoid claiming shared reservations or sensor data before connection. This does not require the front-end to be rebuilt: the interface calls a single service boundary that can be switched to Flask.

## Connection steps for the backend colleague

1. Run the agreed Flask service and database. Confirm the actual database engine: the planning documents describe SQLite, while `updated.sql` is a MySQL dump.
2. Compare the real GET `/api/products` response to the two explicit profiles below. Choose one; do not rename database columns silently.
3. Edit `config.js`: set `MODE: 'api'`, the actual `API_BASE_URL`, the selected `CONTRACT_PROFILE`, valid `USER_ID`, `STAFF_USER_ID`, assigned `ROLE`, and the category IDs from the database.
4. Serve the frontend from Flask or an HTTP static server. For separate origins, backend CORS must explicitly allow the frontend origin. An HTTPS-hosted page cannot call an HTTP backend without browser security problems; use local HTTP for local integration or an HTTPS API for the hosted site. A colleague's `127.0.0.1` cannot be reached from another person's machine.
5. Provide server-enforced identity/permissions. Front-end role visibility and fixed user IDs are review configuration, not authentication. Never trust submitted user/staff IDs as proof of identity. If using sessions, configure credentials, CORS and CSRF protection together and inject any session token at runtime.
6. Implement or confirm the agreed routes below and verify success/error envelopes. Use browser Network tools during integration.
7. Agree the fridge-status route and response, then set `FRIDGE_STATUS_PATH`. Until then the UI deliberately reports status unavailable.
8. Complete the live acceptance checklist. Publish the API-connected configuration only after those checks pass.

## Exact API boundary

All paths below are relative to `API_BASE_URL`, e.g. `http://127.0.0.1:5000/api`.

| Method/path | Request | Expected success |
|---|---|---|
| GET `/products` | none | `{products:[PRODUCT]}` |
| GET `/products/{batch_id}` | none | `{product:PRODUCT}` |
| POST `/products` | profile-specific creation object below | `{batch_id: positive integer, status:'created'}` |
| GET `/reservations?user_id={USER_ID}` | none | `{reservations:[{reservation_id,batch_id,quantity,status}]}` |
| POST `/reservations` | `{batch_id,user_id,quantity}` | `{reservation_id,status:'reserved' or 'pending',quantity}` |
| POST `/reservations/{id}/cancel` | `{user_id}` | `{reservation_id,status:'cancelled'}` |
| POST `/reservations/{id}/collect` | `{staff_user_id}` | `{reservation_id,status:'collected'}` |
| GET `/alerts` | none | `{alerts:[{alert_id,batch_id,type or alert_type,message}]}` |
| GET `/reports` | none | `{collected_units,estimated_original_value_gbp,estimated_sales_value_gbp}` |
| GET `/health` | none | `{status:'ok'}`; adapter available for smoke tests |

Errors: non-2xx with `{error:{code,message}}`. A failed or unreadable request must not return a false success. No automatic POST retries. If a mutation response is lost, the UI warns that it may have completed and requires refresh before re-submission. Backend atomicity and idempotence remain essential.

### Profile `pence` — required database-aligned fields

Product response:

```json
{
  "batch_id":4,
  "name":"Sourdough Loaf",
  "category_id":2,
  "category":"Bakery",
  "original_price_pence":350,
  "discounted_price_pence":298,
  "quantity_available":2,
  "sell_by_at":"2026-10-19T20:30:29Z",
  "availability_status":"AVAILABLE",
  "allergens_json":["gluten"]
}
```

`discounted_price_pence` must be supplied by the backend; it is not in the database batch table and must be computed/returned by Flask. The value above is the document's display example, not an instruction to override the backend's discount rules. `category` is a display label returned through a join or mapping. Known statuses normalize to lowercase; only `available` with positive stock enables reservations. `past_sell_by` and other statuses disable them.

Create request preserves: `name`, `category_id`, `original_price_pence`, `quantity_available`, ISO-8601 `sell_by_at`, and array `allergens_json`. This request profile follows the required field names but has not been confirmed against a running endpoint. The backend owner must confirm it.

### Profile `gbp` — older api-contract.docx

Product response uses `original_price` and `current_price` as decimal GBP, `category`, array `allergens`, and `status` (available/unavailable/past_sell_by). IDs remain positive integers. The adapter converts pounds to integer pence only for display; it does not calculate discounts.

Create request uses `name`, `category_id`, `original_price` in GBP, `quantity`, ISO-8601 `sell_by_at`, and array `allergens`.

Both adapters are implemented and tested. Selecting a profile is an integration configuration decision; it does not modify source documents or rename database fields.

## Decisions the team must resolve

| Item | Confirmed evidence | What needs agreement |
|---|---|---|
| Money fields | User's required fields and SQL use integer `original_price_pence`; older API draft uses GBP `original_price/current_price` | Select the real HTTP profile and provide current price |
| Product IDs | SQL has batches 1–4; old contract uses fixture 101 | Use real API batch IDs; do not renumber silently |
| Student ID | SQL seeds 1; contract example uses 12 | Configure an existing review user, then integrate authenticated identity |
| Database engine | Plans say SQLite; updated SQL is MySQL | Backend/database owners confirm implementation; frontend remains HTTP-only |
| Discounts | Product list shows static reductions; API draft proposes time tiers | Backend owns rules; frontend displays returned price; do not implement tiers in JS |
| Added products/categories | Six additions and category names are marked demo/proposed | Do not assume batches 5–10 or category IDs 3–4 exist in the real database |
| Staff batch location | SQL requires a `location_id`; draft create request omits it | Backend must confirm default/assignment or revise the agreed create contract before adding a location control |
| Fridge status | SQL contains `safety_state`, `hold_reason`, `updated_at`; no agreed GET status route | Agree route and envelope. Current optional adapter expects `{safety_state:'OK'|'HOLD'|'LOCKED',hold_reason,updated_at,temperature_c?,source?}`. This is an explicit adapter expectation, not an existing agreed route |
| Collection lookup | Contract allows POST collection by ID but no staff-wide reservation list/lookup | Current staff UI collects by provided reference; agree a lookup route if staff need a cross-user queue and pre-verification of quantity |
| Staff access | Fixed demo IDs are in draft, no real authentication | Server permissions and session behaviour before real use |
| Collection details | No exact opening times/location supplied | Confirm operational text or add agreed API fields |
| UI/UX sign-off | New interface built here; no current Penpot/token review performed | Marius/UX owner reviews hierarchy, responsive behaviour, accessibility and consistency |

## Front-end/backend ownership boundary

Florin's package contains pages, controls, client input checks, HTTP adapters, visible error handling, review fixtures and tests. It contains no new database, live price engine, IoT simulator or replacement Flask service. The frontend never connects directly to SQL.

The backend must enforce stock and cutoffs atomically; authorize staff/user actions; handle repeated cancellations/collections; compute prices/countdowns; persist records; report only confirmed collections; expose real status and alerts. Local review behaviours do not prove backend correctness.

## Proposed PR content

Title: Complete FoodSave Smart student and staff front-end with configurable API adapter

Summary: Adds food browsing and detail views, quantity reservations and cancellation, staff batch creation and collection confirmation, collection reports, and fridge/alert states. Separates independent review fixtures from the live API and supports the two documented price formats without changing database names.

Validation: 24 automated checks passed; JavaScript syntax and HTML-reference checks passed. Browser rendering, mobile/keyboard acceptance and running-backend integration remain to be performed. Shared-contract conflicts are listed in this handover.

Do not claim all group-project assessment requirements are finished on the strength of this code. Individual evidence, UX review, integration and the lecturer's criteria still need their own verification.


## Downloaded-file update — 18 October 2026

Extract the full ZIP, then open the top-level `index.html`. It renders the application directly without a redirect. The classic `bundle.js` contains the review fixtures and application code; local browsing no longer depends on ES module imports or fetching JSON. Rebuild with `npm run build` after source or fixture changes. API mode remains explicit and has no fallback to review data.

25 automated checks pass, including both source modules and the delivered browser bundle exercised through a lightweight DOM harness. The bundle test rejects all network requests and verifies ten cards/photos, navigation, search, reserve, cancel, staff batch creation and collection. This is not a real-browser visual or accessibility audit. Manually confirm opening the extracted file on Windows, responsive layout, keyboard use and persisted actions. Live backend and fridge integration remain unverified.
