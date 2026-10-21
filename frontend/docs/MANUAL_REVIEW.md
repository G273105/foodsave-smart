# Browser and team acceptance checklist

Record browser/version, device/viewport, tester, date, expected result, actual result and screenshot evidence where appropriate. These checks are PENDING, not fabricated test results.

## Visual and accessibility

- [ ] Desktop at 1440 px, tablet at 768 px, phone at 390 px and narrow phone at 320 px: no horizontal overflow, clipping or overlapping controls.
- [ ] At 200% zoom: text and form labels remain readable and controls usable.
- [ ] Photographs load, crop appropriately and fall back to the neutral placeholder on failure.
- [ ] Keyboard: skip link, navigation, filters, detail dialog, quantity control, reservation, confirmation and close are reachable; focus stays in native dialogs and returns correctly on closing.
- [ ] Focus indicators remain visible; no information depends solely on colour.
- [ ] Screen reader labels, headings, status/error announcements and quantity fields are meaningful.
- [ ] Search/category/sort and zero-result states work without losing the current query.
- [ ] Marius/UX owner reviews the new design against the team's required flows and tokens.

## Independent review

- [ ] Open product details and confirm price, source dates and allergens against the shared files.
- [ ] Reserve a quantity; reload; confirm the reservation persists and sample stock changes.
- [ ] Cancel once and repeat; stock does not restore twice.
- [ ] Confirm collection once and repeat; collected total does not count twice.
- [ ] Add a batch through Staff workspace; catalogue and stock refresh.
- [ ] Past sample sell-by records cannot be reserved; the fixture dates remain unchanged.
- [ ] Denied device storage shows the session-only limitation.
- [ ] Fridge status remains unavailable without a data source; no fabricated safe/unsafe claim.

## API integration — backend required

- [ ] Choose money profile and valid identities; GET products/detail matches real response.
- [ ] Student reservation is stored by Flask/database and visible on a second client.
- [ ] Two clients competing for the last item: exactly one succeeds; other receives a clear 409.
- [ ] Server rejects reservation after cutoff and when fridge access is held.
- [ ] Cancellation restores once; collection records once; reports include collected quantities only.
- [ ] Staff create succeeds with real category and storage location handling.
- [ ] Non-staff requests cannot create/collect even when modifying frontend configuration.
- [ ] Staff collection reference errors are clear; agree lookup if the workflow needs a full queue.
- [ ] 400, 401, 403, 404, 409, 500, network failure and timeout render useful errors without false success.
- [ ] A lost write response is reconciled by refresh before retrying; no automatic duplicate writes.
- [ ] CORS, HTTPS, credentials and CSRF behaviour work with the actual hosting arrangement.
- [ ] Agreed fridge endpoint: known normal/hold states and sensor-error/missing/stale readings render appropriately; backend owns collection permissions.
- [ ] Alerts, collection location/opening times and operational wording are confirmed by the team.
- [ ] Database restart preserves shared reservations and stock.

Only mark these items passed after the stated action has actually been performed.


## Downloaded-file update — 18 October 2026

Extract the full ZIP, then open the top-level `index.html`. It renders the application directly without a redirect. The classic `bundle.js` contains the review fixtures and application code; local browsing no longer depends on ES module imports or fetching JSON. Rebuild with `npm run build` after source or fixture changes. API mode remains explicit and has no fallback to review data.

25 automated checks pass, including both source modules and the delivered browser bundle exercised through a lightweight DOM harness. The bundle test rejects all network requests and verifies ten cards/photos, navigation, search, reserve, cancel, staff batch creation and collection. This is not a real-browser visual or accessibility audit. Manually confirm opening the extracted file on Windows, responsive layout, keyboard use and persisted actions. Live backend and fridge integration remain unverified.
