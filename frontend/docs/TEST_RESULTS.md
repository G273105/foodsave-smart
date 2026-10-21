# Verification evidence — 18 October 2026

Executed with Node.js 24.19.0.

- `npm test`: **24 passed, 0 failed**.
- `npm run check`: all four JavaScript modules passed syntax validation.
- HTML/reference inspection: unique IDs, all referenced local assets present, all literal JS element IDs found, and no dynamic `innerHTML` insertion in the main app.

## Automated coverage

23 focused service/model/contract checks cover all ten source price pairs; money formatting; pence and GBP normalization/payloads; allergens; invalid data; quantity reservations; sold-out/expired cases; single stock restoration on cancellation; single collection accounting; persistence/session-only failures; staff creation; exact HTTP paths and identity fields; 409 responses; network/timeout/non-JSON responses; invalid success status; missing fridge route; and no fallback from failed live requests to fixtures.

One application event/state integration check uses the actual application module in a lightweight DOM harness to exercise product rendering, search and empty results, quantity reservation, cancellation, staff collection, batch creation, alerts and unavailable fridge status.

The DOM harness is not a web browser. These tests do not verify visual layout, focus trapping, browser-specific behaviour, real CORS/session handling, actual backend transactions or physical sensor operation. Browser QA tooling was unavailable in this environment. Complete `MANUAL_REVIEW.md` before declaring the integrated system accepted.


## Downloaded-file update — 18 October 2026

Extract the full ZIP, then open the top-level `index.html`. It renders the application directly without a redirect. The classic `bundle.js` contains the review fixtures and application code; local browsing no longer depends on ES module imports or fetching JSON. Rebuild with `npm run build` after source or fixture changes. API mode remains explicit and has no fallback to review data.

25 automated checks pass, including both source modules and the delivered browser bundle exercised through a lightweight DOM harness. The bundle test rejects all network requests and verifies ten cards/photos, navigation, search, reserve, cancel, staff batch creation and collection. This is not a real-browser visual or accessibility audit. Manually confirm opening the extracted file on Windows, responsive layout, keyboard use and persisted actions. Live backend and fridge integration remain unverified.
