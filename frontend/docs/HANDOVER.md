# Frontend integration handover — 21 October 2026

The API contract in the supplied backend ZIP is the source for this update.
This is a frontend implementation, not confirmation that the live backend works.

## Files changed

- api.js: documented routes, JWT login, registration, reservation envelope,
  backend errors, fridge mapping; removes guessed user-ID-based routes.
- model.js: respects can_reserve; timezone-aware display countdown; retains
  all backend prices and allergen information without inventing data.
- app.js: price/percentage/time display, blocked reserve buttons, auth UI,
  session confirmations, stock refresh and conflict handling.
- index.html/config.js/bundle.js: UI and API mode configuration/build.
- review.html and OFFLINE_REVIEW.html: separate explicit offline review.
- tests: replace obsolete API assumptions with current contract tests; retain
  offline student/staff flows and add an API interface flow with simulated HTTP.

## Exact supported mapping

| UI operation | Backend request |
| --- | --- |
| Catalogue and product details | GET /api/products |
| Create student account | POST /api/auth/register |
| Sign in | POST /api/auth/login |
| Current account adapter | GET /api/auth/me |
| Reserve | POST /api/reservations with Bearer token, batch_id and quantity |
| Fridge status / safety alert | GET /api/fridge/status |

## Remaining work before integrated release

- Backend must resolve CORS for authentication and reservations, timezone metadata,
  schema verification and unavailable-product endpoint coverage.
- Agree history/cancel/staff routes if those features must work against real data.
- Use team-approved test accounts and an approved database environment for writes.
- Complete real browser/visual checks and an end-to-end test, then record Florin's
  actual Git commit and dated screenshots. No commits/screenshots are fabricated.

## Frontend implementation decisions

Keep JWT in memory rather than source or localStorage. Do not use fixed user IDs.
Refresh stock after successful reservations and periodically once a minute.
Backend remains the authority for prices and final reservation validation.
Do not infer UTC or local time from an offset-free sell_by_at string.
Do not call endpoints absent from the supplied contract or pretend local history
is a full backend history. Unknown fridge state fails closed for reservations.
